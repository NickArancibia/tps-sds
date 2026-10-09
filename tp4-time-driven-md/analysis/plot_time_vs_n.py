"""Punto 2.1b: tiempo de ejecución vs N de los dos motores, medidos en la misma máquina.

Lee (scripts/run_time_vs_n.sh):
  output/billiard/time_vs_n/N<N>/s<seed>/run.json   TP4, paso temporal: obstáculos en contacto,
                                                     red hexagonal, dt = 10⁻⁵ s, t_f = 30 s
  output/tp3_time_vs_n/N<N>/s<seed>/run.json        TP3, eventos: punto 1.1 (mesa vacía), t_f = 30 s
El tiempo de una corrida es loopTimeMs (solo el lazo de integración / de eventos). Por cada N:
promedio entre realizaciones ± desvío estándar entre realizaciones (ddof = 1; un escalar por
realización). Figura analysis/figures/ej2/tiempo_vs_n.png (log-log); por stdout la tabla y la
pendiente log-log entre N consecutivos (exponente local de t ∝ N^α).

Uso: python3 analysis/plot_time_vs_n.py
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from common import TP_ROOT, decade_ticks, save_figure, use_style

import matplotlib.pyplot as plt  # noqa: E402  (después de common: backend Agg)

ENGINES = (
    # (directorio, leyenda, marcador, color)
    (TP_ROOT / "output" / "tp3_time_vs_n", "eventos", "s", "tab:red"),
    (TP_ROOT / "output" / "billiard" / "time_vs_n", "paso temporal", "o", "tab:blue"),
)


def load(root: Path) -> list[tuple[int, float, float, int]]:
    """→ filas (N, promedio, desvío, realizaciones) con el tiempo del lazo en s."""
    rows = []
    for n_dir in sorted(root.glob("N*"), key=lambda p: int(p.name[1:])):
        times = np.array([json.loads(p.read_text())["loopTimeMs"] / 1e3 for p in n_dir.glob("s*/run.json")])
        if times.size:
            rows.append((int(n_dir.name[1:]), times.mean(), times.std(ddof=1) if times.size > 1 else 0.0, times.size))
    return rows


def main() -> None:
    use_style()
    fig, ax = plt.subplots()
    for root, label, marker, color in ENGINES:
        rows = load(root)
        if not rows:
            print(f"sin corridas en {root}")
            continue
        n, mean, std, runs = np.array(rows).T
        print(f"\n{label} ({root.relative_to(TP_ROOT)}): N | tiempo (s) promedio ± desvío | realizaciones")
        for row in rows:
            print(f"  {row[0]:4d} | {row[1]:.4g} ± {row[2]:.2g} | {row[3]}")
        slopes = np.diff(np.log(mean)) / np.diff(np.log(n))
        print("  exponente local α (t ∝ N^α) entre N consecutivos: "
              + ", ".join(f"{int(a)}–{int(b)}: {s:.2f}" for a, b, s in zip(n[:-1], n[1:], slopes)))
        ax.errorbar(n, mean, yerr=std, fmt=marker + "-", color=color, ms=6, mfc="white", mew=1.5, lw=1.0,
                    elinewidth=1.5, capsize=4, capthick=1.5, label=label)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(10, 1000)
    decade_ticks(ax.xaxis, 1, 3)
    lo, hi = ax.get_ylim()
    lo_e, hi_e = int(np.floor(np.log10(lo))), int(np.ceil(np.log10(hi)))
    ax.set_ylim(10.0**lo_e, 10.0**hi_e)
    decade_ticks(ax.yaxis, lo_e, hi_e)
    ax.set_xlabel("Número de partículas")
    ax.set_ylabel("Tiempo de ejecución (s)")
    ax.legend(loc="lower right")
    save_figure(fig, "ej2", "tiempo_vs_n.png")


if __name__ == "__main__":
    main()
