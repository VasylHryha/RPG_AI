"""Native strict-boundary arithmetic without changing pinned ancestors/globals.

CPython3.11's compensated hypot can differ by one ulp from libSystem/std::hypot.
At exact range/border thresholds this changes a boolean, not a small numeric
error. Private function namespaces reuse the pinned schema/join code with the
native libm hypot symbol. No epsilon, observation rewrite or global monkeypatch.
"""
import ctypes
import math
import platform
import sys
import types
import schema as _schema
import labels as _labels
import dynamics as _dynamics
import probes as _probes

_hypot=ctypes.CDLL(None).hypot
_hypot.argtypes=(ctypes.c_double,ctypes.c_double)
_hypot.restype=ctypes.c_double
native_hypot=_hypot
math_native=types.SimpleNamespace(**{name:(native_hypot if name=='hypot' else getattr(math,name)) for name in dir(math) if not name.startswith('_')})


def _clone(function,namespace):
    return types.FunctionType(function.__code__,namespace,function.__name__,function.__defaults__,function.__closure__)


_schema_globals={**vars(_schema),'math':math_native}
for _name in ('check','mirror_vector','inverse_point','slots','encode','candidates','decode','opportunities'):
    _schema_globals[_name]=_clone(getattr(_schema,_name),_schema_globals)
globals().update({_name:_schema_globals[_name] for _name in ('check','slots','encode','candidates','decode','opportunities')})
_label_globals={**vars(_labels),'math':math_native,**{name:_schema_globals[name] for name in ('check','slots','opportunities')}}
join=_clone(_labels.join,_label_globals)
add_drift=_clone(_dynamics.add_drift,{**vars(_dynamics),'math':math_native})


def graph(pos,ids,radius=3.):
    if len(ids)!=len(set(ids)) or len(ids)!=len(pos):
        raise ValueError('joint identity')
    points=pos.detach().tolist()
    return [[j for distance,_,j in sorted((native_hypot(points[j][0]-points[i][0],points[j][1]-points[i][1])/100,ids[j],j)
                 for j in range(len(ids)) if j!=i)[:8] if distance<radius] for i in range(len(ids))]


_dynamics_globals={**vars(_dynamics),'graph':graph,'math':math_native}
movement=_clone(_dynamics.movement,_dynamics_globals)
_dynamics_globals['movement']=movement
baseline_drift=_clone(_dynamics.baseline_drift,_dynamics_globals)
phase_step=_clone(_dynamics.phase_step,_dynamics_globals)
matched_kicks=_clone(_probes.matched_kicks,{**vars(_probes),'graph':graph,'phase_step':phase_step,'movement':movement})


def identity():
    dx=900-580.8211916071846; dy=360-382.9104402607728
    return dict(platform=sys.platform,architecture=platform.machine(),python=sys.version.split()[0],
                symbol='process native libm hypot, same symbol as C++ std::hypot',strict_comparisons=True,
                boundary_control=dict(python_hypot=math.hypot(dx,dy),native_hypot=native_hypot(dx,dy)))
