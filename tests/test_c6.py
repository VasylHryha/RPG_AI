"""C6 step 1: fixed random fixtures only, never experiment worlds/entropy."""

from dataclasses import replace
import hashlib
import inspect
import json
from pathlib import Path
import subprocess
import sys
import time

import numpy as np
import pytest

from geomind import c4_model as reference
from geomind import c6_native as native
from tools import build_c6


ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module", autouse=True)
def kernel_and_measurements(request):
    if not native.LIBRARY.exists():
        subprocess.run([sys.executable, str(ROOT / "tools/build_c6.py")], check=True)
    record = json.loads((ROOT / "build/c6/BUILD.json").read_text())
    assert record["source_sha256"] == hashlib.sha256((ROOT / "native/c6/element_law.cpp").read_bytes()).hexdigest()
    assert record["binary_sha256"] == hashlib.sha256(native.LIBRARY.read_bytes()).hexdigest()
    assert (record["compiler"], tuple(record["flags"])) == build_c6.TOOLCHAIN
    metrics = {"check1": {"states": 0, "index_mismatches": 0, "mask_mismatches": 0}}
    start = time.perf_counter()
    yield metrics
    metrics["test_seconds"] = time.perf_counter() - start
    reporter = request.config.pluginmanager.get_plugin("terminalreporter")
    if reporter:
        reporter.write_line("\nC6 equivalence measurements: " + json.dumps(metrics, sort_keys=True))


def fixture(seed, worlds=2, n=17):
    rng = np.random.default_rng(seed)
    return (rng.normal(size=(worlds, n, 2)) * 2,
            rng.uniform(-7, 7, (worlds, n)),
            rng.uniform(-0.2, 0.2, (worlds, n)))


def compare(metrics, check, label, got, want, tolerance, relative=False):
    entry = metrics.setdefault(check, {"x_max": 0.0, "theta_max": 0.0, "scaled_max": 0.0})
    for name, actual, expected in zip(("x", "theta"), got[:2], want[:2]):
        diff = np.abs(actual - expected)
        scale = np.maximum(1.0, np.abs(expected)) if relative else np.ones_like(expected)
        where = np.unravel_index(np.argmax(diff), diff.shape)
        maximum = float(diff[where])
        if name + "_where" not in entry or maximum > entry[name + "_max"]:
            entry[name + "_max"] = maximum
            entry[name + "_where"] = [label, *map(int, where)]
        entry["scaled_max"] = max(entry["scaled_max"], float(np.max(diff / scale)))
        assert np.all(diff <= tolerance * scale), (
            f"{check} {label} {name}: max difference {maximum:.17g} at {where}; "
            f"max scaled difference {np.max(diff / scale):.17g}")


def test_check1_neighbors_1000_states(kernel_and_measurements):
    rng = np.random.default_rng(610101)
    metrics = kernel_and_measurements["check1"]
    for trial in range(1000):
        n = int(rng.integers(5, 121))
        layout = trial % 5
        if layout == 0:
            # Integer grid with many exact ties, permuted to exercise index order.
            points = np.array([(i % 12, i // 12) for i in range(n)], dtype=float)
            x = points[rng.permutation(n)][None]
        else:
            x = rng.normal(size=(1, n, 2)) * (0.02 if layout == 1 else 25 if layout == 2 else 2)
        p = replace(reference.INTACT, k=int(rng.integers(0, n + 5)),
                    radius=float(rng.choice([0.01, 1.0, 3.0, 100.0])))
        batch = reference.Batch(p, 1)
        got, want = native.neighbors(x, batch), reference.neighbors(x, batch)
        metrics["states"] += 1
        metrics["index_mismatches"] += int(np.count_nonzero(got[0] != want[0]))
        metrics["mask_mismatches"] += int(np.count_nonzero(got[1] != want[1]))
        for part in range(3):
            assert np.array_equal(got[part], want[part]), f"neighbor part {part}, state {trial}, N={n}, layout={layout}"


@pytest.mark.parametrize("name", sorted(reference.ABLATIONS))
def test_check2_one_step_presets(name, kernel_and_measurements):
    x, th, omega = fixture(610202)
    p = reference.ABLATIONS[name]
    topology = reference.neighbors(x + 0.7 * fixture(610203)[0], reference.Batch(p, len(x)))
    kwargs = dict(phase_topology=topology)
    got = native.simulate(x, th, omega, p, 0.02, 1, **kwargs)
    want = reference.simulate(x, th, omega, p, 0.02, 1, **kwargs)
    compare(kernel_and_measurements, "check2", name, got, want, 1e-12, relative=True)


def mixed_params():
    # Distinct numeric parameters also test per-world packing, not just flags.
    return [replace(p, A=0.8 + i * 0.1, B=0.7 + i * 0.03,
                    J=p.J * 0.7, K=p.K * 1.2, eps=0.001 + i * 0.002)
            for i, p in enumerate(reference.ABLATIONS.values())]


def test_check2_mixed_parameters_and_epsilon(kernel_and_measurements):
    params = mixed_params()
    x, th, omega = fixture(610204, worlds=len(params))
    x[:, 1] = x[:, 0] + 0.0001  # exercises the per-world eps floor
    topology = reference.neighbors(fixture(610205, worlds=len(params))[0], reference.Batch(params, len(x)))
    # Arbitrary caller-provided counts/masks must be used, not recomputed.
    topology = topology[0], topology[1] * 0.5, topology[2] * 0.7
    got = native.simulate(x, th, omega, params, 0.000001, 1, phase_topology=topology)
    want = reference.simulate(x, th, omega, params, 0.000001, 1, phase_topology=topology)
    compare(kernel_and_measurements, "check2", "mixed/eps/custom-topology", got, want, 1e-12, relative=True)


def test_check3_1000_held_steps(kernel_and_measurements):
    params = mixed_params()
    x, th, omega = fixture(610301, worlds=len(params), n=12)
    topology = reference.neighbors(fixture(610302, worlds=len(params), n=12)[0], reference.Batch(params, len(x)))
    kwargs = dict(hold_neighbors=True, phase_topology=topology, sample_every=100)
    got = native.simulate(x, th, omega, params, 0.002, 1000, **kwargs)
    want = reference.simulate(x, th, omega, params, 0.002, 1000, **kwargs)
    compare(kernel_and_measurements, "check3", "mixed/final", got, want, 1e-9)
    compare(kernel_and_measurements, "check3", "mixed/sampled-trajectory", got[2], want[2], 1e-9)


@pytest.mark.parametrize("sample_every", [None, 0, 1, 3, 20, -3, 2.5])
@pytest.mark.parametrize("hold", [False, True])
def test_sampling_and_input_copy(sample_every, hold):
    x, th, omega = fixture(610401)
    before = x.copy(), th.copy(), omega.copy()
    # Non-contiguous inputs and broadcast omega are accepted by the reference.
    args = (x[:, ::-1], th[:, ::-1], omega[0, ::-1], reference.INTACT, 0.003, 10)
    got = native.simulate(*args, sample_every=sample_every, hold_neighbors=hold)
    want = reference.simulate(*args, sample_every=sample_every, hold_neighbors=hold)
    for a, b in zip(got[:2], want[:2]):
        np.testing.assert_allclose(a, b, rtol=1e-12, atol=1e-12)
        assert a.dtype == np.float64
    if sample_every:
        for a, b in zip(got[2], want[2]):
            assert a.shape == b.shape
            np.testing.assert_allclose(a, b, rtol=1e-12, atol=1e-12)
        assert np.array_equal(got[2][0][0], args[0])
        assert np.array_equal(got[2][1][0], args[1])
    else:
        assert got[2] is want[2] is None
    for a, b in zip((x, th, omega), before):
        assert np.array_equal(a, b)


@pytest.mark.parametrize("steps", [0, -2])
def test_no_steps_and_list_inputs(steps):
    x, th, omega = fixture(610402)
    for simulator in (reference.simulate, native.simulate):
        got = simulator(x.tolist(), th.tolist(), omega.tolist(), reference.INTACT,
                        0.02, steps, sample_every=3)
        assert np.array_equal(got[0], x) and np.array_equal(got[1], th)
        assert np.array_equal(got[2][0], x[None]) and np.array_equal(got[2][1], th[None])


@pytest.mark.parametrize("n,k", [(1, 8), (5, 0), (5, 20), (8, 3), (20, 17)])
def test_small_empty_and_large_neighbor_sets(n, k):
    x, th, omega = fixture(610403, n=n)
    p = replace(reference.INTACT, k=k)
    got, want = native.simulate(x, th, omega, p, 0.003, 5), reference.simulate(x, th, omega, p, 0.003, 5)
    for a, b in zip(got[:2], want[:2]):
        np.testing.assert_allclose(a, b, rtol=1e-12, atol=1e-12)


@pytest.mark.parametrize("field", ["x", "theta", "omega", "eps"])
def test_nonfinite_errors_match(field):
    x, th, omega = fixture(610501)
    p = reference.INTACT
    if field == "x":
        x[0, 0, 0] = np.nan
    elif field == "theta":
        th[0, 0] = np.inf
    elif field == "omega":
        omega[0, 0] = np.inf
    else:
        p = replace(p, eps=np.nan)
    for simulator in (reference.simulate, native.simulate):
        with np.errstate(all="ignore"), pytest.raises(FloatingPointError) as exc:
            simulator(x, th, omega, p, 0.02, 5)
        assert str(exc.value) == "non-finite state at step 1"
    x[0, 0, 0] = np.nan
    assert np.isnan(native.simulate(x, th, omega, p, 0.02, 0)[0][0, 0, 0])


@pytest.mark.parametrize("case,message", [
    ("count", "one Params per world is required"),
    ("k", "a batch must share one neighbor rule"),
    ("radius", "a batch must share one neighbor rule"),
    ("frozen", "frozen_phase_topology needs a phase_topology"),
])
def test_valueerrors_match(case, message):
    x, th, omega = fixture(610502)
    p = reference.INTACT
    params = {"count": [p], "k": [p, replace(p, k=2)],
              "radius": [p, replace(p, radius=2)],
              "frozen": [p, reference.ABLATIONS["frozen_topology"]]}[case]
    for simulator in (reference.simulate, native.simulate):
        with pytest.raises(ValueError) as exc:
            simulator(x, th, omega, params, 0.02, 1)
        assert str(exc.value) == message


def test_signature_and_params_identity():
    assert inspect.signature(native.simulate) == inspect.signature(reference.simulate)
    assert native.Params is reference.Params


def test_build_refuses_wrong_compiler(monkeypatch):
    monkeypatch.setattr(build_c6, "compiler_line", lambda: "wrong compiler")
    def forbidden(*args, **kwargs):
        pytest.fail("compiler invoked after a pin mismatch")
    monkeypatch.setattr(build_c6.subprocess, "run", forbidden)
    with pytest.raises(SystemExit) as exc:
        build_c6.main()
    assert "compiler pin mismatch" in str(exc.value)
    assert exc.value.code != 0


def test_build_refuses_changed_flags(monkeypatch):
    monkeypatch.setattr(build_c6, "compiler_line", lambda: build_c6.TOOLCHAIN[0])
    def forbidden(*args, **kwargs):
        pytest.fail("compiler invoked after a flag mismatch")
    monkeypatch.setattr(build_c6.subprocess, "run", forbidden)
    with pytest.raises(RuntimeError, match="compiler flags mismatch"):
        build_c6.build([*build_c6.TOOLCHAIN[1], "-ffast-math"])
