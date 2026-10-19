"""Punto 2.3: distribución de probabilidad del módulo de la velocidad, f(v), y ajuste de
Maxwell-Boltzmann 2D.

Lee output/billiard/speed_dist/s<seed>/ (scripts/run_speed_dist.sh): las velocidades de las N
partículas en cada estado guardado de dynamic.txt (sin interpolar).

Definiciones (estado guardado k en el instante t_k, v_i = |v_i(t_k)|). Las R realizaciones se
juntan como si fueran una sola de R·N partículas (pedido 2026-10-19): un único histograma y un
único promedio, sin barras de error. Como todas tienen el mismo N, da exactamente lo mismo que
promediar los histogramas (o las rapideces medias) de cada realización.
  - Rapidez media: v̄(t_k) = (1/(R N)) Σ_{s, i} v_i. Sirve para marcar a ojo el inicio del
    estacionario t_est (recta vertical punteada).
  - f(v_b, t_k) = (partículas de las R realizaciones con v_i en el bin b) / (R N Δv): densidad de
    probabilidad (s/m), Σ_b f Δv = 1.
  - f(v) estacionaria: ídem juntando también todos los estados con t_k ≥ t_est.
  - Ajuste (Teórica 0): f_MB(v; k_BT) = (m v / k_BT) exp(−m v² / (2 k_BT)); error cuadrático
    E(k_BT) = Σ_b [f(v_b) − f_MB(v_b; k_BT)]² sobre los centros de bin; el mejor k_BT es el que
    minimiza E en una grilla fina.
  - Comparación: m <v²> / 2 en el estacionario (promedio sobre partículas, estados y
    realizaciones) y m v0² / 2.

Figuras en analysis/figures/ej2/:
  rapidez_media_vs_t.png   v̄(t), eje t log, recta vertical punteada en t_est
  fv_evolucion.png         f(v) en los instantes de --times, un panel por instante con su propio
                           eje vertical
  fv_estacionaria_mb.png   f(v) estacionaria y la curva de MB con el k_BT ajustado
  error_ajuste_mb.png      E(k_BT), con el mínimo marcado
Por stdout: rapidez media en algunos t, k_BT ajustado, m<v²>/2 y m v0²/2.

Uso: python3 analysis/plot_speed_dist.py [--root DIR] [--t-est 1] [--dv 0.05]
         [--times 0.01,0.1,1]
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


def pooled_histogram(v: np.ndarray, edges: np.ndarray) -> np.ndarray:
    """Todas las rapideces de v (cualquier forma) en un único histograma, normalizado como densidad."""
    return np.histogram(v, bins=edges)[0] / (v.size * np.diff(edges))


def mb(v: np.ndarray, kt: float, m: float) -> np.ndarray:
    return m * v / kt * np.exp(-m * v**2 / (2 * kt))


def plot_mean_speed(t: np.ndarray, v: np.ndarray, t_est: float) -> None:
    mean = v.mean(axis=(0, 2))  # un único promedio por estado sobre las R·N partículas
    keep = t > 0
    fig, ax = plt.subplots()
    ax.plot(t[keep], mean[keep], color="tab:blue")
    ax.axvline(t_est, color="black", ls=":", lw=1.5)
    ax.set_xscale("log")
    lo_e, hi_e = int(np.floor(np.log10(t[keep][0]))), int(np.floor(np.log10(t[-1])))
    ax.set_xlim(10.0**lo_e, t[-1])
    decade_ticks(ax.xaxis, lo_e, hi_e)
    ax.set_xlabel("Tiempo (s)")
    ax.set_ylabel("Rapidez media (m/s)")
    save_figure(fig, "ej2", "rapidez_media_vs_t.png")
    print("rapidez media (todas las partículas de todas las realizaciones):")
    for x in (0.01, 0.1, 0.5, 1, 5, 10, 20):
        k = int(np.argmin(np.abs(t - x)))
        print(f"  t = {t[k]:g} s: {mean[k]:.3f} m/s")
    stat = mean[t >= t_est]
    print(f"  estacionario (t ≥ {t_est:g} s): {stat.mean():.3f} m/s, desvío temporal {stat.std(ddof=1):.3f} m/s")


def plot_evolution(t: np.ndarray, v: np.ndarray, times: list[float], edges: np.ndarray) -> None:
    """Un panel por instante, cada uno con su eje vertical (en t ≈ 0 es un pico en v0). El
    instante va en la leyenda de cada panel (sin títulos dentro de la figura)."""
    fig, axes = plt.subplots(1, len(times), figsize=(2.55 * len(times), 3.6))
    for i, (x, ax) in enumerate(zip(times, axes)):
        k = int(np.argmin(np.abs(t - x)))
        f = pooled_histogram(v[:, k, :], edges)
        e = np.log10(t[k])
        label = f"$10^{{{round(e)}}}$" if np.isclose(e, round(e)) else f"{t[k]:g}"
        ax.stairs(f, edges, fill=True, color="tab:blue", alpha=0.35, label=label)
        ax.stairs(f, edges, color="tab:blue", lw=1.2)
        ax.set_xlim(0, 2.5)
        ax.set_ylim(0, None)
        ax.legend(title="t (s)", loc="upper right", handlelength=1.2)
        if i == 0:
            ax.set_ylabel("f(v) (s/m)")
        if i == len(times) // 2:
            ax.set_xlabel("Módulo de la velocidad (m/s)")
    save_figure(fig, "ej2", "fv_evolucion.png")


def fit(t: np.ndarray, v: np.ndarray, t_est: float, edges: np.ndarray, m: float, v0: float) -> None:
    centers = 0.5 * (edges[1:] + edges[:-1])
    stat_v = v[:, t >= t_est, :]
    f = pooled_histogram(stat_v, edges)
    kts = np.linspace(0.005, 0.025, 4001)
    errors = np.array([np.sum((f - mb(centers, kt, m)) ** 2) for kt in kts])
    best = kts[np.argmin(errors)]
    half_mv2 = 0.5 * m * np.mean(stat_v**2)
    print(f"ajuste MB (Δv = {edges[1] - edges[0]:g} m/s, estados con t ≥ {t_est:g} s): k_BT = {best:.5f} J, "
          f"E mínimo = {errors.min():.4g} (s/m)²")
    print(f"m<v²>/2 estacionario = {half_mv2:.5f} J;  m v0²/2 = {0.5 * m * v0**2:.5f} J")

    fig, ax = plt.subplots()
    ax.stairs(f, edges, fill=True, color="tab:blue", alpha=0.35, label="simulación")
    ax.stairs(f, edges, color="tab:blue", lw=1.2)
    vv = np.linspace(0, edges[-1], 500)
    ax.plot(vv, mb(vv, best, m), color="tab:red", lw=1.5, label="Maxwell-Boltzmann")
    ax.set_xlim(0, 2.5)
    ax.set_ylim(0, None)
    ax.set_xlabel("Módulo de la velocidad (m/s)")
    ax.set_ylabel("f(v) (s/m)")
    ax.legend(loc="upper right")
    save_figure(fig, "ej2", "fv_estacionaria_mb.png")

    # Eje y lineal acotado a E ≤ E_TOP y k_BT solo donde E ≤ E_TOP: con todo el rango (E hasta ~5)
    # el mínimo (E(k_BT*) ~ 4·10⁻³) se ve como 0; así queda entre 0 y la primera marca (0.01).
    e_top = 0.05
    inside = errors <= e_top
    fig, ax = plt.subplots()
    ax.plot(kts[inside] * 1e3, errors[inside], color="tab:blue", zorder=1)
    ax.plot(best * 1e3, errors.min(), "o", color="tab:red", ms=8, zorder=2)
    ax.plot([best * 1e3] * 2, [0, errors.min()], color="tab:red", ls=":", lw=1.5, zorder=1)
    ax.set_xlabel("Energía térmica efectiva (mJ)")
    ax.set_ylabel("Error cuadrático (s²/m²)")
    ax.set_xlim(kts[inside][0] * 1e3, kts[inside][-1] * 1e3)
    # k_BT* rotulado en el eje (en rojo); se sacan las marcas regulares a menos de 0.15 mJ de él.
    kt_mj = best * 1e3
    ticks = sorted([x for x in np.arange(11.5, 13.6, 0.5) if abs(x - kt_mj) > 0.15] + [kt_mj])
    ax.set_xticks(ticks, [f"{x:.2f}" if x == kt_mj else f"{x:.1f}" for x in ticks])
    ax.get_xticklabels()[ticks.index(kt_mj)].set_color("tab:red")
    ax.set_ylim(0, e_top)
    ax.set_yticks(np.arange(0, e_top + 1e-9, 0.01))
    save_figure(fig, "ej2", "error_ajuste_mb.png")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--t-est", type=float, default=1.0, help="inicio del estacionario, marcado a ojo (s)")
    parser.add_argument("--dv", type=float, default=0.05, help="ancho de bin (m/s)")
    parser.add_argument("--times", default="0.01,0.1,1", help="instantes de los paneles de fv_evolucion (s)")
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
