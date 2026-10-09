"""Opt-in real trained N2J0 failing-fight replay; no production parity claim."""
import os
import sys
import time
from pathlib import Path
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import HERE, LOCAL, read, sha, write
from collect import identity
from parity import evaluate
from training import environment

@pytest.mark.skipif(os.environ.get('STAGEA_HOST_TEST')!='1',reason='explicit real-host test mode')
def test_real_host_N2J0_validation_0083():
    environment()
    from parmem_recovery import checked_inference_budget
    from parity_recovery import RECOVERY, FAILED_PROOF
    checked_inference_budget();binary=identity();failure_hash=sha(FAILED_PROOF)
    fight=next(f for f in read(LOCAL/'INDEX.json')['fights'] if f['tag']=='validation_0083')
    fixed={str(p.relative_to(HERE)):sha(p) for p in (RECOVERY,FAILED_PROOF,*sorted((LOCAL/'training').glob('*')))
           if p.is_file()}
    from fixture_host import FixtureMonitor, RSS_BOUND_BYTES
    from jobs import locked
    started=time.monotonic()
    with locked():result=evaluate('N2J0',fight,fixture_monitor=FixtureMonitor())
    assert identity()==binary
    assert all(sha(HERE/n)==digest for n,digest in fixed.items())
    result.update(scope='real native binary, full failing validation fight, test mode; not an all-arm parity receipt',
                  binary=binary,failed_receipt_sha256=failure_hash,recovery_sha256=sha(RECOVERY),
                  fixed_artifact_hashes=fixed,wall_seconds=time.monotonic()-started)
    write(HERE/'HOST_PARITY_STAGEA_PARTIE.json',result,exclusive=True)
    print(__import__('json').dumps(dict(status=result['status'],float32_export=result['float32_export'],
          native_float64=result['native_float64'],frames=result['frames'],peak_rss_bytes=result['native_memory']['peak_rss_bytes']),sort_keys=True))
    assert result['status']=='PASS',result
    assert result['frames']==fight['frames'] and result['float32_export']['rows']==47963
    assert result['float32_export']['categorical_mismatches']==1
    assert 0<result['native_memory']['peak_rss_bytes']<RSS_BOUND_BYTES
