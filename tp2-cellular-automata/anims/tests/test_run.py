"""Tests del loader. No necesitan GPU."""

from __future__ import annotations

import os
from pathlib import Path

import numpy as np
import pytest

from anims.run import CACHE_NAME, load_run

N = 3
L = 10.0
FRAMES = [
    (0.0, [(1.0, 2.0, 0.03, 0.0), (3.0, 4.0, 0.0, 0.03), (5.0, 6.0, -0.03, 0.0)]),
    (1.0, [(1.03, 2.0, 0.03, 0.0), (3.0, 4.03, 0.0, 0.03), (4.97, 6.0, -0.03, 0.0)]),
]


def write_run(path: Path, *, observables: bool = True, meta: bool = True) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    static = [str(N), f"{L:.6f}"] + ["0.000000 #1f77b4"] * N
    (path / "static.txt").write_text("\n".join(static) + "\n")

    dynamic = []
    for t, particles in FRAMES:
        dynamic.append(f"{t:.6f}")
        dynamic += [" ".join(f"{c:.6f}" for c in p) for p in particles]
    (path / "dynamic.txt").write_text("\n".join(dynamic) + "\n")

    if observables:
        (path / "observables.csv").write_text(
            "time,polarization,largest_cluster_fraction\n"
            "0.000000,0.500000,0.333333\n"
            "1.000000,0.800000,0.666667\n"
        )
    if meta:
        (path / "run.json").write_text('{"model": "vicsek", "N": 3, "eta": 0.5, "rc": 1.0}\n')
    return path


def test_parses_shape_times_and_values(tmp_path):
    run = load_run(write_run(tmp_path / "run"))

    assert run.n == N
    assert run.l == pytest.approx(L)
    assert run.state.shape == (2, N, 4)
    assert run.frames == 2
    np.testing.assert_allclose(run.times, [0.0, 1.0])
    np.testing.assert_allclose(run.state[0, 0], [1.0, 2.0, 0.03, 0.0], rtol=1e-6)
    np.testing.assert_allclose(run.state[1, 2], [4.97, 6.0, -0.03, 0.0], rtol=1e-6)


def test_reads_meta_and_observables(tmp_path):
    run = load_run(write_run(tmp_path / "run"))

    assert run.meta["model"] == "vicsek"
    assert set(run.observables) == {"time", "polarization", "largest_cluster_fraction"}
    assert run.observable_at(1)["polarization"] == pytest.approx(0.8)


def test_degrades_without_observables(tmp_path):
    run = load_run(write_run(tmp_path / "run", observables=False))

    assert run.observables is None
    assert run.observable_at(0) == {}


def test_degrades_without_meta(tmp_path):
    run = load_run(write_run(tmp_path / "run", meta=False))

    assert run.meta == {}


def test_observables_indexed_by_time_not_position(tmp_path):
    """`dynamic.txt` guarda un bloque cada `outputEvery` pasos; el CSV, uno por paso."""
    path = write_run(tmp_path / "run")
    (path / "observables.csv").write_text(
        "time,polarization,largest_cluster_fraction\n"
        + "".join(f"{t:.6f},{t / 10:.6f},0.5\n" for t in range(6))
    )
    (path / "dynamic.txt").write_text(
        "0.000000\n" + "".join("0 0 0 0\n" for _ in range(N))
        + "5.000000\n" + "".join("0 0 0 0\n" for _ in range(N))
    )
    run = load_run(path, use_cache=False)

    assert run.observable_at(1)["polarization"] == pytest.approx(0.5)


def test_cache_round_trip_and_mtime_invalidation(tmp_path):
    path = write_run(tmp_path / "run")
    first = load_run(path)
    assert (path / CACHE_NAME).is_file()

    cached = load_run(path)
    np.testing.assert_allclose(cached.state, first.state)
    np.testing.assert_allclose(cached.times, first.times)

    dynamic = path / "dynamic.txt"
    dynamic.write_text("7.000000\n" + "".join("1 1 0 0\n" for _ in range(N)))
    os.utime(dynamic, ns=(dynamic.stat().st_atime_ns, dynamic.stat().st_mtime_ns + 10**9))

    refreshed = load_run(path)
    assert refreshed.frames == 1
    np.testing.assert_allclose(refreshed.times, [7.0])


def test_rejects_inconsistent_n(tmp_path):
    path = write_run(tmp_path / "run")
    (path / "static.txt").write_text("7\n10.000000\n" + "0.000000 #1f77b4\n" * 7)

    with pytest.raises(ValueError, match="múltiplo del bloque"):
        load_run(path, use_cache=False)


def test_missing_files(tmp_path):
    (tmp_path / "vacio").mkdir()
    with pytest.raises(FileNotFoundError):
        load_run(tmp_path / "vacio")
