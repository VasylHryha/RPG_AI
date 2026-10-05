"""Fresh development declaration, survivor diagnostics and v1 harness boundaries."""
import json
import subprocess
import sys
import pytest
import s4_v1 as V
import s4_amended as OLD
from result_schema import validate_summary
from test_s4_amended import extended


def test_declared_fresh_panels_and_protocol_constants():
    declared=json.loads((V.ROOT/'S4_V1_SEEDS.json').read_text())
    used=set()
    old={b[1] for stage in 'ABC' for split in ('tuning','validation') for b in OLD.battles(stage,split)}
    for stage in 'ABC':
        for split in ('tuning','validation'):
            panel=V.battles(stage,split)
            assert declared['panels'][stage][split]==[list(b) for b in panel]
            seeds={b[1] for b in panel};assert not seeds&old and not seeds&used;used|=seeds
            assert len(panel)==19 if split=='tuning' else all(sum(b[0]==opp and b[2]==setting for b in panel)==100 for opp,_,setting in panel)
    assert (V.POPULATION,V.GENERATIONS,V.CLUSTERS,V.WORKERS,V.VALIDATION_N)==(16,16,19,10,100)
    assert {a:len(b) for a,b in V.BOUNDS.items()}=={'resonator':10,'morale':10,'pushpull':2}
    assert V.CAP_SECONDS==180*60-34.48*60
    V.verify_sources()


def test_existing_output_refused_without_any_fight(tmp_path,monkeypatch):
    monkeypatch.setattr(sys,'argv',['s4_v1.py','--output',str(tmp_path)])
    with pytest.raises(RuntimeError,match='output already exists'):V.main()
    assert not list(tmp_path.iterdir())


@pytest.mark.parametrize('value', [[-1,0],[1.5,0],[True,0],[0],[float('nan'),0],[100,0]])
def test_artillery_schema_rejects_invalid_counts(value):
    row=extended();row['artilleryAlive']=value
    with pytest.raises(ValueError):validate_summary(row)


def test_optional_end_counts_match_trace_and_preserve_plain_summary():
    from s3_runner import request
    req=request(dict(arm='nearest',skeleton='v1',trace=True))
    req['options']['duration']=.1;req['options']['army']=dict(melee=1,ranged=0,artillery=2)
    def run(req):return [json.loads(x) for x in subprocess.check_output([str(V.BINARY)],input=json.dumps(req)+'\n',text=True).splitlines()]
    plain=run(req);counted=run(dict(req,endCounts=True))
    guns=[sum(u['alive'] and u['team']==side and u['role']=='artillery' for u in counted[-2]['state']['units']) for side in (0,1)]
    summary=counted[-1];assert summary.pop('artilleryAlive')==guns
    assert counted==plain
    assert validate_summary(dict(summary,artilleryAlive=guns))=='completed'
