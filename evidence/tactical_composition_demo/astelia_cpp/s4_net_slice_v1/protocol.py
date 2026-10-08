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
    """No flattening: exact equal trajectory caps per visitor; only training groups."""
    rows=[]
    for round_id in (0,1,2):
        peers={a:sorted([t for t in trajectories if t['round']==round_id and t['visitor']==a and split(t['group'])=='train'],key=lambda t:t['group']) for a in ARMS}
        limit=min(map(len,peers.values()))
        for arm in ARMS:
            for t in peers[arm][:limit]:rows.append({**t,'weight':1/3,'round_weight':1/3})
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
    """Diagonal, antithetic, centered-rank ES; no covariance or CMA claim."""
    def __init__(self,seed,dimension=16):
        self.rng=random.Random(seed);self.mean=[0.]*dimension;self.generation=0
    def candidates(self):
        if self.generation>=20:raise ValueError('ES cap')
        noise=[[self.rng.gauss(0,1) for _ in self.mean] for _ in range(8)]
        noise=[v for e in noise for v in (e,[-x for x in e])]
        self.noise=noise
        return [[min(2,max(-2,m+.1*z)) for m,z in zip(self.mean,e)] for e in noise]
    def update(self,rows):
        if len(rows)!=16 or not hasattr(self,'noise'):raise ValueError('16 candidates required')
        u=rank_utilities(rows)
        self.mean=[min(2,max(-2,m+.05*sum(v*e[j] for v,e in zip(u,self.noise))/(16*.1))) for j,m in enumerate(self.mean)]
        self.generation+=1;del self.noise

def paired_interval(differences,alpha=.05/9):
    """Distribution-free bounded paired Hoeffding interval for normalized [-1,1] contrasts.
    Three metrics times three looks Bonferroni; conservative on purpose."""
    if not differences or any(not math.isfinite(x) or abs(x)>1 for x in differences):raise ValueError('bounded paired contrast')
    mean=sum(differences)/len(differences);radius=math.sqrt(2*math.log(2/alpha)/len(differences))
    return max(-1,mean-radius),min(1,mean+radius)

def reading(n,survival,offense,participation,margin=.1):
    if n not in (50,100,200):raise ValueError('registered looks only')
    intervals=[paired_interval(x) for x in (survival,offense,participation)]
    if any(len(x)!=n for x in (survival,offense,participation)):raise ValueError('paired count')
    if any(hi < -margin for lo,hi in intervals):return 'NEGATIVE',intervals
    if all(lo>=-margin for lo,hi in intervals) and any(lo>margin for lo,hi in intervals):return 'POSITIVE',intervals
    if all(lo>=-margin for lo,hi in intervals):return 'NONINFERIOR',intervals
    return ('PARK' if n==200 else 'CONTINUE'),intervals
