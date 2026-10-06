"""Frozen revision-7.10 configuration identity and numerical recipes; no execution."""
from copy import deepcopy
import math
from .protocol import canonical
import hashlib

PHASE_SCALE=32.
PRODUCTION_H=.005
REFINEMENT_H=.00125
WORLD_DT=.1
STRONG_LINK_RATE=.5
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
N1_RECIPES['N1g']=deepcopy(N1_RECIPES['N1d'])
N1_RECIPES['N1d']['members'][0][2]=math.pi-.5
for name,recipe in N1_RECIPES.items():
    recipe['seconds']=24. if name=='N1f' else 16.
    recipe['entry_member']=len(recipe['members'])-1 if name in ('N1e','N1f') else 0
    recipe['used_in_verdict']=name!='N1g'

N1_SADDLE_DIAGNOSTIC=dict(member=0,departure_radians=.5,
 definition='first world endpoint with abs(unwrapped carrier-relative phase - initial phase) >= departure_radians',
 direction='sign of unwrapped displacement at first departure; not a completed 2pi winding',
 time='first 0.1 s endpoint crossing, bracketed by previous endpoint (initial t=0 included)',
 not_observed='null direction/time/bracket, status NOT_OBSERVED; horizon 16 s',used_in_verdict=False)

CONFIG=dict(revision='7.10',versions=['rev7_rhs_v1','rev7_eval_v1','rev7_template_v1','rev7_qual_v1'],phase_scale=PHASE_SCALE,
 B_path=dict(order='active sites without G_s path; current deficit ascending; ties (site-pointer) mod 8',
     snapshot='once at check start; recompute strong graph/front/back before each site trial',
     deficit='minimum Euclidean distance from site forward set to output backward set; empty sets infinity',
     pointer='advance by one modulo eight at every check, including empty/blocked',
     maximum_births_per_check=2,waiting='all eight sites; eligible/unserved/current/max checks, accepted births and outcomes',
     waiting_units='B-path checks; inactivity pauses, acceptance or observed active connection resets',
     service_guarantee=False,claim='budget-aware outcome-informed heuristic; no guaranteed fixture cure, minimum insertion cost or all-site coverage'),
 strong_links=dict(rate_min_per_second=STRONG_LINK_RATE,formula='lambda * K * exp(-r*r) / full held receiver phase-neighbor count',comparison='computed coefficient >= 0.5 /s; inclusive, no tolerance',selection='filter actual directed phase edges after full k-nearest selection',uses=['B-path site test','B-path front/back sets','B-path graph trial conditions','transmission path exposure E','effective-root-to-output paths'],full_graph_uses=['RHS and mean normalization','D4 liveness','qualification','budget'],root_eligibility='unchanged gain > 0, active strict site reach, ordinary unsilenced member',clock=dict(degree='actual full held receiver row; recomputed after trial insertion',K='live signed coupling K; weighted experiment K=1',tau_link_seconds=2.,status='provisional aligned single-edge scale; no end-to-end settling guarantee or serial bound'),placement='unchanged r_star=0.556; progress conditional on admissible trial, clearance and budget'),
 output_port=dict(death_exempt=['D1','D3','D4'],budget_elements='ordinary only',budget_pairs='actual Ntheta undirected ordinary-to-ordinary pairs; O incident pairs excluded',cap=64,budget=64.,pair_cost=.1,B_out_budget_exempt=True,B_out_placement_required=True,physical_count_includes_output=True),
 fixture_entropy=dict(F5='reused outcome-informed engineering fixture; not independent',F7='previously NOT_RUN; dependent on reused F5; chain not fresh',exception='section 13 supersedes fresh-entropy stop for these fixtures only',development='unchanged'),
 carrier=math.pi,motion=dict(k=8,radius=3.,strict=True,ties=['distance','element_before_site','id'],mean='own_count',held='four RK4 stages',site_presence='strength > 0',site_weight='unweighted',silent_element_motion=True),
 phase=dict(k=8,radius=3.,strict=True,ties=['distance','element_array_index'],mean='own_count',sites=False),
 pins=PIN_TABLE,site_body_r0=.3,element_clearance=.05,site_clearance=.3,clearance_comparison='distance + 8*max_coordinate_or_limit_ULP >= threshold; roundoff only',
 timers=dict(inactive_B1='freeze',active_covered='reset',birth='reset',refusal='retain',ready_check='active only',B_path='immediate'),
 start=dict(policies=['intact','M','U'],elements=0,time=0.,timers=0.,id_counter=0,first_growth=20.,initial_detuning=False),
 excursion=dict(h=PRODUCTION_H,substeps=20,bound='sum h * max_stage abs(theta_dot - pi)',individual_cut=math.pi/2,pair_cut=math.pi/2,policy='pair-only; invalid means inactive; records retained',qualification='screen actual cohort before circular criteria',limitation='stage-sampling assumption'),
 recovery=dict(position_rms_factor=.1,phase_rms=.3,redraws=8,position_denominator='candidate free members',clipping=False,sites_excluded=True,output_included=True),
 clocks=dict(estimator=10.,qualification=60.,adaptation=.05,freq_cut=.005,pattern_cut=.1),
 N1=dict(recipes=N1_RECIPES,h=[PRODUCTION_H,REFINEMENT_H],substeps=[20,80],phase_scale=PHASE_SCALE,world_dt=WORLD_DT,wrapped_phase=.01,unwrapped_phase=.01,free_position=.01,entry=.1,Nx_match=.99,Ntheta_match=.99,pins='exact',minimum_distances='both integrations',saddle_diagnostic=N1_SADDLE_DIAGNOSTIC),
 F1=dict(F1d=dict(scaffold='F1b',phase_scales=list(F1D_SCALES),h=PRODUCTION_H,verdict_cut=None),F1c=dict(margin_time=12.,margin_seconds=4.,margin_verdict_cut=None,deadline_seconds=8.,hold_until=24.,persistence_until=160.)),
 comparator=dict(task='perceive',recipients=[10000512,10000639],scope='fresh final whole medium copy per episode',effect='total effect of removing site bodies, including neighbour selection and normalization',verdict_cut=None,count_changes=True))
CONFIG_SHA256=hashlib.sha256(canonical(CONFIG)).hexdigest()
