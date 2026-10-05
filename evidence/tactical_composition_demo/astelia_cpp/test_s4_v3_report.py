import json
import pytest
import s4_v3_report as R


def test_shared_seed_blocks_retain_cross_doctrine_covariance():
    values = {json.dumps((opponent,seed,'s4_p23')):float(seed) for seed in range(4) for opponent in R.A.POOL}
    blocks = R.seed_blocks(values)
    assert blocks == {str(seed):float(seed) for seed in range(4)}
    assert R.stats(blocks)['n'] == 4
    assert R.stats(blocks)['sd'] > R.stats(values)['sd']
    values.pop(next(iter(values)))
    with pytest.raises(ValueError,match='missing doctrine'):
        R.seed_blocks(values)


def test_every_C_orientation_metric_is_checked():
    first = dict.fromkeys(R.COUNTERS,0)
    second = dict(first,search_calls=1)
    R.check_metrics(first,'C')
    with pytest.raises(ValueError,match='Stage C planning'):
        R.check_metrics(second,'C')


def test_selected_scores_include_initial_and_keep_earlier_ties():
    initial = {'a':2.,'b':4.}
    tied = {'a':3.,'b':3.}
    better = {'a':4.,'b':5.}
    def candidate(v):return dict(scores=v,stats=R.stats(v))
    log = dict(initial_scores=initial,generations=[dict(candidates=[candidate(tied)])])
    assert R.selected_scores(log) is initial
    log['generations'].append(dict(candidates=[candidate(better),candidate(better)]))
    assert R.selected_scores(log) is better


def test_bounded_power_units_and_floor():
    assert R.plan_n(0,3.5,16)==16
    assert R.plan_n(9,3.5,16)>=16
    assert R.plan_n(9,1,16)>R.plan_n(9,3.5,16)
    with pytest.raises(ValueError):R.plan_n(9,0,16)


def test_tuning_and_validation_end_states_stay_separate(tmp_path,monkeypatch):
    import gzip
    from test_s4_amended import extended
    monkeypatch.setattr(R,'OUT',tmp_path)
    uses=[dict(stage='B',split=split,arm='resonator',candidate='best',setting='s4_full_head',opponent='regular') for split in ('tuning','validation')]
    R.write(tmp_path/'s4_seeds.json',dict(uses=uses))
    rows=[]
    for t,guns in [(150,8),(90,0)]:
        result=extended();result.update(t=t,artilleryAlive=[2,guns]);rows.append(dict(summary=result))
    with gzip.open(tmp_path/'fights.jsonl.gz','wt') as stream:
        for row in rows:stream.write(json.dumps(row)+'\n')
    all_states=R.all_end_states();validation=R.diagnostics()
    assert all_states['B|tuning|resonator|s4_full_head|regular']['timeouts']==1
    assert all_states['B|tuning|resonator|s4_full_head|regular']['mean_enemy_artillery_alive']==8
    assert validation['B']['resonator']['s4_full_head|regular']['timeouts']==0
    assert validation['B']['resonator']['s4_full_head|regular']['mean_enemy_artillery_alive']==0
