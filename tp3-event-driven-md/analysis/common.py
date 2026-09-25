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
LABEL_T90 = r"$\langle t_{90} \rangle$ (s)"
LABEL_D = r"$\langle D \rangle$ (m²/s)"


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


def mark_on_axis(ax, axis: str, marks: list[tuple[float, str, object]], min_gap: float = 0.08):
    """Agrega cada (valor, texto, color) de `marks` como tick del eje `axis` ("x" o "y"), con su
    texto en su color; saca los ticks automáticos a menos de `min_gap` (fracción del rango
    visible) de alguna marca para que no se pisen. Congela los límites actuales: llamarla una
    sola vez por eje, después de dibujar todo. Devuelve los textos de las marcas, en orden."""
    ax_obj, get_lim, set_lim, set_ticks, get_labels = (
        (ax.xaxis, ax.get_xlim, ax.set_xlim, ax.set_xticks, ax.get_xticklabels) if axis == "x"
        else (ax.yaxis, ax.get_ylim, ax.set_ylim, ax.set_yticks, ax.get_yticklabels))
    lo, hi = get_lim()
    ticks = [t for t in ax_obj.get_majorticklocs() if lo <= t <= hi]
    texts = ax_obj.get_major_formatter().format_ticks(ticks)
    keep = sorted([(t, s) for t, s in zip(ticks, texts)
                   if all(abs(t - v) > min_gap * (hi - lo) for v, _, _ in marks)]
                  + [(v, s) for v, s, _ in marks])
    set_ticks([t for t, _ in keep], [s for _, s in keep])
    set_lim(lo, hi)
    labels, locs = get_labels(), [t for t, _ in keep]
    out = []
    for v, _, color in marks:
        text = labels[locs.index(v)]
        text.set_color(color)
        out.append(text)
    return out


def mark_point_x(ax, x: float, y: float, label: str) -> None:
    """Mejor punto: recta punteada negra desde (x, y) hasta el eje horizontal (por encima de la
    barra de error), con x como tick en negrita."""
    lo, hi = ax.get_ylim()
    ax.plot([x, x], [lo, y], color="black", linestyle=":", linewidth=1.3, zorder=4)
    ax.set_ylim(lo, hi)
    mark_on_axis(ax, "x", [(x, label, "black")])[0].set_fontweight("bold")


def log_ticks(lo: float, hi: float) -> list[float]:
    """Potencias de 10 que cubren [lo, hi] (rótulos equiespaciados, sin marcas intermedias)."""
    return [10.0 ** k for k in range(int(np.floor(np.log10(lo))), int(np.ceil(np.log10(hi))) + 1)]


def save_figure(fig, name: str) -> Path:
    FIGURES.mkdir(parents=True, exist_ok=True)
    path = FIGURES / name
    fig.savefig(path)
    plt.close(fig)
    print(f"  {path.relative_to(TP_ROOT)}")
    return path
