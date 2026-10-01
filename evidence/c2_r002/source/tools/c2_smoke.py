"""Non-panel 100-update smoke; no final worlds or rehearsal of the panel."""
import json
from pathlib import Path
import sys
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from geomind.c2_network import ConductanceNetwork, digest
from geomind.c2_reference import equilibrium
from tools import gate


def main():
    reasons=gate.check('smoke',milestone='c2')
    if reasons: raise SystemExit('C2 smoke gate blocked: '+' '.join(reasons))
    rng=np.random.default_rng(890002); state=ConductanceNetwork(rng.uniform(.5,1.5,24),digest({'fixture':'non-panel C2 smoke'}))
    statuses=[]
    for x in rng.uniform(0,1,(100,2)): statuses.append(state.learn(x,.2*x[0]+.5*x[1])['status'])
    answers=[state.query(x) for x in ((.1,.9),(.9,.1))]
    error=max(abs(a['output']-equilibrium(state.conductances,state.edges,16,(0,3),x,10)[10]) for a,x in zip(answers,((.1,.9),(.9,.1))))
    if statuses!=['PASS']*100 or any(a['status']!='OK' for a in answers) or error>1e-7: raise RuntimeError('Smoke failed')
    path=Path(sys.argv[1])
    if path.exists(): raise FileExistsError('Smoke receipt already exists')
    path.write_text(json.dumps({'updates':100,'statuses':statuses,'max_equilibrium_error':error,'check_status':'PASS'})+'\n')


if __name__=='__main__': main()
