"""Focused checks, with no fights or coreStep invocations."""
import importlib.util
import json
import pathlib
import subprocess
import sys
import pytest

HERE = pathlib.Path(__file__).resolve().parent
CPP = HERE.parent
sys.path.insert(0,str(CPP))
from build_admission import admit, sha

spec = importlib.util.spec_from_file_location('react_request_adapter',HERE/'requests.py')
requests = importlib.util.module_from_spec(spec)
spec.loader.exec_module(requests)

def host(binary, request):
    admit(binary)
    result = subprocess.run([str(binary),'--metrics'],input=json.dumps(request)+'\n',
                            text=True,capture_output=True,check=True,timeout=15)
    return result

def test_native_recorded_observation_and_decision_fixtures():
    binary=HERE/'build/react_fixture'
    admit(binary)
    result=subprocess.run(['nice','-n','15',str(binary)],input=(CPP/'s4_v7c/THETA_ORIGIN.json').read_text(),
                          text=True,capture_output=True,timeout=30)
    (HERE/'FIXTURE.stdout.log').write_text(result.stdout)
    (HERE/'FIXTURE.stderr.log').write_text(result.stderr)
    assert result.returncode==0,result.stderr
    rows=[json.loads(s) for s in result.stdout.splitlines()]
    assert rows[-1]['status']=='PASS' and rows[-1]['fights']==0
    assert rows[0]['identical'] and rows[0]['ticks']==8

@pytest.mark.parametrize('arm', requests.ARMS)
def test_arms_selectable_in_lab_v2_format_without_steps(arm):
    req=requests.request(arm,{'level':'regular'},73,abilities_off=True,shadow=True)
    req['options']['duration']=0
    result=host(requests.BINARY,req)
    rows=[json.loads(s) for s in result.stdout.splitlines()]
    assert 'error' not in rows[-1]
    assert rows[-1]['t']==0 and rows[-1]['survivors']==50
    assert json.loads(result.stderr)['executed_steps']==0

def test_delivered_zero_step_request_byte_identity():
    req=requests.lab.request('v7',{'level':'regular'},73,abilities_off=True)
    req['options']['duration']=0
    parent=CPP/'s4_shape_lab_v1/build/tactics_lab_host'
    assert host(parent,req).stdout==host(requests.BINARY,req).stdout

@pytest.mark.parametrize('arm', requests.ARMS)
def test_all_drill_constructors_preserve_parent_fields(arm):
    pool=json.loads((CPP/'s4_shape_lab_v2/DECLARATION.json').read_text())['pool']
    for drill in requests.lab.DRILLS:
        for orientation in (0,1):
            opponent=pool[0] if drill=='C3' else 'regular'
            req=requests.drill_request(drill,arm,opponent,73,orientation,pool)
            base=requests.lab.drill_request(drill,requests.base_arm(arm),opponent,73,orientation,pool)
            assert req.pop('labReact')=={'shadow':False}
            req['options']['ai'][0]['controller']=requests.base_arm(arm)
            assert req==base

def test_reduced_survivor_series_heals_and_keeps_role():
    pool=json.loads((CPP/'s4_shape_lab_v2/DECLARATION.json').read_text())['pool']
    survivors=[{'cohort_id':49,'role':'artillery','kind':'shaman','hp':1},
               {'cohort_id':12,'role':'ranged','kind':'spitter','hp':2}]
    req=requests.series_request('v7+react',pool[0],pool,73,survivors,orientation=1)
    assert req['labAbilities']=='off'
    assert len(req['labScenario']['sides'][0])==2
    assert [u['role'] for u in req['labScenario']['sides'][0]]==['ranged','artillery']
    assert all(u['hp_fraction']==1 for u in req['labScenario']['sides'][0])
    req['options']['duration']=0
    result=host(requests.BINARY,req)
    assert json.loads(result.stdout.splitlines()[-1])['survivors']==2

def test_bad_shadow_request_rejected_without_steps():
    req=requests.request('v7+react',{'level':'regular'},73)
    req['options']['duration']=0
    req['labReact']['shadow']='yes'
    result=host(requests.BINARY,req)
    assert 'error' in json.loads(result.stdout.splitlines()[-1])

def test_react_rejects_sandbox_without_steps():
    req=requests.request('v7+react',{'level':'regular'},73)
    req['options'].update(duration=0,rules='sandbox')
    req.pop('labScenario')
    result=host(requests.BINARY,req)
    assert 'requires Game rules' in json.loads(result.stdout.splitlines()[-1])['error']

def test_parent_source_and_objects_still_admitted():
    receipt=json.loads((HERE/'BUILD.json').read_text())
    assert admit(CPP/'s4_shape_lab_v1/build/tactics_lab_host')==receipt['parent']
    record=json.loads(requests.BINARY.with_suffix('.build.json').read_text())
    for path,digest in record['reused_object_sha256'].items():
        assert sha(pathlib.Path(path))==digest
