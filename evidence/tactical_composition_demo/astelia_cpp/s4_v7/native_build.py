"""New host/controller objects; validated inherited engine objects remain read-only."""
import json, pathlib, subprocess, sys, time, hashlib
HERE=pathlib.Path(__file__).resolve().parent; CPP=HERE.parent
sys.path.append(str(CPP))
from build_admission import admit,sha

def build():
 start=time.monotonic(); out=HERE/'build'; out.mkdir(exist_ok=True)
 old=CPP/'build/astelia_native_focus_probe_v1'; admit(old)
 m=json.loads(old.with_suffix('.build.json').read_text())
 observer=CPP/'build/astelia_native_observer_v1'; admit(observer)
 om=json.loads(observer.with_suffix('.build.json').read_text())
 if sha(observer.with_suffix('.build.json'))!=m['reused_observer_manifest_sha256']:raise RuntimeError('observer build drift')
 inherited=[o for o in m['link'][1:-2] if not o.endswith(('s4_focus_probe_v1.cpp.o','s4_focus_probe_v1.o','s4_focus_probe_v1_dispatch.o','observer_v1_host_observer_v1.o'))]
 stamped={str(pathlib.Path(c[-1])):c for c in om['commands']}
 for name in inherited:
  obj=pathlib.Path(name); command=stamped[name]
  fingerprint=hashlib.sha256((json.dumps(om['source_hashes'],sort_keys=True)+json.dumps(command)).encode()).hexdigest()
  if obj.with_suffix('.fingerprint').read_text().splitlines()!=[fingerprint,sha(obj)]:raise RuntimeError('inherited object drift: '+name)
 sources=['src/native/s4_focus_probe_v1.cpp','s4_spacing_probe_v1/spacing.cpp','s4_escort_probe_v1/escort.cpp','s4_escort_probe_v3/escort.cpp','src/native/s4_v7_controller.cpp','src/native/s4_v7_dispatch.cpp','src/native/s4_v7_host.cpp']
 commands=[]; objects=[]
 for i,name in enumerate(sources):
  flags=m['commands'][0][:m['commands'][0].index('-c')]
  argv=flags+['-I'+str(CPP/'src/native'),'-I'+str(CPP/'src'),'-I'+str(CPP/'s4_spacing_probe_v1'),'-c',str(CPP/name),'-o',str(out/f'v7_{i}.o')]
  subprocess.run(argv,check=True,timeout=180); commands.append(argv); objects.append(argv[-1])
 binary=out/'astelia_native_v7'; link=[m['link'][0],*objects,*inherited,'-o',str(binary)]
 subprocess.run(link,check=True,timeout=90)
 # Transitive engine inputs from the delivered focus build, plus all overlay/new inputs.
 hashes=dict(m['source_hashes'])
 for directory in ('s4_spacing_probe_v1','s4_escort_probe_v1','s4_escort_probe_v3'):
  for p in (CPP/directory).iterdir():
   if p.suffix in ('.cpp','.h'):hashes[str(p.relative_to(CPP))]=sha(p)
 for p in (CPP/'src/native').glob('s4_v7_*'):hashes[str(p.relative_to(CPP))]=sha(p)
 manifest=dict(schema=2,engine='native_v7',scope='native_complete_engine',sanitized=False,portable=False,source_hashes=hashes,binary_sha256=sha(binary),commands=commands,link=link,reused_object_sha256={o:sha(pathlib.Path(o)) for o in inherited})
 binary.with_suffix('.build.json').write_text(json.dumps(manifest,indent=2)+'\n')
 # Same link graph, replacing host only, for observation-only contracts.
 fixture=out/'fixture';argv=commands[-1][:];argv[argv.index('-c')+1]=str(CPP/'src/native/s4_v7_fixture.cpp');argv[-1]=str(out/'fixture.o')
 subprocess.run(argv,check=True,timeout=90)
 subprocess.run([link[0],*objects[:-1],argv[-1],*inherited,'-o',str(fixture)],check=True,timeout=90)
 return dict(status='PASS',identity=admit(binary),fixture_sha256=sha(fixture),seconds=time.monotonic()-start)
if __name__=='__main__':print(json.dumps(build()))
