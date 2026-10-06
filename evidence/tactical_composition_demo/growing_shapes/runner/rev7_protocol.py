"""Revision-7.3 identity, entropy, decoder, inference and registered stop rules."""
import hashlib
import math
import numpy as np
from .protocol import BINDING, VERSION as OLD_VERSION, TASKS, canonical, template_hash, entropy, permutation, bindings, oriented, rotation, Calibration, covariance
from ..medium.design_0h import wrap
from ..world.world import Action

RHS_VERSION='rev7_rhs_v1'
EVAL_VERSION='rev7_eval_v1'
TEMPLATE_VERSION='rev7_template_v1'
QUAL_VERSION='rev7_qual_v1'
from .rev7_config import CONFIG_SHA256


def seed(key):
    return int.from_bytes(hashlib.sha256(('0h-rev7/'+key).encode('ascii')).digest()[:8],'big')


def generator(key):return np.random.Generator(np.random.PCG64(seed(key)))

def recovery_generator(master,index):return np.random.default_rng(entropy(master,f'kick:{index}'))


def training_episode(arm,k,e):
    if arm not in ('task_blind','reward') or type(k) is not int or not 0<=k<8 or type(e) is not int or not 0<=e<2000:
        raise ValueError('invalid training slot')
    slot=k+(8 if arm=='reward' else 0)
    return 11000000+10000*slot+e


def donor_entries():
    digests={j:hashlib.sha256(f'0h-rev7/donor_perm/{j}'.encode('ascii')).digest() for j in range(128)}
    ranks={j:r for r,j in enumerate(sorted(digests,key=digests.get))}
    return [dict(j=j,recipient=10000512+j,donor=10000640+ranks[j],rank_pi_j=ranks[j],rank_digest_sha256=digests[j].hex()) for j in range(128)]


def template(native,ids,time):
    es={e.id:e for e in native.elements}
    value=dict(members=[[float(es[id].x),float(es[id].y),float(es[id].phase-math.pi*time),float(es[id].rate),float(native.gain(id)),native.role(id),native.pin(id)[0],list(native.pin(id)[1]) if native.pin(id)[0] else None] for id in sorted(ids)],
        binding=dict(BINDING),rhs_version=RHS_VERSION,eval_version=EVAL_VERSION,template_version=TEMPLATE_VERSION,qual_version=QUAL_VERSION,configuration_sha256=CONFIG_SHA256)
    validate_template(value)
    return value


def validate_template(value):
    if set(value)!={'members','binding','rhs_version','eval_version','template_version','qual_version','configuration_sha256'} or value['binding']!=BINDING or value['qual_version']!=QUAL_VERSION or value['configuration_sha256']!=CONFIG_SHA256 or (value['rhs_version'],value['eval_version'],value['template_version'])!=(RHS_VERSION,EVAL_VERSION,TEMPLATE_VERSION):
        raise ValueError('rev7 template version/binding/schema mismatch')
    canonical(value)
    outputs=0
    for row in value['members']:
        if len(row)!=8 or row[5] not in ('element','output') or not all(type(x) in (float,int) and math.isfinite(x) for x in row[:5]) or not 0<=row[4]<=2:
            raise ValueError('invalid template member')
        if type(row[6]) is not bool or row[6]!=(row[5]=='output'):raise ValueError('pin flag does not match role')
        if row[6]:
            if not isinstance(row[7],list) or len(row[7])!=2 or row[7]!=row[:2]:raise ValueError('stored pin coordinate mismatch')
        elif row[7] is not None:raise ValueError('free member has pin coordinate')
        outputs+=row[5]=='output'
    if outputs>1:raise ValueError('singleton output cap')


def copy_template(value,carrier_offset=0.,*,backend="native"):
    # Legacy loader remains authoritative for its own version; no silent migration.
    if value.get('constants_version')==OLD_VERSION:
        from .evaluator import copy_template as legacy
        return legacy(value,carrier_offset)
    if value.get('template_version')=='rev6_template_v1':
        from .rev6_protocol import copy_template as rev6
        return rev6(value,carrier_offset)
    validate_template(value)
    if carrier_offset not in (0.,math.pi):raise ValueError('carrier offsets are 0 and pi')
    from ..medium.rev7_design import Rev7Medium
    medium=Rev7Medium(frozen=True,backend=backend)
    try:
        medium.native.start_clock(carrier_offset/math.pi)
        medium.step_index=round(carrier_offset/math.pi/.1)
        for x,y,offset,rate,gain,role,pinned,pin in value['members']:
            medium.add((x,y),offset+carrier_offset,rate,gain,rule='COPY',role=role)
        medium.frames.clear();medium.record()
        return medium
    except Exception:medium.close();raise


def decode(task,observation,coherence,phase,time):
    abstain=coherence<.05
    beta=0. if abstain else float(wrap(phase-math.pi*time))
    if task=='choose':
        live=[e for e in observation.enemies[:observation.enemy_count] if e.visible and e.hp>0]
        if not live:raise ValueError('INVALID: no live choice')
        choice=min(live,key=lambda e:(0 if abstain else abs(float(wrap(beta-e.angle))),e.id))
        return Action(0,0,choice.id)
    if abstain:return Action()
    return Action(beta,0. if task!='move' else 1.)


def action(task,observation,native,time):return decode(task,observation,*native.output(),time)


def relay(task,observation,drives,time,kind):
    if kind not in ('site0','oracle'):raise ValueError('unknown relay')
    active=[d for d in drives if d.strength>0 and (kind=='oracle' or d.id==0)]
    selected=min(active,key=lambda d:(-d.strength,d.id)) if active else None
    # Relay's angle is 0 if inactive; it is a virtual singleton, with C=1.
    return decode(task,observation,1.,math.pi*time if selected is None else selected.phase,time)


def input_phasor(observation,drives,time):
    """19.9 input-only perceive decoder; drives carry endpoint carrier phases.

    No elements, gain, geometry or oscillator transfer enters this sum.
    An empty (zero) sum uses arg(0)=0 via atan2, with C=1 as specified.
    """
    active=[d for d in drives if d.strength>0]
    x=sum(d.strength*math.cos(d.phase-math.pi*time) for d in active)
    y=sum(d.strength*math.sin(d.phase-math.pi*time) for d in active)
    return decode('perceive',observation,1.,math.pi*time+math.atan2(y,x),time)


def replay_on_clock(schedule,time):
    """Schedule rows store relative donor angle, not the donor's absolute carrier."""
    from ..medium.medium import Drive
    return [Drive(id,x,y,math.pi*time+angle,rate,strength,width,reach)
            for id,x,y,angle,rate,strength,width,reach in schedule]


def _beta_fraction(a,b,x):
    # Lentz continued fraction for regularized incomplete beta (no extra dependency).
    tiny=1e-300;qab=a+b;qap=a+1;qam=a-1;c=1.;d=1-qab*x/qap
    d=1/max(abs(d),tiny)*(1 if d>=0 else -1);h=d
    for m in range(1,400):
        for aa in (m*(b-m)*x/((qam+2*m)*(a+2*m)), -(a+m)*(qab+m)*x/((a+2*m)*(qap+2*m))):
            d=1+aa*d;c=1+aa/c
            if abs(d)<tiny:d=tiny
            if abs(c)<tiny:c=tiny
            d=1/d;delta=d*c;h*=delta
        if abs(delta-1)<2e-14:return h
    raise ValueError('INVALID: beta fraction failed to converge')


def _ibeta(a,b,x):
    if x<=0:return 0.
    if x>=1:return 1.
    factor=math.exp(math.lgamma(a+b)-math.lgamma(a)-math.lgamma(b)+a*math.log(x)+b*math.log1p(-x))
    if x<(a+1)/(a+b+2):return factor*_beta_fraction(a,b,x)/a
    return 1-factor*_beta_fraction(b,a,1-x)/b


def student_cdf(t,df=127):
    tail=.5*_ibeta(df/2,.5,df/(df+t*t))
    return 1-tail if t>=0 else tail


def t_quantile(probability,df=127):
    if not .5<probability<1 or df<=0:raise ValueError('invalid t quantile')
    lo,hi=0.,1.
    while student_cdf(hi,df)<probability:hi*=2
    for _ in range(70):
        mid=(lo+hi)/2
        if student_cdf(mid,df)<probability:lo=mid
        else:hi=mid
    return (lo+hi)/2


def paired_bounds(intact,comparator,*,secondary=False):
    a,b=np.asarray(intact,dtype=float),np.asarray(comparator,dtype=float)
    if a.shape!=(128,) or b.shape!=(128,) or not np.isfinite(a).all() or not np.isfinite(b).all():
        return dict(verdict='INVALID',reason='128 finite paired normalized episodes required',mean=None,lower=None,upper=None)
    d=a-b
    if not np.isfinite(d).all():return dict(verdict='INVALID',reason='nonfinite difference',mean=None,lower=None,upper=None)
    mean=float(d.mean());sd=float(d.std(ddof=1))
    if not math.isfinite(mean) or not math.isfinite(sd):return dict(verdict='INVALID',reason='nonfinite mean or variance',mean=None,lower=None,upper=None)
    alpha=.05/3 if secondary else .05
    radius=t_quantile(1-alpha)*sd/math.sqrt(128)
    return dict(verdict='VALID',mean=mean,sd=sd,lower=mean-radius,upper=mean+radius,df=127,alpha=alpha,
                positive=mean-radius>0,negative=mean+radius<0,constant=sd==0)


def late_count(growth_counts,events):
    late=[(t/16,n) for t,n in growth_counts if 25600<=t<=32000]
    if len(late)<2 or not np.isfinite(late).all():return dict(invalid='missing/nonfinite late count',slope=None)
    x,y=np.asarray(late,dtype=float).T;den=float(np.sum((x-x.mean())**2))
    if den<=0:return dict(invalid='undefined slope',slope=None)
    slope=float(np.sum((x-x.mean())*(y-y.mean()))/den*100)
    terminal=[];protected=False
    for e in events:
        if not 25600<=e['time']<=32000:continue
        if e['rule']=='birth_terminal':terminal.append(e)
        protected|=e['rule']=='protected_over_budget'
    rejected=any(e['values']['outcome'] in ('placement','exhausted') for e in terminal)
    return dict(invalid=None,slope=slope,rejected=rejected,protected_over_budget=protected,
                settled=abs(slope)<=.5 and not rejected and not protected,
                terminal_requests=len(terminal),attempts=sum(e['values']['attempts'] for e in terminal),
                outcomes={o:sum(e['values']['outcome']==o for e in terminal) for o in ('accepted','cap','cost','placement','exhausted','no_root','no_output','quota')})


def aggregate(seeds):
    names=('G0',"G0'",'G2','G1','G1c','G5')
    if len(seeds)!=8 or any(s.get('invalid') or not s.get('complete') for s in seeds):return {n:'INVALID' for n in names}
    def eight_cut(pass_count,fail_count,fail_at):return 'PASS' if pass_count>=6 else 'FAIL' if fail_count>=fail_at else 'INCONCLUSIVE'
    g0pass=g0fail=g2pass=settled=0;bad0=bad2=badcount=False
    bearing=[]
    for s in seeds:
        bounds=s.get('bounds',{}).get('perceive',{})
        bad2|=not all(bounds.get(c,{}).get('verdict')=='VALID' for c in ('default','random','donor','output_channel')) or not s.get('perceive_usable',False)
        g2pass+=int(all(bounds.get(c,{}).get('positive',False) for c in ('default','random','donor','output_channel')))
        g0=s.get('g0',{});bad0|=g0.get('verdict')!='VALID' or not s.get('perceive_usable',False) or s.get('eligible',0)==0 or s.get('control_eligible',0)==0
        coverage=s.get('coverage');control=s.get('control_coverage')
        finite=all(v is not None and math.isfinite(v) for v in (coverage,control));bad0|=not finite
        matched=s.get('matched',False)
        g0pass+=int(matched and g0.get('positive',False) and finite and coverage>control)
        g0fail+=int(matched and g0.get('negative',False))
        count=s.get('late',{});badcount|=bool(count.get('invalid')) or 'settled' not in count
        settled+=int(count.get('settled',False))
        if s.get('snapshots',0)>0:bearing.append(s)
    g5='INCONCLUSIVE'
    if any(len(s.get('g5',[]))!=min(20,s.get('snapshots',0)) or not np.isfinite(s.get('g5',[])).all() for s in seeds):g5='INVALID'
    elif len(bearing)>=6:
        rates=[float(np.mean(np.asarray(s['g5'])<=.1)) for s in bearing]
        g5=eight_cut(sum(v>=.8 for v in rates),sum(v<.5 for v in rates),3)
    return dict(G0='INVALID' if bad0 else eight_cut(g0pass,g0fail,6),
                **{"G0'":'INVALID' if badcount else eight_cut(settled,8-settled,3)},
                G2='INVALID' if bad2 else 'PASS' if g2pass>=6 else 'FAIL' if g2pass<=2 else 'INCONCLUSIVE',
                G1='PASS' if len(bearing)>=6 else 'FAIL' if len(bearing)<=2 else 'INCONCLUSIVE',G1c='DESCRIPTIVE',G5=g5)


# Every row is an explicit yes/no flag -> one action, one responsible role.
STOP_ROWS=(
 ('integration_not_tested_reviewed','Block all execution','implementer'),
 ('source_unit_endpoint_mismatch','Block execution','implementer'),
 ('N1_failed_or_invalid','Block F1 and every later fixture','implementer'),
 ('F1_F4_failed','Block F5 and development; report','implementer'),
 ('fixture_invalid','Report INVALID; block next stage','implementer'),
 ('F5_failed','Block development; write failure report','drafter'),
 ('F7_unmatched','Block development; write failure report','drafter'),
 ('protocol_changed_after_results','Draft new revision with fresh entropy','drafter'),
 ('development_over_hour_before_22','Ask owner under decision 0031','implementer'),
 ('development_stopped_next_needed','Ask owner','owner'),
 ('engines_not_ready_reviewed','Block all execution','implementer'),
 ('readout_invalid','Report INVALID with raw evidence; never reinterpret as PASS or FAIL','implementer'),
 ('perceive_unusable','Block G2 and G0; no primary-task substitution','implementer'),
 ('full_seed_M_unmatched','Keep seed G0-INCONCLUSIVE; never replace','implementer'),
 ('task_blind_G1_fail','Write failure report; stop development','drafter'),
 ('G0prime_fail','Write failure report; stop development','drafter'),
 ('G2_fail_or_inconclusive','Write failure or diagnosis report; stop development','drafter'),
)

def stops(flags):
    return [dict(question=k,action=a,role=r) for k,a,r in STOP_ROWS if flags.get(k,False)]
