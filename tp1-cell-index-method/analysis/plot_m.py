#!/usr/bin/env python3
"""Punto 3: tiempo de cómputo del CIM en función de M, para dos valores de N.

Lee el CSV que produce `BenchmarkRunner --sweep M` (una fila por repetición) y grafica el tiempo
promedio con barras de error igual al desvío estándar. `M = 1` es el caso de fuerza bruta: una
única celda que contiene a todas las partículas.

Uso:
    python plot_m.py output/bench/bench_M.csv [--out figura.png] [--linear-y]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))

from common.axes import label_log_ticks, uniform_ticks  # noqa: E402
from common.bench import curves, describe, read_all  # noqa: E402

MARKERS = ["o", "s", "^", "D", "v", "P"]
COLORS = ["#1f77b4", "#d62728", "#2ca02c", "#9467bd", "#ff7f0e", "#8c564b"]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("csv", nargs="+", help="CSV(s) del barrido de M")
    parser.add_argument("--out", default=None, help="archivo PNG de salida")
    parser.add_argument("--log-y", action="store_true",
                        help="usa escala logarítmica en el eje de tiempos (por defecto: lineal con "
                             "ticks uniformes)")
    parser.add_argument("--log-x", action="store_true",
                        help="usa escala logarítmica en el eje M (por defecto: lineal)")
    args = parser.parse_args()

    rows = [row for row in read_all(args.csv) if row["experiment"] == "M"]
    if not rows:
        raise SystemExit("El CSV no contiene filas del experimento 'M'.")

    series = curves(rows, x_field="M", group_by=("N",))

    fig, ax = plt.subplots(figsize=(8.5, 5.5))
    for index, ((n,), curve) in enumerate(series.items()):
        best = int(curve.x[curve.mean_ms.argmin()])
        ax.errorbar(curve.x, curve.mean_ms, yerr=curve.std_ms,
                    marker=MARKERS[index % len(MARKERS)], color=COLORS[index % len(COLORS)],
                    capsize=3, lw=1.4, ms=5, label=f"N = {n}")
        print(f"\n=== N = {n}  (M óptimo: {best}) ===")
        print(describe(curve, "M"))

    context = next(iter(series.values())).context
    ax.set_xlabel("M (celdas por lado de la grilla)")
    ax.set_ylabel("tiempo de búsqueda de vecinos [ms]")
    if args.log_x:
        ax.set_xscale("log")
    else:
        # M ya es una secuencia de enteros consecutivos: en lineal queda equiespaciado solo.
        ax.set_xticks(sorted({int(x) for curve in series.values() for x in curve.x}))
    if args.log_y:
        ax.set_yscale("log")
    ax.autoscale_view()
    if args.log_y:
        # Etiquetas también en los ticks menores: si no, entre 0.1 y 1 no hay ninguna referencia.
        label_log_ticks(ax.yaxis)
    else:
        uniform_ticks(ax.yaxis)
        ax.set_ylim(bottom=0)
    if args.log_x:
        label_log_ticks(ax.xaxis)

    max_m = max(int(x) for curve in series.values() for x in curve.x)
    subtitle = (f"L = {context.get('L', 20):g},  rc = {context.get('rc', 1):g},  "
                f"{'con' if context.get('pbc') else 'sin'} contorno periódico,  "
                f"M máximo válido = {max_m}")
    ax.set_title(f"Tiempo de cómputo del CIM en función de M\n{subtitle}", fontsize=11)
    ax.grid(True, which="both", ls=":", lw=0.5, alpha=0.6)
    ax.legend(title="cantidad de partículas", frameon=False)

    out = Path(args.out) if args.out else Path(args.csv[0]).with_name("tiempo_vs_M.png")
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(out, dpi=150)
    print(f"\nFigura guardada en {out}")


if __name__ == "__main__":
    main()
