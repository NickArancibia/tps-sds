"""Goles acumulados N_g(t) de una realización, con t_90 marcado.

Lee `goals.csv` y `run.json` de una corrida sin `--stop-at-t90` (por ejemplo las de
`output/anim/`, t_f = 30 s), así la curva sigue después de t_90. El motor es determinista por
seed: `output/anim/disco_R033` (seed 1) reproduce la seed 1 del barrido `single_R/R0.330`.

Salida: `analysis/figures/<out>`; t_90 se imprime por stdout (va al costado de la figura).

Uso:  python3 plot_goals.py <run_dir> --out goals_disco.png
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np

from common import LABEL_TIME, load_goals, load_run_meta, save_figure, use_style

import matplotlib.pyplot as plt  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("run_dir", type=Path)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    use_style()
    meta = load_run_meta(args.run_dir)
    goals = load_goals(args.run_dir)
    n = meta["N"]
    t = np.concatenate(([0.0], goals["time"], [meta["finalTime"]]))
    ng = np.concatenate(([0], np.arange(1, len(goals) + 1), [len(goals)]))

    fig, ax = plt.subplots()
    ax.step(t, ng, where="post", color="tab:blue")
    if meta["t90"] is not None:
        ax.axvline(meta["t90"], color="tab:red", linestyle=":", linewidth=1.2)
    ax.set_xlabel(LABEL_TIME)
    ax.set_ylabel("Cantidad de goles")
    ax.set_xlim(0, meta["finalTime"])
    ax.set_ylim(0, n)
    save_figure(fig, args.out)
    print(f"  seed {meta['seed']}: t_90 = {meta['t90']:.1f} s, {meta['goals']} goles en "
          f"{meta['finalTime']:.0f} s")


if __name__ == "__main__":
    main()
