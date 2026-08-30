"""Utilidades compartidas del post-proceso del TP2 (carga de outputs + estilo de figuras).

Convenciones (ver ../../AGENTS.md §3):
- Ejes con leyenda en palabras y unidades MKS entre paréntesis (η en rad y el tiempo en s,
  que con Δt = 1 s coincide numéricamente con el número de pasos; v_a y S son
  adimensionales).
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

#: Fracción inicial de cada corrida descartada como transitorio al promediar observables:
#: se promedia la última mitad (t >= T/2). Validado sobre las evoluciones temporales
#: (plot_evolution.py): los casos más lentos (votante con η=0; densidades bajas con η
#: bajo, que por eso corren 5000 pasos en vez de 2000) ya son estacionarios en su mitad.
TRANSIENT_FRACTION = 0.5

MODELS = ("vicsek", "voter")
MODEL_LABEL = {"vicsek": "Vicsek", "voter": "Votante"}
#: Densidades del barrido como strings (= nombres de directorio `rho<valor>`), de menor a
#: mayor. Las bajas son 1/(3π), 1/(2π) y 1/π (~0.33, 0.5 y 1 vecino promedio dentro de
#: r_c); con L = 10 el motor redondea N = round(ρ·L²) = 11, 16, 32, 200, 400, 800.
RHOS = ("0.1061", "0.1592", "0.3183", "2", "4", "8")
RHO_LABEL = {"0.1061": "1/3π", "0.1592": "1/2π", "0.3183": "1/π",
             "2": "2", "4": "4", "8": "8"}
RHO_COLOR = {"0.1061": "tab:purple", "0.1592": "tab:brown", "0.3183": "tab:pink",
             "2": "tab:blue", "4": "tab:red", "8": "black"}
RHO_MARKER = {"0.1061": "v", "0.1592": "D", "0.3183": "P",
              "2": "o", "4": "s", "8": "^"}

LABEL_ETA = "Amplitud de ruido η (rad)"
LABEL_VA = "Polarización $v_a$"
LABEL_S = "Fracción del cluster más grande $S$"
#: Igual que LABEL_S pero en dos renglones, para el eje vertical: rotada a 90° la
#: version de un renglon es mas larga que el alto de la figura y matplotlib la recorta.
LABEL_S_Y = "Fracción del cluster\nmás grande $S$"
LABEL_TIME = "Tiempo (s)"


def use_style() -> None:
    """Estilo común para las figuras que terminan embebidas en diapositivas Beamer.

    El tamaño de fuente que importa es el *aparente*: el texto ya escalado dentro
    del documento. La misma figura se inserta a dos anchos distintos, así que se
    eligen figsize y fuentes para que las dos escalas den un tamaño parecido al
    del cuerpo de texto (11 pt en ambos documentos):

      informe        0.70 x 455.2 pt = 318.7 pt = 4.43 in  -> escala 4.43/5.0 = 0.89
      presentación   0.62 x 398.3 pt = 247.0 pt = 3.43 in  -> escala 3.43/5.0 = 0.69

    Con axes.labelsize = 13 eso da ~11.5 pt en el informe y ~9 pt en las
    diapositivas. El DPI no interviene: \\includegraphics escala a un ancho fijo,
    así que solo cambia la nitidez.

    Tipografía STIX (métricamente similar a Times) para que las figuras coincidan
    con el mathptmx del informe y de la presentación.
    """
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


def load_observables(run_dir: Path) -> np.ndarray:
    """`observables.csv` → array estructurado con time, polarization, largest_cluster_fraction."""
    return np.genfromtxt(run_dir / "observables.csv", delimiter=",", names=True)


def load_run_meta(run_dir: Path) -> dict:
    with open(run_dir / "run.json") as fh:
        return json.load(fh)


def stationary_mean(data: np.ndarray, column: str) -> float:
    """Promedio temporal de una columna de observables sobre la última mitad de la corrida."""
    mask = data["time"] >= TRANSIENT_FRACTION * data["time"][-1]
    return float(data[column][mask].mean())


def sweep_run_dirs(model: str, rho: str, eta: str):
    """Directorios de corridas (una por seed) del barrido para un punto (model, rho, eta)."""
    return sorted((OUTPUT / "sweep" / model / f"rho{rho}" / f"eta{eta}").glob("s*"))


def sweep_etas(model: str, rho: str) -> list[str]:
    """Valores de η disponibles en el barrido, como strings (nombres de directorio)."""
    root = OUTPUT / "sweep" / model / f"rho{rho}"
    return sorted((p.name.removeprefix("eta") for p in root.glob("eta*")), key=float)


#: Ubicaciones candidatas para la leyenda: solo esquinas y bordes (nunca el centro del
#: gráfico, que queda ilógico aunque no tape curvas).
LEGEND_LOCS = ("upper right", "upper left", "lower left", "lower right",
               "center left", "center right", "upper center", "lower center")


def legend_sidebar(ax, loc=None, **kwargs):
    """Coloca la leyenda como `loc="best"` pero restringida a bordes/esquinas.

    Elige, entre `LEGEND_LOCS`, la posición cuyo recuadro se superpone con menos puntos
    de datos; excluye el centro del gráfico. Empates → gana la primera en el orden de
    preferencia (esquinas antes que bordes). Si se pasa `loc`, se usa esa posición fija
    (override manual para casos puntuales)."""
    if loc is not None:
        return ax.legend(loc=loc, **kwargs)
    fig = ax.figure
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    curves = [(np.asarray(ln.get_xdata()), np.asarray(ln.get_ydata()))
              for ln in ax.get_lines()]
    best_loc, best_score = LEGEND_LOCS[0], None
    for loc in LEGEND_LOCS:
        leg = ax.legend(loc=loc, **kwargs)
        fig.canvas.draw()
        (dx0, dy0), (dx1, dy1) = leg.get_window_extent(renderer).get_points()
        (ax0, ay0), (ax1, ay1) = ax.transData.inverted().transform([(dx0, dy0), (dx1, dy1)])
        xlo, xhi = sorted((ax0, ax1))
        ylo, yhi = sorted((ay0, ay1))
        score = sum(int(((xd >= xlo) & (xd <= xhi) & (yd >= ylo) & (yd <= yhi)).sum())
                    for xd, yd in curves)
        if best_score is None or score < best_score:
            best_loc, best_score = loc, score
    return ax.legend(loc=best_loc, **kwargs)


def save_figure(fig, name: str) -> Path:
    FIGURES.mkdir(parents=True, exist_ok=True)
    path = FIGURES / name
    fig.savefig(path)
    plt.close(fig)
    print(f"  {path.relative_to(TP_ROOT)}")
    return path
