"""Validation-only per-role fire operating point, with precision/recall."""
import runtime as r
import numpy as np,torch,time
from models import initial
from training import forward,selected_starts,WINDOW
ROLES=('melee','ranged','artillery')

def choose(scores,truth,allowed):
    scores=np.asarray(scores,dtype=np.float64);truth=np.asarray(truth,dtype=bool);allowed=np.asarray(allowed,dtype=bool)
    if len(scores)==0 or len(scores)!=len(truth) or len(scores)!=len(allowed) or not np.isfinite(scores).all():raise ValueError('calibration rows')
    # Choose the closest attainable active count. Ties are kept together.
    values,counts=np.unique(scores[allowed],return_counts=True);values=values[::-1];counts=counts[::-1]
    candidates=np.r_[0,np.cumsum(counts)];desired=int(truth.sum());i=int(np.argmin(abs(candidates-desired)))
    threshold=float(values[0]+1 if i==0 and len(values) else (values[i-1]+values[i])/2 if i<len(values) else values[-1]-1 if len(values) else 1e9)
    predicted=allowed & (scores>=threshold);tp=int((predicted&truth).sum());fp=int((predicted&~truth).sum());fn=int((~predicted&truth).sum())
    return dict(threshold=threshold,rows=len(scores),oracle_active=desired,predicted_active=int(predicted.sum()),rate_error=(int(predicted.sum())-desired)/len(scores),tp=tp,fp=fp,fn=fn,precision=tp/max(1,tp+fp),recall=tp/max(1,tp+fn),allowed_rows=int(allowed.sum()))

def collect_scores(model,fights,deadline):
    values={role:dict(scores=[],truth=[],allowed=[]) for role in ROLES}
    with torch.no_grad():
        for fight in fights:
            starts=selected_starts(fight['frames'],4);state=initial(model.kind,[]);ids=[];cache=None;nextframe=(0,[])
            for tick,row in enumerate(r.data.frames(fight['raw_file'])):
                if time.monotonic()>=deadline:raise TimeoutError('calibration deadline')
                y,state,ids,enemies,cache,nextframe,_=forward(model,row,state,ids,cache,nextframe)
                if not any(at<=tick<at+WINDOW for at in starts):continue
                byid={v['id']:v for v in row['labels']};own={v[0]:v for v in row['own']}
                for i,id in enumerate(ids):
                    lab=byid[id];v=values[lab['role']];s=own[id]
                    v['scores'].append(float(torch.max(y['fire'][i,[0,2]])-y['fire'][i,1]));v['truth'].append(lab['executed']['fire']!='hold');v['allowed'].append(not lab['active'] and s[1]<=row['t'] and not s[7])
    return values

def fit(model,fights,deadline):
    return {role:choose(**v) for role,v in collect_scores(model,fights,deadline).items()}

def fire_classes(logits,roles,thresholds):
    a=np.asarray(logits);active=np.where(a[:,0]>=a[:,2],0,2)
    return np.where(np.maximum(a[:,0],a[:,2])-a[:,1]>=np.asarray(thresholds)[roles],active,1)
