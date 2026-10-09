"""Esquema de la condición inicial con red hexagonal (--init hex) a partir de una corrida real.

Reconstruye la red con la misma regla que InitialState.hexagonal (lado a = 2r(1 + 10⁻⁹), fila
y = 0 en x = (i + ½) a, sitios con |r| <= R − r y a 2r o más de los obstáculos) y la compara con
el estado t = 0 de dynamic.txt. Cuatro paneles en analysis/figures/ej2/red_hexagonal.png:

  (a) todos los sitios libres de la red
  (b) los N sitios elegidos al azar (el resto, punteado)
  (c) velocidades iniciales: módulo v0, dirección al azar
  (d) ampliación alrededor de los obstáculos: vecinas a distancia 2r (tocándose sin superponerse)

Uso:
    java -jar md-java/target/md.jar billiard --scheme velocity-verlet --n 300 --init hex --xo 0.0175 \\
        --dt 1e-5 --tf 1e-5 --save-dt 1e-5 --out output/billiard/hex_demo_N300_s1
    python3 analysis/plot_hex_init.py output/billiard/hex_demo_N300_s1
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
from matplotlib.collections import EllipseCollection
from matplotlib.patches import Circle, Rectangle

from billiard_common import load_run
from common import save_figure

import matplotlib.pyplot as plt  # noqa: E402  (common configura el backend)

LATTICE_MARGIN = 1e-9  # el mismo de InitialState
SITE, CHOSEN, OBSTACLE, WALL = "0.55", "tab:blue", "black", "0.45"


def lattice_sites(big_r: float, r: float, obstacles: np.ndarray) -> np.ndarray:
    a = 2 * r * (1 + LATTICE_MARGIN)
    row = a * np.sqrt(3) / 2
    max_radius = big_r - r
    rows, cols = int(np.ceil(max_radius / row)), int(np.ceil(max_radius / a)) + 1
    sites = []
    for j in range(-rows, rows + 1):
        shift = 0.5 * a if j % 2 == 0 else 0.0
        for i in range(-cols, cols + 1):
            p = np.array([i * a + shift, j * row])
            if p @ p > max_radius**2:
                continue
            if all((p - o) @ (p - o) >= 4 * r * r for o in obstacles):
                sites.append(p)
    return np.array(sites)


def discs(ax, centers, r, **kwargs) -> None:
    d = np.full(len(centers), 2 * r)
    ax.add_collection(EllipseCollection(d, d, 0, units="xy", offsets=centers, offset_transform=ax.transData,
                                        **kwargs))


def frame(ax, run, lim=None) -> None:
    ax.add_patch(Circle((0, 0), run.big_r, fill=False, edgecolor=WALL, linewidth=2, zorder=1))
    discs(ax, run.obstacles, run.r, facecolors=OBSTACLE, zorder=4)
    lim = lim or (-run.big_r * 1.03, run.big_r * 1.03, -run.big_r * 1.03, run.big_r * 1.03)
    ax.set_xlim(lim[0], lim[1])
    ax.set_ylim(lim[2], lim[3])
    ax.set_aspect("equal")
    ax.set_xlabel("x (m)")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("run_dir", type=Path)
    args = ap.parse_args()

    run = load_run(args.run_dir)
    sites = lattice_sites(run.big_r, run.r, run.obstacles)
    chosen = np.column_stack((run.x[0], run.y[0]))
    # Cada partícula tiene que estar en un sitio de la red reconstruida.
    dist = np.min(np.linalg.norm(chosen[:, None, :] - sites[None, :, :], axis=2), axis=1)
    print(f"sitios libres {len(sites)}, elegidos N = {run.n}; distancia máx. partícula–sitio {dist.max():.1e} m")
    free = sites[np.min(np.linalg.norm(sites[:, None, :] - chosen[None, :, :], axis=2), axis=1) > 1e-9]

    plt.rcParams.update({"font.family": "STIXGeneral", "mathtext.fontset": "stix", "font.size": 15})
    fig, axes = plt.subplots(1, 4, figsize=(17, 4.8), constrained_layout=True)
    a, b, c, d = axes

    frame(a, run)
    discs(a, sites, run.r, facecolors="none", edgecolors=SITE, linewidths=0.6, zorder=2)
    a.set_ylabel("y (m)")

    frame(b, run)
    discs(b, free, run.r, facecolors="none", edgecolors=SITE, linewidths=0.5, linestyles=":", zorder=2)
    discs(b, chosen, run.r, facecolors=CHOSEN, edgecolors="none", alpha=0.85, zorder=3)

    frame(c, run)
    discs(c, chosen, run.r, facecolors=CHOSEN, edgecolors="none", alpha=0.35, zorder=3)
    c.quiver(run.x[0], run.y[0], run.vx[0], run.vy[0], angles="xy", scale_units="xy", scale=1 / 0.05,
             width=0.004, color="black", zorder=5)

    half = 5 * run.r
    frame(d, run, lim=(-half, half, -half, half))
    discs(d, free, run.r, facecolors="none", edgecolors=SITE, linewidths=1.0, linestyles=":", zorder=2)
    discs(d, chosen, run.r, facecolors=CHOSEN, edgecolors="white", linewidths=1.0, alpha=0.85, zorder=3)
    for ax in (a, b, c):
        ax.add_patch(Rectangle((-half, -half), 2 * half, 2 * half, fill=False, edgecolor="tab:red", lw=1.2,
                               zorder=6))

    for ax, letter in zip(axes, "abcd"):
        ax.set_title(f"({letter})", loc="left")
    save_figure(fig, "ej2", "red_hexagonal.png")


if __name__ == "__main__":
    main()
