"""Punto 2.4a: t_90 y t_100 en función de la densidad, con las corridas del 2.1b extendidas.

Lee output/billiard/t100_vs_n/N<N>/s<seed>/ (scripts/run_t100_vs_n.sh): conversions.csv (tiempo
de cada conversión fresca → usada, registrado en el paso del contacto) y run.json (finalTime: t_100
si la corrida cortó con F_u = 1, si no t_max).

Definiciones, por realización: N_u(t) = conversiones con tiempo ≤ t, F_u(t) = N_u(t)/N;
t_90 = tiempo de la conversión número ⌈0.9 N⌉; t_100 = tiempo de la conversión número N. Después
de t_100 la corrida se corta y F_u queda en 1 (F_u no decrece).

Por N: <t_90> y <t_100> = promedio entre realizaciones ± desvío estándar entre realizaciones
(ddof = 1; un escalar por realización), **solo si llegan todas**. Los N con alguna realización
que no llega no se grafican: se informan por stdout con cuántas llegaron y F_u(t_max).
Densidad numérica ρ = N / (π R²).

Figuras en analysis/figures/ej2/: t90_vs_densidad.png, t100_vs_densidad.png (y las mismas vs N:
t90_vs_n.png, t100_vs_n.png), t90_t100_vs_densidad.png (las dos en un mismo eje; mínimo de cada
una por stdout) y fu_vs_t_densidad.png (F_u(t) de una realización, la semilla --fu-seed, para los
N de --fu-ns, incluidos N que no llegan a t_100 o a t_90; rectas horizontales en F_u = 0.9 y 1,
donde se leen t_90 y t_100).

Uso: python3 analysis/plot_t100_vs_n.py [--root DIR] [--fu-ns 25,300,500,625,650] [--fu-seed 1]
"""

from __future__ import annotations

import argparse
import json
import math
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from common import TP_ROOT, decade_ticks, save_figure, use_style

import matplotlib.pyplot as plt  # noqa: E402  (después de common: backend Agg)

DEFAULT_ROOT = TP_ROOT / "output" / "billiard" / "t100_vs_n"


@dataclass
class Run:
    n: int
    seed: int
    times: np.ndarray  # conversiones ordenadas (s)
    t_final: float     # t_100 si cortó, si no t_max (s)
    big_r: float

    def t_k(self, k: int) -> float:
        """Tiempo de la k-ésima conversión, nan si no ocurrió."""
        return float(self.times[k - 1]) if self.times.size >= k else math.nan

    @property
    def t90(self) -> float:
        return self.t_k(math.ceil(0.9 * self.n - 1e-9))

    @property
    def t100(self) -> float:
        return self.t_k(self.n)

    @property
    def fu_final(self) -> float:
        return self.times.size / self.n

    def fu(self, t: np.ndarray) -> np.ndarray:
        return np.searchsorted(self.times, t, side="right") / self.n


def load(root: Path) -> dict[int, list[Run]]:
    runs: dict[int, list[Run]] = {}
    for meta_path in sorted(root.glob("N*/s*/run.json")):
        meta = json.loads(meta_path.read_text())
        conv = np.loadtxt(meta_path.parent / "conversions.csv", delimiter=",", skiprows=1, ndmin=2)
        times = np.sort(conv[:, 0]) if conv.size else np.empty(0)
        t_final = meta.get("finalTime", meta["tf"])
        runs.setdefault(meta["N"], []).append(Run(meta["N"], meta["seed"], times, t_final, meta["R"]))
    return dict(sorted(runs.items()))


def summarize(runs: dict[int, list[Run]], attr: str) -> list[tuple[int, float, float, float]]:
    """→ filas (N, ρ, promedio, desvío) de los N en que todas las realizaciones llegan."""
    rows = []
    for n, rs in runs.items():
        values = np.array([getattr(r, attr) for r in rs])
        if np.all(np.isfinite(values)):
            rho = n / (math.pi * rs[0].big_r ** 2)
            rows.append((n, rho, values.mean(), values.std(ddof=1) if values.size > 1 else 0.0))
    return rows


def report(runs: dict[int, list[Run]]) -> None:
    print("N | ρ (m⁻²) | realizaciones | llegan a t90 | <t90> (s) | llegan a t100 | <t100> (s) | "
          "F_u(t_final) promedio ± desvío (las que no llegan a t100) | t_final máx (s)")
    for n, rs in runs.items():
        rho = n / (math.pi * rs[0].big_r ** 2)
        t90 = np.array([r.t90 for r in rs])
        t100 = np.array([r.t100 for r in rs])
        ok90, ok100 = np.isfinite(t90), np.isfinite(t100)

        def mean_std(v: np.ndarray, ok: np.ndarray) -> str:
            if not ok.all():
                return "—"
            return f"{v.mean():.4g} ± {v.std(ddof=1):.2g}" if v.size > 1 else f"{v[0]:.4g}"

        missing = [r.fu_final for r in rs if not math.isfinite(r.t100)]
        fu_text = (f"{np.mean(missing):.3f} ± {np.std(missing, ddof=1):.2g}" if len(missing) > 1
                   else (f"{missing[0]:.3f}" if missing else "—"))
        print(f"{n:4d} | {rho:6.1f} | {len(rs):2d} | {ok90.sum():2d} | {mean_std(t90, ok90)} | "
              f"{ok100.sum():2d} | {mean_std(t100, ok100)} | {fu_text} | {max(r.t_final for r in rs):.4g}")


def log_limits(ax, values: np.ndarray, errors: np.ndarray) -> None:
    lo = np.min(values - errors)
    lo = lo if lo > 0 else np.min(values) / 2
    lo_e = int(np.floor(np.log10(lo)))
    hi_e = int(np.ceil(np.log10(np.max(values + errors))))
    ax.set_ylim(10.0**lo_e, 10.0**hi_e)
    decade_ticks(ax.yaxis, lo_e, hi_e)


def plot_scalar(rows, attr: str, ylabel: str) -> None:
    if not rows:
        print(f"{attr}: ningún N con todas las realizaciones completas, sin figura")
        return
    n, rho, mean, std = (np.array(c) for c in zip(*rows))
    for x, xlabel, suffix in ((rho, "Densidad numérica (m$^{-2}$)", "densidad"), (n, "Número de partículas", "n")):
        fig, ax = plt.subplots()
        ax.errorbar(x, mean, yerr=std, fmt="o-", color="tab:blue", ms=6, mfc="white", mew=1.5, lw=1.0,
                    elinewidth=1.5, capsize=4, capthick=1.5)
        ax.set_yscale("log")
        log_limits(ax, mean, std)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        save_figure(fig, "ej2", f"{attr}_vs_{suffix}.png")


def plot_t90_t100(rows90, rows100) -> None:
    """<t_90> y <t_100> vs densidad en el mismo eje (log), para comparar dónde está el mínimo de cada uno."""
    fig, ax = plt.subplots()
    values, errors = [], []
    for rows, label, marker, color in ((rows90, r"$t_{90}$", "o", "tab:blue"),
                                       (rows100, r"$t_{100}$", "s", "tab:red")):
        if not rows:
            continue
        n, rho, mean, std = (np.array(c) for c in zip(*rows))
        ax.errorbar(rho, mean, yerr=std, fmt=marker + "-", color=color, ms=6, mfc="white", mew=1.5, lw=1.0,
                    elinewidth=1.5, capsize=4, capthick=1.5, label=label)
        values.append(mean)
        errors.append(std)
        k = int(np.argmin(mean))
        print(f"mínimo de <{label.strip('$').replace('_', '').replace('{', '').replace('}', '')}>: "
              f"N = {int(n[k])} (ρ = {rho[k]:.1f} m⁻²), {mean[k]:.4g} ± {std[k]:.2g} s")
    if not values:
        plt.close(fig)
        return
    ax.set_yscale("log")
    log_limits(ax, np.concatenate(values), np.concatenate(errors))
    ax.set_xlabel("Densidad numérica (m$^{-2}$)")
    ax.set_ylabel("Tiempo (s)")
    ax.legend(loc="upper left")
    save_figure(fig, "ej2", "t90_t100_vs_densidad.png")


def plot_fu(runs: dict[int, list[Run]], ns: list[int], seed: int) -> None:
    """F_u(t) de la realización `seed` para los N pedidos: evolución típica (los promedios entre
    realizaciones están en t90_t100_vs_densidad.png). Incluye N que no llegan a t_100 ni a t_90
    (la curva termina en t_max). Escalones exactos en cada conversión; una corrida que cortó en
    t_100 sigue con F_u = 1."""
    chosen = {n: run for n in ns if n in runs for run in runs[n] if run.seed == seed}
    if not chosen:
        return
    t_end = max(run.t_final for run in chosen.values())
    fig, ax = plt.subplots()
    for level in (0.9, 1.0):
        ax.axhline(level, color="black", ls=":", lw=1.2, zorder=0)
    colors = plt.cm.viridis(np.linspace(0, 0.85, len(chosen)))
    for (n, run), color in zip(chosen.items(), colors):
        end = t_end if math.isfinite(run.t100) else run.t_final
        # Arranca en 10⁻³ s con F_u = 0 (fuera del eje log, que empieza en 10⁻¹ s).
        t = np.concatenate(([1e-3], run.times, [end]))
        fu = np.concatenate(([0.0], np.arange(1, run.times.size + 1), [run.times.size])) / n
        ax.step(t, fu, where="post", color=color, lw=1.2, label=str(n))
        print(f"F_u(t), N = {n}, semilla {seed}: t_90 = {run.t90:.4g} s, t_100 = {run.t100:.4g} s, "
              f"F_u({run.t_final:g} s) = {run.fu_final:.3f}")
    hi_e = math.floor(math.log10(t_end))
    ax.set_xscale("log")
    ax.set_xlim(1e-1, t_end)
    decade_ticks(ax.xaxis, -1, hi_e)
    ax.set_ylim(0, 1.02)
    ax.set_yticks([0, 0.2, 0.4, 0.6, 0.8, 0.9, 1.0])  # 0.9 rotulado: recta de t_90
    ax.set_xlabel("Tiempo (s)")
    ax.set_ylabel(r"$F_u$")
    ax.legend(title="N", loc="center left")
    save_figure(fig, "ej2", "fu_vs_t_densidad.png")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--fu-ns", default="25,300,500,625,650", help="N de la figura F_u(t), separados por coma")
    parser.add_argument("--fu-seed", type=int, default=1, help="realización de la figura F_u(t)")
    args = parser.parse_args()
    runs = load(args.root)
    if not runs:
        raise SystemExit(f"sin corridas en {args.root}")
    use_style()
    report(runs)
    rows90, rows100 = summarize(runs, "t90"), summarize(runs, "t100")
    plot_scalar(rows90, "t90", r"$\langle t_{90} \rangle$ (s)")
    plot_scalar(rows100, "t100", r"$\langle t_{100} \rangle$ (s)")
    plot_t90_t100(rows90, rows100)
    plot_fu(runs, [int(v) for v in args.fu_ns.split(",")], args.fu_seed)


if __name__ == "__main__":
    main()
