"""Independent read-only verification of recorded artifacts, no panel execution."""
import gzip
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import xml.etree.ElementTree as ET

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from tools import gate

folder = ROOT / 'evidence/c2_r002'
result = json.loads((folder/'results.json').read_text())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
canonical = lambda v: json.dumps(v, sort_keys=True, separators=(',', ':'), allow_nan=False)
digest = lambda v: hashlib.sha256(canonical(v).encode()).hexdigest()
assert result['source_commit'] == '63ae7ddc5d11f4c7b59972227c2c0ebf7fbc0cdf'
for name, expected in result['file_hashes'].items():
    assert sha(ROOT/name) == sha(folder/'source'/name) == expected, name
    committed = subprocess.check_output(['git','show',result['source_commit']+':'+name], cwd=ROOT)
    assert hashlib.sha256(committed).hexdigest() == expected, name
assert result['file_hashes'] == result['source_snapshot_hashes']
assert result['manifest_hash'] == digest(result['manifest'])
assert json.loads((ROOT/'experiments/c2_manifest.json').read_text()) == result['manifest']
contract = json.loads((folder/'EVIDENCE_CONTRACT.json').read_text())
assert contract['source_file_hashes'] == result['file_hashes']
assert contract['source_commit'] == result['source_commit']
assert contract['results_sha256'] == sha(folder/'results.json')
pipeline = json.loads((folder/'PIPELINE.json').read_text())
assert pipeline['fingerprint'] == gate.fingerprint()
stamps = json.loads(gate.stamp_path(pipeline['fingerprint'],'c2').read_text())
for entry in pipeline['stages']:
    stage = entry['stage']
    assert {k:v for k,v in entry.items() if k != 'stage'} == stamps[stage]
    assert entry['commit'] == result['source_commit']
    for name, expected in entry['artifacts'].items():
        assert sha(ROOT/name) == expected, name
        assert gate._artifact_valid(stage, ROOT/name)
assert gate.verified('c2') == ['preflight','tests','smoke','mutation','panel']
build = json.loads((folder/'BUILD.json').read_text())
assert build == json.loads((ROOT/'.gate/c2_backend/BUILD.json').read_text())
assert build['source_sha256'] == sha(ROOT/'native/c2/relaxation.cpp')
assert build['binary_sha256'] == sha(ROOT/'.gate/c2_backend/relaxation.dylib')
assert sha(folder/'contracts.xml') == result['contracts']['report_sha256']
cases = list(ET.parse(folder/'contracts.xml').getroot().iter('testcase'))
assert len(cases) == 23
assert all(not any(c.iter(tag)) for c in cases for tag in ('failure','error','skipped'))
properties = {p.attrib['name']:p.attrib['value'] for p in ET.parse(folder/'contracts.xml').getroot().iter('property')}
assert properties['c2_fingerprint'] == pipeline['fingerprint']
mutation = json.loads((folder/'MUTATION.json').read_text())
assert mutation['total'] == mutation['detected'] == 4
assert mutation['fingerprint'] == pipeline['fingerprint']
mutation_stage = next(e for e in pipeline['stages'] if e['stage']=='mutation')
assert sha(folder/'MUTATION.json') == next(iter(mutation_stage['artifacts'].values()))
rows = result['instances']
assert len(rows)==40
assert rows == [json.loads(line) for line in (folder/'instances.jsonl').read_text().splitlines()]
assert {(r['task'],r['trial']) for r in rows} == {(t,i) for t in ['affine','realizable'] for i in range(20)}
state_bindings = orders = 0
for row in rows:
    assert json.loads((folder/'trial_receipts'/f"{row['task']}_s{row['initialization_seed']}.json").read_text()) == row
    artifact = json.loads((folder/row['artifact']).read_text())
    assert digest(artifact) == row['artifact_sha256']
    for key in ['initial','final']:
        assert digest(artifact[key+'_state']) == row[key+'_state_sha256']
        state = dict(artifact[key+'_state']); expected = state.pop('checksum')
        assert digest(state) == expected
        assert state['manifest_hash'] == result['manifest_hash']
        state_bindings += 1
    i = row['trial']; m = result['manifest']
    assert row['initialization_seed']==m['initialization_seeds'][i]
    for name in ['dataset','teacher','order']:
        assert row[name+'_seed']==m[name+'_seed_start']+i
    x = np.random.default_rng(row['dataset_seed']).uniform(0,1,(350,2))
    assert np.array_equal(x, artifact['inputs'])
    initial_g=np.random.default_rng(row['initialization_seed']).uniform(.5,1.5,24)
    assert np.array_equal(initial_g,artifact['initial_state']['conductances'])
    if row['task']=='affine':
        labels=.2*x[:,0]+.5*x[:,1]
        assert artifact['teacher_conductances'] is None
    else:
        teacher=np.random.default_rng(row['teacher_seed']).uniform(.5,1.5,24)
        assert np.array_equal(teacher,artifact['teacher_conductances'])
        edges=artifact['initial_state']['edges']
        incidence=np.zeros((24,16))
        for k,(a,b) in enumerate(edges): incidence[k,a]=1.; incidence[k,b]=-1.
        matrix=incidence.T @ np.diag(teacher) @ incidence+.01*np.eye(16)
        unknown=[k for k in range(16) if k not in (0,3)]
        coefficients=np.linalg.solve(matrix[np.ix_(unknown,unknown)],-matrix[np.ix_(unknown,[0,3])])[unknown.index(10)]
        labels=x@coefficients
    assert np.allclose(labels,artifact['targets'],rtol=1e-14,atol=1e-15)
    rng = np.random.default_rng(row['order_seed'])
    for order in artifact['sample_orders']:
        assert np.array_equal(order,rng.permutation(100)); orders+=1
    for method,predictions in artifact['predictions'].items():
        p=np.asarray(predictions); y=np.asarray(artifact['targets'])
        assert len(p)==350 and np.isfinite(p).all()
        for split,sl in [('train',slice(0,100)),('validation',slice(100,150)),('test',slice(150,350))]:
            mse=float(np.mean((p[sl]-y[sl])**2))
            assert np.isclose(mse,row['metrics'][method][split]['mse'],rtol=1e-14,atol=1e-30)
    assert artifact['predictions']['feedback_removed']==artifact['predictions']['frozen_random']
    assert row['check_status']=='PASS' and all(row['gates'].values()) and not row['failures']
# Recompute uncertainty directly, without evaluator summarize/interval functions.
recomputed={}
for task in ['affine','realizable']:
    group=sorted([r for r in rows if r['task']==task],key=lambda r:r['trial'])
    a=np.array([r['metrics']['candidate']['test']['mse'] for r in group])
    b=np.array([r['metrics']['frozen_random']['test']['mse'] for r in group])
    checks={'candidate_mse':(a,result['tasks'][task]['test_mse']['candidate']),
            'relative_reduction':((b-a)/b,result['tasks'][task]['paired_relative_reduction']),
            'paired_difference':(a-b,result['tasks'][task]['paired_candidate_minus_frozen_mse'])}
    recomputed[task]={}
    for name,(values,record) in checks.items():
        indices=np.random.default_rng(25000000).integers(0,20,(2000,20))
        ci=np.quantile(values[indices].mean(axis=1),[.025,.975]).tolist()
        assert float(values.mean())==record['mean'] and ci==record['ci95']
        recomputed[task][name]={'mean':float(values.mean()),'ci95':ci}
c1=json.loads((ROOT/'evidence/c1_r006/results.json').read_text())
for name,expected in c1['file_hashes'].items(): assert sha(ROOT/name)==expected, name
acceptance=ROOT/'evidence/c1_r006_independent/INDEPENDENT_REVIEW.md'
assert 'Verdict: **ACCEPTED**.' in acceptance.read_text()
assert sha(acceptance)==result['c1_acceptance']['receipt_sha256']
assert sha(ROOT/'evidence/c1_r006/results.json')==result['c1_acceptance']['results_sha256']
historical=ROOT/'evidence/c2_r001'
failure=json.loads((historical/'FAILURE.json').read_text())
integrity=json.loads((historical/'INTEGRITY.json').read_text())
for name,expected in integrity['files'].items(): assert sha(historical/name)==expected,name
assert failure['check_status']=='INFRASTRUCTURE_FAILURE'
assert len(list((historical/'trials').glob('*.json')))==11
assert (historical/'instances.jsonl').read_text()==''
old_manifest=json.loads((ROOT/'experiments/c2_r4_001_manifest.json').read_text())
for name in ['dataset','teacher','order']:
    assert not set(range(old_manifest[name+'_seed_start'],old_manifest[name+'_seed_start']+20)) & set(range(m[name+'_seed_start'],m[name+'_seed_start']+20))
assert not set(old_manifest['initialization_seeds']) & set(m['initialization_seeds'])
initial=ROOT/'evidence/c2_dev_checks/initial_contracts.xml.gz'
initial_xml=ET.fromstring(gzip.decompress(initial.read_bytes()))
assert len(list(initial_xml.iter('failure')))==1
# Historical files are byte-identical to the committed evidence being reviewed.
historical_files=list(historical.rglob('*'))+[initial]
count=0
for path in historical_files:
    if path.is_file():
        name=str(path.relative_to(ROOT))
        committed=subprocess.check_output(['git','show','c4400f7:'+name],cwd=ROOT)
        assert committed==path.read_bytes(),name
        count+=1
report={'status':'PASS','source_commit':result['source_commit'],'results_sha256':sha(folder/'results.json'),
        'fingerprint':pipeline['fingerprint'],'source_files':len(result['file_hashes']),
        'trials':len(rows),'state_bindings':state_bindings,'orders_verified':orders,
        'recorded_contracts':len(cases),'mutation_checks':4,'stages':gate.verified('c2'),
        'historical_files_verified':count,'initial_failed_check_preserved':True,
        'uncertainty_recomputed':recomputed}
print(json.dumps(report,indent=2,allow_nan=False))
