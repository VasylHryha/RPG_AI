"""Pure contracts for splits, DAgger, optimizer ranks, and prospective readings."""
import hashlib
import math
import random

DAGGER_ROUNDS=2
ARMS=('N1','N1r','N2')

def split(group):
    # group is a whole fight or entire series identity, before any windows.
    n=int(hashlib.sha256(('NS1-split:'+group).encode()).hexdigest(),16)%10
    return 'train' if n<7 else 'validation' if n<9 else 'test'

def aggregate(trajectories):
    """Keep whole trajectories. Weight each gun-decision row, not each trajectory."""
    rows=[]
    for round_id in (0,1,2):
        visitors=('teacher',) if round_id==0 else ARMS
        for visitor in visitors:
            pool=sorted((t for t in trajectories if t['round']==round_id and t['visitor']==visitor and split(t['group'])=='train'),key=lambda t:t['group'])
            if not pool:raise ValueError(f'empty training stratum {round_id}/{visitor}')
            if any(type(t.get('decision_rows')) is not int or t['decision_rows']<=0 for t in pool):raise ValueError('positive gun-decision row count required')
            total=sum(t['decision_rows'] for t in pool)
            for t in pool:rows.append({**t,'weight':1/(3*len(visitors)*total),'round_weight':1/3})
    return rows

def eligibility(row):
    # Explicit training surrogate guard. 150s timeout / no enemy kills is ineligible.
    return row['opportunities']>0 and row['launches']/row['opportunities']>=.25 and row['enemy_kills']>0 and row['completed']>=8

def rank(row):
    if not eligibility(row):return (1,0,0,0,0)
    deaths=row['own_gun_deaths'];kills=row['enemy_kills']
    # Null is incomparable as a ratio: zero deaths handled by raw kills/time instead.
    exchange=kills/deaths if deaths else None
    return (0,deaths,0 if exchange is None else 1,-kills if exchange is None else -exchange,-kills/max(row['seconds'],1e-9))

def rank_utilities(rows):
    keys=[rank(r) for r in rows];ordered=sorted(set(keys));ranks={k:ordered.index(k) for k in ordered}
    # Exact ties receive exactly equal utility. No candidate-index tiebreak for fitness.
    raw=[-ranks[k] for k in keys];mean=sum(raw)/len(raw);scale=max(1,max(raw)-min(raw))
    return [(x-mean)/scale for x in raw]

class SliceES:
    """Antithetic ES + evaluated incumbent; every generation uses ten common draws."""
    def __init__(self,seed,dimension=16):
        self.rng=random.Random(seed);self.mean=[0.]*dimension;self.incumbent=self.mean[:];self.generation=0
    def candidates(self,panel):
        if self.generation>=20 or hasattr(self,'noise'):raise ValueError('ES cap/pending generation')
        self.panel=tuple(panel)
        if len(self.panel)!=10 or len(set(self.panel))!=10:raise ValueError('ten unique common draws required')
        noise=[[self.rng.gauss(0,1) for _ in self.mean] for _ in range(8)]
        noise=[v for e in noise for v in (e,[-x for x in e])]
        self.evaluated=[[min(2,max(-2,m+.1*z)) for m,z in zip(self.mean,e)] for e in noise]
        # Gradient uses actual evaluated (clipped) perturbations.
        self.noise=[[(x-m)/.1 for x,m in zip(c,self.mean)] for c in self.evaluated]
        return [v[:] for v in self.evaluated]
    def update(self,rows,incumbent_row,panel):
        if len(rows)!=16 or not hasattr(self,'noise') or tuple(panel)!=self.panel:raise ValueError('matched pending panel required')
        if any(tuple(r.get('panel_ids',()))!=self.panel for r in [*rows,incumbent_row]):raise ValueError('unmatched evaluation panel')
        u=rank_utilities(rows)
        self.mean=[min(2,max(-2,m+.05*sum(v*e[j] for v,e in zip(u,self.noise))/(16*.1))) for j,m in enumerate(self.mean)]
        best=min(range(16),key=lambda i:rank(rows[i]))
        retained=True
        if rank(rows[best])<rank(incumbent_row) and rows[best]['own_gun_deaths']<=incumbent_row['own_gun_deaths']:
            self.incumbent=self.evaluated[best][:];retained=False
        self.generation+=1;del self.noise
        return {'retained':retained,'incumbent':self.incumbent[:],'panel':self.panel}


def es_generation(engines,panel,evaluate):
    """Value-only harness; caller supplies admitted evaluator and sealed draw IDs."""
    panel=tuple(panel);out={}
    for arm,es in engines.items():
        candidates=es.candidates(panel)
        rows=[evaluate(arm,c,panel) for c in candidates]
        incumbent=evaluate(arm,es.incumbent[:],panel)
        out[arm]=es.update(rows,incumbent,panel)
    return out


# Unequal discrete group-sequential alpha spending. Sum=.05 per comparison.
# Split each look's increment equally across the TWO primary axes; two-sided CIs.
# Union bound is valid for dependent nested looks. Stop on first terminal reading.
LOOK_SPEND={50:.005,100:.015,200:.030}
PRIMARY_ORDER=('survival','offense')


def t_critical(df,alpha):
    """Student-t inverse survival by incomplete beta; locked mpmath dependency."""
    import mpmath as mp
    with mp.workdps(35):
        lo=mp.mpf(0);hi=mp.mpf(32)
        def tail(x):return mp.betainc(mp.mpf(df)/2,mp.mpf('.5'),0,df/(df+x*x),regularized=True)/2
        while tail(hi)>alpha/2:hi*=2
        for _ in range(110):
            mid=(lo+hi)/2
            if tail(mid)>alpha/2:lo=mid
            else:hi=mid
        return float((lo+hi)/2)


def paired_interval(differences,alpha):
    """Paired t on whole-draw contrasts; approximate under nonnormal contrasts."""
    if len(differences)<2 or not 0<alpha<1 or any(not math.isfinite(x) or abs(x)>1 for x in differences):raise ValueError('bounded paired contrast')
    n=len(differences);mean=sum(differences)/n
    variance=sum((x-mean)**2 for x in differences)/(n-1)
    radius=t_critical(n-1,alpha)*math.sqrt(variance/n)
    return max(-1,mean-radius),min(1,mean+radius)


def reading(n,survival,offense,participation,margin=.1):
    if n not in LOOK_SPEND or margin!=.1:raise ValueError('registered looks/margin only')
    if any(len(x)!=n for x in (survival,offense,participation)):raise ValueError('paired count')
    if any(not math.isfinite(x) or abs(x)>1 for x in participation):raise ValueError('participation diagnostic')
    intervals=[paired_interval(x,LOOK_SPEND[n]/2) for x in (survival,offense)]
    if any(hi < -margin for lo,hi in intervals):return 'NEGATIVE',intervals
    if all(lo>=-margin for lo,hi in intervals) and any(lo>margin for lo,hi in intervals):return 'POSITIVE',intervals
    if all(lo>=-margin for lo,hi in intervals):return 'NONINFERIOR',intervals
    return ('PARK' if n==200 else 'CONTINUE'),intervals
