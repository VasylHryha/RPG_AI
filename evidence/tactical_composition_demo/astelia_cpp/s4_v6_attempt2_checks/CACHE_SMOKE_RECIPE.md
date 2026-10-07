# Exact no-combat smoke recipe for attempt 2

Executed once by `.venv/bin/python -` from the repository root immediately before launch. The excerpt below is the actual smoke code used after creating the fresh declaration. It returned PASS. No native process, scored fight or extra engineering fight ran. The prior 27 repair tests were not repeated.

`V.CHECKS` was `s4_v6_attempt2_checks/`. The cache root was empty at the original invocation. For any future independent reproduction, use a new empty local cache root; retain the original cache and receipt unchanged. This session did not repeat the smoke.

```python
import pathlib, sys, json
from types import SimpleNamespace
root = pathlib.Path('evidence/tactical_composition_demo/astelia_cpp').resolve()
sys.path.insert(0, str(root))
from s4_v6_attempt2 import V
stored=json.loads((root/'s4_v6_checks/ENGINEERING_REFINEMENT.json').read_text())['rows'][0]
summary=stored['summary']; req=stored['request']
engine=V.identity('cpp',[str(V.BINARY),'--metrics'])
spec=dict(arm='resonator',params=V.defaults('resonator'),skeleton='v6',setting='s4_melee10',
          opponent='novice',seed=req['options']['seed'],endCounts=True,diagnostics=True)
assert V.request(spec)==req
stderr=(root/'s4_v6_checks/engineering'/f"{stored['name']}.stderr.txt").read_text()
class Replay:
    calls=0
    def remaining(self,*args):return 30
    def run(self,*args):
        self.calls+=1
        return SimpleNamespace(returncode=0,stdout=json.dumps([summary])+'\n',stderr=stderr)
r=Replay(); cache=V.CHECKS/'cache_smoke'
first=V.execute((engine,cache,[spec]),r);second=V.execute((engine,cache,[spec]),r)
assert r.calls==1 and not first[0]['cache_hit'] and second[0]['cache_hit']
assert first[0]['summary']==second[0]['summary']==summary
V.write(V.CHECKS/'CACHE_SMOKE.json',dict(status='PASS',combat_fights_executed=0,native_processes=0,
     stored_fixture=stored['name'],stored_source_sha256=V.sha(root/'s4_v6_checks/ENGINEERING_REFINEMENT.json'),
     write_and_hit_verified=True,complex_diagnostics_preserved=True,worker_calls=2,fake_host_calls=r.calls))
```
