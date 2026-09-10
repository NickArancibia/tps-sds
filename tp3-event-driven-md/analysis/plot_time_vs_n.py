"""Punto 1.1: tiempo de ejecución promedio ± desvío en función de N (mesa vacía, t_f = 30 s).

Lee `output/time_vs_n/N<N>/s<seed>/run.json` (generados por `scripts/run_time_vs_n.sh`), toma
`loopTimeMs` (solo el lazo de eventos, sin generación de la condición inicial ni escritura) y
promedia entre seeds. La barra de error es el desvío estándar muestral entre realizaciones.

Salidas:
- `analysis/out/time_vs_n.csv`: N, realizaciones, tiempo medio (s), desvío (s), eventos medios.
- `analysis/figures/time_vs_n.png`: tiempo vs N en log-log (los datos cruzan varios órdenes de
  magnitud); las rectas entre puntos son guía para el ojo.

Uso:  python3 plot_time_vs_n.py
"""

from __future__ import annotations

import csv

import numpy as np

from common import (LABEL_N, OUT_DIR, OUTPUT, load_run_meta, mean_std, save_figure,
                    use_style)

import matplotlib.pyplot as plt  # noqa: E402  (common configura el backend)


def collect() -> list[dict]:
    rows = []
    for n_dir in sorted(OUTPUT.joinpath("time_vs_n").glob("N*"),
                        key=lambda p: int(p.name[1:])):
        times, events = [], []
        for run_json in n_dir.glob("s*/run.json"):
            meta = load_run_meta(run_json.parent)
            times.append(meta["loopTimeMs"] / 1e3)
            events.append(meta["events"]["total"])
        if not times:
            continue
        mean, std = mean_std(times)
        rows.append({"N": int(n_dir.name[1:]), "runs": len(times), "time_mean_s": mean,
                     "time_std_s": std, "events_mean": float(np.mean(events))})
    return rows


def write_csv(rows: list[dict]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUT_DIR / "time_vs_n.csv"
    with open(path, "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(f"  {path.relative_to(OUT_DIR.parent.parent)}")


def log_ticks(lo: float, hi: float) -> list[float]:
    """Potencias de 10 que cubren [lo, hi] (rótulos equiespaciados, sin marcas intermedias)."""
    return [10.0 ** k for k in range(int(np.floor(np.log10(lo))), int(np.ceil(np.log10(hi))) + 1)]


def main() -> None:
    rows = collect()
    if not rows:
        raise SystemExit("No hay corridas en output/time_vs_n: correr scripts/run_time_vs_n.sh")
    write_csv(rows)
    for r in rows:
        print(f"  N={r['N']:4d}  {r['runs']:2d} corridas  t = {r['time_mean_s']:.3f} ± "
              f"{r['time_std_s']:.3f} s  ({r['events_mean']:.0f} eventos)")

    use_style()
    fig, ax = plt.subplots()
    ns = [r["N"] for r in rows]
    means = [r["time_mean_s"] for r in rows]
    stds = [r["time_std_s"] for r in rows]
    ax.errorbar(ns, means, yerr=stds, color="tab:blue", marker="o", linestyle="--",
                linewidth=1.0)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xticks(ns, labels=[str(n) for n in ns])
    yticks = log_ticks(min(means), max(means))
    ax.set_ylim(yticks[0], yticks[-1])
    ax.set_yticks(yticks, labels=[rf"$10^{{{int(np.log10(t))}}}$" for t in yticks])
    ax.minorticks_off()
    ax.set_xlabel(LABEL_N)
    ax.set_ylabel("Tiempo de ejecución (s)")
    save_figure(fig, "time_vs_n.png")


if __name__ == "__main__":
    main()
