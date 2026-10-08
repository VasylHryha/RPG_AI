"""Bounded read-only v5 calibration profile. Never starts native execution."""
import cProfile
import faulthandler
import hashlib
import importlib
import json
import pathlib
import pstats
import signal
import subprocess
import sys
import time

HERE = pathlib.Path(__file__).resolve().parent
V5 = HERE.parent / 's4_shape_lab_v5'
REPO = HERE.parents[3]


def main():
    spec = REPO / 'evidence/tactical_composition_demo/SHAPE_LAB_SPEC.md'
    original = spec.read_bytes()
    pinned = subprocess.check_output(['git', 'show', 'bc8ed24:evidence/tactical_composition_demo/SHAPE_LAB_SPEC.md'], cwd=REPO)
    expected = json.loads((V5 / 'DECLARATION.json').read_text())['source_hashes'][str(spec)]
    assert hashlib.sha256(pinned).hexdigest() == expected
    profile = cProfile.Profile()
    start = time.monotonic()
    calls = {}
    outcome = None
    def stop(*args):
        raise TimeoutError('120 second diagnosis limit')
    def no_execution(*args, **kwargs):
        raise RuntimeError('READ_ONLY_BOUNDARY: calibration ready to execute; no fights allowed')
    try:
        spec.write_bytes(pinned)
        sys.path.insert(0, str(V5))
        lab = importlib.import_module('lab')
        lab.compute_attempt = no_execution
        lab.write = no_execution
        for name in ('identity', 'verified_record', 'stage_summary', 'selected_knobs'):
            fn = getattr(lab, name)
            def counted(*args, _fn=fn, _name=name, **kwargs):
                calls[_name] = calls.get(_name, 0) + 1
                return _fn(*args, **kwargs)
            setattr(lab, name, counted)
        signal.signal(signal.SIGALRM, stop)
        signal.alarm(120)
        with (HERE / 'V5_FAULTHANDLER.log').open('w') as dump:
            faulthandler.dump_traceback_later(90, file=dump)
            profile.enable()
            try:
                lab.calibrate('outcome', 50)
            except (TimeoutError, RuntimeError) as error:
                outcome = str(error)
            finally:
                profile.disable()
                faulthandler.cancel_dump_traceback_later()
                signal.alarm(0)
    finally:
        spec.write_bytes(original)
        assert spec.read_bytes() == original
    profile.dump_stats(str(HERE / 'V5_PROFILE.prof'))
    with (HERE / 'V5_PROFILE.txt').open('w') as output:
        pstats.Stats(profile, stream=output).strip_dirs().sort_stats('cumulative').print_stats(40)
    result = dict(seconds=time.monotonic()-start, boundary=outcome, calls=calls,
                  spec_restored_sha256=hashlib.sha256(original).hexdigest(), fights_started=0)
    (HERE / 'V5_DIAGNOSIS.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
