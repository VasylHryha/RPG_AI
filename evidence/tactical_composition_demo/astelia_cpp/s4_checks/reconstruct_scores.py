"""Independent read-only reconstruction from native summaries, including sampler replay."""
import sys
import pathlib
import gzip
import json
import math
import random
import statistics
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]))
from s4_development import ROOT,OUT,BOUNDS,ARMS,stats,sample,defaults,paired,write
from s4_report import key

raw={}
with gzip.open(OUT/'fights.jsonl.gz','rt') as f:
    for line in f:
        row=json.loads(line);s=row['summary'];score=s['survivors']-s['enemySurvivors']
        assert score==row['S'];raw[key(row['spec'])]=score
count=0

def reconstruct(arm,params,scores):
    global count
    for battle,value in scores.items():
        opp,seed,setting=json.loads(battle)
        values=[]
        for swap in (False,True):
            spec=dict(arm=arm,params=params,opponent=opp,seed=seed,setting=setting,swapSides=swap)
            values.append(raw[key(spec)])
        assert statistics.mean(values)==value
        count+=1

best={arm:defaults(arm) for arm in BOUNDS}
for stage in 'ABC':
    for arm in BOUNDS:
        rng=random.Random(510050+'ABC'.index(stage)*100+list(BOUNDS).index(arm))
        for round_index,entry in enumerate(json.loads((OUT/f'{stage}_{arm}_tuning.json').read_text())):
            assert entry['incumbent']==best[arm]
            reconstruct(arm,entry['incumbent'],entry['incumbent_scores'])
            assert [c['knobs'] for c in entry['candidates']]==sample(arm,best[arm],rng,round_index)
            for candidate in entry['candidates']:
                for race in candidate['races']:
                    reconstruct(arm,candidate['knobs'],race['scores'])
                    differences=paired(race['scores'],{k:entry['incumbent_scores'][k] for k in race['scores']})
                    actual=stats(differences)
                    for name in ('mean','sd','se','n'):
                        assert math.isclose(actual[name],race['gain'][name],abs_tol=1e-12)
            accepted=[c for c in entry['candidates'] if c['accepted']]
            assert len(accepted)<=1
            if accepted:best[arm]=accepted[0]['knobs']
            assert best[arm]==entry['best']
    validation=json.loads((OUT/f'{stage}_validation.json').read_text())
    assert best==validation['knobs']
    for arm in ARMS:
        for endpoint in validation['results'][arm].values():
            reconstruct(arm,best.get(arm,{}),endpoint['scores'])
            actual=stats(endpoint['scores'])
            for name in ('mean','sd','se','n'):
                assert math.isclose(actual[name],endpoint['stats'][name],abs_tol=1e-12)
write(ROOT/'s4_checks/score_reconstruction.json',dict(status='PASSED',raw_fights=len(raw),
    reconstructed_cluster_entries_including_race_prefixes=count,
    sampling_replayed=True,validation_scores_reconstructed=True,paired_gains_recomputed=True,
    new_fights=0))
print('PASSED',count,'cluster entries reconstructed; no new fights')
