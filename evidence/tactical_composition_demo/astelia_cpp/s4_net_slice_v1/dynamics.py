"""C4 projected phase law. Positions are engine authority, never integrated here."""
import math
import torch

ABLATIONS={'intact','K0','frozen_phase','topology_only','no_geometry_to_mode','no_mode_to_geometry','no_reset'}

def graph(pos,ids,radius=3.):
    if len(ids)!=len(set(ids)) or len(ids)!=len(pos):raise ValueError('joint identity')
    return [[j for _,_,j in sorted((float(torch.linalg.vector_norm(pos[j]-pos[i]).detach())/100,ids[j],j) for j in range(len(ids)) if j!=i)[:8] if float(torch.linalg.vector_norm(pos[j]-pos[i]).detach())/100<radius] for i in range(len(ids))]

def phase_step(theta,pos,ids,omega,K,forcing,dt=1/30,ablation='intact',fixed=None):
    if ablation not in ABLATIONS or not 0<dt<=.2:raise ValueError('integration contract')
    if not torch.isfinite(theta).all() or not torch.isfinite(pos).all() or not torch.isfinite(forcing).all():raise FloatingPointError('nonfinite state')
    if bool((omega.abs()>2).any()) or not 0<=float(K.detach())<=2 or bool((forcing.abs()>1).any()):raise ValueError('rate envelope')
    if ablation=='frozen_phase':return theta
    if ablation in ('topology_only','no_geometry_to_mode'):
        if fixed is None:raise ValueError('fixed topology required')
        neighbors=fixed
    else:neighbors=graph(pos,ids)
    coupling=K*0 if ablation=='K0' else K
    def rhs(th):
        rates=[]
        for i,ns in enumerate(neighbors):
            terms=[]
            for j in ns:
                if not 0<=j<len(ids) or j==i:raise ValueError('topology index')
                r=torch.linalg.vector_norm(pos[j]-pos[i])/100
                weight=torch.ones_like(r) if ablation=='no_geometry_to_mode' else torch.exp(-r*r)
                terms.append(weight*torch.sin(th[j]-th[i]))
            rates.append(omega[i]+forcing[i]+coupling*(torch.stack(terms).mean() if terms else th[i]*0))
        return torch.stack(rates) if rates else theta.clone()
    # |rate|<=5; infinity phase-Jacobian norm<=4; h*4<=.25.
    steps=max(1,math.ceil(dt*4/.25));h=dt/steps;result=theta
    for _ in range(steps):
        def shifted(k,scale):
            trial=result+scale*k
            if not torch.isfinite(trial).all() or bool(((trial-theta).abs()>5*dt+1e-9).any()):raise FloatingPointError('phase stage envelope')
            return trial
        k1=rhs(result);k2=rhs(shifted(k1,h/2));k3=rhs(shifted(k2,h/2));k4=rhs(shifted(k3,h))
        trial=result+h*(k1+2*k2+2*k3+k4)/6
        if not torch.isfinite(trial).all() or bool(((trial-theta).abs()>5*dt+1e-9).any()):raise FloatingPointError('phase stage envelope')
        result=trial
    return result

def movement(theta,pos,ids,A,B,J,share,speeds,ablation='intact'):
    if not (0<=float(A.detach())<=1 and 0<=float(B.detach())<=1 and 0<=float(J.detach())<=1 and 0<=float(share.detach())<=.25):raise ValueError('motion envelope')
    neighbors=graph(pos,ids);out=[]
    for i,ns in enumerate(neighbors):
        terms=[]
        for j in ns:
            delta=(pos[j]-pos[i])/100;r=torch.linalg.vector_norm(delta);rr=r.clamp_min(.1)
            mode=J*0 if ablation=='no_mode_to_geometry' else J
            terms.append(delta/rr*(A*(1+mode*torch.cos(theta[j]-theta[i]))-B/rr))
        v=torch.stack(terms).mean(0) if terms else torch.zeros(2,dtype=theta.dtype,device=theta.device)
        # Smooth norm bound: ||v/(1+||v||)|| < 1, <= .25 speed px/s.
        out.append(share*speeds[i]*v/(1+torch.linalg.vector_norm(v)))
    return torch.stack(out) if out else pos.clone()


def remap_graph(fixed,fixed_ids,ids):
    """Prune frozen graph by persistent IDs after deaths, never by current slots."""
    slots={id:i for i,id in enumerate(ids)}
    original={id:i for i,id in enumerate(fixed_ids)}
    return [[slots[fixed_ids[j]] for j in fixed[original[id]] if fixed_ids[j] in slots] if id in original else [] for id in ids]


def baseline_drift(pos,ids,speeds):
    zero=speeds*0
    scalar=lambda x:speeds.new_tensor(x)
    return movement(zero,pos,ids,scalar(.5),scalar(.5),scalar(0),scalar(.125),speeds)


def add_drift(action,drift,snapshot):
    """Deployment goal projection, including Hold + nonzero drift."""
    from schema import check
    me=check(snapshot);out=dict(action)
    goal=[a+float(d) for a,d in zip(out['goal'],drift)]
    if math.hypot(*map(float,drift))>1e-12:out['multiplier']=1.
    delta=[goal[0]-me['x'],goal[1]-me['y']];length=math.hypot(*delta)
    if length>me['speed'] and length>0:goal=[me['x']+delta[0]*me['speed']/length,me['y']+delta[1]*me['speed']/length]
    out['goal']=[min(snapshot['width'],max(0,goal[0])),min(snapshot['height'],max(0,goal[1]))]
    return out
