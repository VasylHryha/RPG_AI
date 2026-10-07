"""Build new overlay/observer host, reusing pinned focus-engine objects read-only."""
import pathlib,json,subprocess,time,hashlib,sys
HERE=pathlib.Path(__file__).resolve().parent;CPP=HERE.parent;REPO=CPP.parents[2];sys.path.insert(0,str(CPP));from build_admission import sha,admit
from common import stage,remaining
BINARY=CPP/'build/astelia_native_spacing_probe_v1'
@stage('build')
def main():
 start=time.time();awake=time.monotonic();old=CPP/'build/astelia_native_focus_probe_v1';admit(old);m=json.loads(old.with_suffix('.build.json').read_text());commands=[];objects=[];observer=CPP/'build/astelia_native_observer_v1';admit(observer);om=json.loads(observer.with_suffix('.build.json').read_text());assert sha(observer.with_suffix('.build.json'))==m['reused_observer_manifest_sha256']
 for name in ('spacing.cpp','dispatch.cpp','host.cpp','../src/native/s4_focus_probe_v1.cpp'):
  argv=m['commands'][0][:];argv=argv[:argv.index('-c')]+['-I'+str(CPP/'src/native'),'-I'+str(CPP/'src'),'-I'+str(HERE),'-c',str(HERE/name),'-o',str(BINARY.parent/('spacing_v1_'+pathlib.Path(name).stem+'.o'))];subprocess.run(argv,check=True,timeout=remaining());commands.append(argv);objects.append(argv[-1])
 inherited=[o for o in m['link'][1:-2] if not o.endswith(('s4_focus_probe_v1.cpp.o','s4_focus_probe_v1.o','s4_focus_probe_v1_dispatch.o','observer_v1_host_observer_v1.o'))]
 stamped={str(pathlib.Path(c[-1])):c for c in om['commands']}
 for objname in inherited:
  command=stamped[objname];obj=pathlib.Path(objname);fingerprint=hashlib.sha256((json.dumps(om['source_hashes'],sort_keys=True)+json.dumps(command)).encode()).hexdigest();assert obj.with_suffix('.fingerprint').read_text().splitlines()==[fingerprint,sha(obj)],objname
 objects+=inherited
 link=[m['link'][0],*objects,'-o',str(BINARY)];subprocess.run(link,check=True,timeout=remaining())
 hashes=dict(m['source_hashes']);hashes.update({str((HERE/n).relative_to(CPP)):sha(HERE/n) for n in ('spacing.cpp','spacing.h','dispatch.cpp','host.cpp','build.py')})
 m.update(source_hashes=hashes,engine='native_spacing_probe_v1',binary_sha256=sha(BINARY),commands=commands,link=link,reused_focus_manifest_sha256=sha(old.with_suffix('.build.json')),reused_object_sha256={o:sha(pathlib.Path(o)) for o in inherited},elapsed_seconds=time.monotonic()-awake)
 BINARY.with_suffix('.build.json').write_text(json.dumps(m,indent=2)+'\n');admit(BINARY)
 print(json.dumps(dict(status='BUILT',seconds=time.monotonic()-awake)))
if __name__=='__main__':
 from common import caffeinate
 caffeinate();main()
