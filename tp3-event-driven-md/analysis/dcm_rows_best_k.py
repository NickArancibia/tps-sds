"""Punto 1.3 para la familia bloque con filas: <D> vs <t_90> con el mejor k (menor <t_90>) de cada
cantidad de filas n. Misma figura que `dcm_multi_barrier.py` (D_vs_t90_multi_barrier.png), pero
un punto por n en lugar de uno por k. n = 0 es el bloque solo (barrido `multi_barrier`, mejor
k = 18).

Mismo ajuste que `dcm.py`: DCM = c·t en [0, t_fin] con t_fin elegido A OJO por configuración
sobre las 20 realizaciones (`FIT_END`); D = c*/4 por realización y <D> ± desvío estándar entre
realizaciones (ddof = 1). k18 y k17_n01 usan la misma ventana que en `dcm.py`.

Salidas:
- `analysis/out/dcm_D_rows_best_k.csv`: n, k, t_fin, seeds, <D>, desvío, <t_90>, desvío.
- `analysis/figures/D_vs_t90_rows_best_k.png`: <D> vs <t_90>, un punto por n (color = n).
- Por stdout: k, t_fin, <D> y <t_90> de cada n.

Uso:  python3 dcm_rows_best_k.py
"""

from __future__ import annotations

import csv

import matplotlib as mpl
import numpy as np

from common import LABEL_D, LABEL_T90, OUT_DIR, mean_std, save_figure, use_style
from dcm import cached_dcm, fit_c, seed_dirs, t90_table

import matplotlib.pyplot as plt  # noqa: E402

# n → (barrido, punto, t_fin (s)); el punto es el de menor <t_90> para ese n
# (analysis/out/t90_multi_barrier_rows_k.csv y t90_multi_barrier.csv).
BEST = {0: ("multi_barrier", "k18", 4.5),
        1: ("multi_barrier_rows_k", "k17_n01", 2.5),
        2: ("multi_barrier_rows_k", "k15_n02", 2.5),
        3: ("multi_barrier_rows_k", "k14_n03", 2.0),
        4: ("multi_barrier_rows_k", "k14_n04", 2.0)}


def main() -> None:
    use_style()
    t90s = t90_table()

    rows = []
    for n, (family, label, t_end) in BEST.items():
        ds = [fit_c(*cached_dcm(family, label, d), t_end) / 4 for d in seed_dirs(family, label)]
        d_mean, d_std = mean_std(ds)
        t90_mean, t90_std, *_ = t90s[(family, label)]
        k = int(label[1:3])
        rows.append({"n": n, "k": k, "t_fit_end_s": t_end, "runs": len(ds), "D_m2_s": d_mean,
                     "D_std_m2_s": d_std, "t90_mean_s": t90_mean, "t90_std_s": t90_std})
        print(f"  n = {n}  k = {k}  t_fin = {t_end:.1f} s   D = {d_mean:.4f} ± {d_std:.4f} m²/s "
              f"({len(ds)} seeds)   <t_90> = {t90_mean:.1f} ± {t90_std:.1f} s")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(OUT_DIR / "dcm_D_rows_best_k.csv", "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    ns = np.array([r["n"] for r in rows])
    cmap = mpl.colormaps["viridis"]
    norm = mpl.colors.Normalize(vmin=ns.min(), vmax=ns.max())
    fig, ax = plt.subplots()
    for r in rows:
        ax.errorbar(r["t90_mean_s"], r["D_m2_s"], xerr=r["t90_std_s"], yerr=r["D_std_m2_s"],
                    marker="o", color=cmap(norm(r["n"])), linestyle="none", capsize=2,
                    elinewidth=0.8)
    cbar = fig.colorbar(mpl.cm.ScalarMappable(norm=norm, cmap=cmap), ax=ax)
    cbar.set_label("Cantidad de filas por lado n")
    cbar.set_ticks(ns)
    ax.set_xlabel(LABEL_T90)
    ax.set_ylabel(LABEL_D)
    ax.set_ylim(0, None)
    save_figure(fig, "D_vs_t90_rows_best_k.png")


if __name__ == "__main__":
    main()
