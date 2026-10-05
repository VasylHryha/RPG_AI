"""Bounded dev/synthetic equivalence; never an experimental or evaluator panel."""
from collections import deque
from copy import deepcopy
from dataclasses import asdict
from concurrent.futures import ThreadPoolExecutor
import ctypes as C
import hashlib
import json
import math
import os
import struct
from pathlib import Path
import numpy as np
import pytest
from evidence.tactical_composition_demo.growing_shapes.medium.design_0h import DesignMedium, Frame
from evidence.tactical_composition_demo.growing_shapes.medium.medium import Params, Drive
from evidence.tactical_composition_demo.growing_shapes.world.world import World
from evidence.tactical_composition_demo.growing_shapes.runner import native, qualification as q
from evidence.tactical_composition_demo.growing_shapes.runner.evaluator import copy_template
from evidence.tactical_composition_demo.growing_shapes.runner.protocol import BINDING, VERSION, bindings, action, permutation
from evidence.tactical_composition_demo.growing_shapes.runner.perf_compare import Compare, medium_state
from evidence.tactical_composition_demo.growing_shapes.runner.trace_store import TraceStore

HERE = Path(__file__).parent
LONG = []


@pytest.fixture(scope='module', autouse=True)
def receipt():
    yield
    target=os.environ.get('GROWING_SHAPES_RECHECK_LONG_OUTPUT')
    if LONG and target:
        with Path(target).open('x') as stream:stream.write(json.dumps(LONG,indent=2)+'\n')


@pytest.mark.parametrize('offset',[0.,math.pi])
@pytest.mark.parametrize('task',['perceive','move','remember_static','choose'])
@pytest.mark.parametrize('empty',[False,True])
def test_individual_evaluator_copy_native_exact(task,offset,empty):
    value = {'members':[] if empty else [[.1*i,0.,.2*i,math.pi,.5] for i in range(3)],
             'binding':BINDING,'constants_version':VERSION}
    a,b = copy_template(value,offset),copy_template(value,offset)
    lib = native.library()
    try:
        initial_events = deepcopy(b.events)
        with World(task,7,'dev') as wa,World(task,7,'dev',library=wa.library) as wb:
            original = deepcopy(value)
            while not wa.observe().done:
                obs = wa.observe()
                a.integrate(bindings(task,obs,permutation(7),a.time))
                wa.step(action(task,obs,a.native,a.time))
            native.evaluate_episode(b,wb,permutation(7),lib)
            assert a.native.save() == b.native.save()
            assert a.step_index == b.step_index
            assert bytes(wa.score()) == bytes(wb.score())
            assert bytes(wa.observe()) == bytes(wb.observe())
            assert value == original and b.events == initial_events
    finally:
        a.close();b.close()


def triangle(n=4):
    m = DesignMedium(105067)
    points = [(0.,0.),(1/1.8,0.),(1/3.6,math.sqrt(3)/3.6)]
    ids = [m.add(p,60*math.pi) for p in points]
    for i in range(3,n):
        m.add((10*i,0),60*math.pi)
        m.birth_steps[i] = 590
    m.frames.clear()
    for k in range(601):
        rows = {id:(*p,k*.1*math.pi) for id,p in zip(ids,points)}
        rows.update({i:(10.*i,0.,k*.1*math.pi) for i in range(3,n) if k>=590})
        m.frames.append(Frame(k,k*.1,rows,{}, {id:() for id in rows}))
    m.step_index = 600
    return m


def schedule(m,count=600):
    return [[Drive(s,4*math.cos(s*math.pi/4),4*math.sin(s*math.pi/4),
                   math.pi*(m.time+k*.1)+s*.1,math.pi,float((k//37+s)%3!=0),1,3)
             for s in range(8)] for k in range(count)]


def test_recovery_every_endpoint_and_full_stats():
    m = triangle()
    a,b = m.clone(events=False),m.clone(events=False)
    original = m.native.save()
    ds = schedule(m)
    try:
        data = native.replay(b,ds)
        for drives,row in zip(ds,data['steps']):
            a.integrate(drives)
            assert asdict(a.frames[-1]) == {k: ({int(id):tuple(v) for id,v in val.items()} if isinstance(val,dict) else val)
                                             for k,val in row['frame'].items()}
        assert a.native.save() == b.native.save()
        check = q.start(m)
        assert len(check['candidates']) == 1 and check['cohort'] == [0,1,2]
        first,second = deepcopy(check),deepcopy(check)
        x = q.finish(m,first,ds,np.random.default_rng(105067))
        y = q.finish(m,second,ds,np.random.default_rng(105067),backend='native')
        Compare().check(first,second,'complete_recovery')
        Compare().check(x,y,'admitted_and_exposure')
        assert m.native.save()==original
    finally:
        for branch in (m,a,b): branch.close()


def test_binary_future_every_endpoint_and_internal_snapshot_exact():
    m=triangle(24);n=m.clone(events=False,frames=False);ds=schedule(m)
    before=deepcopy(m.frames[-1])
    try:
        output=native.future(n,ds)
        assert output.shape==(600,24,3) and len(n.frames)==1 and n.frames[-1]==before
        for step,drives in enumerate(ds):
            m.integrate(drives)
            assert np.array_equal(output[step],[[e.x,e.y,e.phase] for e in m.native.elements])
        assert m.native.save()==n.native.save() and m.step_index==n.step_index
    finally:m.close();n.close()


@pytest.mark.parametrize('members',[3,12,64])
def test_batched_deviation_estimators_and_first_crossing(members):
    # Decaying perturbations plus changing common translation/carrier offset;
    # estimators must remove the latter without changing the first strict crossing.
    rng=np.random.default_rng(105074)
    a=rng.normal(size=(600,members,3))
    decay=np.exp(-np.arange(600)/37.)[:,None,None]
    common=rng.normal(scale=.1,size=(600,1,3))
    b=a+decay*rng.normal(scale=.2,size=(1,members,3))+common
    golden=[]
    for aa,bb in zip(a,b):
        phase=q.wrap(bb[:,2]-aa[:,2]);phase=q.wrap(phase-q.c4.circular_mean(phase))
        dx=bb[:,:2]-aa[:,:2];dx-=dx.mean(0)
        golden.append((np.sqrt(np.mean(phase**2)),np.sqrt(np.mean(np.sum(dx**2,axis=1)))))
    expected=np.array(golden).T;actual=np.array(q.deviation_series(a,b))
    Compare().check(expected,actual)
    for first,second in zip(expected,actual):
        assert np.flatnonzero(first < first[0]/math.e)[0]==np.flatnonzero(second < first[0]/math.e)[0]


@pytest.mark.parametrize('driven,steps,start',[(True,32000,0),(True,1000,319000),(False,320000,0)])
def test_long_continuation_fixed_tolerance(driven,steps,start):
    m = DesignMedium(105068,Params(A=0,B=0,K=0,geometry_rate=0,window=101,min_samples=100))
    m.step_index = start
    m.native.start_clock(start*.1)
    m.add((4,0),math.pi*m.time+.2,math.pi*1.01,.5)
    m.frames.clear();m.record()
    n = m.clone()
    lib,compare = native.library(),Compare()
    try:
        for base in range(0,steps,600):
            length = min(600,steps-base)
            ds = [[Drive(0,4,0,math.pi*((start+base+k)*.1),math.pi,1.,1,3)]
                  if driven else [] for k in range(length)]
            data = native.replay(n,ds,adapt=driven,lib=lib)
            for drives,row in zip(ds,data['steps']):
                m.integrate(drives)
                if driven:
                    m.adapt()
                    coverage = m.timers()
                    compare.check(coverage,row['covered'],'covered',True)
                    compare.check(m.events[-1],row['event'],'adaptation')
                    compare.check(m.death,row['death'],'death',True)
                    compare.check(list(m.novelty.values()),row['novelty'],'novelty',True)
            compare.check(medium_state(m),medium_state(n),'long_complete_state')
            if not driven:
                assert m.native.save()==n.native.save()
                assert list(m.frames)==list(n.frames)
            m.events.clear();n.events.clear()
        assert len(m.frames)==len(n.frames)==601 and len(m.native)==1
        LONG.append({'status':'PASS','driven':driven,'steps':steps,'start':start,'end':m.step_index,
                     'comparison':compare.report(),'native_sha256':hashlib.sha256(n.native.save()).hexdigest()})
    finally:
        m.close();n.close()


def test_growth_changes_visible_to_next_batch_and_newborn_warmup():
    m = DesignMedium(params=Params(A=0,B=0,K=0,geometry_rate=0,window=101,min_samples=100))
    id = m.add((0,0),199*.1*math.pi,gain=0)
    m.step_index = 199
    m.frames = deque([Frame(k,k*.1,{id:(0.,0.,k*.1*math.pi)},
                     {0:(4.,0.,k*.1*math.pi,1.)},{id:()}) for k in range(99,200)],maxlen=601)
    m.death[id],m.novelty[0] = 39.9,19.9
    n = m.clone()
    try:
        for block in (1,200):
            ds = [[Drive(0,4,0,math.pi*(m.time+k*.1),math.pi,1,1,3)] for k in range(block)]
            data = native.replay(n,ds,adapt=True)
            for drives,row in zip(ds,data['steps']):
                m.integrate(drives);m.adapt();m.timers()
                Compare().check(m.events[-1],row['event'])
            assert m.growth()==n.growth()
            Compare().check(medium_state(m),medium_state(n))
        assert 'D1' in [e['rule'] for e in m.events] and 'B1' in [e['rule'] for e in m.events]
        assert id not in m.death and min(m.birth_steps)>id
    finally:
        m.close();n.close()


def test_replay_prevalidates_future_and_poison_refuses_retry():
    m = DesignMedium();m.add((0,0),0)
    before = m.native.save()
    try:
        with pytest.raises(ValueError,match='site'):
            native.replay(m,[[],[Drive(99,0,0,0,0,1,1,3)]])
        assert m.native.save()==before
        with pytest.raises(RuntimeError,match='discard'):
            native.replay(m,[[]])
    finally: m.close()


def test_handle_lock_closed_and_separate_thread_determinism():
    lib = native.library()
    def execute(_):
        m = DesignMedium(105069);m.add((0,0),0)
        try:
            native.replay(m,[[]]*20,lib=lib)
            return m.native.save()
        finally: m.close()
    with ThreadPoolExecutor(max_workers=2) as pool:
        a,b = list(pool.map(execute,range(2)))
    assert a==b==execute(0)
    m = DesignMedium();m.add((0,0),0)
    try:
        with native.locked(m,lib):
            with pytest.raises(RuntimeError,match='concurrent'):
                native.replay(m,[[]],lib=lib)
        m.close()
        with pytest.raises(RuntimeError,match='closed'):
            native.replay(m,[[]],lib=lib)
    finally: m.close()


def test_trace_lossless_clone_isolation_and_no_overwrite(tmp_path):
    store = TraceStore(tmp_path/'events.jsonl')
    records = [{'time':k*.1,'rule':'adaptation','values':{'rates':{0:math.pi}}} for k in range(5000)]
    for row in records: store.append(row)
    Compare().check(records,list(store))
    receipt = store.receipt()
    assert receipt['records']==5000 and receipt['sha256']==hashlib.sha256(store.path.read_bytes()).hexdigest()
    m = DesignMedium();m.events=store
    try:
        branch = m.clone(events=False)
        assert branch.events==[] and m.events is store
        branch.close()
        with pytest.raises(FileExistsError): TraceStore(store.path)
    finally: store.close();m.close()


def test_loader_dependency_identity_failure(monkeypatch):
    # Alter the manifest returned by read_text, never a live binary or receipt.
    original = Path.read_text
    def read(path,*args,**kwargs):
        result = original(path,*args,**kwargs)
        if path == HERE/'_build/build.json':
            data = json.loads(result)
            data['dependencies'] = {key:'0'*64 for key in data['dependencies']}
            return json.dumps(data)
        return result
    monkeypatch.setattr(Path,'read_text',read)
    with pytest.raises(RuntimeError,match='dependency identity'): native.library()


def test_shared_handle_read_and_close_refused_from_other_thread():
    m=DesignMedium();lib=native.library()
    try:
        with World('perceive',105075,'dev') as w, native.locked(m,lib,w):
            def attempt(fn):
                with pytest.raises(RuntimeError,match='concurrent'):fn()
            with ThreadPoolExecutor(max_workers=1) as pool:
                for fn in (m.native.close,m.native.clone,m.native.save,lambda:m.native.elements,
                           w.close,w.observe,w.score):
                    pool.submit(attempt,fn).result()
            assert m.native._handle and w._handle and w.observe().step==0
        # Reverse acquisition order: an ordinary ABI call already owns the
        # medium lease when another thread tries to start a native future.
        from evidence.tactical_composition_demo.growing_shapes.native_guard import access
        with access(m.native), ThreadPoolExecutor(max_workers=1) as pool:
            pool.submit(attempt,lambda:native.replay(m,[[]],lib=lib)).result()
    finally:m.close()


def test_process_image_replacement_refused(tmp_path):
    from evidence.tactical_composition_demo.growing_shapes.native_guard import pin_image
    path=tmp_path/'not_a_real_library'
    pin_image(path,'a'*64);pin_image(path,'a'*64)
    with pytest.raises(RuntimeError,match='restart'):pin_image(path,'b'*64)


@pytest.mark.parametrize('field',['clock','born','track'])
def test_comparator_rejects_sub_tolerance_native_metadata_change(field):
    m=DesignMedium();m.add((0,0),0)
    try:
        original=m.native.save();data=bytearray(original)
        head=8+struct.unpack_from('=Q',data)[0]+struct.calcsize('=7d4i')+struct.calcsize('=15d3i')
        first=head+struct.calcsize('=4i2d2Q')+8
        offset=head+16 if field=='clock' else first+40 if field=='born' else first+52
        before=struct.unpack_from('=d',data,offset)[0]
        struct.pack_into('=d',data,offset,before+1e-12)
        with pytest.raises(AssertionError,match='native_exact'):
            Compare().check({'native':original.hex()},{'native':bytes(data).hex()})
    finally:m.close()


def test_dormant_development_requires_audit_storage_before_run_creation(monkeypatch):
    from types import SimpleNamespace
    from evidence.tactical_composition_demo.growing_shapes.runner import development
    def forbidden(*args,**kwargs):raise AssertionError('no run may be constructed')
    monkeypatch.setattr(development,'Run',forbidden)
    with pytest.raises(ValueError,match='lossless audit_root'):
        development.execute_arm(list(range(8)),{'perceive':SimpleNamespace(usable=True)})


def test_cost_estimator_candidate_caps_match_live_population():
    from evidence.tactical_composition_demo.growing_shapes.runner.perf_recheck import estimate
    runs=[{'timings':{'native':{'stages':{'training':2.},'steps':100}}}]
    stage={f'recovery_N{n}':{'qualification_seconds':.1,'timings':{'native':{'wall':.2}}} for n in (24,64)}
    stage['evaluation']=[{'N':n,'timings':{'native':{'wall':.3}}} for n in (24,64)]
    stage['synthetic_training']=[]
    result=estimate(runs,stage)
    assert result['conditional_N'][24]['maximum_candidate_count']==8
    assert result['conditional_N'][64]['maximum_candidate_count']==21
    assert set(result['conditional_N'][24]['total_hours_by_mean_candidates'])=={0,1,3,8}
    assert result['training_steps']==10240000 and result['maximum_evaluator_episodes']==344064


def test_native_evaluator_128_fresh_copies_two_offsets_mocked(monkeypatch):
    from types import SimpleNamespace
    from evidence.tactical_composition_demo.growing_shapes.runner import evaluator as e
    from evidence.tactical_composition_demo.growing_shapes.runner.protocol import Calibration
    copies, worlds, calls = [],[],[]
    class Copy:
        def close(self): pass
    def copier(value,offset):
        obj = Copy();copies.append((obj,offset));return obj
    class FakeWorld:
        def __init__(self,task,episode,namespace,**_):
            assert namespace=='validation' and 0<=episode<128
            self.task,self.episode,self.done = task,episode,False
            worlds.append(self)
        def __enter__(self): return self
        def __exit__(self,*_): pass
        def score(self):
            assert self.done
            return SimpleNamespace(angular_error=1.)
    def episode(medium,world,assignment,lib):
        assert assignment==permutation(world.episode)
        calls.append((id(medium),world.episode));world.done=True
    monkeypatch.setattr(e,'copy_template',copier)
    monkeypatch.setattr(e,'World',FakeWorld)
    monkeypatch.setattr(native,'library',lambda:object())
    monkeypatch.setattr(native,'evaluate_episode',episode)
    rows = {t:Calibration(t,1.,0.,1.,0.,t=='perceive') for t in ('perceive','move','remember_static','choose')}
    ev = e.Evaluator(rows,object(),'native')
    value = {'members':[],'binding':BINDING,'constants_version':VERSION}
    assert ev.evaluate(value)=={'perceive':-1.}
    assert ev.evaluate(value,math.pi)=={'perceive':-1.}
    assert len(copies)==len({id(obj) for obj,_ in copies})==256
    assert len(worlds)==len(calls)==ev.episodes==ev.copies==256
    assert [row['instance_id'] for row in ev.instances]==list(range(256))
    assert [row['carrier_offset'] for row in ev.instances]==[0.]*128+[math.pi]*128


def test_run_spooled_audit_matches_in_memory_and_indexed_births(tmp_path):
    from evidence.tactical_composition_demo.growing_shapes.runner.run import Run
    from evidence.tactical_composition_demo.growing_shapes.runner.protocol import Calibration
    rows={'perceive':Calibration('perceive',0.,-2.,2.,0.,True)}
    a=Run(105073,rows,episodes=1,backend='native')
    b=Run(105073,rows,episodes=1,backend='native',audit_dir=tmp_path)
    try:
        a.episode(0);b.episode(0)
        ar,br=a.report(),b.report();ar.pop('timing');br.pop('timing')
        assert br['events']['records']==len(a.medium.events)
        br['events'],br['drive_schedule']=list(b.medium.events),list(b.drive_log)
        Compare().check(ar,br)
        a.birth_index[200]=[40,41]
        # Index path cannot scan the audit ledger.
        a.medium.events=object()
        assert a.births_at(200)==[40,41]
    finally:a.close();b.close()


@pytest.mark.parametrize('first_present',[False,True])
def test_qualification_birth_on_left_endpoint_is_cohort_only_if_sampled(first_present):
    m=triangle()
    m.birth_steps[3]=600
    m.step_index=1200
    shifted=deque(maxlen=601)
    for f in m.frames:
        rows={id:(v[0],v[1],v[2]+60*math.pi) for id,v in f.elements.items()}
        if f.index>0 or first_present:rows[3]=(30.,0.,(f.time+60)*math.pi)
        shifted.append(Frame(f.index+600,f.time+60,rows,{}, {id:() for id in rows}))
    m.frames=shifted
    try:
        assert q.start(m)['cohort']==([0,1,2,3] if first_present else [0,1,2])
        # An older member with an unexplained hole still invalidates the run.
        m.birth_steps[3]=599
        if not first_present:
            with pytest.raises(ValueError,match='missing frame'):q.start(m)
    finally:m.close()
