"""Carga de corridas del CPM (static.txt + dynamic.txt + events.csv + run.json)."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np

TP_ROOT = Path(__file__).resolve().parent.parent

IN_ROOM, EXITING, REMOVED = 0, 1, 2
TSDMD, EDMD = 0, 1
COLUMNS = 10  # x y vx vy r tx ty fase contacto esquema (corridas viejas: 9, sin esquema)


@dataclass(frozen=True)
class CpmRun:
    path: Path
    meta: dict
    n: int
    t: np.ndarray  # (F,)
    x: np.ndarray  # (F, N)
    y: np.ndarray
    vx: np.ndarray
    vy: np.ndarray
    r: np.ndarray
    tx: np.ndarray
    ty: np.ndarray
    phase: np.ndarray  # (F, N) int
    contact: np.ndarray  # (F, N) bool
    scheme: np.ndarray  # (F, N) int: 0 = TSDMD, 1 = EDMD
    events: np.ndarray  # registros (t, id, event) con event ∈ {"door", "exit"}


def load_run(path: str | Path) -> CpmRun:
    path = Path(path)
    meta = json.loads((path / "run.json").read_text())
    n = int((path / "static.txt").read_text().split("\n", 1)[0])
    text = (path / "dynamic.txt").read_text()
    columns = len(text.split("\n", 2)[1].split())
    tokens = np.array(text.split(), dtype=float)
    frames = tokens.reshape(-1, 1 + columns * n)
    s = frames[:, 1:].reshape(-1, n, columns)
    if columns == COLUMNS:
        scheme = s[:, :, 9].astype(int)
    else:  # corridas anteriores a la columna de esquema: un solo esquema
        scheme = np.full(s.shape[:2], EDMD if meta.get("scheme") == "edmd" else TSDMD)
    events = np.genfromtxt(path / "events.csv", delimiter=",", names=True, dtype=None, encoding="utf-8")
    return CpmRun(
        path=path, meta=meta, n=n, t=frames[:, 0],
        x=s[:, :, 0], y=s[:, :, 1], vx=s[:, :, 2], vy=s[:, :, 3], r=s[:, :, 4],
        tx=s[:, :, 5], ty=s[:, :, 6], phase=s[:, :, 7].astype(int), contact=s[:, :, 8] > 0.5, scheme=scheme,
        events=np.atleast_1d(events),
    )
