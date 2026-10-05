"""Bind complete native engineering evidence; never promote scientific status."""
import argparse,json,pathlib,math
from result_cache import sha,identity
from build_admission import admit
ROOT=pathlib.Path(__file__).resolve().parent
def assess(coverage,costs,work,benchmark,tests):
    if tests.get('exit_code')!=0:return 'TESTS_FAILED'
    if coverage.get('status')!='NATIVE_COVERAGE_PASSED' or sum(coverage.get('counts',{}).values())!=623 or len(coverage.get('traces',[]))!=20:return 'INCOMPLETE_COVERAGE'
    if any(not row.get('equal') for row in coverage.get('determinism',[])) or len(coverage.get('determinism',[]))<20:return 'NONDETERMINISTIC'
    if costs.get('status')!='MATCHED_COSTS_PASSED' or set(costs.get('costs',{}))!={'geometry','network','fork_playout'} or any(v.get('speed_up',0)<=1 for v in costs.get('costs',{}).values()):return 'MISSING_MATCHED_COSTS'
    if work.get('status')!='WORK_AUDIT_PASSED' or set(work.get('groups',{}))!={'basic50','elite','elite-fast','artillery-rollout'}:return 'MISSING_WORK_AUDIT'
    if benchmark.get('status')!='TIMING_PASSED_AWAITING_WORK_AND_CORRECTNESS_REVIEW':return 'TIMING_FAILED'
    if set(benchmark.get('groups',{}))!={'basic50','elite','elite-fast','artillery-rollout'}:return 'INCOMPLETE_TIMING'
    for name,group in benchmark['groups'].items():
        if not math.isfinite(group.get('speed_up',0)) or group['speed_up']<3:return 'BELOW_MINIMUM'
        samples=group.get('samples',{});js=samples.get('js',[]);cpp=samples.get('cpp',[])
        if len(js)!=2 or len(cpp)!=2:return 'INCOMPLETE_TIMING'
        if any(s.get('execution',{}).get('cache_hits')!=0 or s.get('execution',{}).get('executed_fights')!=group['count'] for s in js+cpp):return 'CACHED_OR_MISSING_WORK'
        # Every balanced sample must support the minimum, and CPU must support
        # it too. This cannot promote a ratio produced by selecting fast runs.
        if min(s['wall_seconds'] for s in js)/max(s['wall_seconds'] for s in cpp)<3:return 'UNSTABLE_TIMING'
        cpu=lambda rows:sum(s['user_seconds']+s['system_seconds'] for s in rows)
        if cpu(cpp)<=0 or cpu(js)/cpu(cpp)<3:return 'CPU_COST_NOT_IMPROVED'
    return 'ENGINEERING_READY'
def main():
    ap=argparse.ArgumentParser()
    for name in ('coverage','costs','work','benchmark','tests'):ap.add_argument('--'+name,type=pathlib.Path,required=True)
    ap.add_argument('--sanitizer',type=pathlib.Path,required=True)
    ap.add_argument('--output',type=pathlib.Path,required=True);args=ap.parse_args()
    if args.output.exists():ap.error('use fresh qualification receipt')
    paths={name:getattr(args,name) for name in ('coverage','costs','work','benchmark','tests')};records={name:json.loads(p.read_text()) for name,p in paths.items()}
    test_hashes=records['tests'].get('source_hashes',{})
    if not test_hashes or any(sha(ROOT/name)!=expected for name,expected in test_hashes.items()):raise RuntimeError('tests do not bind current source and evaluators')
    sanitizer=json.loads(args.sanitizer.read_text());sanitized=ROOT/'build/native_full_contract_sanitized';admit(sanitized)
    if sanitizer.get('exit_code')!=0 or sanitizer.get('build_exit')!=0 or sanitizer.get('binary_sha256')!=sha(sanitized) or sanitizer.get('build_manifest_sha256')!=sha(sanitized.with_suffix('.build.json')) or (args.sanitizer.parent/'sanitizer.stderr.txt').read_bytes():raise RuntimeError('sanitizer evidence does not bind clean current instrumented engine')
    current=identity('cpp',[str(ROOT/'build/astelia_native'),'--metrics']);plain=identity('cpp',[str(ROOT/'build/astelia_native')])
    if records['costs']['identities']['cpp']!=identity('cpp',[str(ROOT/'build/native_matched_probe')]):raise RuntimeError('matched costs do not bind current source/probe')
    if records['benchmark']['identities']['cpp']!=current or records['work']['native_identity']!=current or records['coverage']['native_identity']!=plain:raise RuntimeError('receipts do not bind current engine')
    if records['work']['benchmark_sha256']!=sha(args.benchmark):raise RuntimeError('work/timing receipt mismatch')
    for trace in records['coverage']['traces']:
        if sha(args.coverage.parent/trace['file'])!=trace['sha256']:raise RuntimeError('retained trace changed')
    if records['coverage']['harness_sha256']!=sha(ROOT/'verify_native.py') or records['costs']['harness_sha256']!=sha(ROOT/'verify_native_costs.py') or records['work']['harness_sha256']!=sha(ROOT/'verify_native_work.py'):raise RuntimeError('evaluator identity changed')
    ledger=json.loads((ROOT/'native_feature_ledger.json').read_text())
    if len(ledger['functions'])!=159 or any(v['status']!='IMPLEMENTED_NATIVE' for v in ledger['functions'].values()):raise RuntimeError('feature migration ledger incomplete')
    status=assess(**records);paths['sanitizer']=args.sanitizer;result=dict(status=status,scope='engineering only; independent review remains required before an AI experiment',native_identity=current,receipts={name:dict(path=str(p),sha256=sha(p)) for name,p in paths.items()},feature_ledger_sha256=sha(ROOT/'native_feature_ledger.json'),qualification_harness_sha256=sha(pathlib.Path(__file__)),speedups={name:g['speed_up'] for name,g in records['benchmark']['groups'].items()},minimum=3,target=5)
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(status=status,speedups=result['speedups']),indent=2));return 0 if status=='ENGINEERING_READY' else 1
if __name__=='__main__':raise SystemExit(main())
