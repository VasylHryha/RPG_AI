"""Stored-state + burn-in TBPTT, float64. No fight execution.

A single chronological epoch refresh snapshots complete state before every
window boundary and burn-in start. Snapshots may be stale for at most one epoch;
burn-in recomputes 30 physical ticks under current weights. Never start at zero
except t=0. Equality to full replay holds at unchanged weights.
"""
import copy
from functools import lru_cache
import math
import time
import numpy as np
import torch
from stage1_runtime import Replay,n1r_message,n2_tick
from stage1_arithmetic import graph

BURN_IN=30


class PreparedFight:
    def __init__(self,meta,arrays,geometry_root=None):
        self.meta=meta; self.arrays=arrays
        # Four-fight LRU bounds tensor copies; no per-tick dict/stack/features copy.
        self.x=arrays['x']  # mmap float32; convert only a joint decision row, never full fight
        if self.x.dtype!=np.float32:
            raise ValueError('held-feature snapshot requires original float32 feature arrays')
        self.pos=torch.tensor(np.asarray(arrays['pos']),dtype=torch.float64)
        self.targets=torch.tensor(np.asarray(arrays['targets']),dtype=torch.int64)
        self.assignments=torch.tensor(np.asarray(arrays['assignments']),dtype=torch.int64)
        self.active=[np.flatnonzero(row).tolist() for row in arrays['alive']]
        self.ids=[[meta['ids'][g] for g in gs] for gs in self.active]
        self.launches=[np.flatnonzero(row).tolist() for row in arrays['launch']]
        # Reuse weight-independent geometry across LRU reloads and epochs.
        cache=geometry_root/meta['group'] if geometry_root is not None else None
        shape=(meta['ticks'],meta['guns'],meta['guns'])
        if cache is not None:
            from collection import read,sha,atomic
            cache.mkdir(parents=True,exist_ok=True)
            pin=dict(arrays=meta['arrays'],source_sha256=sha(__file__))
            if (cache/'META.json').exists():
                old=read(cache/'META.json')
                if old['pins']!=pin or any(sha(cache/(k+'.npy'))!=v for k,v in old['hashes'].items()):
                    raise RuntimeError('prepared geometry cache drift; preserve and inspect')
                self.adj=np.load(cache/'adj.npy',mmap_mode='r')
                self.weight=np.load(cache/'weight.npy',mmap_mode='r')
                return
            if list(cache.iterdir()):
                raise RuntimeError('incomplete geometry cache; preserve and inspect')
            adj=np.lib.format.open_memmap(cache/'adj.npy',mode='w+',dtype='float64',shape=shape)
            weight=np.lib.format.open_memmap(cache/'weight.npy',mode='w+',dtype='float64',shape=shape)
        else:
            adj=np.zeros(shape); weight=np.zeros(shape)
        adj[:]=0; weight[:]=0
        for t,gs in enumerate(self.active):
            pos=self.pos[t,gs]; ids=self.ids[t]
            a=pos.new_zeros((len(ids),len(ids)))
            for i,peers in enumerate(graph(pos,ids)) if ids else ():
                a[i,peers]=1/max(1,len(peers))
            adj[t][np.ix_(gs,gs)]=a.numpy()
            weight[t][np.ix_(gs,gs)]=(a*torch.exp(-((pos[:,None]-pos[None,:])/100).square().sum(-1))).numpy()
        if cache is not None:
            adj.flush(); weight.flush()
            atomic(cache/'META.json',dict(pins=pin,hashes={k:sha(cache/(k+'.npy')) for k in ('adj','weight')}))
        self.adj=adj; self.weight=weight

    def geometry(self,t,gs):
        return tuple(torch.tensor(a[t][np.ix_(gs,gs)],dtype=torch.float64) for a in (self.adj,self.weight))

    def tick(self,replay,t,emit=True):
        gs=self.active[t]
        return replay.tick_prepared(self,t,emit) if isinstance(replay,TensorReplay) else replay.tick(
            self.ids[t],torch.tensor(self.x[t//6,gs],dtype=torch.float64),self.pos[t,gs],self.targets[t,gs],self.assignments[t,gs],
            float(self.arrays['dt'][t]),t%6==0,[self.meta['ids'][g] for g in self.launches[t]])


class TensorReplay:
    """Joint tensors indexed by the fight's fixed roster; state is fully snapshotable."""
    def __init__(self,model,guns):
        self.model=model; x=next(model.parameters())
        self.phase=None; self.memory=x.new_zeros((guns,8)); self.held=x.new_zeros((guns,1008))
        self.force=x.new_zeros(guns); self.initial_force=None
        self.assign=x.new_zeros(guns,dtype=torch.int64); self.cache={}
        self.live=[]; self.fixed=None; self.fixed_ids=None

    def snapshot(self):
        return {k:(v.detach().to(torch.float32).clone() if k=='held' else v.detach().clone()) if torch.is_tensor(v) else copy.deepcopy(v)
                for k,v in self.__dict__.items() if k!='model'}

    def restore(self,state):
        for k,v in state.items():
            setattr(self,k,(v.detach().to(next(self.model.parameters()).dtype).clone() if k=='held' else v.detach().clone()) if torch.is_tensor(v) else copy.deepcopy(v))
        return self

    def detach(self):
        for key in ('phase','memory','held','force','initial_force'):
            v=getattr(self,key)
            if torch.is_tensor(v):
                setattr(self,key,v.detach())

    def tick_prepared(self,f,t,emit=True):
        gs=f.active[t]; ids=f.ids[t]; self.live=ids[:]
        if self.phase is None:
            self.phase=self.memory.new_tensor([(i%16)*math.pi/8 for i in f.meta['ids']])
        if self.fixed is None and ids:
            self.fixed=graph(f.pos[t,gs],ids); self.fixed_ids=ids[:]
        if not gs:
            self.phase=self.phase*0; self.memory=self.memory*0; self.held=self.held*0; self.force=self.force*0
            self.assign=self.assign*0; self.initial_force=None; self.cache={}
            return None
        if t%6==0:
            self.held=self.held.index_copy(0,torch.tensor(gs),torch.tensor(f.x[t//6,gs],dtype=self.held.dtype))
            if self.model.kind=='N2':
                self.force=self.force.index_copy(0,torch.tensor(gs),torch.tanh(self.model.force(self.held[gs])).squeeze(-1))
        self.assign=f.assignments[t].clone()
        x=self.held[gs]; pos=f.pos[t,gs]
        if self.model.kind=='N2':
            y,phase=n2_tick(self.model,x,pos,ids,self.phase[gs],f.targets[t,gs],self.assign[gs],float(f.arrays['dt'][t]),
                           held_force=self.force[gs],geometry=f.geometry(t,gs),emit_logits=emit)
            reset=phase.new_tensor([g in f.launches[t] for g in gs],dtype=torch.bool)
            self.phase=self.phase.index_copy(0,torch.tensor(gs),torch.where(reset,phase*0,phase))
        else:
            memory=self.memory[gs]
            y,memory=self.model(x,memory,n1r_message(memory,pos,ids,self.assign[gs],f.targets[t,gs],f.geometry(t,gs)[0]))
            self.memory=self.memory.index_copy(0,torch.tensor(gs),memory)
        # Every Replay arm resets its phase bookkeeping on an actual launch,
        # including N1r where phase is not an input to the readout.
        launch=self.phase.new_tensor(f.arrays['launch'][t],dtype=torch.bool)
        self.phase=torch.where(launch,self.phase*0,self.phase)
        # Dead slots are zeroed; IDs/graph remain fixed. No identity resurrection.
        alive=self.memory.new_tensor(f.arrays['alive'][t],dtype=torch.bool)
        self.phase=torch.where(alive,self.phase,self.phase*0)
        self.memory=torch.where(alive[:,None],self.memory,self.memory*0)
        self.held=torch.where(alive[:,None],self.held,self.held*0)
        self.force=torch.where(alive,self.force,self.force*0)
        self.assign=torch.where(alive,self.assign,self.assign*0)
        return y


class StoredStates:
    def __init__(self):
        self.states={}; self.generation=0

    def refresh(self,model,windows,prepare,deadline=None):
        self.states={}; by_group={}
        for g,s,e in windows:
            by_group.setdefault(g,set()).update((s,max(0,s-BURN_IN)))
        begin=time.monotonic()
        with torch.no_grad():
            for group,boundaries in by_group.items():
                f=prepare(group); replay=TensorReplay(model,f.meta['guns'])
                last=f.meta['ticks']
                for t in range(last+1):
                    if deadline is not None and time.monotonic()>=deadline:
                        raise TimeoutError('training cap during state refresh')
                    if t%90==0:
                        from stage1_train import check_rss
                        check_rss()
                    if t in boundaries:
                        self.states[group,t]=replay.snapshot()
                    if t<last:
                        f.tick(replay,t,False)
        self.generation+=1
        return time.monotonic()-begin

    def start(self,model,f,start):
        t0=max(0,start-BURN_IN)
        replay=TensorReplay(model,f.meta['guns']).restore(self.states[f.meta['group'],t0])
        with torch.no_grad():
            for t in range(t0,start):
                f.tick(replay,t,False)
        replay.detach()
        return replay
