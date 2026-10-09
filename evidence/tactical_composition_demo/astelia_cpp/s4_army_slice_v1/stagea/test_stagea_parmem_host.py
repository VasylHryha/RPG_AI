"""Opt-in real host: 150 s N2 validation fixture and longest held-out replay."""
import os
import secrets
import sys
import time
from pathlib import Path
import pytest
sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import HERE, LOCAL, read, sha, write
from collect import a0, identity
from data import frames
from fixture_host import FixtureMonitor, execute_fixture
from parity import compare, load_model, replay, sequence
import torch
from training import environment

RSS_BOUND_BYTES = 512 * 1024**2
pytestmark = pytest.mark.skipif(os.environ.get('STAGEA_HOST_TEST') != '1', reason='opt-in real binary fixtures')


def test_full_150s_N2_validation_replay_peak_rss():
    environment(); host = identity(); started = time.monotonic()
    model, weights = load_model('N2', torch.float64)
    export_path = LOCAL/'training/N2.weights.json'; export_hash = sha(export_path)
    # Fresh validation fixture, outside sealed training/panel seeds. No existing
    # held-out fight survived 150 s; separated armies enforce the full envelope.
    seed = secrets.randbelow(2**32-1)+1
    request = a0().request('O', 'regular', seed, 0)
    request['options'].update(duration=150, width=100000, height=100000)
    for side, units in enumerate(request['labScenario']['sides']):
        for i, unit in enumerate(units):
            unit['position'] = dict(x=1000+side*98000+(i%5)*25, y=50000+(i//5)*25)
    request['stageA'] = dict(collect=True); request['decisionTrace'] = False
    tag = 'memory_fixture_'+secrets.token_hex(8); path = LOCAL/'requests'/(tag+'.json')
    write(path, request, exclusive=True)
    job = dict(tag=tag, seed=seed, request_sha256=sha(path), split='memory_fixture', arm='O')
    recorded = execute_fixture(job, seconds=300)
    raw = LOCAL/recorded['raw_file']; profile = {}
    from jobs import locked
    with locked():
        native = replay(weights, frames(raw), timeout=300, profile=profile, fixture_monitor=FixtureMonitor())
    expected = sequence(model, frames(raw)); parity = compare(expected, native)
    checks = dict(full_duration=150 <= recorded['stats']['t_end'] < 150.1,
                  full_frames=4500 <= profile['frames'] <= 4501,
                  replay_matches_recording=profile['frames'] == recorded['frames'],
                  all_units_present=all(len(row)==50 for row in native),
                  bounded_peak=0 < profile['peak_rss_bytes'] < RSS_BOUND_BYTES,
                  numeric_parity=parity['max_abs_error'] < 1e-8 and parity['categorical_mismatches']==0,
                  export_unchanged=sha(export_path)==export_hash)
    proof = dict(status='PASS' if all(checks.values()) else 'FAIL', checks=checks,
                 declared_rss_bound_bytes=RSS_BOUND_BYTES, **profile, parity=parity,
                 duration=recorded['stats']['t_end'], export_sha256=export_hash,
                 binary_sha256=host['binary_sha256'], raw_sha256=sha(raw),
                 scope='150 s real-host validation fixture; 100 living units; trained N2; fresh fixture entropy; no fitting',
                 seconds=time.monotonic()-started)
    write(HERE/'HOST_REPLAY_STAGEA_PARMEM.json', proof, exclusive=True)
    print(__import__('json').dumps({k:v for k,v in proof.items() if k!='memory_profile'}, sort_keys=True))
    assert all(checks.values()), proof


def test_N2_longest_actual_heldout_validation_replay():
    environment(); host = identity(); started = time.monotonic()
    index = read(LOCAL/'INDEX.json')
    fight = max((f for f in index['fights'] if f['split']=='validation'), key=lambda f:f['frames'])
    raw = LOCAL/fight['raw_file']; assert sha(raw)==fight['raw_sha256']
    model, weights = load_model('N2', torch.float64); profile = {}
    from jobs import locked
    with locked():
        native = replay(weights, frames(raw), timeout=300, profile=profile, fixture_monitor=FixtureMonitor())
    parity = compare(sequence(model, frames(raw)), native)
    proof = dict(status='PASS', fight=fight['tag'], raw_sha256=sha(raw), binary_sha256=host['binary_sha256'],
                 **profile, parity=parity, seconds=time.monotonic()-started, declared_rss_bound_bytes=RSS_BOUND_BYTES)
    assert len(native)==fight['frames'] and 0 < profile['peak_rss_bytes'] < RSS_BOUND_BYTES
    assert parity['max_abs_error'] < 1e-8 and parity['categorical_mismatches']==0
    write(HERE/'HOST_HELDOUT_STAGEA_PARMEM.json', proof, exclusive=True)
    print(__import__('json').dumps({k:v for k,v in proof.items() if k!='memory_profile'}, sort_keys=True))
