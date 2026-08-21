"""Utilidades compartidas del post-proceso del TP2 (carga de outputs + estilo de figuras).

Convenciones (ver ../../AGENTS.md §3):
- Ejes con leyenda en palabras y unidades entre paréntesis (η y el tiempo del modelo van en
  rad y pasos respectivamente; v_a y S son adimensionales).
- Puntos promedio siempre con símbolo y barra de error; las rectas que los unen son solo
  guía para el ojo.
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
SUMMARY_CSV = TP_ROOT / "analysis" / "out" / "summary.csv"

#: Primer paso considerado estacionario para promediar observables.
#: Elegido a ojo sobre las evoluciones temporales (plot_evolution.py): el caso más lento
#: (votante con η=0) ya está estacionario antes de t = 1000 pasos.
T_STATIONARY = 1000.0

MODELS = ("vicsek", "voter")
MODEL_LABEL = {"vicsek": "Vicsek", "voter": "Votante"}
RHOS = (2, 4, 8)
RHO_COLOR = {2: "tab:blue", 4: "tab:orange", 8: "tab:green"}
RHO_MARKER = {2: "o", 4: "s", 8: "^"}

LABEL_ETA = "Amplitud de ruido η (rad)"
LABEL_VA = "Polarización v_a"
LABEL_S = "Fracción del cluster más grande S"
LABEL_TIME = "Tiempo (pasos)"


def use_style() -> None:
    """Estilo común: fuente grande (las figuras terminan en diapositivas, mínimo 20)."""
    plt.rcParams.update({
        "font.size": 16,
        "axes.labelsize": 18,
        "axes.titlesize": 18,
        "legend.fontsize": 14,
        "xtick.labelsize": 15,
        "ytick.labelsize": 15,
        "figure.figsize": (8.0, 5.0),
        "figure.constrained_layout.use": True,
        "errorbar.capsize": 3.0,
        "lines.markersize": 7.0,
        "savefig.dpi": 150,
    })


def load_observables(run_dir: Path) -> np.ndarray:
    """`observables.csv` → array estructurado con time, polarization, largest_cluster_fraction."""
    return np.genfromtxt(run_dir / "observables.csv", delimiter=",", names=True)


def load_run_meta(run_dir: Path) -> dict:
    with open(run_dir / "run.json") as fh:
        return json.load(fh)


def stationary_mean(data: np.ndarray, column: str, t_from: float = T_STATIONARY) -> float:
    """Promedio temporal de una columna de observables sobre t >= t_from."""
    mask = data["time"] >= t_from
    return float(data[column][mask].mean())


def sweep_run_dirs(model: str, rho: int, eta: str):
    """Directorios de corridas (una por seed) del barrido para un punto (model, rho, eta)."""
    return sorted((OUTPUT / "sweep" / model / f"rho{rho}" / f"eta{eta}").glob("s*"))


def sweep_etas(model: str, rho: int) -> list[str]:
    """Valores de η disponibles en el barrido, como strings (nombres de directorio)."""
    root = OUTPUT / "sweep" / model / f"rho{rho}"
    return sorted((p.name.removeprefix("eta") for p in root.glob("eta*")), key=float)


def save_figure(fig, name: str) -> Path:
    FIGURES.mkdir(parents=True, exist_ok=True)
    path = FIGURES / name
    fig.savefig(path)
    plt.close(fig)
    print(f"  {path.relative_to(TP_ROOT)}")
    return path
