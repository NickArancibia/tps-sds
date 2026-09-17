"""Esquema de configuraciones de obstáculos (formato Config.txt) sobre la mesa, con los arcos.

Uso:  python3 plot_configs.py <config.txt> [<config.txt> ...] [--out nombre.png]
                              [--labels "h = 0.20 m" ...] [--cols 3]
Con varios archivos arma una grilla de paneles. Rótulo de cada panel: `--labels` (uno por
archivo, para figuras de presentación: solo el valor de la variable) o, por default, la ruta
relativa a output/sweeps (uso interno).
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


def draw(ax, config: Path, title: str, fontsize: float = 9) -> None:
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
    if title:
        ax.text(0.5, -0.04, title, transform=ax.transAxes, ha="center", va="top",
                fontsize=fontsize)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("configs", nargs="+", type=Path)
    ap.add_argument("--out", default="configs.png")
    ap.add_argument("--labels", nargs="*", default=None)
    ap.add_argument("--cols", type=int, default=3)
    args = ap.parse_args()
    if args.labels is not None and len(args.labels) != len(args.configs):
        raise SystemExit("--labels: uno por archivo de configuración")

    use_style()
    n = len(args.configs)
    cols = min(args.cols, n)
    rows = math.ceil(n / cols)
    fig, axes = plt.subplots(rows, cols, figsize=(3.2 * cols, 2.1 * rows), squeeze=False)
    for ax in axes.flat:
        ax.axis("off")
    for i, (ax, cfg) in enumerate(zip(axes.flat, args.configs)):
        ax.axis("on")
        if args.labels is not None:
            draw(ax, cfg, args.labels[i], fontsize=13)
        else:
            try:
                title = str(cfg.resolve().relative_to(OUTPUT / "sweeps").parent)
            except ValueError:
                title = cfg.stem
            draw(ax, cfg, title)
    save_figure(fig, args.out)


if __name__ == "__main__":
    main()
