"""Small synthetic controls tests only; no checkpoints, data replay or fights."""
import sys
sys.dont_write_bytecode = True
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_switches import fixture, model as old_model
from controls import neighbor_rule
from controls_model import ControlsPolicy
from models import initial
import numpy as np
import torch

torch.set_num_threads(1)


def model(switch):
    torch.manual_seed(16)
    return ControlsPolicy('N2', switch).double().eval()


def test_intact_and_output_only_reuse_multitick():
    a = model('intact'); b = old_model('intact')
    no_bonus = model('intact_no_bonus'); no_fire = model('intact_no_fire_window')
    x = fixture(); states = [initial('N2', x['ids'], torch.float64) for _ in range(4)]
    with torch.inference_mode():
        for _ in range(12):
            out = []
            for i, m in enumerate((a, b, no_bonus, no_fire)):
                y, states[i], _ = m.tick(**x, state=states[i]); out.append(y)
            assert all(torch.equal(states[0], v) for v in states[1:])
            assert all(torch.equal(out[0][k], out[1][k]) for k in out[0])
            assert torch.equal(a.last_diagnostics['target_without_bonus'], out[2]['target'])
            assert torch.equal(a.last_diagnostics['fire_without_window'], out[3]['fire'])
            assert all(torch.equal(out[0][k], out[2][k]) for k in out[0] if k!='target')
            assert all(torch.equal(out[0][k], out[3][k]) for k in out[0] if k!='fire')
            x['pos'] += .1; x['query'] += .01


def test_indicator_has_identical_k_zero_state_and_exact_bonus():
    a = model('indicator_no_phase'); b = old_model('k_zero'); x = fixture()
    sa = initial('N2', x['ids'], torch.float64); sb = sa.clone()
    with torch.inference_mode():
        for _ in range(5):
            ya, sa, _ = a.tick(**x, state=sa); yb, sb, _ = b.tick(**x, state=sb)
            assert torch.equal(sa, sb)
            assert all(torch.equal(ya[k], yb[k]) for k in ya if k!='target')
            expected = torch.tensor([[0.,2.,2.], [0.,2.,2.], [0.,2.,0.]], dtype=torch.float64)
            assert torch.equal(a.last_diagnostics['target_bonus'], expected)
            assert torch.equal(ya['target'], a.last_diagnostics['target_without_bonus']+expected)
        x['assignments'] = torch.zeros_like(x['assignments'])
        a.tick(**x, state=sa)
        assert torch.count_nonzero(a.last_diagnostics['target_bonus'])==0
        x['assignments'][:] = 20; x['pos'] *= 100
        a.tick(**x, state=sa)
        assert torch.count_nonzero(a.last_diagnostics['target_bonus'])==0


def test_forcing_only_retains_k_and_raw_head_feature():
    a = model('forcing_only_cut'); b = model('intact'); x = fixture()
    state = initial('N2', x['ids'], torch.float64)
    with torch.inference_mode():
        _, out, _ = a.tick(**x, state=state); b.tick(**x, state=state)
    assert torch.equal(a.law, b.law)
    assert torch.equal(a.last_diagnostics['forcing'], b.last_diagnostics['forcing'])
    assert torch.count_nonzero(a.last_diagnostics['phase_forcing']) == 0
    assert torch.count_nonzero(a.last_diagnostics['coupling']) > 0
    assert torch.equal(out[:,5], a.last_diagnostics['forcing'])
    assert not torch.equal(out[:,0], state[:,0])


def test_shuffle_preserves_public_role_multiset_and_is_reproducible():
    x = fixture(); x['tokens'][x['own'],3:6] = 0
    x['tokens'][x['own'][:2],3] = 1; x['tokens'][x['own'][2:],4] = 1
    a = model('role_shuffle'); b = model('intact'); other = model('role_shuffle')
    state = initial('N2', x['ids'], torch.float64)
    with torch.inference_mode():
        changed = False
        for _ in range(12):
            _, sa, _ = a.tick(**x, state=state); _, sb, _ = b.tick(**x, state=state)
            _, sc, _ = other.tick(**x, state=state)
            assert torch.equal(sa, sc)
            assert torch.equal(sa[:2,0].sort().values, sb[:2,0].sort().values)
            assert torch.equal(sa[2:,0], sb[2:,0])
            changed |= not torch.equal(sa[:,0], sb[:,0])
            state = sa
        assert changed


def test_synchrony_forces_zero_each_tick_and_indicator_bonus():
    x = fixture(); a = model('forced_synchronous'); state = initial('N2', x['ids'], torch.float64)
    with torch.inference_mode():
        for _ in range(5):
            y, state, _ = a.tick(**x, state=state)
            assert torch.count_nonzero(state[:,0])==0
            assert torch.equal(a.last_diagnostics['target_bonus'], torch.tensor([[0.,2.,2.],[0.,2.,2.],[0.,2.,0.]], dtype=torch.float64))
            assert torch.equal(a.last_diagnostics['fire_window_bonus'], torch.tensor([[2.,-2.,2.]]*3,dtype=torch.float64))


def test_neighbour_rule_plurality_ties_fallback_and_no_enemy():
    pos = np.array([[0.,0.], [100.,0.], [200.,0.]])
    order = np.array([[1,2],[0,2],[0,1]]); mask = np.ones((3,2), dtype=bool)
    assignments = np.array([20,20,21]); enemy_pos=np.array([[50.,0.],[400.,0.]])
    choice, support = neighbor_rule(pos,enemy_pos,assignments,order,mask,[20,21])
    assert choice.tolist()==[1,1,1] and support[0]=={20,21}
    choice,_ = neighbor_rule(pos,enemy_pos,assignments,order,np.zeros_like(mask),[20,21])
    assert choice.tolist()==[1,1,1]
    choice,_ = neighbor_rule(pos,np.array([[-50.,0.],[50.,0.]]),np.zeros(3),order,mask,[21,20])
    assert choice[0]==2  # equal distance: lower persistent ID wins
    choice,support = neighbor_rule(pos,np.empty((0,2)),assignments,order,mask,[])
    assert choice.tolist()==[0,0,0] and not any(support)


def test_singleton_and_strict_300px_graph():
    x = fixture((1,)); a = model('indicator_no_phase')
    with torch.inference_mode():
        _, state, _ = a.tick(**x, state=initial('N2',x['ids'],torch.float64))
        assert a.last_diagnostics['neighbor_count'].tolist()==[0]
        assert torch.count_nonzero(a.last_diagnostics['target_bonus'])==0
        x = fixture((1,2)); x['pos']=torch.tensor([[0.,0.],[300.,0.]],dtype=torch.float64)
        a.tick(**x,state=initial('N2',x['ids'],torch.float64))
        assert a.last_diagnostics['neighbor_count'].tolist()==[0,0]
        x['pos'][1,0]=299.99
        a.tick(**x,state=initial('N2',x['ids'],torch.float64))
        assert a.last_diagnostics['neighbor_count'].tolist()==[1,1]
