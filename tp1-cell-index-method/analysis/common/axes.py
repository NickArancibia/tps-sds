"""Ayudas de formato de ejes para los gráficos de los puntos 3 y 4.

Los barridos usan valores de `N` log-espaciados, así que en un eje lineal los puntos se amontonan a
la izquierda y en uno logarítmico las etiquetas quedan a distancias dispares (0.001, 0.002, 0.003,
0.005, 0.01...). Por eso el modo por defecto es **categórico**: cada valor medido ocupa una posición
equiespaciada del eje y lleva su propia etiqueta, y el eje de tiempos usa ticks lineales uniformes.

`label_log_ticks` queda para los modos `--log`, donde el eje sí es logarítmico.
"""

from __future__ import annotations

import numpy as np
from matplotlib.ticker import (FixedLocator, FuncFormatter, LogLocator, MaxNLocator, NullLocator)

#: Múltiplos de cada potencia de 10 que reciben etiqueta, según cuántas décadas cubra el eje.
#:
#: En escala logarítmica la parte alta de cada década se comprime: entre 8 y 9 hay 0.051 décadas y
#: entre 9 y 10 apenas 0.046, así que etiquetar 2..9 hace que esas tres etiquetas se pisen. Las
#: listas de acá dejan al menos 0.079 décadas entre etiquetas consecutivas (2-3-5 deja 0.176), y
#: cuantas más décadas entren en el mismo largo, menos etiquetas por década.
SUBS_BY_DECADES = ((2.5, (2, 3, 4, 5, 6, 8)),
                   (4.0, (2, 3, 5)),
                   (float("inf"), (3,)))

#: Pasos admitidos entre ticks del eje de tiempos: múltiplos "redondos" de una potencia de 10.
UNIFORM_STEPS = (1, 2, 2.5, 5, 10)


def decimal_label(value: float, _position: int | None = None) -> str:
    """`0.002` en vez de `2 x 10^-3`, y `1000` en vez de `10^3`."""
    if value == 0:
        return "0"
    if value < 0:
        return ""
    # unique=True corta los dígitos que sobran: los ticks vienen con ruido de punto flotante
    # (0.30000000000000004) y sin esto la etiqueta saldría ilegible.
    return np.format_float_positional(value, precision=4, unique=True, fractional=False, trim="-")


def categorical_positions(values) -> dict[float, int]:
    """Mapea cada valor medido a una posición entera: así todos quedan equiespaciados en el eje."""
    return {value: index for index, value in enumerate(sorted(set(values)))}


def use_categorical_axis(axis, positions: dict[float, int], fontsize: float = 8.0,
                         rotation: float = 0.0) -> None:
    """Convierte el eje en una secuencia de categorías, una etiqueta por valor medido."""
    axis.set_major_locator(FixedLocator(list(positions.values())))
    axis.set_major_formatter(FuncFormatter(
        lambda position, _index=None: _label_at(positions, position)))
    axis.set_minor_locator(NullLocator())
    axis.set_tick_params(which="major", labelsize=fontsize, rotation=rotation)


def _label_at(positions: dict[float, int], position: float) -> str:
    for value, index in positions.items():
        if index == position:
            return decimal_label(value)
    return ""


def uniform_ticks(axis, count: int = 11, fontsize: float = 8.0) -> None:
    """Ticks lineales equiespaciados y con valores redondos, en notación decimal."""
    axis.set_major_locator(MaxNLocator(nbins=count, steps=list(UNIFORM_STEPS)))
    axis.set_major_formatter(FuncFormatter(decimal_label))
    axis.set_minor_locator(NullLocator())
    axis.set_tick_params(which="major", labelsize=fontsize)


def label_log_ticks(axis, subs=None, fontsize: float = 7.5) -> None:
    """Etiqueta los ticks menores de un eje logarítmico (`ax.xaxis` o `ax.yaxis`).

    Con `subs=None` la cantidad de etiquetas se elige según el rango que cubre el eje, que ya tiene
    que estar autoescalado (es decir: llamar a esto **después** de dibujar las series).
    """
    if subs is None:
        subs = _subs_for(axis)
    formatter = FuncFormatter(decimal_label)
    axis.set_major_formatter(formatter)
    axis.set_minor_locator(LogLocator(base=10, subs=subs, numticks=100))
    axis.set_minor_formatter(formatter)
    axis.set_tick_params(which="minor", labelsize=fontsize)


def _subs_for(axis) -> tuple[int, ...]:
    low, high = sorted(axis.get_view_interval())
    if low <= 0 or high <= 0:
        return SUBS_BY_DECADES[-1][1]
    decades = np.log10(high / low)
    return next(subs for limit, subs in SUBS_BY_DECADES if decades <= limit)


def use_data_ticks(axis, values, fontsize: float = 7.5, rotation: float = 0.0) -> None:
    """Pone un tick mayor en cada valor medido, en vez de en las potencias de 10.

    Se usa en el modo logarítmico: los valores están log-espaciados, así que quedan equiespaciados
    en el eje y cada punto de la curva tiene su etiqueta exacta debajo.
    """
    ticks = sorted(set(int(v) for v in values))
    axis.set_major_locator(FixedLocator(ticks))
    axis.set_major_formatter(FuncFormatter(decimal_label))
    axis.set_minor_locator(NullLocator())
    axis.set_tick_params(which="major", labelsize=fontsize, rotation=rotation)
