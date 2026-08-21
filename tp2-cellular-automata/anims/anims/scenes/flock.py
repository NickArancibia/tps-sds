"""Escena del TP2: bandadas de Vicsek / votante.

Cada partícula es un segmento con la punta en su dirección de movimiento. Todas se dibujan con un
único visual `Line` con `connect='segments'` (2 vértices por partícula): una sola llamada de dibujo
para las N partículas, sin ningún bucle por partícula en Python.

El color es cíclico en el ángulo (mapa HSV): cuando la bandada se ordena el campo vira a un color
uniforme, y el orden se lee de un vistazo.
"""

from __future__ import annotations

import numpy as np

from anims.run import Run

#: Largo de la flecha como fracción de `rc` (escala de interacción, no del dominio); por eso el
#: artefacto de los segmentos que cruzan el borde es despreciable y no se dibuja la imagen
#: periódica.
ARROW_FRACTION = 0.45


class FlockScene:
    """Campo de velocidades de la bandada."""

    name = "flock"

    def __init__(self, *, arrow_fraction: float = ARROW_FRACTION) -> None:
        self.arrow_fraction = arrow_fraction
        self.run: Run | None = None
        self._line = None
        self._pos: np.ndarray | None = None
        self._arrow: float = 0.0

    def build(self, view, run: Run) -> None:
        from vispy import scene as vispy_scene

        self.run = run
        rc = float(run.meta.get("rc", 1.0) or 1.0)
        self._arrow = self.arrow_fraction * rc
        self._pos = np.zeros((2 * run.n, 2), dtype=np.float32)
        self._line = vispy_scene.visuals.Line(
            pos=self._pos, color=np.ones((2 * run.n, 4), dtype=np.float32),
            connect="segments", width=1.5, antialias=True, parent=view.scene,
        )
        self.update(0)

    def update(self, i: int) -> list[str]:
        run, line, pos = self.run, self._line, self._pos
        if run is None or line is None or pos is None:
            raise RuntimeError("build() no fue llamado antes de update()")

        frame = run.state[i]
        xy, v = frame[:, 0:2], frame[:, 2:4]
        speed = np.hypot(v[:, 0], v[:, 1])
        direction = np.divide(v, np.where(speed > 0, speed, 1.0)[:, None])

        pos[0::2] = xy
        pos[1::2] = xy + direction * self._arrow
        colors = _angle_colors(np.arctan2(v[:, 1], v[:, 0]))
        line.set_data(pos=pos, color=np.repeat(colors, 2, axis=0))
        return self._hud(i)

    def _hud(self, i: int) -> list[str]:
        run = self.run
        assert run is not None
        lines = [f"t = {run.times[i]:.1f}"]
        eta = run.meta.get("eta")
        if eta is not None:
            model = run.meta.get("model", "")
            lines.append(f"η = {float(eta):.2f}" + (f"   ({model})" if model else ""))
        if run.meta.get("N") is not None:
            lines.append(f"N = {int(run.meta['N'])}   ρ = {float(run.meta.get('density', 0)):.0f}")
        obs = run.observable_at(i)
        if "polarization" in obs:
            lines.append(f"v_a = {obs['polarization']:.3f}")
        if "largest_cluster_fraction" in obs:
            lines.append(f"S = {obs['largest_cluster_fraction']:.3f}")
        return lines


def _angle_colors(theta: np.ndarray) -> np.ndarray:
    """Mapa cíclico HSV: hue = ángulo, saturación y valor plenos. Devuelve RGBA float32."""
    h = (theta / (2.0 * np.pi)) % 1.0
    k = (h * 6.0)
    f = k - np.floor(k)
    sector = np.floor(k).astype(np.int32) % 6
    p, q, t = np.zeros_like(f), 1.0 - f, f
    ones = np.ones_like(f)
    r = np.choose(sector, [ones, q, p, p, t, ones])
    g = np.choose(sector, [t, ones, ones, q, p, p])
    b = np.choose(sector, [p, p, t, ones, ones, q])
    rgba = np.empty((theta.size, 4), dtype=np.float32)
    rgba[:, 0], rgba[:, 1], rgba[:, 2], rgba[:, 3] = r, g, b, 1.0
    return rgba
