"""Optional-to-now, mandatory-before-panel historical byte-parity preflight."""
import json,subprocess,time,sys
from common import *
sys.path.insert(0,str(CPP));from build_admission import admit

@stage('engineering')
def main():
 pilot_gate(wait=True);d=pins();admit(BINARY)
 raw=HERE/'raw';raw.mkdir(exist_ok=True)
 claim=raw/'ENGINEERING_CLAIMED_ONCE.json'
 with claim.open('x') as f:json.dump(dict(seed=d['engineering_seed']),f)
 start=time.monotonic();rows=[]
 for arg in ('--attribution-contract','--v6-contract'):
  results=[subprocess.run([str(CPP/'build'/n),arg],capture_output=True,check=True,timeout=min(60,remaining())) for n in ('astelia_native_v6','astelia_native_observer_v1','astelia_native_focus_probe_v1','astelia_native_spacing_probe_v1')]
  assert all(r.stdout==results[0].stdout and r.stderr==results[0].stderr for r in results)
  rows.append(dict(argument=arg,sha256=hashlib.sha256(results[0].stdout).hexdigest(),bytes=len(results[0].stdout)))
 for head in ('regular','novice'):
  req=json.loads((HERE/(head.upper()+'_REQUEST_TEMPLATE.json')).read_text());req['options']['seed']=d['engineering_seed'];req['options']['duration']=2;outs=[]
  for version,name in (('focus_probe_v1','astelia_native_focus_probe_v1'),('spacing_probe_v1','astelia_native_spacing_probe_v1')):
   req['options']['ai'][0]['skeleton']=version
   r=subprocess.run([str(CPP/'build'/name),'--metrics'],input=(json.dumps(req)+'\n').encode(),capture_output=True,check=True,timeout=min(30,remaining()))
   (raw/f'engineering_{head}_{version}.stdout').write_bytes(r.stdout);(raw/f'engineering_{head}_{version}.stderr').write_bytes(r.stderr);outs.append(r)
  assert outs[0].stdout==outs[1].stdout and outs[0].stderr==outs[1].stderr
  rows.append(dict(head=head,byte_identical=True,stdout_sha256=hashlib.sha256(outs[1].stdout).hexdigest()))
 write(HERE/'ENGINEERING.json',dict(status='PASS',rows=rows,fights=4,duration_s=2,binary_identity=admit(BINARY)))
if __name__=='__main__':
 from common import caffeinate
 caffeinate();main()
