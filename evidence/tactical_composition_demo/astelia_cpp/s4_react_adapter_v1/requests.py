"""Pure request constructors for the sealed lab v2 format. No ledger/run edits."""
import importlib.util
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
# v2 imports a module named build. Resolve that dependency explicitly to v1,
# avoiding collision with this directory's own build.py.
spec = importlib.util.spec_from_file_location('build', HERE.parent/'s4_shape_lab_v1/build.py')
parent_build = importlib.util.module_from_spec(spec)
old_build = sys.modules.get('build')
sys.modules['build'] = parent_build
spec.loader.exec_module(parent_build)
spec = importlib.util.spec_from_file_location('react_parent_lab_v2', HERE.parent/'s4_shape_lab_v2/lab.py')
lab = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lab)
if old_build is None:
    sys.modules.pop('build', None)
else:
    sys.modules['build'] = old_build

ARMS = ('v7+react', 'forcedP16+react')
BINARY = HERE/'build/tactics_react_host'

def base_arm(arm):
    if arm not in ARMS:
        raise ValueError('unknown react arm: '+arm)
    return arm.removesuffix('+react')

def adapt(req, arm, shadow=False):
    base_arm(arm)
    req['options']['ai'][0]['controller'] = arm
    req['labReact'] = {'shadow': bool(shadow)}
    return req

def request(arm, enemy, seed, orientation=0, sides=None, abilities_off=False, shadow=False):
    return adapt(lab.request(base_arm(arm), enemy, seed, orientation, sides, abilities_off), arm, shadow)

def drill_request(drill, arm, opponent, seed, orientation, pool, shadow=False):
    return adapt(lab.drill_request(drill, base_arm(arm), opponent, seed, orientation, pool), arm, shadow)

def series_request(arm, tactic, pool, seed, survivors=None, orientation=0, shadow=False):
    sides = lab.standard(seed, orientation)
    if survivors is not None:
        sides[0] = lab.placement(seed, survivors, orientation=orientation)
    return request(arm, lab.doctrine(tactic,pool), seed, orientation, sides, True, shadow)
