"""Reproduce the engineering comparison from preserved raw outputs; no runs."""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np

def finite_array(value,shape,name,nonnegative=True):
    array=np.asarray(value,float)
    if array.shape!=shape or not np.isfinite(array).all() or (nonnegative and np.any(array<0)):
        raise ValueError('invalid '+name)
    return array

def descriptor_contract(record):
    d=record['descriptor'];sites=d['site_ids'];ns=len(sites)
    if ns!=25 or len(set(sites))!=ns or len(record['checks'])!=51:raise ValueError('invalid site/check inventory')
    finite_array(d['phase_origin_by_dt'],(3,),'phase origins',False)
    finite_array([d['alpha']],(1,),'alpha',False)
    per_probe=finite_array(d['per_probe_by_dt'],(3,50),'per-probe gains')
    gains=finite_array(d['gain_by_dt'],(3,),'mean gains')
    if not np.allclose(gains,per_probe.mean(1),rtol=0.,atol=1e-12):raise ValueError('inconsistent mean gain')
    expected=[(port,q) for port in sites for q in (0,1)]
    if [(r['port'],r['quadrature']) for r in d['raw']]!=expected:raise ValueError('incomplete/duplicate probe inventory')
    for i,row in enumerate(d['raw']):
        raw=finite_array(row['response_real_imag'],(100,25,2),'raw response',False)
        phases=finite_array(row['probe_phase_by_dt'],(3,),'probe phases',False)
        if not np.allclose(phases,d['alpha']+np.asarray(d['phase_origin_by_dt'])+row['quadrature']*np.pi/2,rtol=0.,atol=1e-12):
            raise ValueError('inconsistent realized probe phase')
        raw_gain=float(np.sqrt(np.mean(np.sum(raw*raw,axis=-1))))
        if not np.isfinite(raw_gain) or abs(raw_gain-per_probe[0,i])>1e-12:raise ValueError('gain differs from raw response')
    errors=[]
    for i,c in enumerate(record['checks']):
        if c.get('passed') is not True or set(c['max_errors'])!={'position','phase','field'}:raise ValueError('failed/incomplete full-state check')
        errors.append(finite_array([c['max_errors'][k] for k in ('position','phase','field')],(3,),'full-state errors'))
        finite_array(c['dt_values'],(3,),'check grids')
        finite_array([c['start'],c['duration']],(2,),'check clock')
        if c['duration']!=10. or not np.array_equal(c['dt_values'],record['resolutions']):raise ValueError('incomplete time/grid coverage')
        expected_suffix='/control' if i==0 else f'/port{(i-1)//2}/q{(i-1)%2}'
        if not c['scope'].endswith(expected_suffix):raise ValueError('unmatched check/probe scope')
        sizes=finite_array(c['normalization_sizes'],(2,),'normalization')
        if np.any(sizes<=0):raise ValueError('invalid normalization')
        if abs(c['start']-record['checks'][0]['start'])>1e-10:raise ValueError('unmatched probe clock')
        maxima=finite_array(c['output_max_by_dt'],(3,),'outgoing maxima')
        powers=finite_array(c['output_power_by_dt'],(3,25),'outgoing powers')
        if np.any(maxima) or np.any(powers) or c['first_output_time_by_dt']!=[None]*3:
            raise ValueError('nonzero descriptor source channel')
        if np.any(errors[-1]>.05):raise ValueError('unqualified full-state errors')
        hashes=c['source_trace_hash_by_dt']
        if (len(hashes)!=3 or any(not isinstance(h,str) or len(h)!=64 or any(x not in '0123456789abcdef' for x in h) for h in hashes)
                or hashes!=record['checks'][0]['source_trace_hash_by_dt']):
            raise ValueError('probe changes independent source trajectory')
    finite_array([record['seconds']],(1,),'timing')
    if record['seconds']<=0:raise ValueError('nonpositive timing')
    return np.asarray(errors),per_probe

def compare(baseline,optimized):
    a=json.loads(baseline.read_text());b=json.loads(optimized.read_text())
    for key in ('kind','initial_identity','fixture_entropies','duration','elements_per_cohort','live_cohorts','probes','resolutions'):
        if a[key]!=b[key]:raise ValueError('unmatched fixture '+key)
    if a['kind']!='ENGINEERING_FIXTURE_ONLY' or (a['probes'],len(a['checks']),len(b['checks']))!=(50,51,51):
        raise ValueError('incomplete fixture coverage')
    if a['duration']!=10. or a['resolutions']!=[.005,.0025,.00125]:raise ValueError('unmatched engineering grids/horizon')
    for key in ('alpha','phase_origin_by_dt','site_ids','snapshot_ids'):
        if a['descriptor'][key]!=b['descriptor'][key]:raise ValueError('unmatched descriptor '+key)
    ae,ap=descriptor_contract(a);be,bp=descriptor_contract(b)
    raw_error=0.
    for x,y in zip(a['descriptor']['raw'],b['descriptor']['raw']):
        if {k:v for k,v in x.items() if k!='response_real_imag'}!={k:v for k,v in y.items() if k!='response_real_imag'}:
            raise ValueError('unmatched realized probe')
        raw_error=max(raw_error,float(np.abs(np.asarray(x['response_real_imag'])-np.asarray(y['response_real_imag'])).max()))
    for x,y in zip(a['checks'],b['checks']):
        for key in ('scope','duration','dt_values'):
            if x[key]!=y[key]:raise ValueError('unmatched scope '+key)
        if abs(x['start']-y['start'])>1e-10:raise ValueError('unmatched initial clock')
    per_probe=float(np.abs(ap-bp).max());checks_error=float(np.abs(ae-be).max())
    if max(raw_error,per_probe,checks_error)>=1e-10:raise ValueError('engineering equivalence failure')
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
