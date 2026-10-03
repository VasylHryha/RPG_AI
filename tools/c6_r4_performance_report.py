"""Reproduce the engineering comparison from preserved raw outputs; no runs."""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np

def compare(baseline,optimized):
    a=json.loads(baseline.read_text());b=json.loads(optimized.read_text())
    for key in ('kind','initial_identity','fixture_entropies','duration','elements_per_cohort','live_cohorts','probes','resolutions'):
        if a[key]!=b[key]:raise ValueError('unmatched fixture '+key)
    if a['kind']!='ENGINEERING_FIXTURE_ONLY' or (a['probes'],len(a['checks']),len(b['checks']))!=(50,51,51):
        raise ValueError('incomplete fixture coverage')
    for key in ('alpha','phase_origin_by_dt','site_ids','snapshot_ids'):
        if a['descriptor'][key]!=b['descriptor'][key]:raise ValueError('unmatched descriptor '+key)
    ar,br=a['descriptor']['raw'],b['descriptor']['raw']
    if len(ar)!=50 or len(br)!=50:raise ValueError('incomplete probes')
    raw_error=0.
    for x,y in zip(ar,br):
        if {k:v for k,v in x.items() if k!='response_real_imag'}!={k:v for k,v in y.items() if k!='response_real_imag'}:
            raise ValueError('unmatched realized probe')
        ax,bx=np.asarray(x['response_real_imag']),np.asarray(y['response_real_imag'])
        if ax.shape!=bx.shape or ax.shape!=(100,25,2) or not np.isfinite(ax).all() or not np.isfinite(bx).all():
            raise ValueError('incomplete/nonfinite raw response')
        raw_error=max(raw_error,float(np.abs(ax-bx).max()))
    per_probe=float(np.abs(np.asarray(a['descriptor']['per_probe_by_dt'])-np.asarray(b['descriptor']['per_probe_by_dt'])).max())
    checks_error=0.
    for x,y in zip(a['checks'],b['checks']):
        for key in ('scope','duration','dt_values'):
            if x[key]!=y[key]:raise ValueError('unmatched scope '+key)
        if not x['passed'] or not y['passed']:raise ValueError('failed full-state check')
        checks_error=max(checks_error,max(abs(x['max_errors'][k]-y['max_errors'][k]) for k in x['max_errors']))
    if not np.isfinite([raw_error,per_probe,checks_error]).all() or max(raw_error,per_probe,checks_error)>=1e-10:
        raise ValueError('engineering equivalence failure')
    return {'kind':'REPRODUCED_ENGINEERING_PERFORMANCE_COMPARISON','passed':True,'tolerance':1e-10,
            'baseline_seconds':a['seconds'],'optimized_seconds':b['seconds'],'speedup':a['seconds']/b['seconds'],
            'baseline_calls':a['calls'],'optimized_calls':b['calls'],'maximum_raw_response_error':raw_error,
            'maximum_per_probe_gain_error':per_probe,'maximum_full_state_check_difference':checks_error,
            'raw_artifacts_sha256':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in (baseline,optimized)}}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline',type=Path,required=True);parser.add_argument('--optimized',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    if args.output.exists():raise FileExistsError(args.output)
    result=compare(args.baseline,args.optimized)
    args.output.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print(json.dumps({k:result[k] for k in ('passed','speedup','maximum_raw_response_error')}))
if __name__=='__main__':main()
