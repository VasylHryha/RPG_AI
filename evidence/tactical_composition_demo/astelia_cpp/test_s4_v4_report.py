import pytest
from s4_v4_trace_summary import summarize


def test_trace_summary_excludes_nulls_and_counts_pair_vs_unit_reversals():
    def unit(modes,value,reason=None):
        return dict(id=1,focus=20,reference=20,feasibility=value,undefinedReason=reason,
            pairs=[dict(enemy=20+i,mode=m,remainingHold=1) for i,m in enumerate(modes)])
    records=[dict(dt=1,units=[unit(['commit','commit'],1)],holdEvents=[dict(id=1,enemy=20,reason='started',duration=0,planned=3)]),
             dict(dt=1,units=[unit(['escape','escape'],None,'zero_displacement')],holdEvents=[dict(id=1,enemy=20,reason='target_band',duration=1,planned=3)])]
    result=summarize(records)
    assert result['counts']['pair_reversals']==2 and result['counts']['unit_reversal_ticks']==1
    assert result['commitment_reversals_per_unit_minute']==30
    assert result['mean_completed_hold_seconds']==1 and result['mean_planned_hold_seconds']==3
    assert result['feasibility']['mean']==1 and result['feasibility']['undefined']=={'zero_displacement':1}
    assert result['censored_holds_at_terminal']==2 and result['focus_usage']==1


def test_trace_empty_and_invalid_cosine():
    assert summarize([])['feasibility']['mean'] is None
    with pytest.raises(ValueError,match='invalid cosine'):
        summarize([dict(dt=1,holdEvents=[],units=[dict(id=1,focus=None,reference=20,pairs=[],feasibility=2)])])


def test_replay_instrumentation_does_not_change_audit_identity():
    from s4_v4_report import key
    spec=dict(arm='morale',skeleton='v4',seed=1,params={},swapSides=False,endCounts=True)
    assert key(spec)==key(dict(spec,trace=True,decisionDiagnostics=True))


def test_approved_design_is_a_guarded_immutable_snapshot(tmp_path):
    import hashlib,subprocess
    import s4_v4 as V
    pin=V.ROOT/'S4_V4_DESIGN_PIN.md'
    approved=subprocess.check_output(['git','show','914dda4:evidence/tactical_composition_demo/DESIGN_0G.md'],cwd=V.ROOT)
    assert pin.read_bytes()==approved
    copied=tmp_path/'approved.md';copied.write_bytes(approved)
    expected={str(copied):hashlib.sha256(approved).hexdigest()}
    V.check_inputs(expected)
    live=tmp_path/'live.md';live.write_bytes(approved+b'\nLater unrelated planning\n')
    V.check_inputs(expected) # unrelated live planning does not alter the approved input
    copied.write_bytes(approved+b'\nChanged contract\n')
    with pytest.raises(RuntimeError,match='input changed'):V.check_inputs(expected)
