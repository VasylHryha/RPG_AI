"""Pin scientific inputs once, before any revision-7 result exists."""
import hashlib
import json
from pathlib import Path
import subprocess
from .rev7_config import CONFIG_SHA256,CONFIG
from .protocol import canonical
from .rev7_inventory import check_disjoint
HERE=Path(__file__).parent
ROOT=HERE.parents[3]
PIN=HERE/'REV7_SOURCE_IDENTITY.json'


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def create_pin():
    base=HERE.parent
    paths=list(base.glob('medium/rev7_*.*'))+list(base.glob('medium/build_rev7.py'))+list(base.glob('runner/rev7_*.py'))
    paths+=[HERE/'test_rev7.py',base/'medium/_rev7_build/build.json',base/'medium/_rev7_build/rev7_medium.dylib' if (base/'medium/_rev7_build/rev7_medium.dylib').exists() else base/'medium/_rev7_build/rev7_medium.so',HERE/'REV7_SEED_INVENTORY.json',HERE/'development_20261006/CALIBRATION.json']
    # Bind all inherited read-only runtime dependencies, including frozen criteria,
    # world images and their manifests, from the already pinned rev6 integration.
    inherited=json.loads((HERE/'REV65_SOURCE_IDENTITY.json').read_text())['sha256']
    paths+=[ROOT/p for p in inherited]
    paths+=[base.parent/n for n in ('DESIGN_0H_REV7.md','DESIGN_0H_REV6.md','DESIGN_0H.md')]
    paths+=[ROOT/'docs/reviews/tactical_0h_rev711_design_review_codex_r2.md']
    pin=dict(configuration_sha256=CONFIG_SHA256,configuration=CONFIG,sha256={str(p.relative_to(ROOT)):digest(p) for p in sorted(set(paths))})
    PIN.write_bytes(canonical(pin)+b'\n');return pin


def assert_inputs(pin_path=PIN):
    pin_path=Path(pin_path);pin=json.loads(pin_path.read_text())
    if pin['configuration_sha256']!=CONFIG_SHA256 or pin['configuration']!=CONFIG:raise ValueError('INVALID: configuration mismatch')
    for name,expected in pin['sha256'].items():
        path=ROOT/name
        if not path.is_file() or digest(path)!=expected:raise ValueError(f'INVALID: scientific identity mismatch: {name}')
    for name in ('DESIGN_0H_REV7.md','DESIGN_0H_REV6.md','DESIGN_0H.md'):
        rel='evidence/tactical_composition_demo/'+name
        result=subprocess.run(['git','show',f'HEAD:{rel}'],cwd=ROOT,capture_output=True)
        if result.returncode or hashlib.sha256(result.stdout).hexdigest()!=pin['sha256'][rel]:raise ValueError('INVALID: final committed design identity mismatch')
    inventory=json.loads((HERE/'REV7_SEED_INVENTORY.json').read_text());check_disjoint(inventory)
    return dict(checked='execution_start_once',sha256=pin['sha256'],configuration_sha256=CONFIG_SHA256,pin_sha256=digest(pin_path),inventory=inventory)

if __name__=='__main__':print(json.dumps(dict(files=len(create_pin()['sha256'])),indent=2))
