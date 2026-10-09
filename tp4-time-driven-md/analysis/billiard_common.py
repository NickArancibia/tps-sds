"""Carga de corridas del billar (sistema 2) y energía total a partir de los estados guardados."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from scipy.spatial import cKDTree


@dataclass(frozen=True)
class BilliardRun:
    path: Path
    meta: dict
    n: int
    big_r: float
    r: float
    m: float
    k: float
    obstacles: np.ndarray  # (K, 2) centros
    t: np.ndarray  # (F,)
    x: np.ndarray  # (F, N)
    y: np.ndarray
    vx: np.ndarray
    vy: np.ndarray
    used: np.ndarray  # (F, N) bool


def load_run(path: str | Path) -> BilliardRun:
    path = Path(path)
    meta = json.loads((path / "run.json").read_text())
    static = (path / "static.txt").read_text().split("\n")
    n = int(static[0])
    big_r = float(static[1])
    k_obst = int(static[2 + n])
    obstacles = np.array([[float(v) for v in static[3 + n + o].split()[:2]] for o in range(k_obst)]).reshape(-1, 2)

    tokens = np.array((path / "dynamic.txt").read_text().split(), dtype=float)
    frames = tokens.reshape(-1, 1 + 5 * n)
    state = frames[:, 1:].reshape(-1, n, 5)
    return BilliardRun(
        path=path, meta=meta, n=n, big_r=big_r, r=meta["r"], m=meta["m"], k=meta["k"],
        obstacles=obstacles, t=frames[:, 0],
        x=state[:, :, 0], y=state[:, :, 1], vx=state[:, :, 2], vy=state[:, :, 3],
        used=state[:, :, 4] > 0.5,
    )


def kinetic_energy(run: BilliardRun) -> np.ndarray:
    """E_c(t) = Σ_i ½ m |v_i|²."""
    return 0.5 * run.m * np.sum(run.vx**2 + run.vy**2, axis=1)


def potential_energy(run: BilliardRun) -> np.ndarray:
    """E_p(t) = Σ_contactos ½ k ξ²: pares partícula-partícula, pared (imagen) y obstáculos.
    Estados con posiciones no finitas (integración que explotó) dan E_p = inf."""
    sigma = 2 * run.r
    out = np.empty(len(run.t))
    for f in range(len(run.t)):
        pos = np.column_stack((run.x[f], run.y[f]))
        if not np.all(np.isfinite(pos)):
            out[f] = np.inf
            continue
        pairs = cKDTree(pos).query_pairs(sigma, output_type="ndarray")
        xi_pairs = sigma - np.linalg.norm(pos[pairs[:, 0]] - pos[pairs[:, 1]], axis=1)
        xi_wall = np.linalg.norm(pos, axis=1) + run.r - run.big_r
        xi_obst = [sigma - np.linalg.norm(pos - o, axis=1) for o in run.obstacles]
        total = np.sum(xi_pairs[xi_pairs > 0] ** 2) + np.sum(xi_wall[xi_wall > 0] ** 2)
        total += sum(np.sum(xi[xi > 0] ** 2) for xi in xi_obst)
        out[f] = 0.5 * run.k * total
    return out


def total_energy(run: BilliardRun) -> np.ndarray:
    return kinetic_energy(run) + potential_energy(run)
