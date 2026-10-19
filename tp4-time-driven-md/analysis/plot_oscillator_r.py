"""Sistema 1: evolución r(t) del oscilador amortiguado con los 4 esquemas y la solución analítica,
para un dt del barrido (por defecto el mayor, 5·10⁻³ s, donde Euler predictor-corrector se separa
de la analítica y los tres de orden 2 todavía quedan encima).

Lee output/oscillator/sweep/<esquema>_dt<dt>/ (scripts/run_oscillator_sweep.sh); escribe
analysis/figures/ej1/r_vs_t.png e imprime el máximo de |r_num − r_an| de cada esquema.

Uso: python3 analysis/plot_oscillator_r.py [--dt 5e-3]
"""

from __future__ import annotations

import argparse

import numpy as np

from common import save_figure, use_style
from oscillator_common import OUTPUT, analytic, load_run
from plot_ecm import SCHEMES

import matplotlib.pyplot as plt  # noqa: E402  (después de common: backend Agg)

SWEEP = OUTPUT / "oscillator" / "sweep"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--dt", default="5e-3", help="paso temporal, como en el nombre del directorio")
    args = parser.parse_args()

    use_style()
    fig, ax = plt.subplots()
    meta, t, _, _ = load_run(SWEEP / f"beeman_dt{args.dt}")
    tt = np.linspace(0, t[-1], 2000)
    ax.plot(tt, analytic(tt, meta), color="0.6", lw=4, label="analítica", zorder=1)
    # Solo líneas (sin marcadores): los tres de orden 2 quedan superpuestos con la analítica, que
    # es lo que se quiere mostrar; Euler predictor-corrector se separa.
    for cli, label, color, *_, z in SCHEMES:
        meta, t, r, _ = load_run(SWEEP / f"{cli}_dt{args.dt}")
        print(f"{label:26s} máx |r_num − r_an| = {np.max(np.abs(r - analytic(t, meta))):.2e} m")
        ax.plot(t, r, color=color, lw=1.2, label=label, zorder=z)
    ax.set_xlim(0, t[-1])
    ax.set_ylim(-1.3, 1.05)  # franja libre abajo a la derecha para la leyenda (amplitud < 0.25 m desde t = 2 s)
    ax.set_xlabel("Tiempo (s)")
    ax.set_ylabel("Posición (m)")
    ax.legend(loc="lower right")
    save_figure(fig, "ej1", "r_vs_t.png")


if __name__ == "__main__":
    main()
