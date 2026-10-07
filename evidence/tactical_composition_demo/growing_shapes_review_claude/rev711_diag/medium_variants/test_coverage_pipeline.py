"""Synthetic coverage checks only: no native steps, entropy runs or process listing."""
import ast
from collections import Counter, deque
import copy
import io
import json
import math
from pathlib import Path
import re
import tempfile
from types import SimpleNamespace as NS, MethodType
import unittest
from unittest.mock import patch

import coverage_kernel as K
import coverage_telemetry as T
import execute_coverage_plan as S
import write_coverage_report as R

HERE=Path(__file__).resolve().parent


def method(variant, name):
    # Compile just the actual patched method. Do not import/initialize a native medium.
    tree=ast.parse((HERE/f'kernel_builder/_worktrees/{variant}/evidence/tactical_composition_demo/growing_shapes/medium/rev7_design.py').read_text())
    cls=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='Rev7Medium')
    fn=next(n for n in cls.body if isinstance(n,ast.FunctionDef) and n.name==name)
    scope=dict(math=math,deque=deque,deepcopy=copy.deepcopy,fair_order=K.fair_order,deficit=lambda native,front,back:min(front,default=math.inf),recycle=K.recycle)
    exec(compile(ast.Module(body=[fn],type_ignores=[]),'actual-scratch-method','exec'),scope)
    return scope[name]


def outage(site=0, start=0., gap=3.):
    return dict(site=site,start=start,end=None,duration=None,censored=False,break_cause='X',
                break_candidates=[],break_detail=[],previous_route=[1,2],restored_route=None,route_reuse=None,
                initial_gap=gap,samples=[dict(t=start,gap=gap,rootless_screened=False)],requests=[],terminals=[],internal_route_events=[])


def observer(items):
    o=object.__new__(T.Observer);o.live=NS(step_index=8000);o.stream=io.StringIO()
    o.previous=dict(served=set(),routes={});o.open={x['site']:x for x in items};o.outages=items
    o.requests=[];o.terminals=[];o.recycles=[];o.initial_cost_refusals=[];o.forced=[];o.decisions=[];o.growth_checks=[];o.removals=[]
    o.active=Counter();o.active_served=Counter();o.served=Counter();o.degree=Counter();o.steps=0
    return o


class KernelChecks(unittest.TestCase):
    def test_clock_activity_idle_service_rootloss_and_inactive_pause(self):
        m=NS(coverage_wait=dict.fromkeys(range(8),0.))
        with patch.object(K,'service_snapshot',return_value=dict(served={1},active={0,2})):
            K.update_clock(m)
        self.assertEqual(m.coverage_wait[0],.1);self.assertEqual(m.coverage_wait[2],.1)
        with patch.object(K,'service_snapshot',return_value=dict(served={0},active=set())):
            K.update_clock(m)
        self.assertEqual(m.coverage_wait[0],0.);self.assertEqual(m.coverage_wait[2],.1)
        copied=copy.deepcopy(m);copied.coverage_wait[2]=100.
        self.assertEqual(m.coverage_wait[2],.1)

    def test_actual_kernel_clone_copies_waiting_and_recycle_state(self):
        m=type('FakeMedium',(),{})()
        m.__dict__.update(coverage_wait={s:float(s) for s in range(8)},coverage_locks={1:.5},coverage_recycled=True,native=NS(clone=lambda:NS()),events=[],frames=deque([],maxlen=601))
        for v in S.ARMS:
            branch=method(v,'clone')(m)
            branch.coverage_wait[0]=99.;branch.coverage_locks[1]=9.;branch.coverage_recycled=False
            self.assertEqual(m.coverage_wait[0],0.);self.assertEqual(m.coverage_locks[1],.5);self.assertTrue(m.coverage_recycled)

    def test_finite_first_waiting_pointer_and_rootless(self):
        gaps={0:9.,1:1.,2:math.inf,3:math.inf};wait={0:20.,1:20.,2:999.,3:999.}
        self.assertEqual(K.fair_order(gaps,wait,1),[1,0,2,3])
        wait[0]=21.
        self.assertEqual(K.fair_order(gaps,wait,1),[0,1,2,3])

    def make_recycle(self, classes=None, served=(), feasible=None, trial=True):
        log=[]
        m=NS(coverage_recycled=False,coverage_locks={1:0.,2:.9,3:.2,4:.1},step_index=300,
             birth_steps={1:0,2:100,3:0,4:0},
             remove=lambda i,r,**kw:log.append((i,r,kw)),
             trial=lambda *a:dict(edge=trial),feasible=lambda *a:feasible,
             emit=lambda *a,**kw:log.append((a,kw)))
        snapshot=dict(served=set(served),eligible=[1,2,3,4],classes=classes or dict.fromkeys((1,2,3,4),'non-service'))
        return m,snapshot,log

    def test_donor_anchor_exclusion_class_lock_age_and_same_point(self):
        m,s,log=self.make_recycle(classes={1:'non-service',2:'non-service',3:'critical',4:'redundant'})
        checks=[];m.trial=lambda *a:checks.append(a) or dict(a=True)
        with patch.object(K,'service_snapshot',return_value=s):
            reason,meta=K.recycle(m,(1.,2.),.5,0,7,'B-path',(1,4))
        self.assertIsNone(reason);self.assertEqual(meta['recycled_id'],2)
        self.assertEqual(log[0][0:2],(2,'D3r'));self.assertEqual(log[0][2]['age_steps'],200)
        self.assertEqual(checks,[(0,1,4,(1.,2.))]);self.assertTrue(m.coverage_recycled)
        with patch.object(K,'service_snapshot',side_effect=AssertionError('one removal only')):
            self.assertEqual(K.recycle(m,(1,2),0.,0,8,'B1')[0],'cost')

    def test_failed_geometry_keeps_removal_and_b1_has_no_path_trial(self):
        m,s,log=self.make_recycle(trial=False)
        with patch.object(K,'service_snapshot',return_value=s):
            reason,meta=K.recycle(m,(1.,2.),0.,0,0,'B-path',(2,3))
        self.assertEqual(reason,'recycle_failed');self.assertEqual(meta['retry_reason'],'geometry')
        self.assertEqual(len([x for x in log if len(x)==3]),1)
        m,s,log=self.make_recycle();m.trial=lambda *a:(_ for _ in ()).throw(AssertionError('B1 has no progress trial'))
        with patch.object(K,'service_snapshot',return_value=s):
            self.assertIsNone(K.recycle(m,(1.,2.),0.,0,0,'B1')[0])

    def test_no_donor_served_site_and_retry_cost(self):
        m,s,_=self.make_recycle(served=[0])
        with patch.object(K,'service_snapshot',return_value=s):self.assertEqual(K.recycle(m,(1,2),0,0,0,'B1'),('cost',{}))
        s['served']=set();s['eligible']=[]
        with patch.object(K,'service_snapshot',return_value=s):self.assertEqual(K.recycle(m,(1,2),0,0,0,'B1'),('cost',{}))
        m,s,_=self.make_recycle(feasible='cost')
        with patch.object(K,'service_snapshot',return_value=s):self.assertEqual(K.recycle(m,(1,2),0,0,0,'B1')[0],'recycle_failed')

    def bpath(self, variant, outcomes):
        calls=[];terminals=[];counter=iter(outcomes)
        g=NS(path=lambda s:False,forward=lambda s:{s},backward=lambda:{99})
        m=NS(pointer=0,native=None,drives=[NS(id=s,strength=1.) for s in range(3)],strong_influence=lambda:g,
             coverage_wait={s:0. for s in range(8)},path_waiting={s:dict(eligible_checks=0,unserved_checks=0,current_wait_checks=0,maximum_wait_checks=0,accepted_births=0) for s in range(8)},
             request=lambda *a:len(terminals),terminal=lambda *a,**kw:terminals.append(a),emit=lambda *a,**kw:None)
        def attempt(site,blocked):calls.append(site);return next(counter)
        m._b_path_attempt=attempt
        result=method(variant,'b_path')(m)
        return m,calls,terminals,result

    def test_quota_repeat_and_pointer_unchanged(self):
        m,calls,terms,result=self.bpath('COVA',[('accepted',20),('accepted',21)])
        self.assertEqual(calls,[0,0]);self.assertEqual(result,[20,21]);self.assertEqual(m.pointer,1)
        self.assertEqual([t[3] for t in terms],['quota','quota'])

    def test_cost_propagates_failed_recycle_does_not(self):
        _,calls,terms,_=self.bpath('COVB',[('cost',None)])
        self.assertEqual(calls,[0]);self.assertEqual([t[3] for t in terms],['cost','cost'])
        _,calls,_,births=self.bpath('COVB',[('recycle_failed',None),('accepted',30),('accepted',31)])
        self.assertEqual(calls,[0,1,1]);self.assertEqual(births,[30,31])

    def test_actual_b1_retry_single_terminal_quota_and_timers(self):
        events=[];removed=[];terms=[];births=[]
        m=NS(coverage_recycled=False,coverage_locks={9:.1},step_index=300,birth_steps={9:0},
             novelty={s:20. for s in range(8)},drives=[NS(id=s,strength=1.,x=float(s),y=0.,phase=0.) for s in range(3)],
             output_first=lambda:False,request=lambda *a:len(terms),
             spiral_candidate=lambda *a:((1.,2.),1),feasible=lambda *a:None if removed else 'cost',
             emit=lambda *a,**kw:events.append((a,kw)),remove=lambda *a,**kw:removed.append((a,kw)),
             terminal=lambda *a,**kw:terms.append((a,kw)))
        def add(*a,**kw):births.append((a,kw));return 20+len(births)
        m.add=add
        with patch.object(K,'service_snapshot',return_value=dict(served=set(),eligible=[9],classes={9:'non-service'})):
            accepted=method('COVB','b1')(m)
        self.assertEqual(len(removed),1);self.assertEqual(len(accepted),2)
        self.assertEqual([a[3] for a,k in terms],['accepted','accepted','quota'])
        self.assertEqual(m.novelty[0],0.);self.assertEqual(m.novelty[1],0.);self.assertEqual(m.novelty[2],20.)
        self.assertTrue(terms[0][1]['initial_cost_refusal'])

    def test_actual_path_failed_retry_one_terminal_fixed_point(self):
        events=[];removed=[];terms=[];points=[]
        es=[NS(id=1,x=0.,y=0.,phase=.3),NS(id=2,x=2.,y=0.,phase=.1),NS(id=3,x=3.,y=2.,phase=.2)]
        g=NS(forward=lambda s:{1},backward=lambda:{2})
        m=NS(native=NS(elements=es,params=NS(k=8,radius=3.,K=1.),policy=lambda:(32.,)),drives=[],
             coverage_recycled=False,coverage_locks={3:.1},step_index=300,birth_steps={3:0},
             strong_influence=lambda:g,request=lambda *a:7,feasible=lambda *a:None if removed else 'cost',
             remove=lambda *a,**kw:removed.append((a,kw)),emit=lambda *a,**kw:events.append((a,kw)),
             terminal=lambda *a,**kw:terms.append((a,kw)),trial=lambda *a:points.append(a[-1]) or dict(valid=False))
        fn=method('COVB','_b_path_attempt')
        fn.__globals__.update(R_STAR=.556,TRIAL_NAMES=('valid',),geometry=lambda *a:([],[]),geometric_trial=lambda *a,**k:dict(valid=True))
        with patch.object(K,'service_snapshot',return_value=dict(served=set(),eligible=[3],classes={3:'non-service'})):
            self.assertEqual(fn(m,0,False),('recycle_failed',None))
        self.assertEqual(len(terms),1);self.assertEqual(terms[0][0][3],'recycle_failed')
        attempted=next(k['position'] for a,k in events if a[0]=='birth_attempt')
        self.assertEqual(points,[attempted]);self.assertEqual(len(removed),1)

    def test_exact_patch_and_rd3_parent_hash(self):
        import hashlib
        rd3=(HERE/'kernel_builder/_worktrees/RD3/evidence/tactical_composition_demo/growing_shapes/medium/rev7_design.py').read_text()
        for v in S.ARMS:
            receipt=json.loads((HERE/f'kernel_builder/{v}_BUILD.json').read_text())
            self.assertEqual(receipt['rd3_parent_design_sha256'],hashlib.sha256(rd3.encode()).hexdigest())
            design=(HERE/f'kernel_builder/_worktrees/{v}/evidence/tactical_composition_demo/growing_shapes/medium/rev7_design.py').read_text()
            self.assertEqual(design,K.apply_variant(rd3,v))
        with self.assertRaises(ValueError):K.apply_variant('wrong','COVA')


class ObserverChecks(unittest.TestCase):
    def birth(self,request=0):
        return dict(rule='birth_terminal',cost=1.,values=dict(request=request,birth_rule='B1',site=0,outcome='accepted'))

    def test_restoring_birth_and_gap_excluded_and_kept(self):
        o=observer([outage()]);snapshot=dict(served={0},routes={0:[1,2]},gaps={0:0.},fragment=dict(rooted=True,screened=False))
        with patch.object(T,'service_snapshot',return_value=snapshot):o.event(self.birth())
        result=o.finish();item=result['outages'][0]
        self.assertNotIn('B',item['non_repair_labels']);self.assertEqual(item['restoration_evidence'][0]['gap'],0.)
        self.assertEqual(item['restoration_evidence'][0]['weight'],0)

    def test_earlier_nonrepair_birth_still_B_and_finite_gap_shrink_not_B(self):
        for gap,expected in ((3.,True),(2.,False),(None,True)):
            item=outage(gap=gap);o=observer([item])
            snapshot=dict(served=set(),routes={},gaps={0:gap if gap!=2. else 1.},fragment=dict(rooted=True,screened=False))
            with patch.object(T,'service_snapshot',return_value=snapshot):o.event(self.birth())
            snapshot.update(served={0},routes={0:[1,2]},gaps={0:0.})
            with patch.object(T,'service_snapshot',return_value=snapshot):o.event(self.birth(1))
            self.assertEqual('B' in o.finish()['outages'][0]['non_repair_labels'],expected)

    def test_new_outage_does_not_inherit_birth(self):
        o=observer([]);o.previous=dict(served={0},routes={0:[1,2]})
        snapshot=dict(served=set(),routes={},gaps={0:3.},fragment=dict(rooted=True,screened=False))
        with patch.object(T,'service_snapshot',return_value=snapshot),patch.object(T,'break_labels',return_value=('X',[],[])):
            o.event(self.birth())
        self.assertEqual(o.open[0]['terminals'],[])

    def test_recycle_cost_observation_and_censoring(self):
        o=observer([outage()]);o.live.step_index=7800
        o.event(dict(rule='coverage_cost_refusal',cost=1.,values=dict(request=0,birth_rule='B-path',site=2)))
        o.event(dict(rule='coverage_recycle',cost=1.,ids=[9],values=dict(request=0,birth_rule='B-path',site=2,donor_class='non-service',donor_lock=.1,age_steps=200,retry_outcome='accepted')))
        r=o.finish()
        self.assertNotIn('C',r['outages'][0]['non_repair_labels']);self.assertEqual(len(r['initial_cost_refusals']),1);self.assertEqual(r['recycles'][0]['served_within_60s'],'CENSORED')


class SchedulerChecks(unittest.TestCase):
    def test_pattern_repository_only_and_never_concurrent_pgrep(self):
        root=str(S.ROOT)
        commands=[('/usr/bin/python3 '+root+'/evidence/tactical_composition_demo/astelia_cpp/s4_spacing_probe_v1/run.py',True),
                  (root+'/.venv/bin/python -u '+root+'/evidence/tactical_composition_demo/astelia_cpp/s4_escort_probe_v1/execute.py',True),
                  (root+'/evidence/tactical_composition_demo/astelia_cpp/build/astelia_native --jsonl',True),
                  ('/usr/bin/python3 /other/ai_RPG_test/evidence/tactical_composition_demo/astelia_cpp/s4_spacing_probe_v1/run.py',False),
                  ('/usr/bin/pgrep -fl '+S.PATTERN,False),('pgrep -fl '+S.PATTERN,False),
                  ('/other/ai_RPG_test/native/astelia_native',False),('/usr/bin/python3 '+root+'/other/run.py',False)]
        for command,expected in commands:self.assertEqual(bool(re.search(S.PATTERN,command)),expected,command)

    def test_process_failure_denies_no_subprocess_listing(self):
        with patch.object(S.subprocess,'run',return_value=NS(returncode=3,stdout='',stderr='denied')):self.assertEqual(S.process_check()['status'],'PROCESS_ACCESS_BLOCKED')
        with patch.object(S.subprocess,'run',side_effect=OSError('denied')):self.assertEqual(S.process_check()['status'],'PROCESS_ACCESS_BLOCKED')
        with patch.object(S.subprocess,'run',return_value=NS(returncode=1,stdout='',stderr='')):self.assertEqual(S.process_check()['status'],'CLEAR')

    def test_remaining_projection_pairs_workers_and_deadline(self):
        self.assertEqual(len(S.JOBS),22);self.assertEqual(len(set(S.JOBS)),22)
        self.assertEqual(S.projection(22,10,660),1980)
        self.assertEqual(S.projection(2,1,1000,500),2500)
        self.assertEqual(S.CAP,3600);self.assertEqual(S.MAX_WORKERS,10)

    def test_resume_completed_identity_and_raw_corruption_incomplete_refusal(self):
        with tempfile.TemporaryDirectory(dir=HERE/'_local') as tmp:
            out=Path(tmp);job=('COVA','i',0,'on');name=S.job_name(job);raw=out/'raw.gz';raw.write_bytes(b'fixture')
            row=dict(variant='COVA',start='i',keyset=0,observer='on',code_hashes={'fixture':'hash'},clone_isolation='PASS',cpu_seconds=1.,elapsed_seconds=2.,state_trajectory_sha256='a'*64,telemetry=dict(label_revision='AMENDMENT_1'),raw_traces=[dict(path='raw.gz',bytes=7,sha256=S.sha(raw))])
            summary=out/(name+'.summary.json');summary.write_text(json.dumps(row))
            with patch.object(S,'OUT',out):
                self.assertEqual(S.load_completed(job,row['code_hashes'],out),row)
                with self.assertRaises(RuntimeError):S.load_completed(job,{'different':'code'},out)
                raw.write_bytes(b'corrupt')
                with self.assertRaises(RuntimeError):S.load_completed(job,row['code_hashes'],out)
                summary.unlink();(out/(name+'.started')).write_text('started')
                with self.assertRaises(RuntimeError):S.load_completed(job,row['code_hashes'],out)

    def test_build_hashes_and_all_sources_pinned_without_running_medium(self):
        for v in S.ARMS:S.validate_build(v)
        hashes=S.code_hashes()
        self.assertIn(str(HERE/'run_coverage_pilot.py'),hashes)
        self.assertTrue(any(p.endswith('/runner/rev7_run.py') for p in hashes))
        S.check_frozen(hashes)

    def test_integrity_requires_summary_and_state_both_arms(self):
        rows=[]
        for v in S.ARMS:
            for o in ('on','off'):rows.append(dict(variant=v,start='i',keyset=0,observer=o,summary={'assay':1},state_trajectory_sha256='x',clone_isolation='PASS'))
        self.assertEqual(S.integrity(rows),dict.fromkeys(S.ARMS,'PASS'))
        rows[-1]['state_trajectory_sha256']='y';self.assertEqual(S.integrity(rows)['COVB'],'FAIL')


class ReportChecks(unittest.TestCase):
    def test_reading_complete_and_incomplete_thresholds(self):
        control=dict(status='DONE',pooled_3_6=.1)
        arm=dict(status='DONE',pooled_3_6=.2,gate_shape={'i':{'passes':4}})
        self.assertEqual(R.reading(arm,control,True),'COVERAGE_IMPROVES')
        self.assertEqual(R.reading(arm,control,False),'INCOMPLETE')
        arm['gate_shape']['i']['passes']=3;self.assertEqual(R.reading(arm,control,True),'REGRESSION')
        arm['status']='INCOMPLETE';self.assertEqual(R.reading(arm,control,True),'INCOMPLETE')

    def test_control_pooling_legacy_and_receipts_untouched(self):
        path=HERE/'SERVICE_RUN_SUMMARIES.json';before=path.read_bytes()
        rows=[r for r in json.loads(before)['runs'] if r['variant']=='RD3']
        a=R.aggregate(rows,legacy=True)
        active=sum(r['telemetry']['sites'][str(s)]['active_steps'] for r in rows for s in range(3,7))
        served=sum(r['telemetry']['sites'][str(s)]['active_served_steps'] for r in rows for s in range(3,7))
        self.assertEqual(a['pooled_3_6'],served/active);self.assertNotIn('B',a['non_repair_causes']);self.assertEqual(a['non_repair_causes']['legacy_B'],17)
        self.assertEqual(path.read_bytes(),before)

    def test_partial_report_retains_valid_completions(self):
        historical=json.loads((HERE/'SERVICE_RUN_SUMMARIES.json').read_text())['runs']
        row=copy.deepcopy(next(r for r in historical if r['variant']=='RD3'))
        row.update(variant='COVA',observer='on');row['telemetry'].update(terminals=[],recycles=[],initial_cost_refusals=[])
        def completed(job,baseline):
            if job==('COVA',row['start'],row['keyset'],'on'):return row
            if job==('COVB','i',0,'on'):raise RuntimeError('started/incomplete')
            return None
        with tempfile.TemporaryDirectory(dir=HERE/'_local') as tmp:
            out=Path(tmp)
            for name in ('SERVICE_RUN_SUMMARIES.json','COVERAGE_DIAGNOSTIC.json'):(out/name).write_bytes((HERE/name).read_bytes())
            (out/'COVERAGE_RUN_SUMMARIES.json').write_text(json.dumps(dict(status='PARTIAL',runs=[row])))
            with patch.object(R,'OUT',out),patch.object(R,'code_hashes',return_value={}),patch.object(R,'load_completed',side_effect=completed):
                self.assertEqual(R.main(),2)
            compact=json.loads((out/'COVERAGE_COMPACT_SUMMARIES.json').read_text())
            self.assertEqual(len(compact['arms']['COVA']['runs']),1)
            self.assertEqual(compact['arms']['COVA']['reading'],'INCOMPLETE')
            self.assertEqual(compact['status'],'PARTIAL');self.assertTrue(compact['verification_errors'])
            self.assertEqual(len(compact['control']['births_per_run']),10)

    def test_birth_outcomes_retries_cost_time(self):
        t=dict(terminals=[dict(site=2,outcome='accepted',initial_cost_refusal=True,t=20.)],recycles=[])
        r=R.birth_metrics(t)
        self.assertEqual(r['first_cost_refusal_t'],20.);self.assertEqual(r['births_per_site']['2'],1)


if __name__=='__main__':unittest.main()
