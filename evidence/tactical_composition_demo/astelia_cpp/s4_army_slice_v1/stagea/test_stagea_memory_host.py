"""Host-only 150-second, 100-live-unit recorder memory regression."""
import os
import secrets
import sys
from pathlib import Path
import pytest
sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import LOCAL, sha, write
from collect import a0, execute, identity, disk_projection
from jobs import admitted

RSS_BOUND_BYTES = 512 * 1024**2

@pytest.mark.skipif(os.environ.get('STAGEA_HOST_TEST') != '1', reason='host process discovery required')
def test_full_150s_recording_peak_rss():
    identity()
    # Distinct development fixture entropy, never a training/panel request.
    seed = secrets.randbelow(2**32-1)+1
    request = a0().request('O', 'regular', seed, 0)
    request['options'].update(duration=150, width=100000, height=100000)
    # Separated armies cannot cross this gap in 150 s: all 100 identities remain
    # alive, stressing the maximum entity/label bank for every physical tick.
    for side, units in enumerate(request['labScenario']['sides']):
        for i, unit in enumerate(units):
            unit['position'] = dict(x=1000+side*98000+(i%5)*25, y=50000+(i//5)*25)
    request['stageA'] = dict(collect=True)
    request['decisionTrace'] = False
    tag = 'memory_fixture_'+secrets.token_hex(8)
    path = LOCAL/'requests'/(tag+'.json')
    write(path, request, exclusive=True)
    job = dict(tag=tag, seed=seed, request_sha256=sha(path), split='memory_fixture', arm='O')
    with admitted(300) as (deadline, monitor):
        result = execute(job, deadline, monitor, 'MEMORY_FIXTURE_ONLY', memory_profile=True)
    checks = dict(full_duration=150 <= result['stats']['t_end'] < 150.1,
                  full_frames=4500 <= result['frames'] <= 4501,
                  all_units_alive=result['stats']['own_deaths'] == 0 and result['stats']['enemy_kills'] == 0,
                  final_profile=bool(result['memory_profile']) and result['memory_profile'][-1]['final'] is True and result['memory_profile'][-1]['tick'] == result['frames'],
                  bounded_peak=0 < result['peak_rss_bytes'] < RSS_BOUND_BYTES)
    proof = dict(status='PASS' if all(checks.values()) else 'FAIL', checks=checks,
                 declared_rss_bound_bytes=RSS_BOUND_BYTES, peak_rss_bytes=result['peak_rss_bytes'],
                 frames=result['frames'], duration=result['stats']['t_end'],
                 uncompressed_bytes=result['uncompressed_bytes'], compressed_bytes=result['compressed_bytes'],
                 full_collection=disk_projection([result], 180), memory_profile=result['memory_profile'],
                 completion_sha256=sha(LOCAL/'raw'/(tag+'_COMPLETE.json')),
                 fixture='150 s; 100 living units; no recorded seeds or training', seconds=result['seconds'])
    write(LOCAL/(tag+'_RSS.json'), proof, exclusive=True)
    print(__import__('json').dumps(proof, sort_keys=True))
    assert all(checks.values()), proof
