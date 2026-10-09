"""Paired descriptive diagnosis from existing recordings only; zero new fights."""
import runtime as r
import argparse,collections,math,time
import numpy as np
from recording import rows
from oracle import oracle
from training import forward,flat,environment
from models import initial
import torch
ROLES=('melee','ranged','artillery')

def counter():
    return dict(rows=0,opportunities=0,active_on_opportunity=0,attack_starts=0,releases=0,no_target=0,target_out_of_range=0,any_out_of_range=0,approach=0,retreat=0,stationary=0,distance_sum=0.,spread_sum=0.,spread_frames=0,alive_seconds=0.,out_of_range_seconds=0.,first_shots={},never_shot=[],chosen_targets={},deaths=[],heads={k:dict(rows=0,disagreements=0,error_sum=0.) for k in ('fire','target','move','mult','aim')},raw_heads={k:dict(rows=0,disagreements=0,error_sum=0.) for k in ('fire','target','move','mult','aim')})

def disagreements(c,actual,teacher,W,H,t):
    a,b=actual['executed'],teacher['executed'];bad=[]
    for key in c['heads']:
        if key=='aim' and b['aim'] is None:continue
        if key=='move':error=math.hypot((a['goal'][0]-b['goal'][0])/W,(a['goal'][1]-b['goal'][1])/H);different=error>.02
        elif key=='aim':error=1. if a['aim'] is None else math.hypot((a['aim'][0]-b['aim'][0])/W,(a['aim'][1]-b['aim'][1])/H);different=error>.02
        elif key=='mult':error=abs(a['multiplier']-b['multiplier']);different=error>.1
        else:error=float(a[key]!=b[key]);different=bool(error)
        v=c['heads'][key];v['rows']+=1;v['disagreements']+=int(different);v['error_sum']+=error
        if different:bad.append(key)
    if bad and 'first_command_divergence' not in c:c['first_command_divergence']=dict(t=t,id=actual['id'],heads=bad,student=a,shadow_O=b)

def in_reach(u,e):
    d=math.hypot(u[3]-e[3],u[4]-e[4])
    return u[18]<=d<=u[11] if u[2]==2 else d<=u[11]+u[9]+e[9]

def analyze(raw,request,shadow=True):
    counts={role:counter() for role in ROLES};previous={};previous_unit={};initial_ids={};own_latest={};first_state=None
    context=oracle(request) if shadow else __import__('contextlib').nullcontext(None)
    with context as label:
        for row in rows(raw):
            if row.get('stageA'):
                units={u[0]:u for u in row['units']};own=[u for u in units.values() if u[1]==0];enemy=[u for u in units.values() if u[1]==1];own_latest=units
                teachers={v['id']:v for v in (row.get('shadowLabels') or (label(row) if shadow else row['labels']))}
                groups={role:[u for u in own if ROLES[u[2]]==role] for role in ROLES}
                for role,group in groups.items():
                    if group:
                        a=np.asarray([u[3:5] for u in group]);spread=float(np.sqrt(((a-a.mean(0))**2).sum(1).mean()));counts[role]['spread_sum']+=spread;counts[role]['spread_frames']+=1
                for v in row['labels']:
                    u=units[v['id']];role=v['role'];c=counts[role];cmd=v['executed'];id=v['id'];initial_ids[id]=role
                    distances=[math.hypot(u[3]-e[3],u[4]-e[4]) for e in enemy];nearest=min(distances,default=0.)
                    anyreach=any(in_reach(u,e) for e in enemy);target=units.get(cmd['target']);targetreach=target is not None and target[1]==1 and in_reach(u,target)
                    state=next(s for s in row['own'] if s[0]==id)
                    opportunity=anyreach and u[13]<=0 and state[1]<=row['t'] and not state[7] and state[5]>=state[6] and not v['active']
                    c['rows']+=1;c['opportunities']+=opportunity;c['active_on_opportunity']+=opportunity and cmd['fire']!='hold';c['no_target']+=cmd['target']==0;c['target_out_of_range']+=not targetreach;c['any_out_of_range']+=not anyreach;c['alive_seconds']+=row['dt'];c['out_of_range_seconds']+=(not anyreach)*row['dt'];c['distance_sum']+=nearest
                    c['chosen_targets'][str(cmd['target'])]=c['chosen_targets'].get(str(cmd['target']),0)+1
                    old=previous.get(id)
                    c['attack_starts']+=bool(state[2]>0 and old is not None and old<=0);previous[id]=state[2]
                    if v['engineRelease'] and cmd['fire']!='hold' and targetreach:c['releases']+=1
                    if id in previous_unit and enemy:
                        dx=u[3]-previous_unit[id][0];dy=u[4]-previous_unit[id][1];e=min(enemy,key=lambda e:math.hypot(u[3]-e[3],u[4]-e[4]));radial=(dx*(e[3]-u[3])+dy*(e[4]-u[4]))/max(nearest,1e-9)
                        c['approach']+=radial>.01;c['retreat']+=radial<-.01;c['stationary']+=abs(radial)<=.01
                    previous_unit[id]=u[3:5]
                    disagreements(c,v,teachers[id],row['width'],row['height'],row['t'])
                    if 'raw' in v:disagreements(dict(heads=c['raw_heads']),dict(v,executed=v['raw']),teachers[id],row['width'],row['height'],row['t'])
            elif row.get('observerV1'):
                # Shot timestamps are actual damage/launch events, not release intent.
                for launch in row.get('launches',[]):
                    # Observer launch tuple documented below; source id is index 0.
                    if len(launch)>2 and launch[2]==0 and launch[0] in initial_ids:
                        c=counts[initial_ids[launch[0]]];c['first_shots'].setdefault(str(launch[0]),row['t'])
                for d in row['damage']:
                    if d['sourceTeam']==0 and d['source'] in initial_ids:
                        counts[initial_ids[d['source']]]['first_shots'].setdefault(str(d['source']),row['t'])
                    if d['died'] and d['targetTeam']==0:
                        counts[d['targetRole']]['deaths'].append(dict(t=row['t'],target=d['target'],sourceTeam=d['sourceTeam'],sourceRole=d['sourceRole'],source=d['source']))
    for role,c in counts.items():
        c['never_shot']=[id for id,r0 in initial_ids.items() if r0==role and str(id) not in c['first_shots']]
    return counts

def offline_distribution(arm,fights,split):
    from parity import load_model
    model,_=load_model(arm,torch.float32);counts={role:counter() for role in ROLES}
    for f in fights:
        state=initial(arm,[]);ids=[];cache=None;nextframe=(0,[])
        with torch.no_grad():
            for row in r.data.frames(r.A_LOCAL/f['raw_file']):
                y,state,ids,enemies,cache,nextframe,_=forward(model,row,state,ids,cache,nextframe)
                # Same four training windows; recurrent prefix is replayed in full.
                from training import selected_starts,WINDOW
                if not any(at<=int(round(row['t']/row['dt']))-1<at+WINDOW for at in selected_starts(f['frames'],4)):continue
                truth={v['id']:v for v in row['labels']}
                for i,id in enumerate(ids):
                    fire=int(y['fire'][i].argmax());target=int(y['target'][i].argmax());a=dict(id=id,executed=dict(fire=('automatic','hold','release')[fire],target=0 if not target else enemies[target-1],goal=(y['move'][i].numpy()*[row['width'],row['height']]+y['drift'][i].numpy()).tolist(),multiplier=float(y['mult'][i]),aim=(y['aim'][i].numpy()*[row['width'],row['height']]).tolist()))
                    disagreements(counts[truth[id]['role']],a,truth[id],row['width'],row['height'],row['t'])
    return {role:c['heads'] for role,c in counts.items()}

def run(include_distribution=True):
    started=time.monotonic();out=r.LOCAL/'diagnosis_v2';out.mkdir(parents=True,exist_ok=True)
    ledger=r.read(r.A_LOCAL/'OUTCOME_LEDGER.json');jobs={j['tag']:j for j in ledger['jobs']};records=[]
    for path in sorted((r.A_LOCAL/'raw').glob('outcome*_COMPLETE.json')):
        c=r.read(path);j=jobs[c['job']['tag']];raw=r.A_LOCAL/c['raw_file'];request=r.A_LOCAL/'requests'/(j['tag']+'.json')
        if c['job']!=j or c['ledger_sha256']!=r.sha(r.A_LOCAL/'OUTCOME_LEDGER.json') or r.sha(raw)!=c['raw_sha256'] or r.sha(request)!=j['request_sha256']:raise RuntimeError('Stage A raw/request identity drift')
        target=out/(j['tag']+'.json');binding=dict(raw_sha256=c['raw_sha256'],completion_sha256=r.sha(path),oracle_binary_sha256=r.sha(r.BINARY),sources=r.sources(),request_sha256=r.sha(request),ledger_sha256=r.sha(r.A_LOCAL/'OUTCOME_LEDGER.json'))
        if target.exists():
            result=r.read(target)
            if result['binding']!=binding:raise RuntimeError('diagnosis cache drift')
        else:
            result=dict(job=j,stats=c['stats'],binding=binding,roles=analyze(raw,r.read(request),shadow=j['arm']!='T'))
            r.write(target,result,exclusive=True)
        records.append(result)
    # Pair only completed matching seeds, not an assumed complete look-20 panel.
    bypair={(x['job']['pair_key'],x['job']['arm']):x for x in records};paired={a:[dict(net=x,oracle=bypair[(x['job']['pair_key'],'O')]) for x in records if x['job']['arm']==a and (x['job']['pair_key'],'O') in bypair] for a in (*r.ARMS,'N2J0')}
    distributions={}
    if include_distribution:
        environment();import parity
        parity.LOCAL=r.A_LOCAL
        index=r.read(r.A_LOCAL/'INDEX.json')
        for arm in (*r.ARMS,'N2J0'):
            path=out/(arm+'_training_distribution.json')
            binding=dict(sources=r.sources(),index_sha256=r.sha(r.A_LOCAL/'INDEX.json'),export_sha256=r.sha(r.A_LOCAL/'training'/(arm+'.weights.json')))
            if not path.exists():
                fights=[f for f in index['fights'] if f['split']=='train'];r.write(path,dict(binding=binding,counts=offline_distribution(arm,fights,'train')),exclusive=True)
            cached=r.read(path)
            if cached['binding']!=binding:raise RuntimeError('training distribution identity drift')
            distributions[arm]=cached['counts']
    payload=dict(status='DESCRIPTIVE_PARTIAL',fresh_fights=0,seconds=time.monotonic()-started,definitions=dict(opportunity='alive, any enemy in own range, cooldown <=0, energy sufficient, no guard/busy/react; physical tick count, not independent chances',attack_start='observed own prep transitions zero to positive; no zero-windup starts',first_shot='first recorded own projectile launch or outgoing damage; melee uses damage and may be censored',movement='real pre-step position displacement radial toward current nearest enemy, >0.01 pixels/tick',spread='within-role RMS radius in pixels',head_tolerances='move/aim Euclidean normalized arena error >0.02; multiplier >0.1; fire/target categorical',offline_shadow_limit='public snapshot reconstruction; longVelocity not recorded; no physical step; validate on O below'),completed_fights=len(records),records=records,paired_counts={a:len(p) for a,p in paired.items()},paired=paired,training_distribution=distributions)
    r.write(r.HERE/'STAGEB_DIAGNOSIS_COUNTS.json',payload)
    return payload
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--without-distribution',action='store_true');a=p.parse_args();run(not a.without_distribution)
