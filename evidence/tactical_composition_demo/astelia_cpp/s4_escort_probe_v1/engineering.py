"""Claude-only gated engineering fights: P11 historical byte parity; resumable."""
import gzip
from common import *
from run import RAW,request,verified,execute

def main():
 d=pins();assert json.loads((HERE/'CHECKS.json').read_text())['status']=='PASS';identity=admit(BINARY)
 if (HERE/'ENGINEERING.json').exists():
  r=json.loads((HERE/'ENGINEERING.json').read_text());assert r['status']=='PASS' and r['binary_identity']==identity and r['declaration_sha256']==sha(HERE/'DECLARATION.json')
  for row in r['fights']:
   req=json.loads((RAW/(row['id']+'_request.json')).read_text());assert verified(row['id'],req,CPP/'build'/row['binary_name'])
  print('Verified engineering completion; no replay');return
 RAW.mkdir(exist_ok=True);gate=pilot_gate(wait=True)
 @stage('engineering')
 def work():
  contracts=[];fights=[]
  with owned_deadline() as deadline:
   for arg in ('--attribution-contract','--v6-contract'):
    outs=[]
    for name in ('astelia_native_spacing_probe_v1','astelia_native_escort_probe_v1'):
     admit(CPP/'build'/name);r=deadline.run([str(CPP/'build'/name),arg],'',maximum=60);assert r.returncode==0;outs.append(r)
    assert outs[0].stdout==outs[1].stdout and outs[0].stderr==outs[1].stderr
    contracts.append(dict(argument=arg,stdout_sha256=hashlib.sha256(outs[0].stdout.encode()).hexdigest()))
   for head in d['heads']:
    data=[]
    for version,name in (('spacing_probe_v1','astelia_native_spacing_probe_v1'),('escort_probe_v1','astelia_native_escort_probe_v1')):
     tag=f'engineering_{head}_{version}';req=request('P11',head,d['engineering_seed'],0,duration=2,skeleton=version)
     r=execute(tag,req,deadline,gate,binary=CPP/'build'/name,meta=dict(binary_name=name));fights.append(r)
     with gzip.open(RAW/(tag+'.jsonl.gz'),'rb') as f:data.append(b''.join(line for line in f if not json.loads(line).get('escortProbe')))
    assert data[0]==data[1],('P11 historical bytes differ',head)
   pins();assert admit(BINARY)==identity
   exclusive(HERE/'ENGINEERING.json',dict(status='PASS',contracts=contracts,fights=fights,duration_s=2,binary_identity=identity,declaration_sha256=sha(HERE/'DECLARATION.json'),utc_end=utc()))
 work()
if __name__=='__main__':caffeinate();main()
