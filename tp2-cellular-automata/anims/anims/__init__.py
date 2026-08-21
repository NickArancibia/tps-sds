"""Animaciones GPU de corridas de simulación (formato de cátedra static/dynamic).

El paquete es agnóstico del TP: `run`, `canvas` y `writer` solo conocen el formato de archivos
común a todos los TPs. Lo específico de cada TP vive en `anims.scenes`.
"""

__all__ = ["Run", "load_run"]


def __getattr__(name: str):  # pragma: no cover - reexport perezoso
    if name in __all__:
        from anims.run import Run, load_run

        return {"Run": Run, "load_run": load_run}[name]
    raise AttributeError(name)
