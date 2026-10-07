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
import debt_kernel as K
import debt_telemetry as T
import execute_debt_plan as S
import write_debt_report as R


def source(variant):
    if variant == 'RD3':
        baseline = subprocess.check_output(['git', 'show', 'fd21826:evidence/tactical_composition_demo/growing_shapes/medium/rev7_design.py'], cwd=S.ROOT, text=True)
        baseline = K.replace_once(baseline,
            "            e=min(eligible,key=lambda e:(measured[e.id] or 0.,e.id));self.remove(e.id,'D3',lock=measured[e.id])\n",
            (HERE/'kernel_builder/ranked_d3_body.txt').read_text())
        return baseline + '\n# Scratch-only service geometry, independent of the observer.\nfrom service_graph import service_snapshot, ranked_choice\n'
    return (HERE / f'kernel_builder/_worktrees/{variant}/evidence/tactical_composition_demo/growing_shapes/medium/rev7_design.py').read_text()


def method(name):
    cls = next(n for n in ast.parse(source('DEBT')).body if isinstance(n, ast.ClassDef) and n.name == 'Rev7Medium')
    fn = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == name)
    scope = dict(deque=deque, deepcopy=copy.deepcopy, math=math, debt_order=K.debt_order,
                 deficit=lambda n, front, back: min(front, default=math.inf))
    exec(compile(ast.Module(body=[fn], type_ignores=[]), 'actual-debt-method', 'exec'), scope)
    return scope[name]


class KernelChecks(unittest.TestCase):
    def test_never_reset_rootloss_idle_and_active_rootless(self):
        m = NS(service_debt=dict.fromkeys(range(8), 0.))
        for snapshot in [dict(active={0, 1, 2}, served={1}),
                         dict(active={1}, served={0, 1}), dict(active={0}, served=set())]:
            with patch.object(K, 'service_snapshot', return_value=snapshot):
                K.update_debt(m)
        self.assertEqual(m.service_debt[0], .2)
        self.assertEqual(m.service_debt[1], 0.)
        self.assertEqual(m.service_debt[2], .1)

    def test_finite_class_pointer_and_cumulative_float(self):
        self.assertEqual(K.debt_order({0:9., 1:1., 2:math.inf, 3:math.inf},
                                    {0:20., 1:20., 2:999., 3:999.}, 1), [1, 0, 2, 3])
        m = NS(service_debt=dict.fromkeys(range(8), 0.))
        with patch.object(K, 'service_snapshot', return_value=dict(active={0}, served=set())):
            for _ in range(8): K.update_debt(m)
        self.assertEqual(m.service_debt[0], sum([.1]*8))

    def test_patch_parent_hash_and_every_other_method_unchanged(self):
        rd3 = source('RD3')
        self.assertEqual(source('DEBT'), K.apply_variant(rd3))
        receipt = json.loads((HERE/'kernel_builder/DEBT_BUILD.json').read_text())
        self.assertEqual(receipt['rd3_parent_design_sha256'], hashlib.sha256(rd3.encode()).hexdigest())
        classes = [next(n for n in ast.parse(source(v)).body if isinstance(n, ast.ClassDef) and n.name == 'Rev7Medium') for v in ('RD3', 'DEBT')]
        functions = [{n.name: n for n in c.body if isinstance(n, ast.FunctionDef)} for c in classes]
        for name in functions[0]:
            if name not in ('__init__', 'integrate', 'b_path'):
                self.assertEqual(ast.dump(functions[0][name]), ast.dump(functions[1][name]), name)
        self.assertEqual(functions[1]['integrate'].body[-2].value.func.id, 'update_debt')
        self.assertIsInstance(functions[1]['integrate'].body[-1], ast.Return)
        with self.assertRaises(ValueError): K.apply_variant('wrong')

    def test_actual_clone_independent_debt(self):
        m = type('FakeMedium', (), {})()
        m.__dict__.update(service_debt={s:float(s) for s in range(8)}, native=NS(clone=lambda:NS()), events=[], frames=deque([], maxlen=601))
        clone = method('clone')(m)
        clone.service_debt[0] = 99.
        self.assertEqual(m.service_debt[0], 0.)

    def run_path(self, outcomes, output_first=True):
        calls=[];terminals=[];sequence=iter(outcomes)
        graph=NS(path=lambda s: not output_first and s==7, forward=lambda s:{s}, backward=lambda:{99})
        m=NS(pointer=0, native=None, drives=[NS(id=s,strength=1.) for s in (0,1,2,7)],
             strong_influence=lambda:graph, service_debt={s:10.-s for s in range(8)},
             path_waiting={s:dict(eligible_checks=0,unserved_checks=0,current_wait_checks=0,maximum_wait_checks=0,accepted_births=0) for s in range(8)},
             request=lambda *a:len(terminals), terminal=lambda *a,**kw:terminals.append(a), emit=lambda *a,**kw:None)
        def attempt(site,blocked): calls.append(site); return next(sequence)
        m._b_path_attempt=attempt
        births=method('b_path')(m)
        return m,calls,terminals,births

    def test_actual_quota_repeat_pointer_and_resource_stop(self):
        m,calls,terms,births=self.run_path([('accepted',20),('accepted',21)])
        self.assertEqual(calls,[0,0]);self.assertEqual(births,[20,21]);self.assertEqual(m.pointer,1)
        self.assertTrue(all(t[3]=='quota' for t in terms))
        _,calls,terms,_=self.run_path([('cost',None)])
        self.assertEqual(calls,[0]);self.assertTrue(all(t[3]=='cost' for t in terms))
        _,calls,_,_=self.run_path([('accepted',20),('accepted',21)],False)
        self.assertEqual(calls,[0,1])


class ObserverChecks(unittest.TestCase):
    def test_order_comparisons_and_pure_debt_separate(self):
        row=T.order_comparison({0:9.,1:1.,2:math.inf},{0:5.,1:4.,2:99.},{0:0.,1:9.,2:20.},0)
        self.assertEqual(row['order'],[0,1,2]);self.assertEqual(row['rd3_order'],[1,0,2])
        self.assertEqual(row['cova_order'],[1,0,2]);self.assertEqual(row['pure_debt_diagnostic_order'],[2,0,1])

    def test_fake_on_off_digest_and_clones_do_not_record(self):
        # Fake classes loaded through the exact installer import; no native import or step.
        import types
        module=types.ModuleType('evidence.tactical_composition_demo.growing_shapes.medium.rev7_design')
        digests=[]
        for enabled in (False,True):
            class Fake:
                def integrate(self,drives): self.step_index+=1;self.service_debt[0]+=.1
                def remove(self,*a,**kw): pass
                def emit(self,*a,**kw): pass
                def growth(self,*a,**kw): pass
                def b_path(self,*a,**kw): pass
            module.Rev7Medium=Fake
            def make():
                m=Fake();m.step_index=0;m.birth_steps={};m.death={};m.novelty={};m.pointer=0;m.request_counter=0;m.growth_rng=None
                m.service_debt=dict.fromkeys(range(8),0.);m.native=NS(save=lambda:b'fake-state',elements=[])
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
                holder=T.install_observer(P,Run,'DEBT',None,digest,enabled)
                Run(live).step_boundary()
                before=digest.hexdigest()
                Run(clone).step_boundary()
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
        self.assertFalse(any(p.endswith('.md') or p.endswith('DEBT_CAP.json') for p in baseline))
        with tempfile.TemporaryDirectory(dir=HERE/'_local') as tmp:
            cap=Path(tmp)/'cap.json'
            self.assertEqual(S.read_cap(cap),5400)
            for value in (100.,10000.):
                cap.write_text(json.dumps(dict(cap_seconds=value)))
                self.assertEqual(S.read_cap(cap),value)
                self.assertEqual(S.code_hashes(),baseline)
            cap.write_text('{"cap_seconds":true}')
            with self.assertRaises(ValueError):S.read_cap(cap)
        self.assertEqual(len(S.JOBS),11);self.assertEqual(len(set(S.JOBS)),11);self.assertEqual(S.MAX_WORKERS,10)

    def test_identity_raw_set_corruption_started_and_resume(self):
        with tempfile.TemporaryDirectory(dir=HERE/'_local') as tmp:
            out=Path(tmp);local=out/'debt';local.mkdir();job=('DEBT','i',0,'on');name=S.job_name(job)
            build=out/'kernel_builder';build.mkdir();(build/'DEBT_BUILD.json').write_text('{"build":{"binary_sha256":"binary"}}')
            raw=[]
            for ext in ('.legacy.json.gz','.jsonl.gz'):
                p=local/(name+ext);p.write_bytes(b'fixture');raw.append(dict(path=str(p.relative_to(out)),bytes=7,sha256=S.sha(p)))
            row=dict(variant='DEBT',start='i',keyset=0,observer='on',code_hashes={'a':'b'},binary_sha256='binary',
                     summary=dict(steps=8000,last_t=800.),clone_isolation='PASS',elapsed_seconds=1.,cpu_seconds=1.,
                     state_trajectory_sha256='a'*64,raw_traces=raw,telemetry=dict(steps=8000,debt_boundary_steps=8000,label_revision='AMENDMENT_1_DEBT'))
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
            out=Path(tmp);local=out/'debt';cap=out/'CAP.json';cap.write_text('{"cap_seconds":5555}')
            with patch.object(S,'OUT',out),patch.object(S,'LOCAL',local),patch.object(S,'CAP_CONFIG',cap),\
                 patch.object(S,'process_check',return_value=dict(status='CLEAR')),patch.object(S,'code_hashes',return_value={}),\
                 patch.object(S,'load_completed',side_effect=lambda j,b:rows[j]),patch.object(S,'estimate_seconds',return_value=100.),\
                 patch.object(S,'worker',side_effect=AssertionError('rerun')),patch.object(S.subprocess,'Popen',side_effect=AssertionError('unnecessary process')):
                self.assertEqual(S.main(),0)
            receipt=json.loads((out/'DEBT_RUN_SUMMARIES.json').read_text())
            self.assertEqual(receipt['timing']['cap_seconds'],5555)
            self.assertEqual(len(receipt['timing']['reused']),11)
            self.assertEqual(receipt['integrity'],{'DEBT':'PASS'})

    def test_main_denied_or_projection_stop_no_workers(self):
        for blocked in (True,False):
            with tempfile.TemporaryDirectory(dir=HERE/'_local') as tmp:
                out=Path(tmp);local=out/'debt'
                with patch.object(S,'OUT',out),patch.object(S,'LOCAL',local),patch.object(S,'read_cap',return_value=1.),\
                     patch.object(S,'process_check',return_value=dict(status='PROCESS_ACCESS_BLOCKED' if blocked else 'CLEAR')),\
                     patch.object(S,'code_hashes',return_value={}),patch.object(S,'load_completed',return_value=None),\
                     patch.object(S,'estimate_seconds',return_value=660.),patch.object(S,'worker',side_effect=AssertionError('launched')):
                    self.assertEqual(S.main(),2)
                receipt=json.loads((out/'DEBT_RUN_SUMMARIES.json').read_text())
                self.assertEqual(receipt['status'],'NOT_RUN');self.assertTrue(receipt['timing']['stop_reason'])


class ReportChecks(unittest.TestCase):
    def test_exact_threshold_integrity_and_missing_not_regression(self):
        arm=dict(status='DONE',pooled_3_6=R.TARGET,gate_shape={'i':{'passes':4}})
        self.assertEqual(R.readings(arm,True)['coverage'],'COVERAGE_IMPROVES')
        arm['pooled_3_6']=math.nextafter(R.TARGET,0)
        self.assertEqual(R.readings(arm,True)['coverage'],'DESCRIPTIVE')
        arm['gate_shape']['i']['passes']=3
        self.assertEqual(R.readings(arm,True)['coverage'],'REGRESSION')
        self.assertEqual(R.readings(arm,False)['coverage'],'INCOMPLETE')
        arm['status']='INCOMPLETE'
        self.assertEqual(R.readings(arm,True)['coverage'],'INCOMPLETE')

    def test_minima_distinguishes_pooled_and_per_run_denominators(self):
        rows=[]
        control=json.loads((HERE/'SERVICE_RUN_SUMMARIES.json').read_text())['runs']
        original=next(r for r in control if r['variant']=='RD3')
        for key,served in ((0,0),(1,100)):
            row=copy.deepcopy(original);row.update(keyset=key)
            for s in range(8):
                row['telemetry']['sites'][str(s)].update(active_steps=100,active_served_steps=served,served_fraction_active=served/100)
            rows.append(row)
        data=R.minima(R.aggregate(rows))
        self.assertEqual(data['minimum_of_eight_pooled_site_fractions'],.5)
        self.assertEqual(data['minimum_over_all_site_run_fractions'],0.)

    def test_report_notrun_crashed_and_partial_preserves_controls(self):
        for state in ('NOT_RUN','CRASH','PARTIAL'):
            with tempfile.TemporaryDirectory(dir=HERE/'_local') as tmp:
                out=Path(tmp);local=out/'debt'
                for name in ('SERVICE_RUN_SUMMARIES.json','COVERAGE_RUN_SUMMARIES.json'):
                    (out/name).write_bytes((HERE/name).read_bytes())
                row=copy.deepcopy(next(r for r in json.loads((out/'SERVICE_RUN_SUMMARIES.json').read_text())['runs'] if r['variant']=='RD3'))
                row.update(variant='DEBT',observer='on')
                row['telemetry'].update(debt_samples=[],order_checks=[],mass_samples=[],terminals=[],recycles=[])
                if state!='NOT_RUN':local.mkdir();(local/'DEBT_i_k0_on.started').write_text('started')
                if state=='PARTIAL':(out/'DEBT_RUN_SUMMARIES.json').write_text(json.dumps(dict(status='PARTIAL',runs=[row])))
                def load(job,*a):
                    if state=='PARTIAL' and job==('DEBT',row['start'],row['keyset'],'on'):return row
                    if state=='CRASH' and job==S.JOBS[0]:raise RuntimeError('started/incomplete')
                    return None
                originals={p:p.read_bytes() for p in out.glob('*SUMMARIES.json') if p.name!='DEBT_RUN_SUMMARIES.json'}
                with patch.object(R,'OUT',out),patch.object(R,'LOCAL',local),patch.object(R,'code_hashes',return_value={}),patch.object(R,'load_completed',side_effect=load):
                    R.main()
                data=json.loads((out/'DEBT_COMPACT_SUMMARIES.json').read_text())
                self.assertEqual(data['status'],'NOT_RUN' if state=='NOT_RUN' else 'PARTIAL')
                self.assertEqual(data['arm']['readings']['coverage'],'INCOMPLETE')
                for p,bytes_ in originals.items():self.assertEqual(p.read_bytes(),bytes_)


if __name__ == '__main__':
    unittest.main()
