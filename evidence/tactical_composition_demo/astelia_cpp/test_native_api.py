"""Native caller paths and source-derived catalog/opponent compatibility."""
import json,pathlib,subprocess,sys
import pytest
from build_admission import admit
ROOT=pathlib.Path(__file__).resolve().parent
@pytest.fixture(scope='module')
def native_api():
    for target in ('native','api-check','matched-check'):
        subprocess.run([sys.executable,str(ROOT/'build.py'),'--engine',target],capture_output=True,text=True,check=True)
    return ROOT/'build/astelia_native'
def test_public_native_controller_lifecycle(native_api):
    binary=ROOT/'build/native_api_contract';admit(binary)
    assert subprocess.check_output([str(binary)],text=True)=='native API contracts passed\n'
def test_catalog_is_source_derived(native_api):
    actual=json.loads(subprocess.check_output([str(native_api),'--catalog'],text=True))
    source=ROOT.parent/'astelia_snapshot/formation_sim.js'
    script="const sim=require(process.argv[1]);function f(x,p){if(typeof x==='function')return {native_callback:p};if(Array.isArray(x))return x.map((v,i)=>f(v,p+'.'+i));if(x&&typeof x==='object')return Object.fromEntries(Object.entries(x).map(([k,v])=>[k,f(v,p+'.'+k)]));return x;}console.log(JSON.stringify(Object.fromEntries(Object.entries(sim).filter(([,v])=>typeof v!=='function').map(([k,v])=>[k,f(v,k)]))));"
    expected=json.loads(subprocess.check_output(['node','-e',script,str(source)],text=True));assert actual==expected
@pytest.mark.parametrize('seed',[0,-1,7,20261005,2**32+7,0.125])
@pytest.mark.parametrize('mode',['any','pool'])
def test_opponent_draw_matches_js(native_api,seed,mode):
    req={'operation':'rng','seed':seed,'rounds':30,'drawMode':mode};raw=json.dumps(req)+'\n'
    assert json.loads(subprocess.check_output([str(native_api)],input=raw,text=True))==json.loads(subprocess.check_output(['node',str(ROOT/'js_host.cjs')],input=raw,text=True))
def test_negative_opponent_count_is_explicit_error(native_api):
    assert 'error' in json.loads(subprocess.check_output([str(native_api)],input=json.dumps({'operation':'rng','seed':7,'rounds':-1})+'\n',text=True))
def test_optional_search_recording_uses_native_features(native_api):
    req={'mode':'reactive','trace':True,'debug':True,'options':{'bcRecord':True,'seed':20261005,'scenario':'mirror','duration':.2,'width':650,'army':{'melee':2,'ranged':4,'artillery':0},'ai':[{'lookahead':{'plans':['hold'],'horizon':.1,'dt':.1,'contact':1000}},{}]}}
    rows=[json.loads(s) for s in subprocess.check_output([str(native_api)],input=json.dumps(req)+'\n',text=True).splitlines()];records=rows[-2]['state']['debug']['bcData'];assert records and all(len(features)==34 and choice==0 for features,choice in records)
def test_work_audit_counts_actual_shortlist_inference(native_api):
    req={'mode':'reactive','options':{'seed':20261005,'scenario':'mirror','rules':'game','duration':.1,'width':650,'army':{'melee':2,'ranged':4,'artillery':0},'ai':[{'lookahead':{'extends':'fast','horizon':.1,'contact':1000}},{}]}}
    raw=json.dumps(req)+'\n';plain=subprocess.run(['node',str(ROOT/'js_host.cjs')],input=raw,text=True,capture_output=True,check=True);audit=subprocess.run(['node',str(ROOT/'work_audit_host.cjs')],input=raw,text=True,capture_output=True,check=True)
    assert plain.stdout==audit.stdout;work=json.loads(audit.stderr);assert work['inference_calls']>0 and work['forks']>0 and work['branch_unit_actions']>0
