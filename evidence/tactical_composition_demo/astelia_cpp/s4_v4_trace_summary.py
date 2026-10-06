"""Descriptive replay diagnostics. No policy access, tuning, or additional combat."""
import collections
import gzip
import json
import statistics
from s4_development import ROOT,write


def summarize(records):
    counts=collections.Counter();undefined=collections.Counter();cosines=[];ended=[];planned=[];prior={};exposure=0
    for tick in records:
        exposure+=len(tick['units'])*tick['dt']/60
        live={(u['id'],p['enemy']) for u in tick['units'] for p in u['pairs']}
        prior={k:v for k,v in prior.items() if k in live}
        for event in tick['holdEvents']:
            counts['holds_'+event['reason']]+=1
            if event['reason']=='started':planned.append(event['planned'])
            else:ended.append(event['duration'])
        for u in tick['units']:
            counts['unit_ticks']+=1;counts['focus_ticks']+=u['focus'] is not None
            counts['reference_ticks']+=u['reference'] is not None
            switched=False
            for p in u['pairs']:
                key=(u['id'],p['enemy']);mode=p['mode'];counts['pair_ticks']+=1
                counts['held_pair_ticks']+=p['remainingHold']>0
                counts['committed_pair_ticks']+=mode=='commit'
                if key in prior and prior[key]!=mode:counts['pair_reversals']+=1;switched=True
                prior[key]=mode
            counts['unit_reversal_ticks']+=switched
            if u['feasibility'] is None:undefined[u['undefinedReason']]+=1
            else:
                value=u['feasibility']
                if not -1<=value<=1:raise ValueError('invalid cosine')
                cosines.append(value)
    last=records[-1] if records else {'units':[]}
    censored=sum(p['remainingHold']>0 for u in last['units'] for p in u['pairs'])
    return dict(counts=dict(counts),unit_minutes=exposure,
        commitment_reversals_per_unit_minute=counts['unit_reversal_ticks']/exposure if exposure else None,
        pair_reversals_per_unit_minute=counts['pair_reversals']/exposure if exposure else None,
        mean_completed_hold_seconds=statistics.mean(ended) if ended else None,
        mean_planned_hold_seconds=statistics.mean(planned) if planned else None,
        censored_holds_at_terminal=censored,focus_usage=counts['focus_ticks']/counts['unit_ticks'] if counts['unit_ticks'] else None,
        feasibility=dict(defined=len(cosines),undefined=dict(undefined),mean=statistics.mean(cosines) if cosines else None,
            distribution=dict(negative=sum(x<0 for x in cosines),zero=sum(x==0 for x in cosines),positive=sum(x>0 for x in cosines)),
            quantiles=statistics.quantiles(cosines,n=4) if len(cosines)>=2 else []))


def historical_v3():
    # Same per-unit threshold reconstruction used by the recheck. These are historical,
    # unmatched trajectories/knobs, not counterfactual v3 fights on fresh v4 seeds.
    result={}
    paths=sorted((ROOT/'s4_v3_recheck_checks/replays').glob('*.jsonl.gz'))
    for path in paths:
        modes={};switches=0;exposure=0
        with gzip.open(path,'rt') as stream:
            for line in stream:
                tick=json.loads(line)
                if not tick.get('capture'):continue
                for u in tick['units']:
                    c=u['commitment'];old=modes.get(u['id'],c>=0);new=True if c>.2 else False if c<-.2 else old
                    switches+=u['id'] in modes and new!=old;modes[u['id']]=new;exposure+=tick['dt']/60
        result[path.name]=dict(unit_reversal_ticks=switches,unit_minutes=exposure,
             commitment_reversals_per_unit_minute=switches/exposure if exposure else None)
    return result


def trace_summary(out,replays):
    summaries={}
    for replay in replays:
        payload=json.loads(gzip.decompress((out/'replays'/replay['file'].replace('.html','.replay.json.gz')).read_bytes()))
        arm=payload['spec']['arm']
        summaries[replay['file']]=summarize(payload['decisionDiagnostics']) if arm!='nearest' else dict(status='not_applicable: untuned nearest has no skeleton state')
        summaries[replay['file']]['opponent']=payload['spec']['opponent']
    result=dict(status='DESCRIPTIVE_EXPORTED_REPLAYS_ONLY',v4=summaries,historical_v3=historical_v3(),
        comparison_limit='Historical v3 regular diagnostic replays use different seeds and independently tuned knobs. Unit reversal ticks count at most one change per unit/tick; v4 additionally counts every pair change. V3 reconstruction is a threshold proxy for persistent out-ranged pairs; no v3 hold, focus or feasibility telemetry exists. No causal or population-wide claim follows.',
        hold_limit='Mean completed hold includes expired, early-band and disappearance releases; terminal active holds are censored separately. Early releases mean target_band, not death. All values come from exported 30 Hz decisions, not validation-population telemetry.')
    write(out/'DECISION_TRACE_SUMMARY.json',result);return result
