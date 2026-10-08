"""Compile an observer/JSON overlay; rebuild unbound objects from admitted sources."""
import json
import pathlib
import subprocess
import sys
import time
HERE = pathlib.Path(__file__).resolve().parent
CPP = HERE.parent
ADAPTER = CPP/'s4_react_adapter_v1'
BINARY = HERE/'build/tactics_react_host_v4'
sys.path.insert(0, str(CPP))
from build_admission import admit, sha


def replace_once(text, old, new):
    if text.count(old) != 1:
        raise RuntimeError('observer call site drift: '+old)
    return text.replace(old, new)


def derived_sources():
    host = (ADAPTER/'build/react_host.cpp').read_text()
    # Remove output-only controller audits rather than generate and discard them.
    begin = host.index('    // Output only. Gun rows describe')
    end = host.index('    observer.damage.clear()', begin)
    host = host[:begin]+host[end:]
    host = replace_once(host, 'if(killerTelemetry)react_v1::telemetry(w);', '')
    begin = host.index('    for(const auto& d:observer.damage)')
    end = host.index('    for(const auto& d:observer.dodges)', begin)
    host = host[:begin]+'''    for(const auto& d:observer.damage)damage.push_back(js::obj({
      {"source",double(d.source)},{"sourceRole",astelia::roleName(d.sourceRole)},
      {"sourceTeam",double(d.sourceTeam)},{"target",double(d.target)},
      {"targetRole",astelia::roleName(d.targetRole)},{"targetTeam",double(d.targetTeam)},
      {"dealt",d.dealt},{"t",d.time},{"died",d.died}}));
'''+host[end:]
    begin = host.index('    for(const auto& e:observer.entries)')
    end = host.index('    for(auto i:w.active)', begin)
    host = host[:begin]+host[end:]
    # No attribution geometry collectors: same damage/dodge/launch event seam.
    observer = (CPP/'src/native/observer_v1.cpp').read_text()
    begin = observer.index('void movement(')
    end = observer.index('void hit(', begin)
    observer = observer[:begin]+'void movement(const World&,uint32_t,Vec2){}\n'+observer[end:]
    begin = observer.index(' if(!dst.alive&&dst.team==1')
    end = observer.index('sink->damage.push_back', begin)
    observer = observer[:begin]+' '+observer[end:]
    return {'lean_host.cpp': host, 'lean_observer.cpp': observer}


def build():
    start = time.monotonic()
    parent = ADAPTER/'build/tactics_react_host'
    parent_id = admit(parent)
    record = json.loads(parent.with_suffix('.build.json').read_text())
    if json.loads((ADAPTER/'BUILD.json').read_text())['identity'] != parent_id:
        raise RuntimeError('adapter build receipt mismatch')
    out = HERE/'build'
    out.mkdir(exist_ok=True)
    generated = derived_sources()
    flags = record['commands'][0][:record['commands'][0].index('-c')]
    flags += ['-I'+str(ADAPTER), '-I'+str(CPP/'s4_shape_lab_v1')]
    commands, objects = [], []
    for name, content in generated.items():
        source = out/name
        source.write_text(content)
        obj = source.with_suffix('.o')
        argv = [*flags, '-c', str(source), '-o', str(obj)]
        subprocess.run(['nice','-n','15',*argv],check=True,timeout=180)
        commands.append(argv)
        objects.append(str(obj))
    reused = {}
    linked = record['link'][1:record['link'].index('-o')]
    local_commands = {argv[-1]:argv for argv in record['commands']}
    for path in linked:
        if pathlib.Path(path).name in ('react_host.o','observer_v1_observer_v1.o'):
            continue
        expected = record.get('reused_object_sha256', {}).get(path)
        if expected:
            if sha(pathlib.Path(path)) != expected:
                raise RuntimeError('adapter object drift: '+path)
            reused[path] = expected
        elif path in local_commands:
            # The adapter manifest does not hash its locally compiled objects.
            # Rebuild from its admitted sources rather than trust an unbound cache.
            argv = list(local_commands[path])
            obj = out/('admitted_'+pathlib.Path(path).name)
            argv[-1] = str(obj)
            subprocess.run(['nice','-n','15',*argv],check=True,timeout=180)
            commands.append(argv)
            reused[str(obj)] = sha(obj)
        else:
            raise RuntimeError('unbound adapter object: '+path)
    argv = [record['link'][0], *objects, *reused, '-o', str(BINARY)]
    subprocess.run(['nice','-n','15',*argv],check=True,timeout=120)
    if admit(parent) != parent_id:
        raise RuntimeError('adapter changed during build')
    sources = dict(record['source_hashes'])
    for path in [HERE/'build.py', *(out/n for n in generated)]:
        sources[str(path.relative_to(CPP))] = sha(path)
    manifest = dict(schema=2, engine='react_lab_v4_observer_only', scope='native_complete_engine',
                    sanitized=False, portable=False, source_hashes=sources,
                    binary_sha256=sha(BINARY), commands=commands, link=argv,
                    reused_object_sha256=reused, parent=parent_id)
    BINARY.with_suffix('.build.json').write_text(json.dumps(manifest,indent=2)+'\n')
    receipt = dict(status='PASS', seconds=time.monotonic()-start, identity=admit(BINARY),
                   parent=parent_id, reused_object_sha256=reused,
                   scope='JSON host and observer collectors only; combat/controller objects unchanged',
                   fights=0, execution='sequential; nice requested')
    (HERE/'BUILD.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print('Build prepared; no fights', receipt['seconds'])


if __name__ == '__main__':
    build()
