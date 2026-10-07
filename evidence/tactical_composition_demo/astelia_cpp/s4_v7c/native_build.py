"""Copy the sealed combat binary; build a separate, strictly parse-only checker."""
import shutil
from common import *

def build():
 start=time.monotonic();out=HERE/'build';out.mkdir(exist_ok=True)
 expected=read(ORIGIN/'DECLARATION.json')['binary']
 if admit(ORIGIN/'build/astelia_native_v7')!=expected:raise RuntimeError('v7b sealed binary/source drift')
 fixture_hash=read(ORIGIN/'ENGINEERING.json')['fixture_sha256']
 if sha(ORIGIN/'build/fixture')!=fixture_hash:raise RuntimeError('v7b fixture drift')
 for name in ('astelia_native_v7','astelia_native_v7.build.json','fixture'):
  source=ORIGIN/'build'/name;target=out/name
  if target.exists():raise RuntimeError('partial build exists; preserve and stop')
  shutil.copy2(source,target)
  if sha(source)!=sha(target):raise RuntimeError('copy mismatch')
 m=read(out/'astelia_native_v7.build.json');objects=[];commands=[]
 # Recompile only into our own directory. The combat executable is never rebuilt.
 for index,original in enumerate(m['commands'][:-1]):
  cmd=list(original);cmd[-1]=str(out/f'check_{index}.o')
  subprocess.run(cmd,check=True,timeout=180);commands.append(cmd);objects.append(cmd[-1])
 for path,h in m['reused_object_sha256'].items():
  if sha(path)!=h:raise RuntimeError('sealed inherited object drift: '+path)
  objects.append(path)
 cmd=list(m['commands'][-1]);cmd[cmd.index('-c')+1]=str(HERE/'request_check.cpp');cmd[-1]=str(out/'request_check.o')
 subprocess.run(cmd,check=True,timeout=180);commands.append(cmd)
 link=[m['link'][0],*objects,cmd[-1],'-o',str(out/'request_check')]
 subprocess.run(link,check=True,timeout=90)
 return dict(status='PASS',identity=admit(BINARY),fixture_sha256=fixture_hash,
             request_checker_sha256=sha(out/'request_check'),request_checker_source_sha256=sha(HERE/'request_check.cpp'),commands=commands,link=link,
             reused_object_sha256=m['reused_object_sha256'],seconds=time.monotonic()-start,
             inherited_from='s4_v7b; byte-identical combat binary/manifest/fixture',
             checker_scope='unchanged native configuration and constructors only; no World')
