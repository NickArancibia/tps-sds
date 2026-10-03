"""Exploración (no es entregable ni resultado del TP): compara formas de inferir v(t) en Verlet
original para el oscilador amortiguado del sistema 1 (Teórica 4, diapositiva 37).

La fuerza f = -k r - γ v necesita v(t) para calcular r(t+dt), pero Verlet recién da
v(t) = (r(t+dt) - r(t-dt)) / (2 dt) después de calcularla. Variantes comparadas:

- velocidad anterior:     v(t) ≈ v(t-dt)
- diferencia hacia atrás: v(t) ≈ (r(t) - r(t-dt)) / dt
- predictor Euler:        v(t) ≈ v(t-dt) + a(t-dt) dt
- predictor-corrector:    predictor Euler, avanzar, corregir con la v(t) centrada y re-avanzar
- despeje:                v(t) centrada reemplazada en la ecuación y despejada r(t+dt)

En todas: r(-dt) por Euler en -dt; en el primer paso v(0) es dato; v(t-dt) es la centrada
(r(t) - r(t-2dt)) / (2 dt). ECM sobre los estados guardados cada 10⁻² s (AGENTS.md §5).

Uso: python3 verlet_variantes.py   → verlet_variantes_ecm.png y verlet_variantes_cociente.png
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

M, K, GAMMA, TF = 70.0, 1e4, 100.0, 5.0
R0, A = 1.0, 1.0
V0 = -A * GAMMA / (2 * M)
OMEGA = np.sqrt(K / M - GAMMA**2 / (4 * M**2))
SAVE_INTERVAL = 1e-2
DTS = [1e-2, 5e-3, 2e-3, 1e-3, 5e-4, 2e-4, 1e-4, 5e-5, 2e-5, 1e-5]
HERE = Path(__file__).resolve().parent


def analytic(t):
    return A * np.exp(-GAMMA * t / (2 * M)) * np.cos(OMEGA * t)


def force(r, v):
    return -K * r - GAMMA * v


def verlet(dt: float, variant: str) -> float:
    """Integra hasta TF y devuelve el ECM sobre los instantes múltiplos de SAVE_INTERVAL."""
    n = int(round(TF / dt))
    every = int(round(SAVE_INTERVAL / dt))
    c = GAMMA * dt / (2 * M)
    r_prev2 = None
    r_prev = R0 - dt * V0 + 0.5 * dt**2 * force(R0, V0) / M  # r(-dt), Euler en -dt
    r = R0
    times, positions = [0.0], [R0]
    for i in range(n):
        if variant == "despeje":
            r_next = r + ((1 - c) * (r - r_prev) - K * dt**2 / M * r) / (1 + c)
        else:
            if i == 0:
                v = V0
            elif variant == "diferencia hacia atrás":
                v = (r - r_prev) / dt
            else:
                v_back = (r - r_prev2) / (2 * dt)  # v(t-dt) centrada
                if variant == "velocidad anterior":
                    v = v_back
                else:  # predictor Euler / predictor-corrector
                    v = v_back + force(r_prev, v_back) / M * dt
            r_next = 2 * r - r_prev + dt**2 / M * force(r, v)
            if variant == "predictor-corrector":
                v = (r_next - r_prev) / (2 * dt)
                r_next = 2 * r - r_prev + dt**2 / M * force(r, v)
        r_prev2, r_prev, r = r_prev, r, r_next
        if (i + 1) % every == 0:
            times.append((i + 1) * dt)
            positions.append(r)
    t = np.array(times)
    return float(np.mean((np.array(positions) - analytic(t)) ** 2))


# Orden de dibujo: las que quedan superpuestas (predictor-corrector y despeje) van atrás con
# marcador hueco más grande, para que se vean las dos.
VARIANTS = [
    ("despeje", "tab:gray", "o", 11, "none", 1),
    ("predictor-corrector", "black", "o", 5, "black", 2),
    ("predictor Euler", "tab:blue", "s", 6, "tab:blue", 3),
    ("diferencia hacia atrás", "tab:red", "^", 6, "tab:red", 3),
    ("velocidad anterior", "tab:purple", "v", 6, "tab:purple", 3),
]


def style():
    plt.rcParams.update({
        "font.family": "STIXGeneral",
        "mathtext.fontset": "stix",
        "font.size": 14,
        "axes.labelsize": 15,
        "legend.fontsize": 12,
        "xtick.labelsize": 13,
        "ytick.labelsize": 13,
        "figure.figsize": (7.0, 4.8),
        "figure.constrained_layout.use": True,
        "lines.linewidth": 1.1,
        "savefig.dpi": 200,
    })


def decade_ticks(ax, axis: str, lo_exp: int, hi_exp: int, step: int):
    ticks = [10.0**e for e in range(lo_exp, hi_exp + 1, step)]
    getattr(ax, f"set_{axis}ticks")(ticks)
    getattr(ax, f"set_{axis}ticklabels")([f"$10^{{{e}}}$" for e in range(lo_exp, hi_exp + 1, step)])
    getattr(ax, f"{axis}axis").set_minor_locator(matplotlib.ticker.NullLocator())


def main():
    style()
    ecm = {name: np.array([verlet(dt, name) for dt in DTS]) for name, *_ in VARIANTS}
    dts = np.array(DTS)

    print("dt (s):", "  ".join(f"{d:.0e}" for d in DTS))
    for name, values in ecm.items():
        slope = np.polyfit(np.log10(dts[2:6]), np.log10(values[2:6]), 1)[0]
        print(f"{name:24s} pendiente(2e-3..2e-4) = {slope:.2f}  ECM:",
              "  ".join(f"{x:.1e}" for x in values))

    fig, ax = plt.subplots()
    for name, color, marker, size, face, z in VARIANTS:
        ax.plot(dts, ecm[name], marker=marker, ms=size, color=color, mfc=face, mec=color,
                label=name, zorder=z)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("Paso temporal (s)")
    ax.set_ylabel("Error cuadrático medio (m²)")
    decade_ticks(ax, "x", -5, -2, 1)
    decade_ticks(ax, "y", -18, -3, 3)
    ax.set_ylim(1e-19, 1e-1)
    ax.legend(loc="best")
    fig.savefig(HERE / "verlet_variantes_ecm.png")
    plt.close(fig)

    fig, ax = plt.subplots()
    ref = ecm["despeje"]
    for name, color, marker, size, face, z in VARIANTS[1:]:
        ax.plot(dts, ecm[name] / ref, marker=marker, ms=size, color=color, mfc=face, mec=color,
                label=name, zorder=z)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("Paso temporal (s)")
    ax.set_ylabel("ECM / ECM con despeje")
    decade_ticks(ax, "x", -5, -2, 1)
    decade_ticks(ax, "y", 0, 8, 2)
    ax.set_ylim(0.5, 3e8)
    ax.legend(loc="best")
    fig.savefig(HERE / "verlet_variantes_cociente.png")
    plt.close(fig)
    print("figuras:", HERE / "verlet_variantes_ecm.png", HERE / "verlet_variantes_cociente.png")


if __name__ == "__main__":
    main()
