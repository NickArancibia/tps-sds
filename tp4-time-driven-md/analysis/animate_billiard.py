"""Animación de una corrida del billar (sistema 2) a partir de static.txt + dynamic.txt.

Cada cuadro es un estado guardado en dynamic.txt, dibujado tal cual (no se interpola): el video
avanza save-dt·stride segundos simulados por cuadro. Las partículas se dibujan semitransparentes
para que la superposición ξ de los contactos (resorte) se vea como una zona más oscura.
Frescas en azul, usadas en rojo, obstáculos en negro, pared en gris.

Uso:
    python3 analysis/animate_billiard.py <corrida> [--fps 30] [--stride k] [--t0 s] [--t1 s]
        [--zoom X Y HALF] [--out video.mp4]
    python3 analysis/animate_billiard.py <corrida> --snapshot T [--zoom ...]   # PNG del estado con t >= T

--zoom X Y HALF muestra solo el cuadrado [X − HALF, X + HALF] × [Y − HALF, Y + HALF] (m).
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
from matplotlib.animation import FFMpegWriter
from matplotlib.collections import EllipseCollection
from matplotlib.colors import to_rgba
from matplotlib.patches import Circle

from billiard_common import load_run
from common import TP_ROOT

import matplotlib.pyplot as plt  # noqa: E402  (common configura el backend)

FRESH, USED, OBSTACLE, WALL = "tab:blue", "tab:red", "black", "0.45"
FILL_ALPHA = 0.45


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("run_dir", type=Path)
    ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--stride", type=int, default=1, help="usar uno de cada k estados guardados")
    ap.add_argument("--t0", type=float, default=None, help="solo estados con t >= t0 (s)")
    ap.add_argument("--t1", type=float, default=None, help="solo estados con t <= t1 (s)")
    ap.add_argument("--zoom", type=float, nargs=3, metavar=("X", "Y", "HALF"), default=None)
    ap.add_argument("--snapshot", type=float, default=None, help="PNG del primer estado con t >= este valor (s)")
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args()

    run = load_run(args.run_dir)
    plt.rcParams.update({"font.family": "STIXGeneral", "mathtext.fontset": "stix", "font.size": 20})
    fig, ax = plt.subplots(figsize=(8.6, 9.2), constrained_layout=True)
    ax.set_aspect("equal")
    if args.zoom:
        x, y, half = args.zoom
        ax.set_xlim(x - half, x + half)
        ax.set_ylim(y - half, y + half)
    else:
        lim = run.big_r * 1.02
        ax.set_xlim(-lim, lim)
        ax.set_ylim(-lim, lim)
    ax.set_xlabel("x (m)")
    ax.set_ylabel("y (m)")
    ax.add_patch(Circle((0, 0), run.big_r, fill=False, edgecolor=WALL, linewidth=3, zorder=1))
    if len(run.obstacles):
        ax.add_collection(EllipseCollection(
            np.full(len(run.obstacles), 2 * run.r), np.full(len(run.obstacles), 2 * run.r), 0, units="xy",
            offsets=run.obstacles, offset_transform=ax.transData, facecolors=OBSTACLE, zorder=2))
    diameters = np.full(run.n, 2 * run.r)
    balls = EllipseCollection(diameters, diameters, 0, units="xy", offsets=np.zeros((run.n, 2)),
                              offset_transform=ax.transData, linewidths=1.2, zorder=3)
    ax.add_collection(balls)
    label = ax.text(0.0, 1.01, "", transform=ax.transAxes, ha="left", va="bottom")

    fill = {False: to_rgba(FRESH, FILL_ALPHA), True: to_rgba(USED, FILL_ALPHA)}
    edge = {False: to_rgba(FRESH), True: to_rgba(USED)}

    def render(f: int) -> None:
        used = run.used[f]
        balls.set_offsets(np.column_stack((run.x[f], run.y[f])))
        balls.set_facecolors([fill[bool(u)] for u in used])
        balls.set_edgecolors([edge[bool(u)] for u in used])
        label.set_text(f"t = {run.t[f]:.4f} s    usadas = {int(used.sum())}/{run.n}")

    if args.snapshot is not None:
        f = int(np.argmax(run.t >= args.snapshot)) if (run.t >= args.snapshot).any() else len(run.t) - 1
        out = args.out or args.run_dir / f"snapshot_{run.t[f]:.4f}s.png"
        render(f)
        fig.savefig(out, dpi=120)
        plt.close(fig)
        print(f"  estado {f}, t = {run.t[f]} s → {out}")
        return

    idx = np.arange(len(run.t))
    if args.t0 is not None:
        idx = idx[run.t[idx] >= args.t0]
    if args.t1 is not None:
        idx = idx[run.t[idx] <= args.t1]
    frames = idx[:: max(1, args.stride)]
    if frames.size == 0:
        raise SystemExit("No hay estados guardados en el rango pedido")
    out = args.out or args.run_dir / "animation.mp4"
    writer = FFMpegWriter(fps=args.fps, bitrate=4000)
    with writer.saving(fig, out, dpi=120):
        for f in frames:
            render(f)
            writer.grab_frame()
    plt.close(fig)
    step = np.diff(run.t[frames])
    shown = out.relative_to(TP_ROOT) if out.is_relative_to(TP_ROOT) else out
    print(f"  {shown}  ({frames.size} cuadros = {frames.size / args.fps:.1f} s de video; "
          f"t = {run.t[frames[0]]:.4f} → {run.t[frames[-1]]:.4f} s simulados; "
          f"{step.mean() if step.size else 0:.4g} s simulados por cuadro, "
          f"{step.mean() * args.fps if step.size else 0:.3g} s simulados por s de video)")


if __name__ == "__main__":
    main()
