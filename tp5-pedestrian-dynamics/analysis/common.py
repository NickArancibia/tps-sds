"""Estilo y utilidades de figuras del post-proceso del TP5 (mismo criterio que TP2–TP4)."""

from __future__ import annotations

import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.ticker import FixedLocator, NullLocator  # noqa: E402

TP_ROOT = Path(__file__).resolve().parent.parent
FIGURES = TP_ROOT / "analysis" / "figures"


def use_style() -> None:
    """Figuras para diapositivas Beamer: tipografía STIX, fuentes que quedan ~11 pt una vez
    escaladas en la diapositiva."""
    plt.rcParams.update({
        "font.family": "STIXGeneral",
        "mathtext.fontset": "stix",
        "font.size": 12,
        "axes.labelsize": 13,
        "legend.fontsize": 11,
        "legend.title_fontsize": 11,
        "xtick.labelsize": 11,
        "ytick.labelsize": 11,
        "figure.figsize": (5.0, 3.3),
        "figure.constrained_layout.use": True,
        "lines.markersize": 4.5,
        "lines.linewidth": 1.1,
        "savefig.dpi": 300,
    })


def decade_ticks(axis, lo_exp: int, hi_exp: int, step: int = 1) -> None:
    """Rótulos 10^e equiespaciados cada `step` décadas, sin marcas intermedias sin rótulo."""
    exps = range(lo_exp, hi_exp + 1, step)
    axis.set_major_locator(FixedLocator([10.0**e for e in exps]))
    axis.set_ticklabels([f"$10^{{{e}}}$" for e in exps])
    axis.set_minor_locator(NullLocator())


def value_ticks(axis, values) -> None:
    """Eje logarítmico rotulado en los valores medidos, tal cual, sin marcas intermedias."""
    axis.set_major_locator(FixedLocator(list(values)))
    axis.set_ticklabels([f"{v:g}" for v in values])
    axis.set_minor_locator(NullLocator())


def format_pm(mean: float, std: float) -> str:
    """valor ± error con el error a 1 cifra significativa (2 si empieza en 1) y el valor al mismo decimal."""
    if not math.isfinite(mean):
        return "sin dato"
    if not math.isfinite(std) or std <= 0:
        return f"{mean:.4g}"
    exponent = math.floor(math.log10(std))
    digits = 2 if std / 10.0**exponent < 2 else 1
    decimals = max(0, digits - 1 - exponent)
    step = 10.0 ** (exponent - digits + 1)
    return f"{round(mean / step) * step:.{decimals}f} ± {round(std / step) * step:.{decimals}f}"


def save_figure(fig, group: str, name: str) -> Path:
    """Guarda en analysis/figures/<group>/<name>."""
    path = FIGURES / group / name
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path)
    plt.close(fig)
    print(f"  → {path.relative_to(TP_ROOT)}")
    return path
