"""Loader del formato de cátedra (`static.txt` / `dynamic.txt`) a arrays de numpy.

Este módulo no sabe nada de Vicsek: habla del formato común a todos los TPs. El parseo es
vectorizado (una sola pasada, sin bucle por línea) y el estado se cachea en `state.npz` para que
la segunda corrida arranque instantánea.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

STATIC_NAME = "static.txt"
DYNAMIC_NAME = "dynamic.txt"
OBSERVABLES_NAME = "observables.csv"
META_NAME = "run.json"
CACHE_NAME = "state.npz"


@dataclass
class Run:
    """Una corrida cargada en memoria."""

    path: Path
    n: int
    l: float
    times: np.ndarray                                   # (T,)
    state: np.ndarray                                   # (T, N, 4) float32 — x, y, vx, vy
    meta: dict = field(default_factory=dict)            # run.json, {} si no existe
    observables: dict[str, np.ndarray] | None = None    # columnas de observables.csv

    @property
    def frames(self) -> int:
        return int(self.times.shape[0])

    def observable_at(self, frame: int) -> dict[str, float]:
        """Valores de los observables en el paso correspondiente a `frame`.

        `observables.csv` tiene una fila por paso y `dynamic.txt` un bloque cada `outputEvery`
        pasos, así que se indexa por tiempo en vez de por posición.
        """
        if not self.observables:
            return {}
        times = self.observables.get("time")
        if times is None or times.size == 0:
            return {}
        i = int(np.clip(np.searchsorted(times, self.times[frame]), 0, times.size - 1))
        return {k: float(v[i]) for k, v in self.observables.items() if k != "time"}


def load_run(path: str | Path, *, use_cache: bool = True) -> Run:
    """Carga el directorio de una corrida.

    Degrada sin fallar: si no están `observables.csv` o `run.json` (corridas de otros TPs que no
    los escriben), quedan en `None` y `{}` respectivamente.
    """
    path = Path(path)
    static_path = path / STATIC_NAME
    dynamic_path = path / DYNAMIC_NAME
    if not static_path.is_file():
        raise FileNotFoundError(f"no se encontró {static_path}")
    if not dynamic_path.is_file():
        raise FileNotFoundError(f"no se encontró {dynamic_path}")

    n, l = _read_static(static_path)
    times, state = _read_dynamic(dynamic_path, n, use_cache=use_cache)
    return Run(
        path=path,
        n=n,
        l=l,
        times=times,
        state=state,
        meta=_read_meta(path / META_NAME),
        observables=_read_observables(path / OBSERVABLES_NAME),
    )


def _read_static(path: Path) -> tuple[int, float]:
    with path.open() as handle:
        n = int(handle.readline().split()[0])
        l = float(handle.readline().split()[0])
    return n, l


def _read_dynamic(path: Path, n: int, *, use_cache: bool) -> tuple[np.ndarray, np.ndarray]:
    cache = path.with_name(CACHE_NAME)
    mtime = path.stat().st_mtime_ns
    if use_cache:
        cached = _load_cache(cache, mtime)
        if cached is not None:
            return cached

    tokens = np.array(path.read_text().split(), dtype=np.float32)
    block = 1 + 4 * n
    if tokens.size % block != 0:
        raise ValueError(
            f"{path}: {tokens.size} valores no son múltiplo del bloque de {block} "
            f"(1 tiempo + 4 columnas × N={n}); ¿el N de static.txt no corresponde?"
        )
    frames = tokens.size // block
    blocks = tokens.reshape(frames, block)
    times = np.ascontiguousarray(blocks[:, 0])
    state = np.ascontiguousarray(blocks[:, 1:].reshape(frames, n, 4))

    if use_cache:
        try:
            np.savez(cache, times=times, state=state, mtime=np.int64(mtime))
        except OSError:
            pass  # el caché es una optimización: si el disco no deja, seguimos igual
    return times, state


def _load_cache(cache: Path, mtime: int) -> tuple[np.ndarray, np.ndarray] | None:
    if not cache.is_file():
        return None
    try:
        with np.load(cache) as data:
            if int(data["mtime"]) != mtime:
                return None
            return data["times"], data["state"]
    except (OSError, KeyError, ValueError):
        return None


def _read_meta(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError:
        return {}


def _read_observables(path: Path) -> dict[str, np.ndarray] | None:
    if not path.is_file():
        return None
    lines = path.read_text().splitlines()
    if len(lines) < 2:
        return None
    columns = [c.strip() for c in lines[0].split(",")]
    values = np.array([row.split(",") for row in lines[1:] if row.strip()], dtype=np.float64)
    return {name: np.ascontiguousarray(values[:, i]) for i, name in enumerate(columns)}
