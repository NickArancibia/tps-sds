"""Punto 2.2: t_90 en función de la posición de los obstáculos, para varias densidades (N).

Lee output/billiard/xo_sweep/N<N>/xo<x_o>/s<seed>/ (scripts/run_xo_sweep.sh): conversions.csv y
run.json (xo, finalTime = t_100 si la corrida cortó con F_u = 1, si no t_max).

Definiciones, por realización (mismas que plot_t100_vs_n.py): F_u(t) = conversiones con tiempo
≤ t dividido N; t_90 = tiempo de la conversión número ⌈0.9 N⌉. Por (N, x_o): <t_90> = promedio
entre realizaciones ± desvío estándar entre realizaciones (ddof = 1; un escalar por realización),
solo si llegan todas; si no, el punto no se grafica y se informa por stdout con F_u(t_max).

Figuras en analysis/figures/ej2/: t90_vs_xo.png (los N de --t90-ns) y fu_vs_t_xo_N<N>.png
(<F_u(t)> ± desvío entre realizaciones para los x_o de --fu-xo). La tabla por stdout incluye todos
los N del directorio.

Uso: python3 analysis/plot_xo.py [--root DIR] [--t90-ns 100,60,20] [--fu-xo 0.0175,0.25,0.4925]
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np

from common import TP_ROOT, decade_ticks, save_figure, use_style
from plot_t100_vs_n import Run

import matplotlib.pyplot as plt  # noqa: E402  (después de common: backend Agg)

DEFAULT_ROOT = TP_ROOT / "output" / "billiard" / "xo_sweep"
COLORS = {100: "tab:blue", 60: "black", 20: "tab:red", 10: "tab:purple"}
MARKERS = {100: "o", 60: "^", 20: "s", 10: "D"}


def load(root: Path) -> dict[int, dict[float, list[Run]]]:
    """→ {N: {x_o: [corridas]}}."""
    runs: dict[int, dict[float, list[Run]]] = {}
    for meta_path in sorted(root.glob("N*/xo*/s*/run.json")):
        meta = json.loads(meta_path.read_text())
        conv = np.loadtxt(meta_path.parent / "conversions.csv", delimiter=",", skiprows=1, ndmin=2)
        times = np.sort(conv[:, 0]) if conv.size else np.empty(0)
        run = Run(meta["N"], meta["seed"], times, meta["finalTime"], meta["R"])
        runs.setdefault(meta["N"], {}).setdefault(meta["xo"], []).append(run)
    return {n: dict(sorted(by_xo.items())) for n, by_xo in sorted(runs.items(), reverse=True)}


def report(runs: dict[int, dict[float, list[Run]]]) -> None:
    for n, by_xo in runs.items():
        print(f"\nN = {n}: x_o (m) | realizaciones | llegan a t90 | <t90> (s) | "
              "F_u(t_final) de las que no llegan | t_final máx (s)")
        for xo, rs in by_xo.items():
            t90 = np.array([r.t90 for r in rs])
            ok = np.isfinite(t90)
            mean = f"{t90.mean():.4g} ± {t90.std(ddof=1):.2g}" if ok.all() and t90.size > 1 else "—"
            missing = [f"{r.fu_final:.2f}" for r in rs if not math.isfinite(r.t90)]
            print(f"  {xo:.4f} | {len(rs)} | {ok.sum()} | {mean} | {', '.join(missing) or '—'} | "
                  f"{max(r.t_final for r in rs):.4g}")


def plot_t90(runs: dict[int, dict[float, list[Run]]]) -> None:
    fig, ax = plt.subplots()
    all_values = []
    minima = []  # (x_o, <t_90>, color) del mínimo de cada N
    for n, by_xo in runs.items():
        rows = []
        for xo, rs in by_xo.items():
            t90 = np.array([r.t90 for r in rs])
            if np.all(np.isfinite(t90)) and t90.size > 1:
                rows.append((xo, t90.mean(), t90.std(ddof=1)))
        if not rows:
            continue
        xo, mean, std = (np.array(c) for c in zip(*rows))
        all_values.append((mean, std))
        color = COLORS.get(n)
        ax.errorbar(xo, mean, yerr=std, fmt=MARKERS.get(n, "o") + "-", color=color, ms=6,
                    mfc="white", mew=1.5, lw=1.0, elinewidth=1.5, capsize=4, capthick=1.5, label=str(n))
        best = int(np.argmin(mean))
        minima.append((xo[best], mean[best], color))
        print(f"N = {n}: mínimo de <t90> en x_o = {xo[best]:g} m ({mean[best]:.3g} ± {std[best]:.2g} s)")
    if not all_values:
        print("ningún x_o con todas las realizaciones completas, sin figura")
        plt.close(fig)
        return
    lo = min(np.min(m - s) for m, s in all_values)
    hi = max(np.max(m + s) for m, s in all_values)
    if lo > 0 and hi / lo > 10:
        ax.set_yscale("log")
        lo_e, hi_e = int(np.floor(np.log10(lo))), int(np.ceil(np.log10(hi)))
        ax.set_ylim(10.0**lo_e, 10.0**hi_e)
        decade_ticks(ax.yaxis, lo_e, hi_e)
    else:
        ax.set_ylim(0, None)
    # x_o que minimiza <t_90> para cada N: punteada del color de la curva hasta el eje horizontal.
    bottom = ax.get_ylim()[0]
    for x, y, color in minima:
        ax.vlines(x, bottom, y, colors=color, linestyles=":", lw=1.5, zorder=1)
    ax.set_xlabel("Posición de los obstáculos (m)")
    ax.set_ylabel(r"$\langle t_{90} \rangle$ (s)")
    # Abajo a la izquierda, compacta: tiene que quedar debajo de las tapas inferiores de N = 20 en
    # r (15.0 s) y 0.05 (13.6 s) y a la izquierda de la de 0.10 (9.6 s).
    ax.legend(title="N", loc="lower left", borderaxespad=0.3, borderpad=0.3, labelspacing=0.25,
              handlelength=1.6, handletextpad=0.5)
    save_figure(fig, "ej2", "t90_vs_xo.png")


def plot_fu(runs: dict[int, dict[float, list[Run]]], xos: list[float]) -> None:
    for n, by_xo in runs.items():
        chosen = [xo for xo in by_xo if any(math.isclose(xo, x, abs_tol=1e-9) for x in xos)]
        if not chosen:
            continue
        t_end = max(r.t_final for xo in chosen for r in by_xo[xo])
        t = np.linspace(0, t_end, 2000)
        fig, ax = plt.subplots()
        for xo, color in zip(chosen, ("tab:blue", "tab:red", "black", "tab:purple")):
            rs = by_xo[xo]
            # Las que cortaron en t_100 siguen con F_u = 1; las que llegaron a t_max no se extrapolan.
            unfinished = [r.t_final for r in rs if not math.isfinite(r.t100)]
            t_x = t[t <= min(unfinished)] if unfinished else t
            fu = np.array([r.fu(t_x) for r in rs])
            mean, std = fu.mean(axis=0), fu.std(axis=0, ddof=1)
            ax.fill_between(t_x, mean - std, mean + std, color=color, alpha=0.2, lw=0)
            ax.plot(t_x, mean, color=color, label=f"{xo:g}")
        ax.set_xlim(0, t_end)
        ax.set_ylim(0, 1.02)
        ax.set_xlabel("Tiempo (s)")
        ax.set_ylabel(r"$\langle F_u \rangle$")
        ax.legend(title="$x_o$ (m)", loc="lower right")
        save_figure(fig, "ej2", f"fu_vs_t_xo_N{n}.png")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--fu-xo", default="0.0175,0.25,0.4925", help="x_o de la figura F_u(t), separados por coma")
    parser.add_argument("--t90-ns", default="100,60,20", help="N de la figura t90_vs_xo, separados por coma")
    args = parser.parse_args()
    runs = load(args.root)
    if not runs:
        raise SystemExit(f"sin corridas en {args.root}")
    use_style()
    report(runs)
    t90_ns = {int(v) for v in args.t90_ns.split(",")}
    plot_t90({n: by_xo for n, by_xo in runs.items() if n in t90_ns})
    plot_fu(runs, [float(v) for v in args.fu_xo.split(",")])


if __name__ == "__main__":
    main()
