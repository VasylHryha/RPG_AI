"""Bind historical R004 and reviewed R005 to their archived source sets."""
import hashlib, json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sha = lambda b: hashlib.sha256(b).hexdigest()
out = {}
for revision in ('r004', 'r005'):
    folder = ROOT / 'evidence' / ('c1_' + revision)
    receipt = json.loads((folder / 'results.json').read_text())
    hashes = receipt['file_hashes']
    fingerprint = sha(json.dumps(hashes, sort_keys=True, separators=(',', ':')).encode())
    out[revision] = {
        'experiment_id': receipt['experiment_id'],
        'results_sha256': sha((folder / 'results.json').read_bytes()),
        'source_set_fingerprint': fingerprint,
        'fingerprint_definition': 'SHA256 of compact sorted JSON of receipt file_hashes',
        'archived_source_mismatch': [name for name, expected in hashes.items() if sha((folder / 'source' / name).read_bytes()) != expected],
        'candidate_sha256': hashes['geomind/incremental.py'],
        'manifest_hash': receipt['manifest_hash'],
    }
Path(__file__).with_suffix('.out.json').write_text(json.dumps(out, indent=2) + '\n')
print(json.dumps(out, indent=2))
