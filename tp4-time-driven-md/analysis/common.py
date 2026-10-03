"""Estilo y utilidades de figuras del post-proceso del TP4 (mismo criterio que TP2/TP3)."""

from __future__ import annotations

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


def save_figure(fig, name: str) -> Path:
    FIGURES.mkdir(parents=True, exist_ok=True)
    path = FIGURES / name
    fig.savefig(path)
    plt.close(fig)
    print(f"  {path.relative_to(TP_ROOT)}")
    return path
