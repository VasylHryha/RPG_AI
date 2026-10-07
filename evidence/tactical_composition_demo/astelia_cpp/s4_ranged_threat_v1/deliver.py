"""Explicit-scope normal-hook commit, or verified bundle from current HEAD.

No source experiments, receipts, raw, main index or config are changed when the
main .git is unwritable. Transport logs/sidecar stay in the ignored build root.
"""
import hashlib
import json
import os
import pathlib
import subprocess

HERE = pathlib.Path(__file__).resolve().parent
CPP = HERE.parent
REPO = CPP.parents[2]


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def write(p, obj):
    p.write_text(json.dumps(obj, indent=2, allow_nan=False)+'\n')


def main():
    base = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=REPO, text=True).strip()
    assert (HERE/'OWNER_RECHECK.md').read_text().startswith('APPROVE')
    data = json.loads((HERE/'COMPACT.json').read_text())
    assert data['status'] == 'DONE' and data['script_sha256'] == sha(HERE/'analyze.py')
    for name, expected in data['input_hashes'].items():
        assert sha(CPP/'s4_spacing_probe_v1'/name) == expected
    derived = json.loads((HERE/'DERIVED.json').read_text())
    assert derived['compact_sha256'] == sha(HERE/'COMPACT.json')
    assert derived['script_sha256'] == sha(HERE/'summarize.py')
    assert json.loads((HERE/'SPACING_RECOMPUTATION.json').read_text())['status'] == 'PASS'
    for name in ['docs/PLAN_CURRENT.md', 'evidence/tactical_composition_demo/DESIGN_0G.md']:
        assert (REPO/name).read_bytes() == subprocess.check_output(['git','show',base+':'+name], cwd=REPO)
    for p in (CPP/'s4_spacing_probe_v1').iterdir():
        if p.is_file():
            name = str(p.relative_to(REPO))
            if subprocess.run(['git','ls-files','--error-unmatch','--',name],cwd=REPO,capture_output=True).returncode == 0:
                assert p.read_bytes() == subprocess.check_output(['git','show',base+':'+name],cwd=REPO), name
    marker = REPO/'.git/ranged_threat_v1_write_probe'
    writable, error = False, None
    try:
        with marker.open('x') as f:
            f.write('explicitly authorized task write probe')
        marker.unlink()
        writable = True
    except OSError as e:
        error = str(e)
    write(HERE/'GIT_WRITABILITY.json', dict(writable=writable, error=error))
    names = sorted([str(p.relative_to(REPO)) for p in HERE.iterdir() if p.is_file() and p.name != 'VALIDATION.json'] +
                   [str((CPP/n).relative_to(REPO)) for n in ['S4_SPACING_PROBE.md','S4_RANGED_THREAT_DIAGNOSTIC.md']] +
                   ['docs/reviews/tactical_0g_spacing_probe_recheck_codex.md'])
    assert all((REPO/n).stat().st_size <= 45_000_000 for n in names)
    write(HERE/'VALIDATION.json', dict(status='PASS', base=base, stored_data_only=True,
          source_raw_hashes_verified=370, original_table_cells_recomputed=6, diagnostic_fights=60,
          source_receipts_and_protected_documents_unchanged=True, combat_tests_run=0,
          independent_diagnostic_review='OWNER_RECHECK.md',
          prior_analysis_attempts=['Stopped for redundant per-unit geometry work before optimization; no output or combat',
                                   'Python 3.9 zero-key Counter comparison assertion; fixed normalization; no source measurement error'],
          checks={'request_template_identity':'PASS','terminal_casualties':'PASS','shell_attribution':'PASS',
                  'exact_pooled_quantiles':'PASS','native_clipping_reconciliation':'PASS','regular_gun_hp_conservation':'PASS'},
          checked_hashes={n:sha(REPO/n) for n in names}, max_committed_file_bytes=max((REPO/n).stat().st_size for n in names)))
    names.append(str((HERE/'VALIDATION.json').relative_to(REPO)))
    expected = {n:(REPO/n).read_bytes() for n in names}
    build = CPP/'build/ranged_threat_v1_delivery'
    build.mkdir()
    env = dict(os.environ)
    branch = 'refs/heads/s4-ranged-threat-v1'
    if not writable:
        gitdir = build/'delivery.git'
        subprocess.run(['git','clone','--bare','--shared',str(REPO),str(gitdir)],check=True,capture_output=True)
        env.update(GIT_DIR=str(gitdir), GIT_WORK_TREE=str(REPO), GIT_INDEX_FILE=str(gitdir/'task.index'))
    def git(*args):
        return subprocess.check_output(['git',*args],cwd=REPO,env=env,text=True).strip()
    if not writable:
        git('symbolic-ref','HEAD',branch); git('update-ref',branch,base); git('read-tree',base)
        git('config','core.hooksPath',str(REPO/'.githooks'))
    else:
        assert git('config','core.hooksPath') == '.githooks'
    staged_before = {n:subprocess.check_output(['git','diff','--cached','--binary','--',n],cwd=REPO,env=env)
                     for n in git('diff','--cached','--name-only').splitlines() if n not in names}
    git('add','--',*names)
    git('diff','--cached','--check','--',*names)
    message = 'Review stored S4 spacing probe and diagnose ranged threats\n\nAssisted-by: Codex:GPT-6'
    r = subprocess.run(['git','commit','--only','-m',message,'--',*names],cwd=REPO,env=env,text=True,capture_output=True)
    (build/'COMMIT.log').write_text(r.stdout+r.stderr)
    assert r.returncode == 0, r.stdout+r.stderr
    head = git('rev-parse','HEAD')
    assert set(git('diff-tree','--no-commit-id','--name-only','-r',head).splitlines()) == set(names)
    for n, v in staged_before.items():
        assert subprocess.check_output(['git','diff','--cached','--binary','--',n],cwd=REPO,env=env) == v
    if writable:
        print(json.dumps(dict(commit=head, main_git_modified=True, normal_hooks='PASS')))
        return
    bundle = build/'S4_RANGED_THREAT_DIAGNOSTIC.bundle'
    git('bundle','create',str(bundle),base+'..'+branch)
    r = subprocess.run(['git','bundle','verify',str(bundle)],cwd=REPO,env=env,text=True,capture_output=True)
    (build/'BUNDLE_VERIFY.log').write_text(r.stdout+r.stderr)
    assert r.returncode == 0
    fresh = build/'fresh_fetch'
    subprocess.run(['git','clone','--shared','--no-checkout',str(REPO),str(fresh)],check=True,capture_output=True)
    subprocess.run(['git','fetch',str(bundle),branch],cwd=fresh,check=True,capture_output=True)
    assert subprocess.check_output(['git','rev-parse','FETCH_HEAD'],cwd=fresh,text=True).strip() == head
    for n, v in expected.items():
        assert subprocess.check_output(['git','show',head+':'+n],cwd=fresh) == v
    assert git('show','-s','--format=%B',head).endswith('Assisted-by: Codex:GPT-6')
    assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=REPO,text=True).strip() == base
    write(build/'DELIVERY_TRANSPORT.json',dict(base=base,commit=head,main_git_modified=False,
          bundle_sha256=sha(bundle),bundle_bytes=bundle.stat().st_size,normal_hooks_returncode=0,
          independent_fetch_and_all_blob_bytes_verified=True,explicit_paths=names,
          committed_file_hashes={n:sha(REPO/n) for n in names}))
    print(json.dumps(dict(base=base,commit=head,main_git_modified=False,bundle=str(bundle),verified=True)))


if __name__ == '__main__':
    main()
