"""Typed formations and commanders, with frozen authored shape oracles."""
import json
import pathlib
import subprocess
import sys
import pytest
from build_admission import admit
from result_schema import validate_rows

ROOT=pathlib.Path(__file__).resolve().parent
PRESETS=['line','wide line','wedge','box','column','loose','screen','crescent','ring','wedge hold',
         'line anvil','wedge flank','loose free','swarm','loose skirmish','loose berserk']


@pytest.fixture(scope='module')
def native_formation():
    for engine in ('native','formation-check'):
        subprocess.run([sys.executable,str(ROOT/'build.py'),'--engine',engine],check=True,capture_output=True,text=True)
    return ROOT/'build/astelia_native'


def test_independent_shape_tactics_targets_and_branch_ownership(native_formation):
    binary=ROOT/'build/native_formation_contract';admit(binary)
    assert subprocess.check_output([str(binary)],text=True)=='native formation contracts passed\n'


@pytest.mark.parametrize('preset',PRESETS)
@pytest.mark.parametrize('rules',['sandbox','game'])
def test_presets_run_deterministically(native_formation,preset,rules):
    req=dict(mode='formation',options=dict(seed=20261005,scenario='mirror',duration=1,rules=rules,
        army={'melee':3,'ranged':5,'artillery':2},f={'preset':preset},enemy='formation',enemyF={'preset':preset}))
    raw=json.dumps(req)+'\n'
    first=subprocess.check_output([str(native_formation)],input=raw,text=True)
    repeat=subprocess.check_output([str(native_formation)],input=raw,text=True)
    assert first==repeat and validate_rows(req,[json.loads(first)])=='completed'


@pytest.mark.parametrize('brain',['reactive','storm','wolfpack','gamepack'])
def test_commanders_have_finite_fresh_traces(native_formation,brain):
    req=dict(mode=brain,trace=True,debug=True,options=dict(seed=20261005,scenario='mirror',duration=2,
        rules='game',army={'melee':3,'ranged':5,'artillery':2},enemy=brain,abilities=True,sandboxAbilities=True))
    raw=json.dumps(req)+'\n';first=subprocess.check_output([str(native_formation)],input=raw,text=True)
    assert first==subprocess.check_output([str(native_formation)],input=raw,text=True)
    rows=[json.loads(s) for s in first.splitlines()];assert validate_rows(req,rows)=='completed'
    assert all('0' in frame['state']['debug']['packs'] for frame in rows[:-1])
    assert rows[1]['state']['debug']['packs']['0']['plan']


def test_authored_slots_match_frozen_js(native_formation):
    # A single tick isolates shape/anchor calculations before chaotic contact.
    requests=[dict(mode='formation',trace=True,debug=True,options=dict(seed=20261005,scenario='mirror',duration=.01,
        army={'melee':3,'ranged':5,'artillery':2},f={'preset':preset},ai=[{'level':'regular','formation':{'preset':preset}},{'level':'novice'}])) for preset in PRESETS]
    for req in requests:
        raw=json.dumps(req)+'\n';cpp=[json.loads(s) for s in subprocess.check_output([str(native_formation)],input=raw,text=True).splitlines()]
        js=[json.loads(s) for s in subprocess.check_output(['node',str(ROOT/'js_host.cjs')],input=raw,text=True).splitlines()]
        cu={u['id']:u for u in cpp[1]['state']['units']};ju={u['id']:u for u in js[1]['state']['units']}
        for uid in cu:
            if cu[uid]['team']!=0:continue
            for key in ('slotX','slotY'):
                assert cu[uid]['debug'][key]==pytest.approx(ju[uid]['debug'][key],abs=1e-8)
        for key in ('x','y','ax','ay'):
            assert cpp[1]['state']['debug']['packs']['0']['anchor'][key]==pytest.approx(js[1]['state']['debug']['packs']['0']['anchor'][key],abs=1e-9)


def test_unmigrated_search_and_artillery_planner_reject_without_fallback(native_formation):
    for profile in ({'level':'elite'},{'level':'veteran'},{'brain':'rules','lookahead':'mind'}):
        req={'mode':'reactive','options':{'scenario':'mirror','ai':[profile,{'level':'novice'}]}}
        row=json.loads(subprocess.check_output([str(native_formation)],input=json.dumps(req)+'\n',text=True))
        assert 'error' in row and 'pending' in row['error']


def test_custom_kind_uses_game_role_protection(native_formation):
    req={'mode':'alone','trace':True,'options':{'scenario':'mirror','rules':'game','duration':3,'width':600,
        'ai':[{'level':'novice'},{'level':'novice'}],
        'unitSet':{'kinds':{'dart🐾':{'role':'ranged','hp':80,'speed':0,'r':6,'dmg':12,'cd':1,'windup':.5,'reach':500,'ep':100,'epRegen':8,'cost':5,'shot':350}},'army':[['dart🐾',1]]}}}
    raw=json.dumps(req)+'\n';cpp=[json.loads(s) for s in subprocess.check_output([str(native_formation)],input=raw,text=True).splitlines()]
    js=[json.loads(s) for s in subprocess.check_output(['node',str(ROOT/'js_host.cjs')],input=raw,text=True).splitlines()]
    assert cpp[-1]==js[-1] and cpp[-1]['total']>0
