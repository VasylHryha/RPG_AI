"""N2 offline controls, derived from original ablation_model.py. No training/export."""
import torch
from torch import nn
from common import ARMS

class ControlsPolicy(nn.Module):
    def __init__(self,kind,ablation="intact"):
        if ablation not in ('intact', 'indicator_no_phase', 'intact_no_bonus', 'forcing_only_cut', 'role_shuffle', 'forced_synchronous', 'intact_no_fire_window'):
            raise ValueError(ablation)
        self.shuffle_rng=torch.Generator().manual_seed(41002)
        self.ablation=ablation
        self.last_diagnostics=None
        super().__init__()
        if kind not in ARMS:raise ValueError(kind)
        self.kind=kind
        self.enc1=nn.Linear(64,64);self.enc2=nn.Linear(64,64)
        self.query=nn.Linear(128,64);self.head=nn.Linear(136,64)
        self.out=nn.Linear(64,9);self.target=nn.Linear(64,64)
        # Equal registered parameter budget, including unused N1 state branch.
        self.recur=nn.Linear(144,8);self.force=nn.Linear(128,1)
        self.law=nn.Parameter(torch.zeros(6)) # A,B,J,K,omega,share
    def encode(self,tokens):return torch.tanh(self.enc2(torch.tanh(self.enc1(tokens))))
    def tick(self,tokens,query,own,enemy,pos,speeds,assignments,ids,state,dt,refresh=True,cache=None):
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
            phase_forcing=forcing
            if self.ablation=='indicator_no_phase':K=K*0
            if self.ablation=='forcing_only_cut':phase_forcing=forcing*0
            count=mask.sum(1).clamp_min(1)
            def rhs(th):return omega+phase_forcing+K*(weight*torch.sin(th[order]-th[:,None])).sum(1)/count
            k1=rhs(theta);k2=rhs(theta+dt*k1/2);k3=rhs(theta+dt*k2/2);k4=rhs(theta+dt*k3)
            theta=theta+dt*(k1+2*k2+2*k3+k4)/6
            # Intervene after each physical update; the resulting phase is carried forward.
            # Public unit role flags only, never oracle labels, define shuffle groups.
            if self.ablation=='role_shuffle':
                role=tokens[own,3:6].argmax(-1)
                shuffled=theta.clone()
                for role_id in range(3):
                    ix=torch.nonzero(role==role_id).flatten()
                    shuffled[ix]=theta[ix[torch.randperm(len(ix),generator=self.shuffle_rng)]]
                theta=shuffled
            if self.ablation=='forced_synchronous':theta=torch.zeros_like(theta)
            self.last_diagnostics=dict(theta=theta,forcing=forcing,phase_forcing=phase_forcing,coupling=rhs(theta)-omega-phase_forcing,
                                       neighbor_count=mask.sum(1),order=order,mask=mask)
            z=torch.stack((torch.sin(theta),torch.cos(theta)),-1)
            mean=(z[order]*mask[...,None]).sum(1)/count[:,None]
            state=torch.cat((theta[:,None],z,mean,forcing[:,None],q.new_zeros((len(ids),2))),-1)
            A,B,J=torch.sigmoid(self.law[:3]);J=J*0 if self.kind=='N2J0' else J
            rr=r.gather(1,order).clamp_min(.1)
            v=((d[torch.arange(len(ids),device=r.device)[:,None],order]/100/rr[...,None])*(A*(1+J*torch.cos(theta[order]-theta[:,None]))-B/rr)[...,None]*mask[...,None]).sum(1)/count[:,None]
            drift=.25*torch.sigmoid(self.law[5])*speeds[:,None]*v/(1+torch.linalg.vector_norm(v,dim=-1)[:,None])
            state_for_head=torch.cat((state[:,1:6],q.new_zeros((len(ids),3))),-1)
        else:state_for_head=state
        h=torch.tanh(self.head(torch.cat((q,context,state_for_head),-1)))
        y=self.out(h)
        # Enemy pointer, with explicit none logit. All living enemies; no top-k loss.
        targets=torch.cat((y[:,8:9],self.target(h)@encoded[enemy].T/8),-1)
        if self.kind in ('N2','N2J0'):
            # Phase alignment of neighboring units already engaging each target.
            target_bonus=torch.zeros_like(targets)
            self.last_diagnostics['target_without_bonus']=targets.clone()
            for e,column in enumerate(enemy):
                target_id=tokens[column,1]*256
                peers=mask & (assignments[order]==target_id)
                group=(z[order]*peers[...,None]).sum(1)/peers.sum(1).clamp_min(1)[:,None]
                length=torch.linalg.vector_norm(group,dim=-1)
                bonus=2*(z*group/length.clamp_min(1e-6)[:,None]).sum(1)*(length>=1e-6)
                if self.ablation=='indicator_no_phase':bonus=2*peers.any(1).to(targets.dtype)
                if self.ablation!='intact_no_bonus':
                    targets[:,e+1]=targets[:,e+1]+bonus
                    target_bonus[:,e+1]=bonus
            self.last_diagnostics['target_bonus']=target_bonus
            # Learned logits retain the phase-window readout; no reset clock.
            self.last_diagnostics['fire_window_bonus']=2*torch.cos(theta)[:,None]*y.new_tensor([1.,-1.,1.])
            self.last_diagnostics['fire_without_window']=y[:,3:6].clone()
            if self.ablation!='intact_no_fire_window':
                y=torch.cat((y[:,:3],y[:,3:4]+2*torch.cos(theta)[:,None],y[:,4:5]-2*torch.cos(theta)[:,None],y[:,5:6]+2*torch.cos(theta)[:,None],y[:,6:]),-1)
        movement=torch.sigmoid(y[:,:2]);mult=torch.sigmoid(y[:,2]);aim=torch.sigmoid(y[:,6:8])
        return dict(move=movement,mult=mult,fire=y[:,3:6],aim=aim,target=targets,drift=drift),state,encoded
