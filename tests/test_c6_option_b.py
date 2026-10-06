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
    lib,_=O.load();lib.option_b_cache_limits(*O.CACHE_LIMITS)
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
    # Unselected controls are admitted on first computation (shared store).
    o.cohorts[0].selected=()
    first=raw(o);second=raw(o);third=raw(o)
    assert np.array_equal(first,second) and np.array_equal(second,third)
    stats=O.cache_stats(lib)
    assert stats['control_hits']==2 and stats['retired_bytes']+stats['control_bytes']<=O.CACHE_LIMITS[0]
    assert stats['medium_bytes']<=O.CACHE_LIMITS[1] and stats['drive_bytes']<=O.CACHE_LIMITS[2]
    assert stats['medium_hits']>=1 and stats['avoided_material_rk_steps']==4*100  # 2 retired + 2 control hits


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


@pytest.mark.parametrize('limits',[(0,0,0),(12000,12000,5000),O.CACHE_LIMITS])
def test_cache_pressure_long_churn_and_actual_medium_independence(limits):
    lib,_=O.load();ref,_=O.reference();lib.option_b_cache_limits(*limits)
    try:
        original=owner(6)
        for i in range(100):
            changed=original.clone();changed.time=(i%13)*.01
            if i%2:changed.cohorts[0].selected=()
            if i%5==0:changed.cohorts=[]
            expected=raw_flow(ref,changed)
            for _ in range(3):assert_bits(raw_flow(lib,changed),expected)
            stats=O.cache_stats(lib)
            assert stats['retired_bytes']+stats['control_bytes']<=limits[0]
            assert stats['medium_bytes']<=limits[1] and stats['drive_bytes']<=limits[2]
        lib.option_b_cache_clear()
        assert all(v==0 for v in O.cache_stats(lib).values())
        raw_flow(lib,original)
        altered=original.clone();altered.z+=.1j
        hits=O.cache_stats(lib)['retired_hits']
        assert_bits(raw_flow(lib,altered),raw_flow(ref,altered))
        if limits[0]>=12000:assert O.cache_stats(lib)['retired_hits']==hits+1
    finally:lib.option_b_cache_limits(*O.CACHE_LIMITS)


def test_process_wide_single_flight_is_exact_under_concurrency():
    """Four threads request identical material, medium and ON runs at once."""
    import threading
    from concurrent.futures import ThreadPoolExecutor
    lib,_=O.load();ref,_=O.reference();lib.option_b_cache_limits(*O.CACHE_LIMITS)
    try:
        states=[owner(24)]
        states.append(states[0].clone());states[1].cohorts[0].selected=()
        states.append(states[0].clone());states[2].cohorts=[]
        states.append(states[0].clone());states[3].cohorts[0].output=1.
        for state in states:
            expected=raw_flow(ref,state,steps=400)
            barrier=threading.Barrier(4)
            def request(_):
                barrier.wait(timeout=10);return raw_flow(lib,state,steps=400)
            with ThreadPoolExecutor(max_workers=4) as pool:
                for actual in pool.map(request,range(4)):assert_bits(actual,expected)
        stats=O.cache_stats(lib)
        # One computation per distinct key; every other request hit or waited.
        assert stats['eligible_misses']==2 and stats['retired_hits']==3 and stats['control_hits']==3
        assert stats['medium_misses']==1 and stats['computed_uncached_rk_steps']==4*400
        assert stats['drive_misses']==1
    finally:lib.option_b_cache_limits(*O.CACHE_LIMITS)


@pytest.mark.parametrize('failure',['medium_overflow','material_denominator','material_overflow','both'])
@pytest.mark.parametrize('selected',[(0,1,2),()])
def test_split_off_material_keeps_failure_codes(failure,selected):
    """OFF material misses integrate material and actual medium separately."""
    lib,_=O.load();ref,_=O.reference();lib.option_b_cache_limits(*O.CACHE_LIMITS)
    o=owner(6);o.cohorts[0].selected=selected
    ns,n,nc,arrays=F.arguments(o);y=arrays[0]
    if failure in ('medium_overflow','both'):y[:2*ns]=1e80
    if failure in ('material_denominator','both'):y[2*ns:2*ns+2]=1e150
    if failure=='material_overflow':y[2*ns+3*n:2*ns+3*n+2]=1e80
    pointers=[a.ctypes.data_as(ctypes.POINTER(ctypes.c_int if i in (4,7) else ctypes.c_double)) for i,a in enumerate(arrays)]
    expected=np.empty((21,len(y)));actual=np.empty((21,len(y)))
    code=ref.field_run(ns,n,nc,0.,.005,20,1,*pointers,expected.ctypes.data_as(O.PTR))
    assert code!=0
    for _ in range(2):assert lib.field_run(ns,n,nc,0.,.005,20,1,*pointers,actual.ctypes.data_as(O.PTR))==code


@pytest.mark.parametrize('mode',list(F.MODES))
@pytest.mark.parametrize('defect',['inf_phase','nan_phase','inf_position','inf_output'])
def test_skipped_exact_zero_terms_keep_nonfinite_decisions(mode,defect):
    """Raw-boundary inputs that the R4 path never produces keep codes and bits."""
    lib,_=O.load();ref,_=O.reference()
    o=owner(6);c=o.cohorts[0];c.mode=mode;c.output=0.
    if mode=='no_geometry_to_mode':c.origin=c.x.copy()
    ns,n,nc,arrays=F.arguments(o)
    y,p=arrays[0],arrays[9]
    if defect=='inf_phase':y[2*ns+2*n]=np.inf
    if defect=='nan_phase':y[2*ns+2*n+1]=np.nan
    if defect=='inf_position':y[2*ns]=np.inf
    if defect=='inf_output':p[3]=np.inf
    pointers=[a.ctypes.data_as(ctypes.POINTER(ctypes.c_int if i in (4,7) else ctypes.c_double)) for i,a in enumerate(arrays)]
    expected=np.empty_like(y);actual=np.empty_like(y)
    code=ref.field_rhs(ns,n,nc,0.,*pointers,expected.ctypes.data_as(O.PTR))
    assert lib.field_rhs(ns,n,nc,0.,*pointers,actual.ctypes.data_as(O.PTR))==code
    if code==0:assert_bits(actual,expected)


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
    """Inject list-node allocation failures and leader failures in the shared store."""
    import subprocess
    source=tmp_path/'allocation_contract.cpp';binary=tmp_path/'allocation_contract'
    implementation=Path(__file__).resolve().parents[1]/'native/c6_option_b/field.cpp'
    source.write_text('''#include <cstdlib>
#include <new>
#include <cassert>
#include <thread>
#include <atomic>
#include <chrono>
static bool fail_next = false;
void* operator new(std::size_t n) {
    if (fail_next) { fail_next=false; throw std::bad_alloc(); }
    if (void* p=std::malloc(n)) return p;
    throw std::bad_alloc();
}
void operator delete(void* p) noexcept { std::free(p); }
void operator delete(void* p, std::size_t) noexcept { std::free(p); }
'''+'#include "'+implementation.as_posix()+'"\n'+'''
std::shared_ptr<Value<double>> value(const std::vector<unsigned char>& key){
    auto v=std::make_shared<Value<double>>();v->key=key;v->data.assign(16,1.);return v;
}
int main() {
    Store<double> store; store.configure(1<<20);
    std::vector<unsigned char> key(16,1); const uint64_t h=key_hash(key);
    {   // Admission fails at the list node: value returned, nothing retained.
        Store<double>::Lease lease; assert(!store.acquire(key,h,lease));
        auto v=value(key); fail_next=true; lease.publish(v);
    }
    auto st=store.stats(); assert(st.entries==0 && st.bytes==0);
    {   Store<double>::Lease lease; assert(!store.acquire(key,h,lease)); lease.publish(value(key)); }
    st=store.stats(); assert(st.entries==1 && st.bytes>0 && st.misses==2);
    {   Store<double>::Lease lease; assert(store.acquire(key,h,lease)); }
    // A failed leader (lease destroyed unpublished) lets one waiter lead again.
    std::vector<unsigned char> other(16,2); const uint64_t g=key_hash(other);
    std::atomic<bool> leading{false}; bool retried=false;
    std::thread leader([&]{
        Store<double>::Lease lease; assert(!store.acquire(other,g,lease)); leading=true;
        std::this_thread::sleep_for(std::chrono::milliseconds(50));
    });
    while(!leading) std::this_thread::yield();
    {   Store<double>::Lease lease; retried=!store.acquire(other,g,lease); lease.publish(value(other)); }
    leader.join(); assert(retried);
    {   Store<double>::Lease lease; assert(store.acquire(other,g,lease)); }
    // Single flight: a follower waits for the leader's value.
    std::vector<unsigned char> third(16,3); const uint64_t t=key_hash(third);
    leading=false; std::thread first([&]{
        Store<double>::Lease lease; assert(!store.acquire(third,t,lease)); leading=true;
        std::this_thread::sleep_for(std::chrono::milliseconds(50)); lease.publish(value(third));
    });
    while(!leading) std::this_thread::yield();
    {   Store<double>::Lease lease; auto found=store.acquire(third,t,lease); assert(found && found->data.size()==16); }
    first.join(); assert(store.stats().waits==1);
    // Byte limit: a value larger than the limit is returned but not retained.
    store.configure(64); std::vector<unsigned char> big(16,4);
    {   Store<double>::Lease lease; assert(!store.acquire(big,key_hash(big),lease)); lease.publish(value(big)); }
    st=store.stats(); assert(st.entries==0 && st.bytes==0);
}
''')
    subprocess.run(['clang++','-std=c++17','-O2','-fno-fast-math','-ffp-contract=off',str(source),'-o',str(binary)],check=True,capture_output=True)
    subprocess.run([str(binary)],check=True,capture_output=True)


def _native_contract(tmp_path,name,body):
    import subprocess
    source=tmp_path/(name+'.cpp');binary=tmp_path/name
    implementation=Path(__file__).resolve().parents[1]/'native/c6_option_b/field.cpp'
    source.write_text('''#include <cstdlib>
#include <new>
#include <cassert>
#include <cstdio>
#include <thread>
#include <atomic>
#include <chrono>
#include <malloc/malloc.h>
static std::atomic<long long> live{0},peak{0};
static std::atomic<bool> counting{false};
static std::atomic<size_t> refuse_above{0};
void* operator new(std::size_t n) {
    size_t limit=refuse_above.load();
    if (limit && n>limit) throw std::bad_alloc();
    void* p=std::malloc(n); if(!p) throw std::bad_alloc();
    if (counting) {long long v=live+= (long long)malloc_size(p); long long q=peak; while(v>q&&!peak.compare_exchange_weak(q,v));}
    return p;
}
void operator delete(void* p) noexcept { if(p&&counting) live-= (long long)malloc_size(p); std::free(p); }
void operator delete(void* p, std::size_t) noexcept { operator delete(p); }
'''+'#include "'+implementation.as_posix()+'"\n'+body)
    subprocess.run(['clang++','-std=c++17','-O2','-fno-fast-math','-ffp-contract=off',str(source),'-o',str(binary)],check=True,capture_output=True)
    result=subprocess.run([str(binary)],capture_output=True,text=True)
    assert result.returncode==0,result.stdout+result.stderr


SYNTHETIC_INPUTS='''
struct Inputs {
  int ns=25,n=24;std::vector<double> q,omega,psi,p,rates,masks,origins,initial;std::vector<int> adj,modes;
  Inputs(int nc,bool selected,bool on){
    for(int x=-4;x<=4;x+=2)for(int y=-4;y<=4;y+=2){q.push_back(x);q.push_back(y);}
    adj.assign(ns*ns,0);
    for(int a=0;a<ns;a++)for(int b=0;b<ns;b++){double dx=q[2*a]-q[2*b],dy=q[2*a+1]-q[2*b+1];if(dx*dx+dy*dy==4.)adj[a*ns+b]=1;}
    for(int a=0;a<ns;a++){omega.push_back(-.3+.04*a);for(int m=0;m<8;m++)psi.push_back(.1*a-.3*m);}
    p={-.18,.05,.02,.3,.2,.05,2.,.8,1.};
    for(int a=0;a<ns;a++){initial.push_back(.05*a/ns);initial.push_back(-.03);}
    for(int c=0;c<nc;c++){
      for(int i=0;i<n;i++){initial.push_back(.2*i-2.3+c);initial.push_back(.1*(i%5)-.2);}
      for(int i=0;i<n;i++)initial.push_back(.37*i);
      for(int a=0;a<ns;a++){initial.push_back(.04);initial.push_back(.01*a);}
      for(int i=0;i<n;i++){rates.push_back(.01*i);masks.push_back(selected&&i<3?(on?1.:-1.):0.);}
      modes.push_back(0);
      for(int i=0;i<n;i++){origins.push_back(.2*i-2.3+c);origins.push_back(.1*(i%5)-.2);}
    }
  }
};
static int run(const Inputs& in,int nc,int steps,std::vector<double>& frames){
  const int width=2*in.ns+nc*(3*in.n+2*in.ns);frames.assign(size_t(steps+1)*width,0.);
  return field_run(in.ns,in.n,nc,0.,.00125,steps,1,in.initial.data(),in.q.data(),in.omega.data(),in.psi.data(),
    in.adj.data(),in.rates.data(),in.masks.data(),in.modes.data(),in.origins.data(),in.p.data(),frames.data());
}
'''


def test_disabled_and_failed_optional_storage_bounds_peak_allocation(tmp_path):
    """Review F2: no optional allocation when disabled; streaming/direct fallback."""
    _native_contract(tmp_path,'peak_contract',SYNTHETIC_INPUTS+'''
int main(){
  const int steps=2000;
  struct Case{int nc;bool selected,on;} cases[]={{0,false,false},{1,true,false},{1,false,false},{1,true,true},{2,true,true}};
  for(auto c:cases){
    Inputs in(c.nc,c.selected,c.on);std::vector<double> expected,actual;
    option_b_cache_limits(1ULL<<30,64ULL<<20,128ULL<<20);
    assert(run(in,c.nc,steps,expected)==0);
    // Disabled storage: peak live allocation stays far below one drive path
    // (3*steps*ns complex = 2.4 MB) or one trajectory (>= 0.8 MB).
    option_b_cache_limits(0,0,0);
    actual.assign(expected.size(),0.);
    live=0;peak=0;counting=true;
    int code=run(in,c.nc,steps,actual);
    counting=false;
    assert(code==0&&std::memcmp(actual.data(),expected.data(),expected.size()*8)==0);
    std::printf("nc=%d peak=%lld\\n",c.nc,(long long)peak);
    assert(peak<256*1024);
    // Enabled storage, but every allocation above 256 KiB fails: the drive
    // streams, the medium integrates directly, admission is skipped.
    option_b_cache_limits(1ULL<<30,64ULL<<20,128ULL<<20);
    refuse_above=256*1024;
    for(int repeat=0;repeat<2;repeat++){
      actual.assign(expected.size(),0.);
      code=run(in,c.nc,steps,actual);
      assert(code==0&&std::memcmp(actual.data(),expected.data(),expected.size()*8)==0);
    }
    refuse_above=0;
    auto stats=material_store().stats();assert(stats.entries==0);
  }
  option_b_cache_limits(1ULL<<30,64ULL<<20,128ULL<<20);
}
''')


def test_single_flight_publishes_before_release_and_rejects_same_index_keys(tmp_path):
    """Review F3: non-retained publication reaches waiting followers; forced
    same-hash keys with different bytes never alias."""
    _native_contract(tmp_path,'flight_contract','''
std::shared_ptr<Value<double>> value(const std::vector<unsigned char>& key,double fill){
  auto v=std::make_shared<Value<double>>();v->key=key;v->data.assign(8,fill);return v;
}
int main(){
  Store<double> store;store.configure(0);  // nothing is retained
  std::vector<unsigned char> key(16,7);const uint64_t h=key_hash(key);
  std::atomic<bool> leading{false},waiting{false};std::shared_ptr<const Value<double>> seen;
  Store<double>::Lease* held=nullptr;
  std::thread follower([&]{
    while(!leading)std::this_thread::yield();
    waiting=true;Store<double>::Lease lease;seen=store.acquire(key,h,lease);
    assert(seen);
  });
  {
    Store<double>::Lease lease;assert(!store.acquire(key,h,lease));leading=true;
    while(!waiting)std::this_thread::yield();
    std::this_thread::sleep_for(std::chrono::milliseconds(50));
    lease.publish(value(key,3.));
  }
  follower.join();
  assert(seen&&seen->data[0]==3.);
  auto st=store.stats();assert(st.misses==1&&st.waits==1&&st.entries==0);
  // After publication the value is not retained: the next request leads.
  {Store<double>::Lease lease;assert(!store.acquire(key,h,lease));}
  // Forced same index, different full keys: each is distinct.
  store.configure(1<<20);
  std::vector<unsigned char> a(16,1),b(16,2);const uint64_t same=42;
  {Store<double>::Lease lease;assert(!store.acquire(a,same,lease));lease.publish(value(a,1.));}
  {Store<double>::Lease lease;auto found=store.acquire(b,same,lease);assert(!found);lease.publish(value(b,2.));}
  {Store<double>::Lease lease;auto found=store.acquire(a,same,lease);assert(found&&found->data[0]==1.);}
  {Store<double>::Lease lease;auto found=store.acquire(b,same,lease);assert(found&&found->data[0]==2.);}
  assert(store.stats().entries==2);
}
''')

