"""Tiempos de ejecución del CIM: TP2 (dentro de la simulación) vs bench del TP1 (punto g).

Comparación a igual geometría (L = 10, M = 10, r_c = 1, PBC, partículas puntuales) para
N = 200, 400, 800 (ρ = 2, 4, 8):
- TP1: `bench_tp2_geometry_pbc.csv`, bench del TP1 con `--fresh --seeds 50`: 50
  configuraciones uniformes con semillas distintas, cada una cronometrada una sola vez
  tras calentar el JIT. Así ninguna llamada repite una configuración ya vista, igual que
  en el TP2, donde las partículas se mueven entre llamada y llamada. (El protocolo
  original del TP1, 500 llamadas seguidas sobre una misma configuración, da 2x menos en
  N = 200 porque el procesador memoriza el recorrido repetido; no es comparable.)
  El CSV no registra los radios, pero se verificó que se corrió con r = 0: (a) el generador
  del TP1 rechaza solapamientos y con los radios default (0.23-0.26) N = 800 en L = 10 es
  imposible (área de partículas > área de la caja); (b) los `neighbor_pairs` medidos calzan
  con la predicción para puntuales, dist(centros) < r_c (615/2531/10065 vs ~625/2507/10041),
  y no con el criterio borde a borde de radios default (~1388/5566/22291).
- TP2: tiempos por llamada guardados en cada `run.json` de `output/cimbench` (una llamada
  por paso, intercalada con la dinámica). Se promedia la segunda mitad de cada corrida
  (mismo criterio que los observables) y luego entre corridas; la barra es el desvío
  estándar entre corridas.

Las dos series se miden en la misma máquina: un tiempo de ejecución solo es comparable
contra otro medido en el mismo hardware. Por eso el TP2 no se toma de `output/sweep` (que
puede venir de otra máquina) sino de `output/cimbench`, un conjunto chico hecho para esto:
5 seeds por (modelo, ρ) con η = 0.5 y 1000 pasos, o sea 500 llamadas cronometradas por
corrida. El tiempo por llamada sí
depende de η (con η = 0,5 Vicsek forma bandadas y las celdas quedan desbalanceadas: ~1,4×
más lento que con η = 6,28 en N = 200), por eso se fija un único η para la serie.
Regenerar con `scripts/run_cimbench.sh`.

Figura: `cim_tp1_vs_tp2.png`, tiempo por llamada vs N en log-log (los datos cruzan casi dos
órdenes de magnitud). Las rectas entre puntos son guía para el ojo.

Uso:  python3 plot_cim_times.py
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

import numpy as np

from common import (MODEL_LABEL, MODELS, TP_ROOT, legend_sidebar, save_figure,
                    use_style)

import matplotlib.pyplot as plt  # noqa: E402  (common configura el backend)

TP1_BENCH = TP_ROOT.parent / "tp1-cell-index-method" / "output" / "bench" / "bench_tp2_geometry_pbc.csv"

#: Densidades con N comparable al TP1 (ρ = N/L², L = 10).
RHO_N = (("2", 200), ("4", 400), ("8", 800))

SERIES_STYLE = {
    "tp1": ("TP1", "black", "^"),
    "vicsek": ("TP2 Vicsek", "tab:blue", "o"),
    "voter": ("TP2 votante", "tab:red", "s"),
}


def tp1_times() -> dict[int, tuple[float, float]]:
    """N -> (media, desvío) entre configuraciones del tiempo por llamada (ms) del TP1."""
    by_n: dict[int, list[float]] = {}
    with open(TP1_BENCH) as fh:
        for row in csv.DictReader(fh):
            by_n.setdefault(int(row["N"]), []).append(int(row["time_ns"]) / 1e6)
    return {n: (float(np.mean(ts)), float(np.std(ts, ddof=1))) for n, ts in by_n.items()}


def tp2_times(model: str) -> dict[int, tuple[float, float]]:
    """N -> (media, desvío) entre corridas del tiempo por llamada (ms) en la segunda mitad."""
    result = {}
    for rho, n in RHO_N:
        means = []
        for run_json in (TP_ROOT / "output" / "cimbench" / model / f"rho{rho}").glob("s*/run.json"):
            with open(run_json) as fh:
                times = np.asarray(json.load(fh)["cimTimesNs"], dtype=float)
            means.append(times[len(times) // 2:].mean() / 1e6)
        result[n] = (float(np.mean(means)), float(np.std(means, ddof=1)))
    return result


def main() -> None:
    use_style()
    fig, ax = plt.subplots()
    series = [("tp1", tp1_times())] + [(m, tp2_times(m)) for m in MODELS]
    for key, data in series:
        label, color, marker = SERIES_STYLE[key]
        ns = sorted(data)
        means = [data[n][0] for n in ns]
        stds = [data[n][1] for n in ns]
        ax.errorbar(ns, means, yerr=stds, color=color, marker=marker,
                    linestyle="--", linewidth=1.0, label=label)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xticks([200, 400, 800], labels=["200", "400", "800"])
    # Eje log con rótulos equiespaciados (AGENTS.md §3): solo potencias de 10, sin marcas
    # intermedias sin rótulo. Los datos cubren 0,03-0,7 ms, dentro de 10^-2 .. 10^0.
    ax.set_ylim(0.01, 1.0)
    ax.set_yticks([0.01, 0.1, 1.0], labels=[r"$10^{-2}$", r"$10^{-1}$", r"$10^{0}$"])
    ax.minorticks_off()
    ax.set_xlabel("Número de partículas N")
    ax.set_ylabel("Tiempo por llamada al CIM (ms)")
    legend_sidebar(ax)
    save_figure(fig, "cim_tp1_vs_tp2.png")


if __name__ == "__main__":
    main()
