"""Fresh development probes with reviewer-owned matrix and finite differences."""
from dataclasses import replace
import json
from pathlib import Path
import sys

import numpy as np

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from geomind.c2_network import ConductanceNetwork,Settings,digest

HASH=digest({'review_fixture':'disjoint development seeds 991000xx; never final panel'})
edges=tuple((a,b) for a in range(16) for b in range(a+1,16)
            if b-a==4 or (b-a==1 and a//4==b//4))

def solve(g,x,beta=0.,target=0.):
    # Incidence-matrix Laplacian, independently assembled from kernel loops.
    incidence=np.zeros((24,16))
    for k,(a,b) in enumerate(edges): incidence[k,a]=1.; incidence[k,b]=-1.
    matrix=incidence.T @ np.diag(g) @ incidence + .01*np.eye(16)
    matrix[10,10]+=beta
    unknown=[i for i in range(16) if i not in (0,3)]
    rhs=-matrix[np.ix_(unknown,[0,3])] @ x
    rhs[unknown.index(10)]+=beta*target
    activity=np.zeros(16); activity[[0,3]]=x
    activity[unknown]=np.linalg.solve(matrix[np.ix_(unknown,unknown)],rhs)
    return activity

maximum_equilibrium_error=maximum_update_error=0.
cases=[]
for seed in range(99100000,99100008):
    rng=np.random.default_rng(seed); g=rng.uniform(.2,3.,24); x=rng.uniform(0,1,2); target=float(rng.uniform(0,1))
    state=ConductanceNetwork(g,HASH); answer=state.query(x)
    expected=solve(g,x)
    assert answer['status']=='OK'
    error=float(np.max(np.abs(np.array(answer['activity'])-expected)))
    maximum_equilibrium_error=max(maximum_equilibrium_error,error)
    assert error<1e-7
    assert answer['cost']['phases']==1 and answer['cost']['bound_edges']==24
    assert answer['cost']['force_edges']==24*(answer['cost']['sweeps']+1)
    before=state.export(); trace=state.learn(x,target)
    assert trace['status']=='PASS' and trace['cost']['bound_edges']==48
    free=solve(g,x); nudged=solve(g,x,.05,target)
    proposed=np.array([g[k]+.01/(2*.05)*((free[a]-free[b])**2-(nudged[a]-nudged[b])**2) for k,(a,b) in enumerate(edges)])
    error=float(np.max(np.abs(state.conductances-np.clip(proposed,.05,5))))
    maximum_update_error=max(maximum_update_error,error)
    assert error<1e-8
    # Exact one-sweep synchronous state, with reviewer-owned matrix-force path.
    one=ConductanceNetwork(g,HASH,replace(Settings(),max_sweeps=1))
    trace=one.learn(x,target)
    old=np.zeros(16); old[[0,3]]=x
    degrees=np.zeros(16); matrix=.01*np.eye(16)
    for value,(a,b) in zip(g,edges):
        degrees[a]+=value; degrees[b]+=value
        matrix[a,a]+=value; matrix[b,b]+=value; matrix[a,b]-=value; matrix[b,a]-=value
    force=matrix@old; force[[0,3]]=0
    expected=old-.25/(2*degrees.max()+.01)*force
    assert np.allclose(trace['free'],expected,rtol=0,atol=2e-16)
    assert trace['status']=='NOT_CONVERGED'
    # Small-beta local direction compared directly to finite differences.
    small=ConductanceNetwork(g,HASH,replace(Settings(),beta=.0001,tolerance=1e-12))
    assert small.learn(x,target)['status']=='PASS'
    fd=[]
    for k in range(24):
        plus=g.copy(); minus=g.copy(); plus[k]+=1e-5; minus[k]-=1e-5
        lp=.5*(solve(plus,x)[10]-target)**2; lm=.5*(solve(minus,x)[10]-target)**2
        fd.append((lp-lm)/2e-5)
    direction=(g-small.conductances)/.01; fd=np.array(fd)
    cosine=float(direction@fd/(np.linalg.norm(direction)*np.linalg.norm(fd)))
    assert cosine>.999
    disabled=ConductanceNetwork(g,HASH)
    assert disabled.learn(x,target,feedback=False)['status']=='PASS'
    assert disabled.export()==before
    frozen=ConductanceNetwork.load(state.export()); snapshot=frozen.export()
    assert frozen.query(x)['output']==state.query(x)['output'] and frozen.export()==snapshot
    cases.append({'seed':seed,'equilibrium_error':float(np.max(np.abs(np.asarray(answer['activity'])-solve(g,x)))),'gradient_cosine':cosine})

refusals=[]
# Force free-phase nonconvergence and nudged-only nonconvergence separately.
for name,x,y in [('free_nonconvergence',(.2,.8),.5),('nudged_nonconvergence',(0.,0.),1.)]:
    state=ConductanceNetwork([.7,1.3],HASH,replace(Settings(),max_sweeps=1),edges=((0,1),(1,2)),nodes=3,inputs=(0,2),output=1)
    before=state.export(); trace=state.learn(x,y)
    assert trace['status']=='NOT_CONVERGED' and state.export()==before
    assert trace['cost']['refused']==1
    assert trace['cost']['phases']==(1 if name=='free_nonconvergence' else 2)
    refusals.append({'case':name,'status':trace['status'],'phases':trace['cost']['phases']})
# Both phases converge; overflow in proposal computation must still refuse atomically.
state=ConductanceNetwork([.7,1.3],HASH,replace(Settings(),beta=5e-324),edges=((0,1),(1,2)),nodes=3,inputs=(0,2),output=1)
before=state.export(); trace=state.learn((0.,0.),0.)
assert trace['status']=='INVALID_STATE' and state.export()==before
assert trace['cost']['phases']==2 and trace['cost']['refused']==1 and trace['cost']['committed']==0
refusals.append({'case':'nonfinite_proposal','status':trace['status'],'phases':2})
state=ConductanceNetwork(np.ones(24),HASH)
for x,y in [((float('nan'),.2),.3),((.2,.8),float('inf')),((True,.8),.3),((.2,.8),True),((1e308,-1e308),.3)]:
    before=state.export(); trace=state.learn(x,y)
    assert trace['status']!='PASS' and state.export()==before
    refusals.append({'case':'invalid_or_extreme_input','status':trace['status']})
print(json.dumps({'status':'PASS','grid_cases':cases,'maximum_equilibrium_error':maximum_equilibrium_error,
                  'maximum_update_error':maximum_update_error,'atomic_refusals':refusals},indent=2,allow_nan=False))
