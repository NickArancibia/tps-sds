"""Punto 1.2: <t_90> ± desvío en función de la variable de cada barrido, comparado con la mesa
vacía. Lee `output/sweeps/index.json` (analysis/gen_configs.py) y los `run.json` de cada
realización (scripts/run_sweeps.sh).

Observable: t_90 = primer instante en que N_g(t)/N ≥ 0.9. Se promedia entre realizaciones
(seeds distintas); la barra de error es el desvío estándar muestral. Si en alguna realización no
se alcanza 0.9 antes de t_f, `t90` es null en run.json: esa realización se cuenta aparte
(columna `no_alcanzado`) y NO entra en el promedio.

Salidas:
- `analysis/out/t90_<barrido>.csv`: variable, realizaciones, <t_90>, desvío, no alcanzados.
- `analysis/figures/t90_<barrido>.png`: <t_90> vs variable; mesa vacía como recta horizontal
  (su <t_90> ± desvío va en la leyenda).

Uso:  python3 plot_t90.py
"""

from __future__ import annotations

import csv
import json

import numpy as np

from common import (LABEL_TIME, OUT_DIR, OUTPUT, load_goals, load_run_meta, mean_std,
                    save_figure, use_style)

import matplotlib.pyplot as plt  # noqa: E402

SWEEPS = OUTPUT / "sweeps"
EMPTY_COLOR, DATA_COLOR = "tab:red", "tab:blue"


def t90_stats(run_dir):
    """(<t_90>, desvío, alcanzados, no alcanzados) sobre los s*/run.json de run_dir."""
    values, missing = [], 0
    for run_json in sorted(run_dir.glob("s*/run.json")):
        t90 = load_run_meta(run_json.parent)["t90"]
        if t90 is None:
            missing += 1
        else:
            values.append(t90)
    mean, std = mean_std(values) if values else (float("nan"), float("nan"))
    return mean, std, len(values), missing


def write_csv(name: str, rows: list[dict]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUT_DIR / f"t90_{name}.csv"
    with open(path, "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def plot_fg(run_dirs: list[tuple[str, object]]) -> None:
    fig, ax = plt.subplots()
    for (label, run_dir), color in zip(run_dirs, (EMPTY_COLOR, DATA_COLOR)):
        meta = load_run_meta(run_dir)
        goals = load_goals(run_dir)
        n = meta["N"]
        t = np.concatenate(([0.0], goals["time"], [meta["finalTime"]]))
        fg = np.concatenate(([0.0], np.arange(1, len(goals) + 1) / n, [len(goals) / n]))
        ax.step(t, fg, where="post", color=color, label=label)
        if meta["t90"] is not None:
            ax.axvline(meta["t90"], color=color, linestyle=":", linewidth=1)
    ax.axhline(0.9, color="0.4", linestyle="--", linewidth=0.8)
    ax.set_xlabel(LABEL_TIME)
    ax.set_ylabel("Fracción de partículas usadas")
    ax.set_ylim(0, 1)
    ax.legend(loc="lower right")
    save_figure(fig, "fg_vs_t.png")


def main() -> None:
    with open(SWEEPS / "index.json") as fh:
        index = json.load(fh)
    use_style()

    empty_mean, empty_std, empty_n, empty_missing = t90_stats(SWEEPS / "empty")
    print(f"  mesa vacía: <t_90> = {empty_mean:.2f} ± {empty_std:.2f} s "
          f"({empty_n} realizaciones, {empty_missing} no alcanzaron 0.9)")

    best = (empty_mean, "mesa vacía", SWEEPS / "empty")
    for name, points in index.items():
        rows = []
        for p in points:
            run_dir = SWEEPS / name / p["label"]
            mean, std, n, missing = t90_stats(run_dir)
            rows.append({"value": p["value"], "K": p["K"], "runs": n, "t90_mean_s": mean,
                         "t90_std_s": std, "no_alcanzado": missing})
            print(f"  {name}/{p['label']:8s} <t_90> = {mean:6.2f} ± {std:5.2f} s"
                  f"  ({n} ok, {missing} no)")
            if n and mean < best[0]:
                best = (mean, f"{name}/{p['label']}", run_dir)
        write_csv(name, rows)

        fig, ax = plt.subplots()
        xs = [r["value"] for r in rows]
        ax.axhline(empty_mean, color=EMPTY_COLOR, linestyle="--", linewidth=1,
                   label=f"mesa vacía ({empty_mean:.1f} ± {empty_std:.1f} s)")
        ax.errorbar(xs, [r["t90_mean_s"] for r in rows], yerr=[r["t90_std_s"] for r in rows],
                    color=DATA_COLOR, marker="o", linestyle="--", linewidth=1.0,
                    label="con obstáculos")
        ax.set_xlabel(points[0]["variable"])
        ax.set_ylabel("Tiempo al 90 % de goles (s)")
        ax.legend(loc="best")
        save_figure(fig, f"t90_{name}.png")

    print(f"  mejor: {best[1]} con <t_90> = {best[0]:.2f} s")
    plot_fg([("mesa vacía", SWEEPS / "empty" / "s1"), (best[1], best[2] / "s1")])


if __name__ == "__main__":
    main()
