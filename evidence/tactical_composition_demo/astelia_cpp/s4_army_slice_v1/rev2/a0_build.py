"""Build a local script host from admitted v6 inputs; never edit parent files."""
from pathlib import Path
import subprocess
import time
from a0_common import BINARY, CPP, HERE, code_hashes, load, read, sha, write
PARENT = CPP / 's4_shape_lab_v6/build/tactics_react_host_v6'

def once(text, old, new):
    if text.count(old) != 1:
        raise RuntimeError('A0 source seam drift: ' + old)
    return text.replace(old, new)

def generated_sources():
    out = BINARY.parent
    # Use the already admitted generated v6 code. No imports of a living lab runner.
    parent = PARENT.parent
    react = (parent/'react.cpp').read_text()
    react = '#include "a0_oracle.h"\n' + react
    # All arms independently advance the deterministic public-history unit policy.
    # This uses no World, teacher actions, private enemy state or teacher state.
    # The parent path remains intact: no 5 Hz cache and no nearest-target substitute.
    # Executed labels include participation and react/body precedence.
    react = once(react, 'reacting_[u.id]=reaction.active;records_[u.id]=r;readiness(u.id);',
                 '''reacting_[u.id]=reaction.active;records_[u.id]=r;readiness(u.id);
  shape.audit.push_back(js::obj({{"a0Label",true},{"role",r.role},{"id",double(u.id)},{"t",o.t},
   {"rawToExecuted",std::hypot(r.candidate.movement.x-r.executed.movement.x,r.candidate.movement.y-r.executed.movement.y)},
   {"activeFire",r.executed.fire!=FireIntent::Hold},{"readyLabel",records_.at(u.id).ready},{"react",r.active}}));''')
    # Heavy v6 shape audit is unnecessary in A0 (shape=base/O/O+G/T).
    react = once(react, 'shapes_v6::augment(*this);', '')
    combat = once((parent/'react_combat.cpp').read_text(), 'shapes_v6::geometry(w);', 'army_a0::geometry(w);')
    combat = '#include "a0_oracle.h"\n' + combat
    host = (parent/'lean_host.cpp').read_text()
    shapes = (CPP/'s4_shape_lab_v6/shapes.cpp').read_text()
    shapes = once(shapes, 'arm!="base"&&arm!="V2"&&arm!="E1"&&arm!="R1"&&arm!="E1+R1"',
                  'arm!="O"&&arm!="O+G"&&arm!="T"')
    return {name: content.replace('../../s4_', str(CPP/'s4_')).replace('../s4_shape_lab_v1/', str(CPP/'s4_shape_lab_v1')+'/')
            for name, content in {'react.cpp':react,'react_combat.cpp':combat,'lean_host.cpp':host,
                                  'shapes.cpp':shapes}.items()}

def build():
    start = time.monotonic()
    admission = load('a0_admission', CPP/'build_admission.py')
    identity = admission.admit(PARENT)
    record = read(PARENT.with_suffix('.build.json'))
    out = BINARY.parent
    out.mkdir(parents=True, exist_ok=True)
    generated = generated_sources()
    for name, content in generated.items():
        (out/name).write_text(content)
    for name in ('react.h','shapes.h','timing.h'):
        source = PARENT.parent/name if name=='react.h' else CPP/'s4_shape_lab_v6'/name
        content=source.read_text()
        if name=='react.h':
            content=once(content,' bool game=true;', ' bool game=true;')  # snapshot layout stays unchanged

        (out/name).write_text(content)
    flags = record['commands'][0][:record['commands'][0].index('-c')]
    flags = [flags[0], '-I'+str(out), '-I'+str(HERE), *flags[1:]]
    commands = []; objects = []; reused = {}
    def compile(source, name):
        obj = out/name
        argv = [*flags, '-c', str(source), '-o', str(obj)]
        subprocess.run(['nice','-n','15',*argv], check=True, timeout=180)
        commands.append(argv); objects.append(str(obj))
    replacements = {name.removesuffix('.cpp')+'.o':out/name for name in generated if name!='oracle_overlay.cpp'}
    local = {argv[-1]:argv for argv in record['commands']}
    for path in record['link'][1:record['link'].index('-o')]:
        name = path.rsplit('/',1)[-1]
        if name in replacements:
            compile(replacements[name], name)
        elif path in record['reused_object_sha256']:
            if sha(path)!=record['reused_object_sha256'][path]:
                raise RuntimeError('parent object drift: '+path)
            reused[path] = sha(path)
        elif path in local:
            argv = local[path]; source = argv[argv.index('-c')+1]
            source=Path(source)
            if source.parent==PARENT.parent or source.parent==CPP/'s4_shape_lab_v6':
                content=source.read_text().replace('../../s4_', str(CPP/'s4_')).replace('../s4_shape_lab_v1/', str(CPP/'s4_shape_lab_v1')+'/')
                source=out/source.name;source.write_text(content)
            compile(source, name)
        else:
            raise RuntimeError('unbound parent object: '+path)
    compile(HERE/'a0_oracle.cpp','a0_oracle.o')
    link = [record['link'][0], *objects, *reused, '-o', str(BINARY)]
    subprocess.run(['nice','-n','15',*link], check=True, timeout=120)
    if admission.admit(PARENT)!=identity:
        raise RuntimeError('parent drift during build')
    sources = {k:v for k,v in record['source_hashes'].items() if k.endswith(('.py','.cpp','.h','.json'))}
    sources.update(code_hashes())
    for path in out.glob('*'):
        if path.suffix in ('.cpp','.h'):
            sources[str(path.relative_to(CPP))] = sha(path)
    write(BINARY.with_suffix('.build.json'), dict(schema=2,engine='army_a0_script',scope='native_complete_engine',
          sanitized=False,portable=False,source_hashes=sources,binary_sha256=sha(BINARY),commands=commands,
          link=link,reused_object_sha256=reused,parent=identity))
    write(HERE/'A0_BUILD.json',dict(status='BUILT_NOT_FIGHT_VERIFIED',seconds=time.monotonic()-start,
                                 identity=admission.admit(BINARY),fights=0))

if __name__=='__main__':
    build()
