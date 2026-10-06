"""Section-16 fixed-knob 2x2, development only. Importing never launches fights."""
import argparse
import collections
import gzip
import itertools
import json
import math
import pathlib
import statistics
import subprocess
import time
from build_admission import admit, sha
from s3_runner import request
from s4_deadline import Deadline, BoundedPool
from s4_development import verify_sources

ROOT = pathlib.Path(__file__).resolve().parent
BINARY = ROOT/'build/astelia_native'
CELLS = ('v3', 'H', 'F', 'HF')
ARMS = ('resonator', 'morale')
HEADS = ('novice', 'regular')
LEDGER = ROOT/'S4_ATTRIBUTION_SEEDS.json'
PIN = ROOT/'s4_attribution_checks/INPUT_PIN.json'
KNOBS = ROOT/'s4_v3_development/B_best.json'


def write(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False)+'\n')


def declaration():
    d = json.loads(LEDGER.read_text())
    if d['status'] != 'development_only' or d['judging_seeds'] is not None:
        raise RuntimeError('development ledger required')
    if len(d['seeds']) != 100 or len(set(d['seeds'])) != 100 or any(type(s) is not int or not 1500000000 <= s < 2000000000 for s in d['seeds']):
        raise RuntimeError('invalid fresh development seed allocation')
    if d['trace_seeds'] != d['seeds'][:5]:
        raise RuntimeError('trace allocation drift')
    if d['cells'] != list(CELLS) or d['arms'] != list(ARMS) or d['heads'] != list(HEADS) or d['fight_count'] != 3200:
        raise RuntimeError('section-16 fight set drift')
    return d


def check_pins(pins):
    for name, expected in pins.items():
        if sha(ROOT/name) != expected:
            raise RuntimeError('attribution input changed: '+name)


def tasks(d):
    params = json.loads(KNOBS.read_text())
    # Two orientations form one independent seed cluster. Traces are existing fights.
    for cell, arm, head, seed in itertools.product(CELLS, ARMS, HEADS, d['seeds']):
        trace = head == 'regular' and seed in d['trace_seeds']
        yield [dict(arm=arm, params=params[arm], skeleton=cell, opponent=head,
                    seed=seed, setting='s4_full_head', swapSides=swap, endCounts=True,
                    trace=trace, decisionDiagnostics=trace, attributionDiagnostics=trace)
               for swap in (False, True)]


class TraceCounter:
    """Observer state: latent intent proxy is not a physical movement reversal."""
    def __init__(self):
        self.counts = collections.Counter()
        self.intent = {}
        self.pairs = {}
        self.active = set()
        self.final_units = {}
        self.undefined = collections.Counter()
        self.cosine_sum = 0.
        self.unit_seconds = 0.
        self.last_step = 0

    def consume(self, row):
        if 'state' in row:
            self.final_units = {u['id']:u for u in row['state']['units']}
        if not row.get('decisionDiagnostics'):
            return
        if row['step'] != self.last_step+1:
            raise RuntimeError('missing or duplicate trace tick')
        self.last_step = row['step']
        units = {u['id']:u for u in row['units']}
        self.intent = {k:v for k,v in self.intent.items() if k in units}
        present = {(u['id'], p['enemy']) for u in units.values() for p in u['pairs']}
        self.pairs = {k:v for k,v in self.pairs.items() if k in present}
        self.unit_seconds += len(units)*row['dt']
        for u in units.values():
            self.counts['unit_ticks'] += 1
            old = self.intent.get(u['id'], u['c'] >= 0)
            new = True if u['c'] > .2 else False if u['c'] < -.2 else old
            self.counts['unit_intent_proxy_changes'] += u['id'] in self.intent and new != old
            self.intent[u['id']] = new
            self.counts['focus_ticks'] += u['focus'] is not None
            self.counts['focus_while_escaping_ticks'] += u['focus'] is not None and not new
            self.counts['focus_with_c_below_minus_point2_ticks'] += u['focus'] is not None and u['c'] < -.2
            any_change = False
            for p in u['pairs']:
                key = (u['id'], p['enemy'])
                changed = key in self.pairs and self.pairs[key] != p['mode']
                self.counts['pair_mode_changes'] += changed
                any_change |= changed
                self.pairs[key] = p['mode']
            self.counts['unit_ticks_with_pair_mode_change'] += any_change
            if u['feasibility'] is None:
                self.undefined[u['undefinedReason']] += 1
            else:
                c = u['feasibility']
                if not math.isfinite(c) or not -1 <= c <= 1:
                    raise RuntimeError('invalid feasibility')
                self.cosine_sum += c
                self.counts['defined_feasibility_ticks'] += 1
        for e in row['holdEvents']:
            key = (e['id'], e['enemy'])
            reason = e['reason']
            self.counts['holds_'+reason] += 1
            if reason == 'expired':
                self.counts['holds_expiring_inside_gun_reach'] += units[e['id']]['insideGunReach']
            if reason == 'disappeared':
                cause = e['releaseCause']
                if cause not in ('own_death', 'enemy_death', 'both_death', 'missing'):
                    raise RuntimeError('unclassified disappeared hold')
                self.counts['death_released_holds_'+cause] += 1
            if reason == 'started':
                if key in self.active:
                    raise RuntimeError('hold rearmed without release')
                self.active.add(key)
            else:
                if key not in self.active:
                    raise RuntimeError('hold release without start')
                self.active.remove(key)
        snapshot = {(u['id'], p['enemy']) for u in units.values() for p in u['pairs'] if p['remainingHold'] > 0}
        if snapshot != self.active:
            raise RuntimeError('hold event/snapshot mismatch')

    def finish(self):
        # Final post-step death may have no following prepare; reconcile once, without changing policy.
        for own, enemy in self.active:
            a, b = self.final_units.get(own), self.final_units.get(enemy)
            if a is None or b is None:
                cause = 'missing'
            elif not a['alive'] and not b['alive']:
                cause = 'both_death'
            elif not a['alive']:
                cause = 'own_death'
            elif not b['alive']:
                cause = 'enemy_death'
            else:
                self.counts['terminal_censored_living_holds'] += 1
                continue
            self.counts['terminal_released_holds_'+cause] += 1
        death = sum(self.counts[k] for k in ('death_released_holds_own_death', 'death_released_holds_enemy_death', 'death_released_holds_both_death',
                    'terminal_released_holds_own_death', 'terminal_released_holds_enemy_death', 'terminal_released_holds_both_death'))
        counts = dict(self.counts)
        counts['death_released_holds'] = death
        for name in ('pair_mode_changes', 'unit_intent_proxy_changes', 'focus_while_escaping_ticks', 'holds_expiring_inside_gun_reach', 'terminal_censored_living_holds'):
            counts.setdefault(name, 0)
        n = self.counts['defined_feasibility_ticks']
        return dict(counts=counts, unit_seconds=self.unit_seconds, trace_ticks=self.last_step,
                    feasibility_mean=self.cosine_sum/n if n else None, feasibility_undefined=dict(self.undefined))


def statistics95(values):
    values = list(values)
    if len(values) < 2:
        raise ValueError('at least two independent seed clusters required')
    mean = statistics.mean(values)
    sd = statistics.stdev(values)
    se = sd/math.sqrt(len(values))
    return dict(n=len(values), mean=mean, sd=sd, se=se, descriptive_normal_95=[mean-1.96*se, mean+1.96*se])


def analyze(rows, d):
    scores = collections.defaultdict(dict)
    counts = collections.defaultdict(lambda: collections.Counter())
    for row in rows:
        spec, summary = row['spec'], row['summary']
        key = (spec['arm'], spec['opponent'], spec['skeleton'])
        ident = (spec['seed'], spec['swapSides'])
        if ident in scores[key]:
            raise RuntimeError('duplicate fight')
        scores[key][ident] = summary['survivors']-summary['enemySurvivors']
        counts[key]['timeouts'] += summary['t'] >= 150-1e-9
        counts[key]['enemy_guns_alive'] += summary['artilleryAlive'][1]
    expected = {(s, swap) for s in d['seeds'] for swap in (False, True)}
    result = dict(status='DESCRIPTIVE_ONLY_NO_VERDICT', endpoints={})
    for arm, head in itertools.product(ARMS, HEADS):
        clustered = {}
        endpoint = dict(cells={}, paired_differences={})
        for cell in CELLS:
            key = (arm, head, cell)
            if set(scores[key]) != expected:
                raise RuntimeError('incomplete section-16 endpoint')
            clustered[cell] = [(scores[key][s, False]+scores[key][s, True])/2 for s in d['seeds']]
            endpoint['cells'][cell] = dict(S=statistics95(clustered[cell]), fights=200,
                timeouts=counts[key]['timeouts'], mean_enemy_guns_alive=counts[key]['enemy_guns_alive']/200)
        for a, b in itertools.combinations(CELLS, 2):
            endpoint['paired_differences'][b+'-'+a] = statistics95(y-x for x,y in zip(clustered[a], clustered[b]))
        endpoint['interaction_HF-H-F+v3'] = statistics95(hf-h-f+v3 for v3,h,f,hf in zip(*(clustered[c] for c in CELLS)))
        result['endpoints'][arm+'|'+head] = endpoint
    return result


def traced_fight(spec, out, deadline):
    """Stream native stdout to disk; never hold a full replay in memory."""
    name = f"{spec['skeleton']}_{spec['arm']}_{spec['seed']}_{int(spec['swapSides'])}"
    raw = out/'traces'/(name+'.part.jsonl')
    packed = raw.with_name(name+'.jsonl.gz')
    with raw.open('w') as stream:
        with deadline.lock:
            deadline.remaining()
            child = subprocess.Popen([str(BINARY), '--metrics'], stdin=subprocess.PIPE, stdout=stream,
                    stderr=subprocess.PIPE, text=True, start_new_session=True)
            deadline.children.add(child)
        try:
            _, stderr = child.communicate(json.dumps(request(spec))+'\n', timeout=deadline.remaining())
            deadline.remaining()
            if child.returncode:
                raise RuntimeError(stderr)
        except BaseException:
            deadline.stop()
            child.communicate(timeout=2)
            raise
        finally:
            with deadline.lock:
                deadline.children.discard(child)
    counter = TraceCounter()
    terminal = None
    with raw.open('rb') as stream, packed.open('wb') as target, gzip.GzipFile(fileobj=target, mode='wb', compresslevel=1, mtime=0) as gz:
        for line in stream:
            deadline.remaining()
            gz.write(line)
            row = json.loads(line)
            counter.consume(row)
            terminal = row
    if packed.stat().st_size >= 50*1024*1024:
        raise RuntimeError('raw trace exceeds project 50 MB per-file limit')
    raw.unlink()
    return terminal, json.loads(stderr), dict(file=str(packed.relative_to(out)), sha256=sha(packed), diagnostics=counter.finish())


def validate_result(summary, metrics, fights):
    if summary.get('controllerStatus') != 'completed' or any(summary.get('controllerFailures', [1])):
        raise RuntimeError('native controller failure: '+repr(summary))
    if metrics.get('executed_fights') != fights or any(metrics.get(k, -1) != 0 for k in ('forks', 'search_calls', 'artillery_rollouts', 'branch_steps')):
        raise RuntimeError('fight count or no-planner-work contract failed')
    for field in ('survivors', 'enemySurvivors', 't'):
        if not math.isfinite(summary[field]):
            raise RuntimeError('invalid terminal value')
    if len(summary['artilleryAlive']) != 2:
        raise RuntimeError('missing gun endpoint')


def execute(task, deadline):
    specs, out, pins = task
    check_pins(pins)
    rows = []
    if not specs[0]['trace']:
        run = deadline.run([str(BINARY), '--metrics'], json.dumps([request(s) for s in specs])+'\n', maximum=deadline.remaining())
        if run.returncode:
            raise RuntimeError(run.stderr)
        values, metrics = json.loads(run.stdout), json.loads(run.stderr)
        if not isinstance(values, list) or len(values) != 2:
            raise RuntimeError('two orientations required')
        for spec, value in zip(specs, values):
            validate_result(value, metrics, 2)
            rows.append(dict(spec=spec, summary=value, metrics=metrics, metrics_scope='two_orientation_batch'))
    else:
        for spec in specs:
            value, metrics, trace = traced_fight(spec, out, deadline)
            validate_result(value, metrics, 1)
            rows.append(dict(spec=spec, summary=value, metrics=metrics, metrics_scope='one_trace_fight', trace=trace))
    check_pins(pins)
    return rows


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--execute', action='store_true', help='execute exactly 3,200 development fights')
    ap.add_argument('--quiet-machine-finished', action='store_true', help='caller confirms C6 timing has finished')
    ap.add_argument('--workers', type=int, default=10, choices=range(1, 11))
    ap.add_argument('--output', type=pathlib.Path, default=ROOT/'s4_attribution_development')
    args = ap.parse_args()
    d = declaration()
    pins = json.loads(PIN.read_text())
    check_pins(pins)
    if not args.execute:
        print(json.dumps(dict(status='DECLARED_NOT_RUN', fights=3200, trace_fights=80, workers=args.workers)))
        return
    if not args.quiet_machine_finished:
        raise RuntimeError('C6 quiet-machine timing must finish before attribution fights')
    out = args.output.resolve()
    if not out.is_relative_to(ROOT) or out == ROOT or out.exists():
        raise RuntimeError('fresh output under astelia_cpp required; never overwrite or resume this ledger')
    # One persistent use marker prevents a repeat with the same development ledger.
    claim = ROOT/'s4_attribution_checks/LEDGER_USED.json'
    if claim.exists():
        raise RuntimeError('development ledger already consumed; declare a fresh revision')
    source = verify_sources()
    native = admit(BINARY)
    runtime_pins = dict(pins)
    runtime_pins['build/astelia_native'] = native['binary_sha256']
    runtime_pins['build/astelia_native.build.json'] = native['manifest_sha256']
    runtime_pins.update(native['sources'])
    # No simulation has run before this atomic allocation claim.
    with claim.open('x') as stream:
        stream.write(json.dumps(dict(ledger_sha256=sha(LEDGER), output=str(out), status='claimed_before_fights'))+'\n')
    out.mkdir()
    (out/'traces').mkdir()
    write(out/'run_identity.json', dict(status='development_only', native=native, source=source,
          inputs=runtime_pins, ledger=d, workers=args.workers, time_cap_seconds=3600,
          inference='Two-orientation seed means; normal 95% descriptive intervals over 100 seeds. All six paired contrasts plus interaction.'))
    started = time.monotonic()
    deadline = Deadline(started+3600)
    pool = BoundedPool(args.workers, deadline)
    rows = []
    try:
        with gzip.open(out/'fights.jsonl.gz', 'wt', compresslevel=1) as raw:
            work = ((specs, out, runtime_pins) for specs in tasks(d))
            for completed in pool.map(execute, work):
                for row in completed:
                    raw.write(json.dumps(row, allow_nan=False)+'\n')
                    rows.append(row)
        check_pins(runtime_pins)
        report = analyze(rows, d)
        traces = [dict(spec=r['spec'], **r['trace']) for r in rows if 'trace' in r]
        if len(rows) != 3200 or len(traces) != 80:
            raise RuntimeError('fight/trace allocation mismatch')
        report.update(elapsed_seconds=time.monotonic()-started, fights=3200, trace_fights=80,
                      traces=traces, raw_fights_sha256=sha(out/'fights.jsonl.gz'),
                      claim_limit='Fixed v3 B knobs on fresh development seeds; not historical retuning attribution, v5 selection or scientific acceptance.')
        write(out/'SUMMARY.json', report)
    except BaseException as error:
        write(out/'FAILURE.json', dict(status='INCOMPLETE_NO_VERDICT', completed_fights=len(rows), error=str(error), elapsed_seconds=time.monotonic()-started))
        raise
    finally:
        pool.close()


if __name__ == '__main__':
    main()
