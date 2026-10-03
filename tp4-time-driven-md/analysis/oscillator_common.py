"""Carga de corridas del sistema 1 (oscilador amortiguado) y su solución analítica."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

TP_ROOT = Path(__file__).resolve().parent.parent
OUTPUT = TP_ROOT / "output"


def load_run(run_dir: Path) -> tuple[dict, np.ndarray, np.ndarray, np.ndarray]:
    """`run.json` + columnas t, r, v de `trajectory.csv`."""
    run_dir = Path(run_dir)
    meta = json.loads((run_dir / "run.json").read_text())
    t, r, v = np.loadtxt(run_dir / "trajectory.csv", delimiter=",", skiprows=1, unpack=True)
    return meta, t, r, v


def analytic(t: np.ndarray, meta: dict) -> np.ndarray:
    """r(t) = A exp(-γ t / 2m) cos(√(k/m − γ²/4m²) t), con A = r(0) (Teórica 4, diap. 37).

    Vale solo con v(0) = −Aγ/(2m), la condición inicial de la diapositiva."""
    m, k, gamma, amplitude = meta["m"], meta["k"], meta["gamma"], meta["r0"]
    omega = np.sqrt(k / m - gamma**2 / (4 * m**2))
    return amplitude * np.exp(-gamma * t / (2 * m)) * np.cos(omega * t)
