"""Cache invalidation, tamper rejection and execution accounting contracts."""
import gzip
import json
import pathlib
import sys
import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from result_cache import Cache, Engine, digest


SUMMARY = dict(mode='alone', melee=0, ranged=0, artillery=0, total=0, wasted=0,
               monsterDeaths=0, hunterKills=0, aliveSeconds=0, enemyDamage=0,
               survivors=1, enemySurvivors=1, t=90)


def test_request_order_and_negative_zero_are_distinct():
    assert digest({'x': 1, 'y': 2}) != digest({'y': 2, 'x': 1})
    assert digest({'seed': 0.0}) != digest({'seed': -0.0})


@pytest.mark.parametrize('field,value', [('seed', 2), ('rules', 'game'), ('abilities', True),
                                         ('ai', [{'level': 'elite'}, {}])])
def test_changed_fight_misses(tmp_path, field, value):
    cache = Cache(tmp_path, {'binary': 'one', 'network': 'a'})
    request = {'options': {'seed': 1}}
    cache.put(request, [SUMMARY])
    changed = {'options': dict(request['options'], **{field: value})}
    assert cache.load(changed) is None


@pytest.mark.parametrize('field', ['binary', 'network', 'host', 'node', 'source'])
def test_changed_implementation_misses(tmp_path, field):
    before = {key: 'old' for key in ('binary', 'network', 'host', 'node', 'source')}
    cache = Cache(tmp_path, before)
    cache.put({'seed': 1}, [SUMMARY])
    after = dict(before, **{field: 'new'})
    assert Cache(tmp_path, after).load({'seed': 1}) is None


def test_modified_result_rejected(tmp_path):
    cache = Cache(tmp_path, {'binary': 'one'})
    request = {'seed': 1}
    cache.put(request, [SUMMARY])
    path = cache.path(request)
    record = json.loads(gzip.decompress(path.read_bytes()))
    record['rows'][0]['survivors'] = 999
    path.write_bytes(gzip.compress(json.dumps(record).encode()))
    assert cache.load(request) is None
    assert cache.rejected == 1


def test_host_execution_then_cache_and_changed_host(tmp_path):
    host = tmp_path / 'host.py'
    host.write_text("import json,sys,pathlib\nsummary=" + repr(SUMMARY) + "\nfor line in sys.stdin:\n"
                    " with pathlib.Path(__file__).with_suffix('.calls').open('a') as f:f.write('fight\\n')\n"
                    " print(json.dumps(dict(summary,wasted=1)),flush=True)\n")
    command = [sys.executable, str(host)]
    engine = Engine('test', command, tmp_path / 'cache')
    assert engine.fight({'seed': 1}) == engine.fight({'seed': 1})
    assert engine.counts() == {'cached': 1, 'executed': 1, 'rejected': 0}
    engine.close()
    assert len(host.with_suffix('.calls').read_text().splitlines()) == 1
    # The same command/path with changed bytes must execute again.
    host.write_text(host.read_text().replace("wasted=1", "wasted=2"))
    engine = Engine('test', command, tmp_path / 'cache')
    assert engine.fight({'seed': 1})[-1]['wasted'] == 2
    assert engine.counts()['executed'] == 1
    engine.close()


def test_trace_preserved_and_does_not_alias_summary(tmp_path):
    cache = Cache(tmp_path, {'binary': 'one'})
    req = {'options': {'seed': 1}, 'trace': True}
    def state(t, hp):
        return dict(t=t, units=[dict(id=1, team=0, role='melee', x=1, y=2, hp=hp, cd=0, alive=True, target=None)])
    rows = [{'step': 0, 'state': state(0, 100)}, {'step': 1, 'state': state(90, 90)}, SUMMARY]
    cache.put(req, rows)
    assert cache.load(req) == rows
    assert cache.load({'options': {'seed': 1}}) is None


@pytest.mark.parametrize('rows', [[{}], [dict(SUMMARY, total=99)], [dict(SUMMARY, survivors=-1)],
                                  [dict(SUMMARY, mode='reactive')]])
def test_checksum_valid_malformed_rows_rejected(tmp_path, rows):
    cache = Cache(tmp_path, {'binary': 'one'})
    request = {'seed': 1}
    cache.put(request, [SUMMARY])
    path = cache.path(request)
    record = json.loads(gzip.decompress(path.read_bytes()))
    record.update(rows=rows, rows_sha256=digest(rows))
    path.write_bytes(gzip.compress(json.dumps(record).encode()))
    assert cache.load(request) is None
    assert cache.rejected == 1


def test_truncated_trace_rejected(tmp_path):
    cache = Cache(tmp_path, {'binary': 'one'})
    with pytest.raises(ValueError, match='initial frame'):
        cache.put({'trace': True}, [SUMMARY])


def test_source_change_during_fight_cannot_create_cache_entry(tmp_path):
    host=tmp_path/'changing.py'
    host.write_text('import json,sys,pathlib\nfor line in sys.stdin:\n'
        ' p=pathlib.Path(__file__);p.write_text(p.read_text()+"# changed\\n")\n'
        ' print('+repr(json.dumps(SUMMARY))+',flush=True)\n')
    engine=Engine('test',[sys.executable,str(host)],tmp_path/'cache');request={'seed':2026100409}
    try:
        with pytest.raises(RuntimeError,match='identity changed'):
            engine.fight(request)
        assert not engine.cache.path(request).exists()
    finally:
        with pytest.raises(RuntimeError,match='identity changed'):
            engine.close()


def test_different_js_host_cannot_import_legacy_results(tmp_path):
    from result_cache import prime_legacy
    host=tmp_path/'other.cjs';host.write_text('process.exit(0);')
    engine=Engine('js',['node',str(host)],tmp_path/'cache')
    try:
        assert prime_legacy(engine)==0
        assert not list(engine.cache.root.glob('*.gz'))
    finally:engine.close()


def test_stderr_flood_cannot_deadlock_response(tmp_path):
    host=tmp_path/'chatty.py'
    host.write_text('import json,sys\nfor line in sys.stdin:\n sys.stderr.write("x"*200000);sys.stderr.flush()\n print('+repr(json.dumps(SUMMARY))+',flush=True)\n')
    engine=Engine('test',[sys.executable,str(host)],tmp_path/'cache',request_timeout=3)
    try:
        assert engine.fight({'seed':4})==[SUMMARY]
        assert engine.executed==1
    finally:engine.close()


@pytest.mark.parametrize('body', ['for line in sys.stdin: time.sleep(30)',
    'for line in sys.stdin:\n print("{bad json}",flush=True);time.sleep(30)'])
def test_unresponsive_or_invalid_host_is_killed_without_cache(tmp_path,body):
    import time
    host=tmp_path/'bad.py';host.write_text('import sys,time\n'+body+'\n')
    engine=Engine('test',[sys.executable,str(host)],tmp_path/'cache',request_timeout=.3,shutdown_timeout=1)
    start=time.monotonic()
    with pytest.raises((RuntimeError,ValueError)):
        engine.fight({'seed':9})
    assert time.monotonic()-start<3 and engine.process is None
    assert engine.executed==0 and not engine.cache.path({'seed':9}).exists()
    engine.close()


def test_host_ignoring_input_cannot_block_large_request(tmp_path):
    host=tmp_path/'unread.py';host.write_text('import time\ntime.sleep(30)\n')
    engine=Engine('test',[sys.executable,str(host)],None,request_timeout=.3,shutdown_timeout=1)
    with pytest.raises(RuntimeError,match='timed out'):
        engine.fight({'large':'x'*1000000})
    assert engine.process is None
    engine.close()


def test_host_refusing_eof_has_bounded_close(tmp_path):
    import time
    host=tmp_path/'eof.py';host.write_text('import json,sys,time\nfor line in sys.stdin: print('+repr(json.dumps(SUMMARY))+',flush=True)\ntime.sleep(30)\n')
    engine=Engine('test',[sys.executable,str(host)],None,shutdown_timeout=.3)
    assert engine.fight({'seed':1})==[SUMMARY]
    start=time.monotonic()
    with pytest.raises(RuntimeError,match='combat host exit'):
        engine.close()
    assert time.monotonic()-start<2 and engine.process is None
