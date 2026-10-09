"""Replay parser lifetime, single-frame envelope and frozen-evidence recovery."""
import json
import subprocess
import sys
from pathlib import Path
import pytest
sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import BINARY, HERE, read, sha, write


def test_bounded_request_layouts_and_exception_cleanup(tmp_path):
    record = read(BINARY.with_suffix('.build.json'))
    command = next(c for c in record['commands'] if c[c.index('-c')+1] == str(HERE/'stagea.cpp'))
    source = tmp_path/'bounded.cpp'; binary = tmp_path/'bounded'
    source.write_text(r'''
#include "bounded_json.h"
#include <iostream>
int main(){
 stagea::FrameLayouts layouts;auto before=js::shapes.size();
 for(int tick=0;tick<4501;++tick){
  std::string line="{\"nested\":[{\"history\":{";
  for(int key=0;key<2500;++key){if(key)line+=',';line+='"'+std::to_string(tick*2500+key)+"\":[1,2]";}
  line+="}}],\"duplicate\":1,\"duplicate\":2,\"escape\":\"\\uD83D\\uDE00\\n\"}";
  auto row=stagea::parseBounded(line,layouts);
  js::collect({row},0); // Request layouts remain valid across a rooted tick GC.
  if(js::num(js::get(row,"duplicate"))!=2||js::str(js::get(row,"escape"))!="\xF0\x9F\x98\x80\n")return 2;
  auto nested=js::get(row,"nested").p->items[0];auto history=js::get(nested,"history");
  if(history.p->props.size()!=2500)return 3;
  js::collect({},0);layouts.clear();
  if(js::shapes.size()!=before||!js::arena.empty())return 4;
 }
 try{stagea::parseBounded("{\"a\":[{\"b\":1}],",layouts);return 5;}catch(const std::exception&){}
 js::collect({},0);layouts.clear();
 if(!js::arena.empty()||!layouts.owned.empty())return 6;
 std::cout<<"{\"frames\":4501,\"shapes_added\":"<<js::shapes.size()-before<<"}\n";
}
''')
    subprocess.run([*command[:command.index('-c')], str(source), '-o', str(binary)], check=True, timeout=60)
    proof = json.loads(subprocess.run([str(binary)], capture_output=True, text=True, check=True, timeout=120).stdout)
    assert proof == dict(frames=4501, shapes_added=0)


def test_native_replay_rejects_unbounded_batch():
    result = subprocess.run([str(BINARY)], input=json.dumps(dict(operation='stageaReplay', frames=[{}, {}]))+'\n', text=True, capture_output=True, check=True, timeout=10)
    assert json.loads(result.stdout)['error'] == 'replay requires one frame per RPC'


def recovery_fixture(tmp_path, monkeypatch):
    import parmem_recovery as recovery
    monkeypatch.setattr(recovery, 'HERE', tmp_path)
    monkeypatch.setattr(recovery, 'CPP', tmp_path.parent)
    monkeypatch.setattr(recovery, 'LOCAL', tmp_path/'_local')
    monkeypatch.setattr(recovery, 'BINARY', tmp_path/'_local/build/host')
    monkeypatch.setattr(recovery, 'RECOVERY', tmp_path/'RECOVERY.json')
    old_sources = {'unchanged.py': 'old'}
    new_sources = {**old_sources, str((tmp_path/'parity.py').relative_to(tmp_path.parent)): 'new'}
    old_binary = dict(sources=old_sources, engine='army_stagea', scope='native_complete_engine', sanitized=False, portable=False)
    new_binary = {**old_binary, 'sources': new_sources, 'binary_sha256': 'new'}
    monkeypatch.setattr(recovery, 'sources', lambda: new_sources)
    monkeypatch.setattr(recovery, 'identity', lambda: new_binary)
    local = tmp_path/'_local'; local.mkdir()
    ledger_path = local/'ledger.json'; monkeypatch.setattr(recovery, 'ledger_path', lambda: ledger_path)
    request = local/'requests/job.json'; write(request, {'sealed': True})
    write(ledger_path, dict(sources=old_sources, binary=old_binary, jobs=[dict(tag='job', request_sha256=sha(request))]))
    write(local/'INDEX.json', {'fights': []})
    write(local/'DECIDABILITY.json', dict(status='PASS', sources=old_sources))
    write(local/'TRAIN_BUDGET.json', dict(status='ADMITTED', sources=old_sources, index_sha256=sha(local/'INDEX.json'), audit_sha256=sha(local/'DECIDABILITY.json')))
    exports = {}
    for arm in recovery.ARMS:
        weights = local/'training'/(arm+'.weights.json'); checkpoint = local/'training'/(arm+'.pt')
        write(weights, {'arm': arm}); checkpoint.write_bytes(b'checkpoint')
        exports[arm] = sha(weights)
        write(local/'training'/(arm+'.outcome.json'), dict(budget_sha256=sha(local/'TRAIN_BUDGET.json'), export_sha256=sha(weights), checkpoint_sha256=sha(checkpoint)))
    write(tmp_path/'PARITY_RUN_c7136052e0485bba.json', dict(status='STOP_RESUMABLE', error='RuntimeError: child exceeds 2 GiB RSS', manifest=dict(binary=old_binary, budget_sha256=sha(local/'TRAIN_BUDGET.json'), index_sha256=sha(local/'INDEX.json'), exports=exports)))
    preserved = {str(p.relative_to(tmp_path)): sha(p) for p in tmp_path.rglob('*') if p.is_file()}
    baseline = dict(sources=old_sources, binary=old_binary, ledger_file='ledger.json', preserved=preserved)
    budget, current, delta = recovery.verify_baseline(baseline)
    write(recovery.RECOVERY, dict(status='REGISTERED_INFERENCE_ONLY_NO_RETRY', baseline=baseline, sources=new_sources, binary=current, changed_sources=delta, budget_sha256=sha(local/'TRAIN_BUDGET.json'), index_sha256=sha(local/'INDEX.json'), failure_sha256=sha(tmp_path/'PARITY_RUN_c7136052e0485bba.json')))
    return recovery, new_sources


@pytest.mark.parametrize('path', ['_local/training/N2.weights.json', '_local/training/N2.pt', '_local/training/N2.outcome.json', '_local/TRAIN_BUDGET.json', '_local/INDEX.json', '_local/DECIDABILITY.json', '_local/requests/job.json', 'PARITY_RUN_c7136052e0485bba.json'])
def test_recovery_rejects_fixed_evidence_tampering(tmp_path, monkeypatch, path):
    recovery, _ = recovery_fixture(tmp_path, monkeypatch)
    assert recovery.checked_inference_budget()['status'] == 'ADMITTED'
    target = tmp_path/path; target.write_bytes(target.read_bytes()+b' ')
    with pytest.raises(RuntimeError, match='fixed evidence drift'):
        recovery.checked_inference_budget()


def test_recovery_rejects_unregistered_sources_and_binary(tmp_path, monkeypatch):
    recovery, new_sources = recovery_fixture(tmp_path, monkeypatch)
    new_sources['trainer.py'] = 'bad'
    with pytest.raises(RuntimeError, match='unauthorized source'):
        recovery.checked_inference_budget()
    del new_sources['trainer.py']
    new_sources[next(k for k in new_sources if k.endswith('/parity.py'))] = 'changed again'
    with pytest.raises(RuntimeError, match='registration drift'):
        recovery.checked_inference_budget()
    new_sources[next(k for k in new_sources if k.endswith('/parity.py'))] = 'new'
    binary = recovery.identity().copy(); binary['binary_sha256'] = 'drift'
    monkeypatch.setattr(recovery, 'identity', lambda: binary)
    with pytest.raises(RuntimeError, match='registration drift'):
        recovery.checked_inference_budget()
