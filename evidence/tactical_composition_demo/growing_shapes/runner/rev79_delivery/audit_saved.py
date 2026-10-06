"""Standalone immutable-record audit; standard library only, no project imports."""
import gzip
import hashlib
import json
import math
from pathlib import Path

HERE=Path(__file__).resolve().parent
RUNNER=HERE.parent


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def audit():
    path=RUNNER/'rev77_fixture_run_20261006/F1.json.gz'
    with gzip.open(path,'rt') as source:data=json.load(source)
    result=dict(kind='STANDALONE_SAVED_RECORD_DIAGNOSTIC_NO_PROJECT_IMPORTS',F1_sha256=sha(path),configurations={})
    for name in ('F1a','F1b','F1c'):
        cfg=data['configurations'][name];counts=[0,0,0];error=0.;rates=[]
        for row in cfg['records']:
            positions=row['positions'];output=max(positions,key=int)
            roots={i for i,value in row['exposure'].items() if value['drive']}
            graphs=[{i:set() for i in positions} for _ in range(3)]
            for i,held in row['neighbors'].items():
                for j in held:
                    j=str(j);r=math.hypot(positions[i][0]-positions[j][0],positions[i][1]-positions[j][1])
                    weight=math.exp(-r*r)/len(held)
                    error=max(error,abs(weight-row['weights'][i][j]))
                    graphs[0][j].add(i)
                    if r<=math.sqrt(math.log(2)):graphs[1][j].add(i)
                    if 32*1.*math.exp(-r*r)/len(held)>=.5:graphs[2][j].add(i)
            for k,graph in enumerate(graphs):
                found=set(roots);todo=list(roots)
                while todo:
                    for i in graph[todo.pop()]:
                        if i not in found:found.add(i);todo.append(i)
                counts[k]+=output in found
            held=row['neighbors'][output]
            rates.append(max((32*math.exp(-math.dist(positions[output],positions[str(j)])**2)/len(held) for j in held),default=0.))
        result['configurations'][name]=dict(recorded_verdict=cfg['verdict'],endpoints=len(rates),full_paths=counts[0],rev77_paths=counts[1],rev79_paths=counts[2],weights_max_discrepancy=error,min_best_O_rate=min(rates),final_O_degree=len(cfg['records'][-1]['neighbors'][output]))
    result['analytic_weak_edge_upper_rates']={str(r):32*math.exp(-r*r) for r in (2.2,2.6)}
    result['F5_saved_births']={}
    for start in ('i','ii'):
        path=RUNNER/f'rev76_fixture_run_20261006/F5{start}_BIRTH_EVENTS.json'
        events=json.loads(path.read_text());pin=(0.,0.) if start=='i' else (-.5,0.);attempts={};placements=[]
        for event in events:
            value=event['values']
            if event['rule']=='birth_attempt' and value['birth_rule']=='B-path':attempts[value['request']]=event
            if event['rule']=='birth_terminal' and value['birth_rule']=='B-path' and value['outcome']=='accepted':
                attempt=attempts[value['request']]['values'];r=math.dist(attempt['position'],pin)
                placements.append(dict(time=event['time'],distance_to_actual_O=r,rate_upper_bound_n1=32*math.exp(-r*r)))
        result['F5_saved_births'][start]=dict(input_sha256=sha(path),accepted=len(placements),distance_range=[min(p['distance_to_actual_O'] for p in placements),max(p['distance_to_actual_O'] for p in placements)],maximum_n1_rate=max(p['rate_upper_bound_n1'] for p in placements),all_below_05=all(p['rate_upper_bound_n1']<.5 for p in placements),placements=placements)
    return result


if __name__=='__main__':
    result=audit();(HERE/'DESIGN_AUDIT.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({name:{k:v for k,v in row.items() if k!='placements'} for name,row in result['F5_saved_births'].items()},indent=2))
