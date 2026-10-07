"""Independent stored-only entropy, engineering-byte parity, and timing audit.

Run after part1_recount has verified the complete RAW_FILES_LOCAL inventory.
No combat/execution modules are imported; no original artifact is written.
"""
import gzip,hashlib,json,pathlib
OUT=pathlib.Path(__file__).resolve().parent
SRC=OUT.parent/'s4_escort_probe_v1'
REPO=OUT.parents[3]

def numbers(x):
    if type(x) is int:
        return {x}
    if isinstance(x,list):
        return set().union(*(numbers(v) for v in x)) if x else set()
    if isinstance(x,dict):
        return set().union(*(numbers(v) for v in x.values())) if x else set()
    return set()

def main():
    ledger=json.loads((SRC/'DEVELOPMENT_SEED_LEDGER.json').read_text())
    seeds=set(ledger['seeds']+[ledger['engineering_seed']])
    sources=[]
    for name,digest in ledger['previous_development_ledgers'].items():
        path=REPO/name
        assert hashlib.sha256(path.read_bytes()).hexdigest()==digest
        assert not seeds & numbers(json.loads(path.read_text()))
        sources.append(dict(path=name,sha256=digest,no_seed_overlap=True))
    parity=[]
    for head in ['regular','novice']:
        def raw(skeleton):
            path=SRC/'raw'/f'engineering_{head}_{skeleton}.jsonl.gz'
            with gzip.open(path,'rb') as stream:
                return b''.join(line for line in stream if not json.loads(line).get('escortProbe'))
        left=raw('spacing_probe_v1');right=raw('escort_probe_v1')
        assert left==right
        for skeleton in ['spacing_probe_v1','escort_probe_v1']:
            request=json.loads((SRC/'raw'/f'engineering_{head}_{skeleton}_request.json').read_text())
            assert request['options']['seed']==ledger['engineering_seed']
            assert request['options']['duration']==2
            assert request['options']['ai'][0]['controller']=='P11'
        parity.append(dict(head=head,byte_equal_except_escort_rows=True,normalized_bytes=len(left),normalized_sha256=hashlib.sha256(left).hexdigest()))
    stages=[dict(path=path.name,**json.loads(path.read_text())) for path in sorted(SRC.glob('STAGE_*.json'))]
    result=dict(status='PASS',prior_development_ledgers=sources,judging_ledgers_read=False,engineering_parity=parity,recorded_stages=stages,total_stage_awake_s=sum(stage['awake_seconds'] for stage in stages))
    (OUT/'part1_supplemental_identity.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS: prior development entropy, engineering bytes/seed, recorded timing')

if __name__=='__main__':
    main()
