"""Lectura y agregación de los CSV que produce `BenchmarkRunner`.

El CSV trae **una fila por repetición individual**, no promedios: acá se agrupan esas filas y se
calculan media y desvío. Así se puede recalcular cualquier estadístico sin volver a correr las
simulaciones, que es el principio con el que trabaja todo `analysis/`.

Formato esperado:

    experiment,N,L,M,rc,pbc,seed,repetition,time_ns,neighbor_pairs
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

import numpy as np

#: Nombre legible de cada experimento, para títulos y leyendas.
EXPERIMENT_LABELS = {
    "M": "barrido de M",
    "N_free": "densidad libre",
    "N_fixed_density": "densidad fija",
}

_FIELD_TYPES = {
    "N": int,
    "L": float,
    "M": int,
    "rc": float,
    "seed": int,
    "repetition": int,
    "time_ns": int,
    "neighbor_pairs": int,
}


@dataclass
class Curve:
    """Una serie lista para graficar: x, tiempo medio y desvío estándar (en ms)."""

    x: np.ndarray
    mean_ms: np.ndarray
    std_ms: np.ndarray
    #: Cantidad de mediciones promediadas en cada punto.
    samples: np.ndarray
    #: Valores constantes dentro de la curva (N, L, M, pbc, ...), para armar la leyenda.
    context: dict


def read_csv(path: str | Path) -> list[dict]:
    """Lee un CSV de benchmark convirtiendo cada columna a su tipo."""
    file = Path(path)
    if not file.is_file():
        raise SystemExit(f"No existe el CSV de benchmark: {file}")

    rows: list[dict] = []
    with file.open(encoding="utf-8", newline="") as handle:
        for raw in csv.DictReader(handle):
            row = {key: _FIELD_TYPES.get(key, str)(value) for key, value in raw.items()}
            row["pbc"] = row["pbc"] == "true"
            rows.append(row)
    if not rows:
        raise SystemExit(f"El CSV de benchmark está vacío: {file}")
    return rows


def read_all(paths: list[str] | list[Path]) -> list[dict]:
    """Concatena varios CSV (p. ej. densidad libre + densidad fija) en una sola lista."""
    rows: list[dict] = []
    for path in paths:
        rows.extend(read_csv(path))
    return rows


def curves(rows: list[dict], x_field: str, group_by: tuple[str, ...] = ()) -> dict[tuple, Curve]:
    """Agrupa las repeticiones y devuelve una curva por combinación de `group_by`.

    Para cada valor de `x_field` se promedian **todas** las repeticiones de ese punto (incluyendo
    las de distintas semillas, si el barrido usó varias) y el desvío estándar muestral es la barra
    de error.
    """
    grouped: dict[tuple, dict[float, list[int]]] = {}
    for row in rows:
        key = tuple(row[field] for field in group_by)
        grouped.setdefault(key, {}).setdefault(row[x_field], []).append(row["time_ns"])

    result: dict[tuple, Curve] = {}
    for key, points in sorted(grouped.items(), key=lambda item: item[0]):
        xs = np.array(sorted(points))
        times = [np.array(points[x], dtype=float) / 1e6 for x in xs]
        result[key] = Curve(
            x=xs,
            mean_ms=np.array([t.mean() for t in times]),
            # ddof=1: desvío muestral, el mismo criterio que usa el motor Java.
            std_ms=np.array([t.std(ddof=1) if t.size > 1 else 0.0 for t in times]),
            samples=np.array([t.size for t in times]),
            context=_constant_fields([r for r in rows if tuple(r[f] for f in group_by) == key]),
        )
    return result


def _constant_fields(rows: list[dict]) -> dict:
    """Campos que valen lo mismo en todas las filas del grupo: sirven para la leyenda y el título."""
    return {field: rows[0][field] for field in _FIELD_TYPES
            if field not in ("repetition", "time_ns") and len({r[field] for r in rows}) == 1}


def describe(curve: Curve, x_label: str) -> str:
    """Tabla de texto de la curva, para dejar los números junto al gráfico."""
    lines = [f"{x_label:>8}  {'media [ms]':>12}  {'desvío [ms]':>12}  {'muestras':>9}"]
    for x, mean, std, samples in zip(curve.x, curve.mean_ms, curve.std_ms, curve.samples):
        lines.append(f"{x:>8}  {mean:>12.5f}  {std:>12.5f}  {samples:>9}")
    return "\n".join(lines)
