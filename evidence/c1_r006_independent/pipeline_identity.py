"""Read-only pipeline prerequisite and committed-source binding audit."""
import hashlib, json, subprocess, sys, xml.etree.ElementTree as ET
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
import gate
folder = ROOT / 'evidence/c1_r006'
pipeline = json.loads((folder / 'PIPELINE.json').read_text())
receipt = json.loads((folder / 'results.json').read_text())
source_commit = pipeline['stages'][0]['commit']
code = gate.fingerprint()
assert code == pipeline['fingerprint']
assert gate.verified() == ['preflight','tests','smoke','mutation','panel']
assert gate.tree_problems() == []
mismatches = []
for path in gate.source_files():
    name = str(path.relative_to(ROOT))
    archived = subprocess.run(['git', 'show', source_commit + ':' + name], cwd=ROOT, capture_output=True, check=True).stdout
    if hashlib.sha256(archived).hexdigest() != gate.sha256(path): mismatches.append(name)
assert not mismatches
stamp = json.loads((gate.STAMPS / (code + '.json')).read_text())
assert pipeline['stages'] == [{'stage': s, **stamp[s]} for s in ('preflight','tests','smoke','mutation','panel')]
for stage in pipeline['stages']:
    for name, expected in stage['artifacts'].items():
        assert gate.sha256(ROOT / name) == expected
tests = {}
for name in pipeline['stages'][1]['artifacts']:
    xml = ET.parse(ROOT / name).getroot()
    tests[name] = {'cases': len(list(xml.iter('testcase'))), 'failures': len(list(xml.iter('failure'))), 'errors': len(list(xml.iter('error'))), 'skips': len(list(xml.iter('skipped')))}
mutation = json.loads((folder / 'MUTATION.json').read_text())
assert gate.sha256(folder / 'MUTATION.json') == pipeline['stages'][3]['artifacts'][next(iter(pipeline['stages'][3]['artifacts']))]
previous = json.loads((ROOT / 'evidence/c1_r005/results.json').read_text())
assert set(r['seed'] for r in receipt['instances']).isdisjoint(r['seed'] for r in previous['instances'])
output = {'fingerprint': code, 'verified': gate.verified(), 'source_commit_resolved_from_pipeline': source_commit, 'receipt_source_commit': receipt['source_commit'], 'committed_source_mismatches': mismatches, 'tests': tests, 'mutation_total': mutation['total'], 'mutation_detected': mutation['detected'], 'mutation_problems': mutation['problems'], 'mutation_unexpected_survivors': mutation['unexpected_survivors'], 'panel_results_sha256': gate.sha256(folder / 'results.json'), 'checks': 'PASS'}
Path(__file__).with_suffix('.out.json').write_text(json.dumps(output, indent=2)+'\n')
print(json.dumps(output, indent=2))
