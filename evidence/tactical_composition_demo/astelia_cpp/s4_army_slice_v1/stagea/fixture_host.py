"""Explicit tiny development fixtures; never admits collect/train/readout jobs."""
import os
import secrets
import time
from common import ARMS, LOCAL, sha, write
from jobs import locked

RSS_BOUND_BYTES = 512 * 1024**2

class FixtureMonitor:
    fixture_only = True

    def __init__(self):
        from collect import a0
        self.ram = a0()
        self.peak = 0

    def live_memory(self, pid):
        # Repository process discovery and ps are unavailable in the sandbox.
        # Keep live RAM admission; RSS comes from this child's getrusage stream.
        self.ram.live_memory(None)
        return self.peak

    def memory_report(self, row):
        peak = row['peak_rss_bytes']
        if not 0 < peak < RSS_BOUND_BYTES:raise RuntimeError('fixture RSS exceeds bound or unavailable')
        self.peak = max(self.peak, peak)


def execute_fixture(job, seconds=120, full_detail=False):
    from collect import execute
    from common import read
    if os.environ.get('STAGEA_HOST_TEST') != '1':raise RuntimeError('fixture mode requires STAGEA_HOST_TEST=1')
    allowed = {'integration': 'host_fixture_', 'memory_fixture': 'memory_fixture_', 'sample_fixture': 'sample_fixture_'}
    prefix = allowed.get(job.get('split'))
    if prefix is None or not job['tag'].startswith(prefix) or not job['tag'][len(prefix):].isalnum():
        raise RuntimeError('fixture job required; sealed collection/outcome jobs forbidden')
    request_path = LOCAL/'requests'/(job['tag']+'.json')
    if sha(request_path) != job['request_sha256']:raise RuntimeError('fixture request drift')
    request = read(request_path)
    maximum = 150 if job['split']=='memory_fixture' else 3
    if not 0 < request['options']['duration'] <= maximum or request.get('stageA',{}).get('collect') is not True:
        raise RuntimeError('fixture duration/collection envelope')
    if not 0 < seconds <= 300:raise RuntimeError('fixture cap exceeds 300 seconds')
    with locked():
        return execute(job, time.monotonic()+seconds, FixtureMonitor(), 'FIXTURE_ONLY', memory_profile=True, full_detail=full_detail)


def sample():
    """Two fresh O fixtures through production record/validate/compact/pack/label."""
    from collect import a0, identity, disk_projection
    from data import frames, pack, labels
    identity();results=[]
    for orientation in (0,1):
        seed=secrets.randbelow(2**32-1)+1
        req=a0().request('O','regular',seed,orientation)
        req['options']['duration']=3;req['stageA']={'collect':True};req['decisionTrace']=False
        tag='sample_fixture_'+secrets.token_hex(8);path=LOCAL/'requests'/(tag+'.json')
        write(path,req,exclusive=True)
        job=dict(tag=tag,seed=seed,request_sha256=sha(path),split='sample_fixture',arm='O')
        result=execute_fixture(job)
        count=0;converted={arm:0 for arm in ARMS}
        for row in frames(LOCAL/result['raw_file']):
            count+=1
            for arm in ARMS:
                x,ids,enemies=pack(row,arm);converted[arm]+=len(labels(row,ids,enemies))
        if count!=result['frames'] or not all(converted.values()):raise RuntimeError('fixture conversion coverage')
        results.append(dict(result,converted_rows=converted))
    proof=dict(status='PASS',scope='two 3-second fresh fixtures; no sealed collection jobs or training',
               fights=results,disk_projection=disk_projection(results,180))
    write(LOCAL/('FIXTURE_SAMPLE_'+secrets.token_hex(8)+'.json'),proof,exclusive=True)
    print(__import__('json').dumps({k:v for k,v in proof.items() if k!='fights'},sort_keys=True))
    return proof
