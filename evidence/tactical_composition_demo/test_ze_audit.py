"""Checks of the 0e task-V3 code path, added after the recorded run (2026-10-04 recheck: the registered tests did not cover it). A NEW file; the registered files are
hashed into run_0e and are not edited. Run once:

    .venv/bin/python -m pytest -q -p no:cacheprovider evidence/tactical_composition_demo/test_ze_audit.py
"""
import sys
from pathlib import Path

import numpy as np
import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import tactics as T  # noqa: E402
import tactics_e2 as T2  # noqa: E402
import verify_run_0e as V  # noqa: E402
import zd_models as Z  # noqa: E402
import ze_core as E  # noqa: E402
import ze_run as R  # noqa: E402


@pytest.fixture(scope='module')
def v3():
    pool = T2.collect('V3', np.random.default_rng(11), 8)
    return pool, Z.Arrays(pool, T2.labels('V3', pool))


def test_the_batch_doctrine_equals_the_scalar_doctrine_and_the_labels(v3):
    pool, A = v3
    batch = T2.doctrine_scores_batch('V3')(A)
    scalar = T2.doctrine_scores('V3')
    for k in range(0, A.n, max(1, A.n//25)):
        assert np.allclose(batch[k], scalar(pool['own'][k], pool['enemies'][k]))
    assert np.array_equal(np.argmax(batch, axis=1), A.target)                     # the oracle AIM picks exactly the labelled target


def test_the_oracle_assembly_plays_exactly_as_the_v3_teacher_in_the_v3_world():
    entropy = 2**90+41
    oracle = E.Assembly(E.AimOracle(T2.doctrine_scores_batch('V3')), E.MoveOracle())
    kw = dict(world_fn=T2.world_fn('V3'), mixes=T2.MIXES)
    for opp in ('rush', 'kiter'):
        a = E.play_cell(oracle.policy, opp, entropy, 0, 6, **kw)
        b = E.play_cell(lambda rng: T2.teacher_policy('V3'), opp, entropy, 0, 6, **kw)
        assert a == b
    w = T2.world_fn('V3')(T2.MIXES[0], T2.MIXES[1], np.random.default_rng(1))
    assert w.hpmax[0].tolist() == [T2.GLASS[t]['hp'] for t in T2.MIXES[0]]       # the V3 unit statistics are the ones used


@pytest.mark.parametrize('kind,value', [('default', None), ('wrong', None), ('zero', None), ('noise', 0.1), ('wrongfrac', 0.5), ('scale', 2.0), ('reverse', None)])
def test_a_wire_fault_never_changes_the_attack_target(v3, kind, value):
    _, A = v3
    aim = E.AimOracle(T2.doctrine_scores_batch('V3'))
    intact, _, _ = E.Assembly(aim, E.MoveOracle()).act(A, np.random.default_rng(0))
    faulted, _, _ = E.Assembly(aim, E.MoveOracle(), E.Wire(kind, value, 4.97)).act(A, np.random.default_rng(0))
    assert np.array_equal(intact, faulted)
    policy = E.Assembly(aim, E.MoveOracle(), E.Wire(kind, value, 4.97)).policy(np.random.default_rng(0))
    k = int(np.flatnonzero(A.alive.sum(1) > 1)[0])
    assert policy(A.own[k], A.en[k])[1] == int(intact[k])


def test_a_tiny_v3_seed_scores_the_teacher_perfectly_and_its_saved_models_reload(tmp_path):
    cfg = dict(R.BASE, **R.SMOKE, ref_distance=4.97, run_dir=str(tmp_path))
    rec = R.run_seed(cfg, 2**90+43, 0)
    assert rec['fixed']['OO']['a_joint'] == 1.0
    te = T2.collect('V3', V.stream(2**90+43, 2, 0), cfg['test_episodes'])
    A = Z.Arrays(te, T2.labels('V3', te))
    for name in ('L', 'J', 'Fp', 'Fflat'):
        z = np.load(tmp_path/'models'/('seed_00_%s.npz' % name))
        if name in ('L', 'J'):
            m = Z.Wired(name)
            m.scorer, m.head = V._net(Z.Net, z, 'scorer'), V._net(Z.Net, z, 'head')
            for k in ('xa', 'ya', 'xm', 'ym'):
                setattr(m, k, V._std(z, k))
            score = E.joint3(*E.Assembly(E.AimWired(m, name), E.MoveWired(m, name)).act(A, np.random.default_rng(0))[:2], A)['a_joint']
            assert score == rec['fixed'][name+name]['a_joint']
        else:
            import ze_flat as F
            m = F.FlatPlus('perslot' if name == 'Fp' else 'mse')
            m.net = V._net(F.DeepNet, z, 'net')
            m.xs, m.ss, m.ms = V._std(z, 'xs'), V._std(z, 'ss'), V._std(z, 'ms')
            assert E.joint3(*m.act(A), A)['a_joint'] == rec['fixed'][name]['a_joint']
