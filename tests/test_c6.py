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

# Step 2a contracts. Synthetic fixtures below use no experiment entropy.
import ast
import itertools
from geomind import c5_detect, c5_units, c5_coarse
from geomind import c6_levels as levels, c6_units as units, c6_compose as compose
from geomind import c6_effective as effective, c6_experiment as experiment
from tools import c6_design_gate as design


class FixedDraws:
    """Deterministic fixture directions, not experiment entropy."""
    def normal(self, size):
        return (np.arange(np.prod(size) if isinstance(size, tuple) else size, dtype=float)+1).reshape(size)

    def permutation(self, values):
        return np.asarray(values)[::-1]

    def choice(self, count, size, replace=False):
        return np.arange(size)

    def uniform(self, low, high):
        return .37*(high-low)+low


def square_unit(offset, first=0, C=1.):
    points = np.array([[-.3, -.3], [.3, -.3], [.3, .3], [-.3, .3]])+offset
    owner = levels.Owner(tuple(levels.Owner(element=first+i) for i in range(4)), C=C)
    return points, owner


def stable_world():
    xs, children = [], []
    for i, centre in enumerate(([0., 0.], [2., 0.], [1., 1.8])):
        points, child = square_unit(centre, 4*i)
        xs.append(points)
        children.append(child)
    owner = levels.Owner(tuple(children), C=3.2)
    times = np.arange(481)*.2
    x = np.concatenate(xs)
    return owner, np.repeat(x[None], len(times), axis=0), np.zeros((len(times), len(x))), times


def published_fixture(count=3):
    states = []
    for i in range(count):
        x, _ = square_unit([i*.8, .1*(i % 2)])
        states.append(units.level1_state(x, np.zeros(4), np.zeros(4), np.zeros(4, int), 0, 0.,
                      {'shape_cv': 0.}, reference.INTACT, .03*i))
    return states


@pytest.mark.parametrize('n,C', [(2, 3.2), (3, 9.6), (4, .2)])
def test_threshold_scaling_and_exact_steps(n, C):
    base = experiment.c4_manifest()['detector']
    actual = levels.thresholds(base, C)
    assert actual == c5_detect.level2_thresholds(base, C)
    for key in ('window', 'frame_dt', 'recovery_time'):
        assert actual[key] == base[key]*C
    assert actual['freq_tol'] == base['freq_tol']/C
    for multiplier in (.1, 1, 5, 10, 30, 100):
        assert experiment.steps_exact(multiplier*C)*.02 == pytest.approx(multiplier*C)
    assert experiment.rounded_C(3.3) == pytest.approx(3.4)
    with pytest.raises(ValueError, match='whole number'):
        experiment.steps_exact(.1*3.2*3.2)


def test_shared_procedure_and_revision_two_ledger():
    audit = experiment.same_rule_audit({2: 3.2, 3: 9.6})
    assert audit['one_rule']
    assert any('Direct part' in row for row in audit['normalization_ledger'])
    assert len(set(audit['functions'])) == 5
    assert audit['thresholds'][3]['freq_tol'] == pytest.approx(.01/9.6)


def test_publication_centroid_is_unweighted_and_phase_is_unwrapped():
    a = levels.Owner(tuple(levels.Owner(element=i) for i in range(3)))
    b = levels.Owner(tuple(levels.Owner(element=i) for i in range(3, 8)))
    owner = levels.Owner((a, b), C=3.2)
    x = np.zeros((5, 8, 2))
    x[:, 3:, 0] = 8
    th = np.repeat(np.linspace(2.9, 3.7, 5)[:, None], 8, axis=1)
    X, phase = levels.published_series(owner, x, th)
    assert np.all(X[:, 0] == 4)
    np.testing.assert_allclose(phase, th[:, 0])


def test_n2_regression_criteria_one_to_five_and_geometry():
    owner, xs, ths, times = stable_world()
    t = levels.thresholds(experiment.c4_manifest()['detector'], owner.C)
    idx = np.arange(0, len(times), 16)
    series = levels.child_series(owner, xs[idx], ths[idx])
    found, locked = c5_detect.candidates(*series, t['frame_dt'], t)
    future = (*[v[-1] for v in series], *[v[-1] for v in series])
    detected = levels.detect_level(series, [{'ok': True}]*3, t, lambda *args: future, FixedDraws())
    for actual, (group, expected) in zip(detected, found):
        expected.update(c5_detect.recovery(group, *future, locked, t))
        assert actual['units'] == group.tolist()
        for key, value in expected.items():
            assert actual['stats'][key] == value
        assert c5_detect.criteria_checks(actual['stats'], t) == {**c5_detect.c4_criteria(expected, t), '6_parts_alive': True}
    labels = compose.labels_for(owner, xs.shape[1])
    new = levels.geometric_validity(owner.children, xs[-1:])
    old = c5_units.hull_overlap(xs[-1], labels, range(3))
    np.testing.assert_allclose([r['hull_overlap'] for r in new], old, atol=1e-12)


def test_own_windows_and_insufficient_observation():
    owner, xs, ths, times = stable_world()
    base = experiment.c4_manifest()['detector']
    rows = levels.recursive_validity(owner, xs, ths, times, base)
    assert all(r['ok'] for r in rows)
    assert all(len(r['dynamic']['windows']) == 3 for r in rows)
    missing = levels.dynamic_validity(owner.children[0], xs[-40:], ths[-40:], times[-40:], .2, base)
    assert not missing['ok'] and missing['reason'] == 'INSUFFICIENT_OBSERVATION'
    slow = replace(owner.children[0], C=8.)
    # A fast parent must still record a full slow-part window.
    fast = levels.Owner((slow,), C=.2)
    assert levels.horizon(fast) == 240


def test_criterion_six_merged_and_broken_with_positive_controls():
    owner, xs, ths, times = stable_world()
    base = experiment.c4_manifest()['detector']
    assert all(r['ok'] for r in levels.recursive_validity(owner, xs, ths, times, base))
    merged = xs.copy()
    merged[:, 4:8] -= [2., 0.]
    rows = levels.recursive_validity(owner, merged, ths, times, base)
    assert rows[0]['hull_overlap'] == pytest.approx(1.) and not rows[0]['ok']
    broken = ths.copy()
    broken[:, 0] = .05*times
    rows = levels.recursive_validity(owner, xs, broken, times, base)
    assert not rows[0]['ok'] and rows[1]['ok']


@pytest.mark.parametrize('scale', [0., 1e-14])
def test_collinear_and_degenerate_parts_fail(scale):
    owner, xs, ths, times = stable_world()
    assert not levels.geometric_validity(owner.children, xs[-1:])[0]['degenerate']
    xs[:, :4, 1] = scale*np.array([-1., 1., 1., -1.])
    assert levels.geometric_validity(owner.children, xs[-1:])[0]['degenerate']


def test_concave_composites_and_crossing_hexagons():
    points, children = [], []
    for i, offset in enumerate(([0, 0], [0, 1], [1, 1], [1, 0])):
        p, child = square_unit(offset, i*4)
        points.append(p)
        children.append(child)
    concave = levels.Owner(tuple(children[:3]), C=3.2)
    tiny, child_a = square_unit([0., 0.], 16)
    smaller, child_b = square_unit([0., 0.], 20)
    points.extend([tiny*(2/3)+[.5, .3], smaller/3+[.8, .3]])
    cavity = levels.Owner((child_a, child_b), C=3.2)
    x = np.concatenate(points)
    assert levels.overlap(levels.union_pieces(levels.shape(concave, x)), levels.shape(cavity, x)) == pytest.approx(0, abs=1e-12)
    assert all(not r['degenerate'] and r['hull_overlap'] <= .2 for r in levels.geometric_validity((concave, cavity), x[None]))
    enclosing = [x[:12][levels._convex_hull(x[:12])]]
    assert levels.overlap(levels.union_pieces(levels.shape(cavity, x)), enclosing) > .2
    angles = np.arange(6)*np.pi/3
    a = np.c_[np.cos(angles), np.sin(angles)]
    b = np.c_[np.cos(angles+np.pi/6), np.sin(angles+np.pi/6)]
    assert levels.overlap([a], [b]) > .8
    # Touching faces have exactly zero area intersection; crossed hulls fail the cut.
    square = np.array([[0., 0.], [1., 0.], [1., 1.], [0., 1.]])
    assert levels.overlap([square], [square+[1, 0]]) == pytest.approx(0, abs=1e-12)
    assert levels.overlap([square], [square+[.1, 0]]) > .2


def test_union_exact_overlapping_pieces_no_double_count():
    square = np.array([[0., 0.], [1., 0.], [1., 1.], [0., 1.]])
    pieces = levels.union_pieces([square, square+[.5, 0]])
    assert sum(c5_units.polygon_area(p) for p in pieces) == pytest.approx(1.5)
    assert levels.overlap(pieces, levels.union_pieces([square, square+[.5, 0]])) == pytest.approx(1.)


def mixed_partitions(sizes, real):
    ids = tuple(sorted(set().union(*map(set, real))))
    labels = {m: i for i, group in enumerate(real) for m in group}
    out, seen = [], set()
    def recur(left, remaining_sizes, groups):
        if not remaining_sizes:
            key = tuple(sorted(tuple(sorted(g)) for g in groups))
            if key not in seen:
                seen.add(key)
                out.append(groups)
            return
        for group in itertools.combinations(left, remaining_sizes[0]):
            if len({labels[m] for m in group}) >= 2:
                recur(tuple(m for m in left if m not in group), remaining_sizes[1:], groups+[group])
    recur(ids, sizes, [])
    return out


def flat_null_contract(real, phases, lengths, expected_count):
    alternatives = mixed_partitions(list(map(len, real)), real)
    assert len(alternatives) == expected_count
    N = len(phases)
    times = np.array([0., .1, 1., 4.])
    decay = np.exp(-times)
    largest = 0.
    for probe in range(N):
        for kind in ('pulse', 'push'):
            amount = .5 if kind == 'pulse' else .2*lengths[probe]
            truth = np.zeros((len(times), N, 3))
            channel = 2 if kind == 'pulse' else 0
            truth[..., channel] = amount/N*(1-decay[:, None])
            truth[:, probe, channel] += amount*decay
            # Paired differences cancel every heterogeneous initial phase exactly.
            real_predictions = levels.linear_summary(truth, real)
            for alternative in alternatives:
                row = levels.pair_contrast(truth, real, alternative, probe, 1., real_predictions,
                                           levels.linear_summary(truth, alternative))
                if row['status'] == 'TESTED':
                    largest = max(largest, abs(row['contrast']))
    assert largest <= 1e-12


@pytest.mark.parametrize('phases', [np.repeat([-2., 0., 2.], 3), np.zeros(9)], ids=['heterogeneous', 'homogeneous'])
def test_nine_element_uncorrected_consensus_null(phases):
    # Exactly the balanced, ALL-three-real-parts-mixed subset in the original nine-element fixture.
    real = [(0, 1, 2), (3, 4, 5), (6, 7, 8)]
    all_mixed = mixed_partitions([3, 3, 3], real)
    alternatives = [g for g in all_mixed if all(len({m//3 for m in part}) == 3 for part in g)]
    assert len(alternatives) == 36
    for probe in range(9):
        truth = np.zeros((4, 9, 3))
        decay = np.exp(-np.linspace(0., 32., 101))
        truth = np.zeros((len(decay), 9, 3))
        paired = .5/9*(1-decay[:, None])+np.eye(9)[probe]*.5*decay[:, None]
        truth[..., 2] = (phases[None]+paired)-phases[None]
        for alt in alternatives:
            row = levels.pair_contrast(truth, real, alt, probe, 1.)
            assert row['status'] == 'TESTED' and abs(row['contrast']) <= 1e-12
            assert row['real_error'] <= 1e-12 and row['alternative_error'] <= 1e-12
            assert probe not in row['scored']
            # No later branch offsets may enter the membership-only decoder.
    assert list(levels.MembershipDecoder.__dataclass_fields__) == ['groups']


def test_ten_subpart_unequal_size_push_null_all_1890_alternatives():
    real = [(0, 1, 2), (3, 4, 5), (6, 7, 8, 9)]
    # The fixture admits alternatives in which the four-member real part is split.
    alternatives = mixed_partitions([3, 3, 4], real)
    admissible = [g for g in alternatives if not any(set(p) == set(real[-1]) for p in g)]
    # All parts mix at least two real parts, including the 4-part.
    assert len(admissible) == 1890
    for probe in range(10):
        for kind in ('pulse', 'push'):
            amount = .5 if kind == 'pulse' else .2*(2 if probe >= 6 else 1)
            decay = np.exp(-np.linspace(0., 32., 101))
            truth = np.zeros((len(decay), 10, 3))
            axis = 2 if kind == 'pulse' else 0
            truth[..., axis] = amount/10*(1-decay[:, None])
            truth[:, probe, axis] += amount*decay
            for alt in admissible:
                row = levels.pair_contrast(truth, real, alt, probe, 1.)
                if row['status'] == 'TESTED':
                    assert abs(row['contrast']) <= 1e-12
                    assert row['real_error'] <= 1e-12 and row['alternative_error'] <= 1e-12


@pytest.mark.parametrize('sizes,internal,external', [([3, 3], 10., .1), ([6, 6], 1., 1.)])
def test_modular_and_two_clique_fixtures_positive(sizes, internal, external):
    N = sum(sizes)
    adjacency = np.zeros((N, N))
    offset = sizes[0]
    adjacency[:offset, :offset] = internal
    adjacency[offset:, offset:] = internal
    np.fill_diagonal(adjacency, 0)
    for i in range(offset):
        adjacency[i, offset+i] = adjacency[offset+i, i] = external
    generator = np.diag(adjacency.sum(1))-adjacency
    real = [tuple(range(offset)), tuple(range(offset, N))]
    alt = [tuple(range(0, N, 2)), tuple(range(1, N, 2))]
    values = []
    for probe in range(N):
        impulse = np.zeros((N, 3))
        impulse[probe, 2] = .5
        truth = np.array([effective.matrix_exp(-generator*t) @ impulse for t in (.1, .5, 1.)])
        row = levels.pair_contrast(truth, real, alt, probe, 1.)
        assert row['contrast'] > 0
        values.append(row)
    assert levels.unit_specificity(values)['value'] > 0


def test_probes_before_groupings_and_contiguous_alternatives():
    assert list(inspect.signature(levels.draw_probes).parameters) == ['subparts', 'rng']
    source = inspect.getsource(experiment.specificity_world)
    assert source.index('levels.draw_probes') < source.index('real, offset') < source.index('alternative_groupings')
    real = [(0, 1, 2), (3, 4, 5)]
    adjacency = np.ones((6, 6), bool)
    sampling = levels.alternative_groupings(real, adjacency, np.random.default_rng(1234), K=4)
    alternatives = sampling['alternatives']
    assert len(alternatives) == 4
    for groups in alternatives:
        assert sorted(map(len, groups)) == [3, 3]
        assert all(levels.connected(g, adjacency) and len({p//3 for p in g}) >= 2 for g in groups)
        row = levels.pair_contrast(np.zeros((2, 6, 3)), real, groups, 0, 1.)
        excluded = set(next(g for g in real if 0 in g)) | set(next(g for g in groups if 0 in g))
        assert set(row['scored']) == set(range(6))-excluded


@pytest.mark.parametrize('reason', ['censored', 'nonpositive', 'nonfinite', 'disconnected', 'no_mode'])
def test_diffusion_not_computed_rules(reason):
    adjacency = ~np.eye(3, dtype=bool)
    tau, censored = 1., False
    if reason == 'censored':
        censored = True
    elif reason == 'nonpositive':
        tau = 0.
    elif reason == 'nonfinite':
        tau = float('nan')
    elif reason == 'disconnected':
        adjacency[2] = adjacency[:, 2] = False
    else:
        adjacency = np.zeros((1, 1), bool)
    result = levels.diffusion_diagnostic(adjacency, tau, [0., 1.], np.zeros((len(adjacency), 3)), censored)
    assert result['status'] == 'NOT_COMPUTED'


def test_linear_constructor_has_no_circular_summary_and_E1_identity():
    states = published_fixture(2)
    response = np.zeros((6, 3))
    response[0, 2] = .5
    delta = effective.linear_input(states, response, [(0, 1, 2), (3, 4, 5)])
    assert delta[-2] == pytest.approx(.5/3)
    assert effective.E1 is c5_coarse.run
    assert 'reopen' not in inspect.signature(effective.predict).parameters
    assert 'circular_mean' not in inspect.getsource(effective.linear_input)


def test_matrix_exp_eigen_solution_jordan_and_nonfinite():
    S = np.array([[1., .2, .4], [0., 1., .1], [0., 0., 1.]])
    J = S @ np.diag([-2., -.3, 0.]) @ np.linalg.inv(S)
    np.testing.assert_allclose(effective.matrix_exp(J*2), S @ np.diag(np.exp([-4., -.6, 0.])) @ np.linalg.inv(S), atol=1e-13)
    jordan = np.array([[0., 1.], [0., 0.]])
    np.testing.assert_array_equal(effective.matrix_exp(jordan*3), np.eye(2)+3*jordan)
    with pytest.raises(ValueError, match='finite'):
        effective.matrix_exp([[float('nan')]])
    calls = [n.func for n in ast.walk(ast.parse(inspect.getsource(effective.matrix_exp))) if isinstance(n, ast.Call)]
    assert not any(isinstance(f, ast.Attribute) and f.attr in {'eig', 'eigh', 'eigvals', 'eigvalsh'} for f in calls)


def test_dimensionless_convergence_and_abstention(monkeypatch):
    J = np.array([[.1, .2, .3], [.4, .2, .1], [.2, .3, .4]])
    Jh = J + .001*np.eye(3)
    one = effective.convergence(Jh, J, [2.], 3.2)
    scale = np.array([100., 100., 1.])
    two = effective.convergence(scale[:, None]*Jh/scale[None], scale[:, None]*J/scale[None], [200.], 3.2)
    assert one['converged'] == two['converged']
    assert one['difference'] == pytest.approx(two['difference'])
    assert one['tolerance'] == pytest.approx(two['tolerance'])
    monkeypatch.setattr(effective, 'jacobian', lambda *args: (np.eye(6), {'converged': False}))
    out = effective.E2(published_fixture(2), reference.INTACT, 3.2, np.ones(6), [0., 1.])
    assert out['abstained'] and np.all(out['response'] == 0)


def test_E2_first_order_matches_E1():
    states = published_fixture(2)
    delta = np.zeros(6)
    delta[-1] = 1e-6
    times = np.arange(11)*.02
    one = effective.predict(states, reference.INTACT, 1., 'E1', delta, times)
    two = effective.predict(states, reference.INTACT, 1., 'E2', delta, times)
    assert not two['abstained']
    np.testing.assert_allclose(one['response'], two['response'], atol=2e-8)


@pytest.mark.parametrize("omega_g", [0., .07, -.08])
def test_level1_measured_rate_reaches_consumed_field(omega_g):
    x, owner = square_unit([0., 0.])
    measured, record = units.isolated_rate(owner, x, np.zeros(4), np.full(4, omega_g), reference.INTACT, native.simulate)
    assert measured == pytest.approx(omega_g, abs=record["resolution"])
    state = units.level1_state(x, np.zeros(4), np.zeros(4), np.zeros(4, int), 0, .01, {'shape_cv': 0.}, reference.INTACT, measured)
    assert state['natural_rate'] == measured
    assert c5_coarse.CoarseState([state], reference.INTACT.k).natural[0] == measured


def test_composition_measured_rate_folded_capacities_and_shape():
    states = published_fixture(3)
    old = c5_units.compose_state(states, .123, {'shape_cv': 0.})
    new = units.compose_state(states, .123, {'shape_cv': 0.}, .123, reference.INTACT)
    assert new['natural_rate'] == .123 and old['natural_rate'] != .123
    assert set(new) == set(states[0])
    assert any(len(a['own_neighbour_distances']) > len(b['own_neighbour_distances'])
               for a, b in zip(new['boundary_ports'], old['boundary_ports']))
    upper = units.compose_state([new, {**copy_state(new), 'effective_position': [3., 0.]}], .2, {'shape_cv': 0.}, .2, reference.INTACT)
    assert set(upper) == set(new)


def copy_state(s):
    import copy
    return copy.deepcopy(s)


@pytest.mark.parametrize('defect', ['duplicate', 'omitted', 'swapped', 'nan', 'mode', 'S'])
def test_N1_exact_world_unitset_finite_and_S(defect):
    children = published_fixture(3)
    stats = {'shape_cv': 0.}
    candidate = {'world': 0, 'units': [0, 1, 2], 'accepted': True, 'stats': stats}
    state = units.compose_state(children, 0., stats, 0., reference.INTACT)
    publication = {'world': 0, 'units': [0, 1, 2], 'state': state}
    assert not units.validate_interface([candidate], [publication], {0: children})
    rows = [copy_state(publication)]
    if defect == 'duplicate':
        rows.append(copy_state(publication))
    elif defect == 'omitted':
        rows = []
    elif defect == 'swapped':
        rows[0]['units'] = [0, 1]
    elif defect == 'nan':
        rows[0]['state']['natural_rate'] = float('nan')
    elif defect == 'mode':
        rows[0]['state']['mode_signature'] = {}
    else:
        rows[0]['state']['stability'] = {}
    assert units.validate_interface([candidate], rows, {0: children})


def test_harvest_source_split_at_both_levels():
    assert not units.harvest_isolation({0: [(1, 100), (2, 100)], 1: [(3, 101)]})
    assert units.harvest_isolation({0: [(1, 100)], 1: [(1, 101)]})
    assert units.harvest_isolation({0: [(1, 100)], 1: [(2, 100)]})
    templates = [{'source_world': source, 'id': i} for i, source in enumerate([1, 1, 1, 2, 2, 3, 3])]
    assigned = units.assign_templates(templates, 2, 3)
    assert [[t['id'] for t in group] for group in assigned] == [[0, 1], [3, 4], [5, 6]]


def test_harvest_reacceptance_filter_records_measurement():
    owner, xs, ths, _ = stable_world()
    formation = [{'units': [0, 1, 2], 'accepted': True, 'stats': {'x': 1}}]
    def measure(*args):
        return .08, {'rate': .08}
    out, raw = units.harvest_level(formation, lambda *args: (False, {'accepted': False}), measure,
                                   xs[-1], ths[-1], np.zeros(xs.shape[1]), owner, 9)
    assert out == [] and raw[0]['isolated_rate']['rate'] == .08
    out, _ = units.harvest_level(formation, lambda *args: (True, {'accepted': True}), measure,
                                 xs[-1], ths[-1], np.zeros(xs.shape[1]), owner, 9)
    assert len(out) == 1 and out[0]['isolated_rate'] == .08


@pytest.mark.parametrize('kind', ['pulse', 'push'])
@pytest.mark.parametrize('witness', ['lower', 'upper'])
def test_certified_censored_bounds_Codex_witnesses(kind, witness):
    T, times, c = 10., np.linspace(0, 10, 101), .5/3
    curve = lambda tau: c*(1-np.exp(-times/tau))
    u, v, z = curve(T), curve(2*T), curve(1.5*T)
    y = z
    if witness == 'upper':
        d = v-u
        normal = z-u-np.dot(z-u, d)/np.dot(d, d)*d
        y = z-normal/np.sqrt(np.mean(normal**2))
    truth = np.zeros((101, 3, 3))
    if kind == 'pulse':
        truth[..., 2] = y[:, None]
        lengths, amount = np.ones(3), .5
    else:
        truth[..., 0] = y[:, None]
        truth[..., 2] = .037
        lengths, amount = np.array([.5, 1., 2.]), np.array([.5, 0.])
    bounds = effective.censored_bounds(truth, times, amount, 3, lengths, kind, T)
    expected = effective.error_parts(truth, effective.relaxation_response(times, amount, 3, 3, kind, 1/(1.5*T)), lengths)['total']
    assert bounds['lower'] <= expected <= bounds['upper']
    assert len(bounds['grid_u']) == 65
    assert bounds['h'] == 1/(128*T)
    assert bounds['margin'] == pytest.approx(bounds['K']*bounds['h'])


def test_response_floor_counts_gains_and_censored_tau_never_imputed():
    times = np.arange(101)*.1
    truth = np.full((101, 3, 3), .0001)
    tau = {'censored': True, 'tau': None, 'limit': 10.}
    score = effective.score_excitation(truth, np.zeros_like(truth), times, 0, np.ones(3), 'pulse', .5, tau)
    assert score['response_status'] == 'BELOW_RESPONSE_FLOOR' and score['r'] is None
    assert len(score['gains']) == 3
    assert score['gains']['relaxation']['lo'] <= score['gains']['relaxation']['hi']
    censored = effective.tau_estimate(np.ones(101), 3.2)
    assert censored['censored'] and censored['tau'] is None and censored['limit'] == 32.
    assert effective.tau_estimate(np.exp(-np.arange(101)*.1), 1.)['tau'] == pytest.approx(1.)
    bounds = effective.separation_bounds(censored, [{'tau': 1., 'censored': False}])
    assert bounds == {'lo': 32., 'hi': float('inf')}
    bounds = effective.separation_bounds({'tau': 2., 'censored': False}, [censored])
    assert bounds == {'lo': 0., 'hi': 2/32}


def test_contact_solution_and_rigid_published_centroid_operations():
    a, _ = square_unit([0., 0.])
    b, _ = square_unit([0., 0.])
    position, gap = compose.contact_solve(a, b, [0., 0.], [1., .3])
    assert .6 <= gap <= .600001
    assert np.min(np.linalg.norm(a[:, None]+position-b[None], axis=-1)) == gap
    owner, xs, ths, _ = stable_world()
    shifted = compose.scale_parts(xs[-1], ths[-1], owner, 1.25)
    for part in owner.children:
        m = list(part.members)
        np.testing.assert_allclose(shifted[m]-shifted[m[0]], xs[-1, m]-xs[-1, m[0]], atol=1e-15)


@pytest.mark.parametrize('n,free_steps', [(250, 300)], ids=['realistic_size_free_run'])
def test_realistic_size_free_run(n, free_steps, kernel_and_measurements):
    i = np.arange(n)
    x = np.c_[i % 16, i//16][None].astype(float)*.45
    th = np.sin(i*.13)[None]
    omega = .03*np.cos(i*.07)[None]
    got = native.simulate(x, th, omega, reference.INTACT, .02, free_steps, sample_every=100)
    want = reference.simulate(x, th, omega, reference.INTACT, .02, free_steps, sample_every=100)
    compare(kernel_and_measurements, 'realistic_size', '250/300/free', got, want, 1e-9)
    compare(kernel_and_measurements, 'realistic_size', '250/300/samples', got[2], want[2], 1e-9)


def test_smoke_receipt_scratch_only_and_first_stop(tmp_path):
    receipt = design.Receipt(tmp_path/'scratch', True)
    receipt.step('synthetic', {'world': 0, 'fraction': .5})
    assert not receipt.check(1, True, {'fraction': .5})
    data = json.loads((receipt.folder/'results.json').read_text())
    assert data['status'] == 'STOP' and data['stopped_at'] == 1
    assert not any(r['evaluated'] for r in data['stop_rules'][1:])
    with pytest.raises(ValueError, match='outside evidence'):
        design.Receipt(ROOT/'evidence/c6_smoke_forbidden', True)
    with pytest.raises(FileExistsError):
        design.Receipt(receipt.folder, True)


def test_equivalence_records_absolute_floor_and_outcomes():
    a = {'outcome': 'FORMED', 'candidates': [{'units': [0, 1, 2], 'accepted': True, 'stats': {'shape_cv': 0.}}], 'validity': []}
    b = copy_state(a)
    b['candidates'][0]['stats']['shape_cv'] = 1e-10
    assert design.compare_records(a, b)['passed']
    b['candidates'][0]['stats']['shape_cv'] = 1e-5
    assert not design.compare_records(a, b)['passed']
    b = copy_state(a)
    b['outcome'] = 'MERGED'
    assert not design.compare_records(a, b)['passed']


def recursive_world():
    points, parents = [], []
    for g, origin in enumerate(([0., 0.], [5., 0.], [2.5, 5.])):
        children = []
        for offset in ([0., 0.], [1., 0.], [.5, 1.]):
            p, child = square_unit(np.array(origin)+offset, 4*(3*g+len(children)))
            points.append(p)
            children.append(child)
        parents.append(levels.Owner(tuple(children), C=3.2))
    owner = levels.Owner(tuple(parents), C=9.6)
    times = np.arange(1441)*.2
    x = np.concatenate(points)
    return owner, np.repeat(x[None], len(times), axis=0), np.zeros((len(times), len(x))), times


def test_recursive_criterion_six_broken_child_inside_intact_parent_and_merged_parent():
    owner, xs, ths, times = recursive_world()
    base = experiment.c4_manifest()['detector']
    positive = levels.recursive_validity(owner, xs, ths, times, base)
    assert all(r['ok'] for r in positive)
    broken = ths.copy()
    broken[:, 0], broken[:, 1] = .005*times, -.005*times
    rows = levels.recursive_validity(owner, xs, broken, times, base)
    assert rows[0]['dynamic']['ok']
    assert not rows[0]['children'][0]['ok'] and rows[0]['ok']
    merged = xs.copy()
    merged[:, 12:24] -= [5., 0.]
    rows = levels.recursive_validity(owner, merged, ths, times, base)
    assert rows[0]['hull_overlap'] == pytest.approx(1.) and not rows[0]['ok']


def test_V2_adds_active_nonhull_members_and_rotating_rate_shift():
    x, owner = square_unit([0., 0.])
    x = np.vstack([x, [0., 0.], [0.01, 0.]])
    labels = np.array([0, 0, 0, 0, 0, 1])
    state = units.level1_state(x, np.zeros(6), np.zeros(6), labels, 0, 0., {'shape_cv': 0.}, reference.INTACT, 0., 'V1')
    active = units.level1_state(x, np.zeros(6), np.zeros(6), labels, 0, 0., {'shape_cv': 0.}, reference.INTACT, 0., 'V2')
    assert len(active['boundary_ports']) > len(state['boundary_ports'])
    template = {'x': x[:4], 'th': np.zeros(4), 'omega': np.array([.1, .2, .3, .4]),
                'owner': owner, 'isolated_rate': .23}
    _, _, rates, _, raw = compose.assemble([template], FixedDraws(), 3.2)
    np.testing.assert_allclose(rates-template['omega'], raw['rates'][0]-.23)
    assert abs(raw['rates'][0]) <= .096/3.2


def test_cumulative_timescale_censoring_medians_and_zero_denominator():
    reference_rows = [{'tau': 1., 'censored': False}]*5
    rows = [{'tau': 3.2, 'censored': False}, {'tau': 3.3, 'censored': False},
            {'tau': 3.3, 'censored': False}, {'tau': None, 'censored': True}, {'tau': None, 'censored': True}]
    assert experiment.cumulative_C(rows, reference_rows) == 3.4
    assert experiment.cumulative_C(rows[:4], reference_rows) is None
    assert experiment.cumulative_C(rows, reference_rows[:4]) is None
    assert experiment.cumulative_C(rows+[{'tau': None, 'censored': True}], reference_rows) is None
    assert experiment.cumulative_C(rows, [{'tau': 0., 'censored': False}]*5) is None


def test_readiness_six_cells_floor_counts_and_abstention_exclusion():
    def fake_world(abstained):
        scores = {}
        for name in ('E1_V1', 'E1_V2', 'E2_V1', 'E2_V2'):
            scores[name] = {'gains': {b: {'lo': .1, 'hi': .2} for b in ('no_transfer', 'rigid_transfer', 'relaxation')},
                            'r': .4, 'abstained': abstained and name.startswith('E2')}
        return {'excitations': {'pulse': copy_state(scores), 'push': copy_state(scores)},
                'tau_phase': {'censored': False}, 'tau_position': {'censored': False}}
    out = experiment.readiness_summary({2: [fake_world(True)]*10, 3: [fake_world(True)]*10})
    assert out['selected'].startswith('E1')
    assert out['combinations']['E2_V1']['excluded']
    assert len(out['combinations']['E1_V1']['levels'][2]['cells']) == 6
    assert out['combinations']['E1_V1']['levels'][3]['r']['push']['count'] == 10


def test_effective_information_boundary_expected_level():
    states = published_fixture(2)
    effective.require_published(states, expected_level=1)
    with pytest.raises(ValueError, match='wrong level'):
        effective.require_published(states, expected_level=2)
    states[0]['members'] = [0, 1, 2]
    with pytest.raises(ValueError, match='published interface'):
        effective.require_published(states)


def test_primitive_adapter_regression_against_frozen_C4_detector():
    from geomind import c4_detect
    x, _ = square_unit([0., 0.])
    xs, ths = np.repeat(x[None], 31, axis=0), np.zeros((31, 4))
    om = np.zeros(4)
    owner = levels.Owner(tuple(levels.Owner(element=i) for i in range(4)))
    base = experiment.c4_manifest()['detector']
    got, _ = experiment.detect_snapshot(owner, xs, ths, np.arange(31), om, native.simulate, base, FixedDraws(), True)
    want = c4_detect.detect(xs[:, None], ths[:, None], om[None], reference.INTACT, .02, 1., base, [FixedDraws()])[0]
    assert len(got) == len(want)
    for a, b in zip(got, want):
        assert a['units'] == b['members'].tolist() and a['accepted'] == b['accepted']
        for key, value in b['stats'].items():
            assert a['stats'][key] == pytest.approx(value, abs=1e-9)


def test_exact_union_disjoint_rotated_pieces_do_not_fragment():
    angle = np.arange(6)*np.pi/3+.17
    hexagon = np.c_[np.cos(angle), np.sin(angle)]
    hulls = [hexagon+[3*(i % 8), 3*(i//8)] for i in range(40)]
    started = time.perf_counter()
    first = levels.union_pieces(hulls)
    second = levels.union_pieces(first)
    assert len(first) == len(second) == len(hulls)
    assert sum(map(c5_units.polygon_area, second)) == pytest.approx(sum(map(c5_units.polygon_area, hulls)))
    assert time.perf_counter()-started < 5


def test_development_neighbor_check_uses_reference_indices_and_masks():
    x, _ = square_unit([0., 0.])
    measured = design.development_neighbors(np.repeat(x[None], 10, axis=0))
    assert measured == {'passed': True, 'states': 10, 'index_mismatches': 0, 'mask_mismatches': 0}


def test_same_rule_audit_detects_recipe_ports_functions_and_scaling():
    factors = {2: 3.2, 3: 9.6}
    assert experiment.same_rule_audit(factors)['one_rule']
    for field in ('recipes', 'port_variants', 'functions'):
        rules = {n: experiment.transition_rule() for n in (2, 3)}
        if field == 'functions':
            rules[3][field] = (*rules[3][field][:-1], lambda base, C: dict(base))
        else:
            rules[3][field] = ('DIFFERENT',)
        assert not experiment.same_rule_audit(factors, rules)['one_rule']


def test_rule_14_records_yes_no_stop_row(tmp_path):
    receipt = design.Receipt(tmp_path/'scratch', True)
    assert not receipt.check(14, True, {'passed': False})
    row = next(r for r in receipt.data['stop_rules'] if r['rule'] == 14)
    assert row['evaluated'] and row['stop'] and row['action'] == 'STOP'


def test_bank_supply_audit_against_section_nine():
    plan = design.bank_plan(3, 30)
    assert (plan['composite_worlds'], plan['primitive_worlds']) == (600, 4800)
    assert plan['proposal_estimate'] == {'composite_worlds': 300, 'primitive_worlds': 2250}



def test_level1_harvest_measures_rate_with_common_estimator(monkeypatch):
    x = np.c_[np.arange(6), np.zeros(6)]
    monkeypatch.setattr(experiment.c4_experiment, 'initial_worlds',
        lambda *a: (x[None], np.zeros((1, 6)), np.full((1, 6), .07)))
    def integrate(x, th, omega, duration, simulate, every=None, params=None):
        frames = None if every is None else (np.repeat(x[None], 151, axis=0), np.repeat(th[None], 151, axis=0))
        return x, th, frames
    monkeypatch.setattr(experiment, 'integrate', integrate)
    monkeypatch.setattr(experiment, 'detect_snapshot',
        lambda *a, **k: ([{'units': list(range(6)), 'accepted': True}], []))
    calls = []
    def measured(owner, x, th, omega, params, simulate):
        calls.append((owner, omega))
        return .07, {'rate': .07, 'duration': 30*owner.C, 'sample_dt': owner.C}
    assert 'rate_estimate' in inspect.getsource(units.isolated_rate)
    monkeypatch.setattr(units, 'isolated_rate', measured)
    templates, raw = experiment.harvest_primitives(1, 1, object())
    assert len(calls) == 1 and len(templates) == 1
    assert templates[0]['isolated_rate'] == .07
    np.testing.assert_array_equal(templates[0]['omega'], np.full(6, .07))
    assert raw[0]['isolated_rates'][0]['measurement']['rate'] == .07
    assert 'units.rate_estimate' in inspect.getsource(experiment.alone)


def test_check4_bank_inputs_only_and_projection_never_uses_their_costs(tmp_path, monkeypatch):
    class Pool:
        def map(self, fn, jobs):
            return map(fn, jobs)
    monkeypatch.setattr(design, '_harvest_job', lambda args: ([{'source_world': args[1]}], [{'seconds': 1.}]))
    monkeypatch.setattr(units, 'assign_templates', lambda templates, parts, worlds: [[]]*worlds)
    receipt = design.Receipt(tmp_path/'scratch', True)
    design.bank(Pool(), 2, 2, 1200, design.PROVISIONAL, True, receipt, inputs_only=True)
    assert all(t['inputs_only'] for t in receipt.data['timings'])
    assert all(s['values']['inputs_only'] for s in receipt.data['steps'])
    receipt.data['timings'].extend([
        {'stage': name, 'inputs_only': False, 'seconds': 1.,
         'work': {'level': level, 'pass': 1, 'worlds': 2, 'job_seconds': [2., 2.]}}
        for name in ('primitive_harvest', 'composite_formation', 'composite_isolation', 'isolated_timescales')
        for level in (2, 3)])
    projection = design.full_gate_projection(receipt.data)
    receipt.data['timings'][0]['work']['job_seconds'] = [1e10]
    receipt.data['timings'][0]['seconds'] = 1e10
    assert design.full_gate_projection(receipt.data) == projection
    assert projection['complete_gate_seconds'] is None
    assert 'transition_protocol_l2' in projection['unmeasured']


def test_nested_geometry_overlap_only_early_in_level3_window():
    owner, xs, ths, times = recursive_world()
    base = experiment.c4_manifest()['detector']
    assert all(r['ok'] for r in levels.recursive_validity(owner, xs, ths, times, base))
    # A rigid move preserves this level-1 unit's own dynamic statistics. It
    # overlaps its sibling at a C2 frame far earlier than the trailing 30 C2.
    early = np.flatnonzero(np.isclose(times, owner.children[0].C))[0]
    xs[early, :4] += [1., 0.]
    rows = levels.recursive_validity(owner, xs, ths, times, base)
    child = rows[0]['children'][0]
    assert child['dynamic']['ok']
    assert child['hull_overlap'] == pytest.approx(1.)
    assert not child['ok'] and rows[0]['ok']
    assert child['geometry']['start'] == pytest.approx(0.)
    assert child['geometry']['frame_dt'] == 3.2
    assert child['geometry']['frames'] == 91


def test_missing_deeper_dynamic_frame_does_not_veto_parent():
    owner, xs, ths, times = recursive_world()
    early = np.flatnonzero(np.isclose(times, 1.))[0]
    keep = np.arange(len(times)) != early
    rows = levels.recursive_validity(owner, xs[keep], ths[keep], times[keep], experiment.c4_manifest()['detector'])
    assert rows[0]['geometry']['observed']
    assert not rows[0]['children'][0]['dynamic']['ok']
    assert rows[0]['children'][0]['reason'] == 'INSUFFICIENT_OBSERVATION'
    assert rows[0]['ok']


def test_no_c5_proximity_gate_and_rounded_zero_is_undefined(tmp_path):
    receipt = design.Receipt(tmp_path/'scratch', True)
    rows = {2: [{'level': 1, 'tau': 1., 'censored': False}]*5+
                [{'level': 2, 'tau': 10., 'censored': False}]*5,
            3: [{'level': 3, 'tau': .2, 'censored': False}]*5}
    assert design.pass_one_factors(receipt, rows) == {2: 10., 3: .2}
    assert experiment.cumulative_C([{'tau': .01, 'censored': False}]*5,
                                  [{'tau': 1., 'censored': False}]*5) is None


def test_full_projection_measures_retained_protocol_and_keeps_missing_unknown():
    record = {'seconds': 8., 'duration': 100., 'full_duration': 100.,
              'observation_seconds': 1., 'observation_duration': 30.}
    timings = [{'stage': name, 'seconds': 1., 'inputs_only': False,
                'work': {'level': n, 'pass': p, 'worlds': 6, 'job_seconds': [8.]*6}}
               for name in ('primitive_harvest', 'composite_formation', 'composite_isolation',
                            'isolated_timescales', 'coarse_readiness')
               for n in (2, 3) for p in (1, 2)]
    values = {f'formation_pass_{p}': {n: {'raw': [record]*6} for n in (2, 3)} for p in (1, 2)}
    values.update({f'isolated_timescales_pass_{p}_level_{n}': [{'tau': 1.}] for p in (1, 2) for n in (2, 3)})
    values['runtime_protocol_measurements'] = {n: {'seconds': 8.} for n in (2, 3)}
    data = {'timings': timings, 'steps': [{'name': k, 'values': v} for k, v in values.items()]}
    timings.extend({'stage': 'numerical_checks', 'seconds': 1., 'inputs_only': True,
                    'work': {'level': n}} for n in (2, 3))
    projection = design.full_gate_projection(data, panel=True)
    assert projection['unmeasured'] == []
    by_stage = {s['stage']: s['seconds'] for s in projection['stages']}
    assert by_stage['panel_l2_formation_protocol'] == 40.
    assert by_stage['transition_protocol_l3'] == 40.
    values['runtime_protocol_measurements'][3] = {'status': 'NOT_RUN'}
    assert design.full_gate_projection(data, panel=True)['complete_gate_seconds'] is None


def test_deeper_timescale_cannot_extend_direct_observation():
    owner, xs, ths, times = recursive_world()
    child = owner.children[0]
    deep = replace(child.children[0], C=100.)
    changed = replace(owner, children=(replace(child, children=(deep, *child.children[1:])), *owner.children[1:]))
    assert levels.observation_window(changed) == levels.observation_window(owner)
    assert levels.horizon(changed) == levels.horizon(owner)
    rows = levels.recursive_validity(changed, xs, ths, times, experiment.c4_manifest()['detector'])
    assert rows[0]['ok']
    assert not rows[0]['children'][0]['ok']
    assert experiment.own_stability(deep, (xs, ths, times)) == {'observation': 'INSUFFICIENT_OBSERVATION'}


def test_E2_carries_validity_and_separate_service_reopens(monkeypatch):
    states = published_fixture(2)
    times = np.array([0., .1, .2])
    def response(states, params, C, delta, times, dt):
        M = len(states)
        X = np.repeat(np.array([s['effective_position'] for s in states])[None], len(times), 0)
        theta = np.repeat(np.array([s['optional_phase'] for s in states])[None], len(times), 0)
        return {'response': np.zeros((len(times), M, 3)), 'validity': [False]+[True]*(len(times)-1),
                'control': {'X': X, 'theta': theta}, 'work': 1, 'matrix_exponentials': len(times)}
    monkeypatch.setattr(effective, 'E2', response)
    calls = []
    def reopen(frame):
        calls.append(frame)
        return states
    out = effective.service(states, reference.INTACT, 1., 'E2', times, reopen)
    assert calls == [1, 2]
    assert out['reopens'] == out['flagged'] == 2
    assert 'reopen' not in inspect.signature(effective.predict).parameters


def test_retained_protocol_complete_ablations_and_publication():
    from geomind.c6_protocol import transition_measurements
    owner, xs, ths, times = stable_world()
    row = {'owner': owner, 'x': xs[-1], 'th': ths[-1], 'omega': np.zeros(xs.shape[1]),
           'xs': xs, 'ths': ths, 'times': times,
           'record': {'world': 0, 'candidates': [{'accepted': True, 'units': [0, 1, 2],
                                                'stats': {'shape_cv': 0.}}]}}
    result = transition_measurements(row, native.simulate, 'E1', 'V1', 670101, 0)
    assert result['effects']['g_to_m/no_geometry_to_mode/1.25'] == pytest.approx(0., abs=1e-12)
    assert result['effects']['m_to_g/no_mode_to_geometry/1.0'] == pytest.approx(0., abs=1e-12)
    assert not result['interface_problems']
    assert all(result['controls'][name]['tested'] for name in ('not_independent', 'not_a_clump'))
    assert result['parent_state']['stability'] == row['record']['candidates'][0]['stats']
