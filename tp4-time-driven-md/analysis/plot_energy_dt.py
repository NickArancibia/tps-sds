"""Punto 2.1a: conservación de la energía en el billar sin obstáculos (N = 300, t_f = 10 s) en
función del paso de integración, para elegir dt.

Lee output/billiard/energy_dt/<esquema>_dt<dt>_s<seed>/ (scripts/run_energy_sweep.sh). La energía
total de cada estado guardado es E(t) = Σ ½ m |v|² + Σ_contactos ½ k ξ². El sistema es
conservativo (resortes sin disipación): la exacta es constante, así que todo cambio de E es error
de integración. Error relativo de la energía: ΔE(t) = (E(t) − E(0)) / E(0).

Observable escalar, uno por realización: error medio ε = (1/K) Σ_k |ΔE(t_k)|, sobre los K
estados guardados con t_k > 0. Por cada dt: promedio de ε entre semillas ± desvío estándar entre
semillas (ddof = 1). Un dt "explota" si alguna semilla da E no finita (no tiene ε).

Figuras en analysis/figures/ej2/:

  energia_vs_t.png            E(t) para E_VS_T_DTS (una semilla, Velocity Verlet); la curva que
                              diverge sale por arriba del eje
  energia_error_medio_dt.png  ε vs dt (Velocity Verlet), log-log
  energia_esquemas_dt.png     ε vs dt, Verlet original y Velocity Verlet (decisión de variante)
  energia_costo_dt.png        tiempo del lazo vs dt (corridas en paralelo: no es benchmark)

Uso: python3 analysis/plot_energy_dt.py
"""

from __future__ import annotations

import json
import re
from collections import defaultdict

import numpy as np

from billiard_common import load_run, total_energy
from common import TP_ROOT, decade_ticks, save_figure, use_style

import matplotlib.pyplot as plt  # noqa: E402  (después de common: backend Agg)

SWEEP = TP_ROOT / "output" / "billiard" / "energy_dt"
CACHE = SWEEP / "energy_cache.npz"
NAME = re.compile(r"(?P<scheme>[a-z-]+)_dt(?P<dt>[0-9.e-]+)_s(?P<seed>\d+)$")
SCHEME_LABEL = {"verlet": "Verlet original", "velocity-verlet": "Velocity Verlet"}
MAIN_SCHEME = "velocity-verlet"
EXAMPLE_SEED = 1
# dt de E(t) y su color; zorder creciente con dt: las casi planas (dt chicos) quedan detrás.
E_VS_T = ((5e-4, "tab:red"), (1e-4, "tab:purple"), (5e-5, "tab:blue"), (1e-5, "black"))
DIVERGED = 1.0  # ε >= 1 (o E no finita): la integración diverge; fuera de las figuras de ε
CHOSEN_DT = 1e-5  # dt elegido (2026-10-08): mayor dt redondo con ε < 10⁻⁴; recta vertical


def load_energies() -> dict[tuple[str, float, int], tuple[np.ndarray, np.ndarray, float]]:
    """(esquema, dt, seed) → (t, E, tiempo del lazo en s). Cachea E(t) en energy_cache.npz."""
    runs = sorted(p for p in SWEEP.iterdir() if p.is_dir() and NAME.match(p.name))
    cache = dict(np.load(CACHE)) if CACHE.exists() else {}
    out = {}
    dirty = False
    for path in runs:
        m = NAME.match(path.name)
        key = (m["scheme"], float(m["dt"]), int(m["seed"]))
        meta = json.loads((path / "run.json").read_text())
        if path.name + "/E" not in cache:
            run = load_run(path)
            cache[path.name + "/t"] = run.t
            cache[path.name + "/E"] = total_energy(run)
            dirty = True
        out[key] = (cache[path.name + "/t"], cache[path.name + "/E"], meta["loopTimeMs"] / 1e3)
    if dirty:
        np.savez(CACHE, **cache)
    return out


def mean_error(t: np.ndarray, e: np.ndarray) -> float:
    """ε = (1/K) Σ_{t_k > 0} |ΔE(t_k)|; inf si la integración dio E no finita."""
    rel = np.abs(e / e[0] - 1)[t > 0]
    return float(rel.mean()) if np.all(np.isfinite(rel)) else np.inf


def mean_std(values: np.ndarray) -> tuple[float, float]:
    return float(values.mean()), float(values.std(ddof=1)) if values.size > 1 else 0.0


def main() -> None:
    use_style()
    data = load_energies()
    schemes = sorted({k[0] for k in data})
    dts = sorted({k[1] for k in data})

    # stats[esquema] = filas (dt, promedio de ε, desvío de ε, semillas); cost[esquema] ídem con el lazo.
    stats: dict[str, list] = defaultdict(list)
    cost: dict[str, list] = defaultdict(list)
    for scheme in schemes:
        for dt in dts:
            seeds = sorted(k[2] for k in data if k[0] == scheme and k[1] == dt)
            eps = np.array([mean_error(*data[(scheme, dt, s)][:2]) for s in seeds])
            cost[scheme].append((dt, *mean_std(np.array([data[(scheme, dt, s)][2] for s in seeds]))))
            if np.all(np.isfinite(eps)) and eps.mean() < DIVERGED:
                stats[scheme].append((dt, *mean_std(eps), len(seeds)))
            else:
                print(f"diverge: {scheme} dt = {dt:.0e} s, ε = {eps.mean():.2g} "
                      f"(E no finita en {np.sum(~np.isfinite(eps))}/{len(seeds)} semillas); fuera de la figura")

    for scheme in schemes:
        print(f"\n{SCHEME_LABEL[scheme]}: dt (s) | ε promedio ± desvío | semillas | lazo (s)")
        lazo = {row[0]: row[1] for row in cost[scheme]}
        for dt, mean, std, n in stats[scheme]:
            print(f"  {dt:.0e} | {mean:.2e} ± {std:.1e} | {n} | {lazo[dt]:.1f}")
        dt_s, mean_s = np.array(stats[scheme])[:, :2].T
        print(f"  pendiente log-log de ε ({dt_s.min():.0e}–{dt_s.max():.0e} s): "
              f"{np.polyfit(np.log10(dt_s), np.log10(mean_s), 1)[0]:.2f}")

    plot_energy_vs_t(data)
    plot_error_vs_dt(stats, [MAIN_SCHEME], "energia_error_medio_dt.png")
    plot_error_vs_dt(stats, schemes, "energia_esquemas_dt.png")
    plot_cost(cost[MAIN_SCHEME])


def plot_energy_vs_t(data) -> None:
    """E(t) de una semilla para los dt de E_VS_T."""
    fig, ax = plt.subplots()
    for z, (dt, color) in enumerate(sorted(E_VS_T)):
        t, e, _ = data[(MAIN_SCHEME, dt, EXAMPLE_SEED)]
        ax.plot(t, e, "-", color=color, label=dt_label(dt), zorder=2 + z)
    handles, labels = ax.get_legend_handles_labels()
    ax.set_xlabel("Tiempo (s)")
    ax.set_ylabel("Energía total (J)")
    ax.legend(handles[::-1], labels[::-1], title="dt (s)", loc="upper left")
    save_figure(fig, "ej2", "energia_vs_t.png")


def plot_error_vs_dt(stats, schemes, name: str) -> None:
    """ε vs dt: marcadores huecos y barras en el mismo color, por encima de la línea guía."""
    fig, ax = plt.subplots()
    styles = {"velocity-verlet": ("o", "tab:blue", 7), "verlet": ("s", "tab:red", 5)}
    for scheme in schemes:
        marker, color, size = styles[scheme]
        dt, mean, std, _ = np.array(stats[scheme]).T
        ax.errorbar(dt, mean, yerr=std, fmt=marker + "-", color=color, ms=size, mfc="white", mew=1.5,
                    lw=1.0, elinewidth=1.5, capsize=4, capthick=1.5,
                    label=SCHEME_LABEL[scheme] if len(schemes) > 1 else None)
    log_axes(ax)
    if len(schemes) == 1:
        ax.axvline(CHOSEN_DT, color="0.4", ls="--", lw=1.2, zorder=0)
    ax.set_xlabel("Paso de integración (s)")
    ax.set_ylabel("Error medio de la energía")
    if len(schemes) > 1:
        ax.legend(loc="upper left")
    save_figure(fig, "ej2", name)


def plot_cost(cost) -> None:
    fig, ax = plt.subplots()
    dt, mean, std = np.array(cost).T
    ax.errorbar(dt, mean, yerr=std, fmt="o-", color="black", capsize=3)
    log_axes(ax)
    ax.set_xlabel("Paso de integración (s)")
    ax.set_ylabel("Tiempo de ejecución (s)")
    save_figure(fig, "ej2", "energia_costo_dt.png")


def log_axes(ax) -> None:
    """Ejes log ajustados a los datos (la autoescala de matplotlib) con rótulos 10^e equiespaciados
    en las décadas que caen adentro: cada década, o cada 2 (exponentes pares) si son más de 6."""
    ax.set_xscale("log")
    ax.set_yscale("log")
    for axis, (lo, hi) in ((ax.xaxis, ax.get_xlim()), (ax.yaxis, ax.get_ylim())):
        lo_e, hi_e = int(np.ceil(np.log10(lo))), int(np.floor(np.log10(hi)))
        step = 1 if hi_e - lo_e <= 6 else 2
        decade_ticks(axis, lo_e + (lo_e % step), hi_e, step=step)
    ax.set_xlim(ax.get_xlim())
    ax.set_ylim(ax.get_ylim())


def dt_label(dt: float) -> str:
    mant, exp = f"{dt:.0e}".split("e")
    exp = int(exp)
    return f"$10^{{{exp}}}$" if mant == "1" else f"${mant}\\times10^{{{exp}}}$"


if __name__ == "__main__":
    main()
