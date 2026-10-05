"""Stage-B independent geometry/lifetime checks and explicit host scope."""
import json
import pathlib
import subprocess
import sys
import pytest
from build_admission import admit
from result_schema import validate_rows

ROOT = pathlib.Path(__file__).resolve().parent


@pytest.fixture(scope='module')
def native_core():
    for engine in ('core-check','native'):
        subprocess.run([sys.executable,str(ROOT/'build.py'),'--engine',engine],check=True,capture_output=True,text=True)
    return ROOT/'build/astelia_native'


def request(**options):
    return dict(mode='alone',options=dict(scenario='mirror',duration=.2,width=650,
        army={'melee':2,'ranged':4,'artillery':2},ai=[{'level':'novice'},{'level':'novice'}],**options))


def test_independent_geometry_lifetimes_and_nested_forks(native_core):
    binary=ROOT/'build/native_core_contract'
    admit(binary)
    assert subprocess.check_output([str(binary)],text=True)=='native core contracts passed\n'


@pytest.mark.parametrize('shots',['aimed','homing'])
def test_fresh_core_trace_and_batch(native_core,shots):
    req=request(seed=20261004,shots=shots);req['trace']=True
    raw=json.dumps(req)+'\n'
    first=subprocess.run([str(native_core)],input=raw,text=True,capture_output=True,check=True)
    repeat=subprocess.run([str(native_core)],input=raw,text=True,capture_output=True,check=True)
    assert first.stdout==repeat.stdout
    rows=[json.loads(s) for s in first.stdout.splitlines()]
    assert validate_rows(req,rows)=='completed'
    assert rows[0]['step']==0 and len(rows)>2
    good=request(seed=20261005)
    bad=request();bad['options']['ai'][0]={'level':'unknown'}
    batch=json.loads(subprocess.check_output([str(native_core)],input=json.dumps([bad,good])+'\n',text=True))
    assert 'error' in batch[0] and validate_rows(good,[batch[1]])=='completed'
    assert admit(native_core)['scope']=='native_complete_engine'


def test_complete_elite_profile_is_supported(native_core):
    req=request();req['options']['ai'][0]={'level':'elite'}
    row=json.loads(subprocess.check_output([str(native_core)],input=json.dumps(req)+'\n',text=True))
    assert validate_rows(req,[row])=='completed'


def test_aggregate_overflow_is_explicit_error(native_core):
    req=request();req['options'].update(dt=1e308,duration=1e308)
    row=json.loads(subprocess.check_output([str(native_core)],input=json.dumps(req)+'\n',text=True))
    assert set(row)=={'error'} and 'overflow' in row['error']


def test_native_hot_headers_exclude_dynamic_runtime():
    # An architectural dependency gate, not a test of particular member names.
    for path in (ROOT/'src/native').glob('*.h'):
        text=path.read_text()
        assert 'js_value' not in text and 'builtins.h' not in text and 'std::function' not in text
