"""Persist actual initialization and parent identities across epoch resume."""
import math
import torch
import runtime as r

def capture(model):
    law=model.law.detach().cpu().tolist()
    result=dict(variant=r.VARIANT,law=law,K=float(2*torch.sigmoid(model.law[3]).detach()),forcing_sha256=__import__('hashlib').sha256(b''.join(v.detach().cpu().numpy().tobytes() for k,v in model.state_dict().items() if k.startswith('force.'))).hexdigest(),warm_start=None)
    if r.VARIANT=='learned_dodge':
        from enable_dodge import check,OFF
        parent=check();result['warm_start']=dict(readiness_sha256=r.sha(OFF/'DODGE_READY.json'),checkpoint=parent['checkpoints'][model.kind])
    return result

def resumed(saved,current):
    prior=saved.get('initialization')
    if prior!=current:raise RuntimeError('resume initialization/warm-start identity drift')
    return prior
