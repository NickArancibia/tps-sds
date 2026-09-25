"""Fracción de goles F_g(t) = N_g(t)/N de una o varias realizaciones (una curva por corrida), con
t_90 marcado: recta horizontal en 0.9 y, por curva, recta punteada desde (t_90, 0.9) hasta el eje
horizontal, con t_90 como tick en el color de su curva.

Lee `goals.csv` y `run.json` de corridas sin `--stop-at-t90` (por ejemplo las de `output/anim/`,
t_f = 30 s), así la curva sigue después de t_90. El motor es determinista por seed:
`output/anim/{empty,disco_R033}` (seed 1) reproducen la seed 1 de los barridos `empty` y
`single_R/R0.330`.

Color de cada curva: el de su familia (`plot_t90.FAMILY_COLORS`, mismo que el resto de las
figuras). Salida: `analysis/figures/<out>`; t_90 de cada corrida por stdout.

Uso:  python3 plot_goals.py ../output/anim/empty ../output/anim/disco_R033 \
          --labels "mesa vacía" "disco central" --out fg_empty_disco.png
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np

from common import LABEL_TIME, load_goals, load_run_meta, mark_on_axis, save_figure, use_style
from plot_t90 import DATA_COLOR, FAMILY_COLORS

import matplotlib.pyplot as plt  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("run_dirs", type=Path, nargs="+")
    ap.add_argument("--labels", nargs="+", default=None,
                    help="nombre de cada curva para la leyenda (uno por run_dir)")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    labels = args.labels or [None] * len(args.run_dirs)
    if len(labels) != len(args.run_dirs):
        ap.error("--labels necesita un nombre por run_dir")

    use_style()
    fig, ax = plt.subplots()
    t_max, marks = 0.0, []
    for run_dir, label in zip(args.run_dirs, labels):
        meta = load_run_meta(run_dir)
        goals = load_goals(run_dir)
        n = meta["N"]
        color = FAMILY_COLORS.get(label, DATA_COLOR)
        t = np.concatenate(([0.0], goals["time"], [meta["finalTime"]]))
        fg = np.concatenate(([0.0], np.arange(1, len(goals) + 1) / n, [len(goals) / n]))
        ax.step(t, fg, where="post", color=color, label=label)
        t_max = max(t_max, meta["finalTime"])
        t90 = meta["t90"]
        if t90 is not None:
            ax.plot([t90, t90], [0, 0.9], color=color, linestyle=":", linewidth=1.2)
            marks.append((t90, rf"$t_{{90}}$ = {t90:.1f}", color))
        t90_txt = f"{t90:.1f} s" if t90 is not None else "no alcanzado"
        print(f"  {run_dir.name} (seed {meta['seed']}): t_90 = {t90_txt}, "
              f"{meta['goals']} goles en {meta['finalTime']:.0f} s")

    ax.set_xlabel(LABEL_TIME)
    ax.set_ylabel("Fracción de goles")
    ax.set_xlim(0, t_max)
    ax.set_ylim(0, 1)
    if marks:
        ax.plot([0, max(v for v, _, _ in marks)], [0.9, 0.9], color="0.4", linestyle="--",
                linewidth=0.8)
        mark_on_axis(ax, "x", marks, min_gap=0.12)
        mark_on_axis(ax, "y", [(0.9, "0.9", "black")], min_gap=0.05)
    if any(labels):
        # Abajo a la derecha (pedido del grupo). No entra entera a la derecha de t_90 = 22.9 s:
        # fondo opaco para que tape limpio el tramo inferior de esa recta.
        ax.legend(loc="lower right", handlelength=1.2, handletextpad=0.5, borderaxespad=0.3,
                  framealpha=1)
    save_figure(fig, args.out)


if __name__ == "__main__":
    main()
