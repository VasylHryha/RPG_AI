"""Typed game combat, authored kinds, spawn/player state, and fresh determinism."""
import json
import pathlib
import subprocess
import sys
import pytest
from build_admission import admit
from result_schema import validate_rows

ROOT = pathlib.Path(__file__).resolve().parent


@pytest.fixture(scope='module')
def native_combat():
    for engine in ('native','combat-check'):
        subprocess.run([sys.executable,str(ROOT/'build.py'),'--engine',engine],check=True,capture_output=True,text=True)
    return ROOT/'build/astelia_native'


def request(**options):
    return dict(mode='alone',options=dict(seed=20261005,scenario='mirror',duration=2,width=650,
        army={'melee':2,'ranged':4,'artillery':2},ai=[{'level':'novice'},{'level':'novice'}],**options))


def test_independent_combat_and_state_ownership(native_combat):
    binary=ROOT/'build/native_combat_contract'
    admit(binary)
    assert subprocess.check_output([str(binary)],text=True)=='native combat contracts passed\n'


@pytest.mark.parametrize('scenario',['mirror','hunters','skirmish'])
@pytest.mark.parametrize('rules',['sandbox','game'])
def test_new_combat_runs_fresh_and_deterministically(native_combat,scenario,rules):
    if scenario=='skirmish' and rules=='sandbox':
        return  # authored player/kinds use game rules only
    req=request(rules=rules);req['options']['scenario']=scenario
    req['options'].update(hunters={'melee':2,'archers':1,'respawn':.2})
    req['trace']=True
    raw=json.dumps(req)+'\n'
    first=subprocess.run([str(native_combat)],input=raw,text=True,capture_output=True,check=True)
    repeat=subprocess.run([str(native_combat)],input=raw,text=True,capture_output=True,check=True)
    assert first.stdout==repeat.stdout
    rows=[json.loads(s) for s in first.stdout.splitlines()]
    assert validate_rows(req,rows)=='completed'
    assert len(rows)>2
    if scenario=='skirmish':
        initial=rows[0]['state']['units']
        assert len(initial)==9 and any(u['role']=='player' for u in initial)
        assert all('kind' in u for u in initial if u['team']==0)


def test_rule_switch_and_ability_policy_are_battle_local(native_combat):
    game=request(rules='game');sandbox=request(abilities=True)
    sandbox['options']['ai']=[{'brain':'alone','skills':{'abilities':'auto'}},{'brain':'alone'}]
    rows=json.loads(subprocess.check_output([str(native_combat)],input=json.dumps([game,sandbox,game,sandbox])+'\n',text=True))
    assert rows[0]==rows[2] and rows[1]==rows[3]
    assert all('error' not in row for row in rows)


def test_custom_utf8_kinds_and_carried_asymmetric_armies(native_combat):
    req=request(rules='game')
    req['options']['unitSet']={'kinds':{'dart🐾':{'role':'ranged','hp':80,'speed':60,'r':6,'dmg':12,
        'cd':1,'windup':.5,'reach':220,'ep':100,'epRegen':8,'cost':5,'shot':350}},'army':[['dart🐾',4]]}
    req['trace']=True
    rows=[json.loads(s) for s in subprocess.check_output([str(native_combat)],input=json.dumps(req)+'\n',text=True).splitlines()]
    assert validate_rows(req,rows)=='completed'
    assert all(u['kind']=='dart🐾' and u['hp']==80 for u in rows[0]['state']['units'])
    carried=request();carried['options'].update(ours=[{'role':'melee','hp':123},{'role':'ranged','hp':42}],enemyArmy={'melee':3,'ranged':2,'artillery':1})
    carried['trace']=True
    rows=[json.loads(s) for s in subprocess.check_output([str(native_combat)],input=json.dumps(carried)+'\n',text=True).splitlines()]
    assert validate_rows(carried,rows)=='completed'
    assert [u['hp'] for u in rows[0]['state']['units'] if u['team']==0]==[123,42]
    assert len(rows[0]['state']['units'])==8


def test_empty_custom_army_does_not_fall_back_to_default(native_combat):
    req=request(rules='game');req['options']['unitSet']={'kinds':{},'army':[]}
    row=json.loads(subprocess.check_output([str(native_combat)],input=json.dumps(req)+'\n',text=True))
    assert row['t']==0 and row['survivors']==row['enemySurvivors']==0
