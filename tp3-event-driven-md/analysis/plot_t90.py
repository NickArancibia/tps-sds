"""Punto 1.2: <t_90> ± desvío en función de la variable de cada barrido, comparado con la mesa
vacía. Lee `output/sweeps/index.json` (analysis/gen_configs.py) y los `run.json` de cada
realización (scripts/run_sweeps.sh).

Observable: t_90 = primer instante en que N_g(t)/N ≥ 0.9. Se promedia entre realizaciones
(seeds distintas); la barra de error es el desvío estándar muestral. Si en alguna realización no
se alcanza 0.9 antes de t_f, `t90` es null en run.json: esa realización se cuenta aparte
(columna `no_alcanzado`) y NO entra en el promedio. Si el motor no pudo ubicar las N partículas
(config demasiado llena) no hay run.json: columna `no_generado`.

Barridos de una variable: una curva. Barridos en grilla (`value` = [k, n], hoy solo
`multi_barrier_rows_k`): x = n, una curva por k con el símbolo k como título de leyenda; el csv
lleva columnas k, n.

Salidas:
- `analysis/out/t90_<barrido>.csv`: variable, realizaciones, <t_90>, desvío, no alcanzados.
- `analysis/figures/t90_<barrido>.png`: <t_90> vs variable; mesa vacía como recta horizontal
  (<t_90>) con banda sombreada de ± 1 desvío entre realizaciones;
  el mejor punto (menor <t_90>) se marca con una recta vertical hasta el eje horizontal, con su
  valor como tick.
  Su <t_90> ± desvío y el punto elegido para `fg_vs_t.png` se imprimen por stdout: van al costado
  de la figura (presentación) o en el caption (informe), nunca en la leyenda.
- `analysis/figures/t90_best.png`: barras con el mejor punto (menor <t_90>) de cada familia más
  la mesa vacía; qué punto es cada barra se imprime por stdout (va al costado de la figura).

Uso:  python3 plot_t90.py [--grid-k 14,15,16,17] [--fg-config multi_barrier/k16]
      python3 plot_t90.py --from-csv single_R multi_barrier
      (--grid-k: qué curvas k dibujar en los barridos en grilla; el csv lleva todas.
       --fg-config: configuración de la curva 'con obstáculos' de fg_vs_t.png; default la de
       menor <t_90>.
       --from-csv: solo rehace t90_<barrido>.png de barridos de una variable desde
       `analysis/out/t90_<barrido>.csv`, con la mesa vacía de `analysis/out/dcm_D.csv` (las mismas
       20 realizaciones), sin leer output/sweeps: sirve en una máquina sin los barridos, cuyas
       corridas darían otros t_90 por seed. No toca csv ni t90_best.png.)
"""

from __future__ import annotations

import argparse
import csv
import json

import numpy as np

from common import (LABEL_T90, LABEL_TIME, OUT_DIR, OUTPUT, load_goals, load_run_meta,
                    mark_point_x, mean_std, save_figure, use_style)

import matplotlib.pyplot as plt  # noqa: E402

SWEEPS = OUTPUT / "sweeps"
EMPTY_COLOR, DATA_COLOR = "tab:red", "tab:blue"


# Nombre corto de cada familia (eje de t90_best.png) y su color, el mismo que usa dcm.py.
FAMILY_NAMES = {"single_R": "disco central", "multi_barrier": "bloque central",
                "multi_barrier_rows_k": "bloque con filas"}
FAMILY_COLORS = {"mesa vacía": "tab:red", "disco central": "tab:blue",
                 "bloque central": "tab:green", "bloque con filas": "tab:orange"}


def t90_stats(run_dir):
    """(<t_90>, desvío, alcanzados, no alcanzados, no generados) sobre los s*/ de run_dir."""
    values, missing, failed = [], 0, 0
    for seed_dir in sorted(run_dir.glob("s*")):
        if not (seed_dir / "run.json").exists():
            failed += 1
            continue
        t90 = load_run_meta(seed_dir)["t90"]
        if t90 is None:
            missing += 1
        else:
            values.append(t90)
    mean, std = mean_std(values) if values else (float("nan"), float("nan"))
    return mean, std, len(values), missing, failed


def write_csv(name: str, rows: list[dict]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUT_DIR / f"t90_{name}.csv"
    with open(path, "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def plot_fg(run_dirs: list[tuple[str, object]], name: str) -> None:
    fig, ax = plt.subplots()
    for (label, run_dir), color in zip(run_dirs, (EMPTY_COLOR, DATA_COLOR)):
        meta = load_run_meta(run_dir)
        goals = load_goals(run_dir)
        n = meta["N"]
        t = np.concatenate(([0.0], goals["time"], [meta["finalTime"]]))
        fg = np.concatenate(([0.0], np.arange(1, len(goals) + 1) / n, [len(goals) / n]))
        ax.step(t, fg, where="post", color=color, label=label)
        if meta["t90"] is not None:
            ax.axvline(meta["t90"], color=color, linestyle=":", linewidth=1)
    ax.axhline(0.9, color="0.4", linestyle="--", linewidth=0.8)
    ax.set_xlabel(LABEL_TIME)
    ax.set_ylabel("Fracción de goles")
    ax.set_ylim(0, 1)
    if len(run_dirs) > 1:
        ax.legend(loc="lower right")
    save_figure(fig, name)


def plot_curve(ax, xs, rows, **kw):
    ax.errorbar(xs, [r["t90_mean_s"] for r in rows], yerr=[r["t90_std_s"] for r in rows],
                marker="o", linestyle="--", linewidth=1.0, **kw)


def empty_band(ax, empty_mean: float, empty_std: float) -> None:
    """Mesa vacía: <t_90> (recta) ± desvío entre realizaciones (banda, por detrás de todo)."""
    ax.axhspan(empty_mean - empty_std, empty_mean + empty_std, color=EMPTY_COLOR,
               alpha=0.12, linewidth=0, zorder=0)
    ax.axhline(empty_mean, color=EMPTY_COLOR, linestyle="--", linewidth=1, label="mesa vacía")


def draw_single(ax, name: str, rows: list[dict], variable: str) -> None:
    """Barrido de una variable: una curva en el color de la familia (el mismo de t90_best.png,
    D_vs_t90.png y fg_*.png) y el mejor punto marcado."""
    done = [r for r in rows if r["runs"]]
    plot_curve(ax, [r["value"] for r in done], done,
               color=FAMILY_COLORS.get(FAMILY_NAMES.get(name), DATA_COLOR),
               label="con obstáculos")
    ax.set_xlabel(variable)
    ax.legend(loc="best")
    top_row = min(done, key=lambda r: r["t90_mean_s"])
    mark_point_x(ax, top_row["value"], top_row["t90_mean_s"], f"{top_row['value']:g}")


def plot_from_csv(names: list[str], index: dict) -> None:
    with open(OUT_DIR / "dcm_D.csv") as fh:
        empty = next(r for r in csv.DictReader(fh) if r["family"] == "empty")
    empty_mean, empty_std = float(empty["t90_mean_s"]), float(empty["t90_std_s"])
    print(f"  mesa vacía (dcm_D.csv): <t_90> = {empty_mean:.2f} ± {empty_std:.2f} s "
          f"({empty['runs']} realizaciones)")
    for name in names:
        if isinstance(index[name][0]["value"], list):
            raise SystemExit(f"{name}: --from-csv solo para barridos de una variable")
        with open(OUT_DIR / f"t90_{name}.csv") as fh:
            rows = [{"value": float(r["value"]), "runs": int(r["runs"]),
                     "t90_mean_s": float(r["t90_mean_s"]), "t90_std_s": float(r["t90_std_s"])}
                    for r in csv.DictReader(fh)]
        fig, ax = plt.subplots()
        empty_band(ax, empty_mean, empty_std)
        draw_single(ax, name, rows, index[name][0]["variable"])
        ax.set_ylabel(LABEL_T90)
        save_figure(fig, f"t90_{name}.png")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--grid-k", type=lambda s: {int(v) for v in s.split(",")}, default=None)
    ap.add_argument("--fg-config", default=None,
                    help="<barrido>/<punto> para la curva 'con obstáculos' de fg_vs_t.png "
                         "(default: el de menor <t_90>)")
    ap.add_argument("--from-csv", nargs="+", default=None, metavar="BARRIDO",
                    help="rehacer t90_<barrido>.png desde analysis/out (sin output/sweeps)")
    args = ap.parse_args()
    with open(SWEEPS / "index.json") as fh:
        index = json.load(fh)
    use_style()
    if args.from_csv:
        plot_from_csv(args.from_csv, index)
        return

    empty_mean, empty_std, empty_n, empty_missing, _ = t90_stats(SWEEPS / "empty")
    print(f"  mesa vacía: <t_90> = {empty_mean:.2f} ± {empty_std:.2f} s "
          f"({empty_n} realizaciones, {empty_missing} no alcanzaron 0.9)")

    best = (empty_mean, "mesa vacía", SWEEPS / "empty")
    # Mejor punto de cada familia: (nombre para el eje, <t_90>, desvío, punto) para t90_best.png.
    best_by_family = [("mesa vacía", empty_mean, empty_std, "")]
    for name, points in index.items():
        grid = isinstance(points[0]["value"], list)
        if not any(next((SWEEPS / name / p["label"]).glob("s*"), None) for p in points):
            print(f"  {name}: sin corridas en output/sweeps, se saltea (csv y figura previos quedan)")
            continue
        rows = []
        for p in points:
            run_dir = SWEEPS / name / p["label"]
            mean, std, n, missing, failed = t90_stats(run_dir)
            key = dict(zip(("k", "n"), p["value"])) if grid else {"value": p["value"]}
            rows.append({**key, "K": p["K"], "runs": n, "t90_mean_s": mean,
                         "t90_std_s": std, "no_alcanzado": missing, "no_generado": failed})
            print(f"  {name}/{p['label']:8s} <t_90> = {mean:6.2f} ± {std:5.2f} s"
                  f"  ({n} ok, {missing} no, {failed} sin generar)")
            if n and mean < best[0]:
                best = (mean, f"{name}/{p['label']}", run_dir)
        write_csv(name, rows)
        top = min((rp for rp in zip(rows, points) if rp[0]["runs"]),
                  key=lambda rp: rp[0]["t90_mean_s"], default=None)
        if top:
            best_by_family.append((FAMILY_NAMES.get(name, name), top[0]["t90_mean_s"],
                                   top[0]["t90_std_s"], top[1]["label"]))

        fig, ax = plt.subplots()
        empty_band(ax, empty_mean, empty_std)
        if grid:
            # n = 0 filas = el bloque solo (barrido `multi_barrier`, si está corrido): así la
            # curva arranca en la configuración de partida.
            ks = sorted({r["k"] for r in rows if args.grid_k is None or r["k"] in args.grid_k})
            cmap = plt.get_cmap("viridis")
            shown_best = None  # (<t_90>, n) del mejor punto dibujado
            for i, k in enumerate(ks):
                sub = [r for r in rows if r["k"] == k and r["runs"]]
                block_dir = SWEEPS / "multi_barrier" / f"k{k:02d}"
                if next(block_dir.glob("s*"), None):
                    mean, std, n, _, _ = t90_stats(block_dir)
                    if n:
                        sub.insert(0, {"n": 0, "t90_mean_s": mean, "t90_std_s": std})
                color = cmap(0.85 * i / max(1, len(ks) - 1))
                plot_curve(ax, [r["n"] for r in sub], sub, color=color, label=f"k = {k}")
                top_k = min(sub, key=lambda r: r["t90_mean_s"])
                if shown_best is None or top_k["t90_mean_s"] < shown_best[0]:
                    shown_best = (top_k["t90_mean_s"], top_k["n"])
            ax.set_xlabel("Cantidad de filas por lado")
            ax.xaxis.get_major_locator().set_params(integer=True)
            ax.legend(loc="upper left", ncol=2)
            mark_point_x(ax, shown_best[1], shown_best[0], f"{shown_best[1]:g}")
        else:
            draw_single(ax, name, rows, points[0]["variable"])
        ax.set_ylabel(LABEL_T90)
        save_figure(fig, f"t90_{name}.png")

    print(f"  mejor: {best[1]} con <t_90> = {best[0]:.2f} s")

    # --- barras: mejor configuración de cada familia --------------------------------------
    fig, ax = plt.subplots()
    xs = np.arange(len(best_by_family))
    ax.bar(xs, [b[1] for b in best_by_family], yerr=[b[2] for b in best_by_family],
           color=[FAMILY_COLORS.get(b[0], DATA_COLOR) for b in best_by_family],
           capsize=4, width=0.6)
    ax.set_xticks(xs, [b[0].replace(" ", "\n", 1) if len(b[0]) > 12 else b[0]
                       for b in best_by_family])
    ax.set_ylabel(LABEL_T90)
    save_figure(fig, "t90_best.png")
    print("  t90_best.png (mejor punto por familia; va al costado de la figura):")
    for name, mean, std, label in best_by_family:
        print(f"    {name:18s} {label:8s} <t_90> = {mean:5.1f} ± {std:3.1f} s")

    fg_dir = SWEEPS / args.fg_config if args.fg_config else best[2]
    print(f"  fg_vs_t.png: mesa vacía vs {fg_dir.relative_to(SWEEPS)} (seed 1)")
    plot_fg([("mesa vacía", SWEEPS / "empty" / "s1"), ("con obstáculos", fg_dir / "s1")],
            "fg_vs_t.png")


if __name__ == "__main__":
    main()
