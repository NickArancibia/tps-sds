"""Evolución temporal de los observables: v_a(t) y S(t) para valores característicos de η.

Una figura por (modelo, observable, ρ), con una curva por η (sin ruido / ruido bajo /
ruido intermedio). Cada curva lleva una recta vertical de trazos, de su mismo color, en su
propio comienzo del estado estacionario (validado a ojo, ../../AGENTS.md §3).

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
#: Inicio del estacionario fijado a ojo, clave (tag, model, rho, eta) → t (s), para las
#: curvas donde el criterio automático cae demasiado temprano: v_a con ρ = 1/(3π) y
#: η = 0,5 entra en la banda μ ± 2σ en 413 s (σ es enorme) pero recién llega a ~0,95 en
#: t ≈ 700 s, y después vaga entre 0,4 y 1 sin volver al transitorio.
ONSET_OVERRIDE = {("va", "vicsek", "0.1061", "0.5"): 700.0}

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
    # va_vicsek_rho4: abajo a la izquierda tapaba las rectas de inicio del estacionario.
    "evolucion_va_vicsek_rho4": {"loc": "lower right"},
}


def stationary_onset(time, values, window: int = 100):
    """Comienzo del estacionario de una curva, o None si nunca entra en régimen.

    Criterio: la media móvil centrada (ventana `window`) entra por primera vez en la
    banda μ ± max(2σ, 0.02) del último cuarto de la corrida. Una amplitud de
    fluctuación grande (votante con η = 0.5, densidades bajas) no invalida el
    estacionario: la curva oscila alrededor de un valor fijo, solo que con banda ancha.
    Umbrales calibrados y validados a ojo sobre cada figura.
    """
    duration = time[-1]
    tail = values[time >= 0.75 * duration]
    mu, sigma = tail.mean(), tail.std()
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


def plot_evolution(model: str, rho: str, column: str, ylabel: str, tag: str) -> None:
    fig, ax = plt.subplots()
    runs = {eta: load_observables(OUTPUT / "sweep" / model / f"rho{rho}" / f"eta{eta}" / f"s{SEED}")
            for eta in ETAS}
    lo = min(data[column].min() for data in runs.values())
    if lo >= 0.75:
        # Eje acotado a los datos para que la variación real no quede aplastada
        # contra el techo, pero con un span mínimo: en ρ = 4 y 8 la fracción vale
        # ~1 siempre y un eje pegado a los datos ampliaría puro ruido.
        top = 1.005
        ylim = (min(lo - 0.02, top - SPAN_MIN), top)
    else:
        ylim = (0.0, 1.05)
    marks: list[float] = []
    for eta, data in runs.items():
        ax.plot(data["time"], data[column], color=ETA_COLOR[eta], linewidth=1.2,
                zorder=ETA_ZORDER[eta], label=f"η = {eta} rad")
        onset = ONSET_OVERRIDE.get((tag, model, rho, eta),
                                   stationary_onset(data["time"], data[column]))
        if onset is None:
            print(f"  (sin estacionario: {tag} {model} rho={rho} eta={eta})")
        else:
            # Marca en t=0: corrida un 1% del eje hacia adentro, si no queda encima del
            # borde del gráfico, invisible. Si dos curvas comparten inicio (típico: las
            # dos con ruido del votante, estacionarias desde t = 0), la segunda se
            # corre otro 1% para que la primera no la tape.
            step = 0.01 * data["time"][-1]
            x = max(onset, step)
            while any(abs(x - m) < step / 2 for m in marks):
                x += step
            marks.append(x)
            ax.axvline(x, color=ETA_COLOR[eta], linestyle="--", linewidth=1.3,
                       zorder=ETA_ZORDER[eta] + 0.25)
    ax.set_xlabel(LABEL_TIME)
    ax.set_ylabel(ylabel)
    ax.set_xlim(0, xlim_right(runs, column))
    ax.set_ylim(*ylim)
    name = f"evolucion_{tag}_{model}_rho{rho}"
    legend_sidebar(ax, **LEGEND_LOC.get(name, {}))
    save_figure(fig, f"{name}.png")


def main() -> None:
    use_style()
    for model in MODELS:
        for rho in RHOS:
            for column, ylabel, tag in OBSERVABLES:
                plot_evolution(model, rho, column, ylabel, tag)


if __name__ == "__main__":
    main()
