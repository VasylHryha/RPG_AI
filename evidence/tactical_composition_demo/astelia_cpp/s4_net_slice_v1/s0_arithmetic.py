"""Lightweight read-only native-libm schema/label arithmetic (no Torch import).

Same isolated function-global adapter as stage1_arithmetic, restricted to S0's
public encoding/join dependencies. Never alters imported module globals.
"""
import ctypes
import math as _math
import types
import schema as _schema
import labels as _labels

_hypot=ctypes.CDLL(None).hypot
_hypot.argtypes=(ctypes.c_double,ctypes.c_double)
_hypot.restype=ctypes.c_double
math=types.SimpleNamespace(**{k:(_hypot if k=='hypot' else getattr(_math,k)) for k in dir(_math) if not k.startswith('_')})
math.dist=lambda a,b:_hypot(a[0]-b[0],a[1]-b[1])

def clone(function,namespace):
    return types.FunctionType(function.__code__,namespace,function.__name__,function.__defaults__,function.__closure__)

namespace={**vars(_schema),'math':math}
for name in ('check','mirror_vector','inverse_point','slots','encode','candidates','decode','opportunities'):
    namespace[name]=clone(getattr(_schema,name),namespace)
globals().update({k:namespace[k] for k in ('check','slots','encode','candidates','decode','opportunities')})
join=clone(_labels.join,{**vars(_labels),'math':math,**{k:namespace[k] for k in ('check','slots','opportunities')}})
