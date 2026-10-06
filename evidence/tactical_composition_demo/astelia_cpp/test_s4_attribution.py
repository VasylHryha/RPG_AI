"""Zero-combat Part-1 checks. No compiler subprocesses or simulation requests."""
import copy
import hashlib
import json
import pathlib
import subprocess
import sys
import pytest
import s4_attribution as A
from s3_runner import request
from build_admission import admit


def test_native_synthetic_contracts():
    admit(A.BINARY)
    run = subprocess.run([str(A.BINARY), '--attribution-contract'], capture_output=True, text=True, check=True)
    rows = [json.loads(line) for line in run.stdout.splitlines()]
    assert all(r['status'] == 'passed' and r['fights'] == 0 for r in rows)
    assert rows[-1]['fixture_action_bytes_compared'] > 10000
    A.write(A.ROOT/'s4_attribution_checks/NATIVE_CONTRACT.json', rows[-1])


def test_baseline_is_prechange_source_with_namespace_isolation_only():
    identity = json.loads((A.ROOT/'s4_attribution_checks/BASELINE_IDENTITY.json').read_text())
    for name, h in identity['original_hashes'].items():
        s = (A.ROOT/'s4_attribution_checks/baseline_native'/name).read_text()
        s = s.replace('namespace astelia::control::attribution_baseline {', 'namespace astelia::control {')
        if name.endswith('.h'):
            s = s.replace('#include "../../src/native/controller.h"', '#include "controller.h"')
        s = s.replace('baselineV2Legal', 'v2Legal').replace('baselineV2Threat', 'v2Threat')
        assert hashlib.sha256(s.encode()).hexdigest() == h

    s = (A.ROOT/'s4_attribution_checks/baseline_native/v4_contract.cpp').read_text()
    s = s.replace('int historicalV4Contract()', 'int main()').replace('return 0;\n}catch(const std::exception& e)', '}catch(const std::exception& e)')
    assert hashlib.sha256(s.encode()).hexdigest() == identity['historical_v4_contract_original_sha256']


def test_exact_common_fixed_knob_fight_set_and_fresh_ledger():
    d = A.declaration()
    used = set()
    for path in list(A.ROOT.glob('S4_V*_SEEDS.json')) + list(A.ROOT.glob('s4_v4_development_failed_*/S4_V4_SEEDS.json')):
        old = json.loads(path.read_text())
        used |= {fight[1] for splits in old['panels'].values() for panel in splits.values() for fight in panel}
    used |= {s['seed'] for s in json.loads((A.ROOT/'s3_controllers_r3/default.requests.json').read_text())}
    assert not set(d['seeds']) & used
    assert all(not 310000000 <= s <= 314000000 for s in d['seeds'])
    specs = [s for pair in A.tasks(d) for s in pair]
    assert len(specs) == 3200 and sum(s['trace'] for s in specs) == 80
    params = json.loads(A.KNOBS.read_text())
    assert hashlib.sha256(A.KNOBS.read_bytes()).hexdigest() == d['fixed_knobs_sha256']
    ids = {(s['skeleton'], s['arm'], s['opponent'], s['seed'], s['swapSides']) for s in specs}
    assert len(ids) == 3200
    for s in specs:
        assert s['params'] == params[s['arm']]
        r = request(s)
        assert r['options']['army'] == dict(melee=10, ranged=30, artillery=10)
        assert r['options']['ai'][0]['skeleton'] == s['skeleton']
        assert r['options']['duration'] == 150
        assert s['trace'] == (s['opponent'] == 'regular' and s['seed'] in d['trace_seeds'])


def unit(c, mode, held=0, focus=None, gun=False):
    return dict(id=1, c=c, focus=focus, pairs=[dict(enemy=20, mode=mode, remainingHold=held)], insideGunReach=gun, feasibility=1., undefinedReason=None)


def tick(step, u, events=()):
    return dict(decisionDiagnostics=True, step=step, dt=.1, units=[u], holdEvents=list(events))


def event(reason, cause='none'):
    return dict(id=1, enemy=20, reason=reason, releaseCause=cause)


def test_distinct_unit_proxy_pair_modes_focus_expiry_and_same_tick_rearm():
    t = A.TraceCounter()
    t.consume(tick(1, unit(1, 'commit')))
    t.consume(tick(2, unit(-1, 'escape', 1), [event('started')]))
    t.consume(tick(3, unit(1, 'escape', .9)))
    t.consume(tick(4, unit(-1, 'commit', 1, focus=20, gun=True), [event('expired'), event('started')]))
    t.consume({'state':{'units':[dict(id=1, alive=True), dict(id=20, alive=True)]}})
    d = t.finish()['counts']
    assert d['unit_intent_proxy_changes'] == 3 and d['pair_mode_changes'] == 2
    assert d['focus_while_escaping_ticks'] == 1 and d['holds_expiring_inside_gun_reach'] == 1
    assert d['terminal_censored_living_holds'] == 1 and d['death_released_holds'] == 0


@pytest.mark.parametrize('a,b,cause', [(False,True,'own_death'), (True,False,'enemy_death'), (False,False,'both_death'), (True,True,None)])
def test_terminal_hold_death_without_following_prepare(a, b, cause):
    t = A.TraceCounter()
    t.consume(tick(1, unit(1,'commit')))
    t.consume(tick(2, unit(-1,'escape',1), [event('started')]))
    t.consume({'state':{'units':[dict(id=1, alive=a), dict(id=20, alive=b)]}})
    d = t.finish()['counts']
    if cause:
        assert d['terminal_released_holds_'+cause] == 1 and d['death_released_holds'] == 1
        assert d['terminal_censored_living_holds'] == 0
    else:
        assert d['terminal_censored_living_holds'] == 1


@pytest.mark.parametrize('cause', ['own_death','enemy_death','both_death','missing'])
def test_prepare_disappearance_is_pair_release_not_unique_death(cause):
    t = A.TraceCounter()
    t.consume(tick(1, unit(-1,'escape',1), [event('started')]))
    t.consume(dict(decisionDiagnostics=True, step=2, dt=.1, units=[], holdEvents=[event('disappeared',cause)]))
    d = t.finish()['counts']
    assert d['death_released_holds_'+cause] == 1
    assert d['death_released_holds'] == (cause != 'missing')
    assert d['terminal_censored_living_holds'] == 0


def test_trace_missing_tick_or_hold_event_fails_closed():
    t = A.TraceCounter()
    with pytest.raises(RuntimeError, match='trace tick'):
        t.consume(tick(2, unit(1,'commit')))
    t = A.TraceCounter()
    with pytest.raises(RuntimeError, match='snapshot mismatch'):
        t.consume(tick(1, unit(1,'commit',1)))


def fake_rows(d):
    rows=[]
    for cell_index, cell in enumerate(A.CELLS):
        for arm in A.ARMS:
            for head in A.HEADS:
                for i, s in enumerate(d['seeds']):
                    for swap in (False,True):
                        rows.append(dict(spec=dict(skeleton=cell,arm=arm,opponent=head,seed=s,swapSides=swap),
                            summary=dict(survivors=10+cell_index+i+(100 if swap else 0),enemySurvivors=0,t=150,artilleryAlive=[0,2])))
    return rows


def test_inference_is_orientation_clustered_and_paired_with_interaction():
    d = A.declaration();rows = fake_rows(d);result = A.analyze(rows,d)
    e = result['endpoints']['resonator|regular']
    assert e['cells']['v3']['S']['n'] == 100
    assert e['cells']['v3']['S']['mean'] == 109.5
    assert e['cells']['v3']['S']['sd'] == pytest.approx(A.statistics95(range(100))['sd'])
    assert e['paired_differences']['H-v3']['mean'] == 1
    assert e['paired_differences']['HF-F']['descriptive_normal_95'] == [1,1]
    assert e['interaction_HF-H-F+v3']['mean'] == 0
    assert len(e['paired_differences']) == 6
    with pytest.raises(RuntimeError, match='incomplete'):
        A.analyze(rows[:-1],d)
    with pytest.raises(RuntimeError, match='duplicate'):
        A.analyze(rows+[rows[0]],d)


def test_execute_requires_quiet_release_and_refuses_existing_output(monkeypatch, tmp_path):
    monkeypatch.setattr(sys,'argv',['s4_attribution.py','--execute'])
    with pytest.raises(RuntimeError,match='C6 quiet-machine'):
        A.main()
    monkeypatch.setattr(sys,'argv',['s4_attribution.py','--execute','--quiet-machine-finished','--output',str(A.ROOT)])
    with pytest.raises(RuntimeError,match='fresh output'):
        A.main()


def test_native_failure_or_planner_work_is_rejected():
    summary=dict(controllerStatus='completed',controllerFailures=[0,0],survivors=10,enemySurvivors=4,t=150,artilleryAlive=[1,2])
    metrics=dict(executed_fights=2,forks=0,search_calls=0,artillery_rollouts=0,branch_steps=0)
    A.validate_result(summary,metrics,2)
    with pytest.raises(RuntimeError,match='no-planner'):
        A.validate_result(summary,dict(metrics,forks=1),2)
    with pytest.raises(RuntimeError,match='controller failure'):
        A.validate_result(dict(summary,controllerFailures=[1,0]),metrics,2)


def test_traced_worker_streams_and_retains_exact_rows_without_a_fight(monkeypatch, tmp_path):
    """Use a tiny fake executable, never the native simulation host."""
    import gzip
    import time
    from s4_deadline import Deadline
    tmp_path.joinpath('traces').mkdir()
    records = [dict(state=dict(units=[dict(id=1, alive=True),dict(id=20, alive=True)])),
               tick(1, unit(1,'commit')),
               dict(state=dict(units=[dict(id=1, alive=True),dict(id=20, alive=True)])),
               dict(controllerStatus='completed',controllerFailures=[0,0],survivors=1,enemySurvivors=1,t=.1,artilleryAlive=[0,1])]
    metrics = dict(executed_fights=1,forks=0,search_calls=0,artillery_rollouts=0,branch_steps=0)
    fake = tmp_path/'fake_native'
    fake.write_text('#!'+sys.executable+'\nimport sys\nsys.stdin.read()\nsys.stdout.write('+repr(''.join(json.dumps(r)+'\n' for r in records))+')\nsys.stderr.write('+repr(json.dumps(metrics))+')\n')
    fake.chmod(0o755)
    monkeypatch.setattr(A,'BINARY',fake)
    spec = next(pair[0] for pair in A.tasks(A.declaration()) if pair[0]['trace'])
    deadline=Deadline(time.monotonic()+5)
    terminal, work, trace = A.traced_fight(spec,tmp_path,deadline)
    assert terminal == records[-1] and work == metrics
    packed = tmp_path/trace['file']
    assert [json.loads(x) for x in gzip.decompress(packed.read_bytes()).splitlines()] == records
    assert trace['sha256'] == hashlib.sha256(packed.read_bytes()).hexdigest()
    assert trace['diagnostics']['trace_ticks'] == 1 and not list((tmp_path/'traces').glob('*.part.jsonl'))
    assert not deadline.children
