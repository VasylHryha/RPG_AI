"""Build Amendment-1 ECOF/ECOR atop exact RD3 in detached fd21826 worktrees."""
import argparse
import difflib
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
OUT = HERE.parent
ROOT = OUT.parents[4]
BASE = 'fd21826'
MEDIUM = 'evidence/tactical_composition_demo/growing_shapes/medium'
MODULE = 'evidence.tactical_composition_demo.growing_shapes.medium.build_rev7'
EXPECTED = 'b0b35a16ba134c57e56a44c9cb128b7a7ce2ae9cd4aaf836b8b1e82392c9578d'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def normal_patch(path, diff):
    """Apply the committed traditional diff with exact old-line checks and no fuzz."""
    import re
    source = path.read_text().splitlines(keepends=True)
    result = []; cursor = 0; rows = diff.read_text().splitlines(); i = 0
    while i < len(rows):
        m = re.fullmatch(r'(\d+)(?:,(\d+))?([acd])(\d+)(?:,(\d+))?', rows[i])
        if not m: raise ValueError(f'invalid traditional diff row: {rows[i]}')
        low, high = int(m[1]), int(m[2] or m[1]); op = m[3]; i += 1
        old = []; new = []
        while i < len(rows) and not re.match(r'^\d', rows[i]):
            line = rows[i]
            if line.startswith('< '): old.append(line[2:] + '\n')
            elif line.startswith('> '): new.append(line[2:] + '\n')
            elif line != '---': raise ValueError(line)
            i += 1
        begin = low if op == 'a' else low - 1
        end = begin if op == 'a' else high
        if begin < cursor or source[begin:end] != old: raise ValueError('patch context mismatch')
        result += source[cursor:begin] + new; cursor = end
    result += source[cursor:]; path.write_text(''.join(result))


def compare_reproduction(expected, result):
    fields=('variant','base_commit','screening_binary_reproduced','harness_sha256',
            'design_sha256','variant_patch_sha256','service_graph_sha256',
            'rd3_body_sha256','economy_kernel_sha256','rd3_parent_design_sha256','spec_sha256')
    for name in fields:
        if expected[name]!=result[name]: raise RuntimeError('reproduction identity mismatch: '+name)
    for section in ('build','world_build'):
        for name in ('source_sha256','binary_sha256'):
            if expected[section][name]!=result[section][name]:
                raise RuntimeError('reproduction identity mismatch: '+section+'/'+name)


def build(variant):
    receipt_path=HERE/f'{variant}_BUILD.json'
    expected=json.loads(receipt_path.read_text()) if receipt_path.exists() else None
    destination=HERE/'_worktrees'/variant
    if expected is not None and destination.exists():
        from execute_economy_plan import validate_build
        validate_build(variant)
        return expected
    from economy_kernel import apply_variant
    registration = OUT / '_local' / 'economy_builder_repo'
    if not registration.exists():
        registration.parent.mkdir(exist_ok=True)
        subprocess.run(['git','clone','--shared','--no-checkout',str(ROOT),str(registration)],check=True,capture_output=True)
    destination = HERE / '_worktrees' / variant
    if not destination.exists():
        subprocess.run(['git', 'worktree', 'add', '--detach', str(destination), BASE], cwd=registration, check=True)
    base_sha = subprocess.check_output(['git', 'rev-parse', BASE], cwd=ROOT, text=True).strip()
    actual = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=destination, text=True).strip()
    if actual != base_sha: raise RuntimeError('worktree revision mismatch')
    # Reusing an unmodified initial checkout is safe; never reset an existing edited tree.
    changed = subprocess.check_output(['git', 'diff', '--name-only'], cwd=destination, text=True)
    if changed: raise RuntimeError('worktree already patched; use its existing receipt, do not rebuild')
    native = destination / MEDIUM
    baseline = (native / 'rev7_design.py').read_text()
    normal_patch(native / 'rev7_medium.cpp', OUT / 'bond_v2_screening.patch')
    if variant == 'V1':
        normal_patch(native / 'rev7_design.py', OUT / 'bond_v2_screening_V1_path_protected_D3.pydiff')
        applied = subprocess.run(['diff', str(HERE / '_worktrees/SCR' / MEDIUM / 'rev7_design.py'), str(native / 'rev7_design.py')], text=True, capture_output=True)
        if applied.returncode != 1 or applied.stdout != (OUT / 'bond_v2_screening_V1_path_protected_D3.pydiff').read_text():
            raise RuntimeError('V1 diff reproduction mismatch')
    if variant in ('ECOF','ECOR'):
        old = "            e=min(eligible,key=lambda e:(measured[e.id] or 0.,e.id));self.remove(e.id,'D3',lock=measured[e.id])\n"
        new = (HERE / 'ranked_d3_body.txt').read_text()
        if baseline.count(old) != 1: raise RuntimeError('RD3 insertion mismatch')
        (native / 'rev7_design.py').write_text(baseline.replace(old, new))
        with (native / 'rev7_design.py').open('a') as f:
            f.write('\n# Scratch-only service geometry, independent of the observer.\nfrom service_graph import service_snapshot, ranked_choice\n')
        (destination / 'service_graph.py').write_bytes((OUT / 'service_graph.py').read_bytes())
        rd3 = (native / 'rev7_design.py').read_text()
        if hashlib.sha256(rd3.encode()).hexdigest() != json.loads((HERE/'RD3_BUILD.json').read_text())['design_sha256']:
            raise RuntimeError('RD3 parent design not reproduced')
        (native / 'rev7_design.py').write_text(apply_variant(rd3, variant))
        (destination / 'economy_kernel.py').write_bytes((OUT/'economy_kernel.py').read_bytes())
    historical = json.loads((HERE / 'HISTORICAL_SCREENING_IDENTITY.json').read_text())
    # Native sources in fd21826 already include all historical untracked-source inputs.
    # Verify that explicitly rather than copying mutable current workspace sources.
    for name, digest in historical['source_sha256'].items():
        if sha(native / name) != digest: raise RuntimeError(f'historical build input mismatch: {name}')
    env = dict(os.environ)
    if sys.platform == 'darwin':
        # Mach-O LC_ID_DYLIB affects bytes/UUID/signature. The historical path is only
        # an install-name string; no file at that path is read or written.
        wrapper = destination / 'scratch_clang'
        install_name = historical['command'][-1]
        wrapper.write_text('#!/usr/bin/env python3\nimport os,sys\nos.execv("/usr/bin/clang++", ["/usr/bin/clang++", "-Wl,-install_name,' + install_name + '"] + sys.argv[1:])\n')
        wrapper.chmod(0o755); env['CXX'] = str(wrapper)
    subprocess.run([sys.executable, '-m', MODULE], cwd=destination, env=env, check=True, capture_output=True)
    receipt = json.loads((native / '_rev7_build/build.json').read_text())
    if receipt['binary_sha256'] != EXPECTED: raise RuntimeError('STOP: screening binary not reproduced')
    subprocess.run([sys.executable, '-m', 'evidence.tactical_composition_demo.growing_shapes.world.build'], cwd=destination, check=True, capture_output=True)
    world = json.loads((destination / 'evidence/tactical_composition_demo/growing_shapes/world/_build/build.json').read_text())
    overlay = OUT / 'pilot_common_scratch.py'
    target = destination / 'evidence/tactical_composition_demo/growing_shapes_review_claude/rev711_diag/pilot_common.py'
    target.write_bytes(overlay.read_bytes())
    result = dict(variant=variant, base_commit=base_sha, screening_binary_reproduced=True,
                  build=receipt, world_build=world, harness_sha256=sha(overlay),
                  design_sha256=sha(native / 'rev7_design.py'),
                  variant_patch_sha256=sha(OUT / ('bond_v2_screening_V1_path_protected_D3.pydiff' if variant == 'V1' else 'bond_v2_screening.patch')),
                  service_graph_sha256=sha(OUT / 'service_graph.py') if variant in ('ECOF','ECOR') else None,
                  rd3_body_sha256=sha(HERE / 'ranked_d3_body.txt') if variant in ('ECOF','ECOR') else None,
                  python_diff=''.join(difflib.unified_diff(baseline.splitlines(True), (native / 'rev7_design.py').read_text().splitlines(True), fromfile='fd21826/rev7_design.py', tofile=variant+'/rev7_design.py')),
                  identity_policy='SCRATCH; Execution/assert_inputs stubs confined to copied pilot harness',
                  untracked_inputs='world and medium binaries/manifests built locally; all source inputs matched historical source hashes')
    result.update(economy_kernel_sha256=sha(OUT/'economy_kernel.py'), rd3_parent_design_sha256=hashlib.sha256(rd3.encode()).hexdigest(),spec_sha256=sha(OUT/'ECONOMY_PILOT_SPEC.md'), clock_boundary='ECOF growth-end all-site directed deficits; D5f before D3; ECOR D5r after D3 before births')
    if expected is not None:
        compare_reproduction(expected,result)
        reproduction=OUT/'_local'/f'{variant}_REPRODUCTION_{time.time_ns()}.json'
        reproduction.write_text(json.dumps(result,indent=2)+'\n')
    else:
        with receipt_path.open('x') as f: f.write(json.dumps(result,indent=2)+'\n')
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('variant', choices=['ECOF','ECOR'])
    args = parser.parse_args()
    sys.path.insert(0,str(OUT))
    print(json.dumps(build(args.variant), indent=2))
