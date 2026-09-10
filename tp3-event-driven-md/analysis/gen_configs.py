"""Punto 1.2: genera las configuraciones de obstáculos de cada barrido.

Cada barrido varía UNA variable y deja fijo el resto, para poder graficar <t_90> vs variable:

- `single_x`: un obstáculo de radio R = 0.10 m sobre el eje longitudinal (y = W/2), variando la
  posición x del centro. Por simetría alcanza con x ≤ L/2.
- `single_R`: un obstáculo centrado (L/2, W/2), variando el radio R.
- `grid_K`: K obstáculos de área total fija (la de un círculo de R = 0.10 m), en grilla regular
  cols × rows; R_k = 0.10/√K. Variable: K.
- `funnel`: dos embudos (uno por arco) formados por hileras de obstáculos de R = 0.03 m que van
  desde la pared larga hasta el borde del arco, con separación entre superficies < 2r (las
  partículas no pasan entre ellos). Variable: largo ℓ del embudo en x.

Escribe `output/sweeps/<barrido>/<punto>/config.txt` (formato Config.txt: `x y R` por línea) y
`output/sweeps/index.json` con, por punto, el nombre de la variable y su valor.

Uso:  python3 gen_configs.py
"""

from __future__ import annotations

import json
import math

from common import OUTPUT

L, W, D, R_BALL = 1.20, 0.68, 0.20, 0.0175
SWEEPS = OUTPUT / "sweeps"


def single_x():
    for x in [0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50, 0.55, 0.60]:
        yield f"x{x:.2f}", "Posición x del obstáculo (m)", x, [(x, W / 2, 0.10)]


def single_r():
    # R ≥ 0.3225 deja menos de 2r entre el obstáculo y las paredes largas: la mesa queda partida
    # en dos mitades, cada una con su arco.
    for r in [0.025, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.32, 0.33]:
        yield f"R{r:.3f}", "Radio del obstáculo (m)", r, [(L / 2, W / 2, r)]


def grid_k():
    layouts = {1: (1, 1), 2: (2, 1), 4: (2, 2), 6: (3, 2), 8: (4, 2), 12: (4, 3), 16: (4, 4)}
    for k, (cols, rows) in layouts.items():
        radius = 0.10 / math.sqrt(k)
        obs = [(L * (i + 0.5) / cols, W * (j + 0.5) / rows, radius)
               for i in range(cols) for j in range(rows)]
        yield f"K{k:02d}", "Cantidad de obstáculos K", k, obs


def funnel():
    radius, step = 0.03, 0.08          # separación entre superficies 0.02 < 2r = 0.035
    x_near = 0.07                      # deja 0.04 entre obstáculo y pared corta (pasa una partícula)
    y_near = W / 2 + D / 2 + radius + 0.01
    y_far = W - radius - 0.01
    for length in [0.10, 0.20, 0.30, 0.40]:
        arm_len = math.hypot(length, y_far - y_near)
        count = int(math.ceil(arm_len / step)) + 1
        arm = [(x_near + length * s, y_near + (y_far - y_near) * s)
               for s in (i / (count - 1) for i in range(count))]
        obs = []
        for x, y in arm:
            for xx in (x, L - x):
                for yy in (y, W - y):
                    obs.append((xx, yy, radius))
        yield f"l{length:.2f}", "Largo del embudo (m)", length, obs


def corridor():
    """Mesa rellena con discos grandes salvo un corredor central de altura h alineado con los
    arcos (idea: t_90 ∝ área libre). Cada banda lateral, de altura (W − h)/2, se llena con una
    fila de n discos de radio R = (W − h)/4 tangentes entre sí, a la pared larga y al borde del
    corredor; se elige h = W − 2L/n para que la fila cubra L exacto. Los huecos que quedan del
    lado de la pared (entre dos discos tangentes y la pared: cabe un círculo de radio R/4; en la
    esquina: R(3 − 2√2)) son bolsillos aislados: una partícula que naciera ahí no haría gol
    nunca. Se rellenan con discos menores hasta que el mayor círculo inscripto en cada hueco
    residual sea menor que r (no puede insertarse ninguna partícula). Los radios se reducen en
    EPS para que las tangencias no se lean como solapamiento tras redondear a 6 decimales."""
    yield from _corridor(smooth=False)


def corridor_smooth():
    """Como `corridor`, pero además rellena los huecos del lado del corredor (entre dos discos
    tangentes) con discos de R/4, para que el borde del corredor no tenga cuñas donde las
    trayectorias quedan rebotando muchas veces (atrapamiento en cúspides)."""
    yield from _corridor(smooth=True)


def _corridor(smooth: bool):
    eps = 1e-4
    for n in [5, 6, 7, 8]:
        h = W - 2 * L / n
        radius = (W - h) / 4
        obs = []
        for i in range(n):
            x = radius * (2 * i + 1)
            obs += [(x, radius, radius - eps), (x, W - radius, radius - eps)]
        cusp = radius / 4                     # Descartes: dos círculos R tangentes + recta
        assert radius / 9 < R_BALL, "el sub-hueco (R/9) admitiría una partícula"
        if cusp >= R_BALL:
            for i in range(1, n):
                x = 2 * radius * i
                obs += [(x, cusp, cusp - eps), (x, W - cusp, cusp - eps)]
                if smooth:
                    y = 2 * radius - cusp     # tangente a los dos discos, del lado del corredor
                    obs += [(x, y, cusp - eps), (x, W - y, cusp - eps)]
        corner = radius * (3 - 2 * math.sqrt(2))   # círculo tangente a 2 paredes y al disco
        if corner >= R_BALL:
            for x in (corner, L - corner):
                for y in (corner, W - corner):
                    obs.append((x, y, corner - eps))
        yield f"h{h:.3f}", "Altura del corredor (m)", h, obs


def barrier():
    """Test de hipótesis: partir la mesa en dos mitades con una barrera de discos chicos en
    x = L/2 (separación entre superficies r < 2r: no pasan partículas) casi sin quitar área. Si
    <t_90> ≈ disco R = 0.33, lo que importa es la partición; si ≈ mesa vacía, es el área quitada.
    Variable: radio de los discos de la barrera (a mayor R, más área quitada)."""
    for radius in [0.02, 0.03, 0.05]:
        count = math.ceil((W - 2 * radius) / (2 * radius + R_BALL)) + 1
        ys = [radius + (W - 2 * radius) * i / (count - 1) for i in range(count)]
        yield f"R{radius:.3f}", "Radio de los discos de la barrera (m)", radius, \
            [(L / 2, y, radius) for y in ys]


def main() -> None:
    index = {}
    for name, gen in [("single_x", single_x()), ("single_R", single_r()),
                      ("grid_K", grid_k()), ("funnel", funnel()), ("corridor", corridor()),
                      ("corridor_smooth", corridor_smooth()), ("barrier", barrier())]:
        index[name] = []
        for label, var_name, value, obs in gen:
            path = SWEEPS / name / label
            path.mkdir(parents=True, exist_ok=True)
            with open(path / "config.txt", "w") as fh:
                fh.writelines(f"{x:.6f} {y:.6f} {r:.6f}\n" for x, y, r in obs)
            index[name].append({"label": label, "variable": var_name, "value": value,
                                "K": len(obs), "config": str(path / "config.txt")})
            print(f"  {name}/{label}: K = {len(obs)}")
    with open(SWEEPS / "index.json", "w") as fh:
        json.dump(index, fh, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    main()
