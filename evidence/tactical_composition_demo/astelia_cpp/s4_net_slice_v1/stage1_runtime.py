"""Differentiable joint tick replay. Only the engine supplies positions and launches.

Vectorized degree-normalized reductions preserve the contract's <=8 neighbor
graph. The separate deployment replay is used for full native sequence parity.
"""
import math
import torch
from dynamics import remap_graph
from models import recurrent_message, assert_shared_baseline
from stage1_arithmetic import encode,decode,graph,add_drift,baseline_drift


def n1r_message(memory,pos,ids,assignments,candidates):
    adjacent=memory.new_zeros((len(ids),len(ids)))
    for i,peers in enumerate(graph(pos,ids)):
        adjacent[i,peers]=1/max(1,len(peers))
    candidate=torch.as_tensor(candidates,dtype=torch.int64)
    assign=torch.as_tensor(assignments,dtype=torch.int64)
    matches=(candidate[:,:,None]==assign[None,None,:]) & (candidate[:,:,None]!=0)
    mass=(adjacent[:,None,:]*matches.to(memory.dtype)).sum(-1)
    group=torch.einsum('ij,icj,jk->ick',adjacent,matches.to(memory.dtype),memory)/mass.clamp_min(1e-30)[:,:,None]
    product=torch.linalg.vector_norm(group,dim=-1)*torch.linalg.vector_norm(memory,dim=-1)[:,None]
    cosine=(memory[:,None,:]*group).sum(-1)/product.clamp_min(1e-6)
    cosine=torch.where(product>=1e-6,cosine,cosine*0)
    return torch.cat((adjacent@memory,cosine),-1)


def n2_tick(model, x, pos, ids, theta, candidates, assignments, dt,
            ablation='intact', fixed=None, held_force=None):
    assert_shared_baseline(model)
    ns = fixed if ablation in ('topology_only','no_geometry_to_mode') else graph(pos,ids)
    adjacent = x.new_zeros((len(ids),len(ids)))
    for i,peers in enumerate(ns):
        adjacent[i,peers] = 1/max(1,len(peers))
    distance2 = ((pos[:,None]-pos[None,:])/100).square().sum(-1)
    weight = adjacent if ablation=='no_geometry_to_mode' else adjacent*torch.exp(-distance2)
    force = torch.tanh(model.force(x)).squeeze(-1) if held_force is None else held_force
    K = model.law[3].sigmoid()*2
    omega = model.law[4].tanh()*2
    if ablation=='K0':
        K = K*0
    def rhs(th):
        return omega+force+K*(weight*torch.sin(th[None,:]-th[:,None])).sum(-1)
    if ablation!='frozen_phase':
        original = theta
        h = dt/max(1,math.ceil(dt*4/.25))
        def checked(th):
            if not bool(torch.isfinite(th).all()) or bool(((th-original).abs()>5*dt+1e-9).any()):
                raise FloatingPointError('phase envelope; no update')
            return th
        for _ in range(max(1,math.ceil(dt*4/.25))):
            k1=rhs(theta); k2=rhs(checked(theta+h*k1/2)); k3=rhs(checked(theta+h*k2/2)); k4=rhs(checked(theta+h*k3))
            theta=checked(theta+h*(k1+2*k2+2*k3+k4)/6)
    # Messages always use current geometry, including frozen phase graph arms.
    live = x.new_zeros((len(ids),len(ids)))
    for i,peers in enumerate(graph(pos,ids)):
        live[i,peers] = 1/max(1,len(peers))
    z=torch.stack((theta.sin(),theta.cos()),-1)
    state=torch.cat((z,live@z),-1)
    candidate=torch.as_tensor(candidates,dtype=torch.int64)
    assign=torch.as_tensor(assignments,dtype=torch.int64)
    matches=(candidate[:,:,None]==assign[None,None,:]) & (candidate[:,:,None]!=0)
    group=torch.einsum('ij,icj,jk->ick',live,matches.to(x.dtype),z)
    mass=(live[:,None,:]*matches.to(x.dtype)).sum(-1)
    group=group/mass.clamp_min(1e-30)[:,:,None]
    norm=torch.linalg.vector_norm(group,dim=-1)
    message=(z[:,None,:]*group/norm.clamp_min(1e-6)[:,:,None]).sum(-1)
    message=torch.where(norm>=1e-6,message,message*0)
    y,_=model(x,state,message)
    if ablation=='no_mode_to_geometry':
        blind,_=model(x,state*0,message*0)
        y=torch.cat((blind[:,:33],y[:,33:]),-1)
    return y,theta


class Replay:
    def __init__(self, model, ablation='intact'):
        self.model=model; self.ablation=ablation
        self.phase={}; self.memory={}; self.held={}; self.assign={}; self.cache={}
        self.fixed=None; self.fixed_ids=None; self.initial_force={}

    def tick(self, ids, x, pos, candidates, assignments, dt, decision, launches=()):
        if not ids:
            return None
        phase=torch.stack([self.phase.get(i,x.new_tensor((i%16)*math.pi/8)) for i in ids])
        mem=torch.stack([self.memory.get(i,x.new_zeros(8)) for i in ids])
        if self.fixed is None:
            self.fixed=graph(pos,ids); self.fixed_ids=ids[:]
        if decision:
            for i,v in zip(ids,x):
                self.held[i]=v
        held=torch.stack([self.held[i] for i in ids])
        if self.model.kind=='N2':
            force=None
            if self.ablation=='no_geometry_to_mode':
                for i,v in zip(ids,torch.tanh(self.model.force(held)).squeeze(-1)):
                    if i not in self.initial_force:
                        self.initial_force[i]=v
                force=torch.stack([self.initial_force[i] for i in ids])
            y,phase=n2_tick(self.model,held,pos,ids,phase,candidates,assignments,dt,self.ablation,
                            remap_graph(self.fixed,self.fixed_ids,ids),force)
        elif self.model.kind=='N1r':
            y,mem=self.model(held,mem,n1r_message(mem,pos,ids,assignments,candidates))
        else:
            y,_=self.model(held)
        for j,i in enumerate(ids):
            self.phase[i]=phase[j]*0 if i in launches and self.ablation not in ('frozen_phase','no_reset') else phase[j]
            self.memory[i]=mem[j]
        for table in (self.phase,self.memory,self.held,self.assign,self.cache,self.initial_force):
            for id in list(table):
                if id not in ids:
                    del table[id]
        return y

    def detach(self):
        for table in (self.phase,self.memory,self.held,self.initial_force):
            for key in table:
                table[key]=table[key].detach()

    def deployment(self, frames, launches=None):
        """Replay public observations with student assignments, not teacher targets.

        Native fixture sequence does not run a cast machine. Launch acknowledgements
        are supplied explicitly by the recorded-sequence RPC after each tick.
        """
        from stage1_arithmetic import movement
        results=[]
        for tick,frame in enumerate(frames,1):
            ids=[s['self'] for s in frame]
            if not ids:
                results.append(dict(phases=[],actions=[],drift=[],memory=[])); continue
            x=torch.tensor([encode(s)[0] for s in frame],dtype=torch.float64)
            pos=torch.tensor([[next(u for u in s['units'] if u['id']==s['self'])[k] for k in ('x','y')] for s in frame],dtype=torch.float64)
            candidates=[encode(s)[1]['enemy_ids']+[0]*(12-len(encode(s)[1]['enemy_ids'])) for s in frame]
            launched=[] if launches is None else launches[tick-1]
            y=self.tick(ids,x,pos,candidates,[self.assign.get(i,0) for i in ids],frame[0]['dt'],(tick-1)%6==0)
            phases=torch.stack([self.phase[i] for i in ids])
            speeds=x[:,10]*200
            if self.model.kind=='N2':
                law=self.model.law
                drift=movement(phases,pos,ids,law[0].sigmoid(),law[1].sigmoid(),law[2].sigmoid(),law[5].sigmoid()*.25,speeds,self.ablation)
            else:
                drift=baseline_drift(pos,ids,speeds)
            if (tick-1)%6==0:
                for id,s,yy,d in zip(ids,frame,y,drift):
                    a=add_drift(decode(s,yy.detach().tolist()),d.detach(),s)
                    self.cache[id]=a; self.assign[id]=a['target']
            results.append(dict(phases=[[i,float(self.phase[i].detach())] for i in ids],
                                actions=[dict(id=i,action=self.cache[i]) for i in ids],
                                memory=[[i,self.memory[i].detach().tolist()] for i in ids],drift=drift.detach().tolist()))
            if self.ablation not in ('frozen_phase','no_reset'):
                for i in launched:
                    if i in self.phase:
                        self.phase[i]=self.phase[i]*0
        return results
