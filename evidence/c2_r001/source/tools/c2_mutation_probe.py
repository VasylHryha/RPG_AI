"""Four focused numerical defects, checked without training a panel.

Build mutant kernels in temporary directories; never alter the live kernel/build.
These checks cover synchronous ordering, update sign/factor and geometry freeze.
"""
import ctypes
import json
from pathlib import Path
import subprocess
import tempfile
import time
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from geomind.c2_network import ConductanceNetwork, Cost, GRID_EDGES, Settings, digest
from geomind.c2_reference import direct_local_update, equilibrium
from tools import gate
import numpy as np

MUTANTS={
    'update_sign':('g[e]+eta/(2.0*beta)*(df*df-dn*dn)','g[e]-eta/(2.0*beta)*(df*df-dn*dn)'),
    'update_factor':('eta/(2.0*beta)','eta/beta'),
    'geometry_changes_between_phases':('std::copy(free_state,free_state+n,nudged_state);','std::copy(free_state,free_state+n,nudged_state);\n    g[0]+=0.01;'),
    'synchronous_barrier_removed':('force[a[e]]+=current; force[b[e]]-=current;','force[a[e]]+=current; force[b[e]]-=current; u[a[e]]-=0.001*current;')}


def run(output):
    reasons=gate.check('mutation',milestone='c2')
    if reasons: raise RuntimeError('C2 mutation gate blocked: '+' '.join(reasons))
    start=time.perf_counter(); source=(ROOT/'native/c2/relaxation.cpp').read_text(); results={}
    g=np.random.default_rng(890001).uniform(.5,1.5,24); x=(.3,.9); y=.25
    expected=direct_local_update(g,GRID_EDGES,16,(0,3),x,10,y)
    baseline=ConductanceNetwork(g,digest({'fixture':'C2 mutations'})); trace=baseline.learn(x,y)
    if trace['status']!='PASS' or np.max(np.abs(baseline.conductances-expected))>1e-8:
        raise RuntimeError('Unmutated numerical control fails')
    with tempfile.TemporaryDirectory() as tmp:
        for name,(old,new) in MUTANTS.items():
            if source.count(old)!=1: raise ValueError('Stale C2 mutation definition '+name)
            cpp=Path(tmp)/(name+'.cpp'); binary=Path(tmp)/(name+'.dylib')
            cpp.write_text(source.replace(old,new))
            subprocess.run(['clang++','-std=c++17','-O3','-fno-fast-math','-ffp-contract=off','-dynamiclib',str(cpp),'-o',str(binary)],check=True)
            state=ConductanceNetwork(g,digest({'fixture':'C2 mutations'})); library=ctypes.CDLL(str(binary))
            library.c2_learn.argtypes=state._lib.c2_learn.argtypes; library.c2_learn.restype=ctypes.c_int
            library.c2_relax.argtypes=state._lib.c2_relax.argtypes; library.c2_relax.restype=ctypes.c_int
            state._lib=library
            trace=state.learn(x,y)
            error=float(np.max(np.abs(state.conductances-expected)))
            phases_correct=(trace['status']=='PASS' and np.max(np.abs(np.asarray(trace['free'])-equilibrium(g,GRID_EDGES,16,(0,3),x,10)))<=1e-7
                            and np.max(np.abs(np.asarray(trace['nudged'])-equilibrium(g,GRID_EDGES,16,(0,3),x,10,beta=.05,y=y)))<=1e-7)
            results[name]={'detected':not phases_correct or error>1e-8,'status':trace['status'],'geometry_error_max':error,'phases_correct':bool(phases_correct)}
    unexpected=[name for name,r in results.items() if not r['detected']]
    report={'total':len(results),'detected':len(results)-len(unexpected),'mutants':results,
            'unexpected_survivors':unexpected,'problems':[],'seconds':time.perf_counter()-start,'fingerprint':gate.fingerprint()}
    output=Path(output)
    if output.exists(): raise FileExistsError('Mutation evidence is never overwritten')
    output.parent.mkdir(parents=True,exist_ok=True); output.write_text(json.dumps(report,indent=2)+'\n')
    return report


if __name__=='__main__':
    r=run(sys.argv[1]); print(json.dumps(r)); raise SystemExit(bool(r['unexpected_survivors']))
