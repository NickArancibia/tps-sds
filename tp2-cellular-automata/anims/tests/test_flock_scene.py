"""Tests de la escena que no tocan la GPU: geometría y colores."""

from __future__ import annotations

import numpy as np
import pytest

from anims.scenes.flock import _angle_colors


def test_colors_are_cyclic_in_angle():
    a = _angle_colors(np.array([0.0]))
    b = _angle_colors(np.array([2 * np.pi]))
    np.testing.assert_allclose(a, b, atol=1e-6)


def test_opposite_directions_get_different_colors():
    colors = _angle_colors(np.array([0.0, np.pi]))
    assert not np.allclose(colors[0, :3], colors[1, :3])


def test_colors_are_valid_rgba():
    colors = _angle_colors(np.linspace(-np.pi, np.pi, 64))
    assert colors.shape == (64, 4)
    assert colors.min() >= 0.0 and colors.max() <= 1.0
    assert colors[:, 3] == pytest.approx(1.0)
    # HSV con S=V=1: siempre hay un canal saturado y uno en cero.
    np.testing.assert_allclose(colors[:, :3].max(axis=1), 1.0, atol=1e-6)
    np.testing.assert_allclose(colors[:, :3].min(axis=1), 0.0, atol=1e-6)
