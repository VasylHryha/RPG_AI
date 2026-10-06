"""Affected Part-1 tests: synthetic native observations and fake tuning, zero combat."""
import copy
import hashlib
import json
import subprocess
import sys
import pytest
import s4_v6 as V
from s3_v6_runner import request
from build_admission import admit


def scores(stage,novice,regular=0):
    return {json.dumps(b):novice if b[0]=='novice' else regular for b in V.battles(stage,'tuning')}


def test_native_v6_alias_and_historical_variants_without_combat():
    build=admit(V.BINARY)
    run=subprocess.run([str(V.BINARY),'--attribution-contract'],capture_output=True,text=True,check=True)
    rows=[json.loads(line) for line in run.stdout.splitlines()]
    assert all(r['status']=='passed' and r['fights']==0 for r in rows)
    assert rows[-1]['fixture_action_bytes_compared']>15000
    V.write(V.CHECKS/'NATIVE_CONTRACT.json',dict(results=rows,build=build,historical_v0_v5_contract_passed=True))


def test_fresh_declaration_budget_bounds_and_build():
    import s4_v3
    d=V.declaration()
    assert V.BOUNDS['morale']==s4_v3.BOUNDS['morale'] and V.BOUNDS['pushpull']==s4_v3.BOUNDS['pushpull']
    assert set(V.BOUNDS['resonator'])==set(s4_v3.BOUNDS['resonator'])-{'omega_melee'}|{'mu'}
    assert {a:len(b) for a,b in V.BOUNDS.items()}==dict(resonator=11,morale=11,pushpull=3)
    assert (V.POPULATION,V.GENERATIONS,V.CLUSTERS,V.VALIDATION_N,V.WORKERS,V.CAP_SECONDS)==(16,16,19,100,10,21600)
    assert V.TOTAL_FIGHTS==60996 and 38+16*16*38==V.TUNING_PER_ARM_STAGE
    assert d['status']=='FRESH_DEVELOPMENT_ONLY' and d['judging_root'] is None
    for stage in V.STAGES:
        for split in ('tuning','validation'):
            old=s4_v3.battles(stage,split)
            assert [(b[0],b[2]) for b in V.battles(stage,split)]==[(b[0],b[2]) for b in old]
    V.verify_sources();admit(V.BINARY)
    assert not (V.CHECKS/'LEDGER_USED.json').exists()


def test_request_v6_and_variants():
    for skeleton in ('v0','v1','v2','v3','v4','v5','v6','H','F','HF'):
        for arm in V.ARMS:
            req=request(dict(arm=arm,skeleton=skeleton,setting='s4_full_head',opponent='regular'))
            assert req['options']['ai'][0]['skeleton']==skeleton
            assert req['options']['army']==dict(melee=10,ranged=30,artillery=10)
    with pytest.raises(ValueError):V.battles('C','tuning')
    with pytest.raises(ValueError):V.battles('A','judging')


def test_eligibility_dominates_regular_and_zero_meets_constraint():
    eligible=V.selection('B',scores('B',0,-50));bad=V.selection('B',scores('B',-.001,50))
    assert eligible['rank']>bad['rank'] and eligible['objective']<bad['objective']
    assert eligible['eligible'] is True and bad['eligible'] is False
    assert V.selection('B',scores('B',20,2))['rank']==V.selection('B',scores('B',0,2))['rank']
    assert V.selection('B',scores('B',-20,2))['rank']>V.selection('B',scores('B',-.01,1))['rank']
    assert V.selection('A',scores('A',3))['objective']==-3
    partial=scores('B',0);partial.pop(next(iter(partial)))
    with pytest.raises(ValueError):V.selection('B',partial)
    with pytest.raises(ValueError):V.selection('B',scores('B',float('nan')))
    with pytest.raises(ValueError):V.selection('B',scores('B',0,51))


def validation(novice,regular):
    return {'resonator':{'s4_melee10|novice':{'stats':{'mean':novice}},
                         's4_full_head|novice':{'stats':{'mean':novice}},'s4_full_head|regular':{'stats':{'mean':regular}}}}


@pytest.mark.parametrize('novice,regular,status',[(1,-6.025,'NOT_READY'),(1,-6.024999,'PROGRESS'),(0,30,'NOT_READY'),(-1,-8,'NOT_READY')])
def test_exact_separate_validation_gates(novice,regular,status):
    g=V.stage_gate('B',validation(novice,regular));assert g['status']==status and g['C_authorized'] is False
    assert g['novice_validation_pass']==(novice>0) and g['regular_progress_pass']==(regular>-6.025)
    assert V.stage_gate('A',validation(novice,regular))['status']==('CONTINUE' if novice>0 else 'NOT_READY')


class FakeOptimizer:
    sigma=.25
    def __init__(self):self.feedback=[]
    def ask(self):return [V.normalized('resonator',V.defaults('resonator')) for _ in range(16)]
    def tell(self,x,loss):self.feedback.append(loss)
    def stop(self):return {}


@pytest.mark.parametrize('all_ineligible',[False,True])
def test_actual_tune_feedback_retention_ties_and_budget(tmp_path,monkeypatch,all_ineligible):
    es=FakeOptimizer()
    class Bench:
        out=tmp_path;locked={};identity='fake';started=V.time.monotonic()
        deadline=V.Deadline(V.time.monotonic()+V.CAP_SECONDS)
        budgets={'resonator':9766};executed=0;hits=0
        def ledger(self):pass
        def evaluate(self,arm,params,panel,stage,split,tag,tuning):
            self.budgets[arm]+=38;self.executed+=38
            if tag=='initial':return scores('B',-1 if all_ineligible else 0,-2)
            i=int(tag.split(':')[1])
            return scores('B',-1 if all_ineligible or i%2==0 else 0,50 if i%2==0 else 3)
    def optimizer(arm,start):return es
    monkeypatch.setattr(V,'optimizer',optimizer);monkeypatch.setattr(V,'identity',lambda *a:'fake')
    best,sel=V.tune(Bench(),'B','resonator',V.defaults('resonator'))
    assert len(es.feedback)==16 and all(len(row)==16 for row in es.feedback)
    assert all(row[0]>row[1] for row in es.feedback) if not all_ineligible else all(row[0]<row[1] for row in es.feedback)
    assert sel['eligible']==(not all_ineligible) and sel['regular_mean']==(50 if all_ineligible else 3)
    log=json.loads((tmp_path/'B_resonator_tuning.json').read_text())
    assert sum(c['accepted_as_best'] for gen in log['generations'] for c in gen['candidates'])==1
    assert log['selected_omega']=={'melee':0,'ranged':0}


@pytest.mark.parametrize('stop_a,pass_b',[(True,False),(False,False),(False,True)])
def test_stage_orchestration_stops_and_omega_even_on_b_stop(tmp_path,monkeypatch,stop_a,pass_b):
    events=[]
    class Pool:
        def stop(self):pass
    class Bench:
        out=tmp_path;pool=Pool();budgets={};executed=0;hits=0
    def tune(bench,stage,arm,start):events.append(('tune',stage,arm));return start,{'eligible':False if stage=='B' else None}
    def validate(bench,stage,best):
        events.extend(('validate',stage,a) for a in V.ARMS)
        return validation(0 if stop_a else 1,-6 if pass_b else -6.025)
    monkeypatch.setattr(V,'tune',tune);monkeypatch.setattr(V,'validate',validate)
    result=V.run_stages(Bench())
    assert result['stages_completed']==(['A'] if stop_a else ['A','B'])
    assert result['status']==('PROGRESS' if not stop_a and pass_b else 'NOT_READY')
    assert result['C']['status']=='not_run' and result['selected_omega']=={'melee':0,'ranged':0}
    assert sum(e[0]=='validate' for e in events)==(4 if stop_a else 8)
    assert all(e[1] in ('A','B') for e in events)


def test_failure_retains_omega(tmp_path,monkeypatch):
    class Pool:
        stopped=False
        def stop(self):self.stopped=True
    class Bench:
        out=tmp_path;pool=Pool();budgets={};executed=0;hits=0
    monkeypatch.setattr(V,'tune',lambda *a:(_ for _ in ()).throw(TimeoutError('fake cap')))
    bench=Bench()
    with pytest.raises(TimeoutError):V.run_stages(bench)
    row=json.loads((tmp_path/'failure.json').read_text())
    assert bench.pool.stopped and row['status']=='NOT_READY' and row['selected_omega']=={'melee':0,'ranged':0}


def test_validation_reporting_and_no_selection(tmp_path):
    class Bench:
        out=tmp_path
        def ledger(self):pass
        def evaluate(self,arm,params,panel,stage,split,tag):
            self.last_rows=[dict(spec=dict(opponent=b[0],setting=b[2]),summary=dict(survivors=1,enemySurvivors=2,t=150,
                           artilleryAlive=[1,2],crossTeamDealt=[3,4],crossTeamTaken=[4,3])) for b in panel for _ in (0,1)]
            return {json.dumps(b):-1 for b in panel}
    result=V.validate(Bench(),'B',{a:V.defaults(a) for a in V.BOUNDS})
    assert set(result)==set(V.ARMS)
    for arm in V.ARMS:
        for head in ('novice','regular'):
            row=result[arm]['s4_full_head|'+head]
            assert row['stats']['n']==100 and row['stats']['mean']==-1
            assert row['descriptive']['fights']==200 and row['descriptive']['timeouts']==200
            assert row['descriptive']['own_elimination_time_mean'] is None
            assert row['descriptive']['enemy_guns_alive_mean']==2


def test_existing_output_and_wrong_delivery_refused_before_claim(tmp_path,monkeypatch):
    monkeypatch.setattr(sys,'argv',['s4_v6.py','--output',str(tmp_path),'--implementation-commit','unused'])
    with pytest.raises(RuntimeError,match='output already exists'):V.main()
    assert not list(tmp_path.iterdir())
    monkeypatch.setattr(sys,'argv',['s4_v6.py','--output',str(tmp_path/'fresh'),'--implementation-commit','wrong'])
    V.write(tmp_path/'PART1_DELIVERY.json',dict(implementation_commit='correct'))
    monkeypatch.setattr(V,'CHECKS',tmp_path)
    with pytest.raises(RuntimeError,match='commit mismatch'):V.main()
    assert not (tmp_path/'LEDGER_USED.json').exists()


def test_optimizer_dimensions():
    for arm in V.BOUNDS:
        V.optimizer.stage='B';es=V.optimizer(arm,V.defaults(arm));xs=es.ask()
        assert len(xs)==16 and all(len(x)==len(V.BOUNDS[arm]) for x in xs)
        es.tell(xs,list(range(16)))


def test_interrupted_tune_preserves_new_partial_incumbent(tmp_path,monkeypatch):
    es=FakeOptimizer()
    xs=es.ask()
    for x in xs:x[-2]=.75;x[-1]=.25
    es.ask=lambda:xs
    class Bench:
        out=tmp_path;locked={};identity='fake';started=V.time.monotonic()
        deadline=V.Deadline(V.time.monotonic()+V.CAP_SECONDS)
        budgets={'resonator':0};executed=0;hits=0
        pool=type('Pool',(),{'stop':lambda self:None})()
        def ledger(self):pass
        def evaluate(self,arm,params,panel,stage,split,tag,tuning):
            self.budgets[arm]+=38;self.executed+=38
            if tag=='initial':return scores('A',0)
            if tag=='0:0':return scores('A',5)
            raise TimeoutError('fake mid-generation cap')
    def optimizer(arm,start):return es
    monkeypatch.setattr(V,'optimizer',optimizer);monkeypatch.setattr(V,'identity',lambda *a:'fake')
    bench=Bench()
    with pytest.raises(TimeoutError):V.run_stages(bench)
    row=json.loads((tmp_path/'failure.json').read_text())
    assert row['selections']['resonator']['novice_mean']==5
    assert row['selections']['resonator']['complete'] is False
    assert row['selected_omega']==json.loads((tmp_path/'selected_omega.json').read_text())['omega']
    assert row['selected_omega']=={'melee':0,'ranged':-1}
    assert row['allowance_seconds']==21600


def test_failed_run_still_writes_timing_and_consumes_ledger(tmp_path,monkeypatch):
    checks=tmp_path/'checks';checks.mkdir()
    V.write(checks/'PART1_DELIVERY.json',dict(implementation_commit='correct',runtime_hashes={},binary_sha256='fake',build_manifest_sha256='fake'))
    monkeypatch.setattr(V,'CHECKS',checks)
    monkeypatch.setattr(V,'declaration',lambda:{})
    monkeypatch.setattr(V,'verify_sources',lambda:{})
    monkeypatch.setattr(V,'admit',lambda b:{'binary_sha256':'fake','manifest_sha256':'fake'})
    def fail(*args):raise TimeoutError('fake construction failure')
    monkeypatch.setattr(V,'Bench',fail)
    out=tmp_path/'fresh'
    monkeypatch.setattr(sys,'argv',['s4_v6.py','--output',str(out),'--implementation-commit','correct'])
    with pytest.raises(TimeoutError):V.main()
    timing=json.loads((out/'RUN_TIMING.json').read_text())
    assert 0<=timing['elapsed_seconds']<2 and timing['allowance_seconds']==21600
    assert (checks/'LEDGER_USED.json').exists()
    assert not (V.ROOT/'s4_v6_checks/LEDGER_USED.json').exists()


def test_batch_orientation_mean_and_post_batch_identity_guard(tmp_path,monkeypatch):
    calls=[]
    monkeypatch.setattr(V,'identity',lambda *a:'fake')
    def fake_worker(task,deadline):
        assert deadline is bench.deadline
        return [dict(spec=s,summary={},S=2 if s['swapSides'] else 0,cache_hit=False,cache_key='fake',metrics={}) for s in task[2]]
    monkeypatch.setattr(V,'execute',fake_worker)
    bench=V.Bench(tmp_path,V.Deadline(V.time.monotonic()+5),{})
    def pins(locked):calls.append(len(bench.uses))
    monkeypatch.setattr(V,'check_inputs',pins)
    try:
        panel=V.battles('B','tuning')
        measured=bench.evaluate('resonator',V.defaults('resonator'),panel,'B','tuning','fake',True)
        assert set(measured.values())=={1} and calls==[0,38]
        assert V.selection('B',measured)['novice_mean']==1
        assert bench.budgets['resonator']==38 and all(u['skeleton']=='v6' for u in bench.uses)
        def changed(locked):
            if len(bench.uses)>38:raise RuntimeError('fake final-batch input drift')
        monkeypatch.setattr(V,'check_inputs',changed)
        with pytest.raises(RuntimeError,match='final-batch input drift'):
            bench.evaluate('resonator',V.defaults('resonator'),panel,'B','validation','fake')
    finally:bench.close()


def test_native_complex_controller_contract():
    path=V.CHECKS/'V6_CONTROLLER_CONTRACT.json'
    # A completed native PASS is not rerun for an unrelated wrapper assertion.
    if path.exists():
        saved=json.loads(path.read_text());assert saved['returncode']==0,saved
        assert V.sha(V.BINARY)==saved.get('binary_sha256',saved.get('associated_build_manifest'))
        admit(V.BINARY)
        contract=json.loads(saved['stdout'])
    else:
        run=subprocess.run([str(V.BINARY),'--v6-contract'],capture_output=True,text=True,timeout=30)
        V.write(path,dict(returncode=run.returncode,stdout=run.stdout,stderr=run.stderr,fights=0,
                          binary_sha256=V.sha(V.BINARY)))
        assert run.returncode==0,run.stderr;contract=json.loads(run.stdout)
    assert contract['status']=='passed' and contract['fights']==0
    assert contract['unchanged_arm_action_bytes']>0


@pytest.mark.parametrize('novice,regular,failures,status',[
    (1,0,0,'PROGRESS'),(1,.000001,0,'READY_TO_DRAFT_S5'),(1,1,1,'NOT_READY'),
    (0,1,0,'NOT_READY'),(-.01,1,0,'NOT_READY'),(1,-6.025,0,'NOT_READY')])
def test_beats_regular_requires_novice_and_failure_free(novice,regular,failures,status):
    result=V.stage_gate('B',validation(novice,regular),failures)
    assert result['status']==status and result['S5_run_authorized'] is False
    assert result['beats_regular_in_development']==(regular>0 and novice>0 and failures==0)


def test_all_tracked_baseline_files_preserved():
    pin=json.loads((V.ROOT/'S4_V6_PRESERVATION_PIN.json').read_text())
    repo=V.ROOT.parents[2]
    changed=[name for name,expected in pin['tracked_sha256'].items() if V.sha(repo/name)!=expected]
    external=json.loads((V.CHECKS/'EXTERNAL_WORKSPACE_CHANGES.json').read_text())
    assert set(changed)==set(external['changed_files']),changed
    for name,record in external['changed_files'].items():
        assert V.sha(repo/name)==record['current_sha256']
        head_blob=subprocess.check_output(['git','show',external['workspace_head']+':'+name],cwd=repo)
        assert hashlib.sha256(head_blob).hexdigest()==record['current_sha256']
        assert pin['tracked_sha256'][name]==record['initial_sha256']
    V.write(V.CHECKS/'PRESERVATION.json',dict(status='PASS',tracked_files=len(pin['tracked_sha256']),changed=[],
            external_changes=external,v0_v5_sources_and_historical_fixtures_byte_identical=True,plan_not_edited_by_this_task=True))


def test_failure_record_vetoes_positive_gate():
    records=validation(1,1);records['failure_rows']=[dict(controllerStatus='controller_failure',controllerFailures=[1,0])]
    assert V.stage_gate('B',records)['status']=='NOT_READY'
    assert V.stage_gate('B',records)['failure_free'] is False


@pytest.mark.parametrize('fault',['reuse_panel','reuse_prior','duplicate','nonfinite','missing'])
def test_engineering_entropy_admission(tmp_path,monkeypatch,fault):
    data=V.declaration()
    if fault=='reuse_panel':data['engineering_seeds']['A']=data['panels']['A']['tuning'][0][1]
    elif fault=='reuse_prior':data['engineering_seeds']['A']=data['prior_seed_inventory'][0]
    elif fault=='duplicate':data['engineering_seeds']['A']=data['engineering_seeds']['B_novice']
    elif fault=='nonfinite':data['engineering_seeds']['A']=True
    else:del data['engineering_seeds']['A']
    ledger=tmp_path/'ledger.json';V.write(ledger,data);monkeypatch.setattr(V,'LEDGER',ledger)
    with pytest.raises(RuntimeError):V.declaration()


def test_captured_default_engineering_commitment_refinement_last():
    # Deliberately last: -x ensures every no-combat contract/gate above passes first.
    from s4_v6_engineering import run
    result=run()
    assert result['status']=='PASS',result
