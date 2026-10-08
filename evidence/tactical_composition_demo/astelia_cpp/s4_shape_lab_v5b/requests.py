"""Timing-only arms. Paired world draws and unchanged P16/REACT parameters."""
import importlib.util
import pathlib
import sys
CPP=pathlib.Path(__file__).resolve().parent.parent
spec=importlib.util.spec_from_file_location('v5_adapter_requests',CPP/'s4_react_adapter_v1/requests.py')
adapter=importlib.util.module_from_spec(spec);saved=list(sys.path);spec.loader.exec_module(adapter);sys.path[:]=saved
base=adapter.lab
ARMS=('forcedP16+react','forcedP16+react+central_sync','forcedP16+react+battery_oscillator')
GRID=tuple((k,r) for k in (.5,1,2) for r in (200,400,-1))
ROLES=base.ROLES
cohort=base.cohort

def adapt(req,arm,knobs=(1,400)):
    if arm not in ARMS:raise ValueError('unknown v5 arm')
    if tuple(knobs) not in GRID:raise ValueError('undeclared grid')
    mode=('base','central_sync','battery_oscillator')[ARMS.index(arm)]
    req['labBattery']=dict(mode=mode,k=knobs[0],radius=knobs[1])
    req.update(trace=False,debug=False,killerTelemetry=True,decisionTrace=False,diagnostics=False,decisionDiagnostics=False,attributionDiagnostics=False,s3=True)
    return req

def drill_request(group,arm,tactic,seed,orientation,pool,knobs=(1,400)):
    if group=='V1D2':
        # Dummy targets use the unchanged admitted REACT controller's dummy params:
        # replaced by a v5 dodging dummy in dispatch, never a planner.
        req=adapter.drill_request('D1',ARMS[0],None,seed,orientation,pool)
        req['options']['ai'][1]['controller']='dummy_advance_fire'
        req['options']['ai'][1]['params']={}
        req['labScenario']['sides'][1]=[u for u in req['labScenario']['sides'][1] if u['role']=='ranged']
        req['labAbilities']='off'
    else:req=adapter.drill_request(group,ARMS[0],tactic,seed,orientation,pool)
    if group in ('D1','V1D2'):req['labAbilities']='off'
    return adapt(req,arm,knobs)

def series_request(arm,draw,pool,survivors,knobs=(1,400)):
    return adapt(adapter.series_request(ARMS[0],draw['tactic'],pool,draw['seed'],survivors,orientation=draw['orientation']),arm,knobs)
