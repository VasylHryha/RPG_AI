"""Candidate enumeration; fixed ordering, no policy selection or oracle inputs."""
import math
import numpy as np
from tools import (add,sub,mul,norm,direction,lead,flight_time,range_project,
                   splash_coverage,best_splash,cluster_centres,dodge_spot,
                   behind_friend,threat_estimate)
MAX_AIM=194
MAX_MOVE=996
FEATURES=16
AIM_OFFSET=12. # px per axis
MOVE_OFFSET=24. # px per axis
TOLERANCE=20. # Euclidean pixels, same for all roles/head types

# Feature type indices: aim direct/lead/cluster/splash; movement hold/band/behind/
# approach/flank/retreat/dodge. No nearest/best threat chooser is hidden here.
def validate_frame(row,id):
    from tools import finite
    finite(row['width'],row['height'])
    if row['width']<=0 or row['height']<=0:raise ValueError('candidate arena')
    sizes={'units':23,'own':10,'shells':9,'shots':7,'casts':7,'fields':5}
    caps={'shells':64,'shots':64,'casts':32,'fields':32}
    for name,width in sizes.items():
        for v in row[name]:
            if len(v)!=width:raise ValueError('candidate '+name+' schema')
            finite(v)
        if name in caps and len(row[name])>caps[name]:raise ValueError('candidate threat overflow')
    units=row['units'];ids=[u[0] for u in units];owns=[u[0] for u in units if u[1]==0]
    if len(set(ids))!=len(ids) or any(u[0]<=0 or u[0]!=int(u[0]) or u[0]>=2**24 or u[1] not in (0,1) or u[2] not in (0,1,2) or u[7]<=0 or u[8]<=0 or u[9]<0 or u[10]<0 or u[12]<0 or not 0<=u[18]<=u[11] for u in units):raise ValueError('candidate units envelope')
    if len(owns)>64 or len(units)-len(owns)>64 or id not in owns:raise ValueError('candidate entity envelope')
    ownids=[v[0] for v in row['own']]
    if sorted(ownids)!=sorted(owns):raise ValueError('candidate own-state coverage')
    actor=next(u for u in units if u[0]==id)
    if 2*actor[9]>min(row['width'],row['height']):raise ValueError('candidate body box')
    if any(s[3]<0 or s[2]<0 or s[4]<=0 or s[8]<=0 or s[9]<0 for s in row['own']):raise ValueError('candidate own-state physics')

def bank(row,id,allow_missing_aim=False):
    validate_frame(row,id)
    units=sorted(row['units'],key=lambda u:u[0]);own=next(u for u in units if u[0]==id and u[1]==0)
    enemies=[u for u in units if u[1]==1];friends=[u for u in units if u[1]==0 and u[0]!=id]
    state=next(v for v in row['own'] if v[0]==id)
    W,H=row['width'],row['height'];pos=tuple(own[3:5]);lo,hi=own[18],own[11]
    box=(own[9],own[9],W-own[9],H-own[9]);landing=(0.,0.,W,H)
    windup=max(0.,state[3]-state[2])/max(1e-6,state[4]);lob=state[8]*100;splash=state[9]*100
    enemypos=[tuple(u[3:5]) for u in enemies]
    predictions=[lead(tuple(u[3:5]),tuple(u[5:7]),flight_time(pos,u[3:5],lob,windup)) for u in enemies] if own[2]==2 else enemypos
    threat=[(tuple(u[3:5]),tuple(u[5:7]),u[12],max(.001,u[14]),u[11]) for u in enemies]
    centre=(sum(p[0] for p in enemypos)/len(enemypos),sum(p[1] for p in enemypos)/len(enemypos)) if enemypos else pos
    aims=[];moves=[]
    def append(out,p,typ):
        if p is None:return
        # Geometry normalized once at every role/level: 100 px, 100 damage/s.
        f=[0.]*FEATURES;f[typ]=1.;f[11:14]=[(p[0]-pos[0])/100,(p[1]-pos[1])/100,norm(sub(p,pos))/100]
        out.append((tuple(p),f,typ))
    def aim(p,typ):append(aims,range_project(p,pos,lo,hi,landing),typ)
    def move(p,typ):append(moves,(min(box[2],max(box[0],p[0])),min(box[3],max(box[1],p[1]))) if p is not None else None,typ)
    aim(add(pos,(lo,0)),0) # legal fallback, not a fire recommendation
    for p,q in zip(enemypos,predictions):aim(p,0);aim(q,1)
    if own[2]==2:
        for p in cluster_centres(predictions,2*splash):aim(p,2)
        append(aims,best_splash(predictions,splash,pos,lo,hi,landing),3)
    move(pos,4)
    for u in enemies:
        p=tuple(u[3:5]);d=direction(sub(pos,p));n=(-d[1],d[0]);mid=(lo+hi)/2
        append(moves,range_project(pos,p,lo,hi,box),5) # hold nearest legal band
        append(moves,range_project(add(p,mul(d,hi)),p,lo,hi,box),7) # approach to outer edge
        for side in (-1,1):append(moves,range_project(add(p,mul(add(mul(d,math.cos(math.pi/4)),mul(n,side*math.sin(math.pi/4))),mid)),p,lo,hi,box),8)
        move(add(pos,mul(d,max(60.,own[10]*.5))),9)
    for u in friends:append(moves,behind_friend(u[3:5],centre,u[9]+own[9]+12,centre,lo,hi,box),6)
    for u in enemies:
        for side in (-1,1):move(dodge_spot(pos,u[3:5],u[5:7],.5,max(60.,own[10]*.5),side),10)
    hazards=[]
    for sh in row['shells']:hazards.append(((sh[2]*W,sh[3]*H),(0.,0.),max(0.,sh[4]),sh[5]*100+own[9]+12))
    for sh in row['shots']:hazards.append(((sh[0]*W,sh[1]*H),(sh[2]*sh[5]*100,sh[3]*sh[5]*100),min(.5,sh[6]/max(sh[5],1e-6)),max(60.,own[10]*.5)))
    for sh in row['casts']:hazards.append(((sh[2]*W,sh[3]*H),(0.,0.),max(0.,sh[5]),sh[6]*100+own[9]+12))
    for sh in row['fields']:hazards.append(((sh[0]*W,sh[1]*H),(0.,0.),max(0.,sh[3]),sh[2]*100+own[9]+12))
    for p,v,t,clearance in hazards:
        for side in (-1,1):move(dodge_spot(pos,p,v,t,clearance,side),10)
    if own[2]==2 and not aims and not allow_missing_aim:raise ValueError('empty required artillery aim bank; inspect coverage')
    if len(aims)>MAX_AIM or len(moves)>MAX_MOVE:raise ValueError('candidate overflow; no truncation')
    def arrays(items,cap):
        pts=np.zeros((cap,2));features=np.zeros((cap,FEATURES));mask=np.zeros(cap)
        for i,(p,f,_) in enumerate(items):pts[i]=p;features[i]=f;mask[i]=1
        if items and enemies:
            count=len(items);p=pts[:count]
            predicted=np.asarray(predictions);d=p[:,None,:]-predicted[None,:,:]
            features[:count,14]=(np.hypot(d[:,:,0],d[:,:,1])<=splash+1e-8).sum(1)/len(enemies)
            future=np.asarray([lead(u[3:5],u[5:7],.5) for u in enemies]);d=p[:,None,:]-future[None,:,:]
            reach=np.asarray([max(1.,u[11]) for u in enemies]);rate=np.asarray([u[12]/max(.001,u[14]) for u in enemies]);distance=np.hypot(d[:,:,0],d[:,:,1])/reach
            features[:count,15]=(rate/(1+distance**2)).sum(1)/100
        if not np.isfinite(pts).all() or not np.isfinite(features).all():raise ValueError('nonfinite candidate output')
        return pts,features,mask
    a,af,am=arrays(aims,MAX_AIM);m,mf,mm=arrays(moves,MAX_MOVE)
    if not moves:raise ValueError('missing movement candidates')
    return dict(aim_points=a,aim_features=af,aim_valid=am,move_points=m,move_features=mf,move_valid=mm),dict(aim=aims,move=moves)

def pack_candidates(row,ids):
    values=[bank(row,id)[0] for id in ids]
    return {key:np.stack([v[key] for v in values]) for key in values[0]} if values else {key:np.zeros((0,*shape)) for key,shape in {'aim_points':(MAX_AIM,2),'aim_features':(MAX_AIM,FEATURES),'aim_valid':(MAX_AIM,),'move_points':(MAX_MOVE,2),'move_features':(MAX_MOVE,FEATURES),'move_valid':(MAX_MOVE,)}.items()}

def nearest(point,points,valid,bound):
    indices=np.flatnonzero(valid)
    if not len(indices):return dict(index=0,residual=[0.,0.],distance=None,covered=False,representable=False)
    delta=np.asarray(point)-points[indices];dist=np.linalg.norm(delta,axis=1);j=int(np.argmin(dist));res=delta[j]
    return dict(index=int(indices[j]),residual=res.tolist(),distance=float(dist[j]),covered=bool(dist[j]<=TOLERANCE),representable=bool(np.all(np.abs(res)<=bound)))

def mapped_labels(row,ids,drift=None):
    labels={v['id']:v for v in row['labels']};out=[]
    for i,id in enumerate(ids):
        arrays,_=bank(row,id,allow_missing_aim=True);lab=labels[id];c=lab['executed'];move=np.asarray(c['goal'])-(np.asarray(drift[i]) if drift is not None else 0)
        result=dict(id=id,role=lab['role'],dodge=bool(lab.get('active')),move=nearest(move,arrays['move_points'],arrays['move_valid'],MOVE_OFFSET),aim=None)
        if c['aim'] is not None:result['aim']=nearest(c['aim'],arrays['aim_points'],arrays['aim_valid'],AIM_OFFSET)
        out.append(result)
    return out
