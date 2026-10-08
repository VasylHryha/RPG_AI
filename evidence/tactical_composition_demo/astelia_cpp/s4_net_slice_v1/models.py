"""Fixture-ready trainable forwards, no training entry point."""
import json
import math
from pathlib import Path
import torch
from torch import nn
from dynamics import phase_step, movement, graph
from schema import WIDTH

torch.set_num_threads(4)
torch.set_num_interop_threads(1)

class Policy(nn.Module):
    def __init__(self,kind):
        super().__init__()
        if kind not in ('N1','N1r','N2'):raise ValueError(kind)
        self.kind=kind
        self.hidden=nn.Linear(WIDTH+(0 if kind=='N1' else 28 if kind=='N1r' else 16),64)
        self.readout=nn.Linear(64,81)
        if kind=='N1r':self.recurrence=nn.Linear(64,8)
        if kind=='N2':
            self.force=nn.Linear(WIDTH,1)
            # Raw bounds mapped with sigmoid / tanh; radius fixed at 3.
            self.law=nn.Parameter(torch.zeros(6)) # A,B,J,K,omega,share
        self.double()
        if kind=="N2":self.law.register_hook(lambda g:g*g.new_tensor([0.,0.,0.,1.,1.,0.]))
    def forward(self,x,state=None,message=None):
        if self.kind=='N1':return self.readout(torch.tanh(self.hidden(x))),None
        if state is None or message is None or state.shape[-1]+message.shape[-1]!=(28 if self.kind=='N1r' else 16):raise ValueError('state/message required')
        h=torch.tanh(self.hidden(torch.cat([x,state,message],-1)))
        y=self.readout(h)
        if self.kind=='N1r':return y,torch.tanh(self.recurrence(h))
        # state=sin(theta), cos(theta), mean sin/cos; message=12 previous-target alignments.
        phase=state[...,1]
        y=torch.cat([y[...,:46],6*torch.tanh(y[...,46:48]/6)+2*phase[...,None],y[...,48:]],-1)
        return y,None
    def joint(self,x,pos,ids,theta,previous,dt=1/30,ablation='intact',fixed=None,held_force=None,assignments=None):
        if self.kind!='N2':raise ValueError('N2 only')
        if assignments is None:raise ValueError("previous assignments required")
        if ablation=="no_geometry_to_mode" and held_force is None:raise ValueError("freeze geometry forcing in complete probe")
        A,B,J=torch.sigmoid(self.law[:3]);K=2*torch.sigmoid(self.law[3]);omega=2*torch.tanh(self.law[4]);share=.25*torch.sigmoid(self.law[5])
        forcing=torch.tanh(self.force(x)).squeeze(-1) if held_force is None else held_force
        phase=phase_step(theta,pos,ids,omega.expand_as(theta),K,forcing,dt,ablation,fixed)
        ns=graph(pos,ids)
        fields=[];groups=[]
        for i,neighbors in enumerate(ns):
            z=torch.stack([torch.sin(phase),torch.cos(phase)],-1)
            mean=z[neighbors].mean(0) if neighbors else z[i]*0
            fields.append(torch.cat([z[i],mean]))
            align=[]
            for target in previous[i]:
                # previous[i] holds 12 target IDs followed by assignments via caller below.
                peers=[j for j in neighbors if target and assignments[j]==target]
                g=z[peers].mean(0) if peers else z[i]*0
                length=torch.linalg.vector_norm(g)
                align.append((z[i]*g/length.clamp_min(1e-6)).sum() if float(length.detach())>=1e-6 else phase[i]*0)
            groups.append(torch.stack(align))
        state=torch.stack(fields);message=torch.stack(groups)
        y,_=self.forward(x,state,message)
        if ablation=='no_mode_to_geometry':
            blind,_=self.forward(x,torch.zeros_like(state),torch.zeros_like(message))
            y=torch.cat([blind[...,:33],y[...,33:]],-1)
        drift=movement(phase,pos,ids,A,B,J,share,x[:,10]*200,ablation)
        return y,phase,drift

def export(model,path):
    payload={'version':'NS1','kind':model.kind,'dtype':'float64','parameters':{k: {'shape':list(v.shape),'values':v.detach().reshape(-1).tolist()} for k,v in model.state_dict().items()}}
    Path(path).write_text(json.dumps(payload,allow_nan=False,separators=(',',':'))+'\n')
    return payload

def recurrent_message(memory,pos,ids,assignments,candidates):
    """Neighbor mean8 and separate per-target cosine12; no slot aliasing."""
    result=[]
    for i,ns in enumerate(graph(pos,ids)):
        m=memory[ns].mean(0) if ns else memory[i]*0
        align=[]
        for target in candidates[i]:
            peers=[j for j in ns if target and assignments[j]==target]
            group=memory[peers].mean(0) if peers else memory[i]*0
            length=torch.linalg.vector_norm(group)*torch.linalg.vector_norm(memory[i])
            align.append((memory[i]*group).sum()/length.clamp_min(1e-6) if float(length.detach())>=1e-6 else memory[i].sum()*0)
        result.append(torch.cat([m,torch.stack(align)]))
    return torch.stack(result)


def assert_imitation_optimizer(model,optimizer):
    if any(group.get('weight_decay',0)!=0 for group in optimizer.param_groups):raise ValueError('imitation weight_decay must be zero')
    if model.kind=='N2':
        state=optimizer.state.get(model.law,{})
        frozen=torch.tensor([0,1,2,5],dtype=torch.long)
        for key in ('exp_avg','exp_avg_sq','max_exp_avg_sq','momentum_buffer'):
            if key in state and bool((state[key][frozen]!=0).any()):raise ValueError('frozen law coordinates have inherited optimizer moments')
