"""Punto 1.2: genera las configuraciones de obstáculos de cada barrido.

Cada barrido varía UNA variable y deja fijo el resto, para poder graficar <t_90> vs variable:

- `single_x`: un obstáculo de radio R = 0.10 m sobre el eje longitudinal (y = W/2), variando la
  posición x del centro. Por simetría alcanza con x ≤ L/2.
- `single_R`: un obstáculo centrado (L/2, W/2), variando el radio R.
- `single_x_R0.20`, `single_x_R0.30`: como `single_x` con R = 0.20 y 0.30 (x ≥ R).
- `mirror_x`: dos obstáculos de R = 0.10 sobre el eje, uno frente a cada arco (x y L − x).
  Variable: x.
- `mirror_R`: dos obstáculos en (L/4, W/2) y (3L/4, W/2), variando el radio común R.
- `grid_K`: K obstáculos de área total fija (la de un círculo de R = 0.10 m), en grilla regular
  cols × rows; R_k = 0.10/√K. Variable: K.
- `funnel`: dos embudos (uno por arco) formados por hileras de obstáculos de R = 0.03 m que van
  desde la pared larga hasta el borde del arco, con separación entre superficies < 2r (las
  partículas no pasan entre ellos). Variable: largo ℓ del embudo en x.
- `funnel_filled`: igual que `funnel`, pero la zona muerta detrás de cada embudo (entre la hilera,
  la pared corta y la pared larga) se rellena con discos hasta que no quepa ninguna partícula:
  en `funnel` las que nacen ahí quedan atrapadas y no hacen gol.
- `funnel_open`: `funnel` sin el disco que llega al arco ni el que pega con la pared larga.
- `funnel_open_dy`: `funnel_open` con ℓ = 0.30, acercando las hileras al eje en dy. Variable: dy.
- `bumps`: un disco tangente a cada pared larga en x = L/2, radio R, cuñas contra la pared
  rellenas. Variable: R.
- `dome`: abombamiento de esquina a esquina sobre cada pared larga (arco por (0,0), (L/2,h),
  (L,0)) relleno de discos; queda una lente libre en el medio. Variable: h.
- `dome_wall`: `dome` más una pared de discos de R = 0.02 en x = L/2 que parte la lente en dos.

Escribe `output/sweeps/<barrido>/<punto>/config.txt` (formato Config.txt: `x y R` por línea) y
`output/sweeps/index.json` con, por punto, el nombre de la variable y su valor.

Uso:  python3 gen_configs.py
"""

from __future__ import annotations

import json
import math

import numpy as np

from common import OUTPUT

L, W, D, R_BALL = 1.20, 0.68, 0.20, 0.0175
SWEEPS = OUTPUT / "sweeps"


def single_x(radius: float = 0.10):
    """Un obstáculo de radio `radius` sobre el eje, variando x del centro (x ≥ radius, x ≤ L/2)."""
    for x in [0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50, 0.55, 0.60]:
        if x >= radius:
            yield f"x{x:.2f}", "Posición x del obstáculo (m)", x, [(x, W / 2, radius)]


def mirror_x():
    """Dos obstáculos de R = 0.10 sobre el eje, uno por arco, en x y L − x (espejo de single_x).
    x ≤ 0.45 para que no se toquen (en x = 0.50 quedarían tangentes)."""
    for x in [0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.45]:
        yield f"x{x:.2f}", "Posición x de cada obstáculo (m)", x, \
            [(x, W / 2, 0.10), (L - x, W / 2, 0.10)]


def mirror_r():
    """Dos obstáculos en (L/4, W/2) y (3L/4, W/2), variando el radio común R. R ≤ 0.30 para que
    entren en la mesa (x − R ≥ 0) y dejen paso (≥ 2r) contra las paredes largas."""
    for r in [0.05, 0.10, 0.15, 0.20, 0.25, 0.30]:
        yield f"R{r:.3f}", "Radio de cada obstáculo (m)", r, \
            [(L / 4, W / 2, r), (3 * L / 4, W / 2, r)]


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
    for length in [0.10, 0.20, 0.30, 0.40]:
        yield f"l{length:.2f}", "Largo del embudo (m)", length, _funnel_arms(length)[0]


def funnel_open():
    """Como `funnel` pero sin el primer disco de cada hilera (el que llega al arco) ni el último
    (el que pega con la pared larga): la zona de atrás del embudo queda abierta por ambos extremos,
    para que las partículas que nacen ahí puedan salir."""
    for length in [0.10, 0.20, 0.30, 0.40]:
        yield f"l{length:.2f}", "Largo del embudo (m)", length, \
            _funnel_arms(length, trim=1)[0]


def funnel_open_dy():
    """`funnel_open` con ℓ = 0.30 fijo, acercando las hileras de arriba y de abajo entre sí: cada
    hilera se desplaza `dy` hacia el eje de la mesa (la de arriba baja, la de abajo sube).
    Variable: dy. Con dy = 0.10 el disco más cercano al arco queda a ~0.04 de la altura del arco
    (frente a él); dy = 0.11 haría que las hileras se toquen."""
    for dy in [0.00, 0.02, 0.04, 0.06, 0.08, 0.10]:
        yield f"dy{dy:.2f}", "Cierre vertical de las hileras (m)", dy, \
            _funnel_arms(0.30, trim=1, dy=dy)[0]


def _funnel_arms(length: float, trim: int = 0, dy: float = 0.0):
    radius, step = 0.03, 0.08          # separación entre superficies 0.02 < 2r = 0.035
    x_near = 0.07                      # deja 0.04 entre obstáculo y pared corta (pasa una partícula)
    y_near = W / 2 + D / 2 + radius + 0.01 - dy
    y_far = W - radius - 0.01 - dy
    arm_len = math.hypot(length, y_far - y_near)
    count = int(math.ceil(arm_len / step)) + 1
    arm = [(x_near + length * s, y_near + (y_far - y_near) * s)
           for s in (i / (count - 1) for i in range(count))]
    arm = arm[trim:len(arm) - trim]
    obs = [(xx, yy, radius) for x, y in arm for xx in (x, L - x) for yy in (y, W - y)]
    return obs, x_near, y_near, y_far


def bumps():
    """Un disco tangente a cada pared larga en x = L/2 (arriba y abajo), de radio R, con las cuñas
    entre disco y pared rellenas (`fill_dead_zone` sobre |x − L/2| ≤ R, hasta la altura del
    centro) para que el perfil sea liso y no queden bolsillos. Variable: R. Los dos discos se
    tocan en R = W/4 = 0.17; con R = 0.16 el paso central queda de 0.04 (> 2r)."""
    for r in [0.05, 0.10, 0.13, 0.16]:
        obs = [(L / 2, r, r), (L / 2, W - r, r)]

        def wedge(xs, ys):
            return (np.abs(xs - L / 2) <= r) & (np.minimum(ys, W - ys) <= r)

        yield f"R{r:.3f}", "Radio de los discos laterales (m)", r, fill_dead_zone(obs, wedge)


def dome(wall: float = 0.0):
    """Un abombamiento sobre cada pared larga que va de esquina a esquina: la región bajo el arco
    de circunferencia que pasa por (0, 0), (L/2, h) y (L, 0) (y su espejo arriba) se rellena con
    discos tangentes al arco desde adentro, hasta que no quepa ninguna partícula. Queda una
    "lente" libre entre ambos abombamientos, ancha en los arcos y de W − 2h en el centro.
    Variable: altura h del pico. h ≤ 0.32 para que el paso central sea ≥ 2r.
    Con `wall` > 0 se agrega una pared de discos de ese radio en x = L/2, entre los dos
    abombamientos (separación entre superficies ≤ r: no pasan partículas), que parte la lente en
    dos mitades, cada una con su arco."""
    for h in [0.10, 0.15, 0.20, 0.25, 0.30]:
        rc = (L * L / 4 + h * h) / (2 * h)       # radio del arco que pasa por los tres puntos

        def depth(xs, ys):
            # distancia al arco, positiva bajo el abombamiento (espejado arriba/abajo)
            return rc - np.hypot(xs - L / 2, np.minimum(ys, W - ys) - (h - rc))

        obs = fill_dead_zone([], lambda xs, ys: depth(xs, ys) > 0, limit=depth)
        if wall:
            obs += _wall(obs, wall)
        yield f"h{h:.2f}", "Altura del abombamiento (m)", h, obs


def _wall(obs: list, radius: float, eps: float = 1e-5) -> list:
    """Columna de discos de radio `radius` en x = L/2 que cubre el hueco libre entre los obstáculos
    de abajo y los de arriba: los discos extremos quedan tangentes (a eps) al obstáculo más
    saliente de cada lado, y los intermedios con separación entre superficies < 2r."""
    lo, hi = radius, W - radius
    for x, y, r in obs:
        dx = abs(x - L / 2)
        if dx < r + radius:
            reach = math.sqrt((r + radius) ** 2 - dx * dx)   # centro de un disco tangente
            if y < W / 2:
                lo = max(lo, y + reach)
            else:
                hi = min(hi, y - reach)
    y0, y1 = lo + eps, hi - eps
    # separación entre superficies < 2r (no pasan partículas) y ≥ 0 (no se solapan)
    count = math.ceil((y1 - y0) / (2 * radius + 2 * R_BALL - 0.005)) + 1
    while count > 2 and (y1 - y0) / (count - 1) < 2 * radius + eps:
        count -= 1
    if (y1 - y0) < 2 * radius + eps:
        return [(L / 2, (y0 + y1) / 2, radius)]
    return [(L / 2, y0 + (y1 - y0) * i / (count - 1), radius) for i in range(count)]


def dome_wall():
    yield from dome(wall=0.02)


def fill_dead_zone(obs: list, inside, limit=None, grid: float = 0.0025,
                   eps: float = 1e-5) -> list:
    """Agrega discos (greedy) hasta que en la región `inside(x, y)` no pueda insertarse ninguna
    partícula: en cada paso se pone un disco tangente en el punto de mayor holgura (distancia al
    obstáculo o pared más cercana) mientras esa holgura sea ≥ r. Si se da `limit(x, y)` (distancia
    al borde de la región), los discos tampoco lo cruzan. Los radios se reducen en eps para que
    las tangencias no se lean como solapamiento tras redondear a 6 decimales."""
    xs, ys = np.meshgrid(np.arange(grid / 2, L, grid), np.arange(grid / 2, W, grid))
    mask = inside(xs, ys)
    px, py = xs[mask], ys[mask]
    clearance = np.minimum.reduce([px, L - px, py, W - py])
    if limit is not None:
        clearance = np.minimum(clearance, limit(px, py))
    for x, y, r in obs:
        clearance = np.minimum(clearance, np.hypot(px - x, py - y) - r)
    added = []
    while True:
        k = int(np.argmax(clearance))
        if clearance[k] < R_BALL + eps:
            return obs + added
        x, y, r = float(px[k]), float(py[k]), float(clearance[k]) - eps
        added.append((x, y, r))
        clearance = np.minimum(clearance, np.hypot(px - x, py - y) - r)


def funnel_filled():
    for length in [0.10, 0.20, 0.30, 0.40]:
        obs, x_near, y_near, y_far = _funnel_arms(length)
        x_far = x_near + length
        slope = (y_far - y_near) / length

        def dead(xs, ys):
            # lado exterior de la hilera (hacia la esquina), reflejado a los 4 cuadrantes
            u = np.minimum(xs, L - xs)
            v = np.maximum(ys, W - ys)
            line = y_near + slope * np.clip(u - x_near, 0.0, length)
            return (u <= x_far) & (v >= line)

        yield f"l{length:.2f}", "Largo del embudo (m)", length, fill_dead_zone(obs, dead)


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
                      ("single_x_R0.20", single_x(0.20)), ("single_x_R0.30", single_x(0.30)),
                      ("mirror_x", mirror_x()), ("mirror_R", mirror_r()),
                      ("grid_K", grid_k()), ("funnel", funnel()),
                      ("funnel_filled", funnel_filled()), ("funnel_open", funnel_open()),
                      ("funnel_open_dy", funnel_open_dy()),
                      ("bumps", bumps()), ("dome", dome()), ("dome_wall", dome_wall()),
                      ("corridor", corridor()),
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
