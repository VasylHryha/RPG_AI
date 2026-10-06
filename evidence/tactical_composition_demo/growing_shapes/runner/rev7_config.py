"""Frozen revision-7.4 configuration identity and numerical recipes; no execution."""
import math
from .protocol import canonical
import hashlib

PHASE_SCALE=32.
PRODUCTION_H=.005
REFINEMENT_H=.00125
WORLD_DT=.1
F1D_SCALES=(1.,8.,32.)

PIN_TABLE={'live':[0.,0.],'F1a':[2.644,0.],'F1b':[1.532,0.],'F1c':[0.,0.],
           'F1d':[1.532,0.],'F2b':[-3.,0.],'F3':[4.,0.],'F4':[3.444,0.],'F5ii':[-.5,0.],
           'copies':'stored coordinate'}
N1_RECIPES={
 'N1a':dict(sites=[[4.,0.,4.,0.]],members=[[3.2,0.,0.,math.pi,2.,'element']],entry=True,step=True),
 'N1b':dict(sites=[[4.,0.,2.,0.]],members=[[3.2,0.,0.,1.5*math.pi,1.,'element']],entry=False,step=False),
 'N1c':dict(sites=[[4.,0.,2.,0.],[2.828,2.828,2.,math.pi]],members=[[3.,1.3,0.,math.pi,1.,'element']],entry=False,step=False),
 'N1d':dict(sites=[[4.,0.,2.,0.]],members=[[3.7,0.,math.pi,math.pi,1.,'element'],[3.956,0.,0.,math.pi,1.,'element']],entry=False,step=False),
 'N1e':dict(sites=[[4.,0.,2.,0.]],members=[[3.2,0.,0.,math.pi,1.,'element'],[2.644,0.,0.,math.pi,0.,'element'],[2.088,0.,0.,math.pi,0.,'element'],[1.532,0.,0.,math.pi,1.,'output']],entry=True,step=True),
}
N1_RECIPES['N1f']=dict(sites=[[4.,0.,2.,0.]],members=[[3.2-.556*j,0.,0.,math.pi,1. if j==0 else 0.,'element'] for j in range(6)]+[[0.,0.,0.,math.pi,1.,'output']],entry=True,step=True)
for name,recipe in N1_RECIPES.items():
    recipe['seconds']=24. if name=='N1f' else 16.
    recipe['entry_member']=len(recipe['members'])-1 if name in ('N1e','N1f') else 0

CONFIG=dict(revision='7.4',versions=['rev7_rhs_v1','rev7_eval_v1','rev7_template_v1','rev7_qual_v1'],phase_scale=PHASE_SCALE,
 carrier=math.pi,motion=dict(k=8,radius=3.,strict=True,ties=['distance','element_before_site','id'],mean='own_count',held='four RK4 stages',site_presence='strength > 0',site_weight='unweighted',silent_element_motion=True),
 phase=dict(k=8,radius=3.,strict=True,ties=['distance','element_array_index'],mean='own_count',sites=False),
 pins=PIN_TABLE,site_body_r0=.3,element_clearance=.05,site_clearance=.3,clearance_comparison='distance + 8*max_coordinate_or_limit_ULP >= threshold; roundoff only',
 timers=dict(inactive_B1='freeze',active_covered='reset',birth='reset',refusal='retain',ready_check='active only',B_path='immediate'),
 start=dict(policies=['intact','M','U'],elements=0,time=0.,timers=0.,id_counter=0,first_growth=20.,initial_detuning=False),
 excursion=dict(h=PRODUCTION_H,substeps=20,bound='sum h * max_stage abs(theta_dot - pi)',individual_cut=math.pi/2,pair_cut=math.pi/2,policy='pair-only; invalid means inactive; records retained',qualification='screen actual cohort before circular criteria',limitation='stage-sampling assumption'),
 recovery=dict(position_rms_factor=.1,phase_rms=.3,redraws=8,position_denominator='candidate free members',clipping=False,sites_excluded=True,output_included=True),
 clocks=dict(estimator=10.,qualification=60.,adaptation=.05,freq_cut=.005,pattern_cut=.1),
 N1=dict(recipes=N1_RECIPES,h=[PRODUCTION_H,REFINEMENT_H],substeps=[20,80],phase_scale=PHASE_SCALE,world_dt=WORLD_DT,wrapped_phase=.01,unwrapped_phase=.01,free_position=.01,entry=.1,Nx_match=.99,Ntheta_match=.99,pins='exact',minimum_distances='both integrations'),
 F1=dict(F1d=dict(scaffold='F1b',phase_scales=list(F1D_SCALES),h=PRODUCTION_H,verdict_cut=None),F1c=dict(margin_time=12.,margin_seconds=4.,margin_verdict_cut=None,deadline_seconds=8.,hold_until=24.,persistence_until=160.)),
 comparator=dict(task='perceive',recipients=[10000512,10000639],scope='fresh final whole medium copy per episode',effect='total effect of removing site bodies, including neighbour selection and normalization',verdict_cut=None,count_changes=True))
CONFIG_SHA256=hashlib.sha256(canonical(CONFIG)).hexdigest()
