"""Dibujo del sistema de partículas con una partícula destacada y sus vecinas.

Los vecinos **se leen del output del CIM**; acá no se recalcula nada, sólo se pinta.
"""

from __future__ import annotations

import numpy as np
from matplotlib.collections import PatchCollection
from matplotlib.lines import Line2D
from matplotlib.patches import Circle

from .parsers import Run

COLOR_BASE = "#c7ccd4"       # partículas no involucradas
COLOR_SELECTED = "#d62728"   # partícula elegida
COLOR_NEIGHBOR = "#ff7f0e"   # vecinas de la elegida
COLOR_EDGE = "#3b3f46"


class SystemView:
    """Vista de un sistema de partículas sobre un eje de Matplotlib."""

    def __init__(self, ax, run: Run, show_grid: bool = False, show_links: bool = True):
        self.ax = ax
        self.run = run
        self.show_links = show_links
        self.selected: int | None = None
        self._links: list[Line2D] = []
        self._overlay_patches: list[Circle] = []

        snapshot = run.snapshot
        self.x = snapshot.x
        self.y = snapshot.y

        circles = [Circle((xi, yi), ri) for xi, yi, ri in zip(self.x, self.y, run.radii)]
        self.collection = PatchCollection(circles, linewidths=0.4, edgecolors=COLOR_EDGE)
        self.collection.set_facecolor([COLOR_BASE] * run.n)
        ax.add_collection(self.collection)

        # La grilla se construye siempre (si se conoce M) y se muestra u oculta con toggle_grid().
        self._grid_lines: list[Line2D] = []
        if run.m:
            for k in range(run.m + 1):
                pos = k * run.l / run.m
                self._grid_lines.append(
                    ax.axvline(pos, color="#9aa1ab", lw=0.4, ls=":", zorder=0, visible=show_grid))
                self._grid_lines.append(
                    ax.axhline(pos, color="#9aa1ab", lw=0.4, ls=":", zorder=0, visible=show_grid))

        ax.set_xlim(0, run.l)
        ax.set_ylim(0, run.l)
        ax.set_aspect("equal")
        ax.set_xlabel("x")
        ax.set_ylabel("y")
        for spine in ax.spines.values():
            spine.set_edgecolor(COLOR_EDGE)

    def toggle_grid(self) -> None:
        """Muestra u oculta la grilla de MxM celdas del CIM."""
        for line in self._grid_lines:
            line.set_visible(not line.get_visible())

    # ------------------------------------------------------------------ selección

    def particle_at(self, px: float, py: float) -> int | None:
        """Índice de la partícula bajo el punto (px, py), o la más cercana si está a menos de rc/2."""
        dx = self.x - px
        dy = self.y - py
        if self.run.periodic:
            dx -= self.run.l * np.round(dx / self.run.l)
            dy -= self.run.l * np.round(dy / self.run.l)
        distances = np.hypot(dx, dy)
        index = int(np.argmin(distances))
        tolerance = max(self.run.radii[index], (self.run.rc or 1.0) / 2)
        return index if distances[index] <= tolerance else None

    def select(self, index: int | None) -> None:
        """Colorea la partícula elegida y sus vecinas (leídas del archivo de vecinos)."""
        self.selected = index
        colors = [COLOR_BASE] * self.run.n
        self._clear_overlays()

        if index is not None:
            for neighbor in self.run.neighbors[index]:
                colors[neighbor] = COLOR_NEIGHBOR
            colors[index] = COLOR_SELECTED
            self._draw_overlays(index)

        self.collection.set_facecolor(colors)

    def _draw_overlays(self, index: int) -> None:
        rc = self.run.rc or 0.0
        reach = self.run.radii[index] + rc
        l = self.run.l

        # Radio de referencia: alcance de interacción medido desde el borde de la elegida.
        #
        # Con contorno periódico la partícula "existe" también en las 8 imágenes que rodean al
        # dominio, así que se dibuja el alcance de cada imagen que asome dentro del área. Eso es lo
        # que explica que una vecina del borde opuesto (o de la esquina opuesta) esté a menos de rc.
        offsets = [(0.0, 0.0)]
        if self.run.periodic:
            offsets = [(dx * l, dy * l) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]

        for ox, oy in offsets:
            cx = self.x[index] + ox
            cy = self.y[index] + oy
            # Sólo las imágenes cuyo alcance interseca el área visible.
            if cx + reach < 0 or cx - reach > l or cy + reach < 0 or cy - reach > l:
                continue
            is_original = ox == 0.0 and oy == 0.0
            circle = Circle((cx, cy), reach, fill=False, ls="--", lw=0.9, ec=COLOR_SELECTED,
                            alpha=0.7 if is_original else 0.45, zorder=3)
            circle.set_clip_path(self.ax.patch)
            self.ax.add_patch(circle)
            self._overlay_patches.append(circle)

            if not is_original:
                # Fantasma de la partícula elegida en su imagen periódica.
                ghost = Circle((cx, cy), self.run.radii[index], fc=COLOR_SELECTED, ec=COLOR_EDGE,
                               lw=0.4, alpha=0.35, zorder=3)
                ghost.set_clip_path(self.ax.patch)
                self.ax.add_patch(ghost)
                self._overlay_patches.append(ghost)

        if not self.show_links:
            return

        # Con contorno periódico los segmentos se dibujan hacia la imagen mínima, así que salen del
        # área y quedan recortados por el borde: eso muestra visualmente el "wrap around".
        for neighbor in self.run.neighbors[index]:
            dx = self.x[neighbor] - self.x[index]
            dy = self.y[neighbor] - self.y[index]
            if self.run.periodic:
                dx -= self.run.l * round(dx / self.run.l)
                dy -= self.run.l * round(dy / self.run.l)
            line = Line2D([self.x[index], self.x[index] + dx],
                          [self.y[index], self.y[index] + dy],
                          lw=0.6, color=COLOR_NEIGHBOR, alpha=0.65, zorder=2)
            line.set_clip_path(self.ax.patch)
            self.ax.add_line(line)
            self._links.append(line)

    def _clear_overlays(self) -> None:
        for line in self._links:
            line.remove()
        self._links.clear()
        for patch in self._overlay_patches:
            patch.remove()
        self._overlay_patches.clear()


def run_title(run: Run) -> str:
    meta = run.meta
    return (f"N={run.n}  L={run.l:g}  M={meta.get('M', '?')}  rc={meta.get('rc', '?')}  "
            f"{'con' if run.periodic else 'sin'} contorno periódico")


def add_legend(ax):
    """Coloca la leyenda por fuera del área de dibujo, para no tapar partículas."""
    return ax.legend(handles=legend_handles(), loc="upper left", bbox_to_anchor=(1.02, 1.0),
                     fontsize=9, frameon=False, borderaxespad=0.0)


def legend_handles():
    return [
        Line2D([], [], marker="o", ls="", mfc=COLOR_SELECTED, mec=COLOR_EDGE, label="elegida"),
        Line2D([], [], marker="o", ls="", mfc=COLOR_NEIGHBOR, mec=COLOR_EDGE, label="vecinas"),
        Line2D([], [], marker="o", ls="", mfc=COLOR_BASE, mec=COLOR_EDGE, label="resto"),
        # El criterio es borde a borde: una vecina puede tener su centro fuera de este círculo
        # (que mide rc desde el borde de la elegida) y aun así estar a menos de rc de distancia.
        Line2D([], [], ls="--", lw=0.9, color=COLOR_SELECTED, alpha=0.7,
               label="alcance rc desde el borde"),
    ]
