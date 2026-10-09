"""Pure public geometric movement points. See B2MOVE_MATH.md for equations.

No oracle state, labels, decision rules, target assignment, or history of actions.
Every raw point and its unconditional radial image remains a learned option.
"""
import math
from tools import add, sub, mul, norm, direction, range_project

def ordinary_points(row, own, units):
    pos=tuple(own[3:5]);W,H=row['width'],row['height'];r=own[9]
    enemies=[u for u in units if u[1]==1];friends=[u for u in units if u[1]==0 and u[0]!=own[0]]
    guns=[u for u in units if u[1]==0 and u[2]==2]
    indices={u[0]:i for i,u in enumerate(units)}
    box=(r,r,W-r,H-r);out=[]
    nearest=min(enemies,key=lambda u:(norm(sub(pos,u[3:5])),u[0])) if enemies else None
    def bounds(e):return (own[18],own[11]) if own[2]==2 else (0.,own[11]+r+e[9])
    def clip(p,body=False):
        margin=r if body else 0.
        return (min(W-margin,max(margin,p[0])),min(H-margin,max(margin,p[1])))
    def emit(p,typ,source=-1,image=True):
        out.append((clip(p),typ,source))
        if image and nearest is not None:
            e=tuple(nearest[3:5]);delta=sub(p,e);length=norm(delta)
            d=direction(delta if length else sub(pos,e));lo,hi=bounds(nearest)
            out.append((clip(add(e,mul(d,min(hi,max(lo,length)))),True),23,source))
    shift=(0.,0.)
    for u in friends:
        if own[2]==2 and u[2]!=2:continue
        delta=sub(pos,u[3:5]);distance=norm(delta)
        d=direction(delta) if distance else (-1. if own[0]<u[0] else 1.,0.)
        shift=add(shift,mul(d,max(0.,60-distance)))
    emit(add(pos,shift),24)
    for e in enemies:
        lo,hi=bounds(e);source=indices[e[0]]
        band=range_project(pos,e[3:5],lo,hi,box)
        if band is not None:out.append((band,23,source))
        emit(add(pos,mul(direction(sub(e[3:5],pos)),200)),21,source)
        if own[2]==2:
            anchor=add(e[3:5],mul(direction(sub(pos,e[3:5])),max(own[18],own[11]-12)))
            emit(anchor,19,source);emit(add(anchor,shift),20,source)
    if own[2]==1 and guns:
        g=min(guns,key=lambda u:(norm(sub(pos,u[3:5])),u[0]));p=tuple(g[3:5])
        for e in enemies:emit(clip(add(p,mul(direction(sub(e[3:5],p)),60))),18,indices[e[0]])
        eg=[u for u in enemies if u[2]==2]
        if eg:
            centre=(sum(u[3] for u in eg)/len(eg),sum(u[4] for u in eg)/len(eg))
            emit(clip(add(p,mul(direction(sub(centre,p)),60))),18,indices[g[0]])
    for v in (own[5:7],row.get('longVelocity',{}).get(str(own[0]),own[5:7])):
        emit(add(pos,mul(direction(v),200)) if norm(v) else pos,22)
        emit(add(pos,v),22)
    # Fixed directions compute a basis of options, never an action or target.
    if enemies:
        for j in range(64):
            angle=j*math.pi/32;d=(math.cos(angle),math.sin(angle))
            emit(add(pos,mul(d,200)),25,image=False)
        lo,hi=bounds(nearest)
        for radius in ((hi,lo) if lo>0 else (hi,)):
            for j in range(64):
                angle=j*math.pi/32;d=(math.cos(angle),math.sin(angle))
                emit(add(nearest[3:5],mul(d,radius)),25,indices[nearest[0]],image=False)
    return out
