"""Encode de frames uint8 a MP4 vía el ffmpeg que trae `imageio-ffmpeg` en el wheel.

Depender del binario del wheel evita que en Windows haya que tener ffmpeg instalado y en el PATH.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np


class VideoWriter:
    """Pipe a ffmpeg. H.264 + `yuv420p`, que reproduce en cualquier lado (PowerPoint incluido)."""

    def __init__(self, path: str | Path, size: tuple[int, int], fps: int = 30,
                 quality: int = 8) -> None:
        try:
            import imageio_ffmpeg
        except ImportError as exc:  # pragma: no cover - depende del entorno
            raise RuntimeError(
                "falta imageio-ffmpeg. Instalar con: pip install -r requirements.txt"
            ) from exc

        self.path = Path(path)
        self.size = (int(size[0]), int(size[1]))
        self.fps = int(fps)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._writer = imageio_ffmpeg.write_frames(
            str(self.path),
            self.size,
            fps=self.fps,
            pix_fmt_in="rgb24",
            pix_fmt_out="yuv420p",
            codec="libx264",
            quality=quality,
            macro_block_size=1,
        )
        self._writer.send(None)  # arranca el generador y abre el proceso
        self._closed = False

    def append(self, frame: np.ndarray) -> None:
        """Agrega un frame `(H, W, 3)` uint8."""
        height, width = self.size[1], self.size[0]
        if frame.shape[:2] != (height, width):
            raise ValueError(
                f"el frame es {frame.shape[1]}x{frame.shape[0]} y el video {width}x{height}"
            )
        rgb = np.ascontiguousarray(frame[:, :, :3], dtype=np.uint8)
        self._writer.send(rgb)

    def close(self) -> None:
        if not self._closed:
            self._closed = True
            self._writer.close()

    def __enter__(self) -> "VideoWriter":
        return self

    def __exit__(self, *_exc) -> None:
        self.close()
