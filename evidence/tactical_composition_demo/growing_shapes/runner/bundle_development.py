"""Hook-verified scoped commits using a temporary Git directory, never workspace .git writes."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
import time
from .section10 import HERE, OUT, ROOT, sha, write


def main():
    started = time.perf_counter()
    temporary = Path(tempfile.mkdtemp(prefix='0h-development-delivery-',dir='/private/tmp'))
    author = temporary/'author'
    subprocess.run(['git','init','-q',str(author)],check=True)
    gitdir = author/'.git'
    (gitdir/'objects/info/alternates').write_text(str(ROOT/'.git/objects')+'\n')
    env = dict(os.environ,GIT_DIR=str(gitdir),GIT_WORK_TREE=str(ROOT))
    logfile = HERE/'DEVELOPMENT_COMMIT_LOG.txt'
    log = logfile.open('w')
    def git(*args, capture=True):
        result = subprocess.run(['git',*args],cwd=ROOT,env=env,text=True,capture_output=True)
        log.write('$ git '+' '.join(args)+'\n'+result.stdout+result.stderr); log.flush()
        if result.returncode:
            raise RuntimeError(result.stderr or result.stdout)
        return result.stdout.strip()
    base = subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    branch = 'codex/0h-development'
    git('config','core.hooksPath',str(ROOT/'.githooks'))
    git('config','core.compression','1')
    for key in ('user.name','user.email'):
        value = subprocess.check_output(['git','config',key],cwd=ROOT,text=True).strip()
        git('config',key,value)
    git('update-ref',f'refs/heads/{branch}',base)
    git('symbolic-ref','HEAD',f'refs/heads/{branch}')
    git('read-tree',base)
    extras = ['section10.py','deliver_development.py','bundle_development.py','DEVELOPMENT_REPORT.md',
              'DEVELOPMENT_PREFLIGHT.json','DEVELOPMENT_POSTFLIGHT.json','DEVELOPMENT_COST_LOG.txt',
              'DEVELOPMENT_RUN_LOG.txt','DEVELOPMENT_ARCHIVE_LOG.txt']
    files = [HERE/name for name in extras] + sorted(p for p in OUT.rglob('*') if p.is_file())
    paths = [str(p.relative_to(ROOT)) for p in files]
    assert all(p.startswith('evidence/tactical_composition_demo/growing_shapes/') for p in paths)
    git('add','--',*paths)
    staged = git('diff','--cached','--name-only').splitlines()
    assert set(staged)==set(paths)
    git('commit','-m','Run 0h revision 5.1 authorized development with eight seed-pair workers\n\nRetain all raw audit bytes in verified lossless archives, exposure/accounting ledgers, ordered arm read-outs and qualified-atom replays. G0 prime fails in both arms; stop development as designed.\n\nAssisted-by: Codex:GPT-6')
    evidence_commit = git('rev-parse','HEAD')
    print(json.dumps({'stage':'evidence committed','commit':evidence_commit,'files':len(files)}),flush=True)
    note = HERE/'DEVELOPMENT_DELIVERY.md'
    note.write_text(f'''DELIVERED — exploratory development; summary FAIL, no scientific acceptance

The owner-authorized DESIGN_0H revision-5.1 section-10 run completed without invalid seed pairs. Cost measurement: 415.407 s for 200 episodes; projected 11.403 serial hours. Full run: 2.059 wall hours, at most eight seed-pair workers. Both arms: G0 INCONCLUSIVE; G0' FAIL; G1 PASS; G1c DESCRIPTIVE; G5 PASS. Every seed had a late birth rejection, so development stops under the declared G0' row. No constants, rules, schedule, reviewed source or native build changed during execution. No judging namespace was used.

Evidence commit: `{evidence_commit}`. Bundle prerequisite/base: `{base}`. Branch: `{branch}`.

The managed permission profile makes the workspace `.git` read-only. The scoped commit was made using a separate temporary Git directory with the workspace as a read-only source for already existing files and the repository's normal `.githooks` enabled. The freeze, legacy, milestone, status and provenance guards passed without bypass. Only this task's new growing_shapes paths were staged. Workspace HEAD/index/refs and all unrelated work were preserved. Both evidence and delivery-note commits carry `Assisted-by: Codex:GPT-6`.

`development_commits.bundle` beside this note carries the evidence and this note. `DEVELOPMENT_BUNDLE_VERIFIED.json` and `DEVELOPMENT_COMMIT_LOG.txt` are external verification/delivery records, excluded from the commits together with the bundle to avoid circular identities. The verification record identifies both commits, bundle SHA256/size, independent fetch, exact changed-path scope and byte-for-byte hashes of all delivered blobs. No workspace merge, push or milestone/status promotion was performed.

Read [DEVELOPMENT_REPORT.md](DEVELOPMENT_REPORT.md) for ordered verdicts, per-seed descriptive G1c, exposure/accounting and stage timings. The 66 training event/drive ledgers are retained as lossless gzip archives; [AUDIT_TRANSPORT.json](development_20261006/AUDIT_TRANSPORT.json) maps unchanged original Run receipts to their archives and records verified decoded hashes, bytes and record counts. Every admitted snapshot, template, evaluation-copy identity and replay input is retained. Recovery replay inputs are the complete immutable check-time state, cohort/candidate order, kick entropy from seed/check index, and the next 600 recorded drive steps; recovery results/criteria/timescales are retained in events. The two exported qualified-atom trajectories are REPLAY_task_blind.json.gz and REPLAY_reward.json.gz, with one additional diagnostic validation episode per arm, excluded from read-outs.

To import in an owner-writable checkout containing the base, preserve unrelated changes and use:

```sh
git bundle verify /absolute/path/to/development_commits.bundle
git fetch /absolute/path/to/development_commits.bundle refs/heads/{branch}
git log --reverse --format='%H %s' {base}..FETCH_HEAD
git cherry-pick {evidence_commit}
# Then cherry-pick the delivery-note commit printed above.
```

Native build products are local ignored artifacts and are not bundled. The saved run identity binds their binaries/dependencies/platform. Importing the evidence requires no experimental rerun. An outcome-informed protocol change requires a new design revision and fresh development seeds; the owner decides any next development step. Driven snapshots and numerical copy covariance do not establish autonomous closure, usefulness, background recursion or efficiency.
''')
    git('add','--',str(note.relative_to(ROOT)))
    git('commit','-m','Document verified 0h development bundle delivery and stop condition\n\nAssisted-by: Codex:GPT-6')
    head = git('rev-parse','HEAD')
    bundle = HERE/'development_commits.bundle'
    assert not bundle.exists()
    git('-c','pack.window=0','-c','pack.compression=1','-c','pack.threads=4','bundle','create',str(bundle),f'{base}..refs/heads/{branch}')
    print(json.dumps({'stage':'bundle created','bytes':bundle.stat().st_size}),flush=True)
    verifier = temporary/'verifier'
    subprocess.run(['git','init','--bare','-q',str(verifier)],check=True)
    (verifier/'objects/info/alternates').write_text(str(ROOT/'.git/objects')+'\n')
    def verify_git(*args):
        result = subprocess.run(['git','--git-dir',str(verifier),*args],text=True,capture_output=True)
        log.write('$ verification git '+' '.join(args)+'\n'+result.stdout+result.stderr); log.flush()
        if result.returncode:
            raise RuntimeError(result.stderr or result.stdout)
        return result.stdout.strip()
    verify_git('bundle','verify',str(bundle))
    verify_git('fetch',str(bundle),f'refs/heads/{branch}:refs/heads/{branch}')
    assert verify_git('rev-parse',f'refs/heads/{branch}')==head
    all_files = files+[note]
    expected_paths = {str(p.relative_to(ROOT)) for p in all_files}
    changed = verify_git('diff','--name-only',base,head).splitlines()
    assert set(changed)==expected_paths
    file_checks = {}
    for path in all_files:
        relative = str(path.relative_to(ROOT))
        process = subprocess.Popen(['git','--git-dir',str(verifier),'cat-file','blob',f'{head}:{relative}'],stdout=subprocess.PIPE)
        digest = hashlib.sha256(); size = 0
        for block in iter(lambda:process.stdout.read(1024*1024),b''):
            digest.update(block); size += len(block)
        process.stdout.close()
        assert process.wait()==0
        assert digest.hexdigest()==sha(path) and size==path.stat().st_size,relative
        file_checks[relative] = {'sha256':digest.hexdigest(),'bytes':size}
    assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()==base
    write(HERE/'DEVELOPMENT_BUNDLE_VERIFIED.json',{'status':'PASS','base':base,'evidence_commit':evidence_commit,
          'delivery_commit':head,'branch':branch,'bundle_sha256':sha(bundle),'bundle_bytes':bundle.stat().st_size,
          'bundle_verify':'PASS','independent_fetch':'PASS','workspace_head_unchanged':True,
          'normal_repository_hooks':'PASS for both commits; see DEVELOPMENT_COMMIT_LOG.txt',
          'provenance_trailer':'Assisted-by: Codex:GPT-6','file_checks':file_checks,
          'changed_paths':changed,'scope':'only evidence/tactical_composition_demo/growing_shapes/',
          'temporary_git_directory':str(temporary),'seconds':time.perf_counter()-started})
    log.close()
    print(json.dumps({'status':'PASS','evidence_commit':evidence_commit,'delivery_commit':head,
                      'files':len(file_checks),'bundle_bytes':bundle.stat().st_size,'seconds':time.perf_counter()-started}),flush=True)


if __name__=='__main__':
    main()
