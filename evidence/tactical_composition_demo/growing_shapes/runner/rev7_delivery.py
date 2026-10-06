"""Package and verify new source/evidence only; never include native build products."""
import hashlib
import json
from pathlib import Path
import tarfile
from .rev7_identity import HERE,ROOT,assert_inputs

MAX_BYTES=50_000_000
ARCHIVE=HERE/'REV7_SOURCE_ONLY.tar.gz'
MANIFEST=HERE/'REV7_SOURCE_ONLY_MANIFEST.json'


def package():
    identity=assert_inputs()
    base=HERE.parent
    paths=list(base.glob('medium/rev7_*.*'))+[base/'medium/build_rev7.py']
    paths+=list(HERE.glob('rev7_*.py'))+[HERE/'test_rev7.py']
    paths+=[p for p in HERE.glob('REV7_*') if p.is_file() and p not in (ARCHIVE,MANIFEST,HERE/'REV7_DELIVERY_NOTE.md',HERE/'REV7_DELIVERY_VERIFICATION.json')]
    forbidden={'.dylib','.so','.dll','.o','.obj','.a','.lib','.pyc'}
    entries={}
    for p in sorted(set(paths)):
        if p.suffix in forbidden or '_rev7_build' in p.parts:raise ValueError('native product in source-only package')
        data=p.read_bytes()
        if len(data)>=MAX_BYTES:raise ValueError(f'oversize source: {p}')
        entries[str(p.relative_to(ROOT))]=dict(bytes=len(data),sha256=hashlib.sha256(data).hexdigest())
    manifest=dict(kind='SOURCE_ONLY',execution_pin_sha256=identity['pin_sha256'],files=entries,
        native_products='EXCLUDED',fixture_execution='NOT_RUN',provenance='Assisted-by: Codex:GPT-6')
    MANIFEST.write_text(json.dumps(manifest,sort_keys=True,indent=2)+'\n')
    with tarfile.open(ARCHIVE,'w:gz') as output:
        for name in entries:output.add(ROOT/name,arcname=name,recursive=False)
        output.add(MANIFEST,arcname=str(MANIFEST.relative_to(ROOT)),recursive=False)
    with tarfile.open(ARCHIVE,'r:gz') as archive:
        members=archive.getmembers()
        if {m.name for m in members}!=set(entries)|{str(MANIFEST.relative_to(ROOT))}:raise ValueError('archive membership mismatch')
        for m in members:
            if not m.isfile() or m.size>=MAX_BYTES or Path(m.name).is_absolute() or '..' in Path(m.name).parts or Path(m.name).suffix in forbidden:raise ValueError('invalid archive member')
            if m.name in entries:
                data=archive.extractfile(m).read()
                if len(data)!=entries[m.name]['bytes'] or hashlib.sha256(data).hexdigest()!=entries[m.name]['sha256']:raise ValueError('archive hash mismatch')
        packed_manifest=json.loads(archive.extractfile(str(MANIFEST.relative_to(ROOT))).read())
        if packed_manifest!=manifest:raise ValueError('archive manifest mismatch')
    if ARCHIVE.stat().st_size>=MAX_BYTES:raise ValueError('oversize archive')
    result=dict(status='PASS',archive=str(ARCHIVE.relative_to(ROOT)),archive_bytes=ARCHIVE.stat().st_size,
        archive_sha256=hashlib.sha256(ARCHIVE.read_bytes()).hexdigest(),source_files=len(entries),native_products=0,
        max_member_bytes=max(m.size for m in members),execution_pin_sha256=identity['pin_sha256'])
    return result


if __name__=='__main__':print(json.dumps(package(),sort_keys=True,indent=2))
