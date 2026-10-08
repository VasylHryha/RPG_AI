"""Seal original measurements for hash-only reuse, without decoding raw JSONL."""
import hashlib
import json
import pathlib
HERE=pathlib.Path(__file__).resolve().parent.parent

def sha(p):
    digest=hashlib.sha256()
    with p.open('rb') as stream:
        for block in iter(lambda:stream.read(1024*1024),b''):digest.update(block)
    return digest.hexdigest()

def main():
    path=HERE/'E1_REPORTING_R2.json'
    if path.exists():raise RuntimeError('revision already sealed')
    receipts={}
    for p in sorted((HERE/'raw').glob('*_COMPLETE.json')):
        r=json.loads(p.read_text());tag=p.name.removesuffix('_COMPLETE.json')
        if r['tag']!=tag or sha(HERE/'raw'/(tag+'.jsonl.gz'))!=r['raw_sha256']:raise RuntimeError('inherited raw/receipt drift: '+tag)
        receipts[tag]=sha(p)
    declaration=json.loads((HERE/'DECLARATION.json').read_text())
    if sha(HERE/'e1_fix_diagnostics/original/lab.py')!=declaration['source_hashes']['s4_shape_lab_v6/lab.py']:raise RuntimeError('original tool snapshot drift')
    historical={p.name:sha(p) for p in sorted(HERE.glob('*.json'))}
    tools=('lab.py','lab_r2.py','report_r2.py','receipt_identity_r2.py','test_e1_r2.py')
    record=dict(schema=2,status='REPORTING_REPAIR_ONLY_NO_NEW_FIGHTS',declaration_sha256=sha(HERE/'DECLARATION.json'),metrics_sha256=sha(HERE/'metrics.py'),tool_hashes={name:sha(HERE/name) for name in tools},inherited_receipts=receipts,historical_files=historical,receipt_order=[p.name.removesuffix('_COMPLETE.json') for p in (HERE/'raw').glob('*_COMPLETE.json')])
    with path.open('x') as out:json.dump(record,out,indent=2);out.write('\n')
if __name__=='__main__':main()
