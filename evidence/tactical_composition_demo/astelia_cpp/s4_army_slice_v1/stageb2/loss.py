"""Balanced pointer + categorical geometry choices + measured bounded residuals."""
import time
import numpy as np
import torch
import runtime as r
import training
from candidates import bank,nearest,AIM_OFFSET,MOVE_OFFSET

def target_weights(fights,deadline):
    counts={role:[0,0] for role in ('melee','ranged','artillery')}
    for fight in fights:
        starts=training.selected_starts(fight['frames'],4)
        for tick,row in enumerate(r.data.frames(fight['raw_file'])):
            if time.monotonic()>=deadline:raise TimeoutError('target counting cap')
            if any(at<=tick<at+training.WINDOW for at in starts):
                for lab in row['labels']:counts[lab['role']][int(lab['executed']['target']!=0)]+=1
    if any(not all(v) for v in counts.values()):raise RuntimeError('both pointer classes required per role')
    return {role:dict(counts=c,weights=[sum(c)/(2*c[0]),sum(c)/(2*c[1])]) for role,c in counts.items()}

def install(balance):
    def objective(y,row,ids,enemies,weights=None):
        if not ids:return sum(v.sum()*0 for v in y.values()),{}
        labs=training.labels(row,ids,enemies)
        vals=lambda key:y['move'].new_tensor([v[key] for v in labs])
        ce=torch.nn.functional.cross_entropy(y['target'],vals('target').long(),reduction='none')
        wt=ce.new_tensor([balance[v['role']]['weights'][int(v['target']!=0)] for v in labs])
        losses=dict(target=(ce*wt).sum()/wt.sum(),fire=torch.nn.functional.cross_entropy(y['fire'],vals('fire').long()),mult=torch.mean((y['mult']-vals('mult'))**2))
        scale=y['move'].new_tensor([row['width'],row['height']])
        for name,bound in (('move',MOVE_OFFSET),('aim',AIM_OFFSET)):
            mask=vals('aim_mask').bool() if name=='aim' else torch.ones(len(ids),device=ce.device,dtype=torch.bool)
            mask=mask & y[name+'_valid'].any(-1)
            if name+'_train_logits' not in y:raise RuntimeError('hierarchical loss requires supervised forward')
            zero=y[name+'_residual'].sum()*0
            losses[name+'_family']=torch.nn.functional.cross_entropy(y[name+'_family_logits'][mask],y[name+'_true_family'][mask]) if mask.any() else zero
            losses[name+'_choice']=torch.nn.functional.cross_entropy(y[name+'_train_logits'][mask],y[name+'_true_member'][mask]) if mask.any() else zero
            losses[name+'_residual']=torch.nn.functional.smooth_l1_loss(y[name+'_residual'][mask]/100,y[name+'_true_residual'][mask]/100) if mask.any() else zero
        # N2 geometry drift gets gradients through the executed movement residual.
        actual=y['move']*scale+y['drift'];losses['move_geometry']=torch.nn.functional.smooth_l1_loss(actual/100,vals('move')*scale/100)
        return sum(losses.values()),{k:float(v.detach()) for k,v in losses.items()}
    training.objective=objective
