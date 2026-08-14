"""Lectura de los archivos que produce el motor Java.

Este módulo (y todo `analysis/`) **sólo lee y grafica**: nunca recalcula vecindades. La simulación
se corre offline en Java y acá se consumen sus resultados. Si un script de análisis empieza a
calcular quién es vecino de quién, algo se hizo mal.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np


@dataclass
class Snapshot:
    """Estado del sistema en un instante. Los arrays están indexados por (id - 1)."""

    time: float
    x: np.ndarray
    y: np.ndarray
    vx: np.ndarray
    vy: np.ndarray


@dataclass
class Run:
    """Una corrida completa, tal como quedó persistida en disco."""

    path: Path
    n: int
    l: float
    radii: np.ndarray
    colors: list[str]
    snapshots: list[Snapshot]
    #: neighbors[i] son los índices 0-based de las vecinas de la partícula con id i+1.
    neighbors: list[np.ndarray]
    meta: dict = field(default_factory=dict)

    @property
    def snapshot(self) -> Snapshot:
        """Instante único del TP1 (t0)."""
        return self.snapshots[0]

    @property
    def periodic(self) -> bool:
        return bool(self.meta.get("periodic", False))

    @property
    def m(self) -> int | None:
        return self.meta.get("M")

    @property
    def rc(self) -> float | None:
        return self.meta.get("rc")


def _meaningful_lines(path: Path) -> list[str]:
    with path.open(encoding="utf-8") as handle:
        return [line for line in handle if line.strip() and not line.lstrip().startswith("#")]


def read_static(path: Path) -> tuple[int, float, np.ndarray, list[str]]:
    """Lee el archivo estático: N, L y el radio/color de cada partícula."""
    lines = _meaningful_lines(path)
    n = int(lines[0])
    l = float(lines[1])
    radii = np.empty(n)
    colors: list[str] = []
    for i in range(n):
        tokens = lines[2 + i].split()
        radii[i] = float(tokens[0])
        colors.append(tokens[1] if len(tokens) > 1 else "#1f77b4")
    return n, l, radii, colors


def read_dynamic(path: Path, n: int) -> list[Snapshot]:
    """Lee el archivo dinámico completo (soporta varios tiempos; el TP1 escribe uno solo)."""
    lines = _meaningful_lines(path)
    snapshots: list[Snapshot] = []
    cursor = 0
    while cursor < len(lines):
        time = float(lines[cursor])
        cursor += 1
        block = np.array([[float(v) for v in lines[cursor + i].split()] for i in range(n)])
        cursor += n
        vx = block[:, 2] if block.shape[1] > 2 else np.zeros(n)
        vy = block[:, 3] if block.shape[1] > 3 else np.zeros(n)
        snapshots.append(Snapshot(time, block[:, 0], block[:, 1], vx, vy))
    return snapshots


def read_neighbors(path: Path, n: int) -> list[np.ndarray]:
    """Lee el archivo de vecinos y lo devuelve como índices 0-based."""
    neighbors: list[np.ndarray] = [np.empty(0, dtype=int) for _ in range(n)]
    for line in _meaningful_lines(path):
        ids = [int(token) for token in line.split()]
        particle_index = ids[0] - 1
        neighbors[particle_index] = np.array([i - 1 for i in ids[1:]], dtype=int)
    return neighbors


def load_run(directory: str | Path) -> Run:
    """Carga una corrida entera desde su directorio de salida."""
    path = Path(directory)
    if not path.is_dir():
        raise SystemExit(f"No existe el directorio de corrida: {path}")

    n, l, radii, colors = read_static(path / "static.txt")
    snapshots = read_dynamic(path / "dynamic.txt", n)
    neighbors = read_neighbors(path / "neighbors.txt", n)

    meta = {}
    meta_path = path / "run.json"
    if meta_path.exists():
        meta = json.loads(meta_path.read_text(encoding="utf-8"))

    return Run(path=path, n=n, l=l, radii=radii, colors=colors, snapshots=snapshots,
               neighbors=neighbors, meta=meta)
