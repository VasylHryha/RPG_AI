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
        assert np.array_equal(actual,flow)
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
        assert np.array_equal(actual,reference)
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
    assert not C.compare(a,b,0.,False)['passed']
    b['chain_complete']=True;assert not C.compare(a,b)['passed']
    b=json.loads(json.dumps(a));b['inputs']['x'][0]+=1e-15
    assert not C.compare(a,b)['passed']
    b=json.loads(json.dumps(a));b['checks'][0]['error']=float('nan')
    assert not C.compare(a,b)['passed']
    b=json.loads(json.dumps(a));b['checks'].append(b['checks'][0])
    assert not C.compare(a,b)['passed']
    a={'start_ids':['a'*64],'operation_end_ids':['b'*64],'operation_frames':[[.1]],'qualified':True}
    b={'start_ids':['c'*64],'operation_end_ids':['d'*64],'operation_frames':[[.1]],'qualified':True}
    assert C.compare(a,b)['passed']
    assert not C.compare(a,b,0.,False)['passed']
    b['operation_frames'][0][0]+=.01
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

def test_exact_native_retired_and_repeated_control_memoization():
    lib,_=O.load();lib.option_b_cache_clear()
    o=owner(6)
    def raw(state):
        ns,n,nc,arrays=F.arguments(state)
        steps=100;sample=1
        flow=np.empty((steps+1,len(arrays[0])),dtype='f8')
        ptrs=[a.ctypes.data_as(ctypes.POINTER(ctypes.c_int if i in (4,7) else ctypes.c_double)) for i,a in enumerate(arrays)]
        assert lib.field_run(ns,n,nc,state.time,.005,steps,sample,*ptrs,flow.ctypes.data_as(O.PTR))==0
        return flow
    first=raw(o);second=raw(o)
    assert np.array_equal(first,second)
    assert O.cache_stats(lib)['retired_hits']==1
    # The actual field is a separate live output, never read from material cache.
    changed=o.clone();changed.z+=.1j
    other=raw(changed)
    assert np.array_equal(other[:,50:],first[:,50:])
    assert not np.array_equal(other[:,:50],first[:,:50])
    for change in ('clock','rate','carrier','mask','mode','drive'):
        changed=o.clone()
        if change=='clock':changed.time+=.1
        if change=='rate':changed.cohorts[0].rates[0]+=.01
        if change=='carrier':changed.cohorts[0].carrier[0]+=.01j
        if change=='mask':changed.cohorts[0].selected=(1,2,3)
        if change=='mode':changed.cohorts[0].mode='no_r'
        if change=='drive':changed.model['drive']+=.01
        hits=O.cache_stats(lib)['retired_hits'];raw(changed)
        assert O.cache_stats(lib)['retired_hits']==hits
    o.cohorts[0].selected=()
    first=raw(o);second=raw(o);third=raw(o)
    assert np.array_equal(first,second) and np.array_equal(second,third)
    stats=O.cache_stats(lib)
    assert stats['control_hits']==1 and stats['retired_bytes']<=256*1024*1024
    assert stats['control_bytes']<=32*1024*1024 and stats['probation_bytes']<=2*1024*1024


@pytest.mark.parametrize('difference',[1e-15,-0.])
def test_exact_audit_rejects_a_difference_below_old_tolerance(difference):
    class Fake:
        def __init__(self,delta):self.delta=delta
        def field_rhs(self,*args):
            out=np.ctypeslib.as_array(args[-1],shape=(13,))
            out.fill(0.);out[0]=self.delta
            return 0
    out=np.empty(13,dtype='f8')
    audit=O.Audit(Fake(difference),Fake(0.))
    with pytest.raises(RuntimeError,match='full-flow equivalence failed'):
        audit.invoke('field_rhs',(1,3,1,out.ctypes.data_as(O.PTR)))


def test_exact_comparator_rejects_signed_zero():
    assert not C.compare({'x':0.},{'x':-0.},0.,False)['passed']
    assert C.compare({'x':-0.},{'x':-0.},0.,False)['passed']


def raw_flow(lib, state, steps=4, dt=.005, sample=1):
    ns,n,nc,arrays=F.arguments(state)
    flow=np.empty((steps//sample+1,len(arrays[0])),dtype='f8')
    pointers=[a.ctypes.data_as(ctypes.POINTER(ctypes.c_int if i in (4,7) else ctypes.c_double)) for i,a in enumerate(arrays)]
    code=lib.field_run(ns,n,nc,state.time,dt,steps,sample,*pointers,flow.ctypes.data_as(O.PTR))
    assert code==0,code
    return flow


def assert_bits(a,b):
    assert a.shape==b.shape and np.array_equal(a.view('u8'),b.view('u8'))


@pytest.mark.parametrize('change',['clock','dt','steps','sample','q','omega','psi','adjacency',
    'x','theta','rate','carrier','mask','mode','origin',*F.PARAMETER_NAMES])
def test_every_physical_key_input_changes_or_recomputes_exactly(change):
    lib,_=O.load();ref,_=O.reference();lib.option_b_cache_limits(*O.CACHE_LIMITS)
    original=owner(6);raw_flow(lib,original)
    changed=original.clone();c=changed.cohorts[0];options={}
    if change=='clock':changed.time=.1
    elif change in ('dt','steps','sample'):options[change]={'dt':.0025,'steps':6,'sample':2}[change]
    elif change=='q':changed.q[0,0]+=.01
    elif change=='omega':changed.omega[0]+=.01
    elif change=='psi':changed.psi[0,0]+=.01
    elif change=='adjacency':changed.adjacency[0,1]=changed.adjacency[1,0]=1-changed.adjacency[0,1]
    elif change=='x':c.x[0,0]+=.01
    elif change=='theta':c.theta[0]+=.01
    elif change=='rate':c.rates[0]+=.01
    elif change=='carrier':c.carrier[0]+=.01j
    elif change=='mask':c.selected=(1,2,3)
    elif change=='mode':c.mode='no_r'
    elif change=='origin':c.origin=c.x.copy();c.origin[0,0]+=.01
    else:changed.model[change]+=.01
    hits=O.cache_stats(lib)['retired_hits']
    actual=raw_flow(lib,changed,**options)
    assert O.cache_stats(lib)['retired_hits']==hits
    assert_bits(actual,raw_flow(ref,changed,**options))


@pytest.mark.parametrize('limits',[(0,0,0,0),(12000,12000,5000,5000),O.CACHE_LIMITS])
def test_cache_pressure_long_churn_and_actual_medium_independence(limits):
    lib,_=O.load();ref,_=O.reference();lib.option_b_cache_limits(*limits)
    try:
        original=owner(6)
        for i in range(100):
            changed=original.clone();changed.time=(i%13)*.01
            if i%2:changed.cohorts[0].selected=()
            expected=raw_flow(ref,changed)
            for _ in range(3):assert_bits(raw_flow(lib,changed),expected)
            stats=O.cache_stats(lib)
            for key,limit in zip(('retired_bytes','control_bytes','probation_bytes','drive_bytes'),limits):
                assert stats[key]<=limit
        lib.option_b_cache_clear()
        assert all(v==0 for v in O.cache_stats(lib).values())
        raw_flow(lib,original)
        altered=original.clone();altered.z+=.1j
        hits=O.cache_stats(lib)['retired_hits']
        assert_bits(raw_flow(lib,altered),raw_flow(ref,altered))
        if limits[0]>=12000:assert O.cache_stats(lib)['retired_hits']==hits+1
    finally:lib.option_b_cache_limits(*O.CACHE_LIMITS)


def test_drive_key_signed_zero_and_zero_field_arithmetic():
    lib,_=O.load();ref,_=O.reference();lib.option_b_cache_limits(*O.CACHE_LIMITS)
    for sign in (0.,-0.):
        o=owner(6);o.time=sign;o.psi.fill(sign)
        o.z.fill(complex(sign,sign));o.cohorts[0].carrier=o.z.copy()
        o.model['drive']=sign;o.model['output']=sign;o.omega.fill(sign)
        for _ in range(3):assert_bits(raw_flow(lib,o),raw_flow(ref,o))
    lib.option_b_cache_clear()
    assert O.cache_stats(lib)['drive_bytes']==0


def test_native_invalid_dimensions_and_clock_fail_closed():
    lib,_=O.load();ns,n,nc,arrays=F.arguments(owner(6))
    pointers=[a.ctypes.data_as(ctypes.POINTER(ctypes.c_int if i in (4,7) else ctypes.c_double)) for i,a in enumerate(arrays)]
    out=np.empty((5,len(arrays[0])),dtype='f8').ctypes.data_as(O.PTR)
    for dimensions in ((-1,n,nc),(ns,2,nc),(2**30,n,nc),(ns,n,-1)):
        assert lib.field_rhs(*dimensions,0.,*pointers,out)==3
        assert lib.field_run(*dimensions,0.,.005,4,1,*pointers,out)==3
    for dt in (0.,-1.,float('nan'),float('inf')):
        assert lib.field_run(ns,n,nc,0.,dt,4,1,*pointers,out)==3
    assert lib.field_run(ns,n,nc,float('nan'),.005,4,1,*pointers,out)==3


def test_backend_selection_rejects_nesting_and_reference_never_builds(monkeypatch):
    from tools import build_c6_r4
    def forbidden():raise AssertionError('implicit build')
    monkeypatch.setattr(build_c6_r4,'build',forbidden)
    with O.backend('reference'):
        with pytest.raises(RuntimeError,match='nested'):
            with O.backend('native'):pass
        assert np.isfinite(F.rhs(owner(6))).all()
    with O.backend('native'):
        with pytest.raises(RuntimeError,match='nested'):
            with O.backend('reference'):pass


def test_single_flight_cache_concurrent_success_failure_and_eviction():
    from concurrent.futures import ThreadPoolExecutor
    from collections import OrderedDict
    import threading,time
    cached=O.single_flight_cache();cache=OrderedDict();calls=[]
    barrier=threading.Barrier(4)
    def compute():
        calls.append(1);time.sleep(.03);return np.arange(8.)
    def request():
        barrier.wait(timeout=10);return cached(cache,64,'same',compute)
    with ThreadPoolExecutor(max_workers=4) as pool:
        results=list(pool.map(lambda _:request(),range(4)))
    assert len(calls)==1 and all(r is results[0] for r in results)
    assert not results[0].flags.writeable
    cached(cache,64,'evict',lambda:np.ones(8))
    assert 'same' not in cache and np.array_equal(results[0],np.arange(8.))
    calls.clear();barrier=threading.Barrier(4)
    def failed():calls.append(1);time.sleep(.03);raise ValueError('synthetic failure')
    def failure_request():
        barrier.wait(timeout=10)
        with pytest.raises(ValueError,match='synthetic failure'):cached(cache,64,'fail',failed)
    with ThreadPoolExecutor(max_workers=4) as pool:list(pool.map(lambda _:failure_request(),range(4)))
    assert len(calls)==1 and 'fail' not in cache
    assert_bits(cached(cache,64,'fail',lambda:np.arange(8.)),np.arange(8.))


def test_loaded_binary_record_change_requires_restart():
    lib,record=O.load();altered=dict(record);altered['compiler']='another compiler'
    with pytest.raises(RuntimeError,match='restart process'):
        O._checked_load(O.B.LIBRARY,altered)
    assert O.load()[0] is lib


def test_reference_flags_mismatch_cannot_call_builder(monkeypatch):
    original=O.json.loads
    def tampered(data):
        record=original(data)
        if 'source_sha256' in record:record['flags']=['-ffast-math']
        return record
    monkeypatch.setattr(O.json,'loads',tampered)
    with pytest.raises(RuntimeError,match='explicit rebuild'):O.reference()


def test_builder_compiles_snapshot_and_rejects_source_drift(tmp_path,monkeypatch):
    from tools import build_c6_option_b as B
    sources=(tmp_path/'field.cpp',tmp_path/'detection.cpp')
    for source in sources:source.write_text('original')
    library=tmp_path/'build'/'option_b.dylib'
    monkeypatch.setattr(B,'ROOT',tmp_path);monkeypatch.setattr(B,'SOURCES',sources)
    monkeypatch.setattr(B,'LIBRARY',library)
    monkeypatch.setattr(B.subprocess,'check_output',lambda *a,**k:'test compiler\nTarget: test\n')
    def compile_snapshot(command,**kwargs):
        snapshots=[Path(p) for p in command if p.endswith('.cpp')]
        assert all(p not in sources and p.read_text()=='original' for p in snapshots)
        Path(command[-1]).write_bytes(b'synthetic binary')
    monkeypatch.setattr(B.subprocess,'run',compile_snapshot)
    record=B.build()
    assert record['compiler_version']=='test compiler\nTarget: test\n'
    assert record['architecture'] and record['binary_sha256']==B.digest(library)
    original_binary=library.read_bytes();original_record=(library.parent/'BUILD.json').read_bytes()
    def drift(command,**kwargs):
        compile_snapshot(command,**kwargs);sources[0].write_text('changed')
    monkeypatch.setattr(B.subprocess,'run',drift)
    with pytest.raises(RuntimeError,match='sources changed'):B.build()
    assert library.read_bytes()==original_binary
    assert (library.parent/'BUILD.json').read_bytes()==original_record


def test_detector_raw_boundary_rejects_invalid_inventory():
    lib,_=O.load()
    for n in (-1,2**30):
        assert lib.option_b_components(n,None,1.5,None,None)==1
    assert lib.option_b_components(3,None,1.5,None,None)==1
    assert lib.option_b_components(0,None,1.5,None,None)==0


def test_native_store_accounting_survives_allocation_failure(tmp_path):
    """Inject an actual list-node allocation failure without stressing RAM."""
    import subprocess
    source=tmp_path/'allocation_contract.cpp';binary=tmp_path/'allocation_contract'
    implementation=Path(__file__).resolve().parents[1]/'native/c6_option_b/field.cpp'
    source.write_text('''#include <cstdlib>
#include <new>
#include <cassert>
static bool fail_next = false;
void* operator new(std::size_t n) {
    if (fail_next) { fail_next=false; throw std::bad_alloc(); }
    if (void* p=std::malloc(n)) return p;
    throw std::bad_alloc();
}
void operator delete(void* p) noexcept { std::free(p); }
'''+'#include "'+implementation.as_posix()+'"\n'+'''
int main() {
    std::list<Trajectory> cache; std::size_t bytes=0;
    Trajectory entry{std::vector<unsigned char>(16),std::vector<double>(16)};
    fail_next=true; bool failed=false;
    try { store(cache,bytes,4096,std::move(entry)); }
    catch (const std::bad_alloc&) { failed=true; }
    assert(failed && cache.empty() && bytes==0);
    Trajectory next{std::vector<unsigned char>(16),std::vector<double>(16)};
    store(cache,bytes,4096,std::move(next));
    assert(cache.size()==1 && bytes==cache.front().bytes());
}
''')
    subprocess.run(['clang++','-std=c++17','-O2','-fno-fast-math','-ffp-contract=off',str(source),'-o',str(binary)],check=True,capture_output=True)
    subprocess.run([str(binary)],check=True,capture_output=True)
