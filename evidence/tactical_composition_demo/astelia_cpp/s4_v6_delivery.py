"""Scoped normal-hook commits and independently fetched delivery bundles."""
import argparse,hashlib,json,os,pathlib,subprocess
from s4_v6 import ROOT,CHECKS,BINARY,sha,write
from build_admission import admit
REPO=ROOT.parents[2]
PREFIX=str(ROOT.relative_to(REPO))+'/'

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--phase',choices=['implementation','report'],required=True);args=ap.parse_args()
    gitdir=ROOT/'build/s4_v6_delivery.git';branch='refs/heads/v6-development'
    if args.phase=='implementation':
        if gitdir.exists():raise RuntimeError('preserve existing implementation delivery')
        base=subprocess.check_output(['git','rev-parse','HEAD'],cwd=REPO,text=True).strip()
        subprocess.run(['git','clone','--bare','--shared',str(REPO),str(gitdir)],check=True,capture_output=True)
    else:
        prior=json.loads((CHECKS/'PART1_DELIVERY.json').read_text());base=prior['base']
        if not (CHECKS/'OWNER_RECHECK.md').read_text().startswith(('APPROVE_WITH_NOTES\n','APPROVE\n')):raise RuntimeError('report recheck disposition required')
    env=dict(os.environ,GIT_DIR=str(gitdir),GIT_WORK_TREE=str(REPO),GIT_INDEX_FILE=str(gitdir/'task.index'))
    def git(*args):return subprocess.check_output(['git',*args],cwd=REPO,env=env,text=True).strip()
    git('config','core.hooksPath',str(REPO/'.githooks'))
    if args.phase=='implementation':
        git('symbolic-ref','HEAD',branch);git('update-ref',branch,base);git('read-tree',base)
        files=['s4_v6.py','s4_v6_numerics.py','s4_v6_engineering.py','s4_v6_delivery.py','s4_v6_run_once.py',
               's4_v6_report.py','test_s4_v6.py','test_s4_v6_numerics.py','s3_v6_runner.py','build_v6.py',
               'native_s4_v6_contract.cpp','native_s4_v6_numerics.cpp','S4_V6_PROTOCOL.md','S4_V6_SEEDS.json',
               'S4_V6_PRESERVATION_PIN.json','S4_V6_CLAUDE_REVIEW_ATTEMPT.json','S4_V6_NO_COMBAT_PLAN.md','S4_V6_READINESS.md',
               'src/native/s4_v6_complex.h','src/native/s4_v6_complex.cpp','src/native/s4_v6_controller.h',
               'src/native/s4_v6_controller.cpp','src/native/s4_v6_dispatch.cpp','src/native/host_v6.cpp']
        files += ['s4_v6_numerical_checks/'+n for n in ('ACCEPTANCE.json','BUILD.json','INPUTS.json','KERNEL_CONTRACTS.json','TEST_RESULT.json')]
        files += ['s4_v6_checks/'+n for n in ('IMPLEMENTATION_RECHECK.json','NATIVE_CONTRACT.json','V6_CONTROLLER_CONTRACT.json',
                   'PRESERVATION.json','EXTERNAL_WORKSPACE_CHANGES.json','ENGINEERING_REFINEMENT.json','TEST_RESULT.json',
                   'FAILED_FIRST_TEST_RESULT.json','FAILED_SECOND_TEST_RESULT.json','READINESS.json','DELIVERY_NOTE.md')]
    else:
        files=['S4_V6_DEVELOPMENT_REPORT.md']+['s4_v6_checks/'+n for n in ('OWNER_RECHECK.md','REPORT_AUDIT.json','RAW_FILES_LOCAL.json','DELIVERY_NOTE.md','REPORT_IDENTITY.json','LAUNCH.json','SUPERVISOR_TIMING.json','LOAD_SUMMARY.json','PART1_DELIVERY.json','LEDGER_USED.json')]
        files += ['result_schema_v6.py','result_cache_v6.py','s4_v6_cache_repair.py','test_s4_v6_cache_repair.py']
        files += ['s4_v6_repair_checks/'+n for n in ('SOURCE_RECHECK.md','TEST_RESULT.json','FAILED_LAUNCH_TEST_RESULT.json','FINAL_PRESERVATION.json')]
        files += [n for n in ('s4_v6_report.py','s4_v6_delivery.py','s4_v6_run_once.py') if git('diff','--name-only','HEAD','--',PREFIX+n)]
        out=pathlib.Path(json.loads((CHECKS/'LAUNCH.json').read_text())['output'])
        files+=[str(out.relative_to(ROOT))+'/'+p.name for p in (out.iterdir() if out.exists() else []) if p.name in ('summary.json','failure.json','RUN_TIMING.json','run_identity.json','A_best.json','B_best.json','selected_omega.json')]
    names=[PREFIX+n for n in files];expected={n:(REPO/n).read_bytes() for n in names}
    if any(len(v)>=45_000_000 for v in expected.values()):raise RuntimeError('raw/oversize payload')
    git('add','--',*names);staged=git('diff','--cached','--name-only').splitlines()
    if set(staged)!=set(names):raise RuntimeError('scope mismatch')
    git('diff','--cached','--check')
    result=subprocess.run(['git','commit','-m',('Implement and verify 0g v6 complex controller' if args.phase=='implementation' else 'Report single 0g v6 A/B development and owner recheck')+'\n\nAssisted-by: Codex:GPT-6'],cwd=REPO,env=env,text=True,capture_output=True)
    (CHECKS/('COMMIT_'+args.phase+'.log')).write_text(result.stdout+result.stderr)
    if result.returncode:raise RuntimeError('normal hooks failed: '+result.stdout+result.stderr)
    commit=git('rev-parse','HEAD');bundle=ROOT/('S4_V6_'+args.phase.upper()+'.bundle')
    if bundle.exists():raise RuntimeError('preserve existing bundle')
    git('bundle','create',str(bundle),base+'..'+branch);git('bundle','verify',str(bundle))
    fresh=ROOT/('build/s4_v6_'+args.phase+'_fresh_fetch');subprocess.run(['git','clone','--shared','--no-checkout',str(REPO),str(fresh)],check=True,capture_output=True)
    subprocess.run(['git','fetch',str(bundle),branch],cwd=fresh,check=True,capture_output=True)
    if subprocess.check_output(['git','rev-parse','FETCH_HEAD'],cwd=fresh,text=True).strip()!=commit:raise RuntimeError('fetch identity mismatch')
    for n,data in expected.items():
        if subprocess.check_output(['git','show',commit+':'+n],cwd=fresh)!=data:raise RuntimeError('blob mismatch: '+n)
    receipt=dict(base=base,commit=commit,bundle=str(bundle),bundle_sha256=sha(bundle),bundle_bytes=bundle.stat().st_size,
                 independent_fetch_verified=True,normal_hooks_returncode=0,main_git_modified=False,provenance='Assisted-by: Codex:GPT-6',
                 committed_file_hashes={n:hashlib.sha256(v).hexdigest() for n,v in expected.items()})
    if args.phase=='implementation':
        native=admit(BINARY);runtime={n:sha(ROOT/n) for n in ['s4_v6.py','s4_v6_numerics.py','s3_v6_runner.py','s3_runner.py','s4_v4.py','s4_development.py','s4_deadline.py','result_cache.py','result_schema.py','build_admission.py','S4_V6_SEEDS.json','S4_V6_PROTOCOL.md','../DESIGN_0G.md','../../../docs/reviews/tactical_0g_s18_design_review_codex_r3.md']}
        runtime.update(native['sources']);runtime.update({str(p.relative_to(ROOT)):sha(p) for p in (ROOT/'build/s4_cma_vendor/cma').rglob('*.py')})
        runtime['build/astelia_native_v6']=native['binary_sha256'];runtime['build/astelia_native_v6.build.json']=native['manifest_sha256']
        receipt.update(implementation_commit=commit,runtime_hashes=runtime,binary_sha256=native['binary_sha256'],build_manifest_sha256=native['manifest_sha256'])
    write(CHECKS/('PART1_DELIVERY.json' if args.phase=='implementation' else 'DELIVERY_TRANSPORT.json'),receipt)
    print(json.dumps(dict(commit=commit,bundle=str(bundle),files=len(expected),verified=True)))

if __name__=='__main__':main()
