"""Reduce el barrido completo (2 modelos × 3 ρ × 15 η × 50 seeds) a `out/summary.csv`.

Para cada corrida se calcula el promedio temporal de v_a y S en el estado estacionario
(t >= T_STATIONARY); para cada punto (model, ρ, η) se reporta el promedio sobre seeds y su
desvío estándar muestral (ddof=1), que es la barra de error de las curvas η vs observable.

Uso:  python3 aggregate.py
"""

from __future__ import annotations

import csv
from multiprocessing import Pool

import numpy as np

from common import (MODELS, RHOS, SUMMARY_CSV, T_STATIONARY, load_observables,
                    stationary_mean, sweep_etas, sweep_run_dirs)


def _one_run(run_dir) -> tuple[float, float]:
    data = load_observables(run_dir)
    return (stationary_mean(data, "polarization"),
            stationary_mean(data, "largest_cluster_fraction"))


def main() -> None:
    points = [(model, rho, eta)
              for model in MODELS for rho in RHOS for eta in sweep_etas(model, rho)]
    rows = []
    with Pool() as pool:
        for model, rho, eta in points:
            run_dirs = sweep_run_dirs(model, rho, eta)
            per_seed = np.array(pool.map(_one_run, run_dirs))
            va, s = per_seed[:, 0], per_seed[:, 1]
            rows.append({
                "model": model, "rho": rho, "eta": float(eta), "seeds": len(run_dirs),
                "t_stationary": T_STATIONARY,
                "va_mean": va.mean(), "va_std": va.std(ddof=1),
                "s_mean": s.mean(), "s_std": s.std(ddof=1),
            })
            print(f"{model} rho={rho} eta={eta}: v_a = {va.mean():.4f} ± {va.std(ddof=1):.4f}  "
                  f"S = {s.mean():.4f} ± {s.std(ddof=1):.4f}  ({len(run_dirs)} seeds)")

    SUMMARY_CSV.parent.mkdir(parents=True, exist_ok=True)
    with open(SUMMARY_CSV, "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(f"\n{len(rows)} puntos → {SUMMARY_CSV}")


if __name__ == "__main__":
    main()
