"""Bounded no-combat fixture estimate, never a production admission receipt.

Two metadata-selected train fights, 48 evenly spread 5-Hz ticks/fight. Replay
all public physical ticks for exact smoothed velocity and N2 state. No host,
optimizer, cached production receipt or production process gate is involved.
"""
import argparse, hashlib, time
from collections import defaultdict
import numpy as np
import torch
import runtime as r
from b2move_baseline import baseline_library, baseline_batch
from b2move_diagnose import attribution, summary,geometric_subcluster
from native_candidates import batch,unpack
from candidates import mapped_labels
from coverage import accumulate,report
from models import initial
import training

def run(test_mode):
    if not test_mode:raise ValueError('this is a bounded TEST_ONLY fixture; pass --test-mode')
    training.environment();start=time.monotonic();deadline=start+90
    index_path=r.HERE/'_local/react_on/round0/INDEX.json';index=r.read(index_path)
    from train import timing_fights
    fights=timing_fights([f for f in index['fights'] if f['split']=='train'])
    oldlib,oldidentity=baseline_library();tables={'before':{},'after':{}};details=defaultdict(list);oldmiss=defaultdict(list);subclusters=defaultdict(list);remaining=defaultdict(list);records=[];maximum=0
    model,_=training.make('N2');model.eval()
    for f in fights:
        if r.sha(f['raw_file'])!=f['raw_sha256']:raise RuntimeError('sample raw drift')
        phase=int(hashlib.sha256(f['tag'].encode()).hexdigest()[:8],16)%6
        all_ticks=list(range(phase,f['frames'],6))
        ticks={all_ticks[int(i)] for i in np.linspace(0,len(all_ticks)-1,min(48,len(all_ticks)),dtype=int)}
        context=(initial('N2',[]),[],None,(0,[]));sampled=physical=0;cache_sizes=[]
        with torch.no_grad():
            for tick,row in enumerate(r.frames(f['raw_file'])):
                if time.monotonic()>deadline:raise TimeoutError('90-second fixture limit')
                physical+=1;y,state,ids,_,cache,clock,_=training.forward(model,row,*context,state_only=True);context=(state,ids,cache,clock)
                if tick not in ticks:continue
                sampled+=1;drift=y['drift'].numpy();before=unpack(baseline_batch(row,oldlib));after=unpack(batch(row,True));maximum=max(maximum,max((len(v[1]) for v in after.values()),default=0))
                cache_sizes.append(sum(3+11*(len(a)+len(m)) for a,m in after.values())*8)
                units=sorted(row['units'],key=lambda u:u[0]);byid={u[0]:u for u in units}
                for name,banks in (('before',before),('after',after)):
                    row['_candidate_banks']=banks
                    for arm in ('N1','N1r','N2'):
                        labs=mapped_labels(row,ids,drift if arm=='N2' else None);accumulate(tables[name].setdefault(arm,{}),row,mapped=labs)
                    if name=='before':
                        for lab in mapped_labels(row,ids):
                            if lab['dodge'] or lab['move']['covered']:continue
                            source,part,space,edge,confidence=attribution(byid[lab['id']],next(v for v in row['labels'] if v['id']==lab['id']),units,row)
                            key=lab['role']+':'+source+(' + spacing' if space else '')+(' → participation band' if part else '')
                            oldmiss[key].append(lab['move']['distance'])
                            if source=='history/baseline':
                                name,confidence=geometric_subcluster(byid[lab['id']],next(v for v in row['labels'] if v['id']==lab['id']),units,row)
                                subclusters[lab['role']+':'+name].append(lab['move']['distance'])
                    else:
                        for lab in mapped_labels(row,ids):
                            if not lab['dodge'] and not lab['move']['covered']:remaining[lab['role']].append(lab['move']['distance'])
                # Distance from each actually selected O endpoint to each new family.
                for lab in row['labels']:
                    if lab.get('active'):continue
                    values=after[lab['id']][1];delta=np.linalg.norm(values[:,:2]-lab['executed']['goal'],axis=1)
                    for typ in range(18,26):
                        d=delta[values[:,9]==typ]
                        if len(d):details[lab['role']+':'+str(typ)].append(float(d.min()))
        if physical!=f['frames']:raise RuntimeError('sample prefix length drift')
        records.append(dict(tag=f['tag'],panel=f['panel'],tactic=f['tactic'],raw_sha256=f['raw_sha256'],physical_frames=physical,sampled_frames=sampled,ticks=sorted(ticks),estimated_cache_uncompressed_bytes=float(np.mean(cache_sizes)*physical),cache_estimate='equally spaced sample mean; approximate only; production512MiB cap unchanged'))
    result=dict(status='TEST_ONLY',seconds=time.monotonic()-start,index_sha256=r.sha(index_path),sources=r.sources(),baseline=oldidentity,records=records,sampling='Largest-frame train fight per panel from metadata; 48 evenly spread members of existing hash-phase 5-Hz ticks. All physical prefixes replayed; no sample-driven candidate selection.',before={a:report(c) for a,c in tables['before'].items()},after={a:report(c) for a,c in tables['after'].items()},old_uncovered_clusters={k:summary(v) for k,v in oldmiss.items()},baseline_geometric_subclusters={k:summary(v) for k,v in subclusters.items()},remaining_uncovered={k:summary(v) for k,v in remaining.items()},family_distance={k:summary(v) for k,v in details.items()},max_move_candidates=maximum,irreducible_private_input_share=None,irreducibility='Not established: O is deterministic from public prefixes; remaining misses are vocabulary approximation, not proved private-input dependence.',limits='Small fixed fixture only; no full sampled admission, performance or closed-loop claim. N2 drift is exact physical-prefix deterministic fit initialization. TEST_ONLY cannot authorize measurement/training.')
    r.write(r.HERE/'B2MOVE_SAMPLE.json',result,exclusive=True)
    print(__import__('json').dumps(dict(status=result['status'],seconds=result['seconds'],max_move_candidates=maximum,ordinary={a:{k:dict(rows=v['rows'],coverage=v['coverage'],bounded_residual_coverage=v['bounded_residual_coverage']) for k,v in table.items() if k.endswith(':move:ordinary')} for a,table in result['after'].items()})))
    return result
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--test-mode',action='store_true');run(p.parse_args().test_mode)
