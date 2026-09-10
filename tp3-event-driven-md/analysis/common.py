"""Utilidades compartidas del post-proceso del TP3 (carga de outputs + estilo de figuras).

Convenciones (ver ../../AGENTS.md §3): ejes con leyenda en palabras y unidades MKS entre
paréntesis; puntos promedio siempre con símbolo y barra de error (desvío estándar muestral
entre realizaciones); las rectas que los unen son solo guía para el ojo; sin títulos.
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

#: Raíz del TP (analysis/ está un nivel adentro).
TP_ROOT = Path(__file__).resolve().parent.parent
OUTPUT = TP_ROOT / "output"
FIGURES = TP_ROOT / "analysis" / "figures"
OUT_DIR = TP_ROOT / "analysis" / "out"

LABEL_N = "Número de partículas N"
LABEL_TIME = "Tiempo (s)"


def use_style() -> None:
    """Estilo común para figuras embebidas en diapositivas Beamer (mismo criterio que el TP2:
    tipografía STIX, fuentes que quedan ~11 pt una vez escaladas en la diapositiva)."""
    plt.rcParams.update({
        "font.family": "STIXGeneral",
        "mathtext.fontset": "stix",
        "font.size": 12,
        "axes.labelsize": 13,
        "axes.titlesize": 13,
        "legend.fontsize": 11,
        "xtick.labelsize": 11,
        "ytick.labelsize": 11,
        "figure.figsize": (5.0, 3.3),
        "figure.constrained_layout.use": True,
        "errorbar.capsize": 2.5,
        "lines.markersize": 4.5,
        "lines.linewidth": 1.1,
        "savefig.dpi": 300,
    })


def load_run_meta(run_dir: Path) -> dict:
    with open(run_dir / "run.json") as fh:
        return json.load(fh)


def load_goals(run_dir: Path) -> np.ndarray:
    """`goals.csv` → array estructurado con time, id (vacío si no hubo goles)."""
    data = np.genfromtxt(run_dir / "goals.csv", delimiter=",", names=True, ndmin=1)
    return data


def mean_std(values) -> tuple[float, float]:
    """Media y desvío estándar muestral (n-1); desvío 0 si hay una sola realización."""
    arr = np.asarray(values, dtype=float)
    return float(arr.mean()), float(arr.std(ddof=1)) if arr.size > 1 else 0.0


def save_figure(fig, name: str) -> Path:
    FIGURES.mkdir(parents=True, exist_ok=True)
    path = FIGURES / name
    fig.savefig(path)
    plt.close(fig)
    print(f"  {path.relative_to(TP_ROOT)}")
    return path
