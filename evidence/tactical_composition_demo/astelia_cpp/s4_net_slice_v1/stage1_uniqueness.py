"""Read-only trajectory fingerprints. Never repair or rewrite raw evidence."""
from collections import defaultdict
import hashlib
import json
from pathlib import Path

THRESHOLD=.90
FIRST_K=30


def canonical(value):
    if isinstance(value,dict):
        return {k:canonical(v) for k,v in value.items() if k not in ('fight','seed')}
    if isinstance(value,list):
        return [canonical(v) for v in value]
    return value


def state_hash(path,k=FIRST_K):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for i,line in enumerate(f):
            if i>=k:
                break
            frame=json.loads(line)
            if frame.get('terminal'):
                break
            h.update(json.dumps(canonical(frame.get('joint')),sort_keys=True,separators=(',',':'),allow_nan=False).encode())
    return h.hexdigest()


def gate(rows):
    strata=defaultdict(list)
    for row in rows:
        strata['|'.join(str(row[k]) for k in ('cell','guns','orientation'))].append(row)
    result={}
    for key,values in strata.items():
        fingerprints={(v['records'],v['decision_rows'],v['first_k_state_sha256']) for v in values}
        fraction=len(fingerprints)/len(values)
        result[key]=dict(draws=len(values),distinct=len(fingerprints),fraction=fraction,
                         status='PASS' if fraction>=THRESHOLD else 'FAIL',
                         sample_limit='singleton cannot establish a within-stratum uniqueness rate' if len(values)==1 else None)
    return dict(status='PASS' if result and all(v['status']=='PASS' for v in result.values()) else 'FAIL',
                threshold=THRESHOLD,first_k=FIRST_K,strata=result)


def converted_hash(arrays):
    h=hashlib.sha256()
    for key in ('x','labels','pos','launch'):
        a=arrays[key]; h.update(key.encode()); h.update(str((a.shape,str(a.dtype))).encode())
        # Bounded chunks rather than a second whole-fight copy.
        for start in range(0,len(a),32):
            h.update(a[start:start+32].tobytes(order='C'))
    return h.hexdigest()
