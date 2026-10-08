"""Focused A0 tooling tests. Synthetic streams/observations only, zero fights."""
import copy
import gzip
import json
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parent))
import a0_common as common
import a0_metrics as metrics
import a0_run as run
import a0_build as build

def stats(deaths=20,kills=50,t=60,events=100,multi=10):
    return dict(own_deaths=deaths,enemy_kills=kills,enemy_damage=1000,t_end=t,
                time_to_elimination=t if kills==50 else None,elimination_time_censored=kills!=50,
                win=kills==50 and deaths<50,eligible_events=events,multi_gun_events=multi,
                assignments=3,rejected_assignments=0,max_frame_bytes=100)

def record(arm,index=0,panel='regular',**kw):
    return dict(arm=arm,pair_key=f'{panel}_{index}',panel=panel,tactic='regular',stats=stats(**kw))

def stream(tmp_path,kills=50,terminal=True):
    initial=[[i,0 if i<=50 else 1] for i in range(1,101)]
    survivors=initial[:30]+initial[50:100-kills]
    rows=[dict(observerV1=True,step=0,t=0,units=initial),dict(observerV1=True,step=1,t=60,units=survivors,
          shapeV6=[dict(a0Event=True,eligible=2,joint=True,applied=2,rejected=0),
                   dict(a0Label=True,role='ranged',rawToExecuted=25,activeFire=False,readyLabel=False)],damage=[])]
    if terminal:rows.append(dict(survivors=30,enemySurvivors=50-kills,t=60,controllerStatus='completed'))
    path=tmp_path/'stream.gz'
    with gzip.open(path,'wt') as f:
        for row in rows:f.write(json.dumps(row)+'\n')
    return path

def test_measure_real_denominators_and_executed_label(tmp_path):
    result=metrics.measure(stream(tmp_path))
    assert result['own_deaths']==20 and result['enemy_kills']==50
    assert result['kills_per_own_death']==2.5
    assert result['multi_gun_event_share']==1 and result['raw_to_executed_mean_px']==25
    assert result['active_fire_label_rate']==0

def test_censoring_is_not_silent_eliminated_only(tmp_path):
    result=metrics.measure(stream(tmp_path,kills=20))
    assert result['time_to_elimination'] is None and result['elimination_time_censored']
    summary=metrics.summary([dict(stats=result)])
    assert summary['restricted_elimination_time_150']==150
    assert summary['time_to_elimination_mean_eliminated_only'] is None
    assert summary['kills_per_minute']==20

def test_partial_stream_rejected(tmp_path):
    with pytest.raises(RuntimeError,match='incomplete'):metrics.measure(stream(tmp_path,terminal=False))

def test_exchange_is_ratio_of_totals_and_zero_flag():
    rows=[record('O',deaths=1,kills=20),record('O',1,deaths=9,kills=50)]
    assert metrics.summary(rows)['kills_per_own_death']==7
    zero=metrics.summary([record('O',deaths=0)])
    assert zero['kills_per_own_death'] is None and zero['zero_death_denominator']

def test_pairing_and_duplicates():
    result=metrics.contrast([record('O'),record('O+G',deaths=17),record('O',1)],'O','O+G')
    assert result['n']==1 and result['unmatched_pairs']==1 and result['deaths_saved']==3
    with pytest.raises(RuntimeError,match='duplicate'):metrics.contrast([record('O'),record('O')],'O','O+G')

def test_full_army_leader_parks_and_units_proceed():
    rows=[record(a,i,panel=p) for p in ('regular','C3') for i in range(100) for a in common.ARMS]
    result=metrics.report(rows,100)
    assert result['leader_decision']=='PARK_REPORT_TO_OWNER_UNITS_ALONE_PROCEEDS'
    assert result['series_streak']['status']=='not_run'

def test_useful_exchange_or_survival_and_per_tactic():
    rows=[record(a,i,panel=p,deaths=17 if a=='O+G' else 20) for p in ('regular','C3') for i in range(100) for a in common.ARMS]
    result=metrics.report(rows,100)
    assert result['leader_decision']=='SCRIPT_CEILING_PASSED_FUTURE_LEADER_DESIGN_ONLY'
    assert len(result['panels']['C3']['per_tactic'])==20
    assert result['panels']['C3']['comparisons']['O+G minus O']['planned_death_mde_80pct']['100']==0

def test_floor_and_harm_stop_at_50():
    rows=[record(a,i,panel=p,multi=0) for p in ('regular','C3') for i in range(50) for a in common.ARMS]
    assert metrics.report(rows,50)['leader_decision'].startswith('PARK')
    rows=[record(a,i,panel=p,deaths=23 if a=='O+G' else 20) for p in ('regular','C3') for i in range(50) for a in common.ARMS]
    assert metrics.report(rows,50)['leader_decision'].startswith('PARK')

def test_fresh_paired_entropy_balanced_c3(tmp_path,monkeypatch):
    monkeypatch.setattr(run,'LEDGER',tmp_path/'ledger.json');monkeypatch.setattr(run,'REQUESTS',tmp_path/'requests')
    monkeypatch.setattr(run,'HERE',tmp_path);monkeypatch.setattr(run,'LOCAL',tmp_path)
    monkeypatch.setattr(run,'request',lambda arm,tactic,seed,orientation:dict(arm=arm,tactic=tactic,seed=seed,orientation=orientation))
    monkeypatch.setattr(run,'load',lambda *args:SimpleNamespace(admit=lambda path:{'fake':'test only'}))
    ledger=run.prepare();jobs=ledger['jobs']
    assert sum(j['stage']=='pilot' for j in jobs)==18
    for panel in ('regular','C3'):
        ours=[j for j in jobs if j['stage']=='outcome' and j['panel']==panel and j['arm']=='O']
        assert len(ours)==100
        if panel=='C3':
            assert all(sum(j['tactic']==c for j in ours)==5 for c in common.CELLS)
            assert all(sum(j['tactic']==c for j in ours[:50]) in (2,3) for c in common.CELLS)
    pairs={}
    for j in jobs:pairs.setdefault(j['pair_key'],[]).append(j)
    assert len({p[0]['seed'] for p in pairs.values()})==len(pairs)
    assert all(len({(j['seed'],j['tactic'],j['orientation']) for j in p})==1 for p in pairs.values())

def test_projection_18_fights_and_reuse(tmp_path,monkeypatch):
    monkeypatch.setattr(run,'RAW',tmp_path)
    pilot=[dict(arm=a,seconds=10+i,stats=stats(t=75)) for a in common.ARMS for i in range(6)]
    jobs=[dict(arm=a,tag=a) for a in common.ARMS]
    (tmp_path/'O_COMPLETE.json').write_text('{}')
    result=run.projection(jobs,pilot)
    assert result['remaining_fights']==2 and result['projected_seconds']==72
    with pytest.raises(RuntimeError):run.projection(jobs,pilot[:17])

def test_cap_reads_owner_setting_without_pinning(tmp_path,monkeypatch):
    path=tmp_path/'cap.json';monkeypatch.setattr(common,'CAP_PATH',path)
    common.write(path,dict(cap_seconds=10800,approved_by='owner',date='2026-10-08'))
    assert common.owner_cap()['cap_seconds']==10800
    common.write(path,dict(cap_seconds=True,approved_by='owner',date='today'))
    with pytest.raises(RuntimeError):common.owner_cap()
    assert all(not p.endswith('.md') for p in common.code_hashes())

def test_gate_prevents_every_fight(tmp_path,monkeypatch):
    ledger=tmp_path/'ledger.json';ledger.write_text('{}');monkeypatch.setattr(run,'LEDGER',ledger);monkeypatch.setattr(run,'HERE',tmp_path)
    monkeypatch.setattr(run,'identity',lambda:{'jobs':[]});monkeypatch.setattr(run,'owner_cap',lambda:{'cap_seconds':10})
    def deny(deadline):raise RuntimeError('process gate UNAVAILABLE')
    monkeypatch.setattr(run,'process_gate',deny)
    monkeypatch.setattr(run,'execute',lambda *args:pytest.fail('fight after refused process gate'))
    with pytest.raises(RuntimeError,match='UNAVAILABLE'):run.run('pilot',50)

def test_resume_checks_job_raw_and_stats(tmp_path,monkeypatch):
    monkeypatch.setattr(run,'RAW',tmp_path);ledger=tmp_path/'ledger';ledger.write_text('ledger');monkeypatch.setattr(run,'LEDGER',ledger)
    job=dict(tag='p',arm='O');path=stream(tmp_path);raw=tmp_path/'p.jsonl.gz';path.rename(raw)
    receipt=dict(job=job,ledger_sha256=common.sha(ledger),raw_sha256=common.sha(raw),stats=metrics.measure(raw),seconds=1)
    common.write(tmp_path/'p_COMPLETE.json',receipt)
    assert run.completed(job)['seconds']==1
    receipt['stats']['own_deaths']=0;common.write(tmp_path/'p_COMPLETE.json',receipt)
    with pytest.raises(RuntimeError,match='statistics drift'):run.completed(job)

def test_native_synthetic_fixture():
    record=common.read(common.BINARY.with_suffix('.build.json'))
    admission=common.load('a0_test_admission',common.CPP/'build_admission.py');admission.admit(common.BINARY)
    commands=record['commands'];flags=commands[0][:commands[0].index('-c')]
    out=common.BINARY.parent
    subprocess.run([*flags,'-c',str(common.HERE/'a0_fixture.cpp'),'-o',str(out/'a0_fixture.o')],check=True,timeout=60)
    objects=[p for p in record['link'][1:record['link'].index('-o')] if not p.endswith('/lean_host.o')]
    subprocess.run([record['link'][0],*objects,str(out/'a0_fixture.o'),'-o',str(out/'a0_fixture')],check=True,timeout=60)
    result=subprocess.run([str(out/'a0_fixture')],check=True,capture_output=True,text=True,timeout=30)
    assert 'A0_FIXTURE_PASS no fights' in result.stdout


def test_decomposition_readiness_is_separate():
    rows=[record(a,i,panel=p,deaths=30 if a=='O' else 27 if a=='O+G' else 20)
          for p in ('regular','C3') for i in range(100) for a in common.ARMS]
    result=metrics.report(rows,100)
    assert result['unit_decision']=='REVISE_O_BEFORE_TRAINING'
    assert result['training_readiness']=='BLOCKED_UNIT_DECOMPOSITION'

def test_live_ram_fails_before_child(monkeypatch,tmp_path):
    monkeypatch.setattr(run,'completed',lambda job:None);monkeypatch.setattr(run,'RAW',tmp_path)
    def deny(pid):raise RuntimeError('live RAM unavailable')
    monkeypatch.setattr(run,'live_memory',deny)
    monkeypatch.setattr(run.subprocess,'Popen',lambda *a,**k:pytest.fail('child started before RAM gate'))
    with pytest.raises(RuntimeError,match='live RAM'):run.execute(dict(tag='fake'),float('inf'))

def test_prepare_interruption_preserves_entropy(tmp_path,monkeypatch):
    monkeypatch.setattr(run,'LEDGER',tmp_path/'ledger.json');monkeypatch.setattr(run,'REQUESTS',tmp_path/'requests')
    monkeypatch.setattr(run,'HERE',tmp_path);monkeypatch.setattr(run,'LOCAL',tmp_path)
    monkeypatch.setattr(run,'load',lambda *args:SimpleNamespace(admit=lambda path:{'fake':'test only'}))
    calls=[]
    def interrupted(arm,tactic,seed,orientation):
        calls.append(seed)
        if len(calls)==4:raise RuntimeError('synthetic interruption')
        return dict(arm=arm,tactic=tactic,seed=seed,orientation=orientation)
    monkeypatch.setattr(run,'request',interrupted)
    with pytest.raises(RuntimeError,match='interruption'):run.prepare()
    transaction=common.read(tmp_path/'PREPARATION.json')
    monkeypatch.setattr(run,'request',lambda arm,tactic,seed,orientation:dict(arm=arm,tactic=tactic,seed=seed,orientation=orientation))
    result=run.prepare()
    assert result['jobs'][0]['seed']==transaction['pairs'][0]['seed']==calls[0]
    assert len(result['jobs'])==618


def test_wire_compacts_without_resealing(tmp_path):
    path=tmp_path/'sealed.json'
    common.write(path,{'options':{'duration':3},'note':'line\nbreak'})
    before=path.read_bytes();digest=common.sha(path)
    wire=run.wire_request(path,digest)
    assert wire.count(b'\n')==1 and wire.endswith(b'\n')
    assert json.loads(wire)==json.loads(before) and path.read_bytes()==before
    assert '--metrics' not in run.host_command()
    with pytest.raises(RuntimeError,match='sealed request drift'):
        run.wire_request(path,'wrong')


def repair_fixture(tmp_path,monkeypatch):
    import hashlib
    monkeypatch.setattr(run,'HERE',tmp_path)
    monkeypatch.setattr(run,'LOCAL',tmp_path)
    monkeypatch.setattr(run,'RAW',tmp_path/'raw')
    monkeypatch.setattr(run,'REQUESTS',tmp_path/'requests')
    monkeypatch.setattr(run,'LEDGER',tmp_path/'ledger.json')
    monkeypatch.setattr(run,'RECOVERY',tmp_path/'recovery.json')
    request=run.REQUESTS/'pilot_O.json';common.write(request,{'fixture':True})
    job=dict(tag='pilot_O',arm='O',stage='pilot',request_sha256=common.sha(request))
    key='s4_army_slice_v1/a0_run.py'
    original=subprocess.check_output(['git','show',
        'efcf591:evidence/tactical_composition_demo/astelia_cpp/s4_army_slice_v1/a0_run.py'],cwd=common.CPP)
    current=common.code_hashes()
    old={**current,key:hashlib.sha256(original).hexdigest()}
    binary=dict(binary_sha256='same engine',engine='army_a0_script',scope='native_complete_engine',
                sanitized=False,portable=False,manifest_sha256='new',sources=current)
    common.write(run.LEDGER,dict(code_hashes=old,binary={**binary,'manifest_sha256':'old','sources':old},jobs=[job]))
    common.write(tmp_path/'A0_DECLARATION.json',dict(ledger_sha256=common.sha(run.LEDGER)))
    monkeypatch.setattr(run,'code_hashes',lambda:current)
    monkeypatch.setattr(run,'load',lambda *args:SimpleNamespace(admit=lambda path:binary))
    run.RAW.mkdir()
    payload=b'{"error":"invalid JSON"}\n{"error":"invalid JSON number"}\n{"error":"trailing JSON input"}\n'
    (run.RAW/'pilot_O_old.stdout').write_bytes(payload)
    (run.RAW/'pilot_O_old.stderr').write_bytes(b'')
    with gzip.open(run.RAW/'pilot_O.jsonl.gz','wb') as f:f.write(payload)
    common.write(run.RAW/'pilot_O_old_ATTEMPT.json',dict(job=job,returncode=0))
    return job,current,binary


def test_explicit_tooling_repair_keeps_all_seals_and_failed_evidence(tmp_path,monkeypatch):
    job,current,binary=repair_fixture(tmp_path,monkeypatch)
    paths=[run.LEDGER,tmp_path/'A0_DECLARATION.json',*run.RAW.iterdir(),*run.REQUESTS.iterdir()]
    before={p:p.read_bytes() for p in paths}
    recovery=run.repair_tooling()
    assert recovery['retry_allowed'] and recovery['cause']
    assert run.identity()['jobs']==[job]
    assert run.repair_tooling()==recovery
    assert all(p.read_bytes()==b for p,b in before.items())
    (run.RAW/'pilot_O_old.stdout').write_bytes(b'changed')
    with pytest.raises(RuntimeError,match='failed evidence drift'):run.identity()


@pytest.mark.parametrize('defect',('valid_row','binary_change','completed','other_code'))
def test_repair_refuses_valid_data_or_non_tooling_drift(defect,tmp_path,monkeypatch):
    job,current,binary=repair_fixture(tmp_path,monkeypatch)
    if defect=='valid_row':
        payload=b'{"observerV1":true}\n'
        (run.RAW/'pilot_O_old.stdout').write_bytes(payload)
        with gzip.open(run.RAW/'pilot_O.jsonl.gz','wb') as f:f.write(payload)
    elif defect=='binary_change':binary['binary_sha256']='different'
    elif defect=='completed':common.write(run.RAW/'pilot_O_COMPLETE.json',{})
    else:current['other.py']='changed'
    with pytest.raises(RuntimeError):run.repair_tooling()
    assert not run.RECOVERY.exists()


def test_execute_retry_has_new_raw_id_and_logs_cause(tmp_path,monkeypatch,capsys):
    import time
    job,_,_=repair_fixture(tmp_path,monkeypatch)
    recovery=run.repair_tooling()
    preserved={p:p.read_bytes() for p in run.RAW.iterdir()}
    stream(tmp_path)
    with gzip.open(tmp_path/'stream.gz','rt') as f:rows=f.read()
    script='import sys; import json; json.loads(sys.stdin.read()); sys.stdout.write('+repr(rows)+')'
    monkeypatch.setattr(run,'host_command',lambda:[sys.executable,'-c',script])
    monkeypatch.setattr(run,'live_memory',lambda pid:0)
    result=run.execute(job,time.monotonic()+10)
    assert result['stats']['enemy_kills']==50
    receipt=common.read(run.RAW/'pilot_O_COMPLETE.json')
    assert receipt['raw_file']!='pilot_O.jsonl.gz'
    attempt=common.read(run.RAW/('pilot_O_'+receipt['attempt_id']+'_ATTEMPT.json'))
    assert attempt['retry_of']=={'pilot_O_old_ATTEMPT.json':common.sha(run.RAW/'pilot_O_old_ATTEMPT.json')}
    assert attempt['retry_causes']=={'pilot_O_old_ATTEMPT.json':recovery['cause']}
    assert attempt['status']=='DONE' and recovery['cause'] in capsys.readouterr().out
    assert all(p.read_bytes()==b for p,b in preserved.items())
    assert run.execute(job,time.monotonic()+10)==result


def test_failed_new_attempt_is_preserved_and_requires_diagnosis(tmp_path,monkeypatch):
    import time
    job,_,_=repair_fixture(tmp_path,monkeypatch)
    run.repair_tooling()
    monkeypatch.setattr(run,'host_command',lambda:[sys.executable,'-c',
        'import sys; sys.stdin.read(); print(\'{"error":"unknown failure"}\')'])
    monkeypatch.setattr(run,'live_memory',lambda pid:0)
    with pytest.raises(RuntimeError,match='unknown failure'):run.execute(job,time.monotonic()+10)
    attempts=[p for p in run.RAW.glob('*_ATTEMPT.json') if 'old' not in p.name]
    assert len(attempts)==1 and common.read(attempts[0])['status']=='FAILED'
    before={p:p.read_bytes() for p in run.RAW.iterdir()}
    with pytest.raises(RuntimeError,match='unresolved prior attempt'):run.execute(job,time.monotonic()+10)
    assert all(p.read_bytes()==b for p,b in before.items())


def test_wall_cap_retry_records_its_own_cause(tmp_path,monkeypatch,capsys):
    import time
    job,_,_=repair_fixture(tmp_path,monkeypatch)
    recovery=run.repair_tooling()
    common.write(run.RAW/'pilot_O_cap_ATTEMPT.json',dict(status='INTERRUPTED',
        error='TimeoutError: owner wall cap reached'))
    stream(tmp_path)
    with gzip.open(tmp_path/'stream.gz','rt') as f:rows=f.read()
    monkeypatch.setattr(run,'host_command',lambda:[sys.executable,'-c',
        'import sys; sys.stdin.read(); sys.stdout.write('+repr(rows)+')'])
    monkeypatch.setattr(run,'live_memory',lambda pid:0)
    run.execute(job,time.monotonic()+10)
    receipt=common.read(run.RAW/'pilot_O_COMPLETE.json')
    attempt=common.read(run.RAW/('pilot_O_'+receipt['attempt_id']+'_ATTEMPT.json'))
    assert attempt['retry_causes']=={
        'pilot_O_old_ATTEMPT.json':recovery['cause'],
        'pilot_O_cap_ATTEMPT.json':'TimeoutError: owner wall cap reached'}
