"""Reuse the sealed v7 executable and observation fixture byte for byte; no rebuild."""
import pathlib,shutil,sys,time,json
HERE=pathlib.Path(__file__).resolve().parent;CPP=HERE.parent
sys.path.append(str(CPP))
from build_admission import admit,sha

def build():
 start=time.monotonic();old=CPP/'s4_v7';out=HERE/'build';out.mkdir(exist_ok=True)
 expected=json.loads((old/'DECLARATION.json').read_text())['binary']
 binary=old/'build/astelia_native_v7'
 if admit(binary)!=expected:raise RuntimeError('sealed v7 binary/source drift')
 fixture=old/'build/fixture'
 if sha(fixture)!=json.loads((old/'ENGINEERING.json').read_text())['fixture_sha256']:raise RuntimeError('sealed v7 observation fixture drift')
 for name in ('astelia_native_v7','astelia_native_v7.build.json','fixture'):
  source=old/'build'/name;target=out/name
  if target.exists():raise RuntimeError('existing partial binary copy; preserve and stop')
  shutil.copy2(source,target)
  if sha(source)!=sha(target):raise RuntimeError('binary copy mismatch')
 if admit(out/'astelia_native_v7')!=expected:raise RuntimeError('copied identity mismatch')
 return dict(status='PASS',identity=expected,fixture_sha256=sha(out/'fixture'),seconds=time.monotonic()-start,inherited_from='s4_v7 sealed 23ba9fc; byte-identical binary/manifest/fixture')
if __name__=='__main__':print(json.dumps(build()))
