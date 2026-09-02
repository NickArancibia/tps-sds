"""Curvas input vs observable a partir de `out/summary.csv` (correr antes aggregate.py).

Figuras:
- `<model>_va_vs_eta.png` / `<model>_s_vs_eta.png`: observable estacionario vs η, una curva
  por ρ ∈ {2, 4, 8}, promedio sobre 50 seeds con barra de error (desvío estándar muestral).
- `va_vs_s_<model>.png`: correlación entre ambos observables (cada punto es un η), en
  dos paneles (densidades bajas / exigidas) porque no comparten escala en S.
- Comparaciones Vicsek vs votante sobre los mismos ejes, punto (f) del enunciado:
  `comparacion_va_vs_eta_rho<ρ>.png` (punto c), `comparacion_s_vs_eta_rho<ρ>.png`
  (punto d) y `comparacion_va_vs_s.png` (punto e, a una sola densidad).

Las rectas entre puntos son solo guía para el ojo.

Uso:  python3 plot_curves.py
"""

from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np

from common import (LABEL_ETA, LABEL_S, LABEL_S_Y, LABEL_VA, MODEL_LABEL, MODELS,
                    RHO_COLOR, RHO_LABEL, RHO_MARKER, RHOS, SUMMARY_CSV,
                    legend_sidebar, save_figure, use_style)


def load_summary() -> np.ndarray:
    return np.genfromtxt(SUMMARY_CSV, delimiter=",", names=True, encoding="utf-8",
                         dtype=None)


def select(summary, model: str, rho: str) -> np.ndarray:
    rows = summary[(summary["model"] == model) & (summary["rho"] == float(rho))]
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
                    linewidth=1.0, label=f"ρ = {RHO_LABEL[rho]}")
        lo = min(lo, (rows[f"{column}_mean"] - rows[f"{column}_std"]).min())
    ax.set_xlabel(LABEL_ETA)
    ax.set_ylabel(ylabel)
    ax.set_xlim(left=-0.1)
    if full_scale:
        ax.set_ylim(0, 1.05)
    else:
        margin = 0.05 * (1.0 - lo)
        ax.set_ylim(lo - margin, 1.0 + margin)
    legend_sidebar(ax)
    save_figure(fig, f"{model}_{tag}_vs_eta.png")


def plot_model_comparison(summary, rho: str) -> None:
    fig, ax = plt.subplots()
    for model, color, marker in (("vicsek", "tab:blue", "o"), ("voter", "tab:red", "s")):
        rows = select(summary, model, rho)
        ax.errorbar(rows["eta"], rows["va_mean"], yerr=rows["va_std"], color=color,
                    marker=marker, linestyle="-", linewidth=1.0, label=MODEL_LABEL[model])
    ax.set_xlabel(LABEL_ETA)
    ax.set_ylabel(LABEL_VA)
    ax.set_xlim(left=-0.1)
    ax.set_ylim(0, 1.05)
    legend_sidebar(ax)
    save_figure(fig, f"comparacion_va_vs_eta_rho{rho}.png")


#: Estilo por modelo en las figuras comparativas del punto (f) del enunciado.
MODEL_STYLE = (("vicsek", "tab:blue", "o"), ("voter", "tab:red", "s"))


def plot_model_comparison_s(summary, rho: str) -> None:
    """Punto (d) comparado entre modelos: S estacionario vs η, ambos sobre los mismos ejes.

    Eje y acotado a los datos por la misma razón que en `plot_vs_eta`: con ρ ≥ 2 el
    sistema percola y la escala completa [0, 1] aplastaría la variación."""
    fig, ax = plt.subplots()
    lo = 1.0
    for model, color, marker in MODEL_STYLE:
        rows = select(summary, model, rho)
        ax.errorbar(rows["eta"], rows["s_mean"], yerr=rows["s_std"], color=color,
                    marker=marker, linestyle="-", linewidth=1.0, label=MODEL_LABEL[model])
        lo = min(lo, (rows["s_mean"] - rows["s_std"]).min())
    ax.set_xlabel(LABEL_ETA)
    ax.set_ylabel(LABEL_S_Y)
    ax.set_xlim(left=-0.1)
    margin = 0.05 * (1.0 - lo) or 0.01
    ax.set_ylim(lo - margin, 1.0 + margin)
    legend_sidebar(ax)
    save_figure(fig, f"comparacion_s_vs_eta_rho{rho}.png")


#: Densidad usada en la comparación entre modelos del punto (e). Tiene que ser una de
#: las bajas: con ρ >= 2 el sistema percola y todos los puntos caen en S > 0.99. Entre
#: las tres, 1/π (N = 32) es la que recorre el rango más amplio en los dos observables
#: (S de 0.15 a 0.98, v_a de 0.16 a 1) y la que tiene las barras de error más chicas.
RHO_COMPARACION = "0.3183"


def plot_model_comparison_va_vs_s(summary) -> None:
    """Punto (e) comparado entre modelos, a una sola densidad.

    El punto (e) pide distinguir densidades y eso lo cubre `plot_va_vs_s`, una figura
    por modelo. Acá el punto (f) solo pide comparar las dos reglas, así que va una
    densidad como caso típico —igual criterio que `comparacion_va_vs_eta_rho*`—. Con
    las seis series juntas (dos modelos x tres densidades) las nubes se superponen y
    no se distingue nada, menos todavía entre densidades de un mismo modelo.

    Los puntos van unidos por segmentos rectos en orden de η: guía para el ojo, no
    interpolación (GuiaPresentaciones §46)."""
    fig, ax = plt.subplots()
    for model, color, marker in MODEL_STYLE:
        rows = select(summary, model, RHO_COMPARACION)  # `select` ya ordena por η
        ax.errorbar(rows["s_mean"], rows["va_mean"], xerr=rows["s_std"],
                    yerr=rows["va_std"], color=color, marker=marker, linestyle="-",
                    linewidth=1.0, label=MODEL_LABEL[model])
    ax.set_xlabel(LABEL_S)
    ax.set_ylabel(LABEL_VA)
    ax.set_xlim(0, 1.05)
    ax.set_ylim(0, 1.05)
    legend_sidebar(ax)
    save_figure(fig, "comparacion_va_vs_s.png")


#: Densidades bajas y exigidas. En un solo eje lineal las exigidas se aplastan contra
#: S = 1 y tapan la correlación de las bajas, así que van en paneles separados.
RHOS_BAJAS = ("0.1061", "0.1592", "0.3183")
RHOS_EXIGIDAS = ("2", "4", "8")


def _zoom_xlim(ax, summary, models) -> None:
    """Acota el panel de densidades exigidas al rango que ocupan sus barras de error.

    Con un limite fijo las barras de rho = 2, que llegan a S ~ 0.945, se salian del eje
    y cruzaban el panel como lineas sueltas."""
    lo = min(float((select(summary, m, r)["s_mean"] - select(summary, m, r)["s_std"]).min())
             for m in models for r in RHOS_EXIGIDAS)
    ax.set_xlim(lo - 0.005, 1.005)


def plot_va_vs_s(summary, model: str) -> None:
    """Punto (e): v_a vs S, cada punto un η.

    Dos paneles con el mismo eje vertical. Las densidades bajas recorren S entre
    ~0.12 y 1; las exigidas se quedan en S > 0.99 para todo ruido. Compartir un eje
    x lineal deja a estas últimas apiladas sobre el borde derecho, así que el panel
    derecho se acota a su propio rango. El contraste entre paneles es el resultado:
    a la izquierda v_a crece con S, a la derecha S no se mueve mientras v_a recorre
    casi todo su intervalo."""
    fig, (ax_lo, ax_hi) = plt.subplots(1, 2, sharey=True, figsize=(7.2, 3.2))
    for ax, grupo in ((ax_lo, RHOS_BAJAS), (ax_hi, RHOS_EXIGIDAS)):
        for rho in grupo:
            rows = select(summary, model, rho)
            ax.errorbar(rows["s_mean"], rows["va_mean"], xerr=rows["s_std"],
                        yerr=rows["va_std"], color=RHO_COLOR[rho],
                        marker=RHO_MARKER[rho], linestyle="none",
                        label=f"ρ = {RHO_LABEL[rho]}")
        ax.set_xlabel(LABEL_S)
        ax.legend()
    ax_lo.set_ylabel(LABEL_VA)
    ax_lo.set_xlim(0, 1.05)
    _zoom_xlim(ax_hi, summary, MODELS)
    ax_lo.set_ylim(0, 1.05)
    save_figure(fig, f"va_vs_s_{model}.png")


def main() -> None:
    use_style()
    summary = load_summary()
    for model in MODELS:
        plot_vs_eta(summary, model, "va", LABEL_VA, "va")
        plot_vs_eta(summary, model, "s", LABEL_S_Y, "s", full_scale=False)
        plot_va_vs_s(summary, model)
    for rho in RHOS:
        plot_model_comparison(summary, rho)
        plot_model_comparison_s(summary, rho)
    plot_model_comparison_va_vs_s(summary)


if __name__ == "__main__":
    main()
