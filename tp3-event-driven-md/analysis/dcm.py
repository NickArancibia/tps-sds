"""Punto 1.3: desplazamiento cuadrático medio (DCM) y coeficiente de difusión D por configuración.

Observable: DCM(t) = (1/N) Σ_i |r_i(t) − r_i(0)|², promediado sobre TODAS las partículas (frescas
y usadas) de una realización. Se evalúa en los instantes de los bloques de `dynamic.txt` de las
corridas del 1.2 (`--every 25`: un bloque cada 25 eventos, ~0.01–0.03 s con N = 100), o sea
sin interpolar; el espaciado irregular no afecta al ajuste lineal.

Ajuste (Teórica 0): DCM = c·t desde t = 0 (la recta pasa por el origen, sin ordenada que ajustar)
hasta un t_fin elegido A OJO por configuración sobre la curva de una realización (`FIT_END`),
donde el DCM deja de crecer linealmente y empieza a saturar por confinamiento. Se minimiza
E(c) = Σ_j (DCM_j − c t_j)² con 0 ≤ t_j ≤ t_fin; el mínimo es analítico,
c* = Σ t_j DCM_j / Σ t_j²; igual se grafica E(c) alrededor de c* para mostrar cómo se halló.
En 2D, DCM = 4 D t → D = c*/4.

Realizaciones: la misma ventana [0, t_fin] de cada configuración se aplica a todas sus seeds; una
D por seed, y se reporta el promedio entre seeds ± desvío estándar (ddof = 1). <t_90> ± desvío
sale de los csv del 1.2. Las curvas completas se cachean en
`analysis/out/dcm/<barrido>__<punto>__s<seed>.csv` (t, dcm) para no volver a leer los dynamic.

Configuraciones: solo las cuatro de `SHOWN` (la mejor de cada familia del 1.2).

Entradas: `output/sweeps/<barrido>/<punto>/s<seed>/dynamic.txt` (y `output/sweeps/empty/s<seed>/`)
y `analysis/out/t90_<barrido>.csv` para el <t_90> de cada punto.

Salidas:
- `analysis/out/dcm_D.csv`: barrido, punto, variable, valor, t_fin, seeds, D, desvío, <t_90>, desvío.
- `analysis/figures/dcm_vs_t.png`: DCM(t) de una realización (seed 1) por configuración hasta
  t = 12 s, con la recta ajustada c*·t de esa realización en [0, t_fin] y una recta vertical
  punteada del color de cada curva en su t_fin.
- `analysis/figures/dcm_fit.png`: DCM(t) de la mesa vacía con la recta c*·t ajustada y su t_fin.
- `analysis/figures/dcm_E_c.png`: E(c) con su mínimo, para la mesa vacía.
- `analysis/figures/D_vs_t90.png`: <D> vs <t_90>, un símbolo por configuración, barras en ambos
  ejes (desvío estándar entre seeds).
- Por stdout: t_fin, D y <t_90> de cada configuración, para ponerlos al costado de las figuras.

Uso:  python3 dcm.py
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

import numpy as np

from animate import load_dynamic, load_static
from common import (LABEL_D, LABEL_T90, LABEL_TIME, OUT_DIR, OUTPUT, mean_std, save_figure,
                    use_style)

import matplotlib.pyplot as plt  # noqa: E402

SWEEPS = OUTPUT / "sweeps"
CACHE = OUT_DIR / "dcm"

# Configuraciones que se estudian: (barrido, punto, nombre de leyenda, símbolo, color). Qué punto
# es cada una va al costado de la figura, no en la leyenda.
SHOWN = [("empty", None, "mesa vacía", "s", "tab:red"),
         ("single_R", "R0.330", "disco central", "o", "tab:blue"),
         ("multi_barrier", "k18", "bloque central", "D", "tab:green"),
         ("multi_barrier_rows_k", "k17_n01", "bloque con filas", "v", "tab:orange")]

# Fin de la ventana de ajuste [0, t_fin] (s) por configuración, elegido a ojo sobre dcm_vs_t.png
# (seed 1): hasta donde el DCM crece linealmente antes de saturar.
FIT_END = {("empty", None): 2.0,
           ("single_R", "R0.330"): 4.0,
           ("multi_barrier", "k18"): 4.5,
           ("multi_barrier_rows_k", "k17_n01"): 2.5}


def block_dcm(run_dir: Path) -> tuple[np.ndarray, np.ndarray]:
    """(t_j, DCM(t_j)) en los instantes de los bloques de dynamic.txt, toda la corrida."""
    n, *_ = load_static(run_dir)
    times, state = load_dynamic(run_dir, n)
    pos = state[:, :, :2]
    return times, np.mean(np.sum((pos - pos[0]) ** 2, axis=2), axis=1)


def cached_dcm(family: str, label: str | None, seed_dir: Path):
    CACHE.mkdir(parents=True, exist_ok=True)
    path = CACHE / f"{family}__{label or 'empty'}__{seed_dir.name}.csv"
    if path.exists():
        data = np.loadtxt(path, delimiter=",", skiprows=1)
        return data[:, 0], data[:, 1]
    ts, dcm = block_dcm(seed_dir)
    np.savetxt(path, np.column_stack([ts, dcm]), delimiter=",", header="t_s,dcm_m2", comments="")
    return ts, dcm


def fit_c(ts, dcm, t_end: float) -> float:
    """Mínimo de E(c) = Σ (DCM_j − c t_j)² en la ventana [0, t_end]."""
    m = ts <= t_end
    return float(np.sum(ts[m] * dcm[m]) / np.sum(ts[m] ** 2))


def error_curve(ts, dcm, t_end, cs):
    m = ts <= t_end
    return np.array([np.sum((dcm[m] - c * ts[m]) ** 2) for c in cs])


def t90_table() -> dict[tuple[str, str | None], tuple[float, float, str, float]]:
    """(barrido, punto) → (<t_90>, desvío, nombre de variable, valor) desde los csv del 1.2."""
    with open(SWEEPS / "index.json") as fh:
        index = json.load(fh)
    table = {}
    for family, points in index.items():
        path = OUT_DIR / f"t90_{family}.csv"
        if not path.exists():
            continue
        with open(path, newline="") as fh:
            rows = list(csv.DictReader(fh))
        for p, r in zip(points, rows):
            table[(family, p["label"])] = (float(r["t90_mean_s"]), float(r["t90_std_s"]),
                                           p["variable"], p["value"])
    return table


def empty_t90() -> tuple[float, float]:
    values = [json.load(open(f))["t90"] for f in (SWEEPS / "empty").glob("s*/run.json")]
    return mean_std(values)


def seed_dirs(family: str, label: str | None) -> list[Path]:
    base = SWEEPS / family if label is None else SWEEPS / family / label
    return sorted(d for d in base.glob("s*") if (d / "dynamic.txt").exists())


def main() -> None:
    use_style()
    t90s = t90_table()
    t90s[("empty", None)] = (*empty_t90(), "", None)

    results = []          # filas del csv, en el orden de SHOWN
    curves = {}           # (barrido, punto) → (ts, dcm) de la seed 1, para las figuras
    for family, label, name, _marker, _color in SHOWN:
        t_end = FIT_END[(family, label)]
        ds = []
        for seed_dir in seed_dirs(family, label):
            ts, dcm = cached_dcm(family, label, seed_dir)
            ds.append(fit_c(ts, dcm, t_end) / 4)
            if seed_dir.name == "s1":
                curves[(family, label)] = (ts, dcm)
        d_mean, d_std = mean_std(ds)
        t90_mean, t90_std, var_name, value = t90s[(family, label)]
        results.append({"family": family, "label": label or "", "variable": var_name,
                        "value": json.dumps(value), "t_fit_end_s": t_end, "runs": len(ds),
                        "D_m2_s": d_mean, "D_std_m2_s": d_std,
                        "t90_mean_s": t90_mean, "t90_std_s": t90_std})
        print(f"  {name:16s} t_fin = {t_end:.1f} s   D = {d_mean:.4f} ± {d_std:.4f} m²/s "
              f"({len(ds)} seeds)   <t_90> = {t90_mean:.1f} ± {t90_std:.1f} s")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(OUT_DIR / "dcm_D.csv", "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(results[0]))
        writer.writeheader()
        writer.writerows(results)
    # --- DCM(t) de la seed 1 de cada configuración, con su recta ajustada c*·t en [0, t_fin] ----
    # Recortada en T_PLOT: después solo hay saturación, que ya se ve antes.
    T_PLOT = 12.0
    fig, ax = plt.subplots(figsize=(8.0, 3.9))
    y_max = 0.0
    for family, label, name, _marker, color in SHOWN:
        ts, dcm = curves[(family, label)]
        t_end = FIT_END[(family, label)]
        m = ts <= T_PLOT
        ax.plot(ts[m], dcm[m], color=color, label=name, linewidth=1.2, zorder=1)
        ax.axvline(t_end, color=color, linestyle=":", linewidth=1.2, zorder=2)
        t_fit = np.array([0.0, t_end])
        ax.plot(t_fit, fit_c(ts, dcm, t_end) * t_fit, color="black", linestyle="--",
                linewidth=1.4, zorder=3, label="ajuste lineal" if family == "empty" else None)
        y_max = max(y_max, dcm[m].max())
    ax.set_xlabel(LABEL_TIME)
    ax.set_ylabel("Desplazamiento cuadrático medio (m²)")
    ax.set_xlim(0, T_PLOT)
    ax.set_ylim(0, 1.05 * y_max)
    handles, names = ax.get_legend_handles_labels()
    order = [i for i, n in enumerate(names) if n != "ajuste lineal"] + [names.index("ajuste lineal")]
    ax.legend([handles[i] for i in order], [names[i] for i in order],
              loc="center right", bbox_to_anchor=(0.99, 0.55))
    save_figure(fig, "dcm_vs_t.png")

    # --- DCM(t) de la mesa vacía con la recta ajustada (par de dcm_E_c.png) ---------------------
    ts, dcm = curves[("empty", None)]
    t_end = FIT_END[("empty", None)]
    c_star = fit_c(ts, dcm, t_end)
    fig, ax = plt.subplots()
    m = ts <= 2 * t_end
    ax.plot(ts[m], dcm[m], color=SHOWN[0][4], label="DCM")
    w = ts <= t_end
    ax.plot(ts[w], c_star * ts[w], color="tab:blue", linestyle="--", label="ajuste $c^*\\,t$")
    ax.axvline(t_end, color=SHOWN[0][4], linestyle="--", linewidth=1)
    ax.set_xlabel(LABEL_TIME)
    ax.set_ylabel("Desplazamiento cuadrático medio (m²)")
    ax.set_xlim(0, None)
    ax.set_ylim(0, None)
    ax.legend(loc="upper left")
    save_figure(fig, "dcm_fit.png")

    # --- E(c) para la mesa vacía --------------------------------------------------------------
    cs = np.linspace(0.5 * c_star, 1.5 * c_star, 201)
    fig, ax = plt.subplots()
    ax.plot(cs, error_curve(ts, dcm, t_end, cs), color="tab:blue")
    ax.axvline(c_star, color="tab:red", linestyle="--", linewidth=1)
    ax.set_xlabel("Pendiente c (m²/s)")
    ax.set_ylabel("Error cuadrático E(c) (m$^4$)")
    save_figure(fig, "dcm_E_c.png")
    print(f"  mesa vacía (seed 1): c* = {c_star:.4f} m²/s → D = {c_star / 4:.4f} m²/s; "
          f"ventana [0, {t_end}] s")

    # --- <D> vs <t_90>, un punto por configuración ---------------------------------------------
    fig, ax = plt.subplots()
    for (family, label, name, marker, color), r in zip(SHOWN, results):
        ax.errorbar(r["t90_mean_s"], r["D_m2_s"], xerr=r["t90_std_s"], yerr=r["D_std_m2_s"],
                    marker=marker, color=color, linestyle="none", capsize=3, label=name)
    ax.set_xlabel(LABEL_T90)
    ax.set_ylabel(LABEL_D)
    ax.set_ylim(0, None)
    ax.legend(loc="best")
    save_figure(fig, "D_vs_t90.png")


if __name__ == "__main__":
    main()
