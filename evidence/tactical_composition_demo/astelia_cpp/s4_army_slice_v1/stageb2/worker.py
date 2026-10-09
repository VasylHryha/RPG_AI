"""Copied epoch-transaction and inherited-lock pattern from s4_net_slice_v1."""
import argparse
import copy
import math
import os
import random
import time
import numpy as np
import torch
from common import ARMS,HERE,LOCAL,read,sha,write
from models import export
from training import WINDOW,checked_budget,environment,evaluate,make,step,stored
from training_control import TrainingDeadline,atomic_checkpoint,last_checkpoint

def fit(arm,deadline):
    environment();b=checked_budget();digest=sha(LOCAL/'TRAIN_BUDGET.json');out=LOCAL/'training';directory=out/'epochs'/arm
    m,opt=make(arm)
    from initialization import capture,resumed
    initialization=capture(m)
    initial_force={k:v.detach().clone() for k,v in m.state_dict().items() if k.startswith("force.")};state=last_checkpoint(directory,digest);fights=read(LOCAL/'INDEX.json')['fights'];train=[f for f in fights if f['split']=='train'];val=[f for f in fights if f['split']=='validation'];test=[f for f in fights if f['split']=='test']
    if state:
        initialization=resumed(state,initialization)
        m.load_state_dict(state['model']);opt.load_state_dict(state['optimizer']);random.setstate(state['python_rng']);np.random.set_state(state['numpy_rng']);torch.set_rng_state(state['torch_rng'])
    else:state=dict(initialization=initialization,epoch=0,best=math.inf,best_model=None,best_epoch=None,history=[],steps=[],rows=0,wall_seconds=0,cpu_seconds=0)
    import training
    prior_flops=state.get("forward_flops",0);prior_encoder=state.get("encoder_calls",0);prior_phase=state.get("phase_rhs",0)
    start=time.monotonic();cpu=time.process_time();prior_wall=state['wall_seconds'];prior_cpu=state['cpu_seconds']
    for epoch in range(state['epoch'],b['epochs']):
        checked_budget();cached={};refresh_start=time.monotonic()
        for f in train:
            cachepath=out/'stored'/arm/(f['tag']+'.pt');rows,saved,_=stored(m,f,b['windows_per_fight'],deadline,cachepath);cached[f['tag']]=list(saved)
        refresh_seconds=time.monotonic()-refresh_start
        rng=random.Random(91000+epoch);fight_order=train[:];rng.shuffle(fight_order);order=[]
        for f in fight_order:
            starts=cached[f['tag']][:];rng.shuffle(starts);order.extend((f,at) for at in starts)
        loaded_tag=None;step_count=0
        for fight,at in order:
            if loaded_tag!=fight['tag']:
                from training import window_rows
                rows=window_rows(fight,b['windows_per_fight']);contexts=torch.load(out/'stored'/arm/(fight['tag']+'.pt'),weights_only=False);loaded_tag=fight['tag']
            measured=step(m,opt,rows[at:at+WINDOW],contexts[at],b['class_weights'],deadline);state['steps'].append(dict(epoch=epoch+1,fight=fight['tag'],tick=at,**measured));state['rows']+=measured['decision_rows'];step_count+=1
        if step_count!=b['samples'][arm]['steps_per_epoch']:raise RuntimeError('matched step budget violated')
        diagnostic=evaluate(m,val,b['windows_per_fight'],b['class_weights'],deadline)
        if diagnostic['loss']<state['best']:state.update(best=diagnostic['loss'],best_epoch=epoch+1,best_model=copy.deepcopy(m.state_dict()))
        state['history'].append(dict(epoch=epoch+1,validation=diagnostic,refresh_seconds=refresh_seconds));state.update(forward_flops=prior_flops+training.FORWARD_FLOPS,encoder_calls=prior_encoder+training.ENCODER_CALLS,phase_rhs=prior_phase+training.PHASE_RHS,epoch=epoch+1,kind=arm,budget_sha256=digest,model=m.state_dict(),optimizer=opt.state_dict(),python_rng=random.getstate(),numpy_rng=np.random.get_state(),torch_rng=torch.get_rng_state(),wall_seconds=prior_wall+time.monotonic()-start,cpu_seconds=prior_cpu+time.process_time()-cpu)
        atomic_checkpoint(directory/f'epoch_{epoch+1:04}.pt',state)
    m.load_state_dict(state['best_model']);atomic_checkpoint(out/(arm+'.pt'),dict(model=state['best_model'],epoch=state['best_epoch'],budget_sha256=digest));export(m,out/(arm+'.weights.json'))
    final=evaluate(m,test,b['windows_per_fight'],b['class_weights'],deadline);checked_budget()
    result=dict(arm=arm,budget_sha256=digest,checkpoint_sha256=sha(out/(arm+'.pt')),export_sha256=sha(out/(arm+'.weights.json')),selected_epoch=state['best_epoch'],history=state['history'],test=final,steps=state['steps'],gradient_steps=len(state['steps']),decision_rows=state['rows'],wall_seconds=prior_wall+time.monotonic()-start,cpu_seconds=prior_cpu+time.process_time()-cpu,initialization=initialization,law_initial=initialization['law'],law_final=m.law.detach().tolist(),forcing_parameter_delta_l2=float(sum(((m.state_dict()[k]-v)**2).sum() for k,v in initial_force.items()).sqrt()),K_initial=initialization['K'],K_final=float(2*torch.sigmoid(m.law[3])),J_effective=0. if arm=='N2J0' else float(torch.sigmoid(m.law[2])),attack_resets=0,forward_dense_multiply_add_flops_upper_bound=prior_flops+training.FORWARD_FLOPS,encoder_calls=prior_encoder+training.ENCODER_CALLS,phase_rhs_evaluations=prior_phase+training.PHASE_RHS,flops_scope='conservative dense forward upper bound with at most64 members per family across refresh/train/diagnostics; excludes nonlinear kernels and optimizer/backward',learned_law_interpretation='local geometry-mode imitation only; no source recursion claim; no attack resets',status='FIT_COMPLETE_PARITY_PENDING')
    write(out/(arm+'.outcome.json'),result)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--arm',choices=ARMS,required=True);p.add_argument('--deadline',type=float,required=True);p.add_argument('--cap',type=float,required=True);p.add_argument('--fds',type=int,nargs=2,required=True);a=p.parse_args()
    from jobs import inherited
    inherited(a.fds);os.nice(10)
    import training
    from collect import a0
    training.MONITOR=a0()
    fit(a.arm,TrainingDeadline(HERE,a.deadline,a.cap))
