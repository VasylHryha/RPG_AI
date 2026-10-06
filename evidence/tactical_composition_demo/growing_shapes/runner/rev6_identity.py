"""Section 19.7: verify scientific identities once at execution start."""
import hashlib
import json
from pathlib import Path

HERE=Path(__file__).parent
ROOT=HERE.parents[3]
DESIGN_SHA256='ca9c43362e3eebace889c7306784ffe5dd3095a58eb2095473f745eff31b52c5'


def assert_inputs():
    pin=json.loads((HERE/'REV65_SOURCE_IDENTITY.json').read_text())
    hashes=pin['sha256']
    design='evidence/tactical_composition_demo/DESIGN_0H_REV6.md'
    if hashes.get(design)!=DESIGN_SHA256:raise ValueError('INVALID: design registration mismatch')
    for name,digest in hashes.items():
        path=ROOT/name
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest()!=digest:
            raise ValueError(f'INVALID: scientific input identity {name}')
    return dict(scope='committed rev6 and base designs, calibration, executed inherited inputs, rev6 sources, native images, seed inventory',
                checked='execution_start_once',sha256=dict(hashes),
                identity_record_sha256=hashlib.sha256((HERE/'REV65_SOURCE_IDENTITY.json').read_bytes()).hexdigest())
