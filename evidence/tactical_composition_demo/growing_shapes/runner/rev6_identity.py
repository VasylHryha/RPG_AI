"""Read-only guards for the approved inputs and reused calibration."""
import hashlib
import json
from pathlib import Path

HERE=Path(__file__).parent
ROOT=HERE.parents[3]
DESIGN_SHA256='2abda7e2409920fee3ad71779f224e75cce272c547ad2c4c87cfc87fb91b408b'
BASE_SHA256='39a630c3f4d440a6634538121773253443dcb15e8166406f36cde3727c119925'


def assert_inputs():
    for name,digest in [('DESIGN_0H_REV6.md',DESIGN_SHA256),('DESIGN_0H.md',BASE_SHA256)]:
        if hashlib.sha256((HERE.parents[1]/name).read_bytes()).hexdigest()!=digest:raise ValueError(f'INVALID: source identity {name}')
    inventory=json.loads((HERE/'REV6_SEED_INVENTORY.json').read_text())
    for name,digest in inventory['source_sha256'].items():
        if hashlib.sha256((ROOT/name).read_bytes()).hexdigest()!=digest:raise ValueError(f'INVALID: registered source {name}')
