"""Focused artifact consistency checks. No project tests, combat or raw execution."""
import collections
import hashlib
import json
import math
import pathlib
import subprocess
import sys
import time

HERE = pathlib.Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    start = time.monotonic()
    data = json.loads((HERE / 'COMPACT.json').read_text())
    verify = json.loads((HERE / 'VERIFICATION.json').read_text())
    assert verify['script_sha256'] == sha(HERE / 'analyze.py')
    assert len(data['fights']) == 60
    assert len({r['id'] for r in data['fights']}) == 60
    assert sum(len(r['deaths']) for r in data['fights']) == 425
    for a in data['aggregates']:
        subset = [r for r in data['fights'] if (r['arm'], r['head']) == (a['arm'], a['head'])]
        assert len(subset) == 20
        for side in (0, 1):
            c = collections.Counter()
            for r in subset:
                c.update(r['sides'][side])
                assert len({d['unit'] for d in r['deaths']}) == len(r['deaths'])
                assert all(abs(d['snapshot_age_s']-1/30) < 1e-10 for d in r['deaths'])
            assert dict(c) == a['sides'][side]['counts']
            bc = collections.Counter()
            for b in a['sides'][side]['time_bins']:
                bc.update(b['counts'])
            assert all(math.isclose(bc[k], c[k], abs_tol=1e-7) for k in bc)
            assert c['living_ticks'] == c['movement_known_ticks']+c['death_interval_ticks']
            assert c['launches'] == c['command_launch_ticks']+c['hold_launch_ticks']
            assert c['launches'] == c['gun_launches']+c['other_launches']
            assert c['gun_launches_hit_intended_gun'] <= c['gun_launches_hit_any_gun'] <= c['gun_launches']
            assert c['gun_target_shell_gun_victims'] >= c['gun_launches_hit_any_gun']
            assert sum(v for k,v in c.items() if k.startswith('shells_hitting_')) == c['launches']
            enemy = collections.Counter(a['sides'][1-side]['counts'])
            assert math.isclose(c['gun_target_shell_gun_damage']+c['other_target_shell_gun_damage'],
                                enemy['incoming_damage_'+str(side)+'_artillery'], abs_tol=1e-7)
            assert a['sides'][side]['ready_but_not_firing'] is None
            assert a['sides'][side]['launches_lost_to_target_switch'] is None
    report = HERE.parent / 'S4_FIRE_EFFICIENCY_DIAGNOSTIC.md'
    before = report.read_bytes()
    subprocess.run([sys.executable, str(HERE / 'render.py')], check=True)
    assert before == report.read_bytes(), 'report is stale or render is nondeterministic'
    for p in (HERE / 'analyze.py', HERE / 'render.py', HERE / 'deliver.py', pathlib.Path(__file__)):
        compile(p.read_text(), str(p), 'exec')
    products = [p for p in HERE.iterdir() if p.is_file()] + [report]
    assert all(p.stat().st_size <= 45_000_000 for p in products)
    result = dict(status='PASS', scope='artifact invariants and deterministic rendering; no combat/project suite',
                  fights=60, own_gun_deaths=425, elapsed_s=time.monotonic()-start,
                  checked_hashes={p.name:sha(p) for p in products if p.name not in ('VALIDATION.json','DELIVERY_TRANSPORT.json','COMMIT.log','BUNDLE_VERIFY.log')})
    (HERE / 'VALIDATION.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k != 'checked_hashes'}))


if __name__ == '__main__':
    main()
