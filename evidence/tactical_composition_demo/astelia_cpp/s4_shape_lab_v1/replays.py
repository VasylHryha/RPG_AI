"""Compact viewer-compatible picker group per drill, and one file per S10X run.
All fight choices are retained. FPS is reduced deterministically until <=8 MB.
"""
import collections
import gzip
import importlib.util
import json
import pathlib
from lab import HERE, CPP, RAW, read, write
LIMIT=8_000_000

def one(record,fps):
    frames=[];maxhp={};modes={};deaths=[];next_t=0;pending=None;last=None
    def emit(obs):
        frames.append([round(obs['t'],2),[[u[0],u[1],u[2],round(u[3]),round(u[4]),round(u[5]/maxhp[u[0]],2),u[13] if u[13] is not None else -1,modes.get(u[0]) if u[1]==0 else None] for u in obs['units']],None])
    with gzip.open(RAW/(record['tag']+'.jsonl.gz'),'rt') as f:
        for line in f:
            r=json.loads(line)
            if r.get('observerV1'):
                if r['step']==0:maxhp={u[0]:u[5] for u in r['units']}
                for d in r['damage']:
                    if d['died']:deaths.append([round(d['t'],2),d['targetTeam'],d['targetRole']])
                last=r
                if r['t']+1e-9>=next_t:
                    emit(r);next_t+=1/fps;pending=r['step']
            elif r.get('v7Telemetry'):
                for q in r['choices']:modes[q['id']]=int(q['mode']=='commit')
                if r['step']==pending:
                    for u in frames[-1][1]:
                        if u[1]==0:u[7]=modes.get(u[0])
                    frames[-1][2]=dict(goal=[[q['id'],round(q['command'][0]),round(q['command'][1]),q['command'][4],int(q['mode']=='commit')] for q in r['choices']],
                                          guns=[[g['id'],g['target'],g['targetV'],round(g['post'][0]),round(g['post'][1])] for g in r['guns']],
                                          escorts=[[e['id'],e['gun'],round(e['clipped'][0]),round(e['clipped'][1])] for e in r['escorts']])
    if frames[-1][0]!=round(last['t'],2):emit(last)
    def counts(frame):
        c=collections.Counter((u[1],u[2]) for u in frame[1]);roles=('melee','ranged','guns')
        return {f'team{t}_{roles[r]}':n for (t,r),n in c.items()}
    stats=record['stats'];s=record['summary']
    return dict(name=record['tag'],tag=record['tag'],why=str(record['meta']),win=stats['win'],timeout=stats['timeout'],S=s['survivors']-s['enemySurvivors'],
                width=1400,height=800,summary=s,start=counts(frames[0]),end=counts(frames[-1]),deaths=deaths,gun_survival=None,frames=frames)

def extract(records,path,group):
    if not records:return None
    # Build one fight at a time and abandon an oversized candidate immediately.
    # C3 has 400 fights: this avoids materializing hundreds of MB at 5 FPS.
    for fps in (5,2,1,.5,.2,.1,.05,.02,.01,.005):
        header=dict(note='shape lab development only',picker_group=group,unit_fields=['id','team','role(0 melee,1 ranged,2 gun)','x','y','hp_fraction','target','gate(1 commit,0 escape)'],
                  decision_fields=dict(goal=['id','goal_x','goal_y','target','gate'],guns=['id','target','splash_value_V','post_x','post_y'],escorts=['id','assigned_gun','escort_x','escort_y']),fps=fps)
        prefix=json.dumps(header,separators=(',',':'),allow_nan=False)[:-1].encode()+b',"fights":['
        chunks=[prefix];size=len(prefix)+2
        for index,r in enumerate(records):
            part=json.dumps(one(r,fps),separators=(',',':'),allow_nan=False).encode()
            size+=len(part)+(1 if index else 0)
            if size>LIMIT:break
            chunks.append((b',' if index else b'')+part)
        else:
            chunks.append(b']}');payload=b''.join(chunks)
            pathlib.Path(path).write_bytes(payload)
            return dict(group=group,file=pathlib.Path(path).name,bytes=len(payload),fps=fps,fights=len(records))
    raise RuntimeError('cannot fit complete picker group in 8 MB')

def unchanged_scorecard(records):
    # Import the delivered script unchanged, redirect its public RAW constant only.
    p=CPP/'s4_checks/shape_scorecard_v1/scorecard.py'
    spec=importlib.util.spec_from_file_location('stored_shape_scorecard',p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.RAW=RAW
    result=[]
    for r in records:
        x=m.fight(r['tag']);x['auxiliary_only']=True
        x['limits']='Historical scorecard assumes 50 units and 10 guns, reach +50, and uses successful shells only. Lab section-4 metrics govern.'
        result.append(x)
    return dict(source_sha256=__import__('hashlib').sha256(p.read_bytes()).hexdigest(),fights=result)
