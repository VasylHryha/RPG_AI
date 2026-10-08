"""Focused native fixture/replay tests. Never invoke --collect or coreStep."""
import copy
import json
import math
from pathlib import Path
import subprocess
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
import pytest
from collection import HERE, read, sha
from fixtures import snapshot, threat
import s1fix_build as build
import s1fix_pilot as pilot
from s1fix_metrics import measure


def native(requests):
    result=subprocess.run([str(build.BINARY),'--fixture'],input=''.join(json.dumps(r)+'\n' for r in requests),capture_output=True,text=True,check=True,timeout=60)
    return [json.loads(line) for line in result.stdout.splitlines()]


def frame(views,tick=1,casts=None,project=False):
    return dict(tick=tick,views=views,casts=casts or {},native_projection=project)


def actions(row):return {a['id']:a['action'] for a in row['actions']}


def pending(action,tick,locked=False):
    return dict(target=action['target'],aim=action['aim'],started=tick,originDecision=tick,originVolley=action['volley'],aimLocked=locked)


def test_native_same_state_planner_points_match_before_refresh():
    states=read(HERE/'fixtures/S1FIX_REPLAY.json')['states'];requests=[]
    for s in states:requests.append(dict(wrapper=True,frames=[frame(s['views'],s['tick'],s['casts'])]))
    results=native(requests);points=0;plans=0
    for rows in results:
        row=rows[0];aa=actions(row);commands={c['id']:c for c in row['commands']}
        for e in row['events']:
            if e['stage']=='s1_candidate':
                v=e['value'];assert v['requested']==v['planner_point']
                if e['unit'] in commands and commands[e['unit']]['plan']==row['tick']:
                    assert commands[e['unit']]['absolute']==pytest.approx(v['planner_point'],abs=1e-9)
                    assert aa[e['unit']]['aim']==pytest.approx(v['planner_point'],abs=1e-9)
                    points+=1
            if e['stage']=='s1_joint' and e['value']['feasible']>=2:plans+=1
    assert plans>=5 and points>=15


def test_native_first_physical_refresh_reaction_then_lock_dead_and_expiry():
    s=copy.deepcopy(read(HERE/'fixtures/S1FIX_REPLAY.json')['states'][0]);start=s['tick'];views=s['views']
    # First state starts a real copied-planner group in public scratch geometry.
    initial=native([dict(wrapper=True,frames=[frame(views,start)])])[0][0]
    cmd=initial['commands'];assert len(cmd)>=2
    aa=actions(initial);cast={str(c['id']):pending(aa[c['id']],start) for c in cmd}
    release=copy.deepcopy(views);rt=start+20
    for v in release:
        v.update(t=v['t']+20*v['dt'],tick=rt)
        for u in v['units']:
            if str(u['id']) in cast:u.update(prep=u['windup']-v['dt'],target=cast[str(u['id'])]['target'])
    # A blast covering one commanded gun exercises reaction-declined refresh.
    id=cmd[0]['id'];me=next(u for u in release[0]['units'] if u['id']==id)
    blast=threat('shell');blast.update(x=me['x'],y=me['y'],at=release[0]['t']+1.1,radius=40)
    for v in release:v['threats']=[blast]
    later=copy.deepcopy(release)
    for v in later:
        v.update(t=v['t']+v['dt'],tick=rt+1)
        for u in v['units']:
            if u['team']==1:u['y']+=3
    requests=dict(wrapper=True,frames=[frame(views,start),frame(release,rt,cast,True),frame(later,rt+1,cast)])
    rows=native([requests])[0]
    refresh=[e for e in rows[1]['events'] if e['stage']=='s1_refresh'];assert len(refresh)==len(cmd)
    assert not any(e['stage']=='s1_refresh' for e in rows[2]['events'])
    c1={c['id']:c for c in rows[1]['commands']};c2={c['id']:c for c in rows[2]['commands']}
    for c in cmd:
        assert c1[c['id']]['shape']==c['shape'] and c1[c['id']]['focus']==c['focus']
        assert c1[c['id']]['absolute']==c2[c['id']]['absolute']
        assert c1[c['id']]['refreshed']
    assert not actions(rows[1])[id]['release']
    projections=rows[1]['native_projection'];projected=next(e['value'] for e in projections if e['unit']==id)
    assert not projected['release'] and projected['reason']=='body'
    # A locked dead reference must remain in raw/effective identity, without
    # producing a legal release or recomposing the locked aim.
    locked=copy.deepcopy(cast)
    for c in cmd:locked[str(c['id'])]['aim']=c1[c['id']]['absolute'];locked[str(c['id'])]['aimLocked']=True
    dead=copy.deepcopy(later);focus=cmd[0]['focus']
    for v in dead:
        v['units']=[u for u in v['units'] if u['id']!=focus]
        for u in v['units']:
            if u['id']==id:u['target']=0
        v.update(t=v['t']+v['dt'],tick=rt+2)
    row=native([dict(wrapper=True,frames=[frame(dead,rt+2,locked,True)])])[0][0]
    assert actions(row)[id]['target']==focus and actions(row)[id]['aim']==locked[str(id)]['aim']
    for e in row['native_projection']:
        assert e['value']['raw']['target']==e['value']['effective']['target']
        assert e['value']['raw']['aim']==e['value']['effective']['aim']
    expired=copy.deepcopy(later)
    for v in expired:v.update(t=views[0]['t']+3.1,tick=start+94)
    rows=native([dict(wrapper=True,frames=[frame(views,start),frame(expired,start+94,cast)])])[0]
    assert any(e['stage']=='s1_rejection' and e['value']['reason']=='expired' for e in rows[-1]['events'])
    assert not rows[-1]['commands']


def test_native_safety_guards_range_energy_and_empty_no_wait():
    cases=[]
    for kind in ('empty','body','energy','target_range','cooldown'):
        s=snapshot(1);s['threats']=[];me=s['units'][0]
        if kind=='body':me['guard_until']=10
        if kind=='energy':me['energy']=0
        if kind=='target_range':
            for u in s['units']:
                if u['team']==1:u['x']=1000
        if kind=='cooldown':me['cooldown']=1
        cases.append(dict(wrapper=True,frames=[frame([s],project=True)]))
    rows=[x[0] for x in native(cases)]
    assert actions(rows[0])[1]['start'] and not rows[0]['commands']
    assert all(not actions(r)[1]['start'] for r in rows[1:])
    assert all(not r['native_projection'][0]['value']['start'] for r in rows[1:])


def test_native_all_initial_retained_release_rows_support():
    # Stored-state support replay, not trajectory replay: every old support row
    # is independently evaluated through the new deployed native oracle.
    root=HERE/'_local/s0s1/pilot';inv=read(root/'INVENTORY.json');reqs=[];cells=[]
    for row in inv['rows']:
        if row['pair']>=10 or row['pilot_cell'] not in pilot.CELLS:continue
        cached={}
        with (root/(row['fight']+'.jsonl')).open() as stream:
            for line in stream:
                f=json.loads(line)
                if f.get('terminal'):continue
                for e in f['events']:
                    if e['stage']=='intent':cached[e['unit']]=e['value']
                    if e['stage']=='s1_support':
                        id=e['unit'];s={**f['joint'],'self':id};a=cached[id]
                        reqs.append(dict(wrapper=False,frames=[frame([s],f['tick'],{str(id):pending(a,1)})]));cells.append(row['pilot_cell'])
    results=native(reqs);totals={c:[0,0,0] for c in pilot.CELLS}
    for cell,rows in zip(cells,results):
        ss=[e['value'] for e in rows[0]['events'] if e['stage']=='s1_support']
        assert len(ss)==1
        v=ss[0];totals[cell][0]+=1;totals[cell][1]+=v['snap_error']>v['splash']/4;totals[cell][2]+=v['autonomous_bound_error']>v['splash']/4
    assert totals['D2-10'][0]==1750 and totals['M2-10'][0]==3703
    assert all(1-bad/n>=.95 for n,bad,bound in totals.values())
    assert totals['M2-10'][2]>100 # Physical clipping must remain visible.
    # Save counted regression evidence, not an empirical fresh-pilot claim.
    result=HERE/'S1FIX_SUPPORT_REPLAY.json'
    assert not result.exists()
    result.write_text(json.dumps(dict(physical_fights=0,mode='independent stored-state autonomous support replay',counts={c:dict(rows=n,bad_snap=bad,bound_gt_splash4=bound,snap_pass=1-bad/n) for c,(n,bad,bound) in totals.items()}),indent=2)+'\n')


def test_fresh_inventory_two_cells_no_reuse_no_living_pins(tmp_path,monkeypatch):
    old=set(read(HERE/'S1_PILOT_SEED_EXCLUSIONS.json')['seeds'])
    monkeypatch.setattr(pilot,'HERE',tmp_path);monkeypatch.setattr(pilot,'ROOT',tmp_path/'pilot')
    monkeypatch.setattr(pilot,'pins',lambda:dict(design_commit='cac370a',revision='S1FIX-2'))
    monkeypatch.setattr(pilot,'forbidden_seeds',lambda:(old|set(range(10000)),{}))
    inv=pilot.seal();assert len(inv['rows'])==80 and len(inv['seeds'])==40 and set(inv['seeds']).isdisjoint(old)
    assert sum(r['sample'] for r in inv['rows'])==20
    assert all(sum(r['sample'] for r in inv['rows'] if r['pilot_cell']==cell)==10 for cell in pilot.CELLS)
    assert 'sha256' not in inv['initial_cap_authority']
    for cell in pilot.CELLS:
        for pair in range(20):
            a,b=[r for r in inv['rows'] if r['pilot_cell']==cell and r['pair']==pair]
            assert a['seed']==b['seed'] and a['request']['roster']==b['request']['roster']
    assert pilot.seal()==inv


def test_pins_and_native_build_inputs_no_living_docs():
    v=build.admit();assert v['physical_fights']==0
    assert not any(Path(p).name in ('DESIGN_UNITS_AND_LEADER.md','PLAN_CURRENT.md','SHAPE_LAB_SPEC.md','LAB_CAP.json') for p in (*v['sources'],*v['ancestor_pins']))
    assert 's1fix_fixture.inc' in pilot.pins()['sources']


def test_new_process_gate_fails_closed(tmp_path,monkeypatch):
    monkeypatch.setattr(pilot,'ROOT',tmp_path)
    monkeypatch.setattr(pilot.gate.subprocess,'run',lambda *a,**k:(_ for _ in ()).throw(PermissionError('unavailable')))
    with pytest.raises(RuntimeError,match='UNAVAILABLE'):pilot.clear(100)
    assert (tmp_path/'PROCESS_GATE.json').exists()


@pytest.mark.parametrize('failure',(None,'disk','wall','rss','sample_hash'))
def test_live_remaining_resource_gate_preserves_projection(tmp_path,monkeypatch,failure):
    monkeypatch.setattr(pilot,'ROOT',tmp_path);(tmp_path/'INVENTORY.json').write_text('{}')
    rows=[];records=[]
    for i in range(20):
        row=dict(fight=f'f{i}',sample=True);rows.append(row)
        v=dict(resources=dict(wall_seconds=1,rss_bytes=1000),disk_bytes=1000)
        records.append(v);(tmp_path/(row['fight']+'.receipt.json')).write_text(json.dumps(v))
    stored=dict(status='ADMITTED',sample_max_seconds=1,sample_receipts={r['fight']:sha(tmp_path/(r['fight']+'.receipt.json')) for r in rows})
    projection=tmp_path/'PROJECTION.json';projection.write_text(json.dumps(stored));original=projection.read_bytes()
    attempts=tmp_path/'attempts';attempts.mkdir()
    for i in range(20):(attempts/f'{i}.json').write_text(json.dumps(dict(status='COMPLETE',resources=dict(wall_seconds=1,rss_bytes=1000))))
    monkeypatch.setattr(pilot,'authority',lambda:dict(cap_seconds=200))
    monkeypatch.setattr(pilot,'free_ram_bytes',lambda:8*1024**3)
    monkeypatch.setattr(pilot.shutil,'disk_usage',lambda p:__import__('types').SimpleNamespace(free=6_000_000_000))
    if failure=='disk':monkeypatch.setattr(pilot.shutil,'disk_usage',lambda p:__import__('types').SimpleNamespace(free=5_000_100_000))
    if failure in ('wall','rss'):
        (attempts/'19.json').write_text(json.dumps(dict(status='COMPLETE',resources=dict(wall_seconds=100 if failure=='wall' else 1,rss_bytes=3*1024**3 if failure=='rss' else 1000))))
    if failure=='sample_hash':(tmp_path/'f0.receipt.json').write_text('{}')
    if failure:
        with pytest.raises(RuntimeError,match=dict(disk='disk reserve',wall='live owner cap',rss='RSS',sample_hash='sample receipt hash')[failure]):pilot.resource_gate(dict(rows=rows))
    else:
        result=pilot.resource_gate(dict(rows=rows));assert result['remaining_attempts']==60 and result['maximum_extent_projected_seconds']==140
        assert result['remaining_disk_reserve_bytes']==5_000_120_000
    assert projection.read_bytes()==original
    if failure!='sample_hash':assert (tmp_path/'resource_checks/0001.json').exists()
