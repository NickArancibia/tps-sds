"""`python -m anims <run_dir>`: convierte una corrida ya simulada en un MP4.

No re-simula ni recalcula nada: solo lee los outputs que dejó el motor.
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

from anims.run import load_run
from anims.scenes import SCENES, get_scene


def parse_size(text: str) -> tuple[int, int]:
    try:
        w, h = text.lower().split("x")
        return int(w), int(h)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"tamaño inválido: {text!r} (esperado WxH)") from exc


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m anims", description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("run_dir", type=Path, help="directorio de la corrida")
    parser.add_argument("--out", type=Path, default=None,
                        help="archivo de salida (default: <run_dir>/anim.mp4)")
    parser.add_argument("--fps", type=int, default=30, help="cuadros por segundo (default 30)")
    parser.add_argument("--every", type=int, default=1,
                        help="usar 1 de cada N frames guardados (default 1)")
    parser.add_argument("--size", type=parse_size, default=(1280, 720),
                        help="resolución WxH (default 1280x720)")
    parser.add_argument("--scene", default="flock",
                        help=f"escena a usar (default flock; disponibles: {', '.join(SCENES)})")
    parser.add_argument("--no-hud", action="store_true", help="video limpio, sin overlay")
    parser.add_argument("--no-cache", action="store_true",
                        help="ignora y no escribe el caché state.npz")
    parser.add_argument("--preview", action="store_true",
                        help="abre una ventana interactiva en vez de renderizar")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.every < 1:
        print("--every debe ser >= 1", file=sys.stderr)
        return 2

    run = load_run(args.run_dir, use_cache=not args.no_cache)
    frames = range(0, run.frames, args.every)
    print(f"{run.frames} frames guardados, N={run.n}, L={run.l:g} -> {len(frames)} a renderizar")

    from anims.canvas import AnimCanvas  # import perezoso: sin GPU no hace falta

    canvas = AnimCanvas(run.l, size=args.size, show=args.preview, hud=not args.no_hud,
                        title=f"anims — {args.run_dir.name}")
    scene = get_scene(args.scene)()
    scene.build(canvas.view, run)

    if args.preview:
        return _preview(canvas, scene, frames, args.fps)
    return _render(canvas, scene, frames, args)


def _render(canvas, scene, frames, args) -> int:
    from anims.writer import VideoWriter

    out = args.out or (args.run_dir / "anim.mp4")
    started = time.perf_counter()
    with VideoWriter(out, size=args.size, fps=args.fps) as writer:
        for done, i in enumerate(frames, start=1):
            canvas.set_hud(scene.update(i))
            writer.append(canvas.render())
            if done % 100 == 0 or done == len(frames):
                print(f"\r  {done}/{len(frames)} frames", end="", flush=True)
    canvas.close()
    print(f"\n{out} - {time.perf_counter() - started:.1f} s")
    return 0


def _preview(canvas, scene, frames, fps: int) -> int:
    from vispy import app

    indices = list(frames)
    state = {"k": 0}

    def tick(_event) -> None:
        i = indices[state["k"] % len(indices)]
        canvas.set_hud(scene.update(i))
        canvas.canvas.update()
        state["k"] += 1

    timer = app.Timer(interval=1.0 / max(fps, 1), connect=tick, start=True)
    app.run()
    timer.stop()
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
