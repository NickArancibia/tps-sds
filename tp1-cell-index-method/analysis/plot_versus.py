#!/usr/bin/env python3
"""Comparación de tiempo de cómputo: CIM contra fuerza bruta (CIM con M = 1).

`--verify` ya garantiza que ambos métodos devuelven los mismos vecinos; acá se compara lo único en
lo que difieren: el costo. Las dos curvas salen del mismo barrido de N — densidad libre (L fijo) o
densidad fija (L = sqrt(N/rho)) — una con el M del CIM y la otra con M = 1, que degenera en fuerza
bruta: una sola celda que contiene a todas las partículas, así que se comparan todas contra todas.

Cada CSV aporta una serie, y es la de fuerza bruta si **todo** el barrido usó M = 1. No alcanza con
mirar cada fila: en el barrido de densidad fija el M del CIM crece con L, y en sus primeros N la
geometría sólo admite M = 1, así que la curva del CIM también contiene filas con M = 1.

Cada punto es el promedio de todas las repeticiones cronometradas y la barra de error es el desvío
estándar. Además de las curvas se imprime el speedup (t_bruta / t_CIM) para cada N medido.

Uso:
    python plot_versus.py output/bench/bench_N_libre.csv output/bench/bench_N_bruta.csv \
        [--out figura.png] [--log]
    python plot_versus.py output/bench/bench_N_densidad_fija.csv \
        output/bench/bench_N_densidad_fija_bruta.csv --log
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

from common.axes import (categorical_positions, uniform_ticks,  # noqa: E402
                         use_categorical_axis, use_data_ticks)
from common.bench import Curve, curves, describe, read_csv  # noqa: E402

STYLES = {
    "bruta": {"color": "#d62728", "marker": "s", "ls": "--"},
    "cim": {"color": "#1f77b4", "marker": "o", "ls": "-"},
}

#: Nombre de archivo de salida por defecto según el experimento comparado.
DEFAULT_OUT = {
    "N_free": "tiempo_cim_vs_bruta.png",
    "N_fixed_density": "tiempo_cim_vs_bruta_densidad_fija.png",
}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("csv", nargs="+",
                        help="CSV(s) del barrido de N con el M del CIM y del barrido con M=1")
    parser.add_argument("--out", default=None, help="archivo PNG de salida")
    parser.add_argument("--log", action="store_true",
                        help="usa escala log-log en vez del eje N categórico con tiempos lineales")
    parser.add_argument("--no-fit", action="store_true",
                        help="no ajusta ni muestra la pendiente de cada curva")
    parser.add_argument("--fit-from", type=int, default=100, metavar="N",
                        help="primer N incluido en el ajuste de la pendiente (default 100): con N "
                             "chico dominan los costos fijos y la pendiente no refleja el "
                             "escalamiento del método")
    args = parser.parse_args()

    rows = _read_and_classify(args.csv)

    experiments = {row["experiment"] for row in rows}
    if len(experiments) != 1:
        raise SystemExit("Los CSV mezclan experimentos distintos (" + ", ".join(sorted(experiments))
                         + "): la comparación necesita el mismo barrido con y sin CIM.")
    experiment = experiments.pop()

    series = curves(rows, x_field="N", group_by=("method",))
    if set(key for (key,) in series) != {"bruta", "cim"}:
        raise SystemExit("Hace falta un barrido con el M del CIM y otro con M=1 (fuerza bruta); "
                         f"los CSV sólo traen la serie de {next(iter(series))[0]!r}.")

    # Fuerza bruta al final, así queda dibujada por encima donde las curvas se cruzan.
    ordered = sorted(series.items(), reverse=True)

    positions = categorical_positions(x for curve in series.values() for x in curve.x)

    fig, ax = plt.subplots(figsize=(8.5, 5.5))
    for (method,), curve in ordered:
        label = _series_label(method, curve)
        slope = None if args.no_fit else _log_slope(curve.x, curve.mean_ms, args.fit_from)
        if slope is not None:
            print(f"\najuste log-log de «{label}» para N ≥ {args.fit_from}: t ~ N^{slope:.2f}")
            # La pendiente sólo se lee como pendiente si el gráfico es log-log; en el modo
            # categórico queda en la consola para no sugerir una lectura visual que no aplica.
            if args.log:
                label = f"{label}  (t ~ N^{slope:.2f} para N ≥ {args.fit_from})"

        x = curve.x if args.log else [positions[value] for value in curve.x]
        ax.errorbar(x, curve.mean_ms, yerr=curve.std_ms, capsize=3, lw=1.4, ms=5,
                    label=label, **STYLES[method])
        print(f"\n=== {label} ===")
        print(describe(curve, "N"))

    _print_speedup(series)

    ax.set_xlabel("N (cantidad de partículas)")
    ax.set_ylabel("tiempo de búsqueda de vecinos [ms]")
    if args.log:
        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.autoscale_view()
        use_data_ticks(ax.xaxis, [x for curve in series.values() for x in curve.x])
        # El eje de tiempos queda con el formato por defecto de matplotlib para escala
        # logarítmica: notación científica (10^k) en las décadas, que hace explícita la escala.
    else:
        use_categorical_axis(ax.xaxis, positions)
        ax.set_xlim(-0.5, len(positions) - 0.5)
        uniform_ticks(ax.yaxis)
        ax.set_ylim(bottom=0)

    ax.set_title(f"CIM contra fuerza bruta en función de N\n{_subtitle(experiment, rows)}",
                 fontsize=11)
    # Sólo los ticks mayores llevan grilla: los menores del eje log no tienen etiqueta, así que
    # sus líneas no ayudan a leer valores y ensucian el fondo.
    ax.grid(True, which="major", ls=":", lw=0.5, alpha=0.6)
    ax.legend(frameon=False)

    out = Path(args.out) if args.out else Path(args.csv[0]).with_name(DEFAULT_OUT[experiment])
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(out, dpi=150)
    print(f"\nFigura guardada en {out}")


def _read_and_classify(paths: list[str]) -> list[dict]:
    """Lee cada CSV y etiqueta sus filas como `cim` o `bruta` según el M de todo el archivo."""
    rows: list[dict] = []
    for path in paths:
        file_rows = [row for row in read_csv(path)
                     if row["experiment"] in ("N_free", "N_fixed_density")]
        if not file_rows:
            raise SystemExit(f"{path} no contiene barridos de N (experimentos 'N_free' o "
                             "'N_fixed_density').")
        method = "bruta" if all(row["M"] == 1 for row in file_rows) else "cim"
        for row in file_rows:
            row["method"] = method
        rows.extend(file_rows)
    return rows


def _series_label(method: str, curve: Curve) -> str:
    if method == "bruta":
        return "fuerza bruta (M = 1)"
    # En densidad fija el M escala con L para conservar el lado de celda, así que no es constante
    # dentro de la curva y no aparece en el contexto.
    m = curve.context.get("M")
    return f"CIM (M = {m})" if m is not None else "CIM (M escalado con L)"


def _print_speedup(series: dict[tuple, Curve]) -> None:
    """Speedup t_bruta / t_CIM en los N medidos por ambas curvas."""
    brute, cim = series[("bruta",)], series[("cim",)]
    shared = sorted(set(brute.x) & set(cim.x))
    print("\n=== speedup (t_bruta / t_CIM) ===")
    print(f"{'N':>8}  {'speedup':>8}")
    for n in shared:
        ratio = (brute.mean_ms[list(brute.x).index(n)] / cim.mean_ms[list(cim.x).index(n)])
        print(f"{n:>8}  {ratio:>7.1f}x")


def _log_slope(x: np.ndarray, y: np.ndarray, fit_from: int) -> float | None:
    """Pendiente del ajuste lineal en log-log: el exponente α de t ~ N^α."""
    mask = (x >= fit_from) & (x > 0) & (y > 0)
    if mask.sum() < 2:
        return None
    return float(np.polyfit(np.log(x[mask]), np.log(y[mask]), 1)[0])


def _subtitle(experiment: str, rows: list[dict]) -> str:
    if experiment == "N_free":
        parts = [f"L = {rows[0]['L']:g} fijo (densidad libre)"]
    else:
        density = rows[0]["N"] / rows[0]["L"] ** 2
        parts = [f"densidad fija: ρ = {density:.2f}, L = √(N/ρ)"]
    parts.append(f"rc = {rows[0]['rc']:g}")
    parts.append("con contorno periódico" if rows[0]["pbc"] else "sin contorno periódico")
    return ",  ".join(parts)


if __name__ == "__main__":
    main()
