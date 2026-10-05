"""Option B exact detector and full-state equivalence, using reserved fixtures."""
import ctypes
import gzip
import json
from pathlib import Path
import numpy as np
import pytest
from geomind import c4_detect as D, c6_option_b as O
from geomind import c6_r4_field as F, c6_r4_field_assay as A, c6_r4_field_protocol as P
from tools import c6_option_b_compare as C
from tools import c6_r4_design_gate as G

def owner(n=24):
    random=np.random.default_rng(882901);s=P.load_settings()
    o=F.population(random,F.medium(random,s['model']),0,0,n)
    o.z=.55*np.exp(1j*random.uniform(-np.pi,np.pi,25));o.cohorts[0].carrier=o.z.copy()
    o.cohorts[0].selected=(0,1,2)
    return o

@pytest.mark.parametrize('mode',list(F.MODES))
@pytest.mark.parametrize('on',[0.,1.])
@pytest.mark.parametrize('dt',[.005,.0025,.00125])
def test_full_flow_all_modes_and_grids(mode,on,dt):
    o=owner();c=o.cohorts[0];c.mode=mode;c.output=on
    if mode=='no_geometry_to_mode':c.origin=c.x.copy();c.x[0]+=[.1,.2]
    reference,flow=F.advance(o,1.,dt,.005)
    with O.backend('native',audit=True) as audit:
        native,actual=F.advance(o,1.,dt,.005)
        assert np.max(np.abs(actual-flow))<=O.TOLERANCE
        assert native.time==reference.time and audit.calls>0

def test_empty_cohort_field_arithmetic_is_exact():
    o=F.medium(np.random.default_rng(882901),P.load_settings()['model'])
    _,reference=F.advance(o,.2,.005,.005)
    with O.backend('native',audit=True) as audit:
        _,actual=F.advance(o,.2,.005,.005)
        assert np.array_equal(actual,reference)
        assert audit.exact_calls==audit.calls

def test_retained_ancestors_and_zero_mask_keep_full_channels():
    o=owner();o=F.population(np.random.default_rng(552),o,1,0,24)
    o.cohorts[-1].selected=(1,2,3);o.cohorts[-1].output=1.
    _,reference=F.advance(o,.5,.005,.005,_factor=False)
    with O.backend('native',audit=True):
        _,actual=F.advance(o,.5,.005,.005,_factor=False)
        assert np.max(np.abs(actual-reference))<=O.TOLERANCE
        off=o.clone();off.cohorts[-1].output=0.
        intact=F.rhs(o);sham=F.rhs(off)
        assert np.array_equal(intact[50:],sham[50:])
        assert np.max(np.abs((intact-sham)[:50].copy().view('c16')-F.output(o)))<1e-12

def test_components_exact_on_random_and_boundary_graphs():
    lib,_=O.load();random=np.random.default_rng(882901)
    for n in (1,3,6,24):
        for trial in range(20):
            x=random.normal(size=(n,2));locked=random.random((n,n))>.4
            if trial%3==0:x=np.round(x)
            expected=D.components(x,1.5,locked)
            assert np.array_equal(O.components(lib,x,1.5,locked),expected)
    x=np.array([[0.,0.],[1.,0.],[2.5,0.]])
    locks=np.ones((3,3),bool)
    assert np.array_equal(O.components(lib,x,1.5,locks),D.components(x,1.5,locks))
    with pytest.raises(ValueError):O.components(lib,np.empty((0,2)),1.5,np.empty((0,0),bool))

def test_context_restores_reference_after_failure():
    native,components=F.native,D.components
    with pytest.raises(RuntimeError,match='fixture'):
        with O.backend('native'):raise RuntimeError('fixture')
    assert F.native is native and D.components is components
    with pytest.raises(ValueError):
        with O.backend('final'):pass

def test_build_mismatch_stops_without_rebuilding(tmp_path):
    lib=tmp_path/'option_b.dylib';lib.write_bytes(b'not a library')
    (tmp_path/'BUILD.json').write_text(json.dumps({'source_hashes':{},'binary_sha256':'0'*64}))
    with pytest.raises(RuntimeError,match='identity'):O.verify_build(lib)

def test_comparator_rejects_decision_and_numeric_changes():
    a={'chain_complete':False,'checks':[{'passed':True,'error':.01}], 'inputs':{'x':[.1]}}
    b=json.loads(json.dumps(a));b['checks'][0]['error']+=5e-11
    assert C.compare(a,b)['passed']
    b['chain_complete']=True;assert not C.compare(a,b)['passed']
    b=json.loads(json.dumps(a));b['inputs']['x'][0]+=1e-15
    assert not C.compare(a,b)['passed']
    b=json.loads(json.dumps(a));b['checks'][0]['error']=float('nan')
    assert not C.compare(a,b)['passed']
    b=json.loads(json.dumps(a));b['checks'].append(b['checks'][0])
    assert not C.compare(a,b)['passed']

def test_stored_windows_every_detection_decision():
    root=Path(__file__).resolve().parents[1]
    lib,_=O.load();s=P.load_settings();d=s['detector']
    count=0
    for world in (0,1):
        row=json.loads(gzip.decompress((root/f'evidence/c6_r6_design_gate/world_{world:03d}.json.gz').read_bytes()))
        records=[row['initial_source']]
        for turn in row['turns']:
            records.extend(turn['before_formation'] or [])
            for episodes in turn['episodes'].values():records.extend(episodes)
        for record in records:
            snap=record['qualified_states'][0];cohorts=snap['cohorts'];n=len(cohorts[-1]['theta'])
            offset=50+sum(3*len(c['theta'])+50 for c in cohorts[:-1])
            flow=np.array(record['qualification_window']);x=flow[:,offset:offset+2*n].reshape(-1,n,2);th=flow[:,offset+2*n:offset+3*n]
            locks=D.locked_pairs(th,d['lock_std'])
            for positions in x:
                assert np.array_equal(O.components(lib,positions,d['link_factor'],locks),D.components(positions,d['link_factor'],locks))
                count+=1
    assert count>1000

def test_native_covariance_and_selection_boundary():
    s=P.load_settings()
    with O.backend('native',audit=True):
        assert G.equivariance(s)['passed']
