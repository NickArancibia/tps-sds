"""Figuras combinadas del punto 1.2: para cada barrido, un panel por configuración probada
(distribución de obstáculos sobre la mesa, como `plot_configs.py`) arriba de la curva de
resultados `<t_90>` vs. variable (como `plot_t90.py`), para ver de un vistazo qué mesa da cada
punto de la curva.

No pisa nada de lo que ya existe: lee `analysis/out/t90_<barrido>.csv` (ya calculados) y
`output/sweeps/index.json` + los `config.txt` de cada punto (regenerados por `gen_configs.py`,
no requieren volver a simular) y escribe en `analysis/figures/combined/<barrido>.png`.

La línea de mesa vacía usa el <t_90> pasado por `--empty-mean/--empty-std` (por default, el
último valor medido: ver `plot_t90.py` / `AGENTS.md`).

Uso:  python3 plot_combined.py [--empty-mean 22.08] [--empty-std 2.51]
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import re

from common import FIGURES, OUT_DIR, OUTPUT, use_style
from plot_configs import L, draw

import matplotlib.pyplot as plt  # noqa: E402

SWEEPS = OUTPUT / "sweeps"
EMPTY_COLOR, DATA_COLOR = "tab:red", "tab:blue"
MAX_COLS = 5


def load_t90_csv(name: str) -> list[dict]:
    path = OUT_DIR / f"t90_{name}.csv"
    with open(path, newline="") as fh:
        return list(csv.DictReader(fh))


def panel_title(label: str, variable: str, value: float) -> str:
    sym = re.match(r"[A-Za-z]+", label).group()
    if "(m)" in variable:
        return f"{sym} = {value:.3g} m"
    return f"{sym} = {value:.3g}"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--empty-mean", type=float, default=22.08)
    ap.add_argument("--empty-std", type=float, default=2.51)
    args = ap.parse_args()

    with open(SWEEPS / "index.json") as fh:
        index = json.load(fh)
    use_style()

    out_dir = FIGURES / "combined"
    out_dir.mkdir(parents=True, exist_ok=True)

    for name, points in index.items():
        rows = load_t90_csv(name)
        n = len(points)
        cols = min(MAX_COLS, n)
        config_rows = math.ceil(n / cols)

        fig = plt.figure(figsize=(2.6 * cols, 1.55 * config_rows + 3.0),
                         layout=None)
        fig.set_constrained_layout(False)
        gs = fig.add_gridspec(config_rows + 1, cols,
                               height_ratios=[1.0] * config_rows + [2.6],
                               hspace=0.15, wspace=0.1,
                               top=0.97, bottom=0.1, left=0.08, right=0.98)

        for i, p in enumerate(points):
            r, c = divmod(i, cols)
            ax = fig.add_subplot(gs[r, c])
            title = panel_title(p["label"], p["variable"], p["value"])
            draw(ax, SWEEPS / name / p["label"] / "config.txt", title)
        for j in range(n, config_rows * cols):
            r, c = divmod(j, cols)
            fig.add_subplot(gs[r, c]).axis("off")

        ax = fig.add_subplot(gs[config_rows, :])
        xs = [r["value"] for r in rows]
        means = [float(r["t90_mean_s"]) for r in rows]
        stds = [float(r["t90_std_s"]) for r in rows]
        ax.axhline(args.empty_mean, color=EMPTY_COLOR, linestyle="--", linewidth=1,
                   label="mesa vacía")
        ax.errorbar([float(x) for x in xs], means, yerr=stds, color=DATA_COLOR, marker="o",
                    linestyle="--", linewidth=1.0, label="con obstáculos")
        ax.set_xlabel(points[0]["variable"])
        ax.set_ylabel("Tiempo al 90 % de goles (s)")
        ax.legend(loc="best")

        path = out_dir / f"{name}.png"
        fig.savefig(path)
        plt.close(fig)
        print(f"  {path.relative_to(FIGURES.parent.parent)}")


if __name__ == "__main__":
    main()
