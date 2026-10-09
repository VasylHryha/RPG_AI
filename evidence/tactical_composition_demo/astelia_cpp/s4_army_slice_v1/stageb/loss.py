"""Training-only target balance and geometric losses in existing 100 px units."""
import runtime as r
import time,torch
import training
BASE_OBJECTIVE=training.objective

def target_weights(fights,deadline):
    counts={role:[0,0] for role in ('melee','ranged','artillery')}
    for fight in fights:
        starts=training.selected_starts(fight['frames'],4)
        for tick,row in enumerate(r.data.frames(fight['raw_file'])):
            if time.monotonic()>=deadline:raise TimeoutError('target class counting cap')
            if not any(at<=tick<at+training.WINDOW for at in starts):continue
            for lab in row['labels']:counts[lab['role']][int(lab['executed']['target']!=0)]+=1
    if any(not all(v) for v in counts.values()):raise RuntimeError('both target None/nonzero classes required per role')
    return {role:dict(counts=c,weights=[sum(c)/(2*c[0]),sum(c)/(2*c[1])]) for role,c in counts.items()}

def install(balance):
    def objective(y,row,ids,enemies,weights=None):
        value,heads=BASE_OBJECTIVE(y,row,ids,enemies,None)
        labs=training.labels(row,ids,enemies)
        if not labs:return value,heads
        def vals(key):return y['move'].new_tensor([v[key] for v in labs])
        target=vals('target').long();scale=y['move'].new_tensor([row['width'],row['height']]);move=y['move']+y['drift']/scale;mask=vals('aim_mask').bool()
        ce=torch.nn.functional.cross_entropy(y['target'],target,reduction='none')
        wt=ce.new_tensor([balance[v['role']]['weights'][int(v['target']!=0)] for v in labs]);target_loss=(ce*wt).sum()/wt.sum()
        old_move=torch.mean((move-vals('move'))**2);old_aim=torch.mean((y['aim'][mask]-vals('aim')[mask])**2) if mask.any() else y['aim'].sum()*0
        movement=torch.nn.functional.smooth_l1_loss(move*scale/100,vals('move')*scale/100)
        aim=torch.nn.functional.smooth_l1_loss(y['aim'][mask]*scale/100,vals('aim')[mask]*scale/100) if mask.any() else y['aim'].sum()*0
        value=value-ce.mean()-old_move-old_aim+target_loss+movement+aim
        heads.update(target=float(target_loss.detach()),move=float(movement.detach()),aim=float(aim.detach()))
        return value,heads
    training.objective=objective
