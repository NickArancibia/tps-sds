"""Animación de una corrida del CPM a partir de los estados guardados (sin interpolar).

Cada cuadro es un estado de dynamic.txt dibujado tal cual. Colores:
- TSDMD y EDMD puros, por estado del CPM: azul = libre (r = r_max), negro = recuperando
  (r_min < r < r_max, sin contacto), rojo = en contacto (r = r_min, velocidad de escape).
- Híbrido, solo por esquema (lo pide el enunciado): azul = EDMD, rojo = TSDMD.
Los agentes retirados no se dibujan.

Dos estilos de dibujo:
- Habitación completa: un punto de tamaño fijo por agente (a esa escala el radio no se distingue).
- Zoom (--zoom o el panel de --panel-zoom): disco sólido de radio r_min (el cuerpo) y círculo de
  radio r vigente (el espacio personal del CPM, que es lo que crece y colapsa).

Uso:
    python3 analysis/animate_evacuation.py <corrida> [--fps 30] [--stride k] [--t0 s] [--t1 s]
        [--zoom X Y HALF | --panel-zoom X Y HALF] [--arrows] [--desired] [--trails] [--info]
        [--out video.mp4]
    python3 analysis/animate_evacuation.py <corrida> --snapshot T [...]   # PNG del estado con t >= T

--zoom X Y HALF        solo [X − HALF, X + HALF] × [Y − HALF, Y + HALF] (m), estilo zoom.
--panel-zoom X Y HALF  habitación completa a la izquierda y ese zoom a la derecha.
--arrows               en el zoom, flecha de la velocidad (largo proporcional a la rapidez).
--desired              en el zoom, dirección deseada (hacia el target) de los agentes en contacto.
--trails               en el zoom, trayectoria recorrida desde el primer cuadro animado.
--info                 r, rapidez y estado de cada agente (para corridas de pocos agentes).
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.animation import FFMpegWriter  # noqa: E402
from matplotlib.collections import EllipseCollection  # noqa: E402
from matplotlib.patches import Rectangle  # noqa: E402

from cpm_common import EDMD, REMOVED, TP_ROOT, load_run  # noqa: E402

FREE, RECOVERING, CONTACT, WALL = "tab:blue", "black", "tab:red", "0.35"
STATE_NAMES = {FREE: "libre", RECOVERING: "recuperando", CONTACT: "en contacto"}
SCHEME_EDMD, SCHEME_TSDMD = "tab:blue", "tab:red"
DOT_SIZE = 30  # pt², puntos de la vista completa
ARROW_LENGTH_AT_VD = 0.35  # m de flecha para la rapidez deseada máxima
DESIRED_LENGTH = 0.25  # m
MAX_INFO_AGENTS = 6


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("run_dir", type=Path)
    ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--stride", type=int, default=1, help="usar uno de cada k estados guardados")
    ap.add_argument("--t0", type=float, default=None, help="solo estados con t >= t0 (s)")
    ap.add_argument("--t1", type=float, default=None, help="solo estados con t <= t1 (s)")
    view = ap.add_mutually_exclusive_group()
    view.add_argument("--zoom", type=float, nargs=3, metavar=("X", "Y", "HALF"), default=None)
    view.add_argument("--panel-zoom", type=float, nargs=3, metavar=("X", "Y", "HALF"), default=None)
    ap.add_argument("--arrows", action="store_true")
    ap.add_argument("--desired", action="store_true")
    ap.add_argument("--trails", action="store_true")
    ap.add_argument("--info", action="store_true")
    ap.add_argument("--snapshot", type=float, default=None, help="PNG del primer estado con t >= este valor (s)")
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args()

    run = load_run(args.run_dir)
    m = run.meta
    big_l, r_min, r_max = m["L"], m["rMin"], m["rMax"]
    by_scheme = m.get("scheme") == "hybrid"
    if args.info and run.n > MAX_INFO_AGENTS:
        raise SystemExit(f"--info es para corridas de hasta {MAX_INFO_AGENTS} agentes (esta tiene {run.n})")

    plt.rcParams.update({"font.family": "STIXGeneral", "mathtext.fontset": "stix", "font.size": 20})
    # Layout manual: sin leyenda arriba (los colores se explican al costado de la animación).
    if args.panel_zoom:
        fig, (ax_room, ax_zoom) = plt.subplots(1, 2, figsize=(17.0, 8.6))
        fig.subplots_adjust(left=0.06, right=0.99, bottom=0.09, top=0.93, wspace=0.16)
        zoom = args.panel_zoom
    elif args.zoom:
        fig, ax_zoom = plt.subplots(figsize=(9.6, 9.8))
        fig.subplots_adjust(left=0.13, right=0.97, bottom=0.08, top=0.92)
        ax_room, zoom = None, args.zoom
    else:
        fig, ax_room = plt.subplots(figsize=(9.0, 9.4))
        fig.subplots_adjust(left=0.12, right=0.97, bottom=0.08, top=0.93)
        ax_zoom, zoom = None, None

    for ax in (a for a in (ax_room, ax_zoom) if a is not None):
        ax.set_aspect("equal")
        ax.set_xlabel("x (m)")
        ax.set_ylabel("y (m)")
        draw_walls(ax, big_l, m["doorX1"], m["doorX2"], 0.6 if ax is ax_room else 0.024 * zoom[2])
    if ax_room is not None:
        ax_room.set_xlim(-1, big_l + 1)
        ax_room.set_ylim(-2, big_l + 1)
    if ax_zoom is not None:
        zx, zy, half = zoom
        ax_zoom.set_xlim(zx - half, zx + half)
        ax_zoom.set_ylim(zy - half, zy + half)
        if ax_room is not None:
            ax_room.add_patch(Rectangle((zx - half, zy - half), 2 * half, 2 * half, fill=False,
                                        edgecolor="0.3", linestyle="--", linewidth=1.5, zorder=6))

    title_ax = ax_room if ax_room is not None else ax_zoom
    label = title_ax.text(0.0, 1.01, "", transform=title_ax.transAxes, ha="left", va="bottom")
    info = None
    if args.info:
        info = ax_zoom.text(0.02, 0.98, "", transform=ax_zoom.transAxes, ha="left", va="top", fontsize=16,
                            family="monospace", bbox={"facecolor": "white", "alpha": 0.85, "edgecolor": "0.6"},
                            zorder=10)
    artists: list = []

    def render(f: int, first: int) -> None:
        for a in artists:
            a.remove()
        artists.clear()
        alive = run.phase[f] != REMOVED
        xs, ys, rs = run.x[f, alive], run.y[f, alive], run.r[f, alive]
        contact = run.contact[f, alive]
        if by_scheme:
            colors = np.where(run.scheme[f, alive] == EDMD, SCHEME_EDMD, SCHEME_TSDMD)
        else:
            colors = state_colors(contact, rs, r_max)
        if ax_room is not None:
            artists.append(ax_room.scatter(xs, ys, s=DOT_SIZE, c=colors, linewidths=0, zorder=3))
        if ax_zoom is not None:
            offsets = np.column_stack((xs, ys))
            personal = EllipseCollection(2 * rs, 2 * rs, 0, units="xy", offsets=offsets,
                                         offset_transform=ax_zoom.transData, facecolors=colors,
                                         edgecolors=colors, linewidths=2.0, alpha=0.18, zorder=3)
            rings = EllipseCollection(2 * rs, 2 * rs, 0, units="xy", offsets=offsets,
                                      offset_transform=ax_zoom.transData, facecolors="none",
                                      edgecolors=colors, linewidths=2.0, zorder=3)
            body = np.full(len(xs), 2 * r_min)
            bodies = EllipseCollection(body, body, 0, units="xy", offsets=offsets,
                                       offset_transform=ax_zoom.transData, facecolors=colors,
                                       edgecolors="none", alpha=0.9, zorder=4)
            for c in (personal, rings, bodies):
                ax_zoom.add_collection(c)
                artists.append(c)
            if args.trails:
                for i in np.flatnonzero(alive):
                    artists.extend(ax_zoom.plot(run.x[first:f + 1, i], run.y[first:f + 1, i], color="0.55",
                                                linewidth=1.2, linestyle=":", zorder=2))
            if args.arrows:
                vx, vy = run.vx[f, alive], run.vy[f, alive]
                moving = np.hypot(vx, vy) > 0
                artists.append(ax_zoom.quiver(xs[moving], ys[moving], vx[moving], vy[moving], angles="xy",
                                              scale_units="xy", scale=m["vdMax"] / ARROW_LENGTH_AT_VD,
                                              width=0.005, color="black", edgecolor="white", linewidth=1.0,
                                              zorder=6))
            if args.desired and contact.any():
                dx = run.tx[f, alive][contact] - xs[contact]
                dy = run.ty[f, alive][contact] - ys[contact]
                norm = np.hypot(dx, dy)
                ok = norm > 0
                artists.append(ax_zoom.quiver(xs[contact][ok], ys[contact][ok], dx[ok] / norm[ok],
                                              dy[ok] / norm[ok], angles="xy", scale_units="xy",
                                              scale=1 / DESIRED_LENGTH, width=0.004, color="0.5", zorder=5))
        inside = int(np.sum(run.phase[f] == 0))
        label.set_text(f"t = {run.t[f]:.3f} s    en la habitación: {inside}/{run.n}")
        if info is not None:
            lines = []
            for i in range(run.n):
                if run.phase[f, i] == REMOVED:
                    lines.append(f"agente {i + 1}: retirado")
                    continue
                state = STATE_NAMES[state_colors(run.contact[f, i:i + 1], run.r[f, i:i + 1], r_max)[0]]
                speed = np.hypot(run.vx[f, i], run.vy[f, i])
                lines.append(f"agente {i + 1}: r = {run.r[f, i]:.3f} m  |v| = {speed:.2f} m/s  {state}")
            if run.n == 2 and not (run.phase[f] == REMOVED).any():
                gap = np.hypot(run.x[f, 0] - run.x[f, 1], run.y[f, 0] - run.y[f, 1])
                lines.append(f"distancia = {gap:.3f} m   r1 + r2 = {run.r[f].sum():.3f} m")
            info.set_text("\n".join(lines))

    if args.snapshot is not None:
        hit = run.t >= args.snapshot
        f = int(np.argmax(hit)) if hit.any() else len(run.t) - 1
        out = args.out or args.run_dir / f"snapshot_{run.t[f]:.3f}s.png"
        render(f, f)
        fig.savefig(out, dpi=110)
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
    writer = FFMpegWriter(fps=args.fps, bitrate=6000)
    with writer.saving(fig, out, dpi=110):
        for f in frames:
            render(f, frames[0])
            writer.grab_frame()
    plt.close(fig)
    step = np.diff(run.t[frames])
    shown = out.relative_to(TP_ROOT) if out.is_relative_to(TP_ROOT) else out
    print(f"  {shown}  ({frames.size} cuadros = {frames.size / args.fps:.1f} s de video; "
          f"t = {run.t[frames[0]]:.3f} → {run.t[frames[-1]]:.3f} s simulados; "
          f"{step.mean() if step.size else 0:.4g} s simulados por cuadro, "
          f"{step.mean() * args.fps if step.size else 0:.3g} s simulados por s de video)")


def state_colors(contact: np.ndarray, r: np.ndarray, r_max: float) -> np.ndarray:
    free = ~contact & (r >= r_max - 1e-9)
    return np.where(contact, CONTACT, np.where(free, FREE, RECOVERING))


def draw_walls(ax, big_l: float, x1: float, x2: float, t: float) -> None:
    """Paredes como franjas de espesor t (m) del lado de afuera: la cara interna queda exactamente en
    la posición de la pared, así que un cuerpo que la toca no parece superponerse."""
    bands = [
        (-t, -t, t, big_l + 2 * t),          # izquierda
        (big_l, -t, t, big_l + 2 * t),       # derecha
        (-t, big_l, big_l + 2 * t, t),       # superior
        (-t, -t, x1 + t, t),                 # inferior, a la izquierda de la puerta
        (x2, -t, big_l - x2 + t, t),         # inferior, a la derecha de la puerta
    ]
    for x, y, w, h in bands:
        ax.add_patch(Rectangle((x, y), w, h, facecolor=WALL, edgecolor="none", zorder=1))


if __name__ == "__main__":
    main()
