"""One-time, no-fight migration. All inherited receipt bytes stay unchanged."""
import fcntl
import hashlib
import json
import pathlib
import shutil
import subprocess

HERE = pathlib.Path(__file__).resolve().parent
V5 = HERE.parent / 's4_shape_lab_v5'
REPO = HERE.parents[3]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    if (HERE / 'CONTINUATION.json').exists():
        raise RuntimeError('migration already sealed; do not replace receipts')
    with (V5 / 'raw/EXECUTION.lock').open('r') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        migrate()


def migrate():
    if list((V5 / 'raw').glob('C3_*')) or list((V5 / 'raw').glob('S10X_*')):
        raise RuntimeError('v5 outcome/series already opened; investigate before migration')
    declaration = json.loads((V5 / 'DECLARATION.json').read_text())
    frozen = HERE / 'frozen'
    frozen.mkdir(exist_ok=True)
    docs = {}
    for relative in ('evidence/tactical_composition_demo/SHAPE_LAB_SPEC.md',
                     'docs/decisions/0033-0g-big-levers-and-lighter-tooling-reviews.md'):
        original = REPO / relative
        payload = subprocess.check_output(['git', 'show', 'bc8ed24:' + relative], cwd=REPO)
        if hashlib.sha256(payload).hexdigest() != declaration['source_hashes'][str(original)]:
            raise RuntimeError('pinned document identity mismatch: ' + relative)
        target = frozen / original.name
        with target.open('xb') as output:
            output.write(payload)
        docs[str(original)] = str(target.relative_to(HERE))
    names = ['DECLARATION.json', 'PREPARE.json', 'BUILD.json', 'MECHANISM_SUMMARY.json',
             'MECHANISM_READ.json', 'PICK.json', 'CALIBRATION_mechanism.json',
             'CALIBRATION_mechanism_PROJECTION.json', 'RUN_GATE_mechanism.json',
             'RUN_mechanism.json', 'raw/SEED_LEDGER.json']
    names += [p.name for p in V5.glob('*_mechanism_ATTEMPT_*.json')]
    completions = list((V5 / 'raw').glob('*_COMPLETE.json'))
    tags = [p.name.removesuffix('_COMPLETE.json') for p in completions]
    if len(tags) != 220:
        raise RuntimeError('expected exactly 220 completed mechanism fights')
    streams = {}
    for path, tag in zip(completions, tags):
        row = json.loads(path.read_text())
        if row['tag'] != tag or row['meta']['stage'] != 'mechanism':
            raise RuntimeError('unexpected mechanism completion')
        names += ['raw/' + tag + suffix for suffix in ('_COMPLETE.json', '_request.json', '_CLAIM.json', '_stderr.log')]
        streams[tag] = row['raw_sha256']
        if sha(V5 / 'raw' / (tag + '.jsonl.gz')) != row['raw_sha256']:
            raise RuntimeError('inherited raw drift: ' + tag)
    inherited = {}
    for name in names:
        source = V5 / name
        target = HERE / name
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open('xb') as output:
            output.write(source.read_bytes())
        inherited[name] = sha(target)
        if inherited[name] != sha(source):
            raise RuntimeError('copy mismatch: ' + name)
    # Retain the abandoned RUNNING attempt as historical audit only. It is not
    # a v5b attempt and supplies no calibrated outcome timing.
    audit = HERE / 'inherited_audit'
    audit.mkdir(exist_ok=True)
    for source in V5.glob('*_outcome_ATTEMPT_*.json'):
        target = audit / source.name
        with target.open('xb') as output:
            output.write(source.read_bytes())
        inherited[str(target.relative_to(HERE))] = sha(target)
    for name in ('OBSERVATIONS.json', 'SHAPE_LAB_REPORT.md'):
        target = audit / name
        with target.open('xb') as output:
            output.write((V5 / name).read_bytes())
        inherited[str(target.relative_to(HERE))] = sha(target)
    tools = [*sorted(HERE.glob('*.py')), HERE / 'README.md', HERE / '.gitignore',
             *sorted(frozen.iterdir())]
    manifest = dict(schema='v5b-tooling-continuation-1', status='DEVELOPMENT_ONLY',
                    declaration_sha256=sha(HERE / 'DECLARATION.json'),
                    source_lab='s4_shape_lab_v5', mechanism_tags=tags,
                    inherited_files=inherited, inherited_raw_sha256=streams,
                    frozen_documents=docs,
                    tool_hashes={str(p.relative_to(HERE)):sha(p) for p in tools},
                    migration='Same v5 binary/declaration/entropy/receipts/pick/read; no fights or new choice. Raw stays read-only in v5.',
                    abandoned_outcome_attempt='Historical RUNNING record retained unchanged under inherited_audit; no C3 files existed. No timing reused.')
    (HERE / 'CONTINUATION.json').write_text(json.dumps(manifest, indent=2)+'\n')
    print('Migrated 220 mechanism receipts; zero fights; unchanged v5 declaration/pick/read')


if __name__ == '__main__':
    main()
