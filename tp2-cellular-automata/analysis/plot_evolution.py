"""Evolución temporal de los observables: v_a(t) y S(t) para valores característicos de η.

Una figura por (modelo, observable, ρ), con una curva por η (sin ruido / ruido bajo /
ruido intermedio). Cada curva lleva una marca punteada corta en su propio comienzo del
estado estacionario (validado a ojo, ../../AGENTS.md §3); las curvas que no se estacionan
en la ventana simulada van sin marca.

Las curvas salen de las corridas del barrido (seed 1): `observables.csv` tiene una fila
por paso en todas las corridas, independientemente de `--every`.

Uso:  python3 plot_evolution.py
"""

from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np

from common import (LABEL_S, LABEL_TIME, LABEL_VA, MODEL_LABEL, MODELS, OUTPUT, RHOS,
                    load_observables, save_figure, use_style)

#: η característicos: sin ruido / ruido bajo / ruido intermedio.
ETAS = ("0.0", "0.5", "2.0")
ETA_COLOR = {"0.0": "tab:green", "0.5": "tab:blue", "2.0": "tab:orange"}
#: Seed del barrido usada para las evoluciones típicas.
SEED = 1

#: (columna, label, tag, ylim). Para S el eje va acotado: con ρ ≥ 2 el sistema percola y
#: S vive entre 0.81 y 1 (mínimo global de las curvas: votante ρ=2, η=0.5); la escala
#: completa [0, 1] aplastaría toda la estructura.
OBSERVABLES = (("polarization", LABEL_VA, "va", (0.0, 1.05)),
               ("largest_cluster_fraction", LABEL_S, "s", (0.75, 1.01)))


def stationary_onset(time, values, window: int = 100, drift_tol: float = 0.12):
    """Comienzo del estacionario de una curva, o None si no se estaciona.

    Criterio: la media móvil centrada (ventana `window`) entra por primera vez en la
    banda μ ± max(2σ, 0.02) del tramo final (últimos 500 pasos). Veto de deriva: si las
    medias de bloques de 250 pasos del último cuarto difieren en más de `drift_tol`, la
    curva sigue vagando y no se marca (ej.: votante con η = 0.5, spread 0.15–0.26).
    Umbrales calibrados y validados a ojo sobre cada figura.
    """
    tail = values[time >= time[-1] - 500.0]
    mu, sigma = tail.mean(), tail.std()
    last = values[time >= time[-1] - 1000.0]
    block_means = [block.mean() for block in np.array_split(last, 4)]
    if max(block_means) - min(block_means) > drift_tol:
        return None
    moving = np.convolve(values, np.ones(window) / window, mode="valid")
    t_moving = time[window // 2:window // 2 + len(moving)]
    inside = np.abs(moving - mu) <= max(2.0 * sigma, 0.02)
    return float(t_moving[np.flatnonzero(inside)[0]]) if inside.any() else None


def plot_evolution(model: str, rho: int, column: str, ylabel: str, tag: str,
                   ylim: tuple[float, float]) -> None:
    fig, ax = plt.subplots()
    for eta in ETAS:
        data = load_observables(OUTPUT / "sweep" / model / f"rho{rho}" / f"eta{eta}" / f"s{SEED}")
        ax.plot(data["time"], data[column], color=ETA_COLOR[eta], linewidth=1.2,
                label=f"η = {eta} rad")
        onset = stationary_onset(data["time"], data[column])
        if onset is None:
            print(f"  (sin estacionario: {tag} {model} rho={rho} eta={eta})")
        else:
            level = data[column][data["time"] >= onset].mean()
            span = ylim[1] - ylim[0]
            half = 0.067 * span
            ax.plot([onset, onset],
                    [max(level - half, ylim[0] + 0.01 * span),
                     min(level + half, ylim[1] - 0.01 * span)],
                    color="black", linestyle="--", linewidth=1.5)
    ax.set_xlabel(LABEL_TIME)
    ax.set_ylabel(ylabel)
    ax.set_xlim(left=0)
    ax.set_ylim(*ylim)
    ax.legend(title=f"{MODEL_LABEL[model]}, ρ = {rho}", loc="center right")
    save_figure(fig, f"evolucion_{tag}_{model}_rho{rho}.png")


def main() -> None:
    use_style()
    for model in MODELS:
        for rho in RHOS:
            for column, ylabel, tag, ylim in OBSERVABLES:
                plot_evolution(model, rho, column, ylabel, tag, ylim)


if __name__ == "__main__":
    main()
