"""Development step 4: full-size cost of the registered job. Runs zd_run.seed_job and zd_run.evaluate through tcd_common.harness at FULL size on 8 seeds with 8 workers
(one wave) on its OWN fresh entropy (cost_spec.json), not a registered run: no git guard, no verdict is used. The wall time of one wave, times ceil(S/8), sets the caps.

    .venv/bin/python evidence/tactical_composition_demo/dev_0d/dev_cost.py
"""
import json
import secrets
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import zd_run as R  # noqa: E402
from tcd_common import harness  # noqa: E402
from tcd_common.fileio import write_json  # noqa: E402


def main():
    spec_path = HERE/'cost_spec.json'
    if not spec_path.exists():
        cfg = R.build_config()
        cfg.update({'seeds': 8, 'workers': 8, 'soft_cap': 3000.0, 'hard_cap': 3300.0, 'eval_cap': 300.0, 'boot_entropy': secrets.randbits(96)})
        write_json(spec_path, {'note': 'cost measurement spec: full-size config on fresh development entropy; NOT the registered SPEC_0D.json', 'entropy': 0,
                               'smoke_entropy': secrets.randbits(96), 'config': cfg, 'smoke_overrides': {}})
    code, summary = harness.run_experiment(spec_path=spec_path, here=HERE, root=HERE.parents[2], files=(), run_dirs=('cost_run',), run_name='cost_run',
                                           seed_job=R.seed_job, evaluate=R.evaluate, smoke=True)
    return code


if __name__ == '__main__':
    sys.exit(main())
