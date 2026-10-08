"""S0: immutable collection-v2 analysis; never executes native code or fights."""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
import math
from pathlib import Path
import struct
import time
import numpy as np
from collection import HERE, sha, read
from s0_arithmetic import encode, check, join
from s1_public import reaction, retained_threats, oracle, encoded_view

DESIGN_COMMIT='cac370a4ab08af98d59cccd63ecaa7c3f66a81ac'
HEADS=('move','target','start','release','aim')


def distribution(values):
    if not values:return dict(count=0,status='UNRESOLVED',reason='no finite represented observations')
    a=np.asarray(values,dtype=float)
    return dict(count=len(a),median=float(np.median(a)),p90=float(np.quantile(a,.9)),maximum=float(max(a)),over_200_fraction=float(np.mean(a>200)))


class Conflicts:
    def __init__(self):self.tables=defaultdict(dict);self.rows=Counter();self.repeat=Counter();self.conflicts=Counter()
    def add(self, key, features, labels, masks):
        # One diagnostic bin: .02 continuous; categorical/booleans exact.
        categorical=set(range(998,1004))
        for base in range(0,800,32):categorical.update(base+j for j in (0,1,2,3,16,17,18,25,28,29,31))
        for base in range(800,992,24):categorical.update(base+j for j in (0,1,2,3,4,18,19,20,21,22))
        contexts={'exact':struct.pack('<1008f',*features),'bin_002':json.dumps([v if i in categorical else round(v/.02) for i,v in enumerate(features)],separators=(',',':')).encode()}
        for kind,context in contexts.items():
            for h,lab,active in zip(HEADS,labels,masks):
                if not active:continue
                # Aim resolved-target context and active masks are observable.
                suffix=bytes(map(bool,masks))+(struct.pack('<i',labels[1]) if h=='aim' else b'')
                digest=hashlib.sha256(context+suffix).digest();name=key+'|'+kind+'|'+h
                self.rows[name]+=1;old=self.tables[name].get(digest)
                if old is None:self.tables[name][digest]=1<<lab
                else:self.repeat[name]+=1;self.conflicts[name]+=int(not(old&(1<<lab)));self.tables[name][digest]=old|(1<<lab)
    def report(self):
        return {k:dict(active_rows=self.rows[k],unique_inputs=len(v),repeated_rows=self.repeat[k],conflicting_new_labels=self.conflicts[k],conflicting_inputs=sum(x.bit_count()>1 for x in v.values()),coverage='COLLISIONS_OBSERVED' if self.repeat[k] else 'UNRESOLVED_NO_COLLISIONS') for k,v in sorted(self.tables.items())}


def analyze(root):
    started=time.monotonic();root=Path(root);inv=read(root/'INVENTORY.json');seal=read(root/'SEAL.json');ledger=read(root/'LEDGER.json')
    inventory_hash=sha(root/'INVENTORY.json')
    if inventory_hash!=seal['inventory_sha256'] or inventory_hash!=ledger['inventory_sha256'] or ledger['pending'] or set(ledger['complete'])!={r['group'] for r in inv['rows']}:raise RuntimeError('incomplete/mismatched sealed collection')
    stats={};conf=Conflicts();sources=[]
    for row in inv['rows']:
        key='|'.join(str(row[k]) for k in ('cell','guns','split'))
        z=stats.setdefault(key,dict(fights=0,decision_ticks=0,eligible_ready_multi_ticks=0,multi_assigned_ticks=0,assigned_gun_rows=0,pattern_rows=Counter(),pattern_tick_occurrences=Counter(),coming_gun_rows=0,missing_targets=0,missing_raw_aim=0,reaction_rows=0,reaction_nonzero=0,raw_distances=[],snaps=[]))
        rp=root/(row['group']+'.receipt.json');raw=root/(row['group']+'.jsonl');receipt=read(rp);raw_hash=sha(raw)
        if receipt['raw_sha256']!=raw_hash or receipt['request']!=row['request'] or receipt['status']!='COMPLETE' or receipt['inventory_sha256']!=inventory_hash:raise RuntimeError('fight data/receipt mismatch')
        sources.append(dict(group=row['group'],raw_sha256=raw_hash,receipt_sha256=sha(rp)));z['fights']+=1
        terminal=False;previous=0;frames=0;decisions=0
        with raw.open() as stream:
            for line in stream:
                frame=json.loads(line)
                if terminal:raise RuntimeError('post terminal record')
                if frame.get('terminal'):terminal=True;continue
                if frame['tick']!=previous+1 or frame['fight']!=row['group']:raise RuntimeError('chronology')
                previous=frame['tick'];frames+=1
                intents={e['unit']:e['value'] for e in frame['events'] if e['stage']=='intent'}
                if not intents:continue
                z['decision_ticks']+=1;decisions+=len(intents);joint=frame['joint'];ready=0
                diagnostics=[e for e in frame['events'] if e['stage']=='teacher_planner'];families=set()
                z['assigned_gun_rows']+=len(diagnostics);z['multi_assigned_ticks']+=sum(e['value'].get('family') not in (0,10,None) for e in diagnostics)>=2
                for e in diagnostics:
                    v=e['value'];family=f"{v.get('family','MISSING')}/{v.get('variant','MISSING')}";z['pattern_rows'][family]+=1;families.add(family)
                    own_action=intents.get(e['unit']);target=next((u for u in joint['units'] if own_action and u['id']==own_action['target']),None)
                    if 'raw_aim' not in v:z['missing_raw_aim']+=1
                    elif target:z['raw_distances'].append(math.dist(v['raw_aim'],[target['x'],target['y']]))
                    else:z['missing_targets']+=1
                    if 'snap_distance' in v:z['snaps'].append(v['snap_distance'])
                z['pattern_tick_occurrences'].update(families)
                for id,a in intents.items():
                    s={**joint,'self':id};me=check(s);features,_=encode(s);features=np.asarray(features,dtype=np.float32).tolist()
                    # Ready-only eligibility exactly as historical teacher (before aim support).
                    body=me['guard_until']>s['t'] or me['busy'];full=reaction(s);active=full[0]
                    r=me['prep']>0 and me['prep']+s['dt']*me['time_rate']>=me['windup']-1e-9
                    ready+=bool(r and not body and not active and a['target'])
                    z['coming_gun_rows']+=bool(me['prep']>0 and not r)
                    retained=reaction(s,retained_threats(s));z['reaction_rows']+=1
                    z['reaction_nonzero']+=math.dist(full[1],retained[1])>1e-9
                    events=[dict(fight=s['fight'],tick=s['tick'],unit=id,decision_tick=s['tick'],stage=stage,value=value,volley=a.get('volley',0)) for stage,value in [('snapshot',s),('intent',a)]]
                    masks=join(events)[(s['fight'],s['tick'],id)]['masks']
                    labs=[a['move_index'],a['target_index'],int(a['start']),int(a['release']),a['aim_index'] or 0]
                    conf.add(key+'|old_unit',features,labs,[masks[k] for k in HEADS])
                    represented=encoded_view(s,features);new,_=oracle(represented)
                    # Autonomous only; new group provenance/cache unavailable in v2.
                    conf.add(key+'|prospective_autonomous',features,new,[True,True,True,True,bool(masks['aim'])])
                z['eligible_ready_multi_ticks']+=ready>=2
        if not terminal or frames!=receipt['record_count'] or decisions!=receipt['decision_count']:raise RuntimeError('receipt row count/terminal')
        print(row['group'],flush=True)
    for z in stats.values():
        z['raw_aim_to_own_target_px']=distribution(z.pop('raw_distances'));z['snap_distance_px']=distribution(z.pop('snaps'))
        z['eligible_ready_multi_fraction']=z['eligible_ready_multi_ticks']/z['decision_ticks'] if z['decision_ticks'] else None
        z['multi_gun_assigned_fraction']=z['multi_assigned_ticks']/z['decision_ticks'] if z['decision_ticks'] else None
        z['threat_overflow_goal_nonzero_fraction']=z['reaction_nonzero']/z['reaction_rows'] if z['reaction_rows'] else None
        z['joint_plan_distribution']=dict(status='UNRESOLVED',reason='no selected-plan record/focus provenance in v2; snapped gun rows may omit a whole plan; pattern_tick_occurrences are decision-level occurrences, not complete joint plans')
        z['coming_gun_exclusion']='all coming guns excluded by historical ready-only teacher; count includes unavailable/reaction-blocked coming guns'
    conflicts=conf.report();corrected=sum(v['conflicting_inputs'] for k,v in conflicts.items() if '|prospective_autonomous|exact|' in k)
    return dict(stage='S0',design_commit=DESIGN_COMMIT,physical_fights=0,wall_seconds=time.monotonic()-started,inventory_sha256=inventory_hash,seal_sha256=sha(root/'SEAL.json'),ledger_sha256=sha(root/'LEDGER.json'),sources=sources,tool_sources_sha256={n:sha(HERE/n) for n in ('s0_analysis.py','s0_arithmetic.py','s1_public.py','schema.py','labels.py')},strata=stats,conflicts=conflicts,missing_fields=['joint plan identity','planner focus/led-centre provenance','new command and one-refresh cache context'],group_label_conflicts=dict(status='UNRESOLVED',reason='new group labels cannot be reconstructed from queue points without focus provenance'),stops=[dict(condition='Any required field absent?',yes=True,action='Mark that count unresolved',role='implementer'),dict(condition='Multi-gun assigned coverage <5% in any multi-gun stratum?',yes=any(z['decision_ticks'] and z['multi_gun_assigned_fraction']<.05 for k,z in stats.items() if k.split('|')[1] in ('2','10')),action='Revise S1 cells/readiness diversity',role='drafter'),dict(condition='Corrected oracle has exact active-label conflicts?',yes=corrected>0,action='Revise dependency contract',role='drafter')],limits='Prospective autonomous-only reconstruction at float32 training precision; no group command context. No collisions is unresolved coverage. Bin conflicts are diagnostic. Historical verdicts unchanged.')


def main():
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=HERE/'_local/collection_v2');p.add_argument('--output',type=Path,default=HERE/'S0_ANALYSIS.json');a=p.parse_args()
    if a.output.exists() or a.output.with_suffix('.md').exists():raise RuntimeError('refuse overwrite')
    if a.root.resolve() in a.output.resolve().parents:raise RuntimeError('output inside immutable collection')
    v=analyze(a.root);a.output.write_text(json.dumps(v,indent=2,allow_nan=False)+'\n')
    note=['# S0 collection-v2 analysis','',f"Read-only: {len(v['sources'])} fights; {v['wall_seconds']:.2f} s; zero fights executed.",f"Design commit: `{DESIGN_COMMIT}`. Inventory SHA256: `{v['inventory_sha256']}`.",'','| Cell/guns/split | decisions | ready multi % | assigned multi % | reaction correction % |','|---|---:|---:|---:|---:|']
    for k,z in sorted(v['strata'].items()):note.append(f"| {k.replace(chr(124), chr(47))} | {z['decision_ticks']} | {100*z['eligible_ready_multi_fraction']:.2f} | {100*z['multi_gun_assigned_fraction']:.2f} | {100*z['threat_overflow_goal_nonzero_fraction']:.2f} |")
    note+=['','Joint-plan denominator and corrected group conflicts are unresolved: v2 omits plan/focus provenance. Assigned-row and per-decision family distributions, distances and conflict occupancy are in JSON. Old unit conflicts diagnose historical dependencies; new autonomous checks do not qualify command-conditioned S2 labels. Threat overflow is not group reaction; shift stays dropped.','']
    for stop in v['stops']:note.append(f"- {stop['condition']} **{'YES' if stop['yes'] else 'NO'}** → {stop['action']} ({stop['role']}).")
    a.output.with_suffix('.md').write_text('\n'.join(note)+'\n')
    print(json.dumps(dict(output=str(a.output),wall_seconds=v['wall_seconds'])))
if __name__=='__main__':main()
