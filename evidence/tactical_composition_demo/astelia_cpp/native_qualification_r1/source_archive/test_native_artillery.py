"""Typed artillery prediction, planning, reservation, and actual rollout work."""
import hashlib,json,pathlib,subprocess,sys
import pytest
from build_admission import admit
from result_schema import validate_rows
ROOT=pathlib.Path(__file__).resolve().parent

@pytest.fixture(scope='module')
def native_artillery():
    for target in ('native','artillery-check'):
        subprocess.run([sys.executable,str(ROOT/'build.py'),'--engine',target],check=True,capture_output=True,text=True)
    return ROOT/'build/astelia_native'

def test_prediction_reservations_gates_rollout_and_branch_ownership(native_artillery):
    binary=ROOT/'build/native_artillery_contract';admit(binary)
    assert subprocess.check_output([str(binary)],text=True)=='native artillery contracts passed\n'

def test_predictor_matches_fresh_frozen_js_models(native_artillery):
    actual=[json.loads(s) for s in subprocess.check_output([str(ROOT/'build/native_artillery_contract'),'--oracle'],text=True).splitlines()]
    source=ROOT.parent/'astelia_snapshot/formation_sim.js'
    assert hashlib.sha256(source.read_bytes()).hexdigest()=='85b16e9b84b42b831dd2e64a7055474b6df902e4c1ffd635e6670fc6fb665733'
    script=r"""const fs=require('fs'),vm=require('vm');let source=fs.readFileSync(process.argv[1],'utf8');source=source.replace('const api = { triggerAbility','const api = { predictVolley, smartVolley, triggerAbility');const context={module:{exports:{}}};vm.runInNewContext(source,context);const sim=context.module.exports;
for(const game of [false,true])for(const exact of [false,true])for(let dodge=0;dodge<3;dodge++)for(const lock of [false,true]){
 const w=sim.create('formation',{seed:20261005,scenario:'mirror',width:650,army:{melee:2,ranged:2,artillery:2},rules:game?'game':undefined,ai:[{brain:'formation',skills:{artyModel:exact?'exact':'simple',artyOwn:true,dodgeShells:false}},{brain:'formation',skills:{dodgeShells:dodge===1?true:dodge===2?'smart':false}}]});
 const ours=sim.monsters(w),es=sim.hunters(w);es.forEach((u,j)=>{u.x=380+j*15;u.y=300+j*10;u.svx=-20;u.svy=5;});ours[0].x=390;ours[0].y=300;if(lock)es[0].target=ours[0];
 const planned=[{x:380,y:300,t:.6,dmg:30,splash:45,src:{team:0}},{x:410,y:310,t:.9,dmg:22,splash:40,src:{team:0}}],p=sim.predictVolley(w,0,planned,.9);console.log(JSON.stringify({per:p.per,val:p.val,own:p.own,smart:sim.smartVolley(w,0,planned),snap:p.snap.map(q=>[q.x,q.y,q.hp])}));
}"""
    expected=[json.loads(s) for s in subprocess.check_output(['node','-e',script,str(source)],text=True).splitlines()]
    assert len(actual)==len(expected)==24
    for got,want in zip(actual,expected):
        for key in ('per','val','own','smart'):assert got[key]==pytest.approx(want[key],abs=1e-9)
        assert len(got['snap'])==len(want['snap'])
        for a,b in zip(got['snap'],want['snap']):assert a==pytest.approx(b,abs=1e-8)

@pytest.mark.parametrize('level',['veteran','elite','elite-fast'])
@pytest.mark.parametrize('rules',['sandbox','game'])
def test_complete_profiles_run_fresh_and_deterministically(native_artillery,level,rules):
    req={'mode':'alone','trace':True,'options':{'seed':20261005,'scenario':'mirror','duration':3,'rules':rules,'width':650,'army':{'melee':2,'ranged':4,'artillery':2},'ai':[{'level':level},{'level':'regular'}]}}
    raw=json.dumps(req)+'\n';first=subprocess.run([str(native_artillery),'--metrics'],input=raw,text=True,capture_output=True,check=True);repeat=subprocess.run([str(native_artillery),'--metrics'],input=raw,text=True,capture_output=True,check=True)
    assert first.stdout==repeat.stdout and first.stderr==repeat.stderr
    rows=[json.loads(s) for s in first.stdout.splitlines()];assert validate_rows(req,rows)=='completed'
    if level!='veteran':
        work=json.loads(first.stderr);assert work['search_calls']>0 and work['inference_calls']>0 and work['artillery_rollouts']>0 and work['branch_steps']>0

@pytest.mark.parametrize('skill',[{'holdFire':{'wave':.45}},{'holdFire':{'sync':.5}},{'holdFire':{'wave':.45,'sync':.5}},{'artyFire':'plan','artyModel':'exact','artyOwn':True,'artyFollow':'shooters','artyHerd':10,'artyBattery':True},{'artyFire':'plan','artyRollout':{'top':3,'horizon':.3}},{'artyFire':'plan','artyRollout':{'top':5,'horizon':.3,'score':'ltd2','dt':.1,'every':.3,'shape':['herd','split','battery']}}])
def test_planner_skill_configuration_is_exercised(native_artillery,skill):
    req={'mode':'formation','options':{'seed':20261005,'scenario':'mirror','duration':2,'rules':'game','width':650,'army':{'melee':2,'ranged':4,'artillery':3},'ai':[{'brain':'formation','skills':skill},{}]}}
    result=json.loads(subprocess.check_output([str(native_artillery)],input=json.dumps(req)+'\n',text=True));assert validate_rows(req,[result])=='completed'

@pytest.mark.parametrize('skill',[{'holdFire':{'wave':-1}},{'artyRollout':{'top':0}},{'artyRollout':{'horizon':0}},{'artyRollout':{'score':'unknown'}},{'artyRollout':{'shape':['unknown']}}])
def test_bad_planner_configuration_is_rejected(native_artillery,skill):
    req={'mode':'formation','options':{'scenario':'mirror','ai':[{'skills':skill},{}]}}
    assert 'error' in json.loads(subprocess.check_output([str(native_artillery)],input=json.dumps(req)+'\n',text=True))
