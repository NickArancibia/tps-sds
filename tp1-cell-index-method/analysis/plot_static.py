#!/usr/bin/env python3
"""Figura del punto 1: todas las partículas, con una elegida y sus vecinas en otro color.

A diferencia de `demo_interactiva.py`, este script no es interactivo: recibe el id de la partícula
como input y guarda un PNG, que es lo que pide el enunciado.

Uso:
    python plot_static.py <directorio_de_corrida> --id 42 [--out figura.png] [--grid]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))

from common.parsers import load_run  # noqa: E402
from common.render import SystemView, add_legend, run_title  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("run_dir")
    parser.add_argument("--id", type=int, required=True,
                        help="id 1-based de la partícula a destacar")
    parser.add_argument("--out", default=None, help="archivo PNG de salida")
    parser.add_argument("--grid", action="store_true", help="dibuja la grilla de celdas del CIM")
    parser.add_argument("--no-links", action="store_true")
    args = parser.parse_args()

    run = load_run(args.run_dir)
    if not 1 <= args.id <= run.n:
        raise SystemExit(f"--id debe estar entre 1 y {run.n}, se recibió {args.id}")

    fig, ax = plt.subplots(figsize=(10.5, 8.5))
    view = SystemView(ax, run, show_grid=args.grid, show_links=not args.no_links)
    view.select(args.id - 1)

    count = len(run.neighbors[args.id - 1])
    ax.set_title(f"{run_title(run)}\npartícula {args.id}: {count} vecinas", fontsize=11)
    add_legend(ax)

    out = Path(args.out) if args.out else run.path / f"vecinos_id{args.id}.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(out, dpi=150)
    print(f"Figura guardada en {out}")


if __name__ == "__main__":
    main()
