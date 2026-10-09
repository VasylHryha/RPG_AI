"""TEST_ONLY: compare exact temporal field coding on one real cached window."""
import json,time,zlib,numpy as np
from pathlib import Path
import runtime as r
import prepared_cache as pc

def run():
    started=time.monotonic();root=r.HERE/'_local/b2prof/cache_v9'
    marker=r.read(root/'PREPARED_CACHE.json');index=r.read(r.LOCAL/'round0/INDEX.json')
    fight=max((f for f in index['fights'] if f['split']=='train' and f['panel']=='C3'),key=lambda f:(f['frames'],f['tag']))
    pc.META_HASHES={q['meta_file']:q['meta_sha256'] for q in marker['records']}
    meta=r.read(next(root/q['meta_file'] for q in marker['records'] if q['tag']==fight['tag']))
    # Source identity changed only by this diagnostic file, excluded from cache identity.
    lookup={t:(rec,i) for rec in meta['chunks'] for i,t in enumerate(rec['ticks'])}
    values=[]
    for t in range(90):
        rec,i=lookup[t];a,_=pc.load(root,rec,i);values.append(a['move_numeric'][:,:,4].copy())
    out={}
    for order in (1,2,3,4,5):
        previous=[];pieces=[]
        for value in values:
            bits=value.view(np.uint32);history=previous[:order];degree=len(history)
            if degree:
                import math
                predicted=np.zeros_like(bits)
                for i,old in enumerate(history):
                    term=old*np.uint32(math.comb(degree,i+1))
                    predicted=predicted+term if i%2==0 else predicted-term
                residual=bits-predicted
                residual=(residual<<1)^(np.zeros_like(residual)-(residual>>31))
            else:residual=bits
            previous=[bits]+previous[:order-1]
            pieces.append(residual.ravel().view(np.uint8).reshape(-1,4).T.copy().tobytes())
        data=b''.join(pieces);out[str(order)]={'encoded_bytes':len(data),'compressed_bytes':len(zlib.compress(data))}
    report=dict(status='TEST_ONLY',fight=fight['tag'],ticks=90,seconds=time.monotonic()-started,orders=out)
    r.write(r.HERE/'B2PROF_FIELD_DIAGNOSTIC.json',report,exclusive=True);print(json.dumps(report))
if __name__=='__main__':run()
