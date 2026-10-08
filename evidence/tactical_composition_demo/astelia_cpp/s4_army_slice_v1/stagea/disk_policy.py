"""Development storage planning from the immutable A0 rev2 look-100 receipt."""
import math
from functools import lru_cache
from common import ARMY, read, sha

# The 600-fight distribution includes all arms/panels, without selecting winners.
# Censored elimination times count as the entire 150-second horizon.
LOOK_SHA256 = 'e38f85f050216d7b9db628979d5d737768de2be557c921f80c43204757244781'

@lru_cache(maxsize=1)
def length_policy():
    root = ARMY/'rev2'
    look_path = root/'A0_LOOK_100.json'
    if sha(look_path) != LOOK_SHA256:
        raise RuntimeError('A0 length-policy look receipt drift')
    look = read(look_path)
    ledger_path = root/'_local/A0_LEDGER.json'
    if sha(ledger_path) != look['ledger_sha256']:
        raise RuntimeError('A0 length-policy ledger drift')
    ledger = read(ledger_path)
    jobs = {j['tag']:j for j in ledger['jobs'] if j['stage']=='outcome' and j['index']<100}
    if (look['report']['status']!='COMPLETE' or look['report']['look']!=100 or
            len(jobs)!=600 or set(jobs)!=set(look['completion_receipts'])):
        raise RuntimeError('A0 length-policy requires all 600 look-100 fights')
    values = []; censored = 0
    for tag, digest in look['completion_receipts'].items():
        path = root/'_local/raw'/(tag+'_COMPLETE.json')
        if sha(path)!=digest:
            raise RuntimeError('A0 length-policy completion drift: '+tag)
        # A0 rev2 writes only successful COMPLETE receipts and has no status key.
        # Membership/hash in the completed look receipt proves its inclusion.
        record = read(path)
        if record['job']!=jobs[tag] or record['ledger_sha256']!=look['ledger_sha256']:
            raise RuntimeError('A0 length-policy completion identity: '+tag)
        stats = record['stats']; censor = stats['elimination_time_censored']
        if type(censor) is not bool:
            raise RuntimeError('invalid A0 censor flag')
        value = 150. if censor else stats['time_to_elimination']
        if value is None or not math.isfinite(value) or not 0<value<=150:
            raise RuntimeError('invalid A0 elimination time')
        values.append(value); censored += censor
    values.sort()
    return dict(source='A0 rev2 look-100: all arms and both panels',
                look_sha256=LOOK_SHA256,ledger_sha256=look['ledger_sha256'],fights=len(values),
                censored_fights=censored,censored_seconds=150.,quantile='nearest-rank p99',
                p99_seconds=values[math.ceil(.99*len(values))-1],max_seconds=values[-1],
                fight_length_bound_seconds=values[math.ceil(.99*len(values))-1],
                scope='storage estimate; empirical bound, not a guarantee for unseen fights')
