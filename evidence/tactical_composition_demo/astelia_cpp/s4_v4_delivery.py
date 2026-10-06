"""Scope-limited, hook-checked bundle delivery with an independent object import."""
import argparse
import hashlib
import json
import pathlib
import shutil
import subprocess
from s4_development import ROOT,write,sha

REPO=ROOT.parents[2]
PREFIX=str(ROOT.relative_to(REPO))+'/'
CLONE=ROOT/'build/s4_v4_delivery_repo'
VERIFY=ROOT/'build/s4_v4_bundle_verify'
CHECKS=ROOT/'s4_v4_checks'


def git(directory,*arguments):
    return subprocess.check_output(['git',*arguments],cwd=directory,text=True).strip()


def deliver(part):
    if part==1:
        if not CLONE.exists():
            subprocess.run(['git','clone','--shared','--no-checkout',str(REPO),str(CLONE)],check=True,capture_output=True)
            git(CLONE,'checkout','--detach','914dda4')
            git(CLONE,'config','core.hooksPath','.githooks')
            base=git(CLONE,'rev-parse','HEAD')
        else:
            base=json.loads((CHECKS/'PART1_INITIAL_DELIVERY.json').read_text())['base']
        changed=git(REPO,'diff','--name-only','--',PREFIX).splitlines()
        untracked=git(REPO,'ls-files','--others','--exclude-standard','--',PREFIX).splitlines()
        names=sorted(set(changed+untracked))
        # Do not include the stop report or its historical delivery in Part 1.
        names=[n for n in names if n!=PREFIX+'S4_V4_DEVELOPMENT_REPORT.md' and n!=PREFIX+'s4_v4_checks/DELIVERY_NOTE.md']
    else:
        if not CLONE.exists():raise RuntimeError('Part 1 delivery required')
        base=json.loads((CHECKS/'PART1_DELIVERY.json').read_text())['base']
        names=[PREFIX+'S4_V4_DEVELOPMENT_REPORT.md',PREFIX+'s4_v4_checks/DELIVERY_NOTE.md']
        allowed=('summary.json','failure.json','run_identity.json','AUDIT.json','POWER_PLANNING.json','VALIDATION_END_STATES.json','END_STATES_BY_SPLIT.json','VALIDATION_SUMMARY.json','DECISION_TRACE_SUMMARY.json','LOCAL_ARTIFACTS.json','A_best.json','B_best.json','C_best.json')
        names += [PREFIX+'s4_v4_development/'+name for name in allowed if (ROOT/'s4_v4_development'/name).exists()]
    if not names or any(not n.startswith(PREFIX) for n in names):raise RuntimeError('delivery scope mismatch')
    for name in names:
        src=REPO/name
        if not src.is_file() or src.stat().st_size>=50_000_000:raise RuntimeError('file missing or >=50 MB: '+name)
        if any(token in name for token in ('fights.jsonl','s4_seeds.json','_tuning.json','_partial.json','_validation.json','.jsonl.gz','.replay.json.gz','.stdout.txt','.bundle')):raise RuntimeError('raw evidence prohibited: '+name)
        dest=CLONE/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dest)
    git(CLONE,'add','--',*names)
    staged=git(CLONE,'diff','--cached','--name-only').splitlines()
    if not staged or any(name not in names for name in staged):raise RuntimeError('staging scope mismatch')
    message=f'Implement 0g v4 skeleton and bounded S4 execution' if part==1 else 'Report fresh S4 v4 development and output-only decision diagnostics'
    result=subprocess.run(['git','commit','-m',message+'\n\nAssisted-by: Codex:GPT-6'],cwd=CLONE,text=True,capture_output=True)
    if result.returncode:raise RuntimeError(result.stdout+result.stderr)
    commit=git(CLONE,'rev-parse','HEAD')
    bundle=CHECKS/('part1.bundle' if part==1 else 'commits.bundle')
    git(CLONE,'bundle','create',str(bundle),base+'..HEAD')
    git(CLONE,'bundle','verify',str(bundle))
    if not VERIFY.exists():subprocess.run(['git','clone','--shared','--no-checkout',str(REPO),str(VERIFY)],check=True,capture_output=True)
    git(VERIFY,'fetch',str(bundle),'HEAD')
    imported=git(VERIFY,'rev-parse','FETCH_HEAD')
    if imported!=commit:raise RuntimeError('bundle imported wrong commit')
    tasks=git(CLONE,'diff','--name-only',base,commit).splitlines()
    hashes={}
    for name in tasks:
        if not name.startswith(PREFIX):raise RuntimeError('bundle has unowned path')
        raw=subprocess.check_output(['git','show',commit+':'+name],cwd=VERIFY)
        if len(raw)>=50_000_000 or hashlib.sha256(raw).hexdigest()!=sha(REPO/name):raise RuntimeError('bundle blob mismatch: '+name)
        hashes[name[len(PREFIX):]]=sha(REPO/name)
    receipt=dict(part=part,base=base,commit=commit,bundle_sha256=sha(bundle),bundle=str(bundle),independent_import_verified=True,
                 repository_hooks_enabled=git(CLONE,'config','core.hooksPath'),hook_commit_stdout=result.stdout,
                 provenance='Assisted-by: Codex:GPT-6',task_hashes=hashes,committed_files=len(tasks),all_files_under_50_MB=True,scope=PREFIX)
    if part==1:
        receipt['implementation_commit']=commit;write(CHECKS/'PART1_DELIVERY.json',receipt)
    else:write(CHECKS/'BUNDLE_VERIFIED.json',receipt)
    print(json.dumps(dict(commit=commit,bundle=str(bundle),files=len(tasks),verified=True)))


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('part',type=int,choices=(1,2));deliver(ap.parse_args().part)
