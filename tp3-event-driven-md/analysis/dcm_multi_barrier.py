"""Punto 1.3 para la familia bloque central (`multi_barrier`, k = 1..22 columnas).

Misma lógica que `dcm.py`: para cada k y cada realización, DCM(t) en los instantes de los bloques
de `dynamic.txt`; ajuste DCM = c·t en [0, t_fin] (mínimo de E(c), Teórica 0) con t_fin elegido
A OJO por k sobre las 20 realizaciones (`FIT_END`), donde el DCM deja de crecer linealmente;
D = c*/4 por realización y <D> ± desvío estándar entre realizaciones (ddof = 1). <t_90> ± desvío
sale de `analysis/out/t90_multi_barrier.csv`. k = 18 usa la misma ventana que en `dcm.py`, así el
punto coincide con el "bloque central" de `D_vs_t90.png`.

Salidas:
- `analysis/out/dcm_D_multi_barrier.csv`: k, t_fin, seeds, <D>, desvío, <t_90>, desvío.
- `analysis/figures/D_vs_t90_multi_barrier.png`: <D> vs <t_90>, un punto por k (color = k).
- `analysis/figures/D_vs_k_multi_barrier.png`: <D> vs k.
- `analysis/figures/dcm_multi_barrier.png`: DCM(t) de cada realización para k de `SHOWN_K`, con
  el tramo ajustado [0, t_fin] resaltado y una recta vertical en t_fin.
- Por stdout: t_fin, <D> y <t_90> de cada k.

Uso:  python3 dcm_multi_barrier.py
"""

from __future__ import annotations

import csv

import matplotlib as mpl
import numpy as np

from common import LABEL_TIME, OUT_DIR, mean_std, save_figure, use_style
from dcm import cached_dcm, fit_c, seed_dirs, t90_table

import matplotlib.pyplot as plt  # noqa: E402

FAMILY = "multi_barrier"
KS = range(1, 23)

# Fin de la ventana de ajuste [0, t_fin] (s) por k, elegido a ojo sobre las 20 realizaciones:
# cuanto más ancho el bloque, más tarda el DCM en saturar.
FIT_END = {**{k: 1.0 for k in range(1, 7)}, **{k: 1.5 for k in range(7, 14)},
           14: 2.0, 15: 2.0, 16: 3.0, 17: 3.5, 18: 4.5, 19: 4.5, 20: 5.0, 21: 6.0, 22: 7.0}

# k que se muestran en la figura de curvas DCM(t) (extremos y la mejor del 1.2).
SHOWN_K = [(1, "tab:blue"), (18, "tab:red"), (22, "black")]


def label(k: int) -> str:
    return f"k{k:02d}"


def main() -> None:
    use_style()
    t90s = t90_table()

    rows, curves = [], {}
    for k in KS:
        t_end = FIT_END[k]
        ds, runs = [], []
        for seed_dir in seed_dirs(FAMILY, label(k)):
            ts, dcm = cached_dcm(FAMILY, label(k), seed_dir)
            ds.append(fit_c(ts, dcm, t_end) / 4)
            runs.append((ts, dcm))
        curves[k] = runs
        d_mean, d_std = mean_std(ds)
        t90_mean, t90_std, *_ = t90s[(FAMILY, label(k))]
        rows.append({"k": k, "t_fit_end_s": t_end, "runs": len(ds), "D_m2_s": d_mean,
                     "D_std_m2_s": d_std, "t90_mean_s": t90_mean, "t90_std_s": t90_std})
        print(f"  k = {k:2d}  t_fin = {t_end:.1f} s   D = {d_mean:.4f} ± {d_std:.4f} m²/s "
              f"({len(ds)} seeds)   <t_90> = {t90_mean:.1f} ± {t90_std:.1f} s")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(OUT_DIR / "dcm_D_multi_barrier.csv", "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    ks = np.array([r["k"] for r in rows])
    d = np.array([r["D_m2_s"] for r in rows])
    d_err = np.array([r["D_std_m2_s"] for r in rows])
    t90 = np.array([r["t90_mean_s"] for r in rows])
    t90_err = np.array([r["t90_std_s"] for r in rows])

    # --- <D> vs <t_90>, color = k ---------------------------------------------------------------
    cmap = mpl.colormaps["viridis"]
    norm = mpl.colors.Normalize(vmin=ks.min(), vmax=ks.max())
    fig, ax = plt.subplots()
    for k, x, y, xe, ye in zip(ks, t90, d, t90_err, d_err):
        ax.errorbar(x, y, xerr=xe, yerr=ye, marker="o", color=cmap(norm(k)), linestyle="none",
                    capsize=2, elinewidth=0.8)
    cbar = fig.colorbar(mpl.cm.ScalarMappable(norm=norm, cmap=cmap), ax=ax)
    cbar.set_label("Cantidad de columnas k")
    cbar.set_ticks([1, 5, 10, 15, 20, 22])
    ax.set_xlabel("Tiempo al 90 % de goles (s)")
    ax.set_ylabel("Coeficiente de difusión (m²/s)")
    save_figure(fig, "D_vs_t90_multi_barrier.png")

    # --- <D> vs k -------------------------------------------------------------------------------
    fig, ax = plt.subplots()
    ax.errorbar(ks, d, yerr=d_err, marker="o", color="tab:blue", ecolor="tab:red",
                linestyle="--", linewidth=1.0, capsize=3)
    ax.set_xticks([1, 5, 10, 15, 20, 22])
    ax.set_xlabel("Cantidad de columnas k")
    ax.set_ylabel("Coeficiente de difusión (m²/s)")
    ax.set_ylim(0, None)
    save_figure(fig, "D_vs_k_multi_barrier.png")

    # --- DCM(t) de cada realización, tramo ajustado resaltado ------------------------------------
    fig, ax = plt.subplots()
    t_max = 1.6 * max(FIT_END[k] for k, _ in SHOWN_K)
    for k, color in SHOWN_K:
        t_end = FIT_END[k]
        for i, (ts, dcm) in enumerate(curves[k]):
            m = ts <= t_max
            ax.plot(ts[m], dcm[m], color=color, alpha=0.25, linewidth=0.6, zorder=1)
            w = ts <= t_end
            ax.plot(ts[w], dcm[w], color=color, linewidth=0.9, zorder=2,
                    label=str(k) if i == 0 else None)
        ax.axvline(t_end, color=color, linestyle="--", linewidth=1, zorder=3)
    ax.set_xlabel(LABEL_TIME)
    ax.set_ylabel("Desplazamiento cuadrático medio (m²)")
    ax.set_xlim(0, t_max)
    ax.set_ylim(0, 1.3 * max(dcm[ts <= t_max].max() for ts, dcm in curves[SHOWN_K[0][0]]))
    ax.legend(title="k", loc="upper right", ncols=3)
    save_figure(fig, "dcm_multi_barrier.png")


if __name__ == "__main__":
    main()
