"""Bounded E1/DONE/V2 CLI checks; hash preservation checks; no new fights."""
import hashlib
import json
import os
import pathlib
import subprocess
import sys
import time
HERE=pathlib.Path(__file__).resolve().parent
LAB=HERE.parent
manifest=json.loads((LAB/'E1_REPORTING_R2.json').read_text())
def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
    return h.hexdigest()
def preserved():
    for name,digest in manifest['historical_files'].items():
        if sha(LAB/name)!=digest:raise RuntimeError('historical artifact changed: '+name)
    for tag,digest in manifest['inherited_receipts'].items():
        path=LAB/'raw'/(tag+'_COMPLETE.json')
        if sha(path)!=digest:raise RuntimeError('original receipt changed: '+tag)
        r=json.loads(path.read_text())
        for suffix,key in [('.jsonl.gz','raw_sha256'),('_request.json','request_sha256'),('_CLAIM.json','claim_sha256'),('_stderr.log','stderr_sha256')]:
            if sha(LAB/'raw'/(tag+suffix))!=r[key]:raise RuntimeError('original raw sidecar changed: '+tag+suffix)
preserved()
assert json.loads((LAB/'RUN_mechanism_E1.json').read_text())['status']=='DONE'
rows=[]
for args in [('report','--arm','E1'),('run','--arm','E1','--stage','mechanism'),('report','--arm','V2')]:
    started=time.monotonic()
    result=subprocess.run([sys.executable,'-B',str(LAB/'lab.py'),*args],text=True,capture_output=True,timeout=30,env={**os.environ,'SHAPE_LAB_V6_CAFFEINATED':'1','PYTHONDONTWRITEBYTECODE':'1'})
    row=dict(args=list(args),returncode=result.returncode,seconds=time.monotonic()-started,stdout=result.stdout,stderr=result.stderr)
    rows.append(row)
    if result.returncode:raise RuntimeError(row)
preserved()
summary=json.loads((LAB/'MECHANISM_E1_SUMMARY_R2.json').read_text())
assert summary['arm']=='E1' and summary['complete'] and list(summary['drills'])==['D5'] and all(summary['arms'][a]['n']==20 for a in ('base','E1'))
assert summary['paired']['base minus E1']['n']==20 and not summary['mechanism_gate_observations']['activated']
report=dict(status='PASS',new_fights=0,inherited_receipts_verified=len(manifest['inherited_receipts']),historical_artifacts_verified=len(manifest['historical_files']),commands=rows)
(HERE/'VERIFY_E1_R2.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
