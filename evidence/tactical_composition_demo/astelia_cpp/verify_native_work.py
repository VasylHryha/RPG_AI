"""Separate instrumented work audit bound to fresh unchanged timing outputs."""
import argparse,json,pathlib,subprocess,math
from result_cache import identity,sha,encoded,digest
ROOT=pathlib.Path(__file__).resolve().parent
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--benchmark',type=pathlib.Path,required=True);ap.add_argument('--output',type=pathlib.Path,required=True);args=ap.parse_args();args.output.mkdir(parents=True,exist_ok=True)
    if (args.output/'work_audit.json').exists():ap.error('use fresh evidence')
    benchmark=json.loads((args.benchmark/'benchmark.json').read_text());workloads=json.loads((ROOT/'native_workloads.json').read_text())['groups'];command=['node',str(ROOT/'work_audit_host.cjs')];native_command=[str(ROOT/'build/astelia_native'),'--metrics']
    native_id=identity('cpp',native_command)
    if native_id!=benchmark['identities']['cpp']:raise RuntimeError('work and timing engines differ')
    audit_id=identity('js',command);record=dict(status='RUNNING',benchmark_sha256=sha(args.benchmark/'benchmark.json'),native_identity=native_id,audit_identity=audit_id,harness_sha256=sha(pathlib.Path(__file__)),groups={})
    for name,requests in workloads.items():
        print('work audit: '+name,flush=True);payload=b'\n'.join(encoded(r) for r in requests)+b'\n';run=subprocess.run(command,input=payload,capture_output=True,check=True);outputs=[json.loads(s) for s in run.stdout.splitlines()];work=json.loads(run.stderr);baseline=[json.loads(s) for s in (args.benchmark/f'{name}_js_0.jsonl').read_text().splitlines()]
        if outputs!=baseline:raise RuntimeError('instrumentation changed JS outputs: '+name)
        (args.output/f'{name}_js.jsonl').write_bytes(run.stdout);(args.output/f'{name}_js_work.json').write_bytes(run.stderr)
        native=benchmark['groups'][name]['samples']['cpp'][0]['execution']
        if work['executed_fights']!=len(requests) or work['cache_hits'] or native['cache_hits']:raise RuntimeError('work audit used cached/missing fights')
        for label,counters in (('js',work),('cpp',native)):
            if counters['forks']!=counters['candidate_models']+counters['artillery_rollouts']:raise RuntimeError(label+' fork accounting mismatch')
            if label=='js':settings=[(*map(float,k.split('/')),v) for k,v in counters['fork_settings'].items()]
            else:settings=counters['fork_settings']
            if sum(n for dt,h,n in settings)!=counters['forks']:raise RuntimeError(label+' missing fork settings')
            if any(not (math.isclose(h,2,abs_tol=1e-10) or math.isclose(h,3,abs_tol=1e-10)) or not (math.isclose(dt,.1,abs_tol=1e-12) or math.isclose(dt,1/30,abs_tol=1e-12)) for dt,h,n in settings):raise RuntimeError('configured branch work changed')
        required=('search_calls','inference_calls','candidate_models','branch_steps') if name in ('elite','elite-fast') else ('artillery_rollouts','branch_steps') if name=='artillery-rollout' else ()
        if any(work[k]<=0 or native[k]<=0 for k in required):raise RuntimeError('intended work absent')
        record['groups'][name]=dict(requests_sha256=digest(requests),instrumentation_preserves_output=True,js=work,native=native,ratios={k:native[k]/work[k] if work[k] else None for k in ('executed_steps','branch_steps','forks','candidate_models','artillery_rollouts','inference_calls','unit_actions','projectile_steps','branch_unit_actions','branch_projectile_steps','prediction_steps')})
    if identity('js',command)!=audit_id or identity('cpp',native_command)!=native_id:raise RuntimeError('engine changed during audit')
    record['status']='WORK_AUDIT_PASSED';(args.output/'work_audit.json').write_text(json.dumps(record,indent=2)+'\n');print(record['status']);return 0
if __name__=='__main__':raise SystemExit(main())
