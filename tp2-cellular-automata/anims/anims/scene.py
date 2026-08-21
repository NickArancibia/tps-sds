"""Punto de extensión: una escena decide *qué* se dibuja para un TP dado.

El canvas, el loader y el writer son agnósticos del TP; una animación para otro TP es un archivo
nuevo en `anims/scenes/` que implemente este protocolo.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:  # pragma: no cover - solo para tipos
    from vispy.scene import ViewBox

    from anims.run import Run


@runtime_checkable
class Scene(Protocol):
    """Contrato de una escena."""

    def build(self, view: "ViewBox", run: "Run") -> None:
        """Crea los visuals una única vez."""

    def update(self, i: int) -> list[str]:
        """Reescribe los buffers para el frame `i` y devuelve las líneas del HUD.

        Nunca debe recrear visuals: eso mataría el rendimiento.
        """
