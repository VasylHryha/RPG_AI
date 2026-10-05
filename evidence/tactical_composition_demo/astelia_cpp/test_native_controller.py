"""S2 fence, invalid decisions, engine order and external profile admission."""
import json
import os
import pathlib
import subprocess
import sys
import pytest
from build_admission import admit

ROOT = pathlib.Path(__file__).resolve().parent


@pytest.fixture(scope='module')
def controller_build():
    for target in ('native', 'controller-check'):
        subprocess.run([sys.executable, str(ROOT/'build.py'), '--engine', target],
                       capture_output=True, text=True, check=True)
    return ROOT/'build/astelia_native'


def test_controller_contracts_and_exact_field_list(controller_build):
    binary = ROOT/'build/native_controller_contract'
    admit(binary)
    run = subprocess.run([str(binary)], capture_output=True, text=True)
    if os.environ.get('ASTELIA_S2_EVIDENCE_DIR'):
        output = pathlib.Path(os.environ['ASTELIA_S2_EVIDENCE_DIR'])
        (output/'controller_contract.stdout.txt').write_text(run.stdout)
        (output/'controller_contract.stderr.txt').write_text(run.stderr)
    assert run.returncode == 0, run.stderr
    rows = run.stdout.splitlines()
    fields = json.loads(rows[0])
    assert fields['world_fields'] == ['t', 'dt', 'width', 'height']
    assert fields['unit_fields'] == ['id', 'team', 'role', 'x', 'y', 'vx', 'vy',
        'hp', 'maxhp', 'radius', 'speed', 'range', 'dmg', 'cd', 'cdMax',
        'target', 'damageDealt', 'damageTaken', 'minRange', 'dealtToEnemy', 'takenFromEnemy', 'friendlyDealt', 'friendlyTaken']
    assert fields['status'] == 'passed'
    assert rows[1] == 'native controller contracts passed'


def test_controller_header_cannot_name_world(controller_build, tmp_path):
    manifest = json.loads(controller_build.with_suffix('.build.json').read_text())
    source = tmp_path/'fence.cpp'
    source.write_text('#include "native/controller.h"\nusing namespace astelia::control;\nWorld* forbidden;\n')
    failed = subprocess.run([manifest['compiler_path'], '-std=c++17', '-fsyntax-only',
        '-I'+str(ROOT/'src'), str(source)], capture_output=True, text=True)
    if os.environ.get('ASTELIA_S2_EVIDENCE_DIR'):
        output = pathlib.Path(os.environ['ASTELIA_S2_EVIDENCE_DIR'])
        (output/'fence_negative.cpp.txt').write_text(source.read_text())
        (output/'fence_negative.stderr.txt').write_text(failed.stderr)
    assert failed.returncode != 0 and "unknown type name 'World'" in failed.stderr
    source.write_text('#include "native/controller.h"\nusing namespace astelia::control;\nObservation allowed;\n')
    subprocess.run([manifest['compiler_path'], '-std=c++17', '-fsyntax-only',
        '-I'+str(ROOT/'src'), str(source)], capture_output=True, text=True, check=True)


@pytest.mark.parametrize('side', [0, 1])
@pytest.mark.parametrize('name', ['nearest', 'hold', 'passthrough'])
def test_controller_profile_on_either_side(controller_build, side, name):
    ai = [{}, {}]
    ai[side] = {'controller': name, 'params': {}}
    req = {'mode': 'alone', 'options': {'seed': 20261005, 'scenario': 'mirror',
        'rules': 'game', 'duration': .2, 'ai': ai}}
    rows = json.loads(subprocess.check_output([str(controller_build), "--test-controllers"],
        input=json.dumps([req, req])+'\n', text=True))
    assert rows[0] == rows[1] and 'error' not in rows[0]


@pytest.mark.parametrize('profile', [{'controller': 'other'}, {'controller': ''},
    {'controller': 'nearest', 'params': {'gain': 1}}, {'params': {}},
    {'controller': 'hold', 'params': []}])
def test_invalid_controller_profiles_fail_closed(controller_build, profile):
    req = {'mode': 'alone', 'options': {'scenario': 'mirror', 'ai': [profile, {}]}}
    row = json.loads(subprocess.check_output([str(controller_build), "--test-controllers"],
        input=json.dumps(req)+'\n', text=True))
    assert 'error' in row


@pytest.mark.parametrize('name', ['nearest', 'hold'])
def test_special_player_body_rejected_on_controlled_side(controller_build, name):
    req = {'mode': 'alone', 'options': {'scenario': 'skirmish', 'rules': 'game',
        'duration': .1, 'ai': [{}, {'controller': name}]}}
    row = json.loads(subprocess.check_output([str(controller_build), "--test-controllers"],
        input=json.dumps(req)+'\n', text=True))
    assert 'special player body' in row['error']


@pytest.mark.parametrize('side,name', [(0, 'nearest'), (1, 'passthrough')])
def test_supported_skirmish_control_remains_available(controller_build, side, name):
    ai = [{}, {}]
    ai[side] = {'controller': name}
    req = {'mode': 'alone', 'options': {'scenario': 'skirmish', 'rules': 'game',
        'duration': .1, 'ai': ai}}
    row = json.loads(subprocess.check_output([str(controller_build), "--test-controllers"],
        input=json.dumps(req)+'\n', text=True))
    assert 'error' not in row
