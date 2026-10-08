"""Revision-specific extra integrity and same-state autonomous counters."""
from collections import Counter
import math
from s1_metrics import measure as original_measure, summarize


def measure(frames,request):
    counts=Counter();shadows={};shape={};refresh=set()
    def checked():
        for frame in frames:
            for e in frame.get('events',[]):
                stage=e['stage'];v=e['value'];id=e['unit']
                if stage=='s1_autonomous_shadow':shadows[id]=v
                if stage=='intent' and id in shadows:
                    a=shadows[id]
                    counts['same_state_auto_start']+=a['start'];counts['same_state_start_removed']+=a['start'] and not v['start']
                    counts['same_state_auto_release']+=a['release'];counts['same_state_release_removed']+=a['release'] and not v['release']
                    if v['volley']:counts['command_target_change']+=a['target']!=v['target']
                if stage=='s1_candidate':
                    if v['requested']!=v['planner_point']:raise ValueError('planner point changed at assignment')
                    counts['planner_exact_points']+=1
                if stage=='s1_refresh':
                    key=(id,e['cast_tick'])
                    if key in refresh:raise ValueError('multiple release refreshes')
                    refresh.add(key)
                if stage=='s1_support':
                    counts['autonomous_bound_rows']+=v.get('autonomous_bound_error',0)>1e-8
                    counts['autonomous_bound_gt_splash4']+=v.get('autonomous_bound_error',0)>v['splash']/4
                    if v.get('commanded'):
                        counts['commanded_support']+=1;counts['commanded_bad_snap']+=v['snap_error']>v['splash']/4
                if stage=='projection':
                    counts['raw_effective_target_diff']+=v['raw']['target']!=v['effective']['target']
                    # Any raw/effective aim correction represents an unhandled
                    # native lock; all raw S1FIX actions already respect it.
                    a,b=v['raw']['aim'],v['effective']['aim']
                    counts['raw_effective_aim_diff']+=(a is None)!=(b is None) or (a is not None and b is not None and math.dist(a,b)>1e-9)
            yield frame
    result=original_measure(checked(),request);result['revision']='S1FIX-2';result['integrity']=dict(counts)
    # Preserve the original target-lock endpoint and strengthen with aim lock.
    result['counts']['native_target_lock_correction']=counts['raw_effective_target_diff']+counts['raw_effective_aim_diff']
    return result
