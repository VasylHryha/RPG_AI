"""Stored-data audit only. No project imports, native images, pilots or simulations.

Verify all raw identities before decoding anything; regenerate the new audit JSON.
The mutable PLAN_CURRENT.md is deliberately excluded from every identity manifest.
"""
from collections import Counter
import gzip
import hashlib
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent
ERRORS = []


def sha(p):
    h = hashlib.sha256()
    with p.open('rb') as f:
        for chunk in iter(lambda: f.read(1048576), b''):
            h.update(chunk)
    return h.hexdigest()


def check(value, expected, label):
    if value != expected:
        ERRORS.append(dict(check=label, actual=value, expected=expected))


def legacy_summary(d):
    st = d['steps']; late = [x for x in st if x['t'] > 640]
    conn = sum(len(set(x['paths']) & set(x['active'])) / max(1, len(x['active'])) for x in late) / max(1, len(late))
    best = cur = 0; span = None; first = None
    for x in st:
        if x['paths']:
            if not cur: first = x['t']
            cur += 1
            if cur > best: best = cur; span = [first, x['t']]
        else: cur = 0
    return dict(start=d['start'], tag=d['tag'], steps=len(st), last_t=st[-1]['t'],
                late_connectivity=round(conn, 3), present=sum(bool(x['paths']) for x in st),
                longest_any_site=[span, best], final_n=st[-1]['n'], O=st[-1]['O'],
                births={k: sum(x['rule'] == k for x in d['events']) for k in ('B-out', 'B-path', 'B1')},
                final_dO=st[-1]['dO'], keyset=d['keyset'], assay=d['assay'])


def main():
    coverage = json.loads((OUT/'COVERAGE_RUN_SUMMARIES.json').read_text())
    service = json.loads((OUT/'SERVICE_RUN_SUMMARIES.json').read_text())
    compact = json.loads((OUT/'COVERAGE_COMPACT_SUMMARIES.json').read_text())
    inventories = {}
    # Integrity precedes every gzip decode.
    for name, receipt in [('coverage', coverage), ('service', service)]:
        total = 0
        for raw in receipt['raw_inventory']:
            p = OUT/raw['path']
            assert not p.is_symlink() and p.resolve().is_relative_to((OUT/'_local').resolve())
            assert p.stat().st_size == raw['bytes'] and sha(p) == raw['sha256'], str(p)
            total += raw['bytes']
        inventories[name] = dict(entries=len(receipt['raw_inventory']), bytes=total, status='PASS')
    tickets = sorted((OUT/'_local/coverage').glob('RUN_TICKET_*.json'))
    td = [json.loads(p.read_text()) for p in tickets]
    baseline = coverage['timing']['code_hashes']
    assert not any(Path(p).name == 'PLAN_CURRENT.md' for p in baseline)
    for p, h in baseline.items(): check(sha(Path(p)), h, 'pinned code '+p)
    for d in td: check(d['code_hashes'], baseline, 'ticket code baseline')
    jobs = {(v,s,k,o) for v in ('COVA','COVB') for s in ('i','ii') for k in range(5) for o in ('on',)} | {(v,'i',0,'off') for v in ('COVA','COVB')}
    check({(r['variant'],r['start'],r['keyset'],r['observer']) for r in coverage['runs']}, jobs, 'complete slot set')
    check(len(coverage['runs']),22,'unique slot count')
    starts = Counter(); decoded = []
    for r in coverage['runs']:
        name = f"{r['variant']}_{r['start']}_k{r['keyset']}_{r['observer']}"
        check(json.loads((OUT/'_local/coverage'/(name+'.summary.json')).read_text()),r,'local completion '+name)
        marker = json.loads((OUT/'_local/coverage'/(name+'.started')).read_text())
        starts[Path(marker['ticket']).name] += 1
        check([marker[k] for k in ('variant','start','keyset','observer')],[r[k] for k in ('variant','start','keyset','observer')],'marker slot '+name)
        check(r['code_hashes'],baseline,'completion code '+name)
        check(r['clone_isolation'],'PASS','clone '+name)
        for raw in r['raw_traces']:
            p = OUT/raw['path']; check(p.stat().st_size,raw['bytes'],'raw size '+name);check(sha(p),raw['sha256'],'raw hash '+name)
            if raw['path'].endswith('.legacy.json.gz'):
                with gzip.open(p,'rt') as f: legacy = json.load(f)
                check(legacy_summary(legacy),r['summary'],'legacy summary '+name)
                check(legacy['pin_sha256'],'SCRATCH:'+r['binary_sha256'],'binary pin '+name)
            else:
                with gzip.open(p,'rt') as f: trace = [json.loads(x) for x in f]
                decoded.append((r,trace))
    resumed = td[-1]['reused']; check(len(resumed),20,'resume verified reuse count')
    expected_new = {'COVB_ii_k3_on','COVB_ii_k4_on'}
    check({f'{v}_{s}_k{k}_{o}' for v,s,k,o in jobs} - set(resumed),expected_new,'only never-started resume slots')
    check(starts,Counter({tickets[0].name:20,tickets[1].name:2}),'ticket slot partition')
    for v in ('COVA','COVB'):
        pair = {r['observer']:r for r in coverage['runs'] if (r['variant'],r['start'],r['keyset'])==(v,'i',0)}
        check(pair['on']['state_trajectory_sha256'],pair['off']['state_trajectory_sha256'],'full on/off digest '+v)
        check(pair['on']['summary'],pair['off']['summary'],'on/off summary '+v)
    for r in service['runs']:
        if r['variant'] != 'RD3': continue
        for raw in r['raw_traces']:
            p=OUT/raw['path']
            if raw['path'].endswith('.legacy.json.gz'):
                with gzip.open(p,'rt') as f: legacy=json.load(f)
                check(legacy_summary(legacy),r['summary'],'RD3 legacy summary '+r['start']+'/'+str(r['keyset']))
            else:
                with gzip.open(p,'rt') as f: trace=[json.loads(x) for x in f]
                decoded.append((r,trace))
    run_audits = []; birth_audits = {}
    for r,trace in decoded:
        t = r['telemetry'];name = f"{r['variant']}_{r['start']}_k{r['keyset']}"
        world = [x for x in trace if x['kind']=='world_step']; outages = [dict(x) for x in trace if x['kind']=='outage']
        for x in outages:x.pop('kind')
        check(outages,t['outages'],'raw outages '+name)
        check(len(world),8000,'world count '+name)
        for s in range(8):
            active = sum(s in x['active'] for x in world); served = sum(s in x['active_served'] for x in world);all_served=sum(s in x['served'] for x in world)
            check(t['sites'][str(s)],dict(active_steps=active,active_served_steps=served,served_fraction_active=served/active if active else None,served_fraction_all=all_served/len(world),ever_served=all_served>0),'raw site census '+name+'/'+str(s))
        degree = Counter()
        for x in world:degree.update({str(k):v for k,v in x['realized_degrees'].items()})
        check(dict(degree),t['realized_degree_distribution'],'raw degree '+name)
        for field,kind in [('requests','birth_request'),('terminals','birth_terminal')]:
            rows=[{k:v for k,v in x.items() if k!='kind'} for x in trace if x['kind']=='event' and x['rule']==kind]
            if field in t:check(rows,t[field],'raw '+field+' '+name)
        check(len(outages),t['outage_count'],'outage count '+name)
        check({k:sum(x['break_cause']==k for x in outages) for k in ('D3','D1','D4','G-dist','G-deg','R','X')},t['break_causes'],'break census '+name)
        check({k:sum(k in x['non_repair_labels'] for x in outages) for k in ('S','C','N','B','G','X')},t['non_repair_causes'],'label census '+name)
        check([x['duration'] for x in outages if not x['censored']],t['repair_latencies'],'latencies '+name)
        check([x['duration'] for x in outages if x['censored']],t['latency_censored'],'censored latencies '+name)
        check(max((x['duration'] for x in outages),default=0.),t['maximum_outage'],'maximum outage '+name)
        removals=[{k:v for k,v in x.items() if k!='kind'} for x in trace if x['kind']=='removal']
        check(removals,t['removals'],'raw removals '+name)
        check(dict(Counter(x['service_class'] for x in removals if x['rule']=='D3')),t['d3_removals_by_class'],'raw D3 classes '+name)
        terminals=[x for x in trace if x['kind']=='event' and x['rule']=='birth_terminal']
        initials=[{k:v for k,v in x.items() if k!='kind'} for x in trace if x['kind']=='initial_cost_refusal']
        recycles=[]
        for x in [x for x in trace if x['kind']=='recycle']:
            x={k:v for k,v in x.items() if k!='kind'}
            posts=[y for y in trace if y['kind']=='post_birth_gap' and y['site']==x['site'] and y['restoring'] and x['t']<=y['t']<=x['t']+60]
            served=[y['t'] for y in world if x['t']<=y['t']<=x['t']+60 and x['site'] in y['served']]+[y['t'] for y in posts]
            # An accepted retry may itself create immediate service without an outage.
            terminal=next(y for y in terminals if y['request']==x['request'])
            check(terminal['outcome'],x['retry_outcome'],'single retry terminal '+name)
            check(x['age_steps']>=200,True,'recycle age '+name)
            check(x['donor_class'],'non-service','recycle donor class '+name)
            x['first_served_t']=min(served,default=None) if x['retry_outcome']=='accepted' else None
            x['served_within_60s']=('YES' if x['first_served_t'] is not None else 'CENSORED' if 800<x['t']+60 else 'NO') if x['retry_outcome']=='accepted' else 'NOT_APPLICABLE'
            recycles.append(x)
        if r['variant']!='RD3':
            check(initials,t['initial_cost_refusals'],'raw initial refusals '+name)
            check(recycles,t['recycles'],'raw retry 60-second outcomes '+name)
            check(max(Counter(x['t'] for x in recycles).values(),default=0)<=1,True,'one recycle per check '+name)
        outcomes=('quota','cost','accepted','no_root','deferred_output_first','recycle_failed','cap','placement','exhausted','no_output')
        counts={str(s):Counter(x['outcome'] for x in terminals if x.get('site')==s) for s in range(8)}
        cost=[x['t'] for x in terminals if x['outcome']=='cost' or x.get('initial_cost_refusal')]+[x['t'] for x in initials]
        birth_audits[name]=dict(start=r['start'],keyset=r['keyset'],births_per_site={s:c['accepted'] for s,c in counts.items()},
                               request_outcomes_per_site={s:{k:c[k] for k in outcomes} for s,c in counts.items()},
                               first_cost_refusal_t=min(cost,default=None),initial_cost_refusals=initials,recycles=recycles)
        b_count = 0
        for o in outages if r['variant']!='RD3' else []:
            posts=[x for x in trace if x['kind']=='post_birth_gap' and x['site']==o['site'] and x['outage_start']==o['start']]
            check([{k:v for k,v in x.items() if k not in ('kind','site','outage_start','request')} for x in posts if x['restoring']],o['restoration_evidence'],'restoration exclusion '+name)
            gaps=[x['gap'] for x in posts if not x['restoring'] and x['gap'] is not None]
            gaps += [x['gaps'][str(o['site'])] for x in world if o['start']<=x['t']<o['end'] and x['gaps'][str(o['site'])] is not None]
            if o['initial_gap'] is not None:gaps.append(o['initial_gap'])
            born = [x for x in posts if not x['restoring']]
            shrank = bool(gaps) if o['initial_gap'] is None else bool(gaps) and min(gaps)<o['initial_gap']
            b = o['duration']>20 and bool(born) and not shrank
            check('B' in o['non_repair_labels'],b,'independent revised B '+name+'/'+str(o['site'])+'/'+str(o['start']))
            b_count += b
            for x in posts: check(x['weight'],0,'zero endpoint duration weight '+name)
        run_audits.append(dict(run=name,world_steps=len(world),outages=len(outages),independently_reconstructed_B=b_count if r['variant']!='RD3' else 'legacy_B'))
    cohorts = [('RD3',[r for r in service['runs'] if r['variant']=='RD3'],compact['control'])]+[(v,[r for r in coverage['runs'] if r['variant']==v and r['observer']=='on'],compact['arms'][v]) for v in ('COVA','COVB')]
    for v,rows,c in cohorts:
        for s in range(8):
            a=sum(r['telemetry']['sites'][str(s)]['active_steps'] for r in rows);b=sum(r['telemetry']['sites'][str(s)]['active_served_steps'] for r in rows)
            expected=dict(active_steps=a,active_served_steps=b,fraction=b/a,per_run=[dict(start=r['start'],keyset=r['keyset'],fraction=r['telemetry']['sites'][str(s)]['served_fraction_active']) for r in rows])
            check(c['sites'][str(s)],expected,'compact site '+v+'/'+str(s))
        a=sum(c['sites'][str(s)]['active_steps'] for s in range(3,7));b=sum(c['sites'][str(s)]['active_served_steps'] for s in range(3,7))
        check([c['pooled_3_6_active_steps'],c['pooled_3_6_served_steps'],c['pooled_3_6']],[a,b,b/a],'pooled '+v)
        expected=[]
        for r in rows:
            assay=r['summary']['assay'];gate=assay['A']>=.3 and assay['B']>=.3 and max(assay['E'])>=.5
            expected.append(dict(start=r['start'],keyset=r['keyset'],assay=assay,gate_shape_pass=gate,sites_served_at_least_50_percent=sum((r['telemetry']['sites'][str(s)]['served_fraction_active'] or 0)>=.5 for s in range(8))))
        check(c['runs'],expected,'per-run assay/gates '+v)
        check(c['births_per_run'],[birth_audits[f"{v}_{r['start']}_k{r['keyset']}"] for r in rows],'compact birth metrics '+v)
        check(c['outage_count'],sum(r['telemetry']['outage_count'] for r in rows),'compact outage count '+v)
        for field in ('break_causes','d3_removals_by_class','non_repair_causes'):
            counts=Counter()
            for r in rows:counts.update(r['telemetry'][field])
            if field=='non_repair_causes' and v=='RD3':counts['legacy_B']=counts.pop('B',0)
            check(c[field],dict(counts),'compact '+field+' '+v)
        if v=='COVB':
            recycles=[dict(start=r['start'],keyset=r['keyset'],**x) for r in rows for x in birth_audits[f"{v}_{r['start']}_k{r['keyset']}"]['recycles']]
            check(c['recycles'],recycles,'compact recycles')
            check(c['recycle_count'],len(recycles),'compact recycle count')
            check(c['recycled_classes'],dict(Counter(x['donor_class'] for x in recycles)),'compact recycle classes')
        for start in ('i','ii'):check(c['gate_shape'][start],dict(passes=sum(x['gate_shape_pass'] for x in expected if x['start']==start),runs=5),'gate totals '+v+'/'+start)
        if v!='RD3':check(c['reading'],'DESCRIPTIVE' if c['gate_shape']['i']['passes']>3 and c['pooled_3_6']<2*compact['control']['pooled_3_6'] else 'OTHER','Amendment reading '+v)
    result=dict(status='PASS' if not ERRORS else 'FAIL',mode='STORED_DATA_ONLY',reviewed_commit='e4c6d75',
                inventory_verified=inventories,code_files_verified=len(baseline),slot_count=22,
                ticket_partition=dict(starts),resume_reused=20,resume_new=sorted(expected_new),
                tickets=[dict(file=p.name,status=d['status'],deadline_seconds=d['deadline_epoch']-d['started_epoch'],elapsed_seconds=d['elapsed_seconds'],stop_reason=d.get('stop_reason')) for p,d in zip(tickets,td)],
                run_audits=run_audits,errors=ERRORS,
                limits=['Assay A/B/E match archived aggregates; assay decision streams were not retained.',
                        'Exclusive slot markers and logs corroborate once-only starts; they are not an OS process census.',
                        'Original RUNNING ticket bytes were overwritten by final scheduler status; completion ticket_sha256 cannot be rederived from final ticket bytes.',
                        'RD3 legacy_B remains separate; its missing per-birth boundaries cannot be recreated.'])
    (OUT/'COVERAGE_RECHECK_VERIFICATION.json').write_text(json.dumps(result,indent=2,default=lambda x:sorted(x) if isinstance(x,set) else dict(x))+'\n')
    print(json.dumps(dict(status=result['status'],errors=len(ERRORS),inventories=inventories)))
    return 0 if not ERRORS else 1


if __name__=='__main__':raise SystemExit(main())
