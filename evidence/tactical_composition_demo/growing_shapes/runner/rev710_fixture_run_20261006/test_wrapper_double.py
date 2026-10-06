"""Tiny synthetic harness only: no scientific imports, worlds or entropy."""
from contextlib import redirect_stdout, nullcontext
import gzip
import json
from pathlib import Path
from datetime import datetime
from execute_once import execute_harness, measured_type, portable_clock, write, digest

OUT = Path(__file__).resolve().parent


class BrokenOutput:
    def write(self, value):
        raise BrokenPipeError('synthetic broken pipe')
    def flush(self):
        raise BrokenPipeError('synthetic broken pipe')


class SyntheticHarness:
    calls = 0

    def __init__(self, failure=False):
        self.results = {}
        self.failure = failure

    def F5(self):
        return dict(verdict='FAIL' if self.failure else 'PASS', starts={
            start: dict(verdict='PASS', A=.4, B=.5, E=[.6]*8, B_path_waiting=dict(sites={str(i):dict(eligible_checks=i,current_wait_checks=i+1) for i in range(8)}), B_out=True,
                        B_path=True, events=[dict(rule='B-path', time=800)],
                        qualification_validity=dict(whole=dict(qualification_windows=2,
                            not_qualified_invalid_pairs=1, not_qualified_invalid_pair_fraction=.5)),
                        opaque_nested_data=[start, dict(retain_every_field=True)])
            for start in ('i', 'ii')})

    def run_all(self):
        self.calls += 1
        self.results['F5'] = self.F5()
        return dict(results=self.results, not_run=['F6'] if self.failure else [],
                    stops=[dict(question='F5_failed')] if self.failure else [],
                    opaque_receipt_metadata=dict(retain=True))


def main():
    start = portable_clock()
    observations = []
    for case, fail in (('complete', False), ('failed_gate', True), ('broken_stdout', False)):
        folder = OUT / ('synthetic_' + case)
        folder.mkdir(exist_ok=False)
        h = measured_type(SyntheticHarness)(fail)
        with redirect_stdout(BrokenOutput()) if case == 'broken_stdout' else nullcontext():
            expected = execute_harness(h, folder, portable_clock)
        assert h.calls == 1
        saved = json.load(gzip.open(folder / 'HARNESS_RECEIPT.json.gz', 'rt'))
        stage = json.load(gzip.open(folder / 'F5.json.gz', 'rt'))
        assert saved == expected
        assert stage == expected['results']['F5']
        assert set(stage['starts']) == {'i', 'ii'}
        cost = json.loads((folder / 'F5_TIMING.json').read_text())
        assert cost['awake_seconds'] >= 0 and cost['elapsed_utc_seconds'] >= 0
        m = json.loads((folder / 'MEASUREMENT_RECEIPT.json').read_text())
        assert m['verdict'] == ('FIXTURES_FAIL' if fail else 'FIXTURES_PASS')
        observations.append(dict(case=case, both_starts_retained=True,
                                 whole_return_equal=True, calls=h.calls,
                                 verdict=m['verdict']))
    end = portable_clock()
    write(OUT / 'WRAPPER_SYNTHETIC_CHECK.json', dict(status='PASS',
          real_fixture_execution='NOT_RUN', observations=observations,
          wrapper_sha256=digest(OUT / 'execute_once.py'),
          start_utc=start['utc'], end_utc=end['utc'],
          awake_seconds=end['awake'] - start['awake'],
          elapsed_utc_seconds=(datetime.fromisoformat(end['utc']) -
                               datetime.fromisoformat(start['utc'])).total_seconds()))


if __name__ == '__main__':
    main()
