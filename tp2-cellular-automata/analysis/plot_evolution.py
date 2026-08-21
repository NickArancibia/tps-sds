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

from common import (LABEL_S, LABEL_TIME, LABEL_VA, MODEL_LABEL, MODELS, OUTPUT,
                    RHO_LABEL, RHOS, load_observables, save_figure, use_style)

#: η característicos: sin ruido / ruido bajo / ruido intermedio.
ETAS = ("0.0", "0.5", "2.0")
ETA_COLOR = {"0.0": "tab:green", "0.5": "tab:blue", "2.0": "tab:orange"}
#: Seed del barrido usada para las evoluciones típicas.
SEED = 1
#: Densidades bajas (N = 11, 16, 32): las curvas de v_a con ruido fluctúan tanto que las
#: tres η juntas son ilegibles → dos figuras por densidad, cada ruido contra η = 0.
LOW_RHOS = ("0.1061", "0.1592", "0.3183")

#: (columna, label, tag). El eje y de S se acota a los datos cuando todas las curvas viven
#: cerca de 1 (densidades que percolan): la escala completa [0, 1] aplastaría la estructura.
OBSERVABLES = (("polarization", LABEL_VA, "va"),
               ("largest_cluster_fraction", LABEL_S, "s"))


def stationary_onset(time, values, window: int = 100, drift_tol: float = 0.12):
    """Comienzo del estacionario de una curva, o None si no se estaciona.

    Criterio: la media móvil centrada (ventana `window`) entra por primera vez en la
    banda μ ± max(2σ, 0.02) del último cuarto de la corrida. Veto de deriva: si las
    medias de 4 bloques de la última mitad difieren en más de `drift_tol`, la curva
    sigue vagando y no se marca (ej.: votante con η = 0.5, spread 0.15–0.26).
    Umbrales calibrados y validados a ojo sobre cada figura.
    """
    duration = time[-1]
    tail = values[time >= 0.75 * duration]
    mu, sigma = tail.mean(), tail.std()
    last = values[time >= 0.5 * duration]
    block_means = [block.mean() for block in np.array_split(last, 4)]
    if max(block_means) - min(block_means) > drift_tol:
        return None
    moving = np.convolve(values, np.ones(window) / window, mode="valid")
    t_moving = time[window // 2:window // 2 + len(moving)]
    inside = np.abs(moving - mu) <= max(2.0 * sigma, 0.02)
    if not inside.any():
        return None
    first = np.flatnonzero(inside)[0]
    # Estacionaria desde la primera ventana → el estacionario empieza en t = 0 (la ventana
    # centrada correría la marca artificialmente a t = window/2).
    return float(time[0]) if first == 0 else float(t_moving[first])


def plot_evolution(model: str, rho: str, column: str, ylabel: str, tag: str,
                   etas: tuple[str, ...] = ETAS, suffix: str = "") -> None:
    fig, ax = plt.subplots()
    runs = {eta: load_observables(OUTPUT / "sweep" / model / f"rho{rho}" / f"eta{eta}" / f"s{SEED}")
            for eta in etas}
    lo = min(data[column].min() for data in runs.values())
    ylim = (0.75, 1.01) if lo >= 0.75 else (0.0, 1.05)
    for eta, data in runs.items():
        ax.plot(data["time"], data[column], color=ETA_COLOR[eta], linewidth=1.2,
                label=f"η = {eta} rad")
        onset = stationary_onset(data["time"], data[column])
        if onset is None:
            print(f"  (sin estacionario: {tag} {model} rho={rho} eta={eta})")
        else:
            level = data[column][data["time"] >= onset].mean()
            span = ylim[1] - ylim[0]
            half = 0.067 * span
            # Marca en t=0: corrida un 1% del eje hacia adentro, si no queda negro sobre
            # negro, invisible encima del borde del gráfico.
            x = max(onset, 0.01 * data["time"][-1])
            ax.plot([x, x],
                    [max(level - half, ylim[0] + 0.01 * span),
                     min(level + half, ylim[1] - 0.01 * span)],
                    color="black", linestyle="--", linewidth=1.5)
    ax.set_xlabel(LABEL_TIME)
    ax.set_ylabel(ylabel)
    ax.set_xlim(left=0)
    ax.set_ylim(*ylim)
    ax.legend(title=f"{MODEL_LABEL[model]}, ρ = {RHO_LABEL[rho]}", loc="center right")
    save_figure(fig, f"evolucion_{tag}_{model}_rho{rho}{suffix}.png")


def main() -> None:
    use_style()
    for model in MODELS:
        for rho in RHOS:
            for column, ylabel, tag in OBSERVABLES:
                if tag == "va" and rho in LOW_RHOS:
                    plot_evolution(model, rho, column, ylabel, tag,
                                   etas=("0.0", "0.5"), suffix="_eta0.5")
                    plot_evolution(model, rho, column, ylabel, tag,
                                   etas=("0.0", "2.0"), suffix="_eta2.0")
                else:
                    plot_evolution(model, rho, column, ylabel, tag)


if __name__ == "__main__":
    main()
