"""Punto 2.2, discusión: frecuencia de choques en función de la posición de los obstáculos, para
N = 100 y N = 20 (¿el x_o óptimo depende de la frecuencia de choques entre partículas?).

Lee output/billiard/xo_sweep/N<N>/xo<x_o>/s<seed>/ (scripts/run_xo_sweep.sh, con --log-collisions):
collisions.csv (un choque por episodio de contacto, en el primer paso con ξ > 0), conversions.csv y
run.json.

Definiciones, por realización, sobre la ventana [0, t_90] (t_90 como en plot_xo.py):
  ν_pp = 2 C_pp / (N t_90)   choques entre partículas por partícula y por segundo (s⁻¹); C_pp =
                             choques partícula-partícula con t ≤ t_90 (cada uno involucra 2)
  ν_o  = C_o / t_90          choques contra los dos obstáculos por segundo (s⁻¹); C_o = choques
                             partícula-obstáculo con t ≤ t_90
  η    = ⌈0.9 N⌉ / C_o       fracción de los choques con obstáculos que convierten (solo stdout)
Por (N, x_o): promedio entre realizaciones ± desvío estándar entre realizaciones (ddof = 1; un
escalar por realización), solo si todas llegan a t_90.

Figuras en analysis/figures/ej2/: choques_particulas_vs_xo.png (ν_pp) y
choques_obstaculos_vs_xo.png (ν_o), las dos densidades en cada una. Tabla por stdout.

Uso: python3 analysis/plot_collisions_xo.py [--root DIR]
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np

from common import TP_ROOT, decade_ticks, save_figure, use_style
from plot_xo import COLORS, MARKERS

import matplotlib.pyplot as plt  # noqa: E402  (después de common: backend Agg)

DEFAULT_ROOT = TP_ROOT / "output" / "billiard" / "xo_sweep"


def rates(run_dir: Path) -> tuple[int, float, float, float, float] | None:
    """→ (N, x_o, ν_pp, ν_o, η) de una corrida, o None si no llega a t_90."""
    meta = json.loads((run_dir / "run.json").read_text())
    if not meta.get("collisionsLogged"):
        raise SystemExit(f"{run_dir} no tiene collisions.csv: correr con --log-collisions")
    n = meta["N"]
    conv = np.loadtxt(run_dir / "conversions.csv", delimiter=",", skiprows=1, ndmin=2)
    k90 = math.ceil(0.9 * n - 1e-9)
    if conv.shape[0] < k90:
        return None
    t90 = float(np.sort(conv[:, 0])[k90 - 1])
    t, kind = [], []
    with open(run_dir / "collisions.csv") as f:
        next(f)
        for line in f:
            ti, ki, _ = line.split(",", 2)
            t.append(float(ti))
            kind.append(ki)
    t, kind = np.array(t), np.array(kind)
    window = t <= t90
    c_pp = np.count_nonzero(window & (kind == "particle"))
    c_o = np.count_nonzero(window & (kind == "obstacle"))
    return n, meta["xo"], 2 * c_pp / (n * t90), c_o / t90, k90 / c_o


def mean_std(values: list[float]) -> tuple[float, float]:
    v = np.array(values)
    return float(v.mean()), float(v.std(ddof=1)) if v.size > 1 else 0.0


def plot(table: dict[int, dict[float, list[tuple[float, float, float]]]], column: int, ylabel: str,
         name: str) -> None:
    fig, ax = plt.subplots()
    lows, highs = [], []
    for n, by_xo in table.items():
        rows = [(xo, *mean_std([r[column] for r in rs])) for xo, rs in by_xo.items()]
        xo, mean, std = (np.array(c) for c in zip(*rows))
        # Desvíos de ~1 % en ν_pp: marcador chico y relleno, tapas anchas (como tiempo_vs_n.png).
        ax.errorbar(xo, mean, yerr=std, fmt=MARKERS.get(n, "o") + "-", color=COLORS.get(n), ms=4, lw=1.0,
                    elinewidth=1.5, capsize=6, capthick=1.5, label=str(n))
        lows.append(np.min(mean - std))
        highs.append(np.max(mean + std))
    lo, hi = min(lows), max(highs)
    if lo > 0 and hi / lo > 10:
        ax.set_yscale("log")
        lo_e, hi_e = int(np.floor(np.log10(lo))), int(np.ceil(np.log10(hi)))
        ax.set_ylim(10.0**lo_e, 10.0**hi_e)
        decade_ticks(ax.yaxis, lo_e, hi_e)
    else:
        ax.set_ylim(0, None)
    ax.set_xlabel("Posición de los obstáculos (m)")
    ax.set_ylabel(ylabel)
    ax.legend(title="N", loc="best")
    save_figure(fig, "ej2", name)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    args = parser.parse_args()

    # table[N][x_o] = [(ν_pp, ν_o, η) por realización]; x_o con alguna realización sin t_90 se descartan.
    table: dict[int, dict[float, list[tuple[float, float, float]]]] = {}
    incomplete: set[tuple[int, float]] = set()
    for meta_path in sorted(args.root.glob("N*/xo*/s*/run.json")):
        result = rates(meta_path.parent)
        meta = json.loads(meta_path.read_text())
        if result is None:
            incomplete.add((meta["N"], meta["xo"]))
            continue
        n, xo, nu_pp, nu_o, eta = result
        table.setdefault(n, {}).setdefault(xo, []).append((nu_pp, nu_o, eta))
    for n, xo in incomplete:
        table.get(n, {}).pop(xo, None)
        print(f"N = {n}, x_o = {xo}: alguna realización no llega a t_90, fuera de las figuras")
    if not table:
        raise SystemExit(f"sin corridas en {args.root}")
    table = {n: dict(sorted(by_xo.items())) for n, by_xo in sorted(table.items(), reverse=True)}

    for n, by_xo in table.items():
        print(f"\nN = {n}: x_o (m) | realizaciones | ν_pp (s⁻¹) | ν_o (s⁻¹) | η (fracción que convierte)")
        for xo, rs in by_xo.items():
            cols = [mean_std([r[c] for r in rs]) for c in range(3)]
            print(f"  {xo:.4f} | {len(rs)} | " + " | ".join(f"{m:.4g} ± {s:.2g}" for m, s in cols))

    use_style()
    plot(table, 0, "Choques entre partículas\npor partícula (s$^{-1}$)", "choques_particulas_vs_xo.png")
    plot(table, 1, "Choques con obstáculos (s$^{-1}$)", "choques_obstaculos_vs_xo.png")


if __name__ == "__main__":
    main()
