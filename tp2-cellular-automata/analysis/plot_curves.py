"""Curvas input vs observable a partir de `out/summary.csv` (correr antes aggregate.py).

Figuras:
- `<model>_va_vs_eta.png` / `<model>_s_vs_eta.png`: observable estacionario vs η, una curva
  por ρ ∈ {2, 4, 8}, promedio sobre 50 seeds con barra de error (desvío estándar muestral).
- `comparacion_va_vs_eta_rho<ρ>.png`: Vicsek vs votante sobre los mismos ejes.
- `va_vs_s_<model>.png`: correlación entre ambos observables (cada punto es un η).

Las rectas entre puntos son solo guía para el ojo.

Uso:  python3 plot_curves.py
"""

from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np

from common import (LABEL_ETA, LABEL_S, LABEL_VA, MODEL_LABEL, MODELS, RHO_COLOR,
                    RHO_MARKER, RHOS, SUMMARY_CSV, save_figure, use_style)


def load_summary() -> np.ndarray:
    return np.genfromtxt(SUMMARY_CSV, delimiter=",", names=True, encoding="utf-8",
                         dtype=None)


def select(summary, model: str, rho: int) -> np.ndarray:
    rows = summary[(summary["model"] == model) & (summary["rho"] == rho)]
    return rows[np.argsort(rows["eta"])]


def plot_vs_eta(summary, model: str, column: str, ylabel: str, tag: str,
                full_scale: bool = True) -> None:
    """Si full_scale=False el eje y se acota a los datos: con ρ ≥ 2 y r_c = 1 el sistema
    percola y S ≈ 1 siempre; la escala completa [0, 1] aplastaría la única variación."""
    fig, ax = plt.subplots()
    lo = 1.0
    for rho in RHOS:
        rows = select(summary, model, rho)
        ax.errorbar(rows["eta"], rows[f"{column}_mean"], yerr=rows[f"{column}_std"],
                    color=RHO_COLOR[rho], marker=RHO_MARKER[rho], linestyle="-",
                    linewidth=1.0, label=f"ρ = {rho}")
        lo = min(lo, (rows[f"{column}_mean"] - rows[f"{column}_std"]).min())
    ax.set_xlabel(LABEL_ETA)
    ax.set_ylabel(ylabel)
    ax.set_xlim(left=-0.1)
    if full_scale:
        ax.set_ylim(0, 1.05)
    else:
        margin = 0.05 * (1.0 - lo)
        ax.set_ylim(lo - margin, 1.0 + margin)
    ax.legend(title=MODEL_LABEL[model])
    save_figure(fig, f"{model}_{tag}_vs_eta.png")


def plot_model_comparison(summary, rho: int) -> None:
    fig, ax = plt.subplots()
    for model, color, marker in (("vicsek", "tab:blue", "o"), ("voter", "tab:red", "s")):
        rows = select(summary, model, rho)
        ax.errorbar(rows["eta"], rows["va_mean"], yerr=rows["va_std"], color=color,
                    marker=marker, linestyle="-", linewidth=1.0, label=MODEL_LABEL[model])
    ax.set_xlabel(LABEL_ETA)
    ax.set_ylabel(LABEL_VA)
    ax.set_xlim(left=-0.1)
    ax.set_ylim(0, 1.05)
    ax.legend(title=f"ρ = {rho}")
    save_figure(fig, f"comparacion_va_vs_eta_rho{rho}.png")


def plot_va_vs_s(summary, model: str) -> None:
    fig, ax = plt.subplots()
    for rho in RHOS:
        rows = select(summary, model, rho)
        ax.errorbar(rows["s_mean"], rows["va_mean"], xerr=rows["s_std"], yerr=rows["va_std"],
                    color=RHO_COLOR[rho], marker=RHO_MARKER[rho], linestyle="none",
                    label=f"ρ = {rho}")
    ax.set_xlabel(LABEL_S)
    ax.set_ylabel(LABEL_VA)
    ax.set_xlim(right=1.005)
    ax.set_ylim(0, 1.05)
    ax.legend(title=MODEL_LABEL[model])
    save_figure(fig, f"va_vs_s_{model}.png")


def main() -> None:
    use_style()
    summary = load_summary()
    for model in MODELS:
        plot_vs_eta(summary, model, "va", LABEL_VA, "va")
        plot_vs_eta(summary, model, "s", LABEL_S, "s", full_scale=False)
        plot_va_vs_s(summary, model)
    for rho in RHOS:
        plot_model_comparison(summary, rho)


if __name__ == "__main__":
    main()
