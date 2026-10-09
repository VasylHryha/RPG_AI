"""Read-only production-path inference; no combat, fitting, or label feedback.

Slim round-0 records discarded raw/winner. Exact public P16 formulas can be
matched; baseline/participation attribution is geometric inference, not replay
proof of hidden intermediate commands. The baseline candidate source is HEAD.
"""
import argparse, hashlib, math, time
from collections import defaultdict
import numpy as np
import runtime as r
from native_candidates import batch, unpack

def clamp(p, row, radius=0):
    return [min(row['width']-radius,max(radius,p[0])),min(row['height']-radius,max(radius,p[1]))]

def radial(p, centre, radius, fallback=(1.,0.)):
    d=np.asarray(p)-centre;n=float(np.linalg.norm(d))
    return (np.asarray(centre)+radius*(d/n if n else np.asarray(fallback))).tolist()

def reachable(u,e,p):
    d=math.dist(p,e[3:5]);return (u[18]<=d<=u[11]) if u[2]==2 else d<=u[11]+u[9]+e[9]

def participation(p,u,enemies,row):
    if not enemies or any(reachable(u,e,p) for e in enemies):return list(p),False
    e=min(enemies,key=lambda e:(math.dist(u[3:5],e[3:5]),e[0]))
    d=math.dist(p,e[3:5]);lo=u[18] if u[2]==2 else 0.;hi=u[11] if u[2]==2 else u[11]+u[9]+e[9]
    fallback=np.asarray(u[3:5])-e[3:5];n=np.linalg.norm(fallback);fallback=fallback/n if n else (1.,0.)
    q=clamp(radial(p,e[3:5],min(hi,max(lo,d)),fallback),row,u[9])
    if not any(reachable(u,e,q) for e in enemies) and any(reachable(u,e,u[3:5]) for e in enemies):q=u[3:5]
    return q,True

def overlay(u,units,row):
    guns=[v for v in units if v[2]==2 and v[1]==0];eg=[v for v in units if v[2]==2 and v[1]==1]
    if not guns or not eg:return None,'history/baseline',False
    if u[2]==1:
        g=min(guns,key=lambda v:(math.dist(u[3:5],v[3:5]),v[0]))
        threats=[v for v in units if v[1]==1 and v[2]==1 and math.dist(g[3:5],v[3:5])<=400]
        t=min(threats,key=lambda v:(math.dist(g[3:5],v[3:5]),v[0])) if threats else None
        p=t[3:5] if t is not None else [sum(v[j] for v in eg)/len(eg) for j in (3,4)]
        if math.dist(p,g[3:5])<1e-9:p=[sum(v[j] for v in eg)/len(eg) for j in (3,4)]
        if math.dist(p,g[3:5])<1e-9:p=min(eg,key=lambda v:(math.dist(g[3:5],v[3:5]),v[0]))[3:5]
        if math.dist(p,g[3:5])<1e-9:return None,'history/baseline',False
        return clamp(radial(p,g[3:5],60),row),'escort',False
    if u[2]==2:
        enemies=[v for v in units if v[1]==1]
        def value(g):return sum(math.dist(g[3:5],v[3:5])<=40+v[9] for v in enemies)
        eg=sorted(eg,key=lambda v:(-value(v),v[7],v[0]))
        anchor=next((e for e in eg if any(reachable(g,e,g[3:5]) for g in guns)),eg[0])
        focus=next((e for e in eg if reachable(u,e,u[3:5])),None)
        e=focus if focus is not None else anchor
        p=radial(u[3:5],e[3:5],max(u[18],u[11]-12))
        shift=np.zeros(2)
        for g in guns:
            if g[0]==u[0]:continue
            d=math.dist(u[3:5],g[3:5])
            if d<60:shift+=(60-d)*((np.asarray(u[3:5])-g[3:5])/d if d else np.asarray([-1 if u[0]<g[0] else 1,0]))
        return (np.asarray(p)+shift).tolist(),'focus' if focus is not None else 'anchor',bool(np.linalg.norm(shift)>1e-9)
    return None,'history/baseline',False

def attribution(u,lab,units,row):
    enemies=[v for v in units if v[1]==1];goal=lab['executed']['goal']
    p,source,spacing=overlay(u,units,row)
    if p is not None:
        q,part=participation(p,u,enemies,row);end=clamp(q,row)
        if math.dist(end,goal)<1e-6:
            return source,part,spacing,math.dist(end,q)>1e-9,'exact public overlay endpoint match'
    nearest=min(enemies,key=lambda v:(math.dist(u[3:5],v[3:5]),v[0])) if enemies else None
    band=nearest is not None and abs(math.dist(goal,nearest[3:5])-(u[11] if u[2]==2 else u[11]+u[9]+nearest[9]))<1e-6
    edge=any(abs(goal[j]-limit)<1e-6 for j in (0,1) for limit in (0,row['width'] if j==0 else row['height']))
    return 'history/baseline',band,False,edge,'inferred baseline; intermediates absent'

def geometric_subcluster(u,lab,units,row):
    """Diagnostic compatibility only, never a policy input or causal assertion."""
    goal=lab['executed']['goal'];pos=u[3:5];enemies=[v for v in units if v[1]==1]
    if math.dist(goal,pos)<1e-6:return 'hold', 'exact endpoint match'
    vectors=[('instantaneous-velocity continuation',u[5:7]),('smoothed public-velocity continuation',row.get('longVelocity',{}).get(str(u[0]),u[5:7]))]
    candidates=[]
    for name,v in vectors:
        n=math.hypot(*v)
        if n:
            candidates.append((name,[pos[j]+200*v[j]/n for j in (0,1)]))
            candidates.append((name,[pos[j]+v[j] for j in (0,1)]))
    for e in enemies:
        v=np.asarray(e[3:5])-pos;n=np.linalg.norm(v)
        if n:candidates.append(('straight enemy approach waypoint',(np.asarray(pos)+200*v/n).tolist()))
    shift=np.zeros(2)
    for f in units:
        if f[1]!=0 or f[0]==u[0] or (u[2]==2 and f[2]!=2):continue
        delta=np.asarray(pos)-f[3:5];n=np.linalg.norm(delta)
        shift+=max(0.,60-n)*(delta/n if n else np.asarray([-1 if u[0]<f[0] else 1,0]))
    candidates.append(('local repulsion',(np.asarray(pos)+shift).tolist()))
    for name,p in candidates:
        q,_=participation(p,u,enemies,row)
        if math.dist(clamp(q,row),goal)<1e-6:return name,'geometric compatibility; provenance unrecorded'
    if abs(math.dist(goal,pos)-200)<1e-6:return '200 px history/complex-mode waypoint','v6 waypoint norm match; steering components unrecorded'
    return 'unresolved history-dependent steering','not proved private-input dependence'

def summary(values):
    a=np.asarray(values);return dict(count=len(a),mean_px=float(a.mean()),median_px=float(np.median(a)),p90_px=float(np.quantile(a,.9)),max_px=float(a.max()))

def run(limit=None):
    start=time.monotonic();index_path=r.HERE/'_local/react_on/round0/INDEX.json';index=r.read(index_path)
    fights=index['fights'][:limit] if limit else index['fights'];clusters=defaultdict(list);transforms=defaultdict(list);total=defaultdict(int);miss=defaultdict(int);examples=[];sampled=0
    from b2move_baseline import baseline_library,baseline_batch
    oldlib,baseline=baseline_library()
    sources=dict(baseline['sources'],diagnostic=r.sha(__file__))
    for at,f in enumerate(fights):
        if r.sha(f['raw_file'])!=f['raw_sha256']:raise RuntimeError('raw shard drift')
        phase=int(hashlib.sha256(f['tag'].encode()).hexdigest()[:8],16)%6
        for tick,row in enumerate(r.frames(f['raw_file'])):
            if tick%6!=phase:continue
            sampled+=1;banks=unpack(baseline_batch(row,oldlib));units=sorted(row['units'],key=lambda v:v[0]);byid={v[0]:v for v in units}
            for lab in row['labels']:
                if lab.get('active'):continue
                role=lab['role'];total[role]+=1;p=lab['executed']['goal'];pts=banks[lab['id']][1][:,:2]
                d=float(np.linalg.norm(pts-np.asarray(p),axis=1).min())
                if d<=20:continue
                miss[role]+=1;u=byid[lab['id']];source,part,space,edge,confidence=attribution(u,lab,units,row)
                name=source+(' + spacing' if space else '')+(' → participation band' if part else '')+(' → engine clamp' if edge else '')
                clusters[role+':'+name].append(d)
                for key,flag in (('participation',part),('spacing',space),('engine_clamp',edge),('public_overlay_match',source!='history/baseline')):
                    if flag:transforms[role+':'+key].append(d)
                if len(examples)<24:examples.append(dict(tag=f['tag'],tick=tick,id=u[0],role=role,component=name,distance_px=d,position=u[3:5],goal=p,confidence=confidence))
        if (at+1)%10==0:print(f'diagnosis {at+1}/{len(fights)} fights; {time.monotonic()-start:.1f}s',flush=True)
    result=dict(status='READ_ONLY_DIAGNOSIS' if not limit else 'TEST_ONLY',index_sha256=r.sha(index_path),sources=sources,fights=len(fights),sampled_frames=sampled,seconds=time.monotonic()-start,ordinary_rows=dict(total),uncovered_rows=dict(miss),clusters={k:summary(v) for k,v in clusters.items()},overlapping_transforms={k:summary(v) for k,v in transforms.items()},examples=examples,limitations='P16 overlays reconstructed only for diagnostic attribution; no label-dependent candidates. Raw/winner discarded in slim round0; baseline and participation-only attribution inferred, not causal replay proof. Baseline history includes v6 complex-mode/enemy motion; engine has no ordinary velocity smoother for command goals. No irreducible private-input movement is established: O is a deterministic public-prefix controller.')
    r.write(r.HERE/('B2MOVE_DIAGNOSIS_SAMPLE.json' if limit else 'B2MOVE_DIAGNOSIS.json'),result,exclusive=True)
    print({k:result[k] for k in ('fights','ordinary_rows','uncovered_rows','seconds')})
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--limit',type=int);run(p.parse_args().limit)
