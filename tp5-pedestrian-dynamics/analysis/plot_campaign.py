"""Figuras de la campaña (scripts/run_campaign.py): los tres esquemas, R_h del híbrido y niveles de EDMD.

Lee output/campaign/N<N>_L<L>/<config>/seed<k>/{run.json, events.csv, schemes.csv}.

Escalares de una realización:
  tiempo de evacuación  t_evac = instante del último retiro (run.json; sin dato si no evacuaron todos)
  t_90                  instante en que se retiró el 90 % de los agentes (events.csv, "exit")
  caudal                Q = (n_80 − n_20) / (t_80 − t_20), con t_p el instante del cruce de puerta
                        número n_p = p N / 100 (events.csv, "door": primer cruce de cada agente)
  tiempo de ejecución   loopTimeMs de run.json (lazo de simulación, sin guardar estados; sin dato si
                        no evacuaron todos: la corrida se cortó en t-max)
Curva de población: N_in(t) = N − (cruces de puerta hasta t), de una sola corrida por esquema (misma
seed), para ver el comportamiento; los promedios van en los escalares.
Agentes en cada esquema (híbrido, punto a): una sola corrida, schemes.csv (agentes activos en paso
temporal y en eventos en cada paso) dividido por N: fracción de los N agentes iniciales.
Por configuración: promedio entre realizaciones ± desvío estándar entre realizaciones (ddof = 1; un
escalar por realización). Las realizaciones sin dato (no evacuaron) se excluyen del promedio y se
informan por stdout, igual que los valores alejados de la mediana (posibles atascos).

Figuras en analysis/figures/campaign/, todas con el sistema base N = 500 (la campaña también tiene
N = 200, la alternativa opcional de la cátedra: da las mismas conclusiones y no se grafica); por
stdout, la tabla de cada figura (lo que va al costado).

Uso: python3 analysis/plot_campaign.py
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from common import TP_ROOT, decade_ticks, format_pm, save_figure, use_style, value_ticks

import matplotlib.pyplot as plt  # noqa: E402  (después de common: backend Agg)
from matplotlib.lines import Line2D  # noqa: E402

CAMPAIGN = TP_ROOT / "output" / "campaign"
GROUP = "campaign"
RH = (0.1, 0.2, 0.3, 0.5, 0.75, 1, 1.5, 2, 3, 5, 10)
R_MIN, R_MAX = 0.10, 0.25
RH_STEPPED = tuple(rh for rh in RH if rh >= 2 * R_MIN)  # con R_h menor nadie pasa a paso temporal
LEVELS = tuple(range(9))
SCALING_N = (100, 200, 300, 500, 700, 1000)
RH_BEST = 0.5  # híbrido de la comparación entre esquemas
N_BASE = 500  # sistema base del enunciado

# (config, leyenda, marcador, color); el híbrido se dibuja último, encima del paso temporal. Colores de
# los esquemas como en la animación del híbrido: azul eventos, rojo paso temporal.
SCHEMES = (
    ("tsdmd", "paso temporal", "o", "tab:red"),
    ("edmd_lv8", "eventos", "s", "tab:blue"),
    (f"hybrid_rh{RH_BEST:g}", "híbrido", "^", "black"),
)
SCALARS = {
    # clave: (rótulo del eje, nombre de archivo)
    "evac": ("Tiempo de evacuación (s)", "evacuacion"),
    "t90": ("Tiempo de salida del 90 % (s)", "t90"),
    "q": ("Caudal (1/s)", "caudal"),
    "loop": ("Tiempo de ejecución (s)", "ejecucion"),
}


@dataclass(frozen=True)
class Run:
    seed: int
    meta: dict
    door: np.ndarray  # instantes de cruce de puerta, ordenados
    exits: np.ndarray  # instantes de retiro, ordenados

    def scalar(self, key: str) -> float:
        n = self.meta["N"]
        if key == "evac":
            return self.meta["evacuationTime"] if self.meta["evacuated"] else np.nan
        if key == "loop":
            return self.meta["loopTimeMs"] / 1e3 if self.meta["evacuated"] else np.nan
        if key == "t90":
            k = int(0.9 * n)
            return self.exits[k - 1] if self.exits.size >= k else np.nan
        if key == "q":
            a, b = int(0.2 * n), int(0.8 * n)
            return (b - a) / (self.door[b] - self.door[a]) if self.door.size > b else np.nan
        raise KeyError(key)


_cache: dict[Path, list[Run]] = {}


def load(n: int, length: float, config: str) -> list[Run]:
    root = CAMPAIGN / f"N{n}_L{length:g}" / config
    if root not in _cache:
        runs = []
        for path in sorted(root.glob("seed*/run.json"), key=lambda p: int(p.parent.name[4:])):
            door, exits = [], []
            for line in (path.parent / "events.csv").read_text().splitlines()[1:]:
                t, _, event = line.split(",")
                (door if event == "door" else exits).append(float(t))
            runs.append(Run(int(path.parent.name[4:]), json.loads(path.read_text()), np.sort(door), np.sort(exits)))
        _cache[root] = runs
    return _cache[root]


def stats(n: int, length: int, config: str, key: str) -> tuple[float, float, int, int]:
    """→ (promedio, desvío, realizaciones con dato, realizaciones); avisa valores alejados."""
    runs = load(n, length, config)
    values = np.array([r.scalar(key) for r in runs])
    ok = values[np.isfinite(values)]
    if ok.size == 0:
        return np.nan, np.nan, 0, len(runs)
    median = np.median(ok)
    mad = 1.4826 * np.median(np.abs(ok - median))
    if mad > 0:
        for run, value in zip(runs, values):
            if np.isfinite(value) and abs(value - median) > max(5 * mad, 0.1 * median):
                print(f"    AVISO valor alejado: N{n}_L{length}/{config} seed {run.seed}: "
                      f"{SCALARS[key][1]} = {value:.4g} (mediana {median:.4g})")
    return ok.mean(), ok.std(ddof=1) if ok.size > 1 else 0.0, ok.size, len(runs)


def row(label: str, n: int, length: int, config: str, key: str) -> tuple[float, float]:
    mean, std, ok, total = stats(n, length, config, key)
    missing = "" if ok == total else f" ({total - ok} de {total} sin dato)"
    print(f"    {label:>22s}: {format_pm(mean, std)}{missing}  [{ok} realizaciones]")
    return mean, std


def log_limits(ax, values) -> None:
    """Eje y logarítmico en décadas enteras, con margen para que ningún punto quede sobre el borde."""
    values = np.asarray([v for v in values if np.isfinite(v) and v > 0])
    lo, hi = int(np.floor(np.log10(values.min() / 1.3))), int(np.ceil(np.log10(values.max() * 1.3)))
    ax.set_yscale("log")
    ax.set_ylim(10.0**lo, 10.0**hi)
    decade_ticks(ax.yaxis, lo, hi)


def rh_axis(ax, values=RH) -> None:
    """Eje R_h; rectas punteadas en 2 r_min (por debajo, eventos puro) y en 2 r_max."""
    ax.set_xscale("log")
    ax.set_xlim(values[0] / 1.15, values[-1] * 1.15)
    value_ticks(ax.xaxis, values)
    for mark in (2 * R_MIN, 2 * R_MAX):
        ax.axvline(mark, color="gray", ls=":", lw=0.9, zorder=0)
    ax.set_xlabel("Radio del área (m)")


# ------------------------------------------------------------------------------- esquemas (b, c)

def population(n: int, seed: int = 1) -> None:
    """Agentes en la habitación vs t: una corrida por esquema (misma seed)."""
    print(f"\nCurvas de población, N = {n}, L = 50 m, seed {seed} (híbrido con R_h = {RH_BEST:g} m)")
    fig, ax = plt.subplots()
    for config, label, _, color in SCHEMES:
        runs = [run for run in load(n, 50, config) if run.seed == seed]
        if not runs:
            continue
        run = runs[0]
        thick = config == "tsdmd"  # el híbrido cae encima: paso temporal grueso y detrás
        t = np.concatenate(([0.0], run.door))
        inside = n - np.arange(run.door.size + 1)
        ax.step(t, inside, where="post", color=color, lw=3.0 if thick else 1.0,
                alpha=0.4 if thick else 1.0, zorder=1 if thick else 2, label=label)
        print(f"    {label}: evacuación {run.scalar('evac'):.1f} s, último cruce de puerta {run.door[-1]:.1f} s")
    ax.set_xlabel("Tiempo (s)")
    ax.set_ylabel("Agentes en la habitación")
    ax.set_xlim(left=0)
    ax.set_ylim(0, n * 1.02)
    legend = ax.legend(loc="upper right")
    for handle in legend.get_lines():
        handle.set_alpha(1)
    save_figure(fig, GROUP, f"poblacion_N{n}.png")


def schemes(key: str, n: int) -> None:
    """Escalar de cada esquema puro y del híbrido: un punto por esquema, con su color; sin leyenda."""
    ylabel, name = SCALARS[key]
    print(f"\n{ylabel} por esquema, N = {n}, L = 50 m (híbrido con R_h = {RH_BEST:g} m)")
    fig, ax = plt.subplots()
    plotted = []
    for k, (config, label, marker, color) in enumerate(SCHEMES):
        mean, std = row(label, n, 50, config, key)
        if np.isfinite(mean):
            ax.errorbar([k], [mean], yerr=[std], fmt=marker, color=color, capsize=6, elinewidth=1.3, ms=6)
            plotted += [mean - std, mean + std]
    if not plotted:
        plt.close(fig)
        return
    ax.set_xticks(range(len(SCHEMES)), [label for _, label, _, _ in SCHEMES])
    ax.set_xlim(-0.5, len(SCHEMES) - 0.5)
    ax.set_ylabel(ylabel)
    if key == "loop":
        log_limits(ax, plotted)
    else:
        ax.set_ylim(0, 1.1 * max(plotted))
    save_figure(fig, GROUP, f"{name}_esquemas.png")


# ------------------------------------------------------------------------- híbrido: R_h (a, c)

def hybrid_vs_rh(n: int, key: str, zoom: bool = False) -> None:
    """Escalar del híbrido vs R_h con los esquemas puros de referencia. `zoom`: escala lineal, solo
    R_h ≥ 2 r_min (por debajo es eventos puro) y solo la referencia de paso temporal."""
    ylabel, name = SCALARS[key]
    values = RH_STEPPED if zoom else RH
    print(f"\n{ylabel} del híbrido vs R_h, N = {n}, L = 50 m" + (" (R_h ≥ 2 r_min)" if zoom else ""))
    data = [row(f"R_h = {rh:g} m", n, 50, f"hybrid_rh{rh:g}", key) for rh in values]
    mean, std = np.array(data).T
    if not np.isfinite(mean).any():
        return
    fig, ax = plt.subplots()
    plotted = list(mean - std) + list(mean + std)
    for config, label, _, color in SCHEMES[:1] if zoom else SCHEMES[:2]:
        ref, ref_std = row(label, n, 50, config, key)
        if np.isfinite(ref):
            ax.axhspan(ref - ref_std, ref + ref_std, color=color, alpha=0.18, lw=0, zorder=0)
            ax.axhline(ref, color=color, ls="--", label=label, zorder=1)
            plotted += [ref - ref_std, ref + ref_std]
    ax.errorbar(values, mean, yerr=std, fmt="^-", color="black", capsize=4, elinewidth=1.3, label="híbrido",
                zorder=3)
    rh_axis(ax, values)
    ax.set_ylabel(ylabel)
    if key == "loop" and not zoom:
        log_limits(ax, plotted)
    ax.legend(loc="best")
    save_figure(fig, GROUP, f"hibrido_{name}_vs_rh_N{n}{'_zoom' if zoom else ''}.png")


def scheme_population(n: int, length: int, rh: float, seed: int = 1) -> None:
    """Una corrida del híbrido: fracción de los N agentes que está en cada esquema en cada paso."""
    print(f"\nAgentes en cada esquema vs t (híbrido), N = {n}, L = {length} m, R_h = {rh:g} m, seed {seed}")
    path = CAMPAIGN / f"N{n}_L{length}" / f"hybrid_rh{rh:g}" / f"seed{seed}" / "schemes.csv"
    if not path.is_file():
        print("    sin corrida")
        return
    t, ts, ed = np.loadtxt(path, delimiter=",", skiprows=1, unpack=True)
    fig, ax = plt.subplots()
    ax.plot(t, ed / n, color="tab:blue", lw=1.0, label="eventos")
    ax.plot(t, ts / n, color="tab:red", lw=1.0, label="paso temporal")
    ax.set_xlabel("Tiempo (s)")
    ax.set_ylabel("Fracción de agentes")
    ax.set_xlim(left=0)
    ax.set_ylim(0, 1.03)
    ax.legend(loc="best")
    # Condición inicial: el criterio de pasaje en t = 0 (quien no tiene a nadie en el área arranca en eventos).
    cross = t[np.argmax(ts >= ed)]
    peak = np.argmax(ts)
    print(f"    en t = 0: {int(ed[0])} agentes en eventos y {int(ts[0])} en paso temporal")
    print(f"    paso temporal supera a eventos desde t = {cross:.1f} s; máximo en paso temporal: "
          f"{int(ts[peak])} agentes en t = {t[peak]:.1f} s")
    print(f"    pasos-agente en paso temporal: {ts.sum() / (ts + ed).sum():.2f} del total")
    save_figure(fig, GROUP, f"hibrido_agentes_por_esquema_N{n}_L{length}_rh{rh:g}.png")


def scheme_fraction(n: int, seed: int = 1) -> None:
    print(f"\nFracción de agentes en paso temporal vs t (híbrido), N = {n}, L = 50 m, seed {seed}")
    shown = (0.2, 0.5, 1, 2, 5)
    fig, ax = plt.subplots()
    colors = plt.cm.viridis(np.linspace(0, 0.9, len(shown)))
    drawn = False
    for rh, color in zip(shown, colors):
        path = CAMPAIGN / f"N{n}_L50" / f"hybrid_rh{rh:g}" / f"seed{seed}" / "schemes.csv"
        if not path.is_file():
            continue
        t, ts, ed = np.loadtxt(path, delimiter=",", skiprows=1, unpack=True)
        active = ts + ed
        keep = active > 0
        fraction = ts[keep] / active[keep]
        ax.plot(t[keep], fraction, color=color, lw=0.9, label=f"{rh:g}")
        print(f"    R_h = {rh:g} m: promedio temporal de la fracción en paso temporal {fraction.mean():.2f}")
        drawn = True
    if not drawn:
        plt.close(fig)
        return
    ax.set_xlabel("Tiempo (s)")
    ax.set_ylabel("Fracción de agentes en paso temporal")
    ax.set_xlim(left=0)
    ax.set_ylim(0, 1.03)
    ax.legend(title="$R_h$ (m)", loc="center")
    save_figure(fig, GROUP, f"fraccion_paso_temporal_N{n}.png")


def room_size(n: int, zoom: bool = False) -> None:
    """Tiempo de ejecución del híbrido vs R_h para varios L; la recta de trazos del mismo color es el
    paso temporal en esa habitación (no depende de R_h). Con todos los R_h, en escala logarítmica: el
    punto con R_h < 2 r_min es eventos puro. `zoom`: escala lineal y solo R_h ≥ 2 r_min."""
    values = RH_STEPPED if zoom else RH
    print(f"\nTiempo de ejecución (s) del híbrido vs R_h para varios L, N = {n}" + (" (R_h ≥ 2 r_min)" if zoom else ""))
    lengths = (50, 150, 300)
    fig, ax = plt.subplots()
    drawn = []
    plotted = []
    for length, color, marker in zip(lengths, plt.cm.viridis(np.linspace(0, 0.8, len(lengths))), "os^"):
        print(f"  L = {length} m")
        ref, ref_std = row("paso temporal", n, length, "tsdmd", "loop")
        data = [row(f"R_h = {rh:g} m", n, length, f"hybrid_rh{rh:g}", "loop") for rh in values]
        mean, std = np.array(data).T
        if not (np.isfinite(ref) and np.isfinite(mean).any()):
            continue
        ratio = mean / ref
        error = ratio * np.hypot(std / mean, ref_std / ref)  # propagación de los dos desvíos
        for rh, value, err in zip(values, ratio, error):
            print(f"      R_h = {rh:g} m: híbrido / paso temporal = {format_pm(value, err)}")
        ax.axhline(ref, color=color, ls="--", zorder=1)
        drawn.append(ax.errorbar(values, mean, yerr=std, fmt=marker + "-", color=color, capsize=4,
                                 elinewidth=1.3, zorder=2, label=str(length)))
        plotted += list(mean - std) + list(mean + std) + [ref]
    if not drawn:
        plt.close(fig)
        return
    rh_axis(ax, values)
    ax.set_ylabel("Tiempo de ejecución (s)")
    styles = [Line2D([], [], color="gray", marker="o", ls="-", label="híbrido"),
              Line2D([], [], color="gray", ls="--", label="paso temporal")]
    if zoom:
        ax.set_ylim(bottom=0)
        by_length = ax.legend(handles=drawn, title="$L$ (m)", loc="lower left", ncol=len(drawn), columnspacing=1.0)
        ax.add_artist(by_length)
        ax.legend(handles=styles, loc="lower right")
    else:  # los puntos de eventos puro quedan arriba a la izquierda: leyendas arriba a la derecha
        log_limits(ax, plotted)
        by_length = ax.legend(handles=drawn, title="$L$ (m)", loc="upper right", ncol=len(drawn), columnspacing=1.0)
        ax.add_artist(by_length)
        ax.legend(handles=styles, loc="upper right", bbox_to_anchor=(1.0, 0.78))
    save_figure(fig, GROUP, f"hibrido_ejecucion_vs_rh_por_L_N{n}{'_zoom' if zoom else ''}.png")


# ------------------------------------------------------------------------------ EDMD: niveles

def edmd_levels(key: str, n: int) -> None:
    """Escalar de eventos vs radios intermedios, con paso temporal de referencia (recta de trazos)."""
    ylabel, name = SCALARS[key]
    print(f"\n{ylabel} de eventos vs radios intermedios, N = {n}, L = 50 m")
    data = [row(f"{k} niveles", n, 50, f"edmd_lv{k}", key) for k in LEVELS]
    mean, std = np.array(data).T
    if not np.isfinite(mean).any():
        return
    fig, ax = plt.subplots()
    plotted = list(mean - std) + list(mean + std)
    ref, ref_std = row("paso temporal", n, 50, "tsdmd", key)
    if np.isfinite(ref):
        ax.axhspan(ref - ref_std, ref + ref_std, color="tab:red", alpha=0.18, lw=0, zorder=0)
        ax.axhline(ref, color="tab:red", ls="--", label="paso temporal", zorder=1)
        plotted += [ref - ref_std, ref + ref_std]
    ax.errorbar(LEVELS, mean, yerr=std, fmt="s-", color="tab:blue", capsize=4, elinewidth=1.3, label="eventos",
                zorder=3)
    ax.set_xticks(LEVELS)
    ax.set_xlabel("Radios intermedios de la recuperación")
    ax.set_ylabel(ylabel)
    if key in ("t90", "evac", "loop"):
        log_limits(ax, plotted)
    else:
        ax.set_ylim(bottom=0)
    ax.legend(loc="best")
    save_figure(fig, GROUP, f"eventos_{name}_vs_niveles.png")


# ------------------------------------------------------------------------- escalamiento con N (d)

def scaling(constant_density: bool) -> None:
    """Tiempo de ejecución vs N en log-log; por stdout, el exponente local entre N consecutivos."""
    variant = "densidad inicial constante, L = 50 m √(N/500)" if constant_density else "L = 50 m"
    print(f"\nTiempo de ejecución (s) vs N, {variant} (híbrido con R_h = {RH_BEST:g} m)")
    fig, ax = plt.subplots()
    plotted = []
    for config, label, marker, color in SCHEMES:
        print(f"  {label}")
        ns, means, stds = [], [], []
        for n in SCALING_N:
            length = round(50 * math.sqrt(n / 500), 2) if constant_density else 50
            mean, std = row(f"N = {n}, L = {length:g} m", n, length, config, "loop")
            if np.isfinite(mean):
                ns.append(n)
                means.append(mean)
                stds.append(std)
        if len(ns) < 2:
            continue
        ns, means, stds = np.array(ns), np.array(means), np.array(stds)
        slopes = np.diff(np.log(means)) / np.diff(np.log(ns))
        print("    exponente local α (t ∝ N^α) entre N consecutivos: "
              + ", ".join(f"{a}–{b}: {s:.2f}" for a, b, s in zip(ns[:-1], ns[1:], slopes)))
        ax.errorbar(ns, means, yerr=stds, fmt=marker + "-", color=color, capsize=4, elinewidth=1.3, label=label)
        plotted += list(means - stds) + list(means + stds)
    if not plotted:
        plt.close(fig)
        return
    ax.set_xscale("log")
    ax.set_xlim(SCALING_N[0] / 1.2, SCALING_N[-1] * 1.2)
    value_ticks(ax.xaxis, SCALING_N)
    log_limits(ax, plotted)
    ax.set_xlabel("Número de agentes")
    ax.set_ylabel("Tiempo de ejecución (s)")
    ax.legend(loc="best")
    save_figure(fig, GROUP, f"ejecucion_vs_N_{'densidad_constante' if constant_density else 'L50'}.png")


def main() -> None:
    use_style()
    n = N_BASE
    population(n)
    for key in ("evac", "q", "loop"):
        schemes(key, n)
    hybrid_vs_rh(n, "loop")
    hybrid_vs_rh(n, "loop", zoom=True)
    hybrid_vs_rh(n, "evac")
    hybrid_vs_rh(n, "q")
    scheme_fraction(n)
    for length in (50, 300):
        scheme_population(n, length, RH_BEST)
    room_size(n)
    room_size(n, zoom=True)
    for key in ("t90", "evac", "q", "loop"):
        edmd_levels(key, n)
    for constant_density in (False, True):
        scaling(constant_density)


if __name__ == "__main__":
    main()
