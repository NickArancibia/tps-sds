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
informan por stdout, igual que los valores alejados de la mediana (posibles atascos). En las figuras
de input vs observable, el punto de una configuración en la que alguna realización no evacuó (se
cortó en t-max) va con el símbolo vacío (fondo blanco, borde del color de la curva), también cuando
el escalar tiene dato en todas (t_90 y caudal); el significado va en una entrada de la leyenda.

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
from matplotlib.colors import to_hex  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402

CAMPAIGN = TP_ROOT / "output" / "campaign"
GROUP = "campaign"
RH = (0.1, 0.2, 0.3, 0.5, 0.75, 1, 1.5, 2, 3, 5, 10)
R_MIN, R_MAX = 0.10, 0.25
RH_STEPPED = tuple(rh for rh in RH if rh >= 2 * R_MIN)  # con R_h menor nadie pasa a paso temporal
LEVELS = tuple(range(9))
SCALING_N = (10, 25, 50, 75, 100, 200, 300, 500, 700, 1000)
N_TICKS = (10, 25, 50, 100, 200, 500, 1000)  # rótulos del eje N: los 10 valores se pisan
RH_PANEL_TICKS = (0.1, 0.2, 0.5, 1, 2, 5, 10)  # rótulos del eje R_h en los paneles angostos
HOLLOW_LABEL = "alguna realización no evacuó"
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
    # clave: (rótulo del eje, nombre de archivo). Ejes con la notación de la diapositiva de Observables
    # y no en palabras (pedido del grupo, 2026-11-12); el tiempo de ejecución no tiene símbolo.
    "evac": (r"$\langle t_{ev} \rangle$ (s)", "evacuacion"),
    "t90": (r"$\langle t_{90} \rangle$ (s)", "t90"),
    "q": (r"$\langle Q \rangle$ (1/s)", "caudal"),
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


def stuck(n: int, length: float, config: str) -> int:
    """Realizaciones que no evacuaron (cortadas en t-max)."""
    return sum(not run.meta["evacuated"] for run in load(n, length, config))


def row(label: str, n: int, length: int, config: str, key: str) -> tuple[float, float]:
    mean, std, ok, total = stats(n, length, config, key)
    missing = "" if ok == total else f" ({total - ok} de {total} sin dato)"
    jammed = stuck(n, length, config)
    jammed = f" ({jammed} de {total} no evacuaron: símbolo vacío)" if jammed else ""
    print(f"    {label:>22s}: {format_pm(mean, std)}{missing}{jammed}  [{ok} realizaciones]")
    return mean, std


def hollow(ax, x, y, incomplete, marker: str, color, used: list) -> None:
    """Símbolo vacío sobre los puntos `incomplete` (alguna realización no evacuó). Va encima de todas
    las curvas: si otro punto cae en el mismo lugar, el vacío es el que tiene que verse. Anota en
    `used` el símbolo dibujado, para la entrada de la leyenda."""
    x, y, incomplete = np.asarray(x, float), np.asarray(y, float), np.asarray(incomplete, bool)
    if incomplete.any():
        ax.plot(x[incomplete], y[incomplete], marker, mfc="white", mec=color, mew=1.2, zorder=10)
        used.append((marker, to_hex(color)))


def hollow_handle(used: list) -> list[Line2D]:
    """Entrada de leyenda del símbolo vacío (pedido del grupo, 2026-11-13); ninguna si no se dibujó.
    Con el símbolo de la curva si todos los vacíos son de una sola; si no, un círculo gris."""
    if not used:
        return []
    marker, color = used[0] if len(set(used)) == 1 else ("o", "0.3")
    return [Line2D([], [], ls="none", marker=marker, mfc="white", mec=color, mew=1.2, label=HOLLOW_LABEL)]


def legend(ax, used: list, **kwargs):
    """Leyenda de las curvas del eje más, si hay símbolos vacíos, su entrada."""
    return ax.legend(handles=[*ax.get_legend_handles_labels()[0], *hollow_handle(used)], **kwargs)


def log_limits(ax, values) -> None:
    """Eje y logarítmico en décadas enteras, con margen para que ningún punto quede sobre el borde."""
    values = np.asarray([v for v in values if np.isfinite(v) and v > 0])
    lo, hi = int(np.floor(np.log10(values.min() / 1.3))), int(np.ceil(np.log10(values.max() * 1.3)))
    ax.set_yscale("log")
    ax.set_ylim(10.0**lo, 10.0**hi)
    decade_ticks(ax.yaxis, lo, hi)


def rh_axis(ax, values=RH, ticks=None) -> None:
    """Eje R_h, logarítmico y rotulado en los valores medidos (o en `ticks`, si todos no entran)."""
    ax.set_xscale("log")
    ax.set_xlim(values[0] / 1.15, values[-1] * 1.15)
    value_ticks(ax.xaxis, ticks or values)
    ax.set_xlabel("$R_h$ (m)")


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
    ax.set_xlabel("$t$ (s)")
    ax.set_ylabel("$N_{in}$")
    ax.set_xlim(left=0)
    ax.set_ylim(0, n * 1.02)
    legend = ax.legend(loc="upper right")
    for handle in legend.get_lines():
        handle.set_alpha(1)
    save_figure(fig, GROUP, f"poblacion_N{n}.png")


def schemes(key: str, n: int) -> None:
    """Escalar de cada esquema puro y del híbrido: un punto por esquema, con su símbolo, su color y
    su desvío (pedido del grupo, 2026-11-13; antes eran barras). Sin unir y sin leyenda: el eje nombra
    cada esquema. Tiempo de ejecución en escala logarítmica, como en el resto de las figuras."""
    ylabel, name = SCALARS[key]
    print(f"\n{ylabel} por esquema, N = {n}, L = 50 m (híbrido con R_h = {RH_BEST:g} m)")
    fig, ax = plt.subplots()
    plotted, used = [], []
    for k, (config, label, marker, color) in enumerate(SCHEMES):
        mean, std = row(label, n, 50, config, key)
        if np.isfinite(mean):
            ax.errorbar(k, mean, yerr=std, fmt=marker, color=color, capsize=6, elinewidth=1.3, markersize=7)
            hollow(ax, [k], [mean], [stuck(n, 50, config)], marker, color, used)
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
        ax.margins(y=0.15)
    if used:
        ax.legend(handles=hollow_handle(used), loc="best")
    save_figure(fig, GROUP, f"{name}_esquemas.png")


# ------------------------------------------------------------------------- híbrido: R_h (a, c)

def hybrid_vs_rh(n: int) -> None:
    """Escalares del híbrido vs R_h con los esquemas puros de referencia (rectas de trazos): una
    figura por escalar y `hibrido_vs_rh_N<n>.png` con el tiempo de evacuación, el caudal y el tiempo
    de ejecución lado a lado (pedido del grupo, 2026-11-13: una sola diapositiva, como la de n_r).
    Los tres paneles comparten el eje R_h (rotulado en RH_PANEL_TICKS: los 11 valores no entran) y la
    leyenda, arriba. `zoom` (solo tiempo de ejecución, sin panel): escala lineal, R_h ≥ 2 r_min (por
    debajo es eventos puro) y solo la referencia de paso temporal."""
    order = ("evac", "q", "loop")
    summary, panels = plt.subplot_mosaic([["legend"] * 3, list(order)], figsize=(8.0, 3.3),
                                         height_ratios=[0.1, 1])
    shared = []
    for key, zoom in [(key, False) for key in order] + [("loop", True)]:
        ylabel, name = SCALARS[key]
        values = RH_STEPPED if zoom else RH
        print(f"\n{ylabel} del híbrido vs R_h, N = {n}, L = 50 m" + (" (R_h ≥ 2 r_min)" if zoom else ""))
        data = [row(f"R_h = {rh:g} m", n, 50, f"hybrid_rh{rh:g}", key) for rh in values]
        mean, std = np.array(data).T
        refs = [(label, color, *row(label, n, 50, config, key))
                for config, label, _, color in (SCHEMES[:1] if zoom else SCHEMES[:2])]
        fig, single = plt.subplots()
        for ax in [single] + ([] if zoom else [panels[key]]):
            used = []
            plotted = list(mean - std) + list(mean + std)
            for label, color, ref, ref_std in refs:
                ax.axhspan(ref - ref_std, ref + ref_std, color=color, alpha=0.18, lw=0, zorder=0)
                ax.axhline(ref, color=color, ls="--", label=label, zorder=1)
                plotted += [ref - ref_std, ref + ref_std]
            ax.errorbar(values, mean, yerr=std, fmt="^-", color="black", capsize=4, elinewidth=1.3,
                        label="híbrido", zorder=3)
            hollow(ax, values, mean, [stuck(n, 50, f"hybrid_rh{rh:g}") for rh in values], "^", "black", used)
            rh_axis(ax, values, None if ax is single else RH_PANEL_TICKS)
            ax.set_ylabel(ylabel)
            if key == "loop" and not zoom:
                log_limits(ax, plotted)
            if ax is not single:
                shared = used
        legend(single, used, loc="best")
        save_figure(fig, GROUP, f"hibrido_{name}_vs_rh_N{n}{'_zoom' if zoom else ''}.png")
    panels["legend"].axis("off")
    panels["legend"].legend(handles=[*panels["loop"].get_legend_handles_labels()[0], *hollow_handle(shared)],
                            loc="center", ncol=4)
    save_figure(summary, GROUP, f"hibrido_vs_rh_N{n}.png")


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
    ax.set_xlabel("$t$ (s)")
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
    ax.set_xlabel("$t$ (s)")
    ax.set_ylabel("$N_{pt}/(N_{ev} + N_{pt})$")
    ax.set_xlim(left=0)
    ax.set_ylim(0, 1.03)
    ax.legend(title="$R_h$ (m)", loc="center")
    save_figure(fig, GROUP, f"fraccion_paso_temporal_N{n}.png")


def room_size(n: int, key: str, zoom: bool = False) -> None:
    """Escalar del híbrido vs R_h para varios L; la recta de trazos del mismo color, con su banda de
    ± un desvío, es el paso temporal en esa habitación (no depende de R_h). Dos leyendas con los
    mismos símbolos: L y la densidad inicial N/L² que le corresponde (pedido del grupo, 2026-11-13);
    qué es la recta de trazos va al costado de la figura. Con todos los R_h el punto con
    R_h < 2 r_min es eventos puro, y el tiempo de ejecución va en escala logarítmica. `zoom`: escala
    lineal y solo R_h ≥ 2 r_min."""
    ylabel, name = SCALARS[key]
    values = RH_STEPPED if zoom else RH
    print(f"\n{ylabel} del híbrido vs R_h para varios L, N = {n}" + (" (R_h ≥ 2 r_min)" if zoom else ""))
    lengths = (50, 150, 300)
    fig, ax = plt.subplots()
    drawn, densities, plotted, used = [], [], [], []
    for length, color, marker in zip(lengths, plt.cm.viridis(np.linspace(0, 0.8, len(lengths))), "os^"):
        print(f"  L = {length} m, N/L² = {n / length**2:.2g} 1/m²")
        ref, ref_std = row("paso temporal", n, length, "tsdmd", key)
        data = [row(f"R_h = {rh:g} m", n, length, f"hybrid_rh{rh:g}", key) for rh in values]
        mean, std = np.array(data).T
        if not (np.isfinite(ref) and np.isfinite(mean).any()):
            continue
        ratio = mean / ref
        error = ratio * np.hypot(std / mean, ref_std / ref)  # propagación de los dos desvíos
        for rh, value, err in zip(values, ratio, error):
            print(f"      R_h = {rh:g} m: híbrido / paso temporal = {format_pm(value, err)}")
        ax.axhspan(ref - ref_std, ref + ref_std, color=color, alpha=0.18, lw=0, zorder=0)
        ax.axhline(ref, color=color, ls="--", zorder=1)
        drawn.append(ax.errorbar(values, mean, yerr=std, fmt=marker + "-", color=color, capsize=4,
                                 elinewidth=1.3, zorder=2, label=str(length)))
        densities.append(Line2D([], [], ls="none", marker=marker, color=color, label=f"{n / length**2:.2g}"))
        hollow(ax, values, mean, [stuck(n, length, f"hybrid_rh{rh:g}") for rh in values], marker, color, used)
        plotted += list(mean - std) + list(mean + std) + [ref - ref_std, ref + ref_std]
    if not drawn:
        plt.close(fig)
        return
    rh_axis(ax, values)
    ax.set_ylabel(ylabel)
    if key == "loop" and not zoom:
        log_limits(ax, plotted)  # eventos puro queda arriba a la izquierda: leyendas arriba a la derecha
        corner = "upper right"
    else:
        ax.set_ylim(bottom=0)
        corner = "lower left" if key == "loop" else "lower right"
    # Las dos leyendas apiladas en la misma esquina, la de L arriba y la de densidad debajo.
    by_length = dict(handles=drawn, title="$L$ (m)")
    by_density = dict(handles=densities + hollow_handle(used), title="$N/L^2$ (m$^{-2}$)")
    upper = corner.startswith("upper")
    first = ax.legend(**(by_length if upper else by_density), loc=corner, ncol=len(drawn), columnspacing=1.0)
    ax.add_artist(first)
    fig.canvas.draw()
    box = first.get_window_extent().transformed(ax.transAxes.inverted())
    ax.legend(**(by_density if upper else by_length), loc=corner, ncol=len(drawn), columnspacing=1.0,
              bbox_to_anchor=(float(corner.endswith("right")), box.y0 if upper else box.y1))
    save_figure(fig, GROUP, f"hibrido_{name}_vs_rh_por_L_N{n}{'_zoom' if zoom else ''}.png")


# ------------------------------------------------------------------------------ EDMD: niveles

def edmd_levels(n: int) -> None:
    """Escalares de eventos vs radios intermedios, con paso temporal de referencia (recta de trazos):
    una figura por escalar y `eventos_vs_niveles.png` con el tiempo de ejecución, t_90 y el caudal
    lado a lado (pedido del grupo, 2026-11-13: una sola diapositiva). Los tres paneles comparten el
    eje n_r y la leyenda, arriba; cada uno tiene su magnitud en el eje vertical."""
    summary, panels = plt.subplot_mosaic([["legend"] * 3, ["loop", "t90", "q"]], figsize=(8.0, 3.3),
                                         height_ratios=[0.1, 1])
    for key in ("t90", "evac", "q", "loop"):
        ylabel, name = SCALARS[key]
        print(f"\n{ylabel} de eventos vs radios intermedios, N = {n}, L = 50 m")
        data = [row(f"{k} niveles", n, 50, f"edmd_lv{k}", key) for k in LEVELS]
        mean, std = np.array(data).T
        ref, ref_std = row("paso temporal", n, 50, "tsdmd", key)
        fig, single = plt.subplots()
        for ax in [single] + ([panels[key]] if key in panels else []):
            used = []
            ax.axhspan(ref - ref_std, ref + ref_std, color="tab:red", alpha=0.18, lw=0, zorder=0)
            ax.axhline(ref, color="tab:red", ls="--", label="paso temporal", zorder=1)
            ax.errorbar(LEVELS, mean, yerr=std, fmt="s-", color="tab:blue", capsize=4, elinewidth=1.3,
                        label="eventos", zorder=3)
            hollow(ax, LEVELS, mean, [stuck(n, 50, f"edmd_lv{k}") for k in LEVELS], "s", "tab:blue", used)
            ax.set_xticks(LEVELS)
            ax.set_xlabel("$n_r$")
            ax.set_ylabel(ylabel)
            if key == "q":
                ax.set_ylim(bottom=0)
            else:
                log_limits(ax, list(mean - std) + list(mean + std) + [ref - ref_std, ref + ref_std])
        legend(single, used, loc="best")
        save_figure(fig, GROUP, f"eventos_{name}_vs_niveles.png")
    # La leyenda común sale del último panel dibujado (las mismas curvas y el mismo símbolo vacío en los tres).
    panels["legend"].axis("off")
    panels["legend"].legend(handles=[*panels["loop"].get_legend_handles_labels()[0], *hollow_handle(used)],
                            loc="center", ncol=3)
    save_figure(summary, GROUP, "eventos_vs_niveles.png")


# ------------------------------------------------------------------------- escalamiento con N (d)

def scaling(key: str, constant_density: bool) -> None:
    """Escalar vs N para los tres esquemas, con N en escala logarítmica. Tiempo de ejecución en
    log-log y, por stdout, el exponente local entre N consecutivos; el caudal, en escala lineal. A
    densidad constante, el eje de arriba da el lado L de la habitación que corresponde a cada N."""
    ylabel, name = SCALARS[key]
    variant = "densidad inicial constante, L = 50 m √(N/500)" if constant_density else "L = 50 m"
    print(f"\n{ylabel} vs N, {variant} (híbrido con R_h = {RH_BEST:g} m)")
    fig, ax = plt.subplots()
    plotted, used = [], []
    for config, label, marker, color in SCHEMES:
        print(f"  {label}")
        ns, means, stds, jammed = [], [], [], []
        for n in SCALING_N:
            length = round(50 * math.sqrt(n / 500), 2) if constant_density else 50
            mean, std = row(f"N = {n}, L = {length:g} m", n, length, config, key)
            if np.isfinite(mean):
                ns.append(n)
                means.append(mean)
                stds.append(std)
                jammed.append(stuck(n, length, config))
        if len(ns) < 2:
            continue
        ns, means, stds = np.array(ns), np.array(means), np.array(stds)
        if key == "loop":
            slopes = np.diff(np.log(means)) / np.diff(np.log(ns))
            print("    exponente local α (t ∝ N^α) entre N consecutivos: "
                  + ", ".join(f"{a}–{b}: {s:.2f}" for a, b, s in zip(ns[:-1], ns[1:], slopes)))
        ax.errorbar(ns, means, yerr=stds, fmt=marker + "-", color=color, capsize=4, elinewidth=1.3, label=label)
        hollow(ax, ns, means, jammed, marker, color, used)
        plotted += list(means - stds) + list(means + stds)
    if not plotted:
        plt.close(fig)
        return
    ax.set_xscale("log")
    ax.set_xlim(SCALING_N[0] / 1.2, SCALING_N[-1] * 1.2)
    value_ticks(ax.xaxis, N_TICKS)
    if key == "loop":
        log_limits(ax, plotted)
    else:
        ax.set_ylim(bottom=0)
    ax.set_xlabel("$N$")
    if constant_density:
        top = ax.twiny()
        top.set_xscale("log")
        top.set_xlim(ax.get_xlim())
        value_ticks(top.xaxis, N_TICKS)
        top.set_xticklabels([f"{50 * math.sqrt(n / 500):.0f}" for n in N_TICKS])
        top.set_xlabel("$L$ (m)")
    ax.set_ylabel(ylabel)
    legend(ax, used, loc="best")
    save_figure(fig, GROUP, f"{name}_vs_N_{'densidad_constante' if constant_density else 'L50'}.png")


def main() -> None:
    use_style()
    n = N_BASE
    population(n)
    for key in ("evac", "q", "loop"):
        schemes(key, n)
    hybrid_vs_rh(n)
    scheme_fraction(n)
    for length in (50, 300):
        scheme_population(n, length, RH_BEST)
    room_size(n, "loop")
    room_size(n, "loop", zoom=True)
    room_size(n, "q")
    edmd_levels(n)
    for constant_density in (False, True):
        scaling("loop", constant_density)
    scaling("q", constant_density=False)


if __name__ == "__main__":
    main()
