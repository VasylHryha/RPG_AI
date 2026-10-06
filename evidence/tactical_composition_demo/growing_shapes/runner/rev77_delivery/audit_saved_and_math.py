"""Read saved 7.6 records and standalone math; imports no project code."""
import gzip
import hashlib
import json
import math
from pathlib import Path
import statistics
import numpy as np

HERE=Path(__file__).resolve().parent
SAVED=HERE.parent/'rev76_fixture_run_20261006/F5.json.gz'


def audit():
    with gzip.open(SAVED,'rt') as source:receipt=json.load(source)
    wrap=lambda value:(value+math.pi)%(2*math.pi)-math.pi
    result=dict(kind='READ_ONLY_SAVED_EVIDENCE_AND_STANDALONE_MATH',
                saved_F5_sha256=hashlib.sha256(SAVED.read_bytes()).hexdigest(),starts={})
    for start,rec in receipt['starts'].items():
        pin=(0.,0.) if start=='i' else (-.5,0.)
        episodes=rec['episodes'];attempts={};placements=[]
        for event in rec['events']:
            values=event['values']
            if event['rule']=='birth_attempt' and values['birth_rule']=='B-path':
                attempts[values['request']]=event
            if event['rule']=='birth_terminal' and values['birth_rule']=='B-path' and values['outcome']=='accepted':
                attempt=attempts[values['request']]['values'];distance=math.dist(attempt['position'],pin)
                placements.append(dict(time=event['time'],id=values['id'],site=attempt['site'],a=attempt['a'],b=attempt['b'],
                    position=attempt['position'],distance_to_actual_O=distance,weight=math.exp(-distance**2)))
        bins={mode:[statistics.mean(abs(wrap(a['angle']-b['angle']))
             for episode in episodes for a,b in zip(episode['own']['decisions'][j:j+20],episode[mode]['decisions'][j:j+20]))
             for j in range(0,160,20)] for mode in ('other','lesion')}
        result['starts'][start]=dict(verdict=rec['verdict'],A=rec['A'],B=rec['B'],E=rec['E'],
            O_pin=pin,output_present_every_assay=all(row['has_output'] for episode in episodes for mode in ('own','other','lesion') for row in episode[mode]['decisions']),
            two_second_contrast_bins=bins,accepted_Bpath_placements=placements,
            distance_range=[min(p['distance_to_actual_O'] for p in placements),max(p['distance_to_actual_O'] for p in placements)])
    radius=math.sqrt(math.log(2));x=np.arange(7)*(radius-1e-6);matrix=np.zeros((6,6))
    for i in range(1,7):
        neighbors=[j for j in range(7) if j!=i and abs(x[j]-x[i])<3]
        for j in neighbors:
            coefficient=32*math.exp(-(x[j]-x[i])**2)/len(neighbors)
            matrix[i-1,i-1]-=coefficient
            if j:matrix[i-1,j-1]+=coefficient
    values,vectors=np.linalg.eig(matrix);initial=np.linalg.solve(vectors,np.ones(6))
    result['standalone_math']=dict(weight_min=8/(32*.5),radius=radius,birth_weight=math.exp(-.556**2),
        six_link_linearization=dict(recipe='clamped source; seven collinear nodes at r_s-1e-6 spacing; full strict radius3 weighted mean; no project imports',
            slowest_relaxation_seconds=float(-1/max(values.real)),
            residual_fraction={t:float((vectors@(np.exp(values*t)*initial))[-1].real) for t in (3,4,8)}),
        feedforward_six_stage_residual={t:math.exp(-t/.5)*sum((t/.5)**j/math.factorial(j) for j in range(6)) for t in (3,4)},
        interpretation='local coefficient allocation only; not engine evidence or an end-to-end settling guarantee')
    (HERE/'DESIGN_AUDIT.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    print(json.dumps(dict(status='COMPLETE',starts={k:dict(A=v['A'],B=v['B'],distance_range=v['distance_range']) for k,v in result['starts'].items()})))


if __name__=='__main__':audit()
