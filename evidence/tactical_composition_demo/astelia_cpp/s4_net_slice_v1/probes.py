"""Matched recorded-context kicks only; no engine execution or task claims."""
import torch
from dynamics import graph,phase_step,movement


def matched_kicks(theta,pos,ids,law,forcing,speeds,geometry_kick,phase_kick,dt=1/30,ablations=('intact','K0','topology_only','no_geometry_to_mode','no_mode_to_geometry')):
    """Same context, weights, held forcing, ID topology and dt across interventions.
    Returns baseline/geometry/phase contexts for phase increments and command drift.
    Tests the explicit distance-coupling and phase-motion channels; geometry-derived
    forcing is held to isolate them. Launch reset is not exercised by these kicks.
    """
    if geometry_kick.shape!=pos.shape or phase_kick.shape!=theta.shape:raise ValueError('kick shape')
    fixed=graph(pos,ids);A,B,J,K,omega,share=law
    rows={}
    for ab in ablations:
        contexts={}
        for name,p,t in (('baseline',pos,theta),('geometry',pos+geometry_kick,theta),('phase',pos,theta+phase_kick)):
            phase=phase_step(t,p,ids,omega.expand_as(theta),K,forcing,dt,ab,fixed)
            drift=movement(phase,p,ids,A,B,J,share,speeds,ab)
            contexts[name]={'phase_increment':(phase-t).detach().tolist(),'motion':drift.detach().tolist()}
        rows[ab]=contexts
    return {'scope':'recorded context explicit channels; no launch/forcing/task closure claim','ablations':rows}
