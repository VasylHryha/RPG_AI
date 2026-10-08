"""Focused contract tests: scenario admission, survival/series logic and metric denominators.
No panel or judging execution. Native requests here have duration 0 only.
"""
import copy
import gzip
import json
import pathlib
import sys
import pytest
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parent))
import lab
from metrics import measure
from replays import one


def test_placement_keeps_role_and_kind_and_heals():
    survivors=[dict(cohort_id=44,role='artillery',kind='shaman',hp=1),dict(cohort_id=11,role='ranged',kind='spitter',hp=3)]
    placed=lab.placement(9382,survivors,orientation=1)
    assert [u['role'] for u in placed]==['ranged','artillery']
    assert all(u['hp_fraction']==1 for u in placed)
    assert placed==lab.placement(9382,list(reversed(survivors)),orientation=1)


def test_drill_allocations():
    pool=lab.catalog()['POOL']
    expected={'D1':(10,30),'D2':(30,10),'D3':(30,15),'D4':(10,10),'D5':(30,30),'C1':(50,50),'C2':(50,50),'C3':(50,50)}
    for drill,counts in expected.items():
        req=lab.drill_request(drill,'v7','regular',18231,0,pool)
        assert tuple(map(len,req['labScenario']['sides']))==counts
        reversed_req=lab.drill_request(drill,'v7','regular',18231,1,pool)
        for side,other in zip(req['labScenario']['sides'],reversed_req['labScenario']['sides']):
            assert all(abs(a['position']['x']+b['position']['x']-1400)<1e-9 for a,b in zip(side,other))
    assert lab.drill_request('D1','v7',None,18231,0,pool)['options']['ai'][1]['params']=={'ranged':0}


def test_doctrines_keep_regular_skills_not_elite():
    for name in lab.catalog()['POOL']:
        p=lab.doctrine(name,lab.catalog()['POOL'])
        assert p['level']=='regular'
        assert 'lookahead' not in p and 'skills' not in p
        req=lab.request('elite',p,9832,abilities_off=True)
        assert req['labAbilities']=='off'
        assert all(ai['skills']['abilities']=='off' for ai in req['options']['ai'])
        assert req['options']['ai'][0]['level']=='elite'


def native(req):
    p=lab.subprocess.run([str(lab.BINARY),'--metrics'],input=json.dumps(req)+'\n',text=True,capture_output=True,check=True)
    rows=[json.loads(line) for line in p.stdout.splitlines()]
    return rows,json.loads(p.stderr)

@pytest.mark.parametrize('mutation',[lambda q:q['labScenario']['sides'][0][0].update(hp_fraction=0),lambda q:q['labScenario']['sides'][0][0].update(hp_fraction=1.01),lambda q:q['labScenario']['sides'][0][0].update(kind='spitter'),lambda q:q['labScenario']['sides'][0][0]['position'].update(x=-1),lambda q:q.update(labAbilities='on')])
def test_native_rejects_invalid_scenario(mutation):
    q=lab.request('v7',lab.controller('dummy_static'),88234)
    q['options']['duration']=0
    mutation(q)
    rows,m=native(q)
    assert 'error' in rows[-1]
    assert m['executed_steps']==0


def test_native_custom_kind_uses_catalog_stats():
    sides=lab.standard(82723)
    sides[0]=[sides[0][0]]
    sides[0][0]['kind']='hound'
    sides[0][0]['hp_fraction']=.5
    q=lab.request('v7',lab.controller('dummy_static'),82723,sides=sides)
    q['options']['duration']=0
    rows,m=native(q)
    u=next(u for u in rows[0]['units'] if u[1]==0)
    assert u[5]==53 and u[6]==6 and u[7]==38
    assert rows[-1]['survivors']==1 and m['executed_steps']==0


def unit(uid,team,role,x,hp=100,reach=300):
    return [uid,team,role,x,400,hp,10,reach,0,False,x,400,0,None]

def test_stream_metrics_use_all_landed_shells_and_real_initial_count(tmp_path):
    path=tmp_path/'fixture.jsonl.gz'
    initial=[unit(41,0,2,500),unit(91,1,2,700)]
    launch=lambda source,team,at:[source,41 if team else 91,team,500,400,0,at,40,False,False]
    damage=dict(source=91,sourceTeam=1,sourceRole='artillery',target=41,targetTeam=0,targetRole='artillery',dealt=20,t=.2,died=False)
    rows=[dict(observerV1=True,step=0,t=0,units=initial,launches=[],damage=[]),
          dict(observerV1=True,step=1,t=.1,units=initial,launches=[launch(91,1,.2),launch(91,1,.4)],damage=[]),
          dict(observerV1=True,step=2,t=.2,units=initial,launches=[],damage=[damage]),
          dict(observerV1=True,step=3,t=.4,units=initial,launches=[],damage=[]),
          dict(survivors=1,enemySurvivors=1,t=.4)]
    with gzip.open(path,'wt') as f:
        for r in rows:f.write(json.dumps(r)+'\n')
    s,alive=measure(path)
    assert s['own_lost']==0 and s['enemy_killed']==0
    assert s['own_units_hit_per_enemy_shell']==.5
    assert s['damage_taken_per_enemy_shell']==10
    assert s['firepower_retained']==1
    assert s['units_out_of_fight']==0
    assert alive[0]['id']==41


def test_series_stops_on_timeout_and_preserves_cohort(monkeypatch,tmp_path):
    pool=lab.catalog()['POOL'];draws=[[dict(seed=100+i,tactic=pool[i]) for i in range(10)]]
    ledger=dict(draws=draws)
    monkeypatch.setattr(lab,'identity',lambda:dict(pool=pool))
    monkeypatch.setattr(lab,'RAW',tmp_path)
    real_read=lab.read
    monkeypatch.setattr(lab,'read',lambda p:ledger if str(p).endswith('SEED_LEDGER.json') else real_read(p))
    seen=[]
    def fake(tag,req,meta,timeout,deadline):
        seen.append((req,meta))
        assert req['labAbilities']=='off'
        assert len(req['labScenario']['sides'][1])==50
        survivors=[dict(id=41,role='artillery',kind='shaman',hp=1)]
        return dict(tag=tag,stats=dict(win=len(seen)==1),survivors=survivors)
    monkeypatch.setattr(lab,'execute',fake)
    r=lab.run_series('v7',0,lab.time.monotonic()+100)
    assert r['streak']==1 and r['fight_reached']==2
    assert r['fights'][1]['units_before']==1 and r['fights'][1]['cohort_before']==[41]
    assert len(seen[1][0]['labScenario']['sides'][0])==1
    assert seen[1][0]['labScenario']['sides'][0][0]['hp_fraction']==1


def test_no_elimination_win_at_timeout(tmp_path):
    p=tmp_path/'late.jsonl.gz'
    rows=[dict(observerV1=True,step=0,t=0,units=[unit(1,0,0,500),unit(51,1,0,520)],launches=[],damage=[]),
          dict(observerV1=True,step=1,t=150,units=[unit(1,0,0,500)],launches=[],damage=[]),dict(survivors=1,enemySurvivors=0,t=150)]
    with gzip.open(p,'wt') as f:
        for r in rows:f.write(json.dumps(r)+'\n')
    stats,_=measure(p)
    assert not stats['win'] and stats['timeout'] and stats['t_elimination'] is None


def test_expired_deadline_never_claims_or_starts_child(monkeypatch,tmp_path):
    monkeypatch.setattr(lab,'RAW',tmp_path)
    monkeypatch.setattr(lab,'identity',lambda:pytest.fail('admission after expiry'))
    with pytest.raises(TimeoutError):lab.execute('expired',{}, {},deadline=lab.time.monotonic()-1)
    assert not list(tmp_path.iterdir())


def test_failed_check_report_survives_missing_timing(monkeypatch,tmp_path):
    import report
    monkeypatch.setattr(report,'HERE',tmp_path)
    monkeypatch.setattr(report,'RAW',tmp_path/'raw')
    monkeypatch.setattr(report,'catalog',lambda:dict(POOL=['line']))
    lab.write(tmp_path/'BUILD.json',dict(status='PASS'))
    lab.write(tmp_path/'CHECKS.json',dict(status='FAIL',checks=[dict(name='early check',pass_check=False)]))
    report.render()
    text=(tmp_path/'SHAPE_LAB_REPORT.md').read_text()
    assert text.startswith('PARTIAL\n') and 'FAIL' in text and 'not evaluated' in text


def test_cached_receipt_tampering_is_rejected(monkeypatch,tmp_path):
    monkeypatch.setattr(lab,'RAW',tmp_path)
    monkeypatch.setattr(lab,'HERE',tmp_path)
    monkeypatch.setattr(lab,'identity',lambda:{})
    declaration=tmp_path/'DECLARATION.json';lab.write(declaration,{})
    req={};meta={};tag='receipt'
    lab.write(tmp_path/(tag+'_request.json'),req)
    claim=dict(meta=meta,request_sha256=lab.sha(tmp_path/(tag+'_request.json')),declaration_sha256=lab.sha(declaration))
    lab.write(tmp_path/(tag+'_CLAIM.json'),claim)
    terminal=dict(survivors=1,enemySurvivors=1,t=0,controllerFailures=[0,0])
    raw=tmp_path/(tag+'.jsonl.gz')
    with gzip.open(raw,'wt') as f:
        f.write(json.dumps(dict(observerV1=True,step=0,t=0,units=[unit(1,0,0,500),unit(51,1,0,520)],launches=[],damage=[]))+'\n')
        f.write(json.dumps(terminal)+'\n')
    native=dict(executed_fights=1)
    lab.write(tmp_path/(tag+'_stderr.log'),native)
    stats,survivors=measure(raw)
    r=dict(meta=meta,summary=terminal,native_metrics=native,stats=stats,survivors=survivors,
           declaration_sha256=lab.sha(declaration),claim_sha256=lab.sha(tmp_path/(tag+'_CLAIM.json')),
           request_sha256=lab.sha(tmp_path/(tag+'_request.json')),raw_sha256=lab.sha(raw),stderr_sha256=lab.sha(tmp_path/(tag+'_stderr.log')))
    lab.write(tmp_path/(tag+'_COMPLETE.json'),r)
    assert lab.verified_record(tag,req,meta)==r
    claim['declaration_sha256']='wrong';lab.write(tmp_path/(tag+'_CLAIM.json'),claim)
    with pytest.raises(RuntimeError,match='declaration/claim'):lab.verified_record(tag,req,meta)


def test_replay_group_size_fallback_retains_all_fights(monkeypatch,tmp_path):
    import replays
    def fake(r,fps):return dict(name=r['tag'],frames=['x'*(1_000_000 if fps>1 else 100)])
    monkeypatch.setattr(replays,'one',fake)
    records=[dict(tag=str(i)) for i in range(10)]
    p=tmp_path/'compact.json';receipt=replays.extract(records,p,'C3')
    assert p.stat().st_size<=8_000_000 and receipt['fps']==1
    assert len(json.loads(p.read_text())['fights'])==10


def test_slow_fields_excluded_from_shell_denominator(tmp_path):
    p=tmp_path/'slow.jsonl.gz'
    rows=[dict(observerV1=True,step=0,t=0,units=[unit(1,0,0,500),unit(91,1,2,700)],launches=[],damage=[]),
          dict(observerV1=True,step=1,t=.2,units=[unit(1,0,0,500),unit(91,1,2,700)],launches=[[91,1,1,500,400,0,.1,45,False,True]],damage=[]),dict(survivors=1,enemySurvivors=1,t=.2)]
    with gzip.open(p,'wt') as f:
        for r in rows:f.write(json.dumps(r)+'\n')
    s,_=measure(p)
    assert s['slow_field_launches']==1 and s['enemy_shells_landed']==0
    assert s['own_units_hit_per_enemy_shell'] is None
