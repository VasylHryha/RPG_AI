"""Record review-driven edits before combat, preserving unused entropy and prior declaration."""
import json
from common import *

def main():
 assert not (HERE/'raw').exists(), 'cannot reseal after any engineering/development claim'
 path=HERE/'DECLARATION.json';prior=HERE/'PRE_RECHECK_DECLARATION.json'
 assert not prior.exists(), 'single precombat correction batch only'
 prior.write_bytes(path.read_bytes());d=json.loads(path.read_text())
 new={str(p.relative_to(REPO)):sha(p) for p in HERE.iterdir() if p.is_file() and p.suffix in ('.py','.cpp','.h','.md') and p.name!='OWNER_RECHECK.md'}
 write(HERE/'PRECOMBAT_CORRECTIONS.json',dict(status='BEFORE_ANY_FIGHT',previous_declaration_sha256=sha(prior),changes={n:dict(before=d['implementation_hashes'].get(n),after=h) for n,h in new.items() if d['implementation_hashes'].get(n)!=h},reason='independent owner recheck corrections; no rule/constant/seed change',entropy_unconsumed=True))
 d['implementation_hashes']=new;d['policy_sha256']=sha(HERE/'POLICY.md');d['precombat_corrections_sha256']=sha(HERE/'PRECOMBAT_CORRECTIONS.json');write(path,d)
 print('Sealed complete precombat correction batch; same unused entropy and constants.')

if __name__=='__main__':main()
