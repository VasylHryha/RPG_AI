"""One paired batch, shared base, public scripted atoms; timing is batch-wide."""
import importlib.util
import pathlib
import sys
CPP=pathlib.Path(__file__).resolve().parent.parent
spec=importlib.util.spec_from_file_location('v6_adapter_requests',CPP/'s4_react_adapter_v1/requests.py')
adapter=importlib.util.module_from_spec(spec);saved=list(sys.path);spec.loader.exec_module(adapter);sys.path[:]=saved
base=adapter.lab
ARMS=('base','V2','E1','R1','E1+R1')
ROLES=base.ROLES
cohort=base.cohort

def comparison_arms(arm):
    if arm not in ARMS[1:]:raise ValueError('select a candidate arm')
    return ('base','E1','E1+R1') if arm=='E1+R1' else ('base',arm)

def groups(arm):return ('D1','V2D2') if arm=='V2' else ('D5',) if arm=='E1' else ('RD',)

def adapt(req,arm,timing):
    if arm not in ARMS:raise ValueError('unknown v6 arm')
    if timing['mode'] not in ('base','central_sync','battery_oscillator'):raise ValueError('unknown shared timing')
    req['labShapes']=dict(arm=arm)
    req['labBattery']=dict(timing)
    req.update(trace=False,debug=False,killerTelemetry=True,decisionTrace=False,diagnostics=False,decisionDiagnostics=False,attributionDiagnostics=False,s3=True)
    return req

def drill_request(group,arm,tactic,seed,orientation,pool,timing):
    if group=='V2D2':
        req=adapter.drill_request('D1','forcedP16+react',None,seed,orientation,pool)
        req['options']['ai'][1]['controller']='dummy_advance_fire'
        req['options']['ai'][1]['params']={}
        req['labScenario']['sides'][1]=[u for u in req['labScenario']['sides'][1] if u['role']=='ranged']
    elif group=='RD':
        # Active ranged with friends versus artillery-heavy/rushing doctrines.
        req=adapter.drill_request('D5','forcedP16+react',None,seed,orientation,pool)
        sides=base.standard(seed)
        ours=base.select(sides[0],{'melee':10,'ranged':30})
        theirs=base.select(sides[1],{'melee':10,'ranged':20,'artillery':10})
        for i,u in enumerate(ours):u['position']=dict(x=460 if u['role']=='melee' else 500,y=180+(i%20)*22)
        for i,u in enumerate(theirs):u['position']=dict(x=740 if u['role']=='artillery' else 750,y=180+(i%20)*22)
        if orientation:
            for u in ours+theirs:u['position']['x']=1400-u['position']['x']
        req['labScenario']['sides']=[ours,theirs]
        req['options']['ai'][1]=base.controller('regular') if tactic=='regular' else base.doctrine(tactic,pool)
    else:req=adapter.drill_request(group,'forcedP16+react',tactic,seed,orientation,pool)
    req['labAbilities']='off'
    return adapt(req,arm,timing)

def series_request(arm,draw,pool,survivors,timing):
    return adapt(adapter.series_request('forcedP16+react',draw['tactic'],pool,draw['seed'],survivors,orientation=draw['orientation']),arm,timing)
