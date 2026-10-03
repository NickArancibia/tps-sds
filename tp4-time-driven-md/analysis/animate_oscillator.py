"""Animación de una corrida del sistema 1: masa-resorte arriba y r(t) numérica contra la analítica
abajo. Cada cuadro es un estado guardado en `trajectory.csv` (no se interpola).

Uso:
    python3 analysis/animate_oscillator.py output/oscillator/<corrida> [--fps 25] [--out video.mp4]

Con save-dt = 10⁻² s y 25 cuadros/s el video va a 1/4 de la velocidad real.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.animation import FFMpegWriter, FuncAnimation  # noqa: E402

from oscillator_common import analytic, load_run  # noqa: E402

SCHEME_NAMES = {
    "beeman": "Beeman",
    "verlet": "Verlet original",
    "velocity-verlet": "Velocity Verlet",
    "euler-pc": "Euler predictor-corrector",
}
WALL_X = -1.6
BLOCK_HALF = 0.12
COILS = 12


def spring(x_end: float) -> tuple[np.ndarray, np.ndarray]:
    """Zigzag desde la pared hasta el borde izquierdo del bloque."""
    xs = np.linspace(WALL_X, x_end, 2 * COILS + 3)
    ys = np.zeros_like(xs)
    ys[1:-1:2] = 0.08
    ys[2:-1:2] = -0.08
    ys[1], ys[-2] = 0.0, 0.0
    return xs, ys


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("run_dir", type=Path)
    parser.add_argument("--fps", type=int, default=25)
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args()

    meta, t, r, _ = load_run(args.run_dir)
    t_fine = np.linspace(0.0, meta["tf"], 4000)
    out = args.out or args.run_dir / "animation.mp4"

    plt.rcParams.update({
        "font.family": "STIXGeneral",
        "mathtext.fontset": "stix",
        "font.size": 20,
        "legend.fontsize": 18,
    })
    fig, (ax_mass, ax_r) = plt.subplots(2, 1, figsize=(12.8, 7.2), height_ratios=[1, 2],
                                        constrained_layout=True)

    ax_mass.set_xlim(WALL_X - 0.05, 1.3)
    ax_mass.set_ylim(-0.25, 0.25)
    ax_mass.set_yticks([])
    ax_mass.set_xlabel("Posición (m)")
    ax_mass.axvline(0.0, color="0.6", ls=":", lw=1.2, zorder=0)
    ax_mass.fill_betweenx([-0.25, 0.25], WALL_X - 0.05, WALL_X, color="0.4")
    (spring_line,) = ax_mass.plot([], [], color="0.3", lw=1.6)
    block = plt.Rectangle((r[0] - BLOCK_HALF, -0.12), 2 * BLOCK_HALF, 0.24, color="tab:blue")
    ax_mass.add_patch(block)

    ax_r.plot(t_fine, analytic(t_fine, meta), color="black", lw=1.2, ls="--", label="analítica", zorder=1)
    (num_line,) = ax_r.plot([], [], color="tab:blue", lw=2.2, label=SCHEME_NAMES[meta["scheme"]], zorder=2)
    (num_dot,) = ax_r.plot([], [], "o", color="tab:blue", ms=9, zorder=3)
    ax_r.set_xlim(0.0, meta["tf"])
    ax_r.set_ylim(-1.05, 1.05)
    ax_r.set_xlabel("Tiempo (s)")
    ax_r.set_ylabel("Posición (m)")
    ax_r.legend(loc="upper right")
    clock = ax_r.text(0.98, 0.06, "", transform=ax_r.transAxes, ha="right", va="bottom")

    def update(i: int):
        xs, ys = spring(r[i] - BLOCK_HALF)
        spring_line.set_data(xs, ys)
        block.set_x(r[i] - BLOCK_HALF)
        num_line.set_data(t[: i + 1], r[: i + 1])
        num_dot.set_data([t[i]], [r[i]])
        clock.set_text(f"t = {t[i]:.2f} s")
        return spring_line, block, num_line, num_dot, clock

    anim = FuncAnimation(fig, update, frames=len(t), blit=True)
    anim.save(out, writer=FFMpegWriter(fps=args.fps, bitrate=4000), dpi=100)
    plt.close(fig)
    print(f"{out}  ({len(t)} cuadros a {args.fps} cuadros/s, dt = {meta['dt']} s, {meta['scheme']})")


if __name__ == "__main__":
    main()
