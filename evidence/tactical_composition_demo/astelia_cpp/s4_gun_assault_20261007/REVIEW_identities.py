"""Stored-only executed-build and accepted-freeze identity review."""
import pathlib,json,hashlib
H=pathlib.Path(__file__).resolve().parent;C=H.parent;R=H.parents[3]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
id=json.loads((H/'INPUT_IDENTITY.json').read_text());out={}
for key,name in [('observer_build','astelia_native_observer_v1'),('v6_build','astelia_native_v6')]:
 b=id[key];assert sha(C/'build'/name)==b['binary_sha256'];assert sha(C/'build'/(name+'.build.json'))==b['manifest_sha256']
 for p,v in b['sources'].items():assert sha(C/p)==v,p
 out[key]={'sources_verified':len(b['sources']),'binary_sha256':b['binary_sha256'],'manifest_sha256':b['manifest_sha256']}
for receipt in ['evidence/c1_r006/results.json','evidence/c2_r002/results.json']:
 hashes=json.loads((R/receipt).read_text())['file_hashes']
 for n,v in hashes.items():assert sha(R/n)==v,n
 out[receipt]={'receipt_bound_hashes_verified':len(hashes)}
status=json.loads((R/'STATUS.json').read_text())
for milestone in ['c4','c5']:
 hashes=status['milestones'][milestone]['frozen_hashes']
 for n,v in hashes.items():assert sha(R/n)==v,n
 out[milestone]={'frozen_hashes_verified':len(hashes)}
out['status']='PASS';(H/'REVIEW_BUILD_IDENTITIES.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
