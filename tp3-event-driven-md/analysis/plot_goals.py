"""Fracción de goles F_g(t) = N_g(t)/N de una o varias realizaciones (una curva por corrida), con
t_90 marcado: recta horizontal en 0.9 y, por curva, recta punteada desde (t_90, 0.9) hasta el eje
horizontal, con t_90 como tick en el color de su curva.

Sirve para corridas completas (por ejemplo las de `output/anim/`, t_f = 30 s: la curva sigue
después de t_90) y para las de los barridos (`--stop-at-t90`: la curva termina en (t_90, 0.9); el
eje horizontal se estira un 5 % para que el último t_90 no quede sobre el borde). El motor es
determinista por seed en una misma máquina: `output/anim/{empty,disco_R033}` (seed 1) reproducen
la seed 1 de los barridos `empty` y `single_R/R0.330`.

Color de cada curva: `--colors` (uno por corrida) o, si no se da, el de su familia según el label
(`plot_t90.FAMILY_COLORS`, mismo que el resto de las figuras). `--legend-title`: símbolo común a
todas las entradas (ej. `n`), así las entradas llevan solo el valor (../../AGENTS.md §3).
Salida: `analysis/figures/<out>`; t_90 de cada corrida por stdout.

Uso:  python3 plot_goals.py ../output/anim/empty ../output/anim/disco_R033 \
          --labels "mesa vacía" "disco central" --out fg_empty_disco.png
      python3 plot_goals.py ../output/sweeps/multi_barrier/k17/s1 \
          ../output/sweeps/multi_barrier_rows_k/k17_n01/s1 ../output/sweeps/multi_barrier_rows_k/k17_n03/s1 \
          --labels 0 1 3 --legend-title n --colors tab:green tab:orange black --out fg_rows.png
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np

from common import LABEL_TIME, load_goals, load_run_meta, mark_on_axis, save_figure, use_style
from plot_t90 import DATA_COLOR, FAMILY_COLORS

import matplotlib.pyplot as plt  # noqa: E402


def stagger_x_marks(ax, values: list[float], min_sep: float = 0.14) -> None:
    """Baja un renglón el rótulo de cada t_90 que quede a menos de `min_sep` (fracción del rango
    visible) del anterior en su mismo renglón, para que "t_90 = …" no se pisen."""
    lo, hi = ax.get_xlim()
    locs = list(ax.get_xticks())
    ticks = ax.xaxis.get_major_ticks(len(locs))
    last_by_level: list[float] = []
    for v in sorted(values):
        level = next((i for i, last in enumerate(last_by_level)
                      if v - last > min_sep * (hi - lo)), len(last_by_level))
        if level == len(last_by_level):
            last_by_level.append(v)
        last_by_level[level] = v
        tick = ticks[locs.index(v)]
        tick.set_pad(tick.get_pad() + level * 1.3 * tick.label1.get_fontsize())


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("run_dirs", type=Path, nargs="+")
    ap.add_argument("--labels", nargs="+", default=None,
                    help="nombre de cada curva para la leyenda (uno por run_dir)")
    ap.add_argument("--colors", nargs="+", default=None,
                    help="color de cada curva (uno por run_dir); default: el de su familia")
    ap.add_argument("--legend-title", default=None,
                    help="símbolo común a todas las entradas de la leyenda (ej. n)")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    labels = args.labels or [None] * len(args.run_dirs)
    if len(labels) != len(args.run_dirs):
        ap.error("--labels necesita un nombre por run_dir")
    colors = args.colors or [FAMILY_COLORS.get(label, DATA_COLOR) for label in labels]
    if len(colors) != len(args.run_dirs):
        ap.error("--colors necesita un color por run_dir")

    use_style()
    fig, ax = plt.subplots()
    t_max, truncated, marks = 0.0, False, []
    for run_dir, label, color in zip(args.run_dirs, labels, colors):
        meta = load_run_meta(run_dir)
        goals = load_goals(run_dir)
        n = meta["N"]
        t = np.concatenate(([0.0], goals["time"], [meta["finalTime"]]))
        fg = np.concatenate(([0.0], np.arange(1, len(goals) + 1) / n, [len(goals) / n]))
        ax.step(t, fg, where="post", color=color, label=label)
        t_max = max(t_max, meta["finalTime"])
        truncated |= bool(meta.get("stopAtT90"))
        t90 = meta["t90"]
        if t90 is not None:
            ax.plot([t90, t90], [0, 0.9], color=color, linestyle=":", linewidth=1.2)
            marks.append((t90, rf"$t_{{90}}$ = {t90:.1f}", color))
        t90_txt = f"{t90:.1f} s" if t90 is not None else "no alcanzado"
        print(f"  {run_dir.name} (seed {meta['seed']}): t_90 = {t90_txt}, "
              f"{meta['goals']} goles en {meta['finalTime']:.0f} s")

    ax.set_xlabel(LABEL_TIME)
    ax.set_ylabel("Fracción de goles")
    ax.set_xlim(0, 1.05 * t_max if truncated else t_max)
    ax.set_ylim(0, 1)
    if marks:
        ax.plot([0, max(v for v, _, _ in marks)], [0.9, 0.9], color="0.4", linestyle="--",
                linewidth=0.8)
        mark_on_axis(ax, "x", marks, min_gap=0.12)
        stagger_x_marks(ax, [v for v, _, _ in marks])
        mark_on_axis(ax, "y", [(0.9, "0.9", "black")], min_gap=0.05)
    if any(labels):
        # Corridas completas: abajo a la derecha (pedido del grupo); no entra entera a la derecha
        # de t_90 = 22.9 s, fondo opaco para que tape limpio el tramo inferior de esa recta.
        # Cortadas en t_90 (barridos): el último t_90 queda sobre el borde derecho y las rectas
        # de t_90 caen en cualquier lado, así que "best" (evita curvas y rectas dibujadas).
        ax.legend(loc="best" if truncated else "lower right", title=args.legend_title,
                  handlelength=1.2, handletextpad=0.5, borderaxespad=0.3, framealpha=1)
    save_figure(fig, args.out)


if __name__ == "__main__":
    main()
