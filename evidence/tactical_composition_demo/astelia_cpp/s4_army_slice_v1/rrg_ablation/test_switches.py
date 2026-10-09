"""Small synthetic inference checks; no project datasets or fights."""
import sys
sys.dont_write_bytecode = True
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import check as c
import torch
from models import Policy, initial, remap
from ablation_model import AblationPolicy

torch.set_num_threads(1)


def fixture(ids=(1, 2, 3)):
    torch.manual_seed(82)
    n = len(ids)
    tokens = torch.randn(n+2, 64, dtype=torch.float64)
    tokens[-2, 1] = 20/256; tokens[-1, 1] = 21/256
    return dict(tokens=tokens, query=torch.randn(n, 128, dtype=torch.float64),
                own=torch.arange(n), enemy=torch.tensor([n, n+1]),
                pos=torch.tensor([[0., 0.], [50., 0.], [80., 50.]][:n], dtype=torch.float64),
                speeds=torch.full((n,), 100., dtype=torch.float64), assignments=torch.tensor([20, 20, 21][:n]),
                ids=list(ids), dt=1/30, refresh=True, cache=None)


def model(switch):
    torch.manual_seed(16)
    return AblationPolicy('N2', switch).double().eval()


def test_intact_matches_pinned_multi_tick():
    m = model('intact'); original = Policy('N2').double().eval(); original.load_state_dict(m.state_dict())
    x = fixture(); a = initial('N2', x['ids'], torch.float64); b = a.clone()
    for tick in range(20):
        x['pos'] = x['pos'] + torch.tensor([[0., 0.], [1., 0.], [0., 2.]])
        x['refresh'] = tick % 6 == 0
        ya, a, cache_a = m.tick(**x, state=a)
        yb, b, cache_b = original.tick(**x, state=b)
        assert torch.equal(a, b) and torch.equal(cache_a, cache_b)
        assert all(torch.equal(ya[k], yb[k]) for k in ya)
        x['cache'] = cache_a


def test_zero_coupling_retains_forcing_and_changes_phase():
    x = fixture(); zero = model('k_zero'); intact = model('intact'); state = initial('N2', x['ids'], torch.float64)
    _, out, _ = zero.tick(**x, state=state)
    assert torch.allclose(out[:, 0], state[:, 0]+x['dt']*zero.last_diagnostics['forcing'])
    assert torch.allclose(zero.last_diagnostics['coupling'], torch.zeros(3, dtype=torch.float64))
    _, baseline, _ = intact.tick(**x, state=state)
    assert not torch.allclose(out[:, 0], baseline[:, 0])


def test_frozen_phase_persists_with_live_inputs_and_removal():
    x = fixture(); m = model('frozen_phase'); state = initial('N2', x['ids'], torch.float64); theta = state[:, 0].clone()
    for _ in range(5):
        _, state, _ = m.tick(**x, state=state); x['query'] += .5
        assert torch.equal(state[:, 0], theta)
    surviving = remap('N2', state, x['ids'], [1, 3])
    assert torch.equal(surviving[:, 0], theta[[0, 2]])


def test_reset_disabled_is_exact_noop():
    x = fixture(); a = model('intact'); b = model('reset_disabled'); sa = initial('N2', x['ids'], torch.float64); sb = sa.clone()
    for _ in range(8):
        ya, sa, _ = a.tick(**x, state=sa); yb, sb, _ = b.tick(**x, state=sb)
        assert torch.equal(sa, sb) and all(torch.equal(ya[k], yb[k]) for k in ya)


def test_no_mode_geometry_changes_only_drift():
    x = fixture(); a = model('intact'); b = model('no_mode_to_geometry'); state = initial('N2', x['ids'], torch.float64)
    ya, sa, _ = a.tick(**x, state=state); yb, sb, _ = b.tick(**x, state=state)
    assert torch.equal(sa, sb) and torch.count_nonzero(ya['drift'])
    assert torch.count_nonzero(yb['drift']) == 0
    assert all(torch.equal(ya[k], yb[k]) for k in ya if k != 'drift')


def test_no_geometry_mode_is_omega_only_even_after_geometry_change():
    x = fixture(); a = model('no_geometry_to_mode'); state = initial('N2', x['ids'], torch.float64)
    with torch.no_grad(): a.law[4] = .25
    start = state[:, 0].clone(); omega = 2*torch.tanh(a.law[4])
    for _ in range(5):
        _, state, _ = a.tick(**x, state=state); x['pos'] *= 1.5; x['query'] += 1
    assert torch.allclose(state[:, 0], start+5*x['dt']*omega)
    assert torch.count_nonzero(a.last_diagnostics['phase_forcing']) == 0
    assert torch.count_nonzero(a.last_diagnostics['forcing']) > 0
    assert torch.equal(state[:, 5], a.last_diagnostics['forcing'])
    assert torch.allclose(a.last_diagnostics['coupling'], torch.zeros(3, dtype=torch.float64))


def test_frozen_graph_survives_geometry_change_and_death():
    x = fixture(); a = model('topology_only'); b = model('intact'); state = initial('N2', x['ids'], torch.float64)
    ya, sa, _ = a.tick(**x, state=state); yb, sb, _ = b.tick(**x, state=state)
    assert torch.equal(sa, sb) and all(torch.equal(ya[k], yb[k]) for k in ya)
    x['pos'] = x['pos']*100
    _, sa, _ = a.tick(**x, state=state); _, sb, _ = b.tick(**x, state=state)
    assert a.last_diagnostics['neighbor_count'].tolist() == [2, 2, 2]
    assert b.last_diagnostics['neighbor_count'].tolist() == [0, 0, 0]
    assert not torch.equal(sa, sb)
    x = fixture((1, 3)); state = remap('N2', sa, [1, 2, 3], [1, 3])
    a.tick(**x, state=state)
    assert a.last_diagnostics['neighbor_count'].tolist() == [1, 1]


def test_windows_match_outcome_selection_and_phase_singletons():
    assert c.selected_starts(1231, 4) == [0, 360, 720, 1170]
    stats = c.PhaseStats(); stats.add(c.np.array([0., 0.]), [0., 0.], [0., 0.], .1)
    stats.add(c.np.array([0., c.math.pi]), [0., 0.], [0., 0.], .9)
    assert abs(stats.result()['order_parameter']['mean']-.5) < 1e-12
    assert stats.result()['pair_fraction_within_pi_over_6']['mean'] == .5
    stats.add(c.np.array([0.]), [0.], [0.], .5)
    assert stats.result()['singleton_frames'] == 1


def test_cached_packing_matches_pinned_inputs_and_forward(monkeypatch):
    rows = []
    for tick in range(10):
        units = [[uid, side, role, 250+side*220+tick*.5, 200+role*50, 15, 0, 100, 100, 10, 60, 300, 40, 0, 1, 0, tick, tick*2, 0, tick, tick*2, 0, 0]
                 for side in (0, 1) for role in range(3) for uid in [side*3+role+1] if not (tick >= 6 and uid == 2)]
        rows.append(dict(stageA=True, t=tick/30, dt=1/30, width=1000, height=800, units=units,
                         own=[[u[0], 0, .2, .2, 1, 100, 0, False, 3, .4] for u in units if u[1] == 0],
                         shells=[], shots=[], fields=[], casts=[], history={str(u[0]): [tick*.01]*16 for u in units}, pairModes={'1:4': True}))
    cached = c.PackedInputs()
    for row in rows:
        for kind in ('N1', 'N1h', 'N1r', 'N2'):
            actual, ids, enemies = cached.pack(row, kind); expected, ei, ee = c.pack(row, kind)
            assert ids == ei and enemies == ee
            assert all(c.np.array_equal(actual[k], expected[k]) for k in actual)
    torch.manual_seed(4); a = Policy('N2').float().eval(); b = Policy('N2').float().eval(); b.load_state_dict(a.state_dict())
    def replay(m):
        context = (initial('N2', []), [], None, (0, [])); out = []
        with torch.inference_mode():
            for row in rows:
                state, ids, cache, next_frame = context
                y, state, ids, enemies, cache, next_frame, _ = c.forward(m, row, state, ids, cache, next_frame)
                context = state, ids, cache, next_frame; out.append((y, state))
        return out
    expected = replay(a)
    monkeypatch.setattr(c.training, 'pack', cached.pack); monkeypatch.setattr(c.training, 'tensor', cached.tensor)
    actual = replay(b)
    assert all(torch.equal(sa, sb) and all(torch.equal(ya[k], yb[k]) for k in ya) for (ya, sa), (yb, sb) in zip(actual, expected))
