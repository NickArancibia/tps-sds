"""Punto 1.2: ECM(dt) de los 4 esquemas del oscilador amortiguado, en ejes log-log.

ECM(dt) = (1/K) Σ_k (r_num(t_k) − r_an(t_k))², sobre los K instantes guardados (cada 10⁻² s,
de 0 a t_f). Lee output/oscillator/sweep/ (scripts/run_oscillator_sweep.sh); escribe
analysis/figures/ecm_vs_dt.png e imprime la tabla y la pendiente log-log de cada esquema.

Uso: python3 analysis/plot_ecm.py
"""

from __future__ import annotations

import numpy as np

from common import decade_ticks, save_figure, use_style
from oscillator_common import OUTPUT, analytic, load_run

import matplotlib.pyplot as plt  # noqa: E402  (después de common: backend Agg)

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
    save_figure(fig, "ecm_vs_dt.png")


if __name__ == "__main__":
    main()
