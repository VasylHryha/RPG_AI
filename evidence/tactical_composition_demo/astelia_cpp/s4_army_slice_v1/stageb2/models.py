"""Shared physical-tick entity attention; physical-tick GRU/phase updates and heads.
C4 projected phase/spacing law, as amended in 0g R2.6; J learns here.
"""
import math
import torch
from torch import nn
from common import ARMS,write

class Policy(nn.Module):
    def __init__(self,kind):
        super().__init__()
        if kind not in ('N1','N1h','N1r','N2'):raise ValueError(kind)
        self.kind=kind
        self.enc1=nn.Linear(64,64);self.enc2=nn.Linear(64,64)
        self.query=nn.Linear(128,64);self.head=nn.Linear(136,64)
        self.out=nn.Linear(64,9);self.target=nn.Linear(64,64)
        # Equal registered parameter budget, including unused N1 state branch.
        self.recur=nn.Linear(144,8);self.force=nn.Linear(128,1)
        self.law=nn.Parameter(torch.zeros(6))
        from candidates import FEATURES
        self.aim_choice=nn.Linear(64,FEATURES);self.move_choice=nn.Linear(64,FEATURES)
        for name in ('aim','move'):
            setattr(self,name+'_source',nn.Linear(64,64))
            setattr(self,name+'_hidden',nn.Linear(FEATURES+128,16))
            setattr(self,name+'_score',nn.Linear(16,1))
        self.aim_offset=nn.Linear(64,2);self.move_offset=nn.Linear(64,2) # A,B,J,K,omega,share
    def encode(self,tokens):return torch.tanh(self.enc2(torch.tanh(self.enc1(tokens))))
    def tick(self,tokens,query,own,enemy,pos,speeds,assignments,ids,state,dt,refresh=True,cache=None,aim_points=None,aim_features=None,aim_valid=None,move_points=None,move_features=None,move_valid=None,aim_sources=None,move_sources=None,state_only=False):
        encoded=self.encode(tokens) if refresh else cache
        q=torch.tanh(self.query(query));a=torch.softmax(q@encoded.T/8,dim=-1);context=a@encoded
        if self.kind in ('N1','N1h'):state=q.new_zeros((len(ids),8))
        if self.kind=='N1r':
            r=torch.linalg.vector_norm(pos[None,:,:]-pos[:,None,:],dim=-1)/100
            order=torch.argsort(r+torch.eye(len(ids),device=r.device)*1e6,dim=-1,stable=True)[:,:8]
            mask=(r.gather(1,order)<3)&(order!=torch.arange(len(ids),device=r.device)[:,None])
            message=(state[order]*mask[...,None]).sum(1)/mask.sum(1).clamp_min(1)[:,None]
            state=torch.tanh(self.recur(torch.cat((q,context,state,message),-1)))
        drift=pos*0
        if self.kind in ('N2','N2J0'):
            # graph sorted by distance then persistent ID; eight neighbors inside 300 px.
            d=pos[None,:,:]-pos[:,None,:];r=torch.linalg.vector_norm(d,dim=-1)/100
            order=torch.argsort(r+torch.eye(len(ids),device=r.device)*1e6,dim=-1,stable=True)[:,:8]
            mask=(r.gather(1,order)<3)&(order!=torch.arange(len(ids),device=r.device)[:,None])
            weight=torch.exp(-r.gather(1,order)**2)*mask
            theta=state[:,0];K=2*torch.sigmoid(self.law[3]);omega=2*torch.tanh(self.law[4])
            forcing=torch.tanh(self.force(torch.cat((q,context),-1))).squeeze(-1)
            count=mask.sum(1).clamp_min(1)
            def rhs(th):return omega+forcing+K*(weight*torch.sin(th[order]-th[:,None])).sum(1)/count
            k1=rhs(theta);k2=rhs(theta+dt*k1/2);k3=rhs(theta+dt*k2/2);k4=rhs(theta+dt*k3)
            theta=theta+dt*(k1+2*k2+2*k3+k4)/6
            z=torch.stack((torch.sin(theta),torch.cos(theta)),-1)
            mean=(z[order]*mask[...,None]).sum(1)/count[:,None]
            state=torch.cat((theta[:,None],z,mean,forcing[:,None],q.new_zeros((len(ids),2))),-1)
            A,B,J=torch.sigmoid(self.law[:3]);J=J*0 if self.kind=='N2J0' else J
            rr=r.gather(1,order).clamp_min(.1)
            v=((d[torch.arange(len(ids),device=r.device)[:,None],order]/100/rr[...,None])*(A*(1+J*torch.cos(theta[order]-theta[:,None]))-B/rr)[...,None]*mask[...,None]).sum(1)/count[:,None]
            drift=.25*torch.sigmoid(self.law[5])*speeds[:,None]*v/(1+torch.linalg.vector_norm(v,dim=-1)[:,None])
            state_for_head=torch.cat((state[:,1:6],q.new_zeros((len(ids),3))),-1)
        else:state_for_head=state
        if state_only:return dict(drift=drift),state,encoded
        h=torch.tanh(self.head(torch.cat((q,context,state_for_head),-1)))
        y=self.out(h)
        # Enemy pointer, with explicit none logit. All living enemies; no top-k loss.
        targets=torch.cat((y[:,8:9],self.target(h)@encoded[enemy].T/8),-1)
        if self.kind in ('N2','N2J0'):
            # Phase alignment of neighboring units already engaging each target.
            for e,column in enumerate(enemy):
                target_id=tokens[column,1]*256
                peers=mask & (assignments[order]==target_id)
                group=(z[order]*peers[...,None]).sum(1)/peers.sum(1).clamp_min(1)[:,None]
                length=torch.linalg.vector_norm(group,dim=-1)
                targets[:,e+1]=targets[:,e+1]+2*(z*group/length.clamp_min(1e-6)[:,None]).sum(1)*(length>=1e-6)
            # Learned logits retain the phase-window readout; no reset clock.
            y=torch.cat((y[:,:3],y[:,3:4]+2*torch.cos(theta)[:,None],y[:,4:5]-2*torch.cos(theta)[:,None],y[:,5:6]+2*torch.cos(theta)[:,None],y[:,6:]),-1)
        from candidates import AIM_OFFSET,MOVE_OFFSET
        def choose(name,points,features,valid,sources,scorer,offsetter,bound):
            # Factor the first MLP linear: never retain [candidate,h,source]
            # concatenations, nor score padding, across a 90-tick autograd window.
            valid=valid>=.5
            unit_index,candidate_index=valid.nonzero(as_tuple=True)
            f=features[unit_index,candidate_index]
            source=sources[unit_index,candidate_index];has_source=source>=0
            key=scorer(h);source_key=getattr(self,name+'_source')(h)
            source_scores=source_key@encoded.T/8
            values=(f*key[unit_index]).sum(-1)/math.sqrt(features.shape[-1])
            values=values+source_scores[unit_index,source.clamp_min(0)]*has_source
            layer=getattr(self,name+'_hidden');width=features.shape[-1]
            projection=torch.nn.functional.linear(f,layer.weight[:,:width],layer.bias)
            own_projection=torch.nn.functional.linear(h,layer.weight[:,width:width+64])
            source_projection=torch.nn.functional.linear(encoded,layer.weight[:,width+64:])
            projection=projection+own_projection[unit_index]+source_projection[source.clamp_min(0)]*has_source[:,None]
            values=values+getattr(self,name+'_score')(torch.tanh(projection)).squeeze(-1)
            logits=h.new_zeros(valid.shape).index_put((unit_index,candidate_index),values)
            if not torch.isfinite(logits[valid]).all():raise FloatingPointError('nonfinite candidate scores')
            masked=logits.masked_fill(~valid,-torch.inf);choice=masked.argmax(-1)
            maximum=masked.max(-1).values
            maximum=torch.where(valid.any(-1),maximum,torch.zeros_like(maximum))
            logits=(logits-maximum[:,None]).masked_fill(~valid,-1e6)
            offset=bound*torch.tanh(offsetter(h))
            point=points[torch.arange(len(ids),device=h.device),choice]+offset
            return point,logits,offset
        movement,move_logits,move_residual=choose('move',move_points,move_features,move_valid,move_sources,self.move_choice,self.move_offset,MOVE_OFFSET)
        aim,aim_logits,aim_residual=choose('aim',aim_points,aim_features,aim_valid,aim_sources,self.aim_choice,self.aim_offset,AIM_OFFSET)
        # query stores arena-normalized own position; dimensions passed via world token.
        scale=tokens[-1,38:40]*1000
        movement=movement/scale;aim=aim/scale;mult=torch.sigmoid(y[:,2])
        return dict(move=movement,mult=mult,fire=y[:,3:6],aim=aim,target=targets,drift=drift,aim_logits=aim_logits,move_logits=move_logits,aim_residual=aim_residual,move_residual=move_residual,aim_points=aim_points,aim_valid=aim_valid,move_points=move_points,move_valid=move_valid),state,encoded

def initial(kind,ids,dtype=torch.float32):
    x=torch.zeros((len(ids),8),dtype=dtype)
    if kind in ('N2','N2J0'):x[:,0]=torch.tensor([(i*0.6180339887498949%1)*2*math.pi for i in ids],dtype=dtype)
    return x

def remap(kind,state,previous,ids):
    fresh=initial(kind,ids,state.dtype).to(state.device);lookup={id:i for i,id in enumerate(previous)}
    return torch.stack([state[lookup[id]] if id in lookup else fresh[i] for i,id in enumerate(ids)]) if ids else fresh

def export(model,path):
    payload=dict(version='ARMYB2',kind=model.kind,dtype='float64',learnedDodge=__import__('os').environ.get('B2_VARIANT','react_on')=='learned_dodge',parameters={k:dict(shape=list(v.shape),values=v.detach().double().reshape(-1).tolist()) for k,v in model.state_dict().items()})
    write(path,payload)
    return payload
