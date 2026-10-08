"""Categorical modes never average opposed safe directions; no Gaussian variance."""
import torch
from torch.nn import functional as F

WEIGHTS={'move':1.,'target':1.,'start':.5,'release':.5,'aim':1.}

def losses(logits,labels,masks,legal,fire_positive_weights=(1.,1.)):
    if not torch.isfinite(logits).all():raise FloatingPointError('invalid batch; no optimizer update')
    parts={}
    for name,begin,end in (('move',0,33),('target',33,46),('aim',48,81)):
        active=masks[name].bool()
        if bool(active.any()):
            scores=logits[active,begin:end];allowed=legal[name][active].bool();truth=labels[name][active].long()
            if not bool(allowed.any(-1).all()) or not bool(allowed.gather(1,truth[:,None]).all()):raise ValueError('unsupported teacher label')
            parts[name]=F.cross_entropy(scores.masked_fill(~allowed,float("-inf")),truth)
        else:parts[name]=logits.sum()*0
    for name,col,weight in (('start',46,fire_positive_weights[0]),('release',47,fire_positive_weights[1])):
        active=masks[name].bool();weight=max(1.,min(10.,float(weight)))
        parts[name]=F.binary_cross_entropy_with_logits(logits[active,col],labels[name][active].double(),pos_weight=logits.new_tensor(weight)) if bool(active.any()) else logits.sum()*0
    return sum(WEIGHTS[k]*v for k,v in parts.items()),parts

def fire_weights(labels,masks):
    return tuple(min(10.,max(1.,float((labels[k][masks[k]]==0).sum())/max(1,float((labels[k][masks[k]]==1).sum())))) for k in ('start','release'))
