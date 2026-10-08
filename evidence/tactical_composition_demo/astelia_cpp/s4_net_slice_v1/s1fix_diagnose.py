"""Read-only, hashed initial-pilot diagnosis. No native fights or receipt edits."""
from collections import Counter, defaultdict
import hashlib
import json
import math
from pathlib import Path
import time
from collection import HERE, read, sha, atomic
from s1_public import oracle, intercept, support, reaction, retained_threats

ROOT=HERE/'_local/s0s1/pilot'
OUTPUT=HERE/'S1_WRAPPER_DIAGNOSIS_COUNTS.json'
FIXTURES=HERE/'fixtures/S1FIX_REPLAY.json'


def diagnose():
    start=time.monotonic();inv=read(ROOT/'INVENTORY.json')
    assert sha(ROOT/'INVENTORY.json')==read(ROOT/'SEAL.json')['inventory_sha256']
    stats=defaultdict(Counter);examples={};fixtures=[];inputs={};errors=defaultdict(list)
    for row in inv['rows']:
        if row['pair']>=10:continue
        fight=row['fight'];cell=row['pilot_cell'];arm=row['arm'];key=cell+'|'+arm;c=stats[key]
        path=ROOT/(fight+'.jsonl');receipt_path=ROOT/(fight+'.receipt.json');r=read(receipt_path)
        assert r['request']==row['request'] and r['inventory_sha256']==sha(ROOT/'INVENTORY.json')
        inputs[fight]=dict(receipt_sha256=sha(receipt_path),raw_sha256=r['raw_sha256'])
        raw_hash=hashlib.sha256();pending={};accepted={};cached={};decision=None
        with path.open('rb') as stream:
            for line in stream:
                raw_hash.update(line);f=json.loads(line)
                if f.get('terminal'):continue
                joint=f['joint'];tick=f['tick'];units={u['id']:u for u in joint['units']} if joint else {}
                snaps={e['unit']:{**joint,'self':e['unit']} for e in f['events'] if e['stage']=='snapshot'}
                candidates={e['unit']:e['value'] for e in f['events'] if e['stage']=='s1_candidate'}
                feasible=next((e['value']['feasible'] for e in f['events'] if e['stage']=='s1_joint'),0)
                if feasible>=2:
                    accepted.update({id:{**v,'plan':tick} for id,v in candidates.items()})
                for e in f['events']:
                    id=e['unit'];v=e['value'];stage=e['stage'];c['events:'+stage]+=1
                    if stage=='s1_rejection':c['reject:'+v['reason']]+=1
                    if stage=='s1_candidate':
                        me=next(u for u in snaps[id]['units'] if u['id']==id);focus=next(u for u in snaps[id]['units'] if u['id']==v['focus'])
                        lead,_=intercept(me,focus);request=[lead[i]+v['shape'][i] for i in (0,1)]
                        d=math.dist(request,v['planner_point']);errors[key+'|initial_recenter_px'].append(d)
                        c['candidate_recenter_nonzero']+=d>1e-8
                        c['candidate_recenter_gt_splash4']+=d>me['splash']/4
                        c['candidate_planner_point_out_of_reach']+=not(me['min_range']<=math.dist([me['x'],me['y']],v['planner_point'])<=me['range'])
                    if stage=='intent':
                        cached[id]=v
                        s=snaps[id];me=next(u for u in s['units'] if u['id']==id)
                        labs,sup=oracle(s);enemies=__import__('s0_arithmetic').slots(s)[1]
                        auto_target=enemies[labs[1]-1]['id'] if labs[1] else 0
                        auto_aim=sup['points'][sup['index']] if sup and sup['index'] is not None else None
                        c['decisions']+=1;c['command_decisions']+=v['volley']!=0
                        c['same_state_auto_start']+=bool(labs[2]);c['same_state_start']+=v['start']
                        c['same_state_start_removed']+=bool(labs[2]) and not v['start']
                        c['same_state_start_added']+=v['start'] and not labs[2]
                        c['same_state_auto_release']+=bool(labs[3]);c['same_state_release']+=v['release']
                        c['same_state_release_removed']+=bool(labs[3]) and not v['release']
                        if v['volley']:
                            c['command_target_changed_vs_auto']+=auto_target!=v['target']
                            if auto_aim and v['aim']:
                                d=math.dist(auto_aim,v['aim']);errors[key+'|command_vs_auto_aim_px'].append(d)
                                c['command_aim_gt_splash4_vs_auto']+=d>me['splash']/4
                            if id in accepted:
                                d=math.dist(accepted[id]['planner_point'],v['aim']) if v['aim'] else 0
                                if tick==accepted[id]['plan']:
                                    errors[key+'|initial_snapped_vs_planner_px'].append(d)
                                    c['initial_point_not_planner']+=d>1e-8
                        if id in pending:
                            c['decision_pending_target_differs']+=v['target']!=pending[id]['target']
                        if arm.endswith('wrapper') and feasible>=2 and len([x for x in fixtures if x['cell']==cell])<8:
                            # Save joint decision inputs once, not once per gun.
                            if not fixtures or fixtures[-1]['fight']!=fight or fixtures[-1]['tick']!=tick:
                                fixtures.append(dict(cell=cell,fight=fight,tick=tick,views=list(snaps.values()),casts={str(k):p for k,p in pending.items()}))
                    if stage=='projection':
                        me=units.get(id,{});raw=v['raw'];effective=v['effective'];phase=v['state'];c['projection:'+phase+':'+v['reason']]+=1
                        if raw['target']!=effective['target']:
                            c['target_correction_ticks']+=1;c['target_correction_phase:'+phase]+=1
                            c['target_correction_at_decision' if (tick-1)%6==0 else 'target_correction_between_decisions']+=1
                            c['target_correction_command' if raw['volley'] else 'target_correction_empty']+=1
                            c['target_correction_raw_focus_alive']+=units.get(raw['target'],{}).get('hp',0)>0
                            c['target_correction_locked_focus_dead']+=units.get(effective['target'],{}).get('hp',0)<=0
                            c['target_correction_native_snapshot_differs']+=me.get('target')!=effective['target']
                            c['target_correction_roots:'+str(e['cast_tick'])]+=0 # roots tracked separately below
                            examples.setdefault(key,dict(fight=fight,tick=tick,unit=id,cast_tick=e['cast_tick'],phase=phase,reason=v['reason'],raw_target=raw['target'],effective_target=effective['target'],snapshot_target=me.get('target'),command_plan=raw['volley']))
                        if v['start']:c['projected_starts']+=1
                        if v['release']:c['projected_releases']+=1
                    if stage=='s1_support':
                        c['support_rows']+=1;c['bad_snap']+=v['snap_error']>v['splash']/4;c['bad_snap_command' if cached.get(id,{}).get('volley') else 'bad_snap_empty']+=v['snap_error']>v['splash']/4
                        if v['snap_error']>v['splash']/4:
                            errors[key+'|bad_snap_px'].append(v['snap_error']);me=units[id];focus=units.get(cached[id]['target'])
                            if focus:
                                lead,_=intercept(me,focus);radius=max(me['splash'],math.dist(lead,[focus['x'],focus['y']]),math.dist(v['requested'],[focus['x'],focus['y']]))
                                errors[key+'|bad_snap_radius_px'].append(radius)
                                c['bad_snap_request_illegal']+=not(0<=v['requested'][0]<=joint['width'] and 0<=v['requested'][1]<=joint['height'] and me['min_range']<=math.dist([me['x'],me['y']],v['requested'])<=me['range'])
                    if stage=='s1_refresh':
                        c['refresh_reaction_active']+=reaction(snaps[id],retained_threats(snaps[id]))[0]
                        c['refresh_body_active']+=units[id]['busy'] or units[id]['guard_until']>joint['t']
                    if stage=='cast_start':pending[id]=dict(target=v['target'],aim=v['aim'],started=tick,originDecision=e['decision_tick'],originVolley=e['volley'])
                    if stage in ('launch','cancel','consumed_without_launch'):pending.pop(id,None)
        assert raw_hash.hexdigest()==r['raw_sha256'],fight
        for name in ('kills','deaths','damage','win','resolved_shells','friendly_damage'):
            c['outcome:'+name]+=r['metrics'][name]
    # Remove unused zero entries and report distributions without retaining every px sample.
    def dist(xs):
        xs=sorted(xs);return dict(n=len(xs),mean=sum(xs)/len(xs),min=xs[0],median=xs[len(xs)//2],p95=xs[min(len(xs)-1,int(.95*len(xs)))],max=xs[-1])
    value=dict(status='READ_ONLY_INITIAL_PILOT_DIAGNOSIS',physical_fights=0,inventory_sha256=sha(ROOT/'INVENTORY.json'),initial_report_sha256=sha(HERE/'S1_PILOT_INITIAL.json'),inputs=inputs,counts={k:{n:v for n,v in c.items() if v} for k,c in stats.items()},distributions={k:dist(v) for k,v in errors.items() if v},target_correction_examples=examples,wall_seconds=time.monotonic()-start)
    if OUTPUT.exists() or FIXTURES.exists():raise RuntimeError('preserve existing diagnosis output')
    atomic(OUTPUT,value);atomic(FIXTURES,dict(source_inventory_sha256=value['inventory_sha256'],physical_fights=0,states=fixtures))
    print(json.dumps({k:v for k,v in value.items() if k not in ('inputs','counts')},indent=2))
if __name__=='__main__':diagnose()
