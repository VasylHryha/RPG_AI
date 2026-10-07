"""Sealed §20.2 rules; pure fake-record checks never execute the engine."""
import math, random
BOUNDS=dict(K=(0,5),K_t=(0,5),kappa=(0,50),beta=(0,3),G=(0,5),w=(0,3),f_c=(.3,1),m_k=(.2,1),lambda_th=(0,3),mu=(-2,2),omega_ranged=(-2,2))
ARMS=('v7','forcedP16','forcedv6','omega0','historicalP16')
HEADS=('regular','novice')
POPULATION=16; GENERATIONS=16; EVALUATIONS=257; FIGHTS=8224+400

def normalized(params):
 if set(params)!=set(BOUNDS):raise ValueError('knob ledger mismatch')
 x=[(params[k]-a)/(b-a) for k,(a,b) in BOUNDS.items()]
 if any(not math.isfinite(v) or not 0<=v<=1 for v in x):raise ValueError('knob bounds')
 return x

def knobs(x):
 if len(x)!=len(BOUNDS) or any(not math.isfinite(float(v)) or not 0<=v<=1 for v in x):raise ValueError('normalized bounds')
 return {k:float(a+float(v)*(b-a)) for v,(k,(a,b)) in zip(x,BOUNDS.items())}

def measure(summary):
 if summary.get('controllerStatus')!='completed' or any(summary.get('controllerFailures',[1])) or summary.get('complexDiagnostics',{}).get('numericalFailureTicks',1):raise ValueError('failure row; never score')
 own,enemy,t=(summary[k] for k in ('survivors','enemySurvivors','t'))
 if any(not math.isfinite(v) for v in (own,enemy,t)) or not 0<=own<=50 or not 0<=enemy<=50 or own!=int(own) or enemy!=int(enemy) or not 0<=t<=150+1/30+1e-8:raise ValueError('invalid end state')
 return dict(win=int(enemy==0 and own>=1 and t<150),timeout=int(t>=150),termination_time=t,S=own-enemy,losses=50-own)

def selection(rows,ordinal):
 if len(rows)!=32 or type(ordinal) is not int or ordinal<0:raise ValueError('candidate allocation')
 expected={(h,c,o) for h in HEADS for c in range(8) for o in (0,1)}
 if {(r['head'],r['cluster'],r['orientation']) for r in rows}!=expected:raise ValueError('candidate cells')
 cells={h:[measure(r['summary']) for r in rows if r['head']==h] for h in HEADS}
 regular=cells['regular'];novice=cells['novice'];eligible=sum(r['win'] for r in novice)>=8
 return dict(ordinal=ordinal,eligible=eligible,regular_wins=sum(r['win'] for r in regular),regular_S=sum(r['S'] for r in regular)/16,regular_losses=sum(r['losses'] for r in regular)/16,novice_wins=sum(r['win'] for r in novice))

def rank(r):
 return (-int(r['eligible']),-r['regular_wins'],-r['regular_S'],r['regular_losses'],r['ordinal'])

def cma_losses(records):
 order=sorted(range(len(records)),key=lambda i:rank(records[i]));losses=[0]*len(records)
 for loss,i in enumerate(order):losses[i]=loss
 return losses

def readings(regular,novice,comparator,failures=0):
 if not all(math.isfinite(x) for x in (regular['mean_S'],novice['mean_S'])):raise ValueError('nonfinite reading')
 diff=regular['wins']-comparator['wins'];floor=comparator['wins']>=21
 return dict(relative='the panel does not support a comparison' if not floor else 'Observed improvement' if diff>=4 else 'Observed worse' if diff<=-4 else 'Observed match',comparator_underperformance=not floor,win_difference=diff,observed_owner_criterion=regular['wins']>=21 and novice['wins']>=21 and regular['mean_S']>0 and novice['mean_S']>0 and failures==0,descriptive_only=True,S5_authorized=False)

def bootstrap(differences):
 if len(differences)!=20 or any(d not in (-1,-.5,0,.5,1) for d in differences):raise ValueError('paired cluster allocation')
 rng=random.Random(20261007)
 values=sorted(sum(rng.choice(differences) for _ in range(20))/20 for _ in range(10000))
 def percentile(q):
  i=9999*q;lo=int(i);hi=min(lo+1,9999);return values[lo]+(i-lo)*(values[hi]-values[lo])
 return dict(seed=20261007,resamples=10000,unit='paired two-orientation cluster',construction='95% percentile; linear interpolation at (n-1)*q',low=percentile(.025),high=percentile(.975),mean=sum(differences)/20)
