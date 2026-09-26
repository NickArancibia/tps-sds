"""Animación de una corrida a partir de `static.txt` + `dynamic.txt` (outputs primarios del motor).

Regla de la cátedra para este TP (simulación dirigida por eventos): NO se permite ningún tipo de
interpolación, búsqueda o uso de tiempos que no correspondan a eventos, ni para animar ni para
ningún otro fin. Por eso cada cuadro del video es EXACTAMENTE un bloque de `dynamic.txt`, o sea el
estado que escribió el motor en el instante de un evento: posiciones y estado (fresca/usada) tal
cual están en el archivo, sin avanzar en MRU ni interpolar. El tiempo que se muestra en el cuadro
es el instante t de ese evento.

Qué bloques se usan (solo se elige entre los instantes de eventos, nunca se evalúa el estado en
otro t):
- `--stride k`: uno de cada k bloques (el primero del rango y luego cada k). Si `dynamic.txt` se
  escribió con `--every e`, dos cuadros consecutivos están separados por k·e eventos.
- Sin `--stride`, k se elige para que el video dure en promedio (t_último − t_primero)/`--speed`
  segundos a `--fps` cuadros por segundo: k = round(bloques / (fps · duración)). Como los eventos
  no están equiespaciados en el tiempo, la reproducción NO es en tiempo real: cada cuadro avanza
  un número fijo de eventos y un tiempo simulado variable (el t de cada cuadro está en pantalla).
- `--first/--last` (índices de bloque) o `--t0/--t1` (se usan los bloques con t0 ≤ t ≤ t1)
  recortan el rango.
- El bloque que el motor escribe al final de una corrida cortada por `--tf` (estado avanzado
  hasta t = tf, que no es un evento) se descarta si aparece.

Con `--snapshot t` se guarda un PNG del primer bloque con t_b ≥ t (se informa el t_b y el número
de evento que se usaron); con `--snapshot-block b`, del bloque b (negativo cuenta desde el final).

Colores: fresca azul, usada roja; obstáculos gris; arcos en verde sobre las paredes cortas.

Uso:  python3 animate.py <run_dir> [--fps 30] [--speed 1.0 | --stride k] [--t0 0] [--t1 tf]
                         [--first b] [--last b] [--out anim.mp4]
      python3 animate.py <run_dir> --snapshot t | --snapshot-block b [--out snapshot.png]
"""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

import numpy as np
from matplotlib.animation import FFMpegWriter
from matplotlib.collections import EllipseCollection

from common import TP_ROOT, use_style

import matplotlib.pyplot as plt  # noqa: E402  (common configura el backend)

FRESH, USED, OBSTACLE, GOAL = "tab:blue", "tab:red", "0.35", "tab:green"
# dynamic.txt escribe los tiempos con 6 decimales (RunWriter.num).
T_PRINT_TOL = 5e-7


def ensure_ffmpeg() -> None:
    """matplotlib escribe el mp4 con el binario de ffmpeg: si no está en el PATH, usa el que trae
    `imageio-ffmpeg` (ver requirements.txt)."""
    if shutil.which("ffmpeg"):
        return
    try:
        import imageio_ffmpeg
    except ImportError:
        raise SystemExit("Falta ffmpeg: 'pip install -r analysis/requirements.txt' "
                         "(trae imageio-ffmpeg) o instalarlo en el sistema.")
    plt.rcParams["animation.ffmpeg_path"] = imageio_ffmpeg.get_ffmpeg_exe()


def load_static(run_dir: Path):
    with open(run_dir / "static.txt") as fh:
        n = int(fh.readline())
        L, W, d = map(float, fh.readline().split())
        radii = np.array([float(fh.readline().split()[0]) for _ in range(n)])
        k = int(fh.readline())
        obstacles = np.array([list(map(float, fh.readline().split())) for _ in range(k)])
    return n, L, W, d, radii, obstacles.reshape(k, 3)


def load_dynamic(run_dir: Path, n: int):
    """→ times (B,), state (B, N, 5) con columnas x y vx vy usada, un bloque por fila."""
    raw = np.fromstring((run_dir / "dynamic.txt").read_text(), sep=" ")
    block = 1 + 5 * n
    blocks = raw.size // block
    raw = raw[: blocks * block].reshape(blocks, block)
    return raw[:, 0], raw[:, 1:].reshape(blocks, n, 5)


def event_numbers(run_dir: Path, times: np.ndarray):
    """→ (número de evento de cada bloque, cantidad de bloques que son eventos, every).

    El motor escribe el bloque 0 en t = 0 (condición inicial) y el bloque b después de b·every
    eventos; si la corrida no terminó en un múltiplo de every, agrega un último bloque: en el
    último evento (corte por t_90) o en t = tf (corte por tf, estado avanzado en MRU hasta un
    instante que NO es un evento). Este último caso se excluye devolviendo `valid` < B."""
    meta_path = run_dir / "run.json"
    if not meta_path.exists():
        return np.arange(times.size), times.size, 1
    meta = json.loads(meta_path.read_text())
    every = max(1, int(meta.get("every") or 1))
    total = int(meta["events"]["total"])
    valid = times.size
    if (times.size > 1 and abs(times[-1] - meta["tf"]) < T_PRINT_TOL
            and (times.size - 1) * every != total):
        valid -= 1
        print(f"  se descarta el último bloque (t = tf = {times[-1]:.6f} s: no es un evento)")
    return np.minimum(np.arange(times.size) * every, total), valid, every


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("run_dir", type=Path)
    ap.add_argument("--fps", type=int, default=30, help="cuadros por segundo del video")
    ap.add_argument("--speed", type=float, default=1.0,
                    help="segundos simulados por segundo de video, EN PROMEDIO (fija el stride)")
    ap.add_argument("--stride", type=int, default=None,
                    help="usar uno de cada k bloques de dynamic.txt (ignora --speed)")
    ap.add_argument("--t0", type=float, default=None, help="usar solo bloques con t >= t0 (s)")
    ap.add_argument("--t1", type=float, default=None, help="usar solo bloques con t <= t1 (s)")
    ap.add_argument("--first", type=int, default=None, help="primer bloque (índice)")
    ap.add_argument("--last", type=int, default=None, help="último bloque (índice, inclusive)")
    ap.add_argument("--out", type=Path, default=None)
    ap.add_argument("--snapshot", type=float, default=None,
                    help="en vez de un video, PNG del primer bloque con t >= este valor (s)")
    ap.add_argument("--snapshot-block", type=int, default=None,
                    help="en vez de un video, PNG de este bloque (índice; negativo desde el final)")
    args = ap.parse_args()

    n, L, W, d, radii, obstacles = load_static(args.run_dir)
    times, state = load_dynamic(args.run_dir, n)
    events, valid, every = event_numbers(args.run_dir, times)

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
    balls = EllipseCollection(2 * radii, 2 * radii, 0, units="xy", offsets=state[0, :, :2],
                              offset_transform=ax.transData, edgecolors="none", zorder=2)
    ax.add_collection(balls)
    label = ax.text(0.01, 1.02, "", transform=ax.transAxes, ha="left", va="bottom")

    def render(b: int) -> None:
        """Dibuja el bloque b tal cual está en dynamic.txt (instante del evento events[b])."""
        s = state[b]
        used = s[:, 4] > 0.5
        balls.set_offsets(s[:, :2])
        balls.set_facecolors(np.where(used, USED, FRESH))
        label.set_text(f"t = {times[b]:.4f} s    evento {events[b]}    "
                       f"goles = {int(used.sum())}/{n}")

    if args.snapshot is not None or args.snapshot_block is not None:
        if args.snapshot_block is not None:
            b = range(valid)[args.snapshot_block]
        else:
            later = np.flatnonzero(times[:valid] >= args.snapshot)
            b = int(later[0]) if later.size else valid - 1
            if not later.size:
                print(f"  ningún evento con t >= {args.snapshot} s: se usa el último bloque")
        out = args.out or args.run_dir / f"snapshot_{times[b]:.3f}s.png"
        render(b)
        fig.savefig(out, dpi=120)
        plt.close(fig)
        print(f"  bloque {b}, evento {events[b]}, t = {times[b]:.6f} s → {out}")
        return

    # Rango de bloques (solo selección entre instantes de eventos).
    first = 0 if args.first is None else range(valid)[args.first]
    last = valid - 1 if args.last is None else range(valid)[args.last]
    idx = np.arange(first, last + 1)
    if args.t0 is not None:
        idx = idx[times[idx] >= args.t0]
    if args.t1 is not None:
        idx = idx[times[idx] <= args.t1]
    if idx.size == 0:
        raise SystemExit("No hay bloques en el rango pedido")
    if args.stride is not None:
        stride = max(1, args.stride)
    else:
        # Duración media buscada del video: (t_último − t_primero)/speed; ambos son eventos.
        video_s = (times[idx[-1]] - times[idx[0]]) / args.speed
        stride = max(1, round(idx.size / (args.fps * video_s))) if video_s > 0 else 1
    frames = idx[::stride]
    out = args.out or args.run_dir / "anim.mp4"

    ensure_ffmpeg()
    writer = FFMpegWriter(fps=args.fps, bitrate=2500)
    with writer.saving(fig, out, dpi=120):
        for b in frames:
            render(b)
            writer.grab_frame()
    plt.close(fig)
    dt = np.diff(times[frames])
    print(f"  {out.relative_to(TP_ROOT) if out.is_relative_to(TP_ROOT) else out}  "
          f"({frames.size} cuadros = {frames.size / args.fps:.1f} s de video; "
          f"t = {times[frames[0]]:.4f} → {times[frames[-1]]:.4f} s simulados; "
          f"{stride} bloques = {stride * every} eventos por cuadro"
          + (f"; tiempo simulado entre cuadros {dt.min():.4f}–{dt.max():.4f} s)" if dt.size
             else ")"))


if __name__ == "__main__":
    main()
