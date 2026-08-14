#!/usr/bin/env python3
"""Punto 4: tiempo de cómputo del CIM en función de N, con densidad libre y densidad fija.

Superpone las dos curvas que pide el enunciado:

* **densidad libre** (4.1): L fijo, así que ρ = N/L² crece con N.
* **densidad fija** (4.2): L = sqrt(N/ρ) crece junto con N para mantener ρ constante.

Ambas usan el M óptimo hallado en el punto 3. Cada punto es el promedio de todas las repeticiones
cronometradas y la barra de error es el desvío estándar.

El eje N es **categórico**: los N medidos están log-espaciados, así que en un eje lineal se
amontonarían a la izquierda; acá cada uno ocupa una posición equiespaciada y lleva su etiqueta. El
eje de tiempos es lineal con ticks uniformes. Con `--log` se vuelve a la vista log-log, que es la
que comprime los órdenes de magnitud.

Uso:
    python plot_n.py output/bench/bench_N_libre.csv output/bench/bench_N_densidad_fija.csv \
        [--out figura.png]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))

from common.axes import (categorical_positions, label_log_ticks, uniform_ticks,  # noqa: E402
                         use_categorical_axis, use_data_ticks)
from common.bench import EXPERIMENT_LABELS, curves, describe, read_all  # noqa: E402

STYLES = {
    "N_free": {"color": "#1f77b4", "marker": "o", "ls": "-"},
    "N_fixed_density": {"color": "#d62728", "marker": "s", "ls": "--"},
}

#: Orden en que se dibujan las series: primero el punto 4.1, después el 4.2.
ORDER = ["N_free", "N_fixed_density"]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("csv", nargs="+", help="CSV(s) de los barridos de N")
    parser.add_argument("--out", default=None, help="archivo PNG de salida")
    parser.add_argument("--log", action="store_true",
                        help="usa escala log-log en vez del eje N categórico con tiempos lineales")
    parser.add_argument("--no-fit", action="store_true",
                        help="no ajusta ni muestra la pendiente de cada curva")
    parser.add_argument("--fit-from", type=int, default=100, metavar="N",
                        help="primer N incluido en el ajuste de la pendiente (default 100): con N "
                             "chico domina el costo fijo de recorrer las M^2 celdas y la pendiente "
                             "no refleja el escalamiento del método")
    parser.add_argument("--ticks-at-decades", action="store_true",
                        help="con --log, etiqueta el eje N en las potencias de 10 en vez de en "
                             "cada N medido")
    args = parser.parse_args()

    rows = [row for row in read_all(args.csv) if row["experiment"] != "M"]
    if not rows:
        raise SystemExit("Los CSV no contienen barridos de N (experimentos 'N_free' o "
                         "'N_fixed_density').")

    series = curves(rows, x_field="N", group_by=("experiment",))

    ordered = sorted(series.items(),
                     key=lambda item: (ORDER.index(item[0][0]) if item[0][0] in ORDER else len(ORDER),
                                       item[0][0]))

    # En modo categórico las curvas se dibujan contra la posición del N, no contra el N.
    positions = categorical_positions(x for curve in series.values() for x in curve.x)

    fig, ax = plt.subplots(figsize=(8.5, 5.5))
    for (experiment,), curve in ordered:
        style = STYLES.get(experiment, {"color": "#2ca02c", "marker": "^", "ls": ":"})
        label = EXPERIMENT_LABELS.get(experiment, experiment)
        slope = None if args.no_fit else _log_slope(curve.x, curve.mean_ms, args.fit_from)
        if slope is not None:
            print(f"\najuste log-log de «{label}» para N ≥ {args.fit_from}: t ~ N^{slope:.2f}")
            # La pendiente sólo se lee como pendiente si el gráfico es log-log; en el modo
            # categórico queda en la consola para no sugerir una lectura visual que no aplica.
            if args.log:
                label = f"{label}  (t ~ N^{slope:.2f} para N ≥ {args.fit_from})"

        x = curve.x if args.log else [positions[value] for value in curve.x]
        ax.errorbar(x, curve.mean_ms, yerr=curve.std_ms, capsize=3, lw=1.4, ms=5,
                    label=label, **style)
        print(f"\n=== {EXPERIMENT_LABELS.get(experiment, experiment)} ===")
        print(describe(curve, "N"))

    ax.set_xlabel("N (cantidad de partículas)")
    ax.set_ylabel("tiempo de búsqueda de vecinos [ms]")
    if args.log:
        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.autoscale_view()
        # Con sólo las décadas etiquetadas no se puede leer a qué (N, tiempo) corresponde cada
        # punto: en x se etiqueta cada N medido y en y también los ticks menores.
        if args.ticks_at_decades:
            label_log_ticks(ax.xaxis)
        else:
            use_data_ticks(ax.xaxis, [x for curve in series.values() for x in curve.x])
        label_log_ticks(ax.yaxis)
    else:
        use_categorical_axis(ax.xaxis, positions)
        ax.set_xlim(-0.5, len(positions) - 0.5)
        uniform_ticks(ax.yaxis)
        ax.set_ylim(bottom=0)

    ax.set_title(f"Tiempo de cómputo del CIM en función de N\n{_subtitle(rows)}", fontsize=11)
    ax.grid(True, which="both", ls=":", lw=0.5, alpha=0.6)
    ax.legend(frameon=False)

    out = Path(args.out) if args.out else Path(args.csv[0]).with_name("tiempo_vs_N.png")
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(out, dpi=150)
    print(f"\nFigura guardada en {out}")


def _log_slope(x: np.ndarray, y: np.ndarray, fit_from: int) -> float | None:
    """Pendiente del ajuste lineal en log-log: el exponente α de t ~ N^α."""
    mask = (x >= fit_from) & (x > 0) & (y > 0)
    if mask.sum() < 2:
        return None
    return float(np.polyfit(np.log(x[mask]), np.log(y[mask]), 1)[0])


def _subtitle(rows: list[dict]) -> str:
    free = [r for r in rows if r["experiment"] == "N_free"]
    fixed = [r for r in rows if r["experiment"] == "N_fixed_density"]
    parts = []
    if free:
        parts.append(f"densidad libre: L = {free[0]['L']:g}, M = {free[0]['M']}")
    if fixed:
        density = fixed[0]["N"] / fixed[0]["L"] ** 2
        parts.append(f"densidad fija: ρ = {density:.2f}, L = √(N/ρ)")
    parts.append(f"rc = {rows[0]['rc']:g}")
    parts.append("con contorno periódico" if rows[0]["pbc"] else "sin contorno periódico")
    return ",  ".join(parts)


if __name__ == "__main__":
    main()
