"""Punto 2.3: distribución de probabilidad del módulo de la velocidad, f(v), y ajuste de
Maxwell-Boltzmann 2D.

Lee output/billiard/speed_dist/s<seed>/ (scripts/run_speed_dist.sh): las velocidades de las N
partículas en cada estado guardado de dynamic.txt (sin interpolar).

Definiciones (realización s, estado guardado k en el instante t_k, v_i = |v_i(t_k)|):
  - Rapidez media: <|v|>_s(t_k) = (1/N) Σ_i v_i. Curva = promedio entre realizaciones, banda =
    desvío estándar entre realizaciones (ddof = 1). Sirve para marcar a ojo el inicio del
    estacionario t_est (recta vertical punteada).
  - f_{s,k}(v_b) = (partículas con v_i en el bin b) / (N Δv): densidad de probabilidad (s/m),
    Σ_b f Δv = 1.
  - f(v, t) en un instante: promedio de f_{s,k} entre realizaciones ± desvío entre realizaciones.
  - f(v) estacionaria: promedio de f_{s,k} sobre todos los pares (s, k) con t_k ≥ t_est; barra =
    desvío estándar de esos f_{s,k} instantáneos (ddof = 1), o sea la fluctuación de un instante,
    no el error de la media (criterio del repo, ../AGENTS.md §8.3).
  - Ajuste (Teórica 0): f_MB(v; k_BT) = (m v / k_BT) exp(−m v² / (2 k_BT)); error cuadrático
    E(k_BT) = Σ_b [f(v_b) − f_MB(v_b; k_BT)]² sobre los centros de bin; el mejor k_BT es el que
    minimiza E en una grilla fina.
  - Comparación: m <v²> / 2 en el estacionario (promedio sobre partículas, estados y
    realizaciones) y m v0² / 2.

Figuras en analysis/figures/ej2/:
  rapidez_media_vs_t.png   <|v|>(t), eje t log, recta vertical punteada en t_est
  fv_evolucion.png         f(v) en algunos instantes, del transitorio hasta t_est
  fv_estacionaria_mb.png   f(v) estacionaria ± fluctuación y la curva de MB con el k_BT ajustado
  error_ajuste_mb.png      E(k_BT), con el mínimo marcado
Por stdout: rapidez media en algunos t, k_BT ajustado, m<v²>/2 y m v0²/2.

Uso: python3 analysis/plot_speed_dist.py [--root DIR] [--t-est 1] [--dv 0.05]
         [--times 0.05,0.1,0.2,0.5,1]
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from billiard_common import load_run
from common import TP_ROOT, decade_ticks, save_figure, use_style

import matplotlib.pyplot as plt  # noqa: E402  (después de common: backend Agg)

DEFAULT_ROOT = TP_ROOT / "output" / "billiard" / "speed_dist"


def speeds(root: Path) -> tuple[np.ndarray, np.ndarray, dict]:
    """→ (t de los estados guardados, |v| con forma (realizaciones, estados, N), run.json de una)."""
    paths = sorted(root.glob("s*/run.json"))
    if not paths:
        raise SystemExit(f"sin corridas en {root}")
    runs = [load_run(p.parent) for p in paths]
    return runs[0].t, np.stack([np.hypot(r.vx, r.vy) for r in runs]), json.loads(paths[0].read_text())


def histograms(v: np.ndarray, edges: np.ndarray) -> np.ndarray:
    """v (..., N) → f (..., bins) normalizada como densidad, un histograma por cada fila."""
    flat = v.reshape(-1, v.shape[-1])
    dv = np.diff(edges)
    f = np.array([np.histogram(row, bins=edges)[0] for row in flat]) / (v.shape[-1] * dv)
    return f.reshape(*v.shape[:-1], len(dv))


def mb(v: np.ndarray, kt: float, m: float) -> np.ndarray:
    return m * v / kt * np.exp(-m * v**2 / (2 * kt))


def plot_mean_speed(t: np.ndarray, v: np.ndarray, t_est: float) -> None:
    per_run = v.mean(axis=2)  # (realizaciones, estados)
    mean, std = per_run.mean(axis=0), per_run.std(axis=0, ddof=1)
    keep = t > 0
    fig, ax = plt.subplots()
    ax.fill_between(t[keep], (mean - std)[keep], (mean + std)[keep], color="tab:blue", alpha=0.3, lw=0)
    ax.plot(t[keep], mean[keep], color="tab:blue")
    ax.axvline(t_est, color="black", ls=":", lw=1.5)
    ax.set_xscale("log")
    lo_e, hi_e = int(np.floor(np.log10(t[keep][0]))), int(np.floor(np.log10(t[-1])))
    ax.set_xlim(10.0**lo_e, t[-1])
    decade_ticks(ax.xaxis, lo_e, hi_e)
    ax.set_xlabel("Tiempo (s)")
    ax.set_ylabel("Rapidez media (m/s)")
    save_figure(fig, "ej2", "rapidez_media_vs_t.png")
    print("rapidez media (promedio ± desvío entre realizaciones):")
    for x in (0.01, 0.1, 0.5, 1, 5, 10, 20):
        k = int(np.argmin(np.abs(t - x)))
        print(f"  t = {t[k]:g} s: {mean[k]:.3f} ± {std[k]:.3f} m/s")
    stat = per_run[:, t >= t_est]
    print(f"  estacionario (t ≥ {t_est:g} s): {stat.mean():.3f} m/s, fluctuación instantánea "
          f"{stat.std(ddof=1):.3f} m/s")


def stationary(t: np.ndarray, v: np.ndarray, t_est: float, edges: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    f = histograms(v[:, t >= t_est, :], edges).reshape(-1, len(edges) - 1)
    return f.mean(axis=0), f.std(axis=0, ddof=1)


def plot_evolution(t: np.ndarray, v: np.ndarray, times: list[float], edges: np.ndarray) -> None:
    centers = 0.5 * (edges[1:] + edges[:-1])
    fig, ax = plt.subplots()
    colors = plt.cm.viridis(np.linspace(0, 0.85, len(times)))
    for x, color in zip(times, colors):
        k = int(np.argmin(np.abs(t - x)))
        f = histograms(v[:, k, :], edges)
        ax.errorbar(centers, f.mean(axis=0), yerr=f.std(axis=0, ddof=1), fmt="o-", color=color, ms=3.5,
                    lw=0.9, elinewidth=0.9, capsize=2, label=f"{t[k]:g}")
    ax.set_xlim(0, 2.5)
    ax.set_ylim(0, None)
    ax.set_xlabel("Módulo de la velocidad (m/s)")
    ax.set_ylabel("f(v) (s/m)")
    ax.legend(title="t (s)", loc="upper right")
    save_figure(fig, "ej2", "fv_evolucion.png")


def fit(t: np.ndarray, v: np.ndarray, t_est: float, edges: np.ndarray, m: float, v0: float) -> None:
    centers = 0.5 * (edges[1:] + edges[:-1])
    mean, std = stationary(t, v, t_est, edges)
    kts = np.linspace(0.005, 0.025, 4001)
    errors = np.array([np.sum((mean - mb(centers, kt, m)) ** 2) for kt in kts])
    best = kts[np.argmin(errors)]
    stat_v = v[:, t >= t_est, :]
    half_mv2 = 0.5 * m * np.mean(stat_v**2)
    print(f"ajuste MB (Δv = {edges[1] - edges[0]:g} m/s, estados con t ≥ {t_est:g} s): k_BT = {best:.5f} J, "
          f"E mínimo = {errors.min():.4g} (s/m)²")
    print(f"m<v²>/2 estacionario = {half_mv2:.5f} J;  m v0²/2 = {0.5 * m * v0**2:.5f} J")

    fig, ax = plt.subplots()
    ax.errorbar(centers, mean, yerr=std, fmt="o", color="tab:blue", ms=4, mfc="white", mew=1.2,
                elinewidth=0.9, capsize=2, label="simulación")
    vv = np.linspace(0, edges[-1], 500)
    ax.plot(vv, mb(vv, best, m), color="tab:red", lw=1.5, label="Maxwell-Boltzmann")
    ax.set_xlim(0, 2.5)
    ax.set_ylim(0, None)
    ax.set_xlabel("Módulo de la velocidad (m/s)")
    ax.set_ylabel("f(v) (s/m)")
    ax.legend(loc="upper right")
    save_figure(fig, "ej2", "fv_estacionaria_mb.png")

    fig, ax = plt.subplots()
    ax.plot(kts * 1e3, errors, color="tab:blue")
    ax.axvline(best * 1e3, color="black", ls=":", lw=1.5)
    ax.set_xlabel("Energía térmica efectiva (mJ)")
    ax.set_ylabel("Error cuadrático (s²/m²)")
    ax.set_ylim(0, None)
    save_figure(fig, "ej2", "error_ajuste_mb.png")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--t-est", type=float, default=1.0, help="inicio del estacionario, marcado a ojo (s)")
    parser.add_argument("--dv", type=float, default=0.05, help="ancho de bin (m/s)")
    parser.add_argument("--times", default="0.05,0.1,0.2,0.5,1", help="instantes a graficar en fv_evolucion (s)")
    args = parser.parse_args()

    t, v, meta = speeds(args.root)
    print(f"{v.shape[0]} realizaciones, N = {v.shape[2]}, {len(t)} estados hasta t = {t[-1]:g} s, "
          f"|v| máximo observado {v.max():.2f} m/s")
    v_max = np.ceil(v.max() / args.dv) * args.dv
    edges = np.arange(0, v_max + args.dv / 2, args.dv)

    use_style()
    plot_mean_speed(t, v, args.t_est)
    plot_evolution(t, v, [float(x) for x in args.times.split(",")], np.arange(0, v_max + 0.05, 0.1))
    fit(t, v, args.t_est, edges, meta["m"], meta["v0"])


if __name__ == "__main__":
    main()
