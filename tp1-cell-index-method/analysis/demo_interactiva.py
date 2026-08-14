#!/usr/bin/env python3
"""Demo interactiva del punto 2: clic sobre una partícula y se colorean sus vecinas.

Los vecinos salen del archivo `neighbors.txt` que generó el CIM en Java: este script no calcula
vecindades, sólo las pinta. Es la demostración visual de que el CIM está funcionando.

Uso:
    python demo_interactiva.py <directorio_de_corrida> [--grid] [--no-links]

Controles:
    clic izquierdo   elegir partícula (clic en el vacío = deseleccionar)
    n / N            elegir una partícula al azar
    g                mostrar u ocultar la grilla de celdas
    q                salir
"""

from __future__ import annotations

import argparse
import random
import sys
from pathlib import Path

import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parent))

from common.parsers import load_run
from common.render import SystemView, add_legend, run_title


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("run_dir", help="directorio de salida de una corrida (contiene static.txt, "
                                        "dynamic.txt, neighbors.txt, run.json)")
    parser.add_argument("--grid", action="store_true", help="dibuja la grilla de celdas del CIM")
    parser.add_argument("--no-links", action="store_true",
                        help="no dibuja los segmentos hacia las vecinas")
    parser.add_argument("--id", type=int, default=None,
                        help="parte con esta partícula ya seleccionada (id 1-based)")
    args = parser.parse_args()

    run = load_run(args.run_dir)

    fig, ax = plt.subplots(figsize=(10.5, 8.5))
    fig.canvas.manager.set_window_title(f"SdS TP1 - CIM - {run.path.name}")
    view = SystemView(ax, run, show_grid=args.grid, show_links=not args.no_links)

    ax.set_title(run_title(run), fontsize=11)
    add_legend(ax)

    status = fig.text(0.5, 0.015, "", ha="center", fontsize=10, family="monospace")

    def describe(index: int | None) -> str:
        if index is None:
            return "Clic sobre una partícula para ver sus vecinas  |  n: al azar   g: grilla   q: salir"
        neighbors = run.neighbors[index]
        ids = sorted(int(j) + 1 for j in neighbors)
        shown = ", ".join(str(i) for i in ids[:14])
        if len(ids) > 14:
            shown += f", ... (+{len(ids) - 14})"
        return f"partícula {index + 1}  |  {len(ids)} vecinas  |  ids: [{shown}]"

    def refresh(index: int | None) -> None:
        view.select(index)
        status.set_text(describe(index))
        fig.canvas.draw_idle()

    def on_click(event) -> None:
        if event.inaxes is not ax or event.button != 1:
            return
        refresh(view.particle_at(event.xdata, event.ydata))

    def on_key(event) -> None:
        if event.key in ("n", "N"):
            refresh(random.randrange(run.n))
        elif event.key == "g":
            view.toggle_grid()
            fig.canvas.draw_idle()

    fig.canvas.mpl_connect("button_press_event", on_click)
    fig.canvas.mpl_connect("key_press_event", on_key)

    refresh(args.id - 1 if args.id else None)
    plt.tight_layout(rect=(0, 0.03, 1, 1))
    plt.show()


if __name__ == "__main__":
    main()
