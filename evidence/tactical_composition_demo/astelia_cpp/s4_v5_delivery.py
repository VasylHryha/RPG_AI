"""Normal-hook commit in an isolated Git directory; verify scope and a fresh fetch."""
import hashlib
import json
import os
import pathlib
import subprocess
from s4_development import ROOT,sha,write
from build_admission import admit

REPO=ROOT.parents[2]
PREFIX=str(ROOT.relative_to(REPO))+'/'
CHECKS=ROOT/'s4_v5_part1_checks'
REVIEW='docs/reviews/tactical_0g_s17_design_review_codex_r2.md'
FILES=['.gitignore','s3_runner.py','src/native/controller.cpp','src/native/s3_controller.cpp',
       'native_s4_attribution_contract.cpp','s4_v5.py','s4_v5_delivery.py','test_s4_v5.py',
       'S4_V5_SEEDS.json','S4_V5_PROTOCOL.md','S4_V5_DESIGN_PIN.md','S4_V5_READINESS.md',
       's4_v5_part1_checks/PLAN_AND_REVIEW.md','s4_v5_part1_checks/OWNER_RECHECK.md',
       's4_v5_part1_checks/CLAUDE_REVIEW_ATTEMPT.json','s4_v5_part1_checks/NATIVE_CONTRACT.json',
       's4_v5_part1_checks/BUILD_RESULT.json','s4_v5_part1_checks/TEST_RESULT.json',
       's4_v5_part1_checks/DELIVERY_NOTE.md',
       's4_v5_part1_checks/FAILED_FIRST_TEST_RESULT.json',
       's4_v5_part1_checks/FAILED_FIRST_TESTS.stdout.txt','s4_v5_part1_checks/FAILED_FIRST_TESTS.stderr.txt',
       's4_v5_part1_checks/TESTS.stdout.txt','s4_v5_part1_checks/TESTS.stderr.txt',
       's4_v5_part1_checks/BUILD.stdout.txt','s4_v5_part1_checks/BUILD.stderr.txt']
RUNTIME=['test_s4_v5.py','test_s4_deadline.py','s4_v5.py','s4_v4.py','s4_development.py','s3_runner.py','s4_deadline.py','s4_v4_replay.py',
         'result_cache.py','result_schema.py','build_admission.py','S4_V5_SEEDS.json',
         'S4_V5_PROTOCOL.md','S4_V5_DESIGN_PIN.md','S4_AMENDED_PROTOCOL.md','s4_replay.html']


def main():
    repo_git=ROOT/'build/s4_v5_part1.git'
    verify=ROOT/'build/s4_v5_fresh_fetch'
    bundle=ROOT/'S4_V5_PART1.bundle'
    if repo_git.exists() or verify.exists() or bundle.exists():raise RuntimeError('delivery exists; preserve it')
    base=subprocess.check_output(['git','rev-parse','HEAD'],cwd=REPO,text=True).strip()
    subprocess.run(['git','clone','--bare','--shared',str(REPO),str(repo_git)],check=True,capture_output=True)
    env=dict(os.environ,GIT_DIR=str(repo_git),GIT_WORK_TREE=str(REPO),GIT_INDEX_FILE=str(repo_git/'task.index'))
    def git(*args):return subprocess.check_output(['git',*args],cwd=REPO,env=env,text=True).strip()
    git('config','core.hooksPath',str(REPO/'.githooks'))
    git('symbolic-ref','HEAD','refs/heads/v5-part1');git('update-ref','refs/heads/v5-part1',base)
    git('read-tree',base)
    names=[PREFIX+n for n in FILES]+[REVIEW]
    for name in names:
        if not (REPO/name).is_file() or (REPO/name).stat().st_size>=50_000_000:raise RuntimeError('file/size mismatch: '+name)
    git('add','--',*names)
    staged=git('diff','--cached','--name-only').splitlines()
    if set(staged)!=set(names):raise RuntimeError('staging scope mismatch')
    result=subprocess.run(['git','commit','-m','Review amended 0g v5 and implement bounded A/B development readiness\n\nAssisted-by: Codex:GPT-6'],cwd=REPO,env=env,text=True,capture_output=True)
    (CHECKS/'COMMIT_HOOKS.txt').write_text(result.stdout+result.stderr)
    if result.returncode:raise RuntimeError('normal commit hooks failed: '+result.stdout+result.stderr)
    commit=git('rev-parse','HEAD')
    git('bundle','create',str(bundle),base+'..refs/heads/v5-part1');git('bundle','verify',str(bundle))
    subprocess.run(['git','clone','--shared','--no-checkout',str(REPO),str(verify)],check=True,capture_output=True)
    subprocess.run(['git','fetch',str(bundle),'refs/heads/v5-part1'],cwd=verify,check=True,capture_output=True)
    fetched=subprocess.check_output(['git','rev-parse','FETCH_HEAD'],cwd=verify,text=True).strip()
    if fetched!=commit:raise RuntimeError('independent fetch mismatch')
    changed=git('diff','--name-only',base,commit).splitlines()
    if set(changed)!=set(names):raise RuntimeError('commit scope mismatch')
    hashes={}
    for name in changed:
        blob=subprocess.check_output(['git','show',commit+':'+name],cwd=verify)
        if len(blob)>=50_000_000 or hashlib.sha256(blob).hexdigest()!=sha(REPO/name):raise RuntimeError('independent blob mismatch: '+name)
        hashes[name]=sha(REPO/name)
    runtime={name:sha(ROOT/name) for name in RUNTIME}
    runtime.update({str(p.relative_to(ROOT)):sha(p) for p in (ROOT/'build/s4_cma_vendor/cma').rglob('*.py')})
    build=admit(ROOT/'build/astelia_native')
    runtime.update(build['sources'])
    runtime['build/astelia_native']=build['binary_sha256']
    runtime['build/astelia_native.build.json']=build['manifest_sha256']
    receipt=dict(implementation_commit=commit,base=base,bundle=str(bundle),bundle_sha256=sha(bundle),bundle_bytes=bundle.stat().st_size,
                 independent_fetch_verified=True,committed_file_hashes=hashes,runtime_hashes=runtime,
                 binary_sha256=build['binary_sha256'],build_manifest_sha256=build['manifest_sha256'],
                 provenance='Assisted-by: Codex:GPT-6',hooks=git('config','core.hooksPath'),hook_returncode=0,
                 all_files_under_50_MB=True,development_run=False)
    if receipt['bundle_bytes']>=50_000_000:raise RuntimeError('bundle >=50 MB')
    write(CHECKS/'PART1_DELIVERY.json',receipt)
    print(json.dumps(dict(commit=commit,bundle=str(bundle),files=len(changed),verified=True)))


if __name__=='__main__':main()
