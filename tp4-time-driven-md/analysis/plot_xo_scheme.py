"""Punto 2.2: esquemas de las configuraciones simuladas, a escala, leídos de las corridas reales.

Lee output/billiard/xo_sweep/N<N>/xo<x_o>/s<seed>/ (scripts/run_xo_sweep.sh): R, r y los centros
de los obstáculos de static.txt / run.json, y el estado t = 0 de dynamic.txt.

Figuras en analysis/figures/ej2/:
  esquema_xo.png        una mesa por x_o barrido (obstáculos a escala); los x_o de --fu-xo con los
                        colores de fu_vs_t_xo_N<N>.png, el resto en gris; último panel con las
                        dimensiones R, r y x_o
  esquema_densidad.png  estado inicial (red hexagonal, semilla --seed) de cada N barrido en el
                        x_o de --density-xo, con las velocidades iniciales

Uso: python3 analysis/plot_xo_scheme.py [--root DIR] [--fu-xo 0.0175,0.25,0.4925]
                                        [--density-xo 0.25] [--seed 1]
"""

from __future__ import annotations

import argparse
import math
from pathlib import Path

import numpy as np
from matplotlib.patches import Circle

from billiard_common import load_run
from common import TP_ROOT, save_figure, use_style
from plot_hex_init import discs

import matplotlib.pyplot as plt  # noqa: E402  (después de common: backend Agg)

DEFAULT_ROOT = TP_ROOT / "output" / "billiard" / "xo_sweep"
FU_COLORS = ("tab:blue", "tab:red", "black", "tab:purple")  # los de plot_xo.plot_fu, mismo orden
OTHER, WALL, PARTICLE = "0.6", "0.35", "tab:blue"


def table(ax, big_r: float, lim: float) -> None:
    ax.add_patch(Circle((0, 0), big_r, fill=False, edgecolor=WALL, linewidth=1.5, zorder=1))
    ax.set_xlim(-lim, lim)
    ax.set_ylim(-lim, lim)
    ax.set_aspect("equal")
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)


def first_runs(root: Path, n: int, seed: int) -> dict[float, Path]:
    """→ {x_o: directorio de la corrida de esa semilla}, ordenado por x_o."""
    runs = {}
    for path in root.glob(f"N{n}/xo*/s{seed}"):
        if (path / "run.json").exists():
            runs[float(path.parent.name.removeprefix("xo"))] = path
    return dict(sorted(runs.items()))


def plot_positions(runs: dict[float, Path], fu_xos: list[float]) -> None:
    cols = 6
    rows = math.ceil((len(runs) + 1) / cols)
    fig, axes = plt.subplots(rows, cols, figsize=(8.0, 1.55 * rows + 0.2))
    axes = axes.ravel()
    run = None
    for ax, (xo, path) in zip(axes, runs.items()):
        run = load_run(path)
        lim = 1.04 * run.big_r
        table(ax, run.big_r, lim)
        typical = [i for i, x in enumerate(fu_xos) if math.isclose(x, xo, abs_tol=1e-9)]
        color = FU_COLORS[typical[0] % len(FU_COLORS)] if typical else OTHER
        discs(ax, run.obstacles, run.r, facecolors=color, edgecolors=color, linewidths=0.5, zorder=2)
        ax.set_xlabel(f"$x_o$ = {xo:g} m", fontsize=11)
    if run is None:
        raise SystemExit("sin corridas")

    # Panel de referencia: dimensiones, con un x_o intermedio
    ax = axes[len(runs)]
    big_r, r, xo = run.big_r, run.r, 0.25
    lim = 1.04 * big_r
    table(ax, big_r, lim)
    discs(ax, np.array([[-xo, 0.0], [xo, 0.0]]), r, facecolors="black", edgecolors="black", zorder=2)
    ax.annotate("", xy=(big_r * math.cos(2.2), big_r * math.sin(2.2)), xytext=(0, 0),
                arrowprops=dict(arrowstyle="->", lw=1.0, color=WALL, shrinkA=0, shrinkB=0))
    ax.text(-0.17, 0.28, "$R$", fontsize=12, color=WALL, ha="center", va="center")
    ax.annotate("", xy=(xo, -0.09), xytext=(0, -0.09),
                arrowprops=dict(arrowstyle="<->", lw=1.0, color="black", shrinkA=0, shrinkB=0))
    ax.plot([0, 0], [-0.13, 0.03], color="black", lw=0.6, ls=":")
    ax.text(xo / 2, -0.17, "$x_o$", fontsize=12, ha="center", va="center")
    ax.text(xo, 0.09, "$r$", fontsize=12, ha="center", va="center")
    ax.set_xlabel(f"$R$ = {big_r:g} m\n$r$ = {r:g} m", fontsize=11, linespacing=1.1)
    for ax in axes[len(runs) + 1:]:
        ax.set_visible(False)
    fig.get_layout_engine().set(w_pad=0.02, h_pad=0.02, wspace=0.02, hspace=0.05)
    save_figure(fig, "ej2", "esquema_xo.png")


def plot_density(root: Path, ns: list[int], xo: float, seed: int) -> None:
    fig, axes = plt.subplots(1, len(ns), figsize=(2.6 * len(ns), 2.9))
    for ax, n in zip(np.atleast_1d(axes), ns):
        run = load_run(root / f"N{n}" / f"xo{xo:g}" / f"s{seed}")
        lim = 1.03 * run.big_r
        table(ax, run.big_r, lim)
        centers = np.column_stack([run.x[0], run.y[0]])
        discs(ax, centers, run.r, facecolors=PARTICLE, edgecolors="none", alpha=0.8, zorder=2)
        discs(ax, run.obstacles, run.r, facecolors="black", edgecolors="black", zorder=3)
        scale = 0.06 / run.meta["v0"]  # flecha de 0.06 m para |v| = v0
        ax.quiver(run.x[0], run.y[0], scale * run.vx[0], scale * run.vy[0], angles="xy", scale_units="xy",
                  scale=1, width=0.006, color="0.15", zorder=4)
        density = n / (math.pi * run.big_r**2)
        ax.set_xlabel(f"$N$ = {n}  ({density:.0f} m$^{{-2}}$)", fontsize=12)
        print(f"  N = {n}: densidad {density:.1f} m⁻², fracción de área {n * run.r**2 / run.big_r**2:.3f}")
    save_figure(fig, "ej2", "esquema_densidad.png")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--fu-xo", default="0.0175,0.25,0.4925", help="x_o de fu_vs_t_xo_N<N>.png, separados por coma")
    parser.add_argument("--density-xo", type=float, default=0.25)
    parser.add_argument("--seed", type=int, default=1)
    args = parser.parse_args()
    ns = sorted((int(p.name.removeprefix("N")) for p in args.root.glob("N*")), reverse=True)
    if not ns:
        raise SystemExit(f"sin corridas en {args.root}")
    use_style()
    plot_positions(first_runs(args.root, ns[0], args.seed), [float(v) for v in args.fu_xo.split(",")])
    plot_density(args.root, ns, args.density_xo, args.seed)


if __name__ == "__main__":
    main()
