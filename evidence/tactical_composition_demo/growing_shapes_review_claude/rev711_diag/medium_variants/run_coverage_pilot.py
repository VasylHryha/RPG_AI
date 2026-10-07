"""One-shot coverage worker; invoked only by execute_coverage_plan.py."""
import argparse
import contextlib
import hashlib
import io
import json
import os
import pickle
from pathlib import Path
import shutil
import sys
import time

OUT=Path(__file__).resolve().parent


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--variant',choices=['COVA','COVB'],required=True)
    parser.add_argument('--start',choices=['i','ii'],required=True)
    parser.add_argument('--keyset',type=int,choices=range(5),required=True)
    parser.add_argument('--observer',choices=['on','off'],default='on')
    parser.add_argument('--ticket',type=Path,required=True)
    args=parser.parse_args()
    ticket=json.loads(args.ticket.read_text())
    from execute_coverage_plan import process_check, check_frozen, validate_build, LOCAL, job_name
    check=process_check()
    if check['status']!='CLEAR': raise RuntimeError('worker process preflight: '+json.dumps(check))
    check_frozen(ticket['code_hashes'])
    if ticket['status']!='RUNNING' or time.time()>ticket['deadline_epoch']: raise RuntimeError('no current preflight grant')
    if [args.variant,args.start,args.keyset,args.observer] not in ticket['jobs']: raise RuntimeError('slot outside scheduler grant')
    if args.observer=='off' and (args.start,args.keyset)!=('i',0): raise ValueError('off only for specified integrity run')
    kernel=OUT/'kernel_builder/_worktrees'/args.variant
    build=json.loads((OUT/f'kernel_builder/{args.variant}_BUILD.json').read_text())
    binary=kernel/'evidence/tactical_composition_demo/growing_shapes/medium/_rev7_build'
    image=next(binary.glob('rev7_medium.*'))
    if hashlib.sha256(image.read_bytes()).hexdigest()!=build['build']['binary_sha256']: raise RuntimeError('binary changed')
    for name,digest in build['build']['source_sha256'].items():
        if hashlib.sha256((binary.parent/name).read_bytes()).hexdigest()!=digest: raise RuntimeError('source changed')
    if hashlib.sha256((binary.parent/'rev7_design.py').read_bytes()).hexdigest()!=build['design_sha256']: raise RuntimeError('design changed')
    harness=kernel/'evidence/tactical_composition_demo/growing_shapes_review_claude/rev711_diag/pilot_common.py'
    if hashlib.sha256(harness.read_bytes()).hexdigest()!=build['harness_sha256']: raise RuntimeError('scratch harness changed')
    if args.variant=='RD3' and hashlib.sha256((kernel/'service_graph.py').read_bytes()).hexdigest()!=build['service_graph_sha256']: raise RuntimeError('RD3 service graph changed')
    validate_build(args.variant)
    sys.path.insert(0,str(kernel));sys.path.insert(1,str(OUT))
    os.chdir(kernel);os.environ['PILOT_ASSAY']='1'
    from evidence.tactical_composition_demo.growing_shapes_review_claude.rev711_diag import pilot_common as P
    from evidence.tactical_composition_demo.growing_shapes.runner.rev7_run import Run
    from coverage_telemetry import install_observer, Observer
    name=f'{args.variant}_{args.start}_k{args.keyset}_{args.observer}'
    local=LOCAL; local.mkdir(exist_ok=True)
    # Exclusive marker persists on failure; never silently rerun a key.
    marker=local/(name+'.started')
    with marker.open('x') as f: f.write(json.dumps(vars(args),default=str))
    P.OUT=local/(name+'.harness');P.OUT.mkdir(exist_ok=False)
    state=hashlib.sha256()
    holder=install_observer(P,Run,args.variant,local/(name+'.jsonl.gz'),state,args.observer=='on')
    old_check=P.clone_isolation_check
    def observer_state():
        if holder[0] is None:return None
        obs=holder[0]
        payload={k:v for k,v in obs.__dict__.items() if k not in ('live','stream')}
        return hashlib.sha256(pickle.dumps(payload)).hexdigest(),obs.stream.tell()
    def kernel_state(m):
        return pickle.dumps({k:getattr(m,k,None) for k in ('coverage_wait','coverage_locks','coverage_recycled')})
    def clone_check(m):
        if args.observer=='on' and holder[0] is None:
            holder[0]=Observer(m,local/(name+'.jsonl.gz'),args.variant)
        before=(state.copy().hexdigest(),len(P.TRACE), holder[0].steps if holder[0] else 0,m.native.save(),observer_state(),kernel_state(m))
        old_check(m)
        after=(state.copy().hexdigest(),len(P.TRACE),holder[0].steps if holder[0] else 0,m.native.save(),observer_state(),kernel_state(m))
        if after!=before: raise AssertionError('clone leaked into observer/digest')
    P.clone_isolation_check=clone_check
    capture=io.StringIO(); wall=time.monotonic(); cpu=time.process_time()
    with contextlib.redirect_stdout(capture): P.run(args.start,'baseline',keyset=args.keyset)
    summary=json.loads(capture.getvalue().splitlines()[-1])
    result=dict(variant=args.variant,start=args.start,keyset=args.keyset,observer=args.observer,
                summary=summary,state_trajectory_sha256=state.hexdigest(),clone_isolation='PASS',
                telemetry=holder[0].finish() if holder[0] else None,
                elapsed_seconds=time.monotonic()-wall,cpu_seconds=time.process_time()-cpu,
                binary_sha256=build['build']['binary_sha256'],code_hashes=ticket['code_hashes'],ticket_sha256=hashlib.sha256(args.ticket.read_bytes()).hexdigest())
    tag='baseline_assay'+(f'_alt{args.keyset}' if args.keyset else '')
    raw=P.OUT/f'pilot_{tag}_{args.start}.json.gz'
    target=local/(name+'.legacy.json.gz');shutil.move(raw,target)
    raw_paths=[target]+([local/(name+'.jsonl.gz')] if holder[0] else [])
    result['raw_traces']=[dict(path=str(p.relative_to(OUT)),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in raw_paths]
    check_frozen(ticket['code_hashes'])
    if time.time()>ticket['deadline_epoch']: raise RuntimeError('deadline exceeded before completion')
    with (local/(name+'.summary.json')).open('x') as f: json.dump(result,f,separators=(',',':'),allow_nan=False);f.write('\n')
    print(json.dumps(dict(name=name,elapsed=result['elapsed_seconds'],cpu=result['cpu_seconds'],state_hash=state.hexdigest())))


if __name__=='__main__': main()
