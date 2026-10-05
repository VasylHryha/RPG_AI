"""Compare complete engineering artifacts without assigning scientific verdicts."""
import argparse
import gzip
import json
import math
from pathlib import Path
import re

TOLERANCE = 1e-10
HASH_KEYS = {'identity','initial_identity','initial_ids','qualified_ids','before_ids','after_ids',
             'end_ids','start_ids','operation_end_ids','snapshot_ids','snapshot','introduced_ids','next_operation_ids','source_trace_hash_by_dt'}
ROOT_COSTS = {'seconds','cpu_seconds','peak_rss_bytes','memory_measurement','native_build'}
EXACT_KEYS = {'inputs','perturbations','model','time','start','duration','dt_values','resolutions',
              'scope','world','turn','episode','first_loss_time','first_output_time_by_dt'}

def compare(left,right,tolerance=TOLERANCE,allow_digest_changes=True):
    result={'passed':True,'absolute_tolerance':tolerance,'maximum_error':0.,
            'numeric_values_compared':0,'decision_values_compared':0,'digest_values_changed':0,
            'failures':[]}
    def fail(path,why):
        result['passed']=False
        if len(result['failures'])<20:result['failures'].append({'path':path,'reason':why})
    def walk(a,b,path='',exact=False,hashes=False):
        if hashes:
            if isinstance(a,list) and isinstance(b,list) and len(a)==len(b):
                for i,(x,y) in enumerate(zip(a,b)):walk(x,y,path+'/'+str(i),hashes=True)
            elif isinstance(a,str) and isinstance(b,str) and re.fullmatch('[0-9a-f]{64}',a) and re.fullmatch('[0-9a-f]{64}',b):
                result['digest_values_changed']+=int(a!=b)
                if not allow_digest_changes and a!=b:fail(path,'digest differs on unchanged arithmetic')
            else:fail(path,'invalid digest inventory')
            return
        if isinstance(a,dict) and isinstance(b,dict):
            keys_a=set(a)-(ROOT_COSTS if not path else set())
            keys_b=set(b)-(ROOT_COSTS if not path else set())
            if keys_a!=keys_b:fail(path,'key inventory differs');return
            for k in sorted(keys_a):
                walk(a[k],b[k],path+'/'+k,exact or k in EXACT_KEYS,k in HASH_KEYS)
        elif isinstance(a,list) and isinstance(b,list):
            if len(a)!=len(b):fail(path,'array inventory differs');return
            for i,(x,y) in enumerate(zip(a,b)):walk(x,y,path+'/'+str(i),exact)
        elif type(a) is bool or type(b) is bool:
            result['decision_values_compared']+=1
            if type(a)!=type(b) or a!=b:fail(path,'decision flip')
        elif isinstance(a,(int,float)) and isinstance(b,(int,float)):
            result['numeric_values_compared']+=1
            if not math.isfinite(a) or not math.isfinite(b):fail(path,'nonfinite value');return
            error=abs(a-b);result['maximum_error']=max(result['maximum_error'],error)
            if error>(0. if exact or isinstance(a,int) and isinstance(b,int) else tolerance):fail(path,'numerical difference '+str(error))
        elif type(a)!=type(b) or a!=b:fail(path,'discrete value differs')
    walk(left,right)
    return result

def read(path):
    raw=path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix=='.gz' else raw)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--reference',type=Path,required=True)
    parser.add_argument('--native',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--fixture',action='store_true')
    parser.add_argument('--exact',action='store_true')
    args=parser.parse_args()
    if args.output.exists():raise FileExistsError(args.output)
    a,b=read(args.reference),read(args.native)
    if args.fixture:
        a={k:a[k] for k in ('initial_identity','descriptor','checks')}
        b={k:b[k] for k in ('initial_identity','descriptor','checks')}
    result=compare(a,b,0. if args.exact else TOLERANCE,not args.exact)
    result['reference']=str(args.reference);result['native']=str(args.native)
    args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result))
    return 0 if result['passed'] else 1

if __name__=='__main__':raise SystemExit(main())
