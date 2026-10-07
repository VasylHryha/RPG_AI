"""Reuse admitted observer objects; compile only the new controller and dispatch."""
import pathlib,json,subprocess,time,hashlib
from build import ROOT
from build_admission import admit,sha

def main():
 old=ROOT/'build/astelia_native_observer_v1';admit(old);m=json.loads(old.with_suffix('.build.json').read_text());start=time.monotonic();target=ROOT/'build/astelia_native_focus_probe_v1'
 sources=['src/native/s4_focus_probe_v1.cpp','src/native/s4_focus_probe_v1_dispatch.cpp'];commands=[];objects=[]
 for n in sources:
  argv=m['commands'][0][:];argv=argv[:argv.index('-c')]+['-c',str(ROOT/n),'-o',str(target.parent/(pathlib.Path(n).stem+'.o'))];subprocess.run(argv,check=True);commands.append(argv);objects.append(argv[-1])
 for command in m['commands']:
  obj=pathlib.Path(command[-1]);stamp=obj.with_suffix('.fingerprint').read_text().splitlines();fingerprint=hashlib.sha256((json.dumps(m['source_hashes'],sort_keys=True)+json.dumps(command)).encode()).hexdigest();assert stamp==[fingerprint,sha(obj)],str(obj)
 objects += [o for o in m['link'][1:-2] if not o.endswith('observer_v1_observer_v1_dispatch.o')]
 link=[m['link'][0],*objects,'-o',str(target)];subprocess.run(link,check=True)
 hashes=dict(m['source_hashes']);hashes.update({n:sha(ROOT/n) for n in sources+['src/native/s4_focus_probe_v1.h','build_focus_probe_v1.py']})
 m.update(source_hashes=hashes,engine='native_focus_probe_v1',binary_sha256=sha(target),commands=commands,link=link,elapsed_seconds=time.monotonic()-start,reused_observer_manifest_sha256=sha(old.with_suffix('.build.json')))
 target.with_suffix('.build.json').write_text(json.dumps(m,indent=2)+'\n');admit(target);print(json.dumps(dict(build_seconds=m['elapsed_seconds'],binary_sha256=m['binary_sha256'])))
if __name__=='__main__':main()
