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

from common import (LABEL_S_Y, LABEL_TIME, LABEL_VA, MODELS, OUTPUT, RHOS,
                    legend_sidebar, load_observables, save_figure, use_style)

#: η característicos: sin ruido / ruido bajo / ruido intermedio.
ETAS = ("0.0", "0.5", "2.0")
#: Colores independientes (azul / rojo / negro): verde y naranja se confundían entre sí.
#: η = 0 (curva suave que satura en 1) va detrás para no tapar las curvas con ruido.
ETA_COLOR = {"0.0": "black", "0.5": "tab:blue", "2.0": "tab:red"}
ETA_ZORDER = {"0.0": 1.5, "0.5": 2.5, "2.0": 2.0}
#: Seed del barrido usada para las evoluciones típicas.
SEED = 1
#: Densidades bajas (N = 11, 16, 32): las curvas de v_a con ruido fluctúan tanto que las
#: tres η juntas son ilegibles → dos figuras por densidad, cada ruido contra η = 0.
LOW_RHOS = ("0.1061", "0.1592", "0.3183")

#: Alto mínimo del eje y cuando se lo acota a los datos, en unidades del observable.
#: Evita ampliar fluctuaciones despreciables hasta que parezcan una señal.
SPAN_MIN = 0.10

#: (columna, label, tag). El eje y de S se acota a los datos cuando todas las curvas viven
#: cerca de 1 (densidades que percolan): la escala completa [0, 1] aplastaría la estructura.
OBSERVABLES = (("polarization", LABEL_VA, "va"),
               ("largest_cluster_fraction", LABEL_S_Y, "s"))

#: Override manual de la leyenda (clave = nombre del archivo sin extensión; valor = kwargs
#: de `ax.legend`). La colocación automática (`legend_sidebar`) elige la esquina con menos
#: superposición, pero en estos casos igual cae sobre algo:
#: - s_voter_rho0.3183: tapaba la marca de inicio del estacionario de la curva negra.
#: - va_voter_rho4: tapaba la curva azul; va arriba a la derecha, debajo de la curva
#:   negra saturada en 1 (por eso el bbox baja el borde superior a y = 0.92).
LEGEND_LOC = {
    "evolucion_s_voter_rho0.3183": {"loc": "upper right"},
    "evolucion_va_voter_rho4": {"loc": "upper right", "bbox_to_anchor": (0.98, 0.92)},
}


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


def xlim_right(runs, column, tol: float = 0.01) -> float:
    """Límite derecho del eje temporal.

    Las corridas de votante con η = 0 duran 10000 pasos (ordenan lento) pero saturan en
    v_a = S = 1 mucho antes; sin recorte el eje se estira hasta 10000 con una única curva
    plana y aplasta la dinámica del resto. Si la corrida más larga supera 1.5× a la
    siguiente y su cola (más allá de esa longitud) es plana, se corta en la longitud de la
    siguiente. No se descartan datos: la cola recortada es constante.
    """
    ends = sorted(float(data["time"][-1]) for data in runs.values())
    if len(ends) < 2 or ends[-1] <= 1.5 * ends[-2]:
        return ends[-1]
    longest = max(runs.values(), key=lambda data: data["time"][-1])
    tail = longest[column][longest["time"] > ends[-2]]
    if tail.size and (tail.max() - tail.min()) <= tol:
        return ends[-2]
    return ends[-1]


def plot_evolution(model: str, rho: str, column: str, ylabel: str, tag: str,
                   etas: tuple[str, ...] = ETAS, suffix: str = "") -> None:
    fig, ax = plt.subplots()
    runs = {eta: load_observables(OUTPUT / "sweep" / model / f"rho{rho}" / f"eta{eta}" / f"s{SEED}")
            for eta in etas}
    lo = min(data[column].min() for data in runs.values())
    if lo >= 0.75:
        # Eje acotado a los datos para que la variación real no quede aplastada
        # contra el techo, pero con un span mínimo: en ρ = 4 y 8 la fracción vale
        # ~1 siempre y un eje pegado a los datos ampliaría puro ruido.
        top = 1.005
        ylim = (min(lo - 0.02, top - SPAN_MIN), top)
    else:
        ylim = (0.0, 1.05)
    for eta, data in runs.items():
        ax.plot(data["time"], data[column], color=ETA_COLOR[eta], linewidth=1.2,
                zorder=ETA_ZORDER[eta], label=f"η = {eta} rad")
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
    ax.set_xlim(0, xlim_right(runs, column))
    ax.set_ylim(*ylim)
    name = f"evolucion_{tag}_{model}_rho{rho}{suffix}"
    legend_sidebar(ax, **LEGEND_LOC.get(name, {}))
    save_figure(fig, f"{name}.png")


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
