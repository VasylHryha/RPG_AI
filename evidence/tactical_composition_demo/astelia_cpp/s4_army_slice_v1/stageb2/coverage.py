"""Whole-fight expressiveness audit; no training or fights. Cap and lock required."""
import argparse,time,secrets
import runtime as r
from candidates import mapped_labels,TOLERANCE,AIM_OFFSET,MOVE_OFFSET

def accumulate(counts,row):
    ids=sorted(v[0] for v in row['units'] if v[1]==0)
    for lab in mapped_labels(row,ids):
        for name in ('move','aim'):
            v=lab[name]
            if v is None:continue
            for category in ('all', 'dodge' if lab['dodge'] else 'ordinary'):
                c=counts.setdefault((lab['role'],name,category),dict(rows=0,covered=0,representable=0,no_candidates=0,distance_sum=0.,max_distance=0.))
                c['rows']+=1;c['covered']+=v['covered'];c['representable']+=v['representable']
                if v['distance'] is None:c['no_candidates']+=1
                else:c['distance_sum']+=v['distance'];c['max_distance']=max(c['max_distance'],v['distance'])

def report(counts):
    return {':'.join(key):dict(c,coverage=c['covered']/c['rows'],bounded_residual_coverage=c['representable']/c['rows'],mean_distance=c['distance_sum']/max(1,c['rows']-c['no_candidates'])) for key,c in counts.items()}

def run(round):
    from train import configure,prepare
    from jobs import admitted
    from training_control import training_cap,TrainingDeadline
    local=configure(round);index=prepare(round);token=secrets.token_hex(8);start=time.monotonic();receipt=dict(status='RUNNING',index_sha256=r.sha(local/'INDEX.json'),sources=r.sources(),records=[])
    cap=training_cap(r.HERE)
    try:
        with admitted(cap['cap_seconds']) as (absolute,monitor):
            deadline=TrainingDeadline(r.HERE,absolute,cap['cap_seconds']);counts={};mass=0
            for at,f in enumerate(index['fights']):
                if r.sha(f['raw_file'])!=f['raw_sha256']:raise RuntimeError('coverage shard drift')
                for row in r.data.frames(f['raw_file']):
                    if time.monotonic()>=deadline:raise TimeoutError('coverage live cap')
                    accumulate(counts.setdefault(f['split']+':'+f.get('arm','shared'),{}),row);mass+=1
                    if mass%30==0:monitor.live_memory(__import__('os').getpid())
                receipt['records'].append(dict(tag=f['tag'],split=f['split'],raw_sha256=f['raw_sha256']))
                if at==0:
                    projection=1.2*(time.monotonic()-start)/max(1,mass)*sum(q['frames'] for q in index['fights'][1:]);receipt['projected_remaining_seconds']=projection
                    if projection>deadline-time.monotonic():raise RuntimeError('coverage projection exceeds cap')
            result={split:report(c) for split,c in counts.items()};receipt.update(status='DONE',coverage=result,tolerance_px=TOLERANCE,offset_px=dict(aim=AIM_OFFSET,move=MOVE_OFFSET),interpretation='candidate-only coverage and bounded residual coverage, including O executed dodges; no conditional action or closed-loop sufficiency claim')
            r.write(local/'COVERAGE.json',receipt,exclusive=True)
    except BaseException as e:receipt.update(status='STOP',error=str(e));raise
    finally:receipt['seconds']=time.monotonic()-start;r.write(r.HERE/('COVERAGE_RUN_'+token+'.json'),receipt,exclusive=True)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--round',type=int,choices=(0,1,2),default=0);run(p.parse_args().round)
