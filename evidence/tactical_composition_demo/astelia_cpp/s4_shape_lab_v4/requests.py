"""New lightweight requests; shared seed/placement/tactic draw per comparison."""
import importlib.util
import pathlib
import sys

CPP = pathlib.Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location('v4_react_requests', CPP/'s4_react_adapter_v1/requests.py')
adapter = importlib.util.module_from_spec(spec)
saved_path = list(sys.path)
spec.loader.exec_module(adapter)
sys.path[:] = saved_path
base = adapter.lab
ARMS = ('forcedP16', 'forcedP16+react')
ROLES = base.ROLES
cohort = base.cohort


def lean(req):
    req.update(trace=False, debug=False, killerTelemetry=True, decisionTrace=False,
               diagnostics=False, decisionDiagnostics=False, attributionDiagnostics=False, s3=True)
    return req


def drill_request(group, arm, tactic, seed, orientation, pool):
    if arm not in ARMS:
        raise ValueError('unknown v4 arm')
    fn = adapter.drill_request if arm.endswith('+react') else base.drill_request
    return lean(fn(group, arm, tactic, seed, orientation, pool))


def series_request(arm, draw, pool, survivors):
    if arm not in ARMS:
        raise ValueError('unknown v4 arm')
    if arm.endswith('+react'):
        req = adapter.series_request(arm,draw['tactic'],pool,draw['seed'],survivors,
                                     orientation=draw['orientation'])
    else:
        sides = base.standard(draw['seed'],draw['orientation'])
        sides[0] = base.placement(draw['seed'],survivors,orientation=draw['orientation'])
        req = base.request(arm,base.doctrine(draw['tactic'],pool),draw['seed'],
                           draw['orientation'],sides,True)
    return lean(req)
