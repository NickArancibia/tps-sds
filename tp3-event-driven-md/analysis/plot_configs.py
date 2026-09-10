"""Esquema de configuraciones de obstáculos (formato Config.txt) sobre la mesa, con los arcos.

Uso:  python3 plot_configs.py <config.txt> [<config.txt> ...] [--out nombre.png]
Con varios archivos arma una grilla de paneles, rotulados con la ruta relativa a output/sweeps.
"""

from __future__ import annotations

import argparse
import math
from pathlib import Path

import numpy as np
from matplotlib.patches import Circle

from common import OUTPUT, save_figure, use_style

import matplotlib.pyplot as plt  # noqa: E402

L, W, D = 1.20, 0.68, 0.20


def draw(ax, config: Path, title: str) -> None:
    obs = np.loadtxt(config, ndmin=2)
    ax.set_xlim(0, L)
    ax.set_ylim(0, W)
    ax.set_aspect("equal")
    ax.set_xticks([])
    ax.set_yticks([])
    for x in (0.0, L):
        ax.plot([x, x], [W / 2 - D / 2, W / 2 + D / 2], color="tab:green", linewidth=4,
                solid_capstyle="butt")
    for x, y, r in obs:
        ax.add_patch(Circle((x, y), r, facecolor="0.35", edgecolor="none"))
    ax.text(0.5, -0.04, title, transform=ax.transAxes, ha="center", va="top", fontsize=9)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("configs", nargs="+", type=Path)
    ap.add_argument("--out", default="configs.png")
    args = ap.parse_args()

    use_style()
    n = len(args.configs)
    cols = min(3, n)
    rows = math.ceil(n / cols)
    fig, axes = plt.subplots(rows, cols, figsize=(3.2 * cols, 2.1 * rows), squeeze=False)
    for ax in axes.flat:
        ax.axis("off")
    for ax, cfg in zip(axes.flat, args.configs):
        ax.axis("on")
        try:
            title = str(cfg.resolve().relative_to(OUTPUT / "sweeps").parent)
        except ValueError:
            title = cfg.stem
        draw(ax, cfg, title)
    save_figure(fig, args.out)


if __name__ == "__main__":
    main()
