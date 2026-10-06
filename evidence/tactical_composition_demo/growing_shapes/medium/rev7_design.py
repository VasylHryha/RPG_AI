"""Revision 7.7: full structural graph and strong transmission paths."""
from collections import deque
from copy import deepcopy
from dataclasses import dataclass
import math
import numpy as np
from .design_0h import DesignMedium, DT, SITES, kernel, wrap
from .rev7_native import Rev7Native,budget_counts
from ..runner.rev7_config import PRODUCTION_H, REFINEMENT_H, STRONG_LINK_RADIUS

@dataclass(frozen=True)
class Frame:
    index:int
    time:float
    elements:dict
    sites:dict
    neighbors:dict
    excursion:dict
    motion_neighbors:dict

def individual_valid(frame,id):return frame.excursion[id]<=math.pi/2

def pair_valid(frame,a,b):return frame.excursion[a]+frame.excursion[b]<=math.pi/2

def separated(point,other,limit):
    # Bound coordinate/subtraction/hypot roundoff only. Physical clearances
    # remain .05 and .3; a literal (3.7,0) must represent .3 from (4,0).
    distance=math.hypot(point[0]-other[0],point[1]-other[1])
    allowance=8*max(math.ulp(float(v)) for v in (*point,*other,limit))
    return distance+allowance>=limit

def clear_position(point,positions):
    return all(separated(point,p,.05) for p in positions) and all(separated(point,p,.3) for p in SITES)


R_STAR=.556
TRIAL_NAMES=('edge_a_to_new','new_reached','a_reached','paths_kept','deficit_or_connect','clearance')
OUTCOMES=('accepted','cap','cost','placement','exhausted','no_output','no_root','quota')
ROLE_BY_MEASUREMENT={
    'element':dict(drive='gain * strength * kernel',sensor_partners=True,P_i='base',e_i='episode mean',lock='sensor and C4',coverage=True,effective_root='gain > 0 and active strict reach',geometric_exposure='recorded'),
    'output':dict(drive=0,sensor_partners=False,P_i=None,e_i=0,lock='C4 only',coverage=False,effective_root=False,geometric_exposure='recorded'),
}


def reach(starts,edges):
    found=set(starts);todo=list(found)
    while todo:
        for node in edges.get(todo.pop(),()):
            if node not in found:found.add(node);todo.append(node)
    return found


@dataclass
class Influence:
    incoming: dict
    outgoing: dict
    roots: dict
    outputs: set

    def forward(self,site=None):
        return reach(set().union(*self.roots.values()) if site is None else self.roots.get(site,set()),self.outgoing)

    def backward(self): return reach(self.outputs,self.incoming)
    def path(self,site): return bool(self.forward(site)&self.outputs)


def graph(native,drives,*,strong=False):
    es=native.elements
    if strong:
        incoming={e.id:{es[j].id for j in row}
                  for e,row in zip(es,native.strong_neighbors())}
    else:
        idx,mask,_=native.neighbors()
        incoming={e.id:{es[j].id for j,on in zip(idx[i],mask[i]) if on} for i,e in enumerate(es)}
    outgoing={e.id:set() for e in es}
    for target,sources in incoming.items():
        for source in sources:outgoing[source].add(target)
    outputs={e.id for e in es if native.role(e.id)=='output'}
    roots={d.id:{e.id for e in es if e.id not in outputs and not e.silent and native.gain(e.id)>0 and d.strength>0 and math.hypot(e.x-d.x,e.y-d.y)<d.reach} for d in drives}
    return Influence(incoming,outgoing,roots,outputs)


def deficit(native,front,back):
    es={e.id:e for e in native.elements}
    return min((math.hypot(es[a].x-es[b].x,es[a].y-es[b].y) for a in front for b in back),default=math.inf)


def geometry(native,drives):
    """Only immutable geometry/role/gain records; no histories, frames or RNG."""
    return ([(e.id,e.x,e.y,native.role(e.id),native.gain(e.id),bool(e.silent))
             for e in native.elements],
            [(d.id,d.x,d.y,d.strength,d.reach) for d in drives])


def geometric_graph(elements,drives,k=8,radius=3.,*,strong=False):
    # Medium::neighbors ties by element array index, including after deletions.
    incoming={}
    for i,(id,x,y,role,gain,silent) in enumerate(elements):
        candidates=[] if silent else [(math.hypot(x-e[1],y-e[2]),j,e[0])
            for j,e in enumerate(elements) if i!=j and not e[5]]
        incoming[id]={id2 for r,j,id2 in sorted(candidates)[:k]
                      if r<radius and (not strong or r<=STRONG_LINK_RADIUS)}
    outgoing={e[0]:set() for e in elements}
    for target,sources in incoming.items():
        for source in sources:outgoing[source].add(target)
    outputs={e[0] for e in elements if e[3]=='output'}
    roots={id:{e[0] for e in elements if e[3]!='output' and not e[5] and e[4]>0
               and strength>0 and math.hypot(e[1]-x,e[2]-y)<reach}
           for id,x,y,strength,reach in drives}
    return Influence(incoming,outgoing,roots,outputs)


def geometric_trial(elements,drives,site,a,b,position,new,*,k=8,radius=3.,before=None):
    # Trials use G_s, including edge_a_to_new; budget admission still uses G.
    before=before or geometric_graph(elements,drives,k,radius,strong=True)
    positions={e[0]:(e[1],e[2]) for e in elements}
    def gap(g,positions):
        return min((math.hypot(positions[u][0]-positions[v][0],positions[u][1]-positions[v][1])
            for u in g.forward(site) for v in g.backward()),default=math.inf)
    old_gap=gap(before,positions)
    after=geometric_graph(elements+[(new,*position,'element',1.,False)],drives,k,radius,strong=True)
    reached=after.forward(site);positions[new]=position
    return dict(edge_a_to_new=a in after.incoming[new],new_reached=new in reached,
        a_reached=a in reached,paths_kept=all(not before.path(s) or after.path(s) for s in before.roots),
        deficit_or_connect=after.path(site) or gap(after,positions)<old_gap,
        clearance=clear_position(position,[(e[1],e[2]) for e in elements]))


class Rev7Medium(DesignMedium):
    def __init__(self,seed=0,*,growth_rng=None,frozen=False,params=None,backend="native",h=PRODUCTION_H):
        self.backend=backend;self.h=h
        if backend not in ("native","reference") or h not in (PRODUCTION_H,REFINEMENT_H):raise ValueError("invalid solver configuration")
        self.frame_excursion={};self.fast_transient_count=0;self.invalid_pair_count=0
        self.estimator_counts={};self.estimator_seen=set();self.estimator_index=None
        self.native=Rev7Native(seed,params=params)
        self.native.options(automatic_samples=False,carried_sites=True,undirected_cost=True)
        self.native.first_id(0)
        self.step_index=0;self.frames=deque(maxlen=601)
        self.death={};self.birth_steps={};self.novelty={s:0. for s in range(8)}
        self.events=[];self.drives=[];self.peak=0
        self.growth_rng=growth_rng
        self.frozen=frozen;self.pointer=0;self.request_counter=0
        self.diagnostics=[];self.record()

    def clone(self,*,events=True,frames=True):
        branch=object.__new__(type(self))
        branch.__dict__={k:[] if not events and k in ('events','diagnostics') else
            deque([deepcopy(v[-1])] if v else [],maxlen=601) if k=='frames' and not frames else deepcopy(v)
            for k,v in self.__dict__.items() if k!='native'}
        branch.native=self.native.clone()
        return branch

    def role(self,id):return self.native.role(id)
    def influence(self):return graph(self.native,self.drives)

    def strong_influence(self):
        if self.backend=='native':return graph(self.native,self.drives,strong=True)
        elements,drives=geometry(self.native,self.drives)
        return geometric_graph(elements,drives,self.native.params.k,
                               self.native.params.radius,strong=True)

    def add(self,position,phase,rate=math.pi,gain=1.,rule='B1',role='element',**values):
        id=self.native.add(*position,phase,rate,role=role)
        self.native.set_gain(id,gain);self.death[id]=0.;self.birth_steps[id]=self.step_index
        self.peak=max(self.peak,len(self.native));self.emit(rule,[id],role=role,**values)
        # Native topology is always computed from positions, never cached through mutations.
        return id

    def remove(self,id,rule,**values):
        super().remove(id,rule,**values);self.influence()

    def record(self):
        elements=self.native.elements;idx,mask,_=self.native.neighbors()
        motion=self.native.motion_neighbors();drives=self.native.reference_drives()
        self.frames.append(Frame(self.step_index,self.time,
            {e.id:(e.x,e.y,e.phase) for e in elements},
            {d.id:(d.x,d.y,d.phase,d.strength) for d in self.drives},
            {e.id:tuple(elements[j].id for j,on in zip(idx[i],mask[i]) if on) for i,e in enumerate(elements)},
            {e.id:self.frame_excursion.get(e.id,0.) for e in elements},
            {e.id:tuple(('element',elements[j].id) if j>=0 else ('site',drives[-j-1].id) for j in motion[i]) for i,e in enumerate(elements)}))

    def offsets(self,id,partner,sensor=False):
        if sensor and self.role(id)=='output':return None
        frames=self.samples(id,100)
        if frames is None:return None
        values=[];excluded=eligible=0
        for f in frames:
            e=f.elements[id]
            if sensor:
                site=f.sites.get(partner)
                if site is not None and site[3]>0 and math.hypot(e[0]-site[0],e[1]-site[1])<3:
                    eligible+=1
                    if individual_valid(f,id):values.append(e[2]-site[2])
                    else:excluded+=1
            elif partner in f.neighbors[id] and partner in f.elements:
                eligible+=1
                if pair_valid(f,id,partner):values.append(e[2]-f.elements[partner][2])
                else:excluded+=1
        if self.estimator_index!=self.step_index:
            self.estimator_seen.clear();self.estimator_index=self.step_index
        key=(id,partner,sensor)
        if key not in self.estimator_seen:
            self.estimator_seen.add(key)
            counts=self.estimator_counts.setdefault('site' if sensor else 'element',dict(windows=0,eligible_observations=0,valid_observations=0,transient_exclusions=0,rejected_below_80=0,active_histogram={}))
            counts['windows']+=1;counts['eligible_observations']+=eligible;counts['valid_observations']+=len(values)
            counts['transient_exclusions']+=excluded;counts['rejected_below_80']+=int(len(values)<80)
            counts['active_histogram'][len(values)]=counts['active_histogram'].get(len(values),0)+1
        return values if len(values)>=80 else None

    def estimator_validity(self):
        return dict(status='DESCRIPTIVE',used_in_verdict=False,window_records=100,minimum_active=80,
            denominator_policy='unique directed id/partner/kind windows actually requested per world endpoint; site reach/strength or element neighbour eligibility before excursion filter',
            site=deepcopy(self.estimator_counts.get('site')),element=deepcopy(self.estimator_counts.get('element')))

    def adapt(self):
        signals={}
        for e in self.native.elements:
            frames=self.samples(e.id,101)
            if frames is not None and individual_valid(frames[0],e.id) and individual_valid(frames[-1],e.id):
                estimate=(frames[-1].elements[e.id][2]-frames[0].elements[e.id][2])/10
                rate=float(np.clip(e.rate+.005*(estimate-e.rate),.5*math.pi,1.5*math.pi))
                self.native.set_element(e.id,e.x,e.y,e.phase,rate)
            signal=self.gain_signal(e.id)
            if signal is not None:
                self.native.set_gain(e.id,float(np.clip(self.native.gain(e.id)+.005*(signal-self.native.gain(e.id)),0,2)))
                signals[e.id]=signal
        self.emit('adaptation',rates={e.id:e.rate for e in self.native.elements},gains={e.id:self.native.gain(e.id) for e in self.native.elements},defined_signals=signals)
        return signals

    def covered(self,site):
        f=self.frames[-1];s=f.sites.get(site)
        if s is None or s[3]<=0:return False
        for element in self.native.elements:
            id=element.id;e=f.elements.get(id)
            if self.role(id)=='output' or e is None or self.samples(id,101) is None or math.hypot(e[0]-s[0],e[1]-s[1])>=3:continue
            values=self.offsets(id,site,True)
            if values is not None:
                plv,offset=self.statistics(values)
                if plv>=.8 and abs(offset)<=.5:return True
        return False

    def gain_signal(self,id):
        return None if self.role(id)=='output' or not individual_valid(self.frames[-1],id) else super().gain_signal(id)

    def integrate(self,drives):
        self.drives=[type(d).from_buffer_copy(d) for d in drives]
        self.native.set_drives(self.drives)
        bounds=np.zeros(len(self.native));interactions=[]
        for _ in range(round(DT/self.h)):
            if self.backend=='native':self.native.step(self.h)
            else:self.native.reference_step(self.h)
            bounds+=np.asarray(self.native.excursion())
            interactions.append(self.native.motion_neighbors())
        self.frame_excursion={e.id:float(v) for e,v in zip(self.native.elements,bounds)}
        self.fast_transient_count+=int(any(v>math.pi/2 for v in bounds))
        self.step_index+=1
        for d in self.drives:d.phase+=DT*d.rate
        if not self.frozen:self.native.observe();self.record()
        row=self.endpoint_diagnostics();row['excursion']=dict(self.frame_excursion)
        pairs=[(a,b) for i,a in enumerate(self.frame_excursion) for b in list(self.frame_excursion)[i+1:] if self.frame_excursion[a]+self.frame_excursion[b]>math.pi/2]
        row['invalid_pairs']=pairs;self.invalid_pair_count+=len(pairs)
        row['fast_transient']=any(v>math.pi/2 for v in bounds)
        row['stage_sampling_limitation']='warning bound assumes excursions between RK4 stage evaluations are controlled'
        row['motion_interactions']=interactions
        row['motion_neighbors']=self.motion_topology()
        row['motion_counts']={id:len(v) for id,v in row['motion_neighbors'].items()}
        row['site_motion']=self.site_motion()
        return row

    def phase_topology(self):
        es=self.native.elements;indices,masks,_=self.native.neighbors()
        return {e.id:[es[j].id for j,on in zip(row,mask) if on] for e,row,mask in zip(es,indices,masks)}

    def motion_topology(self):
        es=self.native.elements;ds=self.native.reference_drives()
        return {e.id:[('element',es[j].id) if j>=0 else ('site',ds[-j-1].id) for j in row] for e,row in zip(es,self.native.motion_neighbors())}

    def site_motion(self):
        es=self.native.elements;ds=self.native.reference_drives();p=self.native.params
        result={}
        for e,links in zip(es,self.native.motion_neighbors()):
            terms=[]
            for j in links:
                if j>=0:continue
                d=ds[-j-1];dx,dy=d.x-e.x,d.y-e.y;rr=max(math.hypot(dx,dy),.3)
                scale=p.geometry_rate*(p.A*(1+p.J*math.cos(d.phase-e.phase))-p.B/rr)/rr/max(1,len(links))
                terms.append(dict(site=d.id,velocity=[scale*dx,scale*dy],applied=self.role(e.id)!='output' and not self.native.policy()[1],count=len(links)))
            result[e.id]=terms
        return result

    def endpoint_diagnostics(self):
        g=self.strong_influence();exposure={}
        for e in self.native.elements:
            radius=math.hypot(e.x,e.y)
            geometric=any(d.strength>0 and math.hypot(e.x-d.x,e.y-d.y)<d.reach for d in self.drives)
            exposure[e.id]=dict(radius=radius,wall=radius>6,geometric=geometric,
                sensor_access=any(math.hypot(e.x-x,e.y-y)<3 for x,y in SITES),
                drive=geometric and self.role(e.id)!='output' and self.native.gain(e.id)>0)
        return dict(index=self.step_index,active_sites=[d.id for d in self.drives if d.strength>0],paths=[g.path(s) for s in range(8)],
                    cut_off={e.id:self.native.cut_off(e.id) for e in self.native.elements},exposure=exposure)

    def observe_diagnostics(self,row):
        self.diagnostics.append(dict(excursion=dict(self.frame_excursion),invalid_pairs=[(a,b) for i,a in enumerate(self.frame_excursion) for b in list(self.frame_excursion)[i+1:] if self.frame_excursion[a]+self.frame_excursion[b]>math.pi/2],motion_neighbors=self.motion_topology(),site_motion=self.site_motion(),index=row.get('step',row.get('index',self.step_index)),
            active_sites=row.get('active_sites',[d.id for d in self.drives if d.strength>0]),
            covered_sites=row.get('covered_sites',{}),
            paths=row['paths'],cut_off=row['cut_off'],exposure=row['exposure']))

    def timers(self):
        if self.frozen:raise ValueError('frozen timers are inactive')
        for e in self.native.elements:
            lock=self.lock(e.id)
            self.death[e.id]=self.death.get(e.id,0.)+DT if lock is not None and lock<.5 else 0.
        covered=[]
        for site in range(8):
            active=any(d.id==site and d.strength>0 for d in self.drives)
            yes=self.covered(site) if active else False;covered.append(yes)
            if active:self.novelty[site]=0. if yes else self.novelty[site]+DT
        g=self.influence();live=g.forward()|g.backward()
        for e in self.native.elements:
            self.native.cut_off(e.id,0. if e.id in live else self.native.cut_off(e.id)+DT)
        self.observe_diagnostics(dict(self.endpoint_diagnostics(),covered_sites={s:covered[s] if len(self.frames)>=101 else None for s in range(8)}))
        return covered

    def request(self,rule,site=None):
        value=self.request_counter;self.request_counter+=1
        self.emit('birth_request',request=value,birth_rule=rule,site=site)
        return value

    def terminal(self,request,rule,site,outcome,attempts=0,**extra):
        if outcome not in OUTCOMES:raise ValueError('unknown birth outcome')
        self.emit('birth_terminal',request=request,birth_rule=rule,site=site,
                  outcome=outcome,attempts=attempts,accepted=int(outcome=='accepted'),**extra)

    def spiral_candidate(self,site,request,rule):
        positions=[(e.x,e.y) for e in self.native.elements]
        for j in range(50):
            point=np.asarray(site)+.1*j*np.array([math.cos(j*2.39996),math.sin(j*2.39996)])
            clear=clear_position(point,positions)
            self.emit('birth_attempt',request=request,birth_rule=rule,candidate=j,position=point.tolist(),clearance=clear)
            if clear:return tuple(point),j+1
        return None,50

    def trial(self,site,a,b,position):
        elements,drives=geometry(self.native,self.drives)
        # The trial id only needs to be unique; tie order is insertion order.
        new=max((e[0] for e in elements),default=-1)+1
        return geometric_trial(elements,drives,site,a,b,position,new,
            k=self.native.params.k,radius=self.native.params.radius)

    def feasible(self,position,phase):
        # O and its incident pairs are external to N + .1 per ordinary pair.
        # Admission also uses geometry only; never clone native histories.
        if not clear_position(position,[(e.x,e.y) for e in self.native.elements]):return 'placement'
        elements,drives=geometry(self.native,self.drives)
        if sum(e[3]!='output' for e in elements)+1>64:return 'cap'
        new=max((e[0] for e in elements),default=-1)+1
        g=geometric_graph(elements+[(new,*position,'element',1.,False)],drives,
            self.native.params.k,self.native.params.radius)
        n,pairs=budget_counts({e[0]:e[3] for e in elements}|{new:'element'},g.incoming)
        return 'cost' if n+.1*pairs>64 else None

    def b_out(self,blocked=False):
        if self.influence().outputs:return []
        request=self.request('B-out');point=(0.,0.);attempts=1
        clear=clear_position(point,[(e.x,e.y) for e in self.native.elements])
        self.emit('birth_attempt',request=request,birth_rule='B-out',candidate=0,position=point,clearance=clear)
        if not clear:point=None
        # A permanent external receiver never competes with growth for budget.
        reason='placement' if point is None else None
        if reason:self.terminal(request,'B-out',None,reason,attempts);return []
        neighbors=[e.phase for e in self.native.elements if math.hypot(e.x-point[0],e.y-point[1])<3]
        z=np.exp(1j*np.asarray(neighbors)).mean() if neighbors else 0j
        if abs(z)<.1:
            if self.growth_rng is None:raise ValueError('persistent growth PCG64 required for B-out fallback')
            phase=float(self.growth_rng.uniform(0,2*math.pi))
        else:phase=float(np.angle(z))
        id=self.add(point,phase,rule='B-out',role='output',request=request)
        self.terminal(request,'B-out',None,'accepted',attempts,id=id);return [id]

    def b_path(self,blocked=False):
        added=[];p=self.pointer;self.pointer=(p+1)%8
        for site in [(p+j)%8 for j in range(8)]:
            d=next((d for d in self.drives if d.id==site and d.strength>0),None)
            if d is None:continue
            g=self.strong_influence()
            if g.path(site):continue
            request=self.request('B-path',site)
            if len(added)>=2:self.terminal(request,'B-path',site,'quota');continue
            front,back=g.forward(site),g.backward()
            if not back:self.terminal(request,'B-path',site,'no_output');continue
            if not front:self.terminal(request,'B-path',site,'no_root');continue
            es={e.id:e for e in self.native.elements}
            elements,drives=geometry(self.native,self.drives)
            new=max(es,default=-1)+1
            pairs=sorted((math.hypot(es[a].x-es[b].x,es[a].y-es[b].y),a,b) for a in front for b in back)[:8]
            attempts=0;done=False;failures={name:0 for name in TRIAL_NAMES}
            for _,a,b in pairs:
                direction=math.atan2(es[b].y-es[a].y,es[b].x-es[a].x)
                for rotation in [0]+[sign*angle for angle in range(15,91,15) for sign in (1,-1)]:
                    angle=direction+math.radians(rotation)
                    point=(es[a].x+R_STAR*math.cos(angle),es[a].y+R_STAR*math.sin(angle))
                    checks=geometric_trial(elements,drives,site,a,b,point,new,
                        k=self.native.params.k,radius=self.native.params.radius,before=g);attempts+=1
                    for name,yes in checks.items():failures[name]+=int(not yes)
                    self.emit('birth_attempt',request=request,birth_rule='B-path',site=site,
                              a=a,b=b,position=point,checks=checks)
                    if not all(checks.values()):continue
                    reason=self.feasible(point,es[a].phase)
                    if blocked and reason is None:reason='cost'
                    if reason:self.terminal(request,'B-path',site,reason,attempts,failures=failures)
                    else:
                        id=self.add(point,es[a].phase,rule='B-path',site=site,request=request)
                        added.append(id);self.terminal(request,'B-path',site,'accepted',attempts,id=id,failures=failures)
                    done=True;break
                if done:break
            if not done:self.terminal(request,'B-path',site,'exhausted',attempts,failures=failures)
        return added

    def b1(self,blocked=False):
        added=[]
        for site in range(8):
            if self.novelty[site]<20-1e-9:continue
            if not any(d.id==site and d.strength>0 for d in self.drives):
                self.emit('queued_demand',site=site,timer=self.novelty[site]);continue
            request=self.request('B1',site)
            if len(added)>=2:self.terminal(request,'B1',site,'quota');continue
            d=next(d for d in self.drives if d.id==site)
            point,attempts=self.spiral_candidate((d.x,d.y),request,'B1')
            reason='placement' if point is None else self.feasible(point,d.phase)
            if blocked and reason is None:reason='cost'
            if reason:self.terminal(request,'B1',site,reason,attempts)
            else:
                id=self.add(point,d.phase,rule='B1',site=site,request=request)
                added.append(id);self.novelty[site]=0.;self.terminal(request,'B1',site,'accepted',attempts,id=id)
        return added

    def growth(self,*,b1=True,control=None,intact_births=()):
        if self.frozen:raise ValueError('frozen growth is inactive')
        measured={e.id:self.lock(e.id) for e in self.native.elements}
        for rule,threshold,timer in [('D1',40,self.death.get),('D4',120,self.native.cut_off)]:
            for e in self.native.elements:
                if self.role(e.id)=='output':continue
                if self.step_index-self.birth_steps[e.id]>=200 and (timer(e.id) or 0)>=threshold-1e-9:
                    duration=timer(e.id)
                    self.remove(e.id,rule,lock=measured[e.id],duration=duration)
        blocked=False
        while self.cost()>64:
            eligible=[e for e in self.native.elements if self.role(e.id)!='output' and self.step_index-self.birth_steps[e.id]>=200]
            if not eligible:blocked=True;self.emit('protected_over_budget');break
            e=min(eligible,key=lambda e:(measured[e.id] or 0.,e.id));self.remove(e.id,'D3',lock=measured[e.id])
        out=self.b_out(blocked);path=self.b_path(blocked)
        births=self.b1(blocked) if b1 else control.check(self,intact_births,blocked) if control else []
        self.emit('growth_check',count=len(self.native),additions=out+path+births,
                  b1_additions=births,protected_over_budget=blocked,pointer=self.pointer)
        return births
