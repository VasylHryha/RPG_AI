"""One shared token bank per frame, no oracle actions in any policy input."""
import gzip
import hashlib
import json
import math
import sqlite3
import numpy as np
from common import ARMS,LOCAL,ROLES,read,sha,sources,write
CAPS={'shells':64,'shots':64,'fields':32,'casts':32}

def frames(path):
    from recording import rows
    for x in rows(path):
        if x.get('stageA'):yield x

def pack(row,kind,with_candidates=True):
    units=sorted(row['units'],key=lambda u:u[0]);own=[u for u in units if u[1]==0];enemy=[u for u in units if u[1]==1]
    if any(sum(u[1]==side for u in units)>64 for side in (0,1)):raise ValueError('entity overflow')
    if any(len(row[k])>v for k,v in CAPS.items()):raise ValueError('threat overflow; no omitted-threat labels admitted')
    W,H=row['width'],row['height']
    if not 0<row['dt']<=.2:raise ValueError('invalid physical dt')
    hist={int(k):v for k,v in row['history'].items()};ownstate={u[0]:u[1:] for u in row['own']}
    tokens=[];indices={}
    for u in units:
        id,side,role,x,y,vx,vy,hp,maxhp,radius,speed,reach,damage,cd,cdmax,target,*counters=u
        if id>=2**24 or maxhp<=0:raise ValueError('identity/hp envelope')
        v=np.zeros(64,dtype=np.float64);v[:24]=[1,id/256,side,role==0,role==1,role==2,x/W,y/H,vx/100,vy/100,hp/maxhp,radius/100,speed/100,reach/100,damage/maxhp,cd/max(cdmax,.001),target/256,*[a/maxhp for a in counters[:7]]]
        if id in ownstate:
            guard,prep,windup,rate,energy,cost,busy,lob,splash=ownstate[id]
            v[24:31]=[(guard-row['t']),prep/max(windup,.001),windup,rate,energy/100,cost/100,busy]
            v[31]=lob;v[41]=splash
        v[19]=u[18]/100
        v[40]=row['t']/150;v[42]=row['dt']
        if kind=='N1h':v[48:64]=hist.get(id,[0]*16)
        indices[id]=len(tokens);tokens.append(v)
    for bank in CAPS:
        for item in row[bank]:
            v=np.zeros(64);v[32+list(CAPS).index(bank)]=1
            # Values are already normalized by the C++ public snapshot serializer.
            v[36:36+len(item)]=item;tokens.append(v)
    world=np.zeros(64);world[47]=1;world[36:40]=[row['t']/150,row['dt'],W/1000,H/1000];tokens.append(world)
    query=np.zeros((len(own),128));pair=row['pairModes']
    for i,u in enumerate(own):
        query[i,:48]=tokens[indices[u[0]]][:48]
        if kind=='N1h':
            query[i,48:64]=hist.get(u[0],[0]*16)
            query[i,64:128]=[float(pair.get(f'{u[0]}:{e[0]}',False)) for e in enemy]+[0]*(64-len(enemy))
    arrays=dict(tokens=np.asarray(tokens),query=query,own=np.array([indices[u[0]] for u in own]),enemy=np.array([indices[u[0]] for u in enemy]),pos=np.array([[u[3],u[4]] for u in own]).reshape(-1,2),speeds=np.array([u[10] for u in own]),assignments=np.array([u[15] for u in own]))
    if not all(np.isfinite(v).all() for v in arrays.values()):raise ValueError('nonfinite policy input')
    from candidates import pack_candidates
    if with_candidates:arrays.update(pack_candidates(row,[u[0] for u in own]))
    return arrays,[u[0] for u in own],[u[0] for u in enemy]

def labels(row,ids,enemies):
    byid={r['id']:r for r in row['labels']};out=[]
    for id in ids:
        r=byid[id];c=r['executed'];target=c['target']
        if target and target not in enemies:raise ValueError('missing label target')
        out.append(dict(move=[c['goal'][0]/row['width'],c['goal'][1]/row['height']],mult=c['multiplier'],fire=('automatic','hold','release').index(c['fire']),aim=[a/s for a,s in zip(c['aim'] or [0,0],(row['width'],row['height']))],aim_mask=c['aim'] is not None,target=0 if not target else 1+enemies.index(target),role=r['role'],ready=r['ready'],release=r['engineRelease']))
    return out

def audit(index):
    """Disk-backed exact conflicts on actual inputs, one combined record/unit.
    Physical prefixes define complete memory inputs; fixed-cap learned state
    sufficiency remains empirical. A zero collision count is not that proof.
    """
    import time
    import os
    from jobs import admitted
    from training_control import training_cap,TrainingDeadline
    from common import HERE
    cap=training_cap(HERE)
    with admitted(cap['cap_seconds']) as (absolute,monitor):
        deadline=TrainingDeadline(HERE,absolute,cap['cap_seconds'])
        db=sqlite3.connect(LOCAL/'conflicts.sqlite');db.execute('DROP TABLE IF EXISTS labels');db.execute('CREATE TABLE labels (key BLOB PRIMARY KEY, value TEXT) WITHOUT ROWID')
        counts={a:{} for a in ARMS};seen=set();seeds=set();coverage={s:{r:dict(rows=0,ready=0,aim=0,active_fire=0) for r in ROLES} for s in ('train','validation','test')}
        began=time.monotonic();sample_frames=0;checked=0;last_monitor=0
        try:
            for fight in index['fights']:
                if fight['seed'] in seeds:raise ValueError('repeated seed')
                seeds.add(fight['seed']);path=LOCAL/fight['raw_file']
                if sha(path)!=fight['raw_sha256']:raise ValueError('shard drift')
                prefix={a:b'' for a in ARMS};cached={a:None for a in ARMS};next_refresh={a:(0,[]) for a in ARMS};trajectory=hashlib.sha256();n=0
                for row in frames(path):
                    if time.monotonic()>=deadline:raise TimeoutError('audit cap reached; completed source data preserved')
                    if time.monotonic()-last_monitor>=1:monitor.live_memory(os.getpid());last_monitor=time.monotonic()
                    n+=1;trajectory.update(json.dumps({k:v for k,v in row.items() if k not in ('history','pairModes','labels','networkState','networkKind')},sort_keys=True,separators=(',',':')).encode())
                    for arm in ARMS:
                        x,ids,enemies=pack(row,arm);ys=labels(row,ids,enemies)
                        current=[u[0] for u in sorted(row['units'],key=lambda u:u[0])]
                        refresh=row['t']+1e-9>=next_refresh[arm][0] or current!=next_refresh[arm][1]
                        if refresh:cached[arm]=x['tokens'].astype(np.float32).tobytes();next_refresh[arm]=(row['t']+.2,current)
                        used=[x['query']]
                        if arm in ('N1r','N2','N2J0'):used += [x['pos'],x['speeds'],x['assignments']]
                        raw=cached[arm]+b''.join(v.astype(np.float32).tobytes() for v in used)+json.dumps([ids,enemies,row['dt']],separators=(',',':')).encode()
                        prefix[arm]=hashlib.sha256(prefix[arm]+raw).digest()
                        # Each memoryless unit sees its own fresh query, not peers' queries.
                        roots=[hashlib.sha256(cached[arm]+x['query'][i].astype(np.float32).tobytes()+json.dumps(enemies).encode()).digest() for i in range(len(ids))] if arm in ('N1','N1h') else [prefix[arm]]*len(ids)
                        batch=[]
                        for id,y,root in zip(ids,ys,roots):
                            if arm=='N1':
                                c=coverage[fight['split']][y['role']];c['rows']+=1;c['ready']+=y['ready'];c['aim']+=y['aim_mask'];c['active_fire']+=y['fire']!=1
                            key=hashlib.sha256(arm.encode()+root+str(id).encode()).digest()
                            value={k:y[k] for k in ('move','mult','target','fire')}
                            if y['aim_mask']:value['aim']=y['aim']
                            for head in value:counts[arm].setdefault(head,dict(rows=0,exact_conflicts=0))['rows']+=1
                            batch.append((key,json.dumps(value,separators=(',',':')),value))
                        if batch:
                            previous=dict(db.execute('SELECT key,value FROM labels WHERE key IN ('+','.join('?' for _ in batch)+')',[b[0] for b in batch]))
                            merged=[]
                            for key,text,value in batch:
                                old=json.loads(previous[key]) if key in previous else {}
                                for head in value:
                                    if head in old:
                                        if old[head]!=value[head]:counts[arm][head]['exact_conflicts']+=1
                                    else:old[head]=value[head]
                                # Preserve the first value of every head independently.
                                # A no-aim first occurrence cannot hide later aim conflicts.
                                merged.append((key,json.dumps(old,separators=(',',':'))))
                            db.executemany('INSERT INTO labels VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value',merged)
                    if n%100==0:db.commit()
                digest=trajectory.hexdigest()
                if not n or digest in seen:raise ValueError('empty/duplicate trajectory')
                seen.add(digest);checked+=1;sample_frames+=n
                if checked==min(20,len(index['fights'])):
                    seconds=time.monotonic()-began;remaining=sum(f['frames'] for f in index['fights'][checked:]);projection=1.2*seconds/max(1,sample_frames)*remaining
                    write(LOCAL/'AUDIT_PROJECTION.json',dict(sample_fights=checked,seconds=seconds,projected_remaining_seconds=projection))
                    if projection>deadline-time.monotonic():raise RuntimeError('audit measured remaining projection exceeds owner cap')
            db.commit()
        finally:db.close()
        blocked=[a for a in ARMS if any(c['exact_conflicts'] for c in counts[a].values())]
        missing=[f'{s}:{r}' for s in coverage for r,c in coverage[s].items() if not c['rows'] or not c['ready'] or not c['active_fire'] or (r=='artillery' and not c['aim'])]
        result=dict(sources=sources(),status='PASS' if not blocked and not missing else 'BLOCKED',counts=counts,blocked_arms=blocked,missing_coverage=missing,coverage=coverage,index_sha256=sha(LOCAL/'INDEX.json'),seconds=time.monotonic()-began,sequence_definition='complete physical-tick public prefix; no oracle state in recurrent inputs',limits='zero exact conflicts does not prove fixed-cap memory sufficiency; N1 and N1h keys use only the individual query plus actual cached bank',N1_control='N1h sees fresh self history and cached public-history bank; N1 does not')
        write(LOCAL/'DECIDABILITY.json',result);return result
