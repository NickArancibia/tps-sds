"""Tests del encoder: frames sintéticos → mp4 → releer. No necesitan GPU."""

from __future__ import annotations

import numpy as np
import pytest

from anims.writer import VideoWriter

imageio_ffmpeg = pytest.importorskip("imageio_ffmpeg")

SIZE = (64, 48)  # ancho, alto
FRAMES = 10


def synthetic_frame(i: int) -> np.ndarray:
    frame = np.zeros((SIZE[1], SIZE[0], 3), dtype=np.uint8)
    frame[:, :, i % 3] = 10 * i
    return frame


def test_writes_readable_mp4(tmp_path):
    out = tmp_path / "sub" / "anim.mp4"
    with VideoWriter(out, size=SIZE, fps=15) as writer:
        for i in range(FRAMES):
            writer.append(synthetic_frame(i))

    assert out.is_file() and out.stat().st_size > 0

    reader = imageio_ffmpeg.read_frames(str(out))
    meta = reader.send(None)
    assert tuple(meta["size"]) == SIZE
    assert sum(1 for _ in reader) == FRAMES


def test_rejects_frame_with_wrong_size(tmp_path):
    with VideoWriter(tmp_path / "anim.mp4", size=SIZE) as writer:
        with pytest.raises(ValueError, match="video"):
            writer.append(np.zeros((10, 10, 3), dtype=np.uint8))


def test_close_is_idempotent(tmp_path):
    writer = VideoWriter(tmp_path / "anim.mp4", size=SIZE)
    writer.append(synthetic_frame(0))
    writer.close()
    writer.close()
