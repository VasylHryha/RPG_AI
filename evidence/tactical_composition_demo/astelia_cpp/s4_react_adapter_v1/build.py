"""New isolated host. Sequential nice compilation; no simulation execution."""
import json
import os
import pathlib
import subprocess
import sys
import time

HERE = pathlib.Path(__file__).resolve().parent
CPP = HERE.parent
sys.path.insert(0, str(CPP))
from build_admission import admit, sha
BINARY = HERE / 'build/tactics_react_host'

def replace_once(source, old, new):
    if source.count(old) != 1:
        raise RuntimeError('delivered call site drift: ' + old)
    return source.replace(old, new)

def derived_sources():
    host = (CPP/'s4_shape_lab_v1/build/lab_host.cpp').read_text()
    host = replace_once(host, 'shape_lab::configuration(request)', 'react_v1::configuration(request)')
    host = replace_once(host, 'shape_lab::create(config,request)', 'react_v1::create(config,request)')
    host = replace_once(host, 'dumpObserver(tick);', 'dumpObserver(tick);if(killerTelemetry)react_v1::telemetry(w);')
    combat = (CPP/'s4_shape_lab_v1/build/lab_combat.cpp').read_text()
    combat = replace_once(combat, 'prepareControllers(w);', 'react_v1::prepare(w);prepareControllers(w);react_v1::shadows(w);')
    combat = replace_once(combat, 'controllerDecision(w,i)', 'react_v1::decide(w,i)')
    combat = replace_once(combat, 'for(auto i:w.active)gamePrep(w,i,dt*w.state[i].timeRate);', 'react_v1::constrainPrep(w);for(auto i:w.active)gamePrep(w,i,dt*w.state[i].timeRate);')
    combat = replace_once(combat, 'd.release==Release::Artillery&&prepared(w,i)', 'd.release==Release::Artillery&&prepared(w,i)&&react_v1::aimReach(w,i)')
    # Explicit artillery aim at the final point, preserving fallback and mechanics.
    combat = replace_once(combat, 'fireShellAt(w,i,t->pos+(sk.lobLead||(sk.adaptiveLobLead&&steady)?ts.longVelocity*fl:Vec2{}));', 'fireShellAt(w,i,react_v1::aimPoint(w,i,t->pos+(sk.lobLead||(sk.adaptiveLobLead&&steady)?ts.longVelocity*fl:Vec2{})));')
    rules = (CPP/'src/native/observer_v1_combat_rules.cpp').read_text()
    rules = replace_once(rules, 'const Vec2 delta=point-u.pos;', 'if(p.aimed)point=react_v1::aimPoint(w,i,point);\n  const Vec2 delta=point-u.pos;')
    return {name:'#include "react.h"\n'+content for name, content in
            [('react_host.cpp', host), ('react_combat.cpp', combat), ('react_rules.cpp', rules)]}

def build():
    started = time.monotonic()
    parent = CPP/'s4_shape_lab_v1/build/tactics_lab_host'
    parent_identity = admit(parent)
    manifest = json.loads(parent.with_suffix('.build.json').read_text())
    out = HERE/'build'
    out.mkdir(exist_ok=True)
    generated = derived_sources()
    for name, content in generated.items():
        (out/name).write_text(content)
    flags = manifest['commands'][0][:manifest['commands'][0].index('-c')]
    flags += ['-I'+str(HERE), '-I'+str(CPP/'s4_shape_lab_v1')]
    commands, objects = [], []
    # Parent overlay objects lack their own historical object hashes. Rebuild
    # their admitted source bytes locally rather than trusting those caches.
    for index, original in enumerate(manifest['commands'][:5]):
        argv=list(original)
        argv[-1]=str(out/f'overlay_{index}.o')
        subprocess.run(['nice','-n','15',*argv],check=True,timeout=300)
        commands.append(argv)
        objects.append(argv[-1])
    for name in ['react.cpp', 'dispatch.cpp', *('build/'+n for n in generated), 'fixture.cpp']:
        obj = out/(pathlib.Path(name).stem+'.o')
        argv = flags + ['-c', str(HERE/name), '-o', str(obj)]
        subprocess.run(['nice','-n','15',*argv], check=True, timeout=300)
        commands.append(argv)
        if name != 'fixture.cpp':
            objects.append(str(obj))
    excluded = {'lab_host.o', 'lab_dispatch.o', 'lab_combat.o', 'observer_v1_observer_v1_combat_rules.o', *(f'overlay_{i}.o' for i in range(5))}
    inherited = {}
    for path in manifest['link'][1:manifest['link'].index('-o')]:
        if pathlib.Path(path).name not in excluded:
            expected = manifest.get('reused_object_sha256', {}).get(path)
            if not expected or sha(pathlib.Path(path)) != expected:
                raise RuntimeError('parent object drift: '+path)
            inherited[path] = sha(pathlib.Path(path))
    links = []
    for target, files in [(BINARY, objects), (out/'react_fixture', [p for p in objects if not p.endswith('react_host.o')]+[str(out/'fixture.o')])]:
        argv = [manifest['link'][0], *files, *inherited, '-o', str(target)]
        subprocess.run(['nice','-n','15',*argv], check=True, timeout=120)
        links.append(argv)
        sources = dict(manifest['source_hashes'])
        for p in [HERE/'build.py', HERE/'react.h', HERE/'react.cpp', HERE/'dispatch.cpp', HERE/'fixture.cpp', *(out/n for n in generated)]:
            sources[str(p.relative_to(CPP))] = sha(p)
        record = dict(schema=2, engine='react_adapter_v1', scope='native_complete_engine',
                      sanitized=False, portable=False, source_hashes=sources,
                      binary_sha256=sha(target), commands=commands, link=argv,
                      reused_object_sha256=inherited, parent=parent_identity)
        target.with_suffix('.build.json').write_text(json.dumps(record, indent=2)+'\n')
    # Admission rechecks inputs after compile, catching concurrent source changes.
    if admit(parent) != parent_identity:
        raise RuntimeError('parent changed during build')
    receipt = dict(status='PASS', seconds=time.monotonic()-started,
                   identity=admit(BINARY), fixture_identity=admit(out/'react_fixture'),
                   commands=commands, links=links, parent=parent_identity,
                   execution='sequential; nice -n 15 requested for each compiler/link process; no fights',
                   priority_at_launch=os.getpriority(os.PRIO_PROCESS,0),
                   priority_limit='Sandbox may deny nice setpriority; inspect build stderr. No parallel workers.')
    (HERE/'BUILD.json').write_text(json.dumps(receipt, indent=2)+'\n')
    print('Build PASS', round(receipt['seconds'],2), 'seconds')

if __name__ == '__main__':
    build()
