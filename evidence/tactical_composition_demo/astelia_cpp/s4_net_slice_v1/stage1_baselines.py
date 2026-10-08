"""Read-only head baselines and exact matched budget; no model/optimizer/fights.

This is useful when the process/resource gate prevents a training timing sample.
The same declared baselines are used by stage1_train.evaluate after actual fits.
"""
from collections import Counter
import numpy as np
from stage1_data import HERE,HEADS,load,read,sha,atomic,DATA
from stage1_train import environment,index,schedule,fire_stats,CONFIG,sources


def run():
    environment(); fights=index(); plan=schedule(fights); weights,modes,fire=fire_stats(fights)
    rows=sum(m['counts']['decision_rows'] for m in fights if m['split']=='train')
    budget=dict(**CONFIG,steps_per_epoch=len(plan),gradient_steps_per_arm=CONFIG['epochs']*len(plan),
                decision_rows_per_arm=CONFIG['epochs']*rows,positive_windows_per_epoch=sum(map(len,plan)),
                training_only_fire_weights=weights,fire_counts=fire,majority_modes=modes,
                dataset_index_sha256=sha(DATA/'INDEX.json'),sources=sources(),
                status='DECLARED_NOT_MEASURED',timing_steps=0)
    atomic(HERE/'STAGE1_BUDGET.json',budget)
    results={}
    for split in ('validation','test'):
        counts={k:Counter() for k in HEADS}
        for m in fights:
            if m['split']!=split:
                continue
            _,a=load(m['group'])
            for j,k in enumerate(HEADS):
                mask=a['masks'][...,j]; truth=np.asarray(a['labels'][...,j][mask]); c=counts[k]
                c['active']+=len(truth); c['excluded']+=int(a['alive'][::6].sum())-len(truth)
                c['majority_correct']+=int((truth==modes[k]).sum())
                if k in ('start','release'):
                    c['positive']+=int((truth==1).sum()); c['negative']+=int((truth==0).sum())
                else:
                    baseline=1 if k=='target' else 0
                    c['baseline_correct']+=int((truth==baseline).sum())
                    if k in ('move','aim') and len(truth):
                        points=np.asarray(a['offsets'][...,0 if k=='move' else 1,:,:][mask])
                        c['zero_error_px_sum']+=float(np.linalg.norm(points[:,0]-points[np.arange(len(truth)),truth],axis=1).sum())
        heads={}
        for k,c in counts.items():
            n=c['active']; positive=c['positive']
            if k in ('start','release'):
                heads[k]=dict(counts=dict(c),hold=dict(precision=None,recall=0 if positive else None,missed_readiness=1 if positive else None),
                              permit=dict(precision=positive/n if n else None,recall=1 if positive else None,missed_readiness=0 if positive else None))
            else:
                heads[k]=dict(counts=dict(c),baseline='nearest-target' if k=='target' else 'zero-offset',
                              top1=c['baseline_correct']/n if n else None,training_majority_top1=c['majority_correct']/n if n else None)
                if k in ('move','aim'):
                    heads[k]['zero_offset_mean_error_px']=c['zero_error_px_sum']/n if n else None
        results[split]=heads
    value=dict(status='MEASURED_BASELINES_ONLY',splits=results,
               teacher_repeat_baseline=read(HERE/'TEACHER_REPEAT_BASELINE.json'),dataset_index_sha256=sha(DATA/'INDEX.json'),
               source_sha256=sha(HERE/'stage1_baselines.py'),network_diagnostics='NOT_RUN: no fitted checkpoints',physical_fights=0,training_steps=0)
    atomic(HERE/'STAGE1_BASELINES.json',value)
    print(dict(steps_per_epoch=len(plan),steps_per_arm=budget['gradient_steps_per_arm'],rows_per_arm=budget['decision_rows_per_arm']))
    return value


if __name__=='__main__':
    run()
