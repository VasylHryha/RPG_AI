"""Measurement-only wrapper. Whole calls only; scientific Harness.run_all unchanged.

No scientific imports occur until main verifies explicit owner approval.
F1a-c and F5i/ii have no returned execution clocks, so their individual wall
costs are explicitly unavailable. Complete nested results remain persisted.
"""
import gzip
import hashlib
import json
import math
import os
from datetime import datetime, timezone
from pathlib import Path
import sys
import time

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[4]
PIN_DIGEST = '7a63d15064df745bfa63071473e02ffcb327901d6210c8310f5b5f8c3a330bce'
REVIEW = 'evidence/tactical_composition_demo/growing_shapes_review_claude/REV75_FIXTURE_READINESS_CONFIRMED.md'
APPROVAL = 'docs/decisions/0031-owner-run-approval-policy.md'
PROVENANCE = 'Assisted-by: Codex:GPT-6'
OWNER_APPROVAL = 'you can run tests now; 2026-10-06 16:4x Europe/Kiev, reiterated explicitly in this task despite ~91-minute estimate'
ORDER = ('N1', 'F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8', 'F9')


def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def write(path, value):
    with Path(path).open('x') as stream:
        json.dump(value, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write('\n')


def persist(path, value):
    """Stream every returned field, without pruning or a giant encoded buffer."""
    path = Path(path)
    with gzip.open(path, 'xt', encoding='utf-8') as stream:
        for block in json.JSONEncoder(allow_nan=False, separators=(',', ':')).iterencode(value):
            stream.write(block)
        stream.write('\n')
    return dict(path=path.name, bytes=path.stat().st_size, sha256=digest(path),
                delivery_eligible=path.stat().st_size < 50_000_000)


def machine_load():
    # Optional load observation must never invalidate a returned fixture result.
    try:
        return dict(load_average_1_5_15=list(os.getloadavg()), logical_cpus=os.cpu_count(),
                    process_inventory=None,
                    qualification='Concurrent C6 timing benchmark reported by owner; shared machine, not isolated timing. Per-process inventory unavailable: sandbox denies ps from Python.')
    except OSError as error:
        return dict(load_average_1_5_15=None, logical_cpus=os.cpu_count(),
                    observation_error=type(error).__name__ + ': ' + str(error),
                    qualification='Shared machine; concurrent C6 benchmark reported by owner.')


def portable_clock():
    return dict(awake=time.monotonic(), continuous=time.monotonic(),
                utc=datetime.now(timezone.utc).isoformat())


def timing(a, b):
    return dict(start_clock=a, end_clock=b, start_utc=a['utc'], end_utc=b['utc'],
                awake_seconds=b['awake'] - a['awake'],
                continuous_seconds=b['continuous'] - a['continuous'],
                elapsed_utc_seconds=(datetime.fromisoformat(b['utc']) - datetime.fromisoformat(a['utc'])).total_seconds(),
                scope='whole method call; excludes persistence after return')


def measured_type(base):
    class Measured(base):
        def __getattribute__(self, name):
            method = super().__getattribute__(name)
            if name not in ORDER + ('F1d',):
                return method

            def whole_call(*args, **kwargs):
                a = self.measure_clock()
                print(a['utc'], 'START', name, flush=True)
                try:
                    row = method(*args, **kwargs)
                except BaseException as error:
                    cost = timing(a, self.measure_clock())
                    cost['exception'] = type(error).__name__ + ': ' + str(error)
                    self.measure_costs[name] = cost
                    write(self.measure_out / (name + '_TIMING.json'), cost)
                    raise
                cost = timing(a, self.measure_clock())
                self.measure_costs[name] = cost
                cost['machine_load_after_call'] = machine_load()
                write(self.measure_out / (name + '_TIMING.json'), cost)
                # Both F5 starts are persisted together as returned by the harness.
                self.measure_artifacts[name] = persist(self.measure_out / (name + '.json.gz'), row)
                print(cost['end_utc'], 'END', name, flush=True)
                return row

            return whole_call
    return Measured


def execute_harness(harness, out, clock):
    harness.measure_out = Path(out)
    harness.measure_clock = clock
    harness.measure_costs = {}
    harness.measure_artifacts = {}
    a = clock()
    try:
        receipt = harness.run_all()
    except BaseException as error:
        persist(Path(out) / 'INTERRUPTED_RESULTS.json.gz', harness.results)
        write(Path(out) / 'INTERRUPTION.json', dict(verdict='INVALID',
              error=type(error).__name__ + ': ' + str(error), total=timing(a, clock()),
              original_harness_receipt_returned=False))
        raise
    b = clock()
    # Preserve the exact original receipt, including all nested records.
    artifact = persist(Path(out) / 'HARNESS_RECEIPT.json.gz', receipt)
    rows = receipt['results']
    verdict = ('INVALID' if any(r['verdict'] == 'INVALID' for r in rows.values()) else
               'FIXTURES_FAIL' if any(r['verdict'] == 'FAIL' for r in rows.values()) else
               'INVALID' if receipt['not_run'] else 'FIXTURES_PASS')
    write(Path(out) / 'MEASUREMENT_RECEIPT.json', dict(verdict=verdict,
          harness_receipt=artifact, timings=harness.measure_costs,
          artifacts=harness.measure_artifacts, total=timing(a, b), provenance=PROVENANCE,
          individual_nested_execution_costs=None,
          nested_cost_reason='Harness returns no individual execution clocks for F1a-c or F5i/ii; enclosing whole calls are timed. F1 includes F1d; do not sum both.',
          wrapper_sha256=digest(__file__)))
    return receipt


def main():
    estimate = json.loads((OUT / 'DURATION_ESTIMATE.json').read_text())
    seconds = estimate['scheduling_allowance_seconds']
    if not math.isfinite(seconds) or seconds <= 0:
        raise SystemExit('STOP: invalid scheduling estimate')
    synthetic = json.loads((OUT / 'WRAPPER_SYNTHETIC_CHECK.json').read_text())
    if synthetic['status'] != 'PASS' or synthetic['wrapper_sha256'] != digest(__file__):
        raise SystemExit('STOP: passing synthetic persistence test for this wrapper missing')
    authorization = json.loads((OUT / 'OWNER_EXECUTION_AUTHORIZATION.json').read_text())
    if authorization['approved_over_one_hour'] is not True or authorization['owner_instruction'] != OWNER_APPROVAL:
        raise SystemExit('STOP: explicit long-run approval missing')
    if (OUT / 'PRE_EXECUTION_SEED_INVENTORY.json').exists():
        raise SystemExit('STOP: existing execution receipt; no rerun')
    sys.path.insert(0, str(ROOT))
    from evidence.tactical_composition_demo.growing_shapes.runner.rev7_identity import assert_inputs, PIN
    from evidence.tactical_composition_demo.growing_shapes.runner.rev7_execution import Execution
    from evidence.tactical_composition_demo.growing_shapes.runner.rev7_fixtures import Harness
    from evidence.tactical_composition_demo.growing_shapes.runner.rev7_verify import clocks
    if digest(PIN) != PIN_DIGEST:
        raise SystemExit('STOP: execution pin mismatch')
    identity = assert_inputs()
    write(OUT / 'EXECUTION_PREFLIGHT.json', identity)
    write(OUT / 'EXECUTION_CLAIM.json', dict(pin_sha256=PIN_DIGEST,
          approval_reference=APPROVAL, integration_review=REVIEW, execution_once=True,
          kind='MEASUREMENT_TOOL_RERUN', first_attempt_F5_persisted_or_observed=False,
          provenance=PROVENANCE, owner_explicit_approval=authorization,
          estimate_seconds=estimate['estimate_seconds'], scheduling_allowance_seconds=seconds,
          machine_load=machine_load()))
    grant = Execution(engines_ready_reviewed=True, integration_tested_reviewed=True,
                      approval_reference=APPROVAL, integration_review=str(ROOT / REVIEW),
                      receipt_dir=str(OUT))
    harness = measured_type(Harness)(grant, backend='native')
    execute_harness(harness, OUT, clocks)
    assert assert_inputs()['pin_sha256'] == PIN_DIGEST


if __name__ == '__main__':
    main()
