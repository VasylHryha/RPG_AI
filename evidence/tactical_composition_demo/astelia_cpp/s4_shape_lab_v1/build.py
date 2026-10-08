"""Build a separate development host, deriving only the host and collision call site.
No delivered files or objects are written. Source/binary identities are admitted on use.
"""
import hashlib
import json
import pathlib
import subprocess
import sys
import time
HERE = pathlib.Path(__file__).resolve().parent
CPP = HERE.parent
sys.path.insert(0, str(CPP))
from build_admission import admit, sha
BINARY = HERE / 'build/tactics_lab_host'

def derived_sources():
    host = (CPP / 'src/native/s4_v7_host.cpp').read_text()
    changes = {'astelia::configuration(request)': 'shape_lab::configuration(request)',
               'astelia::World::create(config)': 'shape_lab::create(config,request)'}
    for old, new in changes.items():
        if host.count(old) != 1:
            raise RuntimeError('delivered host call site drift: ' + old)
        host = host.replace(old, new)
    combat = (CPP / 'src/native/combat.cpp').read_text()
    old = 'separate(w.units,w.active,w.separationGrid,w.config->width,w.config->height,w.pushes);'
    if combat.count(old) != 1:
        raise RuntimeError('delivered collision call site drift')
    dispatch = (CPP / 'src/native/s4_v7_dispatch.cpp').read_text()
    signature = 'std::unique_ptr<Controller> makeController('
    if dispatch.count(signature) != 1:
        raise RuntimeError('delivered dispatcher drift')
    dispatch = dispatch.replace(signature, 'std::unique_ptr<Controller> makeDeliveredV7Controller(')
    return {'lab_v7_dispatch.cpp': dispatch, 'lab_host.cpp': '#include "lab_native.h"\n' + host,
            'lab_combat.cpp': '#include "lab_native.h"\n' + combat.replace(old, 'shape_lab::separate(w);')}

def build():
    start = time.monotonic()
    delivered = CPP / 's4_v7c/build/astelia_native_v7'
    identity = admit(delivered)
    expected = json.loads((CPP / 's4_v7c/BUILD.json').read_text())['identity']
    if identity != expected:
        raise RuntimeError('delivered v7c identity drift')
    m = json.loads(delivered.with_suffix('.build.json').read_text())
    out = HERE / 'build'
    out.mkdir(exist_ok=True)
    for name, content in derived_sources().items():
        (out / name).write_text(content)
    commands, objects = [], []
    # Recompile unchanged five overlay/controller objects locally, with exact delivered flags.
    for index, original in enumerate(m['commands'][:5]):
        argv = list(original)
        argv[-1] = str(out / f'overlay_{index}.o')
        subprocess.run(argv, check=True, timeout=180)
        commands.append(argv)
        objects.append(argv[-1])
    flags = m['commands'][-1][:m['commands'][-1].index('-c')]
    for name in ('lab_dispatch.cpp', 'build/lab_host.cpp', 'build/lab_combat.cpp'):
        obj = out / (pathlib.Path(name).stem + '.o')
        argv = flags + ['-I' + str(HERE), '-I' + str(CPP / 'src'),
                        '-I' + str(CPP / 'src/native'), '-I' + str(CPP / 's4_spacing_probe_v1'),
                        '-c', str(HERE / name), '-o', str(obj)]
        subprocess.run(argv, check=True, timeout=180)
        commands.append(argv)
        objects.append(str(obj))
    inherited = {}
    for path, digest in m['reused_object_sha256'].items():
        if sha(pathlib.Path(path)) != digest:
            raise RuntimeError('inherited object drift: ' + path)
        if pathlib.Path(path).name != 'observer_v1_combat.o':
            inherited[path] = digest
    link = [m['link'][0], *objects, *inherited, '-o', str(BINARY)]
    subprocess.run(link, check=True, timeout=90)
    hashes = dict(m['source_hashes'])
    for p in [HERE / 'lab_native.h', HERE / 'lab_dispatch.cpp', *(out / n for n in derived_sources())]:
        hashes[str(p.relative_to(CPP))] = sha(p)
    manifest = dict(schema=2, engine='shape_lab_v1', scope='native_complete_engine',
                    sanitized=False, portable=False, binary_sha256=sha(BINARY), source_hashes=hashes,
                    commands=commands, link=link, reused_object_sha256=inherited)
    BINARY.with_suffix('.build.json').write_text(json.dumps(manifest, indent=2) + '\n')
    receipt = dict(status='PASS', seconds=time.monotonic() - start, identity=admit(BINARY),
                   delivered_identity=identity, commands=commands, link=link,
                   changes=['host configuration/world creation boundary',
                            'post-collision static dummy position restoration'],
                   preserved_delivered_sha256=sha(delivered))
    (HERE / 'BUILD.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print('Build PASS', round(receipt['seconds'], 2), 'seconds')

if __name__ == '__main__':
    build()
