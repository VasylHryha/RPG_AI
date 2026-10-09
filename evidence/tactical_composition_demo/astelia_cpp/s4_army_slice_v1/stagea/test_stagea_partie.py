"""Adversarial near-tie certification and immutable recovery checks."""
import sys
from pathlib import Path
import numpy as np
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parent))
from parity import compare, parity_passes
import parity_recovery  # Import durable paths before fixtures monkeypatch the legacy module.


def bank(fire=(1.,0.,0.), target=(1.,0.,0.)):
    row=np.zeros((1,13),dtype=np.float64)
    row[0,3:6]=fire;row[0,10:]=target
    return row


def verdict(a,b):
    return dict(float32_export=compare(a,b,near_ties=True),native_float64=compare(b,b))


@pytest.mark.parametrize('head',['fire','target'])
def test_measured_head_bound_and_gap(head):
    reference=bank(**{head:(1.,1.-1e-5,0.)});observed=reference.copy()
    offset=3 if head=='fire' else 10
    observed[0,offset]-=8e-6;observed[0,offset+1]+=8e-6
    result=verdict([observed],[reference]);detail=result['float32_export']['mismatches'][0]
    assert detail['head']==head and detail['float64_top2_gap']==pytest.approx(1e-5)
    assert detail['bound']==pytest.approx(1.6e-5) and detail['certified']
    assert parity_passes(result)
    # This same argmax flip MUST fail the deployed float64 gate.
    result['native_float64']=compare([reference],[observed])
    assert not parity_passes(result)


def test_nonrunner_up_cannot_hide_behind_unrelated_near_tie():
    reference=bank(target=(1.,1.-1e-7,.1));observed=reference.copy();observed[0,12]=1.1
    result=verdict([observed],[reference])
    detail=result['float32_export']['mismatches'][0]
    assert detail['float64_top2_gap']<1e-4
    assert detail['float64_selected_class_deficit']==pytest.approx(.9)
    assert detail['bound']==1e-4 and not detail['certified']
    assert not parity_passes(result)


def test_large_gap_mismatch_fails_measured_bound_with_ceiling():
    result=verdict([bank(fire=(0.,1.,0.))],[bank()])
    detail=result['float32_export']['mismatches'][0]
    assert detail['float64_top2_gap']==1. and detail['bound']==1e-4
    assert not parity_passes(result)


def test_head_error_cannot_borrow_from_another_head_or_numeric_output():
    reference=bank();observed=reference.copy();observed[0,0]=100.
    result=compare([observed],[reference],near_ties=True)
    assert result['max_abs_error']==100. and result['near_tie_bounds']==dict(fire=0.,target=0.)


def test_exact_bound_is_inclusive():
    reference=bank(fire=(1e-4,0.,-1.));observed=reference.copy()
    observed[0,3]=0.;observed[0,4]=1e-4
    result=verdict([observed],[reference])
    assert result['float32_export']['mismatches'][0]['float64_top2_gap']==1e-4
    assert parity_passes(result)


def test_single_target_and_empty_rows_and_variable_width():
    a=np.zeros((0,11));b=bank(target=(0.,0.,0.))
    result=verdict([a,b],[a,b]);assert parity_passes(result)
    assert result['float32_export']['rows']==1 and result['float32_export']['mismatches']==[]


@pytest.mark.parametrize('value',[np.nan,np.inf,-np.inf])
def test_nonfinite_fails_even_without_argmax_change(value):
    a=bank();a[0,0]=value
    with pytest.raises(RuntimeError,match='nonfinite'):compare([a],[bank()],near_ties=True)


def test_dimension_mismatch_fails():
    with pytest.raises(RuntimeError,match='dimensions'):compare([bank()],[])
    with pytest.raises(RuntimeError,match='dimensions'):compare([np.zeros((1,10))],[np.zeros((1,10))])


def test_deployed_numeric_tolerance_is_unchanged():
    result=verdict([bank()],[bank()]);result['native_float64']['max_abs_error']=1.01e-8
    assert not parity_passes(result)


def test_uncertified_mismatch_fails():
    reference=bank(target=(1.,1.-1e-5,0.));observed=reference.copy()
    observed[0,10]-=8e-6;observed[0,11]+=8e-6
    result=verdict([observed],[reference])
    assert result['float32_export']['uncertified_mismatches']==0
    result['float32_export']['mismatches'][0]['certified']=False
    assert not parity_passes(result)


def test_recovery_preserves_old_evidence_and_source_gate(tmp_path,monkeypatch):
    from test_stagea_parmem import recovery_fixture
    recovery,_=recovery_fixture(tmp_path,monkeypatch)
    # No new registration: the existing memory recovery keeps its strict gate.
    assert recovery.checked_inference_budget()['status']=='ADMITTED'


@pytest.mark.parametrize('defect',['old_rule','missing_arm','duplicate','uncertified','native_flip'])
def test_readout_rejects_stale_or_incomplete_parity(monkeypatch,defect):
    import copy
    import readout
    from parity import PARITY_RULE
    records=[dict(arm=arm,fight='validation_fixture',status='PASS',parity_rule=PARITY_RULE,
                  **verdict([bank()],[bank()])) for arm in readout.ARMS]
    proof=dict(status='PASS',binary={'identity':'fixed'},exports={arm:'hash' for arm in readout.ARMS},
               budget_sha256='hash',index_sha256='hash',parity_rule=PARITY_RULE,records=copy.deepcopy(records))
    if defect=='old_rule':proof.pop('parity_rule')
    elif defect=='missing_arm':proof['records'].pop()
    elif defect=='duplicate':proof['records'][-1]=proof['records'][0]
    elif defect=='uncertified':proof['records'][0]['float32_export']['uncertified_mismatches']=1
    else:proof['records'][0]['native_float64']['categorical_mismatches']=1
    monkeypatch.setattr(readout,'read',lambda path:dict(fights=[dict(tag='validation_fixture',split='validation')]) if path.name=='INDEX.json' else proof)
    monkeypatch.setattr(readout,'identity',lambda:dict(identity='fixed'))
    monkeypatch.setattr(readout,'sha',lambda path:'hash')
    with pytest.raises(RuntimeError,match='certified full-sequence parity'):readout.parity_gate()


def tie_recovery_fixture(tmp_path,monkeypatch):
    from test_stagea_parmem import recovery_fixture
    legacy,now=recovery_fixture(tmp_path,monkeypatch)
    import parity_recovery as tie
    from common import read,sha,write
    monkeypatch.setattr(tie,'HERE',tmp_path)
    monkeypatch.setattr(tie,'CPP',tmp_path.parent)
    monkeypatch.setattr(tie,'LOCAL',tmp_path/'_local')
    monkeypatch.setattr(tie,'MEMORY_RECOVERY',legacy.RECOVERY)
    monkeypatch.setattr(tie,'RECOVERY',tmp_path/'RECOVERY_STAGEA_PARTIE.json')
    monkeypatch.setattr(tie,'FAILURE',tmp_path/'PARITY_RUN_5838d7b675e8dc7e.json')
    monkeypatch.setattr(tie,'FAILED_PROOF',tmp_path/'_local/parity/N2J0_validation_0083.receipt.json')
    monkeypatch.setattr(tie,'sources',lambda:now)
    # Binary identity is unchanged by this Python-only recovery.
    binary=legacy.identity().copy();binary['sources']=binary['sources'].copy()
    monkeypatch.setattr(legacy,'identity',lambda:binary)
    manifest=dict(binary=binary,budget_sha256=sha(tmp_path/'_local/TRAIN_BUDGET.json'),
                  index_sha256=sha(tmp_path/'_local/INDEX.json'),
                  exports=read(tmp_path/'PARITY_RUN_c7136052e0485bba.json')['manifest']['exports'])
    write(tie.FAILURE,dict(status='STOP_RESUMABLE',error='RuntimeError: categorical/numeric export parity defect',manifest=manifest))
    write(tie.FAILED_PROOF,dict(status='FAIL',arm='N2J0',fight='validation_0083',manifest=manifest,
          native_float64=dict(categorical_mismatches=0,max_abs_error=1e-14),float32_export=dict(categorical_mismatches=1)))
    now[next(k for k in now if k.endswith('/parity.py'))]='near_tie_revision'
    import jobs,contextlib
    monkeypatch.setattr(jobs,'locked',contextlib.nullcontext)
    return tie,now


@pytest.mark.parametrize('path',['_local/parity/N2J0_validation_0083.receipt.json','PARITY_RUN_5838d7b675e8dc7e.json','RECOVERY.json','_local/training/N2.pt'])
def test_tie_recovery_registration_idempotent_and_rejects_preserved_drift(tmp_path,monkeypatch,path):
    tie,_=tie_recovery_fixture(tmp_path,monkeypatch)
    from common import sha
    assert tie.register()['status']=='ADMITTED'
    before=sha(tie.RECOVERY)
    assert tie.register()['status']=='ADMITTED' and sha(tie.RECOVERY)==before
    target=tmp_path/path;target.write_bytes(target.read_bytes()+b' ')
    with pytest.raises(RuntimeError,match='drift'):tie.checked()


def test_tie_recovery_rejects_source_and_binary_drift(tmp_path,monkeypatch):
    tie,now=tie_recovery_fixture(tmp_path,monkeypatch);tie.register()
    key=next(k for k in now if k.endswith('/parity.py'));old=now[key];now[key]='unregistered'
    with pytest.raises(RuntimeError,match='registration drift'):tie.checked()
    now[key]=old;now['trainer.py']='bad'
    with pytest.raises(RuntimeError,match='unauthorized source'):tie.checked()
    del now['trainer.py']
    import parmem_recovery as legacy
    binary=legacy.identity().copy();binary['binary_sha256']='drift'
    monkeypatch.setattr(legacy,'identity',lambda:binary)
    with pytest.raises(RuntimeError,match='native build identity drift'):tie.checked()
