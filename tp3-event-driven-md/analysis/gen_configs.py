"""Punto 1.2: genera las configuraciones de obstáculos de cada barrido.

Cada barrido varía UNA variable y deja fijo el resto, para poder graficar <t_90> vs variable.
Solo las familias que aparecen en la presentación (el resto de las exploradas —single_x,
mirror, grid, funnel, bumps, dome, barrier, corridor_smooth, c_gate— se descartaron; ver
AGENTS.md §5 para lo que dieron):

- `corridor`: mesa rellena con discos grandes salvo un corredor central de altura h alineado
  con los arcos. Variable: h.
- `single_R`: un obstáculo centrado (L/2, W/2), variando el radio R.
- `multi_barrier`: bloque de k columnas contiguas de discos R = 0.02 centrado en L/2 (come área
  del medio sin partir la mesa en más de dos mitades). Variable: k.
- `multi_barrier_rows_k`: `multi_barrier` más n filas horizontales de discos R = 0.02 pegadas a
  cada pared larga en cada compartimento; grilla k = 14..17 × n = 1..4 (k alrededor del mínimo
  de `multi_barrier`; n = 5 nunca deja ubicar las 100 partículas).

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


def single_r():
    # R ≥ 0.3225 deja menos de 2r entre el obstáculo y las paredes largas: la mesa queda partida
    # en dos mitades, cada una con su arco.
    for r in [0.025, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.32, 0.33]:
        yield f"R{r:.3f}", "Radio del obstáculo (m)", r, [(L / 2, W / 2, r)]


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
        corner = radius * (3 - 2 * math.sqrt(2))   # círculo tangente a 2 paredes y al disco
        if corner >= R_BALL:
            for x in (corner, L - corner):
                for y in (corner, W - corner):
                    obs.append((x, y, corner - eps))
        yield f"h{h:.3f}", "Altura del corredor (m)", h, obs


def _barrier_at(x0: float, radius: float) -> list:
    """Columna de discos de radio `radius` en x = x0 que cubre todo W con separación entre
    superficies < 2r (las partículas no pasan)."""
    count = math.ceil((W - 2 * radius) / (2 * radius + R_BALL)) + 1
    return [(x0, radius + (W - 2 * radius) * i / (count - 1), radius) for i in range(count)]


def _block(k: int, radius: float = 0.02, eps: float = 1e-4) -> list:
    """Bloque de k columnas `_barrier_at` pegadas (separación entre centros 2R + eps, evita
    solapar por redondeo) centrado en x = L/2."""
    step = 2 * radius + eps
    return [pt for i in range(k) for pt in _barrier_at(L / 2 + (i - (k - 1) / 2) * step, radius)]


def multi_barrier():
    """Bloque de k columnas contiguas de discos R = 0.02 centrado en L/2: come más área del medio
    a medida que crece k, pero sigue partiendo la mesa en solo dos mitades (cada una con su arco).
    Variable: cantidad de columnas k."""
    for k in range(1, 23):           # k = 23 ya no deja lugar para ubicar las 100 partículas
        yield f"k{k:02d}", "Cantidad de columnas pegadas", k, _block(k)


def _rows_block(k: int, n: int) -> list:
    """`multi_barrier` (bloque de k columnas) más n filas horizontales de discos del mismo radio
    que las columnas (R = 0.02) en cada compartimento libre, apiladas desde cada pared larga hacia
    el centro (sin diagonal). Arrancan pegadas a la pared corta (x = radio) y se reparten parejo
    hasta pegar con el bloque, así que ocupan todo el largo disponible en x."""
    radius, eps = 0.02, 1e-4
    step = 2 * radius + eps
    block_half = (k - 1) * step / 2 + radius
    x1 = L / 2 - block_half                       # borde interno del compartimento izquierdo

    span = (x1 - radius - eps) - radius        # centros: de `radius` a pegado al bloque
    ncols = int(span / step) + 1               # piso: separación >= step, nunca se solapan
    leftover = span - (ncols - 1) * step        # < step; se reparte a ambos lados para centrar
    xs = [radius + leftover / 2 + i * step for i in range(ncols)]

    obs = _block(k, radius, eps)
    for j in range(n):
        y_bottom = radius + j * step
        y_top = W - radius - j * step
        for x in xs:
            obs += [(x, y_bottom, radius), (x, y_top, radius),
                    (L - x, y_bottom, radius), (L - x, y_top, radius)]
    return obs


def multi_barrier_rows_k():
    """`_rows_block` variando el tamaño k del bloque (14..17, alrededor del mínimo de
    `multi_barrier`) y la cantidad de filas n por lado (1..4): grilla k × n, 16 configuraciones
    (k = 17, n = 4 casi nunca deja ubicar las 100 partículas; se genera igual y
    `run_sweeps`/`plot_t90` la cuenta como no generada)."""
    for k in range(14, 18):
        for n in range(1, 5):
            yield f"k{k:02d}_n{n:02d}", "Columnas k / filas n", (k, n), _rows_block(k, n)


def main() -> None:
    index = {}
    for name, gen in [("corridor", corridor()), ("single_R", single_r()),
                      ("multi_barrier", multi_barrier()),
                      ("multi_barrier_rows_k", multi_barrier_rows_k())]:
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
