"""Registered numeric diagnostics (reference battery 1e-10, transform equivariance 1e-9) under the
option-B native engine of the scratch repo given as argv[1]. Diagnostic only; nothing registered."""
import json, os, sys, time
root = sys.argv[1]; out = sys.argv[2]
for v in ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'VECLIB_MAXIMUM_THREADS'): os.environ[v] = '1'
sys.path.insert(0, root); os.chdir(root)
from geomind import c6_option_b as O, c6_r4_field_protocol as P
from tools.c6_r4_design_gate import reference_battery, equivariance
s = P.load_settings(); t = time.perf_counter()
with O.backend('native'):
    rb = reference_battery(s); eq = equivariance(s); rec = O.verify_build()
res = dict(root=root, option_b_build=rec, seconds=time.perf_counter() - t,
           b_reference_equivalence=dict(passed=rb['passed'], tolerance=rb['tolerance'],
               fixtures=[{k: r[k] for k in r if k != 'initial_state'} for r in rb['fixtures']]),
           b_transform_equivariance=eq)
json.dump(res, open(out, 'w'), indent=1, default=float)
print(json.dumps(dict(ref=rb['passed'], max_ref=max(r['maximum_error'] for r in rb['fixtures']), eq=eq['passed'],
                      eq_err=[eq['scene_maximum_error'], eq['rename_maximum_error']], seconds=res['seconds'])))
