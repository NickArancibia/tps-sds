"""Escenas: lo específico de cada TP. Una animación nueva es un archivo nuevo acá."""

from __future__ import annotations


def get_scene(name: str):
    """Devuelve la clase de escena registrada bajo `name`."""
    if name == "flock":
        from anims.scenes.flock import FlockScene

        return FlockScene
    raise ValueError(f"escena desconocida: {name!r} (disponibles: {', '.join(SCENES)})")


SCENES = ("flock",)
