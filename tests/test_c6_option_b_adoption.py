"""Decision 0032 kernel selection, bounded vector scratch, and analyzer guards."""
import copy
import ctypes as ct
import json
from pathlib import Path
import numpy as np
import pytest
from geomind import c6_option_b as O
from tools import build_c6_option_b as B, c6_option_b_adoption_analyze as A
from test_c6_option_b import owner, raw_flow


def test_default_and_declared_switch(monkeypatch):
    monkeypatch.delenv('C6_OPTION_B_KERNEL',raising=False)
    assert B.kernel()=='inexact'
    vector,vr=O.load()
    assert vector.option_b_inexact_kernel()==1 and vr['kernel']=='inexact'
    assert vr['macos_build']==B.PINNED_MACOS
    monkeypatch.setenv('C6_OPTION_B_KERNEL','exact')
    scalar,sr=O.load()
    assert scalar.option_b_inexact_kernel()==0 and sr['kernel']=='exact'
    assert scalar is not vector and sr['binary_sha256']!=vr['binary_sha256']
    assert '-framework' not in sr['flags'] and 'Accelerate' in vr['flags']
    monkeypatch.setenv('C6_OPTION_B_KERNEL','unknown')
    with pytest.raises(ValueError,match='Unknown'):O.load()


def test_receipt_kernel_and_os_tampering_refused(monkeypatch):
    monkeypatch.setenv('C6_OPTION_B_KERNEL','inexact')
    original=O.json.loads
    def tampered(raw):
        rec=original(raw);rec['kernel']='exact';return rec
    monkeypatch.setattr(O.json,'loads',tampered)
    with pytest.raises(RuntimeError,match='identity mismatch'):O.load()
    monkeypatch.setattr(O.json,'loads',original)
    monkeypatch.setattr(B,'macos_build',lambda:{**B.PINNED_MACOS,'BuildVersion':'different'})
    with pytest.raises(RuntimeError,match='macOS build changed'):O.load()


@pytest.mark.parametrize('mode',['intact','no_r','no_geometry_to_mode','no_mode_to_geometry'])
@pytest.mark.parametrize('dt',[.005,.0025,.00125])
def test_inexact_full_flow_and_repeated_cache(mode,dt,monkeypatch):
    monkeypatch.setenv('C6_OPTION_B_KERNEL','inexact')
    lib,_=O.load();ref,_=O.reference();state=owner();state.cohorts[0].mode=mode
    if mode=='no_geometry_to_mode':state.cohorts[0].origin=state.cohorts[0].x.copy()
    state.cohorts[0].output=1.
    exact=raw_flow(ref,state,steps=20,dt=dt)
    first=raw_flow(lib,state,steps=20,dt=dt);second=raw_flow(lib,state,steps=20,dt=dt)
    assert np.max(np.abs(first-exact))<=1e-10
    assert np.array_equal(first.view('u8'),second.view('u8'))


@pytest.mark.parametrize('n,ns',[(64,64),(65,25),(24,65),(65,65)])
def test_vector_gaussian_guard_boundary_and_scalar_fallback(n,ns,monkeypatch):
    # 64 distinct coordinates use all buffers; 65 must bypass them. Exercise
    # both rhs and integration and mode-2 fixed origins with selected emission.
    monkeypatch.setenv('C6_OPTION_B_KERNEL','inexact');lib,_=O.load();ref,_=O.reference()
    width=2*ns+3*n+2*ns
    q=np.column_stack((np.arange(ns)*.01,np.arange(ns)*.02)).ravel()
    y=np.zeros(width);y[2*ns:2*ns+2*n]=np.column_stack((np.arange(n)*.001,np.arange(n)*.002)).ravel()
    y[2*ns+2*n:2*ns+3*n]=np.arange(n)*.03
    omega=np.zeros(ns);psi=np.zeros(8*ns);adj=np.zeros(ns*ns,dtype='i4')
    rates=np.zeros(n);mask=np.zeros(n);mask[:3]=1.;modes=np.array([2],dtype='i4')
    origins=y[2*ns:2*ns+2*n].copy();p=np.array([-.18,.05,.02,.3,.2,.05,2.,.8,1.])
    arrays=(y,q,omega,psi,adj,rates,mask,modes,origins,p)
    ptr=[a.ctypes.data_as(ct.POINTER(ct.c_int if i in (4,7) else ct.c_double)) for i,a in enumerate(arrays)]
    for name in ('field_rhs','field_run'):
        args=(ns,n,1,0.) if name=='field_rhs' else (ns,n,1,0.,.00125,2,1)
        expected=np.empty(width if name=='field_rhs' else width*3);actual=np.empty_like(expected)
        assert getattr(ref,name)(*args,*ptr,expected.ctypes.data_as(O.PTR))==0
        assert getattr(lib,name)(*args,*ptr,actual.ctypes.data_as(O.PTR))==0
        assert np.isfinite(actual).all() and np.max(np.abs(actual-expected))<=1e-10


def test_dimension_guard_rejects_pair_overflow_before_access(monkeypatch):
    monkeypatch.setenv('C6_OPTION_B_KERNEL','inexact');lib,_=O.load()
    assert lib.field_rhs(1,100000,1,0.,*[None]*11)==3
    assert lib.field_run(1,100000,1,0.,.001,1,1,*[None]*11)==3


def test_nonfinite_counts_reject_matching_nan_and_inf():
    for bad in (float('nan'),float('inf'),-float('inf')):
        value={'nested':[bad,0.,True]}
        out=dict(bools=0,ints=0,strings=0,digests=0,digests_changed=0,semantic_digests=0,
                 discrete=[],monitor=A.new_stats(),other=A.new_stats())
        A.walk(value,value,'',out)
        assert A.count_nonfinite(value)==1 and len(out['discrete'])==1


def test_two_stored_guard_preconditions():
    from geomind import c4_detect as D
    world={'qualification':{'candidates':[],'selected_members':[],
        'causal':{k:{'intact':[1.,1.,1.],'ablated':[0.,0.,0.]} for k in ('g_to_m','m_to_g')}},
        'qualified_states':[{'cohorts':[{'tokens':['a','b']}]}]}
    def found(w):return {family:ok for family,path,margin,ok in A.guards(D,w)}
    clean=found(world)
    assert clean['causal input lengths: intact and ablated each have 3 grids']
    assert clean['causal inputs nonnegative and finite: >= 0']
    assert clean['selection tokens unique: no duplicate priorities']
    bad=copy.deepcopy(world);bad['qualification']['causal']['m_to_g']['ablated']=[-1.]
    bad['qualified_states'][0]['cohorts'][0]['tokens']=['a','a']
    failed=found(bad)
    assert not failed['causal input lengths: intact and ablated each have 3 grids']
    assert not failed['causal inputs nonnegative and finite: >= 0']
    assert not failed['selection tokens unique: no duplicate priorities']
