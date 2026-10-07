"""Synthetic checks only: no native step, assay, pilot or real process listing."""
import ast
from collections import deque
import copy
import hashlib
import io
import json
import math
from pathlib import Path
import re
import sys
import subprocess
import tempfile
import unittest
from types import SimpleNamespace as NS
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import capacity_kernel as K
import capacity_telemetry as T
import execute_capacity_plan as S
import write_capacity_report as R


def scratch(variant):
    return (HERE/f'kernel_builder/_worktrees/{variant}/evidence/tactical_composition_demo/growing_shapes/medium/rev7_design.py').read_text()


def method(variant, name, **scope):
    cls = next(n for n in ast.parse(scratch(variant)).body if isinstance(n, ast.ClassDef) and n.name == 'Rev7Medium')
    fn = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == name)
    exec(compile(ast.Module(body=[fn], type_ignores=[]), 'actual-capacity-method', 'exec'), scope)
    return scope[name]


class KernelChecks(unittest.TestCase):
    def test_exact_rd3_parent_and_only_three_literal_changes(self):
        rd3 = scratch('RD3')
        original = ast.dump(ast.parse(rd3))
        for v, cap in K.CEILINGS.items():
            self.assertEqual(scratch(v), K.apply_variant(rd3, v))
            receipt=json.loads((HERE/f'kernel_builder/{v}_BUILD.json').read_text())
            self.assertEqual(receipt['rd3_parent_design_sha256'],hashlib.sha256(rd3.encode()).hexdigest())
            self.assertEqual(receipt['base_commit'],'fd2182681ee8ed7b7b3a0772d69de898a8aa17c2')
            tree=ast.parse(scratch(v));count=0
            for n in ast.walk(tree):
                if isinstance(n,ast.Constant) and type(n.value) is int and n.value==cap:
                    n.value=64;count+=1
            self.assertEqual(count,3)
            self.assertEqual(ast.dump(tree),original)
        with self.assertRaises(ValueError):K.apply_variant('wrong','CAP96')

    def test_actual_count_and_prospective_cost_admission_boundaries(self):
        for v,cap in K.CEILINGS.items():
            for n,cost,want in ((cap,0,'cap'),(cap-1,cap,None),(cap-1,cap+.01,'cost')):
                m=NS(native=NS(elements=[],params=NS(k=8,radius=3)),drives=[])
                scope=dict(clear_position=lambda *a:True,geometry=lambda *a:([(i,0,0,'element') for i in range(n)],[]),
                           geometric_graph=lambda *a:NS(incoming={}),budget_counts=lambda *a:(cost,0))
                self.assertEqual(method(v,'feasible',**scope)(m,(0,0),0),want)

    def test_actual_d3_trigger_and_ranking_unchanged(self):
        for v,cap in K.CEILINGS.items():
            for cost,expected in ((cap,[]),(cap+.1,[(1,'D3')])):
                es=[NS(id=1)];removed=[]
                m=NS(frozen=False,native=NS(elements=es,cut_off=lambda i:0,__len__=lambda:1),
                     lock=lambda i:1,death={},role=lambda i:'element',step_index=1000,birth_steps={1:0},
                     emit=lambda *a,**kw:None,cost=lambda:cost if not removed else cap,
                     b_out=lambda b:[],b_path=lambda b:[],b1=lambda b:[],pointer=0)
                class Native:
                    elements=es
                    def cut_off(self,i):return 0
                    def __len__(self):return 1
                m.native=Native()
                m.remove=lambda id,rule,**kw:removed.append((id,rule))
                method(v,'growth',service_snapshot=lambda m:{},ranked_choice=lambda *a:(1,[]))(m)
                self.assertEqual(removed,expected)


class ObserverChecks(unittest.TestCase):
    def test_actual_growth_end_and_event_reporting(self):
        import coverage_telemetry as C
        snapshot=dict(active={0},served=set(),active_served=set(),routes={s:[] for s in range(8)},
                      roots={s:set() for s in range(8)},outgoing={},incoming={},outputs=set(),positions={},held={},
                      fragment=dict(rooted=False,screened=False),eligible=[],classes={},selected={},degree={},ids=[],
                      gaps={s:None for s in range(8)},pairs=set())
        medium=NS(step_index=50,events=[],cost=lambda:0.)
        with tempfile.TemporaryDirectory(dir=HERE/'_local') as tmp,\
             patch.object(C,'service_snapshot',return_value=snapshot),patch.object(T,'service_snapshot',return_value=snapshot):
            obs=T.Observer(medium,Path(tmp)/'trace.gz','CAP128')
            obs.event(dict(rule='birth_request',values=dict(request=1,birth_rule='B-path',site=0),cost=0.))
            obs.growth_end(0)
            self.assertEqual(obs.requests[-1]['cap'],128)
            self.assertEqual(obs.growth_checks[-1]['cap'],128)
            obs.step()
            telemetry=obs.finish()
            self.assertEqual(telemetry['cost_ceiling'],128)
            self.assertEqual(len(telemetry['capacity_samples']),1)
            import gzip
            rows=[json.loads(line) for line in gzip.open(Path(tmp)/'trace.gz','rt')]
            for row in rows:
                if row['kind'] in ('event','growth_check','world_step','capacity_sample'):
                    self.assertEqual(row['cost_ceiling'],128)
                    self.assertEqual(row['count_ceiling'],128)

    def test_mass_cost_ratios_and_zero_service(self):
        snapshot=dict(ids=[1,2,3],outputs={3},held={1:[2,3],2:[1],3:[1]},classes={1:'critical',2:'non-service',3:'critical'},
                      roots={s:{1} for s in range(8)},outgoing={1:{2,3},2:{1},3:set()},served={0,1},active_served={1})
        sample=T.capacity_sample(snapshot,5.,2.1,96)
        self.assertAlmostEqual(sum(c['cost'] for c in sample['classes'].values()),2.1)
        self.assertEqual(sample['cost_per_structurally_served_site'],1.05)
        self.assertEqual(sample['cost_per_active_served_site'],2.1)
        snapshot.update(served=set(),active_served=set())
        sample=T.capacity_sample(snapshot,5.,2.1,128)
        self.assertIsNone(sample['cost_per_active_served_site'])
        self.assertIsNone(sample['cost_per_structurally_served_site'])
        self.assertTrue(sample['zero_active_service'] and sample['zero_structural_service'])
        with self.assertRaises(AssertionError):T.capacity_sample(snapshot,5.,9.,96)

    def test_inherited_transitions_and_exact_reporting_only_overrides(self):
        import coverage_telemetry as C
        for name in ('integrate','transition','finish'):
            if name!='finish':self.assertIs(getattr(T.Observer,name),getattr(C.Observer,name))
        old=ast.parse((HERE/'coverage_telemetry.py').read_text())
        new=ast.parse((HERE/'capacity_telemetry.py').read_text())
        self.assertEqual(ast.dump(old.body[-1]),ast.dump(new.body[-1])) # exact installer/digest
        classes=[next(n for n in t.body if isinstance(n,ast.ClassDef) and n.name=='Observer') for t in (old,new)]
        for name in ('event','growth_end'):
            funcs=[next(n for n in c.body if isinstance(n,ast.FunctionDef) and n.name==name) for c in classes]
            for node in ast.walk(funcs[1]):
                if isinstance(node,ast.Call):
                    node.keywords=[k for k in node.keywords if k.arg not in ('cost_ceiling','count_ceiling')]
                    for k in node.keywords:
                        if k.arg=='cap':k.value=ast.Constant(value=64)
            self.assertEqual(ast.dump(funcs[0]),ast.dump(funcs[1]))
        obs=T.Observer.__new__(T.Observer);obs.variant='CAP128'
        with patch.object(C.Observer,'removal_before',side_effect=lambda *a:T.Observer.__name__):
            obs.removal_before(1,'D3',{})
        self.assertEqual(obs.variant,'CAP128')
        with patch.object(C.Observer,'removal_before',side_effect=lambda *a:self.assertEqual(obs.variant,'RD3')):
            obs.removal_before(1,'D3',{})

    def test_fake_on_off_digest_and_clone_exclusion(self):
        import types
        module=types.ModuleType('evidence.tactical_composition_demo.growing_shapes.medium.rev7_design');digests=[]
        for enabled in (False,True):
            class Fake:
                def integrate(self,drives):self.step_index+=1
                def remove(self,*a,**kw):pass
                def emit(self,*a,**kw):pass
                def growth(self,*a,**kw):pass
            module.Rev7Medium=Fake
            def make():
                m=Fake();m.__dict__.update(step_index=0,birth_steps={},death={},novelty={},pointer=0,request_counter=0,growth_rng=None,
                                           native=NS(save=lambda:b'fake-state',elements=[]))
                return m
            live,clone=make(),make();P=NS(LIVE=[live])
            class Run:
                def __init__(self,m):self.medium=m
                def step_boundary(self):self.medium.integrate([])
            class Obs:
                def __init__(self,*a):self.steps=0;self.integrates=0
                def integrate(self):self.integrates+=1
                def step(self):self.steps+=1
            digest=hashlib.sha256()
            with patch.dict(sys.modules,{module.__name__:module}),patch.object(T,'Observer',Obs):
                holder=T.install_observer(P,Run,'CAP96',None,digest,enabled)
                Run(live).step_boundary();before=digest.hexdigest();Run(clone).step_boundary()
                self.assertEqual(digest.hexdigest(),before)
                if enabled:self.assertEqual((holder[0].steps,holder[0].integrates),(1,1))
            digests.append(digest.hexdigest())
        self.assertEqual(digests[0],digests[1])


class SchedulerChecks(unittest.TestCase):
    def test_gate_never_matches_pgrep_or_other_repo(self):
        root=str(S.ROOT)
        for cmd,want in [(f'/usr/bin/python3 {root}/evidence/tactical_composition_demo/astelia_cpp/s4_spacing_probe_v1/run.py',True),
                         (f'{root}/.venv/bin/python -u {root}/evidence/tactical_composition_demo/astelia_cpp/s4_escort_probe_v1/run.py',True),
                         (f'{root}/build/astelia_native --jsonl',True),
                         ('pgrep -fl '+S.PATTERN,False),('/usr/bin/pgrep -fl '+S.PATTERN,False),
                         ('/elsewhere/ai_RPG_test/build/astelia_native',False)]:
            self.assertEqual(bool(re.search(S.PATTERN,cmd)),want,cmd)
        with patch.object(S.subprocess,'run',return_value=NS(returncode=3,stderr='denied',stdout='')):
            self.assertEqual(S.process_check()['status'],'PROCESS_ACCESS_BLOCKED')

    def test_cap_config_not_in_identity_and_relaunch_reads_it(self):
        baseline=S.code_hashes()
        self.assertFalse(any(p.endswith('.md') or p.endswith('CAPACITY_CAP.json') for p in baseline))
        with tempfile.TemporaryDirectory(dir=HERE/'_local') as tmp:
            cap=Path(tmp)/'cap.json'
            self.assertEqual(S.read_cap(cap),5400)
            for value in (100.,10000.):
                cap.write_text(json.dumps(dict(cap_seconds=value)))
                self.assertEqual(S.read_cap(cap),value)
                self.assertEqual(S.code_hashes(),baseline)
            cap.write_text('{"cap_seconds":true}')
            with self.assertRaises(ValueError):S.read_cap(cap)
        self.assertEqual(len(S.JOBS),22);self.assertEqual(len(set(S.JOBS)),22);self.assertEqual(S.MAX_WORKERS,10)

    def test_identity_raw_set_corruption_started_and_resume(self):
        with tempfile.TemporaryDirectory(dir=HERE/'_local') as tmp:
            out=Path(tmp);local=out/'capacity';local.mkdir();job=('CAP96','i',0,'on');name=S.job_name(job)
            build=out/'kernel_builder';build.mkdir();(build/'CAP96_BUILD.json').write_text('{"build":{"binary_sha256":"binary"}}')
            raw=[]
            for ext in ('.legacy.json.gz','.jsonl.gz'):
                p=local/(name+ext);p.write_bytes(b'fixture');raw.append(dict(path=str(p.relative_to(out)),bytes=7,sha256=S.sha(p)))
            row=dict(variant='CAP96',start='i',keyset=0,observer='on',code_hashes={'a':'b'},binary_sha256='binary',
                     summary=dict(steps=8000,last_t=800.),clone_isolation='PASS',elapsed_seconds=1.,cpu_seconds=1.,
                     state_trajectory_sha256='a'*64,raw_traces=raw,telemetry=dict(steps=8000,label_revision='AMENDMENT_1_CAPACITY',cost_ceiling=96,count_ceiling=96,capacity_samples=[{}]*160,sites={str(s):dict(active_steps=100,active_served_steps=50,served_fraction_active=.5) for s in range(8)}))
            p=local/(name+'.summary.json');p.write_text(json.dumps(row))
            with patch.object(S,'OUT',out):
                self.assertEqual(S.load_completed(job,{'a':'b'},local),row)
                with self.assertRaises(RuntimeError):S.load_completed(job,{'changed':'code'},local)
                row['raw_traces']=raw[:1];p.write_text(json.dumps(row))
                with self.assertRaises(RuntimeError):S.load_completed(job,{'a':'b'},local)
                row['raw_traces']=raw;p.write_text(json.dumps(row));(out/raw[0]['path']).write_bytes(b'corrupt')
                with self.assertRaises(RuntimeError):S.load_completed(job,{'a':'b'},local)
                p.unlink()
                with self.assertRaises(RuntimeError):S.load_completed(job,{'a':'b'},local)

    def test_main_reuses_all_jobs_and_records_changed_cap_no_workers(self):
        rows={j:dict(variant=j[0],start=j[1],keyset=j[2],observer=j[3],summary={'same':1},
                     state_trajectory_sha256='a'*64,clone_isolation='PASS',cpu_seconds=1.,elapsed_seconds=1.) for j in S.JOBS}
        with tempfile.TemporaryDirectory(dir=HERE/'_local') as tmp:
            out=Path(tmp);local=out/'capacity';cap=out/'CAP.json';cap.write_text('{"cap_seconds":5555}')
            with patch.object(S,'OUT',out),patch.object(S,'LOCAL',local),patch.object(S,'CAP_CONFIG',cap),\
                 patch.object(S,'process_check',return_value=dict(status='CLEAR')),patch.object(S,'code_hashes',return_value={}),\
                 patch.object(S,'load_completed',side_effect=lambda j,b:rows[j]),patch.object(S,'estimate_seconds',return_value=100.),\
                 patch.object(S,'worker',side_effect=AssertionError('rerun')),patch.object(S.subprocess,'Popen',side_effect=AssertionError('unnecessary process')):
                self.assertEqual(S.main(),0)
            receipt=json.loads((out/'CAPACITY_RUN_SUMMARIES.json').read_text())
            self.assertEqual(receipt['timing']['cap_seconds'],5555)
            self.assertEqual(len(receipt['timing']['reused']),22)
            self.assertEqual(receipt['integrity'],{'CAP96':'PASS','CAP128':'PASS'})

    def test_main_denied_or_projection_stop_no_workers(self):
        for blocked in (True,False):
            with tempfile.TemporaryDirectory(dir=HERE/'_local') as tmp:
                out=Path(tmp);local=out/'capacity'
                with patch.object(S,'OUT',out),patch.object(S,'LOCAL',local),patch.object(S,'read_cap',return_value=1.),\
                     patch.object(S,'process_check',return_value=dict(status='PROCESS_ACCESS_BLOCKED' if blocked else 'CLEAR')),\
                     patch.object(S,'code_hashes',return_value={}),patch.object(S,'load_completed',return_value=None),\
                     patch.object(S,'estimate_seconds',return_value=660.),patch.object(S,'worker',side_effect=AssertionError('launched')):
                    self.assertEqual(S.main(),2)
                receipt=json.loads((out/'CAPACITY_RUN_SUMMARIES.json').read_text())
                self.assertEqual(receipt['status'],'NOT_RUN');self.assertTrue(receipt['timing']['stop_reason'])

    def test_projection_all_22_jobs_and_worker_bound(self):
        self.assertEqual(S.projection(22,10,660),1980)
        self.assertEqual(S.projection(12,10,660,100),1420)
        self.assertEqual(set(S.JOBS),{(v,s,k,'on') for v in S.ARMS for s in ('i','ii') for k in range(5)} |
                         {(v,'i',0,'off') for v in S.ARMS})

    def test_validation_invalid_and_zero_exposure(self):
        sites={str(s):dict(active_steps=100,active_served_steps=50,served_fraction_active=.5) for s in range(8)}
        S.validate_sites(sites)
        for a,b,f in ((100,101,1.01),(True,1,1),(100,50,.6),(-1,0,None)):
            bad=copy.deepcopy(sites);bad['0'].update(active_steps=a,active_served_steps=b,served_fraction_active=f)
            with self.assertRaises(RuntimeError):S.validate_sites(bad)


class ReportChecks(unittest.TestCase):
    def test_literal_cutoff_inclusive_between_integrity_and_complete_arms(self):
        control=dict(status='DONE',total_service=2.147575404987718)
        arms={'CAP96':dict(status='DONE',total_service=control['total_service']),
              'CAP128':dict(status='DONE',total_service=3.22)}
        self.assertEqual(R.reading(arms,control,True),'CAPACITY_SCALES_WITH_RESOURCE_CEILING')
        self.assertLess(R.POSITIVE_CUTOFF,1.5*control['total_service'])
        arms['CAP128']['total_service']=math.nextafter(3.22,0)
        self.assertEqual(R.reading(arms,control,True),'DESCRIPTIVE')
        arms['CAP128']['total_service']=3.3;arms['CAP96']['total_service']=3.3
        self.assertEqual(R.reading(arms,control,True),'CAPACITY_SCALES_WITH_RESOURCE_CEILING')
        arms['CAP96']['total_service']=3.4
        self.assertEqual(R.reading(arms,control,True),'DESCRIPTIVE')
        self.assertEqual(R.reading(arms,control,False),'INCOMPLETE')
        arms['CAP96']['status']='INCOMPLETE'
        self.assertEqual(R.reading(arms,control,True),'INCOMPLETE')

    def test_pooled_index_equal_site_weights_slots_and_denominators(self):
        original=next(r for r in json.loads((HERE/'SERVICE_RUN_SUMMARIES.json').read_text())['runs'] if r['variant']=='RD3')
        rows=[]
        for key,a,b in ((0,100,0),(1,900,900)):
            row=copy.deepcopy(original);row.update(start='i',keyset=key)
            for s in range(8):row['telemetry']['sites'][str(s)].update(active_steps=a,active_served_steps=b,served_fraction_active=b/a)
            rows.append(row)
        result=R.aggregate(rows)
        self.assertAlmostEqual(result['total_service'],7.2)
        self.assertEqual(result['status'],'INCOMPLETE')
        self.assertEqual(result['runs'][0]['total_service'],0.)
        with self.assertRaises(RuntimeError):R.aggregate(rows+[rows[0]])
        for r in rows:r['telemetry']['sites']['0'].update(active_steps=0,active_served_steps=0,served_fraction_active=None)
        self.assertIsNone(R.aggregate(rows)['total_service'])

    def test_report_states_integrity_raw_and_committed_controls_preserved(self):
        for state in ('NOT_RUN','CRASH','PARTIAL','DONE','MISMATCH','FAIL_PAIR','ZERO'):
            with tempfile.TemporaryDirectory(dir=HERE/'_local') as tmp:
                out=Path(tmp);local=out/'capacity'
                control=(HERE/'SERVICE_RUN_SUMMARIES.json').read_bytes();(out/'SERVICE_RUN_SUMMARIES.json').write_bytes(control)
                original=next(r for r in json.loads(control)['runs'] if r['variant']=='RD3')
                rows={}
                if state not in ('NOT_RUN','CRASH'):
                    jobs=S.JOBS if state in ('DONE','MISMATCH','FAIL_PAIR','ZERO') else S.JOBS[:1]
                    for j in jobs:
                        row=copy.deepcopy(original);row.update(variant=j[0],start=j[1],keyset=j[2],observer=j[3],clone_isolation='PASS',state_trajectory_sha256='a'*64,raw_traces=[])
                        row['telemetry'].update(capacity_samples=[],terminals=[],recycles=[])
                        if state=='FAIL_PAIR' and j[3]=='off':row['state_trajectory_sha256']='b'*64
                        if state=='ZERO':row['telemetry']['sites']['0'].update(active_steps=0,active_served_steps=0,served_fraction_active=None)
                        rows[j]=row
                    supplied=copy.deepcopy(list(rows.values()))
                    if state=='MISMATCH':supplied[0]['clone_isolation']='FAIL'
                    (out/'CAPACITY_RUN_SUMMARIES.json').write_text(json.dumps(dict(status='DONE' if len(rows)==22 else 'PARTIAL',runs=supplied)))
                if state!='NOT_RUN':local.mkdir();(local/'CAP96_i_k0_on.started').write_text('started')
                def load(job,*a):
                    if state=='CRASH' and job==S.JOBS[0]:raise RuntimeError('started/incomplete')
                    return rows.get(job)
                with patch.object(R,'OUT',out),patch.object(R,'LOCAL',local),patch.object(R,'code_hashes',return_value={}),\
                     patch.object(R,'load_completed',side_effect=load):
                    R.main()
                data=json.loads((out/'CAPACITY_COMPACT_SUMMARIES.json').read_text())
                self.assertEqual(data['status'],'DONE' if state=='DONE' else 'NOT_RUN' if state=='NOT_RUN' else 'PARTIAL')
                self.assertEqual(data['reading'],'DESCRIPTIVE' if state=='DONE' else 'INCOMPLETE')
                self.assertEqual((out/'SERVICE_RUN_SUMMARIES.json').read_bytes(),control)


if __name__=='__main__':unittest.main()
