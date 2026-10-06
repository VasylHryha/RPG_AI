"""Tiny static synthetic B-path timing only; no world, fixture or panel."""
import argparse
from copy import deepcopy
import json
from pathlib import Path
import statistics
import time
import numpy as np
from ..medium.rev6_design import Rev6Medium
from ..medium.medium import Drive


def exhausted_state(n=48):
    if n<26:raise ValueError('synthetic configuration needs 26 elements')
    m=Rev6Medium(growth_rng=np.random.default_rng(8642))
    m.add((-2.9,0),0,gain=1.)
    m.add((0,0),0,gain=0.)
    for j in range(7):m.add((1+.0001*j,2.72+.0001*j),0,gain=0.)
    for j in range(9):m.add((1+.001*j,2.85+.001*j),0,gain=0.)
    for j in range(8):m.add((3.1+.001*j,0),0,gain=0.,role='output' if j==0 else 'element')
    while len(m.native)<n:m.add((100+10*len(m.native),100),0,gain=0.)
    m.drives=[Drive(0,-4,0,0,np.pi,2,1,3)]
    m.frames.clear();m.record()
    # Populate a 601-frame ledger without integration; timing cannot copy it.
    frame=m.frames[-1]
    for _ in range(600):m.frames.append(deepcopy(frame))
    return m


def measure(repeats=3):
    rows=[]
    for n in (26,48,64):
        samples=[]
        for _ in range(repeats):
            m=exhausted_state(n)
            try:
                before=m.native.save();rng=deepcopy(m.growth_rng.bit_generator.state)
                started=time.perf_counter();births=m.b_path();elapsed=time.perf_counter()-started
                terminal=[e['values'] for e in m.events if e['rule']=='birth_terminal'][-1]
                if births or terminal['outcome']!='exhausted' or terminal['attempts']!=104:
                    raise ValueError(f'synthetic timing configuration not exhausted: {terminal}')
                if before!=m.native.save() or rng!=m.growth_rng.bit_generator.state:raise ValueError('rejected trial mutated native state or RNG')
                samples.append(elapsed)
            finally:m.close()
        rows.append(dict(elements=n,frames=601,site_requests=1,candidate_attempts=104,
            samples_seconds=samples,median_seconds=statistics.median(samples),maximum_seconds=max(samples),
            per_candidate_median_seconds=statistics.median(samples)/104,
            eight_exhausted_sites_proxy_seconds=8*max(samples)))
    return dict(status='SYNTHETIC_TIMING_ONLY',world_steps=0,fixtures='NOT_RUN',panels='NOT_RUN',
        configuration='one exhausted B-path site, eight pairs x thirteen directions, 601 synthetic frames',
        repeats=repeats,rows=rows,assisted_by='Codex:GPT-6')


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True)
    args=p.parse_args();args.output.write_text(json.dumps(measure(),indent=2,allow_nan=False)+'\n')

if __name__=='__main__':main()
