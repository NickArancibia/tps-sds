"""SceneCanvas de VisPy: cámara fijada al dominio PBC, borde de la caja y HUD.

Agnóstico del TP: solo sabe que hay un dominio cuadrado `[0, L]²` y que la escena le devuelve
líneas de texto para el overlay, así que el formato del HUD no se duplica en cada escena futura.
"""

from __future__ import annotations

import numpy as np

BACKGROUND = "#0d1117"
BOX_COLOR = "#8b949e"
HUD_COLOR = "#e6edf3"
#: El HUD se escala con la altura del canvas para que 720p y 1080p se vean igual.
HUD_FONT_FRACTION = 0.014
HUD_LINE_SPACING = 3.2
HUD_MAX_LINES = 8


def _import_vispy():
    try:
        from vispy import scene
    except ImportError as exc:  # pragma: no cover - depende del entorno
        raise RuntimeError(
            "falta VisPy. Instalar con: pip install -r requirements.txt"
        ) from exc
    return scene


class AnimCanvas:
    """Canvas offscreen (`show=False`) o visible, según el modo."""

    def __init__(self, l: float, size: tuple[int, int] = (1280, 720), *, show: bool = False,
                 hud: bool = True, title: str = "anims") -> None:
        scene = _import_vispy()
        try:
            self.canvas = scene.SceneCanvas(
                keys="interactive", size=size, show=show, bgcolor=BACKGROUND, title=title
            )
        except Exception as exc:  # pragma: no cover - depende del entorno
            raise RuntimeError(
                "no se pudo crear un contexto OpenGL. En Windows suele faltar el backend de "
                "ventanas: pip install PyQt5 (ver requirements.txt). Detalle: %s" % exc
            ) from exc

        self.size = size
        self.l = float(l)
        self.view = self.canvas.central_widget.add_view()
        margin = 0.06 * self.l
        self.view.camera = scene.PanZoomCamera(
            rect=(-margin, -margin, self.l + 2 * margin, self.l + 2 * margin), aspect=1
        )
        self.view.camera.interactive = show

        corners = np.array(
            [[0, 0], [self.l, 0], [self.l, self.l], [0, self.l], [0, 0]], dtype=np.float32
        )
        scene.visuals.Line(pos=corners, color=BOX_COLOR, width=1.5, parent=self.view.scene)

        # Una línea = un visual: el Text de VisPy no maneja el salto de línea, y así el HUD se
        # actualiza reescribiendo strings en visuals ya creados.
        self._hud_lines = []
        if hud:
            font_size = HUD_FONT_FRACTION * size[1]
            line_height = HUD_LINE_SPACING * font_size
            for k in range(HUD_MAX_LINES):
                self._hud_lines.append(scene.visuals.Text(
                    "", color=HUD_COLOR, font_size=font_size, anchor_x="left",
                    anchor_y="top", pos=(line_height, line_height * (k + 1)),
                    parent=self.canvas.scene,
                ))

    def set_hud(self, lines: list[str]) -> None:
        """Reescribe el overlay con las líneas que devolvió la escena."""
        for k, visual in enumerate(self._hud_lines):
            visual.text = lines[k] if k < len(lines) else ""

    def render(self) -> np.ndarray:
        """Frame actual como `(H, W, 3)` uint8."""
        frame = self.canvas.render(alpha=False)
        return np.ascontiguousarray(frame[:, :, :3], dtype=np.uint8)

    def close(self) -> None:
        self.canvas.close()
