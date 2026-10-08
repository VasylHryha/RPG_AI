"""Explicit paired D1/D2 mechanism check; never called by training or tests.

Ten to twenty independent draws per arm, matching seed/cell/placement/orientation
within each draw. This is a mechanism diagnostic, not the 50/100/200 outcome gate.
"""
import argparse
from collections import Counter,defaultdict
import hashlib
import math
from pathlib import Path
import secrets
import time
from collection import HERE, read, sha, atomic, cap
from requests_v2 import drill
from stage1_data_v2 import admit, frame_rows
from stage1_jobs import JOBS, pins, execute, job_lock, physical_budget
from stage1_native_v2 import BINARY

ABLATIONS=('K0','frozen_phase','topology_only','no_geometry_to_mode','no_mode_to_geometry','no_reset')
ARMS=('teacher','N1','N1r','N2',*(f'N2_{a}' for a in ABLATIONS))


def inventory(entropy,pairs,weights,excluded):
    if not 10<=pairs<=20:
        raise ValueError('10..20 paired draws per arm')
    rows=[]; used=set(excluded)|set(range(10000))
    # Coverage first, then repeated cell/gun strata with independently seeded
    # orientations. Reflections of a single entropy draw are never replicates.
    strata=[(c,g,o) for o in (0,1) for c in ('D1-static','D2-shellfire') for g in (1,2,10)]
    for i in range(pairs):
        cell,guns,orientation=strata[i%len(strata)]; counter=0
        while True:
            h=hashlib.sha256(f'NS1-mechanism:{entropy}:{i}:{counter}'.encode()).hexdigest(); counter+=1
            seed=int(h[:8],16)
            if seed not in used:
                break
        used.add(seed); draw='NS1-M-'+h[8:40]
        for arm in ARMS:
            kind='N2' if arm.startswith('N2_') else arm
            fight=draw+'-'+arm; request=drill(cell,guns,seed,orientation,kind,weights.get(kind),fight)
            request['ablation']=arm[3:] if arm.startswith('N2_') else 'intact'
            rows.append(dict(fight=fight,draw=draw,arm=arm,cell=cell,guns=guns,orientation=orientation,request=request))
    return dict(version='NS1-mechanism-2',entropy=entropy,pairs=pairs,arms=ARMS,rows=rows,
                pins=pins(weights),max_physical_attempts=pairs*len(ARMS),
                reading='mechanism descriptive only; formal outcome reading requires 50/100/200 independent pairs')


from stage1_metrics import metrics


def report(rows):
    lookup={(r['draw'],r['arm']):r for r in rows}; results={}
    for arm in ARMS:
        own=[r for r in rows if r['arm']==arm]; contrasts=[]
        for r in own:
            teacher=lookup[r['draw'],'teacher']
            contrasts.append(dict(draw=r['draw'],survival=teacher['survival_loss_fraction']-r['survival_loss_fraction'],
                                  offense=r['offense_kill_fraction']-teacher['offense_kill_fraction'],
                                  deaths_saved=teacher['own_gun_deaths']-r['own_gun_deaths'],kills_gained=r['enemy_kills']-teacher['enemy_kills']))
        deaths=sum(r['own_gun_deaths'] for r in own); kills=sum(r['enemy_kills'] for r in own)
        cells={}
        for cell,guns in sorted({(r['cell'],r['guns']) for r in own}):
            subset=[r for r in own if r['cell']==cell and r['guns']==guns]
            opportunities=sum(r['counts'].get('start_opportunities',0) for r in subset)
            launches=sum(r['counts'].get('launches',0) for r in subset)
            enemy_kills=sum(r['enemy_kills'] for r in subset)
            participation=launches/opportunities if opportunities else None
            cells[cell+'|'+str(guns)]=dict(fights=len(subset),launches=launches,opportunities=opportunities,
                launch_fraction=participation,enemy_kills=enemy_kills,
                reading='PRODUCTIVE' if participation is not None and participation>=.25 and enemy_kills>0 else 'REDESIGN_BEFORE_OUTCOME_OR_ES',
                responsible_role='drafter')
        results[arm]=dict(label='script' if arm=='teacher' else 'network/RRG mechanism' if arm.startswith('N2') else 'network',
                         own_deaths=deaths,enemy_kills=kills,exchange=kills/deaths if deaths else None,
                         kills_per_minute=60*kills/sum(r['seconds'] for r in own),paired_contrasts=contrasts,
                         armed_cells=cells,
                         mechanism_reading='ACTIVATES_PRODUCTIVELY' if all(r['reading']=='ACTIVATES' for r in own) and all(c['reading']=='PRODUCTIVE' for c in cells.values()) else 'MECHANISM_REVIEW_REQUIRED',
                         outcome_reading='NOT_EVALUATED: 10..20 is a mechanism sample; contract outcome looks are 50/100/200')
    contrasts={}
    for ab in ABLATIONS:
        arm='N2_'+ab; paired=[]
        for r in (r for r in rows if r['arm']==arm):
            intact=lookup[r['draw'],'N2']
            paired.append(dict(draw=r['draw'],deaths_added=r['own_gun_deaths']-intact['own_gun_deaths'],
                               kills_lost=intact['enemy_kills']-r['enemy_kills'],
                               launches_lost=intact['counts'].get('launches',0)-r['counts'].get('launches',0)))
        contrasts[ab]=dict(paired=paired,reading='OBSERVED_TASK_HARM' if sum(p['deaths_added'] for p in paired)>0 or sum(p['kills_lost'] for p in paired)>0 else 'NO_OBSERVED_TASK_HARM',
                           interpretation='descriptive at mechanism sample size; no-harm is inconclusive about use')
    direct={}
    for baseline in ('N1','N1r'):
        paired=[]
        for r in (r for r in rows if r['arm']=='N2'):
            other=lookup[r['draw'],baseline]
            ratio=lambda n,d:n/d if d else None
            phase=lambda v:ratio(v['counts'].get('phase_order_sum',0),v['counts'].get('phase_order_ticks',0))
            motion=lambda v:ratio(v['counts'].get('command_realized_dot_sum',0),v['counts'].get('command_realized_pairs',0))
            delta=lambda a,b:a-b if a is not None and b is not None else None
            paired.append(dict(draw=r['draw'],deaths= r['own_gun_deaths']-other['own_gun_deaths'],
                kills=r['enemy_kills']-other['enemy_kills'],launches=r['counts'].get('launches',0)-other['counts'].get('launches',0),
                launch_opportunity_fraction=delta(r['launch_opportunity_fraction'],other['launch_opportunity_fraction']),
                phase_order=delta(phase(r),phase(other)),command_realized_motion=delta(motion(r),motion(other))))
        direct['N2-minus-'+baseline]=dict(paired=paired,reading='DESCRIPTIVE',
            cause_limits='stateless imitation teacher, seed noise and fixed untrained J=0.5 motion prior; no RRG mechanism conclusion')
    return dict(arms=results,all_fights=rows,within_n2=contrasts,direct_network_contrasts=direct,ablation_scope='observed harm or no observed harm is descriptive; neither alone proves H-M/use/non-use',
                formal_outcome_reading='NOT_EVALUATED',hierarchy='NOT_TESTED')


def recorded_kicks(path,weights):
    import torch
    from models import Policy
    from stage1_arithmetic import encode,matched_kicks
    model=Policy('N2'); payload=read(weights)
    model.load_state_dict({k:torch.tensor(v['values'],dtype=torch.float64).reshape(v['shape']) for k,v in payload['parameters'].items()})
    for f in frame_rows(path):
        if f.get('terminal'):
            break
        if len(f['gun_ids'])<2:
            continue
        ids=f['gun_ids']; units={u['id']:u for u in f['joint']['units']}; phases=dict(f['phase_state'])
        pos=torch.tensor([[units[i]['x'],units[i]['y']] for i in ids],dtype=torch.float64)
        theta=torch.tensor([phases[i] for i in ids],dtype=torch.float64)
        x=torch.tensor([encode({**f['joint'],'self':i})[0] for i in ids],dtype=torch.float64)
        law=model.law; mapped=(law[0].sigmoid(),law[1].sigmoid(),law[2].sigmoid(),2*law[3].sigmoid(),2*law[4].tanh(),.25*law[5].sigmoid())
        geometry=pos*0; geometry[1,0]=20
        phase=theta*0; phase[1]=.25
        with torch.no_grad():
            result=matched_kicks(theta,pos,ids,mapped,torch.tanh(model.force(x)).squeeze(-1),x[:,10]*200,geometry,phase,f['joint']['dt'])
        return dict(fight=f['fight'],tick=f['tick'],geometry_kick_px=geometry.tolist(),phase_kick_rad=phase.tolist(),**result)
    return dict(status='NOT_RUN',reason='no multi-gun context')


def run(pairs):
    result=read(HERE/'STAGE1_V2_RESULTS.json')
    if result['status']!='TRAINED_BC' or result['export_parity']['status']!='PASS':
        raise RuntimeError('trained BC exports and parity required')
    weights={k:HERE/'_local/stage1_v2'/(k+'.weights.json') for k in ('N1','N1r','N2')}
    for k,p in weights.items():
        if sha(p)!=result['models'][k]['export_sha256']:
            raise RuntimeError('selected stage-1 export drift')
    directory=JOBS/'mechanism'; directory.mkdir(parents=True,exist_ok=True); path=directory/'INVENTORY.json'
    excluded=[r['seed'] for r in admit()['rows']]
    for p in JOBS.glob('dagger_r*/INVENTORY.json'):
        excluded += [r['request']['seed'] for r in read(p)['rows']]
    if path.exists():
        inv=read(path)
        if inv!=inventory(inv['entropy'],pairs,weights,excluded):
            raise RuntimeError('mechanism sealed inventory/pin drift')
    else:
        inv=inventory(secrets.token_hex(32),pairs,weights,excluded); atomic(path,inv)
    deadline=physical_budget(directory); values=[]
    for row in inv['rows']:
        if pins(weights)!=inv['pins']:
            raise RuntimeError('mechanism admission drift')
        execute(directory,row,sha(path),BINARY,pairs*len(ARMS),deadline)
        if row['arm']!='teacher':
            from stage1_logged_parity import verify
            kind='N2' if row['arm'].startswith('N2_') else row['arm']
            check=verify(directory/(row['fight']+'.jsonl'),weights[kind],row['request']['ablation'])
            parity_path=directory/(row['fight']+'.parity.json')
            if parity_path.exists() and read(parity_path)!=check:
                raise RuntimeError('own-Host parity evidence drift')
            if not parity_path.exists():
                atomic(parity_path,check)
        values.append(metrics(directory/(row['fight']+'.jsonl'),row))
    contexts=[recorded_kicks(directory/(r['fight']+'.jsonl'),weights['N2']) for r in inv['rows'] if r['arm']=='N2' and r['guns']>1]
    value=dict(status='MECHANISM_ONLY',inventory_sha256=sha(path),pairs_per_arm=pairs,matched_recorded_context_kicks=contexts,**report(values))
    atomic(HERE/'STAGE1_V2_MECHANISM_RESULTS.json',value)
    return value


if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--pairs',type=int,default=12); a=p.parse_args()
    with job_lock('mechanism'):
        run(a.pairs)
