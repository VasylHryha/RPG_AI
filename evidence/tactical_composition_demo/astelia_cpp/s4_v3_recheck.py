"""Reconstruct preserved v3 evidence and two diagnostic captures. No native execution."""
import collections
import gzip
import hashlib
import json
import math
import pathlib
import statistics
import time
import s4_v3_report as R

ROOT = pathlib.Path(__file__).resolve().parent
OUT = ROOT/'s4_v3_recheck_checks'
DATA = ROOT/'s4_v3_development'


def read(p):
    return json.loads(p.read_text())


def stats(xs):
    mean = statistics.mean(xs)
    sd = statistics.stdev(xs)
    return dict(n=len(xs), mean=mean, sd=sd, se=sd/math.sqrt(len(xs)))


def replay_analysis(path):
    """Align prepare(k) capture with pre-step trace(k-1), never post-step target/state."""
    previous = None
    current = None
    modes = {}
    changes = collections.Counter()
    aggregates = collections.defaultdict(list)
    snapshots = []
    first_only_guns = None
    initial = None
    with gzip.open(path, 'rt') as stream:
        for line in stream:
            row = json.loads(line)
            if 'state' in row:
                previous, current = current, row['state']
                if initial is None:
                    initial = current
                enemies = [u for u in current['units'] if u['alive'] and u['team']==1]
                if first_only_guns is None and enemies and all(u['role']=='artillery' for u in enemies):
                    first_only_guns = dict(t=current['t'], own_alive=sum(u['alive'] and u['team']==0 for u in current['units']), enemy_guns=len(enemies))
                if not snapshots or current['t'] >= snapshots[-1]['t']+10-1e-6:
                    alive = [u for u in current['units'] if u['alive']]
                    snapshots.append(dict(t=current['t'],counts={f'{team}|{role}':sum(u['team']==team and u['role']==role for u in alive) for team in (0,1) for role in ('melee','ranged','artillery')}))
            elif row.get('capture'):
                if previous is None:
                    raise ValueError('capture without producing snapshot')
                byid = {u['id']:u for u in previous['units']}
                for u in row['units']:
                    actual = byid[u['id']]
                    # This diagnostic reconstructs the threshold state shared by out-ranged
                    # pairs present since initialization. It does not export actual pair modes.
                    c = u['commitment']
                    prior = modes.get(u['id'], c>=0)
                    mode = True if c>.2 else False if c<-.2 else prior
                    if u['id'] in modes and prior!=mode:
                        changes[u['id']]+=1
                    modes[u['id']] = mode
                    role = actual['role']
                    window = '60plus' if previous['t']>=60 else '0to60'
                    aggregates[(window,role,'commit')].append(int(mode))
                    aggregates[(window,role,'c')].append(c)
                    aggregates[(window,role,'pressure')].append(u['pressure'])
                    if row['arm']=='resonator':
                        # Magnitude of the uncoupled instantaneous angular drive.
                        aggregates[(window,role,'free_drive')].append(abs(u['rate']+u['pressure']*math.sin(u['state'])))
                # Living pair lifecycle is independently exercised by the synthetic contract.
            else:
                terminal = row
    return dict(summary=terminal,first_enemy_artillery_only=first_only_guns,
        snapshots=snapshots,threshold_switches_by_unit=dict(changes),
        role_means={'|'.join(k):statistics.mean(v) for k,v in aggregates.items()},
        alignment='capture uses previous trace (pre-step); captures state before integration and commitment after integration',
        limitation='Threshold reconstruction is not an exported pair-mode trace. No force attribution or counterfactual performance is measured.',
        initial_units=initial['units'])


def independent_raw():
    uses = read(DATA/'s4_seeds.json')['uses']
    uses = [u for u in uses if u['candidate']!='replay_capture']
    counts = collections.Counter()
    end = collections.defaultdict(lambda:collections.Counter())
    score_sums = collections.defaultdict(float)
    world_signatures = {}
    diagnostics = {}
    tuning_seeds, validation_seeds = set(), set()
    marker = object()
    n = 0
    with gzip.open(DATA/'fights.jsonl.gz','rt') as stream:
        for n,line in enumerate(stream,1):
            u = uses[n-1]
            row = json.loads(line)
            spec, result = row['spec'], row['summary']
            if any(spec[k]!=u[k] for k in ('arm','seed','opponent','setting','swapSides')):
                raise ValueError('raw/ledger join')
            if row['cache_hit'] or result['controllerFailures']!=[0,0]:
                raise ValueError('unexpected cache/failure in fresh record')
            if any(row['metrics'][k] for k in R.COUNTERS):
                raise ValueError('planning work')
            if row['S']!=result['survivors']-result['enemySurvivors']:
                raise ValueError('survivor objective')
            counts[(u['stage'],u['split'],u['arm'])]+=1
            (tuning_seeds if u['split']=='tuning' else validation_seeds).add(spec['seed'])
            endpoint = (u['stage'],u['split'],u['arm'],spec['setting'],spec['opponent'])
            end[endpoint]['fights']+=1
            end[endpoint]['timeouts']+=result['t']>=150-1e-9
            end[endpoint]['enemy_artillery_alive']+=result['artilleryAlive'][1]
            if u['split']=='validation':
                score_sums[(u['stage'],u['arm'],spec['setting'],spec['opponent'],spec['seed'])]+=row['S']/2
            # Independent cross-arm world equality, stripping only controlled controller profile.
            req=json.loads(json.dumps(row['request']))
            controlled=req['options']['ai'][0]
            if set(controlled)!={'controller','params','skeleton'} or controlled['controller']!=spec['arm'] or controlled['skeleton']!='v3':
                raise ValueError('controlled profile')
            req['options']['ai'][0]={'controller':'<arm>','params':'<selected knobs>','skeleton':'v3'}
            signature=json.dumps(req,sort_keys=True)
            key=(u['stage'],u['split'],spec['opponent'],spec['seed'],spec['setting'],spec['swapSides'])
            prior=world_signatures.get(key,marker)
            if prior is not marker and prior!=signature:
                raise ValueError('unequal cross-arm world conditions')
            world_signatures[key]=signature
            if u['split']=='validation' and spec['seed']==712101000 and spec['opponent']=='regular' and not spec['swapSides'] and spec['arm'] in ('resonator','morale'):
                diagnostics[spec['arm']]=result
    if n!=len(uses) or tuning_seeds&validation_seeds:
        raise ValueError('count or seed leakage')
    for stage in 'ABC':
        for arm in ('resonator','morale','pushpull'):
            if counts[(stage,'tuning',arm)]!=9766:
                raise ValueError('unequal budgets')
        validation=read(DATA/f'{stage}_validation.json')['results']
        for arm,endpoints in validation.items():
            for endpoint,record in endpoints.items():
                setting,opponent=endpoint.split('|')
                scores=record['scores']
                xs=[]
                for key,value in scores.items():
                    opp,seed,sett=json.loads(key)
                    actual=score_sums[(stage,arm,sett,opp,seed)]
                    if actual!=value:
                        raise ValueError('validation score disagreement')
                    xs.append(actual)
                computed=stats(xs)
                for field in computed:
                    if not math.isclose(computed[field],record['stats'][field],abs_tol=1e-12):
                        raise ValueError('independent validation arithmetic')
                d=end[(stage,'validation',arm,setting,opponent)]
                recorded=read(DATA/'VALIDATION_END_STATES.json')[stage][arm][endpoint]
                if any(d[k]!=recorded[k] for k in d):
                    raise ValueError('independent end-state disagreement')
    return dict(raw_fights=n,tuning_seed_count=len(tuning_seeds),validation_seed_count=len(validation_seeds),
        cross_arm_world_signatures=len(world_signatures),budgets={'|'.join(k):v for k,v in counts.items()},
        diagnostics=diagnostics)


def planning_check():
    p=read(DATA/'POWER_PLANNING.json')
    ends=p['endpoints']
    delta=math.ceil(max(1,.25*max(ends[e]['configuration_cluster']['sd'] for e in ('P2','P3')))*2)/2
    z=statistics.NormalDist().inv_cdf(.9975)+statistics.NormalDist().inv_cdf(.90)
    required={}
    for endpoint in ('P2','P3'):
        e=ends[endpoint]
        variance=max(e['seed_block_sd_upper']**2,e['development_sd_upper']**2/19,e['stratum_variance_floor'])
        required[endpoint]=max(16,math.ceil(z*z*variance/delta**2))
        if not math.isclose(variance,e['variance_used']) or required[endpoint]!=e['n_per_doctrine']:
            raise ValueError('paired planning arithmetic')
    ns=[]
    for e in ends['P1']['subtests'].values():
        ns.append(max(32,math.ceil(z*z*max(e['validation_sd_upper'],e['development_sd_upper'])**2/delta**2)))
        if ns[-1]!=e['required_n']:
            raise ValueError('head planning arithmetic')
    required['P1']=max(ns)
    if required['P1']!=ends['P1']['n_per_head'] or delta!=p['delta_proposed']:
        raise ValueError('head count or delta')
    # At the floor n=16, true SD is estimated, so the known-variance normal rule
    # is not by itself a calibrated .90 power guarantee for a future t/bootstrap test.
    return dict(delta=delta,n=required,zsum_squared=z*z,bootstrap_repeated=False,
        limitation='Checks recorded bootstrap-derived spreads and normal arithmetic; does not certify bootstrap coverage or finite-sample power.')


def main():
    started=time.monotonic()
    preserved={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(DATA.rglob('*')) if p.is_file()}
    for p in (ROOT/'s4_v3_checks').iterdir():
        if p.is_file() and p.suffix!='.bundle':preserved[str(p.relative_to(ROOT))]=hashlib.sha256(p.read_bytes()).hexdigest()
    # Original reconstruction runs unchanged, but writes only to NEW recheck artifacts.
    original_write=R.write
    R.write=lambda path,value:original_write(OUT/('RECONSTRUCTED_'+path.name),value)
    try: reconstructed=R.audit()
    finally:R.write=original_write
    independent=independent_raw()
    equality={}
    replays={}
    for arm in ('resonator','morale'):
        path=OUT/'replays'/f'C_regular_{arm}.jsonl.gz'
        replays[arm]=replay_analysis(path)
        equality[arm]=replays[arm]['summary']==independent['diagnostics'][arm]
        if not equality[arm]:raise ValueError('diagnostic replay differs from original orientation')
    if replays['resonator']['initial_units']!=replays['morale']['initial_units']:
        raise ValueError('diagnostic initial worlds differ')
    for entry in replays.values():del entry['initial_units']
    for name,expected in preserved.items():
        if hashlib.sha256((ROOT/name).read_bytes()).hexdigest()!=expected:
            raise ValueError('recorded bytes changed: '+name)
    result=dict(status='PASS',preserved_hashes=preserved,original_reconstruction=reconstructed,
        independent=independent,planning=planning_check(),diagnostic_equality=equality,replay_analysis=replays,
        elapsed_seconds=time.monotonic()-started,workers=1,tuning_runs=0,new_fights=0)
    original_write(OUT/'ANALYSIS.json',result)
    print(json.dumps({k:result[k] for k in ('status','diagnostic_equality','planning','elapsed_seconds')},indent=2))


if __name__=='__main__':main()
