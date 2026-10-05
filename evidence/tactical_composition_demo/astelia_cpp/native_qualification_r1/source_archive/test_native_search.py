"""Fresh typed neural, full/fast/mind search and independent branch contracts."""
import json,pathlib,random,subprocess,sys
import pytest
from build_admission import admit
from result_schema import validate_rows
ROOT=pathlib.Path(__file__).resolve().parent

@pytest.fixture(scope='module')
def native_search():
    for target in ('native','search-check'):
        subprocess.run([sys.executable,str(ROOT/'build.py'),'--engine',target],check=True,capture_output=True,text=True)
    return ROOT/'build/astelia_native'

def test_branch_options_models_budgets_and_ownership(native_search):
    binary=ROOT/'build/native_search_contract';admit(binary)
    assert subprocess.check_output([str(binary)],text=True)=='native search contracts passed\n'

def test_frozen_network_scores_match_fresh_js(native_search):
    rng=random.Random(20261005)
    vectors=[[0.0]*46,[1.0]*46]+[[rng.uniform(-2,2) for _ in range(46)] for _ in range(128)]
    payload='\n'.join(' '.join(map(repr,v)) for v in vectors)+'\n'
    actual=[json.loads(s) for s in subprocess.check_output([str(ROOT/'build/native_search_contract'),'--network'],input=payload,text=True).splitlines()]
    script="""const fs=require('fs'),net=require(process.argv[1]);const xs=JSON.parse(fs.readFileSync(0,'utf8'));for(const x of xs){const h=net.W1.map((row,j)=>Math.max(0,row.reduce((v,a,i)=>v+a*x[i],net.b1[j])));const scores=net.W2.map((row,q)=>row.reduce((v,a,j)=>v+a*h[j],net.b2[q]));console.log(JSON.stringify(scores));}"""
    expected=[json.loads(s) for s in subprocess.check_output(['node','-e',script,str(ROOT.parent/'astelia_snapshot/bc_net.json')],input=json.dumps(vectors),text=True).splitlines()]
    assert actual==expected

@pytest.mark.parametrize('name',['full','fast','mind'])
@pytest.mark.parametrize('model',['oracle','continue','rush','rules'])
def test_search_modes_execute_and_repeat_fresh(native_search,name,model):
    req={'mode':'reactive','trace':True,'options':{'seed':20261005,'scenario':'mirror','duration':1,'width':650,'army':{'melee':2,'ranged':4,'artillery':0},'ai':[{'brain':'rules','lookahead':{'extends':name,'models':[model],'horizon':.3,'contact':1000}},{}]}}
    raw=json.dumps(req)+'\n';first=subprocess.run([str(native_search),'--metrics'],input=raw,text=True,capture_output=True,check=True)
    repeat=subprocess.run([str(native_search),'--metrics'],input=raw,text=True,capture_output=True,check=True)
    assert first.stdout==repeat.stdout and first.stderr==repeat.stderr
    rows=[json.loads(s) for s in first.stdout.splitlines()];assert validate_rows(req,rows)=='completed'
    counters=json.loads(first.stderr);assert counters['forks']>0 and counters['branch_steps']>0 and counters['candidate_models']>0
    assert counters['inference_calls']>0 if name!='full' else counters['inference_calls']==0

def test_initial_features_match_frozen_js(native_search):
    req={'mode':'reactive','trace':True,'debug':True,'options':{'seed':20261005,'scenario':'mirror','duration':.01,'width':650,'army':{'melee':2,'ranged':4,'artillery':2},'ai':[{'brain':'rules'},{'level':'regular'}]}}
    rows=[json.loads(s) for s in subprocess.check_output([str(native_search)],input=json.dumps(req)+'\n',text=True).splitlines()]
    script="""const fs=require('fs'),sim=require(process.argv[1]),r=JSON.parse(fs.readFileSync(0,'utf8')),w=sim.create(r.mode,r.options);console.log(JSON.stringify(sim.bcFeatures(w,w.packs[0],sim.LOOKAHEAD.plans)));"""
    expected=json.loads(subprocess.check_output(['node','-e',script,str(ROOT.parent/'astelia_snapshot/formation_sim.js')],input=json.dumps(req),text=True))
    assert rows[0]['state']['debug']['packs']['0']['features']==pytest.approx(expected,abs=1e-14)

@pytest.mark.parametrize('look',[{'dt':-1},{'horizon':0},{'models':[]},{'budget':0},{'models':['unknown']},{'extends':'fast','plans':['hold']},{'urgency':{'from':1,'kMin':.3}}])
def test_bad_search_configuration_rejected(native_search,look):
    req={'mode':'reactive','options':{'scenario':'mirror','ai':[{'brain':'rules','lookahead':look},{}]}}
    row=json.loads(subprocess.check_output([str(native_search)],input=json.dumps(req)+'\n',text=True));assert 'error' in row

def test_search_is_not_global_between_profiles(native_search):
    basic={'mode':'reactive','options':{'scenario':'mirror','duration':1,'width':650,'army':{'melee':2,'ranged':4,'artillery':0},'ai':[{'brain':'rules'},{}]}}
    search=json.loads(json.dumps(basic));search['options']['ai'][0]['lookahead']={'extends':'mind','horizon':.3,'objective':'deaths','urgency':{'from':.4,'kMin':.2},'everyStable':2,'stall':.5,'terminal':1}
    rows=json.loads(subprocess.check_output([str(native_search)],input=json.dumps([basic,search,basic,search])+'\n',text=True));assert rows[0]==rows[2] and rows[1]==rows[3] and all('error' not in r for r in rows)
