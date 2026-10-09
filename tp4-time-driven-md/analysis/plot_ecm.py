"""Punto 1.2: ECM(dt) de los 4 esquemas del oscilador amortiguado, en ejes log-log.

ECM(dt) = (1/K) Σ_k (r_num(t_k) − r_an(t_k))², sobre los K instantes guardados (cada 10⁻² s,
de 0 a t_f). Lee output/oscillator/sweep/ (scripts/run_oscillator_sweep.sh); escribe
analysis/figures/ej1/ecm_vs_dt.png e imprime la tabla y la pendiente log-log de cada esquema.

Segunda figura, solo para análisis (no va a la diapositiva), analysis/figures/ej1/ecm_dt4_vs_dt.png:
ECM/dt⁴ de los esquemas de orden 2 (Verlet original, Velocity Verlet, Beeman). Si ECM ≈ C dt⁴,
el cociente es la constante C de cada esquema; en eje y lineal se ven las diferencias de ~10 %
que en log-log quedan superpuestas. Solo dt ≥ 10⁻⁵: por debajo Verlet original entra en el piso
de redondeo (visible en la primera figura) y el cociente deja de medir C.

Tercera figura, también solo para análisis, analysis/figures/ej1/ecm_vs_dt_tramo.png: el mismo
log-log de la primera, restringido a dt entre 10⁻³/1.04 y 10⁻³·1.04 y a los tres esquemas de
orden 2, para ver su separación (~0.03 décadas) a escala.

Uso: python3 analysis/plot_ecm.py
"""

from __future__ import annotations

import numpy as np

from common import decade_ticks, save_figure, use_style
from oscillator_common import OUTPUT, analytic, load_run

import matplotlib.pyplot as plt  # noqa: E402  (después de common: backend Agg)
from matplotlib.ticker import FixedLocator, MaxNLocator, NullLocator  # noqa: E402

SWEEP = OUTPUT / "oscillator" / "sweep"
# (cli, leyenda, color, marcador, tamaño, relleno, zorder). Verlet, Velocity Verlet y Beeman
# quedan casi superpuestas: de atrás hacia adelante, marcadores huecos cada vez más chicos y el
# último relleno, para que se vean las tres.
SCHEMES = [
    ("verlet", "Verlet original", "tab:red", "o", 9, "none", 2),
    ("beeman", "Beeman", "black", "s", 6, "none", 3),
    ("velocity-verlet", "Velocity Verlet", "tab:blue", "o", 3, "tab:blue", 4),
    ("euler-pc", "Euler predictor-corrector", "tab:purple", "^", 5, "tab:purple", 4),
]
FIT_RANGE = (1e-4, 5e-3)  # tramo para informar la pendiente (antes del piso de redondeo)
SECOND_ORDER = ("verlet", "velocity-verlet", "beeman")
CONSTANT_MIN_DT = 1e-5  # por debajo, Verlet original está en el piso de redondeo
SECTION_DT = 1e-3  # centro del tramo ampliado (tercera figura)
SECTION_HALF_WIDTH = 1.04  # el tramo va de SECTION_DT/1.04 a SECTION_DT·1.04


def ecm_curve(scheme: str) -> tuple[np.ndarray, np.ndarray]:
    dts, ecms = [], []
    for run_dir in SWEEP.glob(f"{scheme}_dt*"):
        meta, t, r, _ = load_run(run_dir)
        dts.append(meta["dt"])
        ecms.append(np.mean((r - analytic(t, meta)) ** 2))
    order = np.argsort(dts)
    return np.array(dts)[order], np.array(ecms)[order]


def main() -> None:
    use_style()
    curves = {cli: ecm_curve(cli) for cli, *_ in SCHEMES}

    dts = curves["verlet"][0]
    print("dt (s)          " + "  ".join(f"{d:7.0e}" for d in dts))
    for cli, label, *_ in SCHEMES:
        x, y = curves[cli]
        mask = (x >= FIT_RANGE[0]) & (x <= FIT_RANGE[1])
        slope = np.polyfit(np.log10(x[mask]), np.log10(y[mask]), 1)[0]
        print(f"{label:26s} pendiente({FIT_RANGE[0]:.0e}..{FIT_RANGE[1]:.0e}) = {slope:.2f}")
        print("                " + "  ".join(f"{e:7.1e}" for e in y))

    fig, ax = plt.subplots()
    for cli, label, color, marker, size, face, z in SCHEMES:
        x, y = curves[cli]
        ax.plot(x, y, marker=marker, ms=size, color=color, mfc=face, mec=color, label=label, zorder=z)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("Paso temporal (s)")
    ax.set_ylabel("Error cuadrático medio (m²)")
    all_y = np.concatenate([c[1] for c in curves.values()])
    lo_y = int(np.floor(np.log10(all_y.min())))
    hi_y = int(np.ceil(np.log10(all_y.max())))
    step = 4
    lo_y -= (hi_y - lo_y) % step
    decade_ticks(ax.xaxis, -6, -2)
    decade_ticks(ax.yaxis, lo_y, hi_y, step)
    ax.set_xlim(6e-7, 1e-2)
    ax.set_ylim(10.0**lo_y, 10.0**hi_y)
    ax.legend(loc="best")
    save_figure(fig, "ej1", "ecm_vs_dt.png")

    print(f"C = ECM/dt⁴ (m² s⁻⁴), dt ≥ {CONSTANT_MIN_DT:.0e}: media [mín, máx] y cociente a Beeman")
    beeman_x, beeman_y = curves["beeman"]
    beeman_c = np.mean(beeman_y[beeman_x >= CONSTANT_MIN_DT] / beeman_x[beeman_x >= CONSTANT_MIN_DT] ** 4)
    fig, ax = plt.subplots()
    constants = []
    for cli, label, color, marker, _, _, z in SCHEMES:
        if cli not in SECOND_ORDER:
            continue
        x, y = curves[cli]
        mask = x >= CONSTANT_MIN_DT
        c = y[mask] / x[mask] ** 4
        constants.extend(c)
        print(f"  {label:16s} {c.mean():5.0f} [{c.min():.0f}, {c.max():.0f}]  {c.mean() / beeman_c:.3f}")
        ax.plot(x[mask], c, marker=marker, ms=6, color=color, mfc=color, mec=color, label=label, zorder=z)
    ax.set_xscale("log")
    ax.set_xlabel("Paso temporal (s)")
    ax.set_ylabel("ECM / (paso temporal)$^4$ (m$^2$ s$^{-4}$)")
    decade_ticks(ax.xaxis, -5, -2)
    ax.set_xlim(7e-6, 1e-2)
    # Franja libre debajo de las curvas para la leyenda (las curvas ocupan todo el ancho).
    span = max(constants) - min(constants)
    ax.set_ylim(min(constants) - 0.7 * span, max(constants) + 0.1 * span)
    ax.legend(loc="lower left", ncol=3, columnspacing=1.0, handlelength=1.5)
    save_figure(fig, "ej1", "ecm_dt4_vs_dt.png")
    plot_section(curves)


def plot_section(curves: dict[str, tuple[np.ndarray, np.ndarray]]) -> None:
    """Tramo de ecm_vs_dt.png alrededor de SECTION_DT, mismos ejes log-log y mismos marcadores,
    solo con los esquemas de orden 2."""
    lo_x, hi_x = SECTION_DT / SECTION_HALF_WIDTH, SECTION_DT * SECTION_HALF_WIDTH
    fig, ax = plt.subplots()
    at_center = []
    for cli, label, color, marker, size, face, z in SCHEMES:
        if cli not in SECOND_ORDER:
            continue
        x, y = curves[cli]
        ax.plot(x, y, marker=marker, ms=size, color=color, mfc=face, mec=color, label=label, zorder=z)
        at_center.extend(y[np.isclose(x, SECTION_DT)])
    # Con pendiente 4, en [lo_x, hi_x] las rectas recorren un factor SECTION_HALF_WIDTH⁴ a cada lado.
    spread = SECTION_HALF_WIDTH**4
    lo_y, hi_y = min(at_center) / spread, max(at_center) * spread
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(lo_x, hi_x)
    ax.set_ylim(lo_y, hi_y)
    sci_ticks(ax.xaxis, lo_x, hi_x)
    sci_ticks(ax.yaxis, lo_y, hi_y)
    ax.set_xlabel("Paso temporal (s)")
    ax.set_ylabel("Error cuadrático medio (m²)")
    ax.legend(loc="upper left")
    save_figure(fig, "ej1", "ecm_vs_dt_tramo.png")


def sci_ticks(axis, lo: float, hi: float) -> None:
    """Marcas redondas en [lo, hi] (tramo de menos de una década), rotuladas m × 10^e con un
    exponente común; sin marcas menores."""
    exp = int(np.floor(np.log10(np.sqrt(lo * hi))))
    scale = 10.0**exp
    mantissas = MaxNLocator(nbins=4, steps=[1, 2, 2.5, 5, 10]).tick_values(lo / scale, hi / scale)
    mantissas = mantissas[(mantissas >= lo / scale) & (mantissas <= hi / scale)]
    axis.set_major_locator(FixedLocator(mantissas * scale))
    axis.set_ticklabels([f"${m:g}\\times10^{{{exp}}}$" for m in mantissas])
    axis.set_minor_locator(NullLocator())


if __name__ == "__main__":
    main()
