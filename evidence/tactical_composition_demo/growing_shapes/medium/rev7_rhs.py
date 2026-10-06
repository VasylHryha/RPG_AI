"""Independent Python rev7_rhs_v1 reference. Stage-sampled excursion is a warning bound."""
import math
import numpy as np


def lists(elements,drives,k=8,radius=3.,site_bodies=True):
    phase=[];motion=[]
    for i,e in enumerate(elements):
        pc=[];mc=[]
        for j,f in enumerate(elements):
            if i==j:continue
            r=math.hypot(f.x-e.x,f.y-e.y)
            if r<radius:
                mc.append((r,0,f.id,j))
                if not e.silent and not f.silent:pc.append((r,j))
        if site_bodies:
            for j,d in enumerate(drives):
                r=math.hypot(d.x-e.x,d.y-e.y)
                if d.strength>0 and r<radius:mc.append((r,1,d.id,-j-1))
        phase.append([j for _,j in sorted(pc)[:k]])
        motion.append([row[3] for row in sorted(mc)[:k]])
    return phase,motion


def rhs(state,elements,drives,phase,motion,params,gains,outputs,lesions,*,scale=8.,fixed=False):
    result=np.zeros((len(elements),3));terms=np.zeros((len(elements),4))
    for i,e in enumerate(elements):
        x,y,theta=state[i];vx=vy=coupling=drive=0.
        for j in motion[i]:
            if j>=0:
                dx,dy=state[j,0]-x,state[j,1]-y;delta=state[j,2]-theta
                rr=max(math.hypot(dx,dy),params.eps)
            else:
                d=drives[-j-1];dx,dy=d.x-x,d.y-y;delta=d.phase-theta
                rr=max(math.hypot(dx,dy),.3)
            radial=(params.A*(1+params.J*math.cos(delta))-params.B/rr)/rr
            vx+=dx*radial;vy+=dy*radial
        inv=1/max(1,len(motion[i]));vx*=params.geometry_rate*inv;vy*=params.geometry_rate*inv
        radius=math.hypot(x,y)
        if radius>6:terms[i,2:]=[-(radius-6)*x/radius,-(radius-6)*y/radius]
        vx+=terms[i,2];vy+=terms[i,3]
        if not e.silent:
            for j in phase[i]:
                r=math.hypot(state[j,0]-x,state[j,1]-y)
                coupling+=params.K*(math.exp(-r*r) if params.distance_weighted else 1)*math.sin(state[j,2]-theta)
            coupling=0. if e.id in lesions else scale*coupling/max(1,len(phase[i]))
            if e.id not in outputs:
                for d in drives:
                    r=math.hypot(d.x-x,d.y-y)
                    if r<d.reach:drive+=gains[i]*d.strength*math.exp(-r*r/(2*d.width*d.width))*math.sin(d.phase-theta)
            drive*=scale
            result[i,2]=e.rate+coupling+drive
        if fixed or e.id in outputs:vx=vy=0.
        result[i,:2]=vx,vy;terms[i,:2]=drive,coupling
    return result,terms


def step(native,h):
    from .medium import Drive
    es=native.elements;ds=native.reference_drives()
    policy=native.policy();scale,fixed,site_bodies=policy
    phase,motion=lists(es,ds,native.params.k,native.params.radius,site_bodies)
    start=np.array([[e.x,e.y,e.phase] for e in es],dtype=float).reshape(-1,3)
    gains=[native.gain(e.id) for e in es];outputs={e.id for e in es if native.role(e.id)=='output'}
    lesions=set(native.reference_lesions());stages=[];terms=[]
    for amount,previous in [(0,None),(h/2,0),(h/2,1),(h,2)]:
        drives=[Drive(d.id,d.x,d.y,d.phase+amount*d.rate,d.rate,d.strength,d.width,d.reach) for d in ds]
        state=start if previous is None else start+amount*stages[previous]
        value,record=rhs(state,es,drives,phase,motion,native.params,gains,outputs,lesions,scale=scale,fixed=fixed)
        stages.append(value);terms.append(record)
    result=start+h/6*(stages[0]+2*stages[1]+2*stages[2]+stages[3])
    excursion=h*np.max(np.abs(np.array(stages)[:,:,2]-math.pi),axis=0)
    native.reference_commit(result,excursion,np.array(terms),h)
