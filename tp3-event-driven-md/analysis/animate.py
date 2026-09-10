"""Animación de una corrida a partir de `static.txt` + `dynamic.txt` (escrito con `--every 1`).

Entre eventos las partículas hacen MRU, así que el estado en un instante arbitrario t se obtiene
exactamente avanzando el último bloque con t_b <= t: r(t) = r(t_b) + v (t - t_b). Con eso se
muestrea a fps constante sin depender del espaciado irregular de los eventos.

Colores: fresca azul, usada roja; obstáculos gris; arcos en verde sobre las paredes cortas.

Uso:  python3 animate.py <run_dir> [--fps 30] [--speed 1.0] [--t0 0] [--t1 tf] [--out anim.mp4]
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
from matplotlib.animation import FFMpegWriter
from matplotlib.collections import EllipseCollection

from common import TP_ROOT, use_style

import matplotlib.pyplot as plt  # noqa: E402  (common configura el backend)

FRESH, USED, OBSTACLE, GOAL = "tab:blue", "tab:red", "0.35", "tab:green"


def load_static(run_dir: Path):
    with open(run_dir / "static.txt") as fh:
        n = int(fh.readline())
        L, W, d = map(float, fh.readline().split())
        radii = np.array([float(fh.readline().split()[0]) for _ in range(n)])
        k = int(fh.readline())
        obstacles = np.array([list(map(float, fh.readline().split())) for _ in range(k)])
    return n, L, W, d, radii, obstacles.reshape(k, 3)


def load_dynamic(run_dir: Path, n: int):
    """→ times (B,), state (B, N, 5) con columnas x y vx vy usada."""
    raw = np.fromstring((run_dir / "dynamic.txt").read_text(), sep=" ")
    block = 1 + 5 * n
    blocks = raw.size // block
    raw = raw[: blocks * block].reshape(blocks, block)
    return raw[:, 0], raw[:, 1:].reshape(blocks, n, 5)


def state_at(times, state, t):
    b = np.searchsorted(times, t, side="right") - 1
    s = state[b]
    pos = s[:, :2] + s[:, 2:4] * (t - times[b])
    return pos, s[:, 4] > 0.5


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("run_dir", type=Path)
    ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--speed", type=float, default=1.0, help="segundos simulados por segundo")
    ap.add_argument("--t0", type=float, default=0.0)
    ap.add_argument("--t1", type=float, default=None)
    ap.add_argument("--out", type=Path, default=None)
    ap.add_argument("--snapshot", type=float, default=None,
                    help="en vez de un video, guardar un PNG del estado en este instante (s)")
    args = ap.parse_args()

    n, L, W, d, radii, obstacles = load_static(args.run_dir)
    times, state = load_dynamic(args.run_dir, n)
    t1 = times[-1] if args.t1 is None else args.t1
    frame_times = np.arange(args.t0, t1, args.speed / args.fps)
    out = args.out or args.run_dir / "anim.mp4"

    use_style()
    fig, ax = plt.subplots(figsize=(8, 8 * W / L + 0.5))
    ax.set_xlim(0, L)
    ax.set_ylim(0, W)
    ax.set_aspect("equal")
    ax.set_xlabel("x (m)")
    ax.set_ylabel("y (m)")
    for x in (0.0, L):
        ax.plot([x, x], [W / 2 - d / 2, W / 2 + d / 2], color=GOAL, linewidth=6,
                solid_capstyle="butt", zorder=3)
    if len(obstacles):
        ax.add_collection(EllipseCollection(
            2 * obstacles[:, 2], 2 * obstacles[:, 2], 0, units="xy", offsets=obstacles[:, :2],
            offset_transform=ax.transData, facecolors=OBSTACLE, edgecolors="none", zorder=1))
    pos0, used0 = state_at(times, state, frame_times[0])
    balls = EllipseCollection(2 * radii, 2 * radii, 0, units="xy", offsets=pos0,
                              offset_transform=ax.transData, edgecolors="none", zorder=2)
    ax.add_collection(balls)
    label = ax.text(0.01, 1.02, "", transform=ax.transAxes, ha="left", va="bottom")

    def render(t):
        pos, used = state_at(times, state, t)
        balls.set_offsets(pos)
        balls.set_facecolors(np.where(used, USED, FRESH))
        label.set_text(f"t = {t:5.2f} s    goles = {int(used.sum())}/{n}")

    if args.snapshot is not None:
        out = args.out or args.run_dir / f"snapshot_{args.snapshot:.1f}s.png"
        render(args.snapshot)
        fig.savefig(out, dpi=120)
        plt.close(fig)
        print(f"  {out}")
        return

    writer = FFMpegWriter(fps=args.fps, bitrate=2500)
    with writer.saving(fig, out, dpi=120):
        for t in frame_times:
            render(t)
            writer.grab_frame()
    plt.close(fig)
    print(f"  {out.relative_to(TP_ROOT) if out.is_relative_to(TP_ROOT) else out}  "
          f"({len(frame_times)} cuadros, {len(frame_times) / args.fps:.1f} s)")


if __name__ == "__main__":
    main()
