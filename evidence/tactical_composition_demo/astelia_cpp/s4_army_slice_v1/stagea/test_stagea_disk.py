"""Storage estimate provenance and explicit unchanged-binary sample recovery."""
import contextlib
import sys
import time
from pathlib import Path
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parent))
import collect
import disk_policy
from common import read,sha,write
from recording import CADENCE
from metrics import last_tick_time


def test_actual_a0_distribution_includes_censored_and_all_600():
    p=disk_policy.length_policy()
    assert p['fights']==600 and p['censored_fights']==8
    assert p['censored_seconds']==p['p99_seconds']==p['max_seconds']==150
    assert p['fight_length_bound_seconds']==150


def test_shorter_declared_bound_keeps_worst_case_free_space(tmp_path,monkeypatch):
    monkeypatch.setattr(collect,'LOCAL',tmp_path)
    monkeypatch.setattr(disk_policy,'length_policy',lambda:{'fight_length_bound_seconds':60})
    monkeypatch.setattr(collect.shutil,'disk_usage',lambda p:type('U',(),{'free':100_000_000_000})())
    # A different fight sets the byte/sec maximum; max(bytes) alone is insufficient.
    records=[dict(compressed_bytes=10_000_000,stats={'t_end':100}),
             dict(compressed_bytes=8_000_000,stats={'t_end':40})]
    p=collect.disk_projection(records,180,160)
    bounded=200_000*last_tick_time(60,1/30)
    worst=8_000_000*(last_tick_time(150,1/30)/40)
    assert p['bounded_fight_compact_bytes']==bounded
    assert p['projected_collection_bytes']==180*bounded
    assert p['worst_case_150s_projected_collection_bytes']==180*worst
    assert p['required_free_bytes']==2*160*worst+5_000_000_000
    # A measured longer fight cannot be projected below its already recorded bytes.
    assert collect.disk_projection(records[:1],180)['bounded_fight_compact_bytes']==10_000_000
    for records in ([],[dict(compressed_bytes=1,stats={'t_end':0})],
                    [dict(compressed_bytes=float('nan'),stats={'t_end':10})]):
        with pytest.raises(RuntimeError,match='measured fights|invalid disk calibration'):
            collect.disk_projection(records,180)


def recovery_fixture(tmp_path,monkeypatch):
    cpp=tmp_path/'cpp';here=cpp/'stagea';local=here/'_local';here.mkdir(parents=True)
    monkeypatch.setattr(collect,'CPP',cpp);monkeypatch.setattr(collect,'HERE',here)
    monkeypatch.setattr(collect,'LOCAL',local)
    binary=local/'build/host';binary.parent.mkdir(parents=True);binary.write_bytes(b'unchanged native binary')
    monkeypatch.setattr(collect,'BINARY',binary)
    (here/'collect.py').write_text('before');(here/'recording.py').write_text('unchanged recorder')
    def sources():return {str(p.relative_to(cpp)):sha(p) for p in here.glob('*.py')}
    monkeypatch.setattr(collect,'sources',sources)
    manifest=binary.with_suffix('.build.json')
    write(manifest,dict(schema=2,source_hashes=sources(),binary_sha256=sha(binary),
          engine='stagea',scope='native_complete_engine',sanitized=False,portable=False,commands=['original compiler']))
    def identity():
        m=read(manifest)
        assert sha(binary)==m['binary_sha256']
        for k,v in m['source_hashes'].items():assert sha(cpp/k)==v
        return dict(manifest_sha256=sha(manifest),binary_sha256=sha(binary),sources=m['source_hashes'],
                    **{k:m[k] for k in ('engine','scope','sanitized','portable')})
    monkeypatch.setattr(collect,'identity',identity)
    @contextlib.contextmanager
    def locked():yield
    import jobs
    monkeypatch.setattr(jobs,'locked',locked)
    jobs_list=[]
    for i in range(2):
        tag=f'train_{i:04d}';req=local/'requests'/(tag+'.json')
        write(req,dict(options={'duration':150,'dt':1/30},stageA={'collect':True}))
        jobs_list.append(dict(tag=tag,split='train',request_sha256=sha(req)))
    baseline=local/'DATA_LEDGER.json'
    write(baseline,dict(jobs=jobs_list,timing_sample=[j['tag'] for j in jobs_list],binary=identity(),sources=sources()))
    for j in jobs_list:
        raw=local/'raw'/(j['tag']+'.slim.xz');raw.parent.mkdir(exist_ok=True);raw.write_bytes(b'recorded bytes')
        write(local/'raw'/(j['tag']+'_COMPLETE.json'),dict(status='DONE',job=j,ledger_sha256=sha(baseline),
              raw_file=str(raw.relative_to(local)),raw_sha256=sha(raw),compressed_bytes=raw.stat().st_size,
              recording='STAGEASLIM1',recording_cadence=CADENCE,physical_dt=1/30,stats={'t_end':45},
              frames=1350,trajectory_sha256='trajectory',memory_profile=[]))
    (here/'collect.py').write_text('revised gating');(here/'disk_policy.py').write_text('new policy')
    return local,binary,manifest,jobs_list


def test_recovery_reuses_samples_and_resamples_changed_recording_without_overwrite(tmp_path,monkeypatch):
    local,binary,manifest,jobs=recovery_fixture(tmp_path,monkeypatch)
    second=local/'raw/train_0001_COMPLETE.json';r=read(second);r['recording_cadence']='other';write(second,r)
    originals={p:sha(p) for p in [binary,local/'DATA_LEDGER.json',*local.glob('requests/*.json'),*local.glob('raw/*')]}
    manifest_before=manifest.read_bytes()
    ledger=collect.recover_disk();note=collect.disk_note()
    assert ledger['jobs']==jobs and ledger['timing_sample']==[j['tag'] for j in jobs]
    assert note['collection_limit_bytes']==4_000_000_000
    assert list(note['reused'])==['train_0000'] and list(note['resample'])==['train_0001']
    assert not collect.completion_path(jobs[1]).exists() and collect.completion_path(jobs[1])!=second
    assert all(sha(p)==digest for p,digest in originals.items())
    assert (local/'disk_revision'/note['recovery_id']/'ORIGINAL.build.json').read_bytes()==manifest_before
    assert read(manifest)['commands']==['original compiler']
    assert collect.recover_disk()==ledger
    monkeypatch.setattr(collect,'validate_raw',lambda *a,**k:{key:read(collect.completion_path(jobs[0]))[key]
                       for key in ('stats','frames','trajectory_sha256','memory_profile')})
    receipt=collect.execute(jobs[0],time.monotonic()+10,None,sha(collect.ledger_path()))
    assert receipt['ledger_sha256']==note['previous_ledger_sha256']
    # A new result uses its registered destination, leaving the incompatible one intact.
    write(collect.completion_path(jobs[1]),dict(read(second),ledger_sha256=sha(collect.ledger_path())))
    collect.completion_identity(collect.completion_path(jobs[1]),read(collect.completion_path(jobs[1])),sha(collect.ledger_path()))
    assert sha(second)==originals[second]
    (local/receipt['raw_file']).write_bytes(b'tampered')
    with pytest.raises(RuntimeError,match='preserved evidence drift'):collect.check()


def test_unlogged_ledger_reuse_and_native_or_request_drift_refuse(tmp_path,monkeypatch):
    local,binary,manifest,jobs=recovery_fixture(tmp_path,monkeypatch)
    complete=collect.completion_path(jobs[0]);receipt=read(complete)
    with pytest.raises(RuntimeError,match='explicit recovery required'):
        collect.completion_identity(complete,receipt,'unregistered ledger')
    binary.write_bytes(b'changed binary')
    with pytest.raises(RuntimeError,match='unchanged admitted binary'):collect.recover_disk()
    binary.write_bytes(b'unchanged native binary')
    recorder=collect.HERE/'recording.py';recorder.write_text('changed recorder')
    with pytest.raises(RuntimeError,match='unauthorized source'):collect.recover_disk()
    recorder.write_text('unchanged recorder')
    (local/'requests/train_0000.json').write_text('{}')
    with pytest.raises(RuntimeError,match='sealed request drift'):collect.recover_disk()
    assert not (local/'DATA_DISK_RECOVERY_ACTIVE.json').exists()


def test_interrupted_manifest_install_resumes_exact_transaction(tmp_path,monkeypatch):
    local,binary,manifest,jobs=recovery_fixture(tmp_path,monkeypatch)
    original_write=collect.write
    def interrupt(path,value,**kw):
        if Path(path)==local/'DATA_DISK_RECOVERY_ACTIVE.json':raise OSError('interrupted activation')
        return original_write(path,value,**kw)
    monkeypatch.setattr(collect,'write',interrupt)
    with pytest.raises(OSError,match='interrupted activation'):collect.recover_disk()
    assert (local/'DATA_DISK_RECOVERY_PENDING.json').exists()
    assert not (local/'DATA_DISK_RECOVERY_ACTIVE.json').exists()
    monkeypatch.setattr(collect,'write',original_write)
    ledger=collect.recover_disk()
    assert ledger==collect.recover_disk()
    assert len(list((local/'disk_revision').iterdir()))==1


def test_a0_length_policy_rejects_receipt_tampering(tmp_path,monkeypatch):
    # No raw combat rerun is necessary: planning consumes hash-bound completion receipts.
    monkeypatch.setattr(disk_policy,'ARMY',tmp_path)
    path=tmp_path/'rev2/A0_LOOK_100.json';write(path,{'tampered':True})
    disk_policy.length_policy.cache_clear()
    try:
        with pytest.raises(RuntimeError,match='look receipt drift'):disk_policy.length_policy()
    finally:disk_policy.length_policy.cache_clear()


def test_marker_replace_interruption_does_not_publish_partial_json(tmp_path,monkeypatch):
    local,binary,manifest,jobs=recovery_fixture(tmp_path,monkeypatch)
    import common
    replace=common.os.replace
    marker=local/'DATA_DISK_RECOVERY_ACTIVE.json'
    def interrupt(source,target):
        if Path(target)==marker:raise OSError('interrupted atomic marker replacement')
        return replace(source,target)
    monkeypatch.setattr(common.os,'replace',interrupt)
    with pytest.raises(OSError,match='atomic marker replacement'):collect.recover_disk()
    assert not marker.exists() and marker.with_suffix('.json.tmp').exists()
    monkeypatch.setattr(common.os,'replace',replace)
    ledger=collect.recover_disk()
    assert read(marker)['ledger_sha256']==sha(collect.ledger_path())
    assert collect.check()==ledger


def test_revised_target_requires_measurement_exceeding_original(tmp_path,monkeypatch):
    local,binary,manifest,jobs=recovery_fixture(tmp_path,monkeypatch)
    # Scale the denominator to exceed 4 GB for two fights without huge raw fixtures.
    for job in jobs:
        p=collect.completion_path(job);r=read(p)
        r['stats']['t_end']=r['compressed_bytes']/(2_350_000_000/last_tick_time(150,1/30))
        write(p,r)
    ledger=collect.recover_disk();note=collect.disk_note()
    assert ledger['recovery']['collection_limit_bytes']==5_000_000_000
    assert 'exceeds original 4 GB' in note['collection_limit_cause']
    assert note['measured_projection']['projected_collection_bytes']==pytest.approx(4_700_000_000)


def test_logged_followup_source_revision_keeps_original_sample_provenance(tmp_path,monkeypatch):
    local,binary,manifest,jobs=recovery_fixture(tmp_path,monkeypatch)
    first=collect.recover_disk();first_note=collect.disk_note()
    first_ledger=collect.ledger_path();first_hash=sha(first_ledger)
    receipts={collect.completion_path(j):sha(collect.completion_path(j)) for j in jobs}
    # A subsequent authorized gating/test correction gets another identity.
    (collect.HERE/'collect.py').write_text('second gating revision')
    second=collect.recover_disk();second_note=collect.disk_note()
    assert second_note['recovery_id']!=first_note['recovery_id']
    assert second_note['previous_ledger_sha256']==first_hash and sha(first_ledger)==first_hash
    assert second['binary']['binary_sha256']==first['binary']['binary_sha256']
    for j in jobs:
        p=collect.completion_path(j);r=read(p)
        assert sha(p)==receipts[p]
        collect.completion_identity(p,r,sha(collect.ledger_path()))
        assert second_note['reused'][j['tag']]['ledger_sha256']==first_note['previous_ledger_sha256']
    assert collect.recover_disk()==second
    (collect.HERE/'collect.py').write_text('third gating revision')
    import common
    replace=common.os.replace
    def interrupt(source,target):
        if Path(target)==local/'DATA_DISK_RECOVERY_ACTIVE.json':raise OSError('sequential activation interrupted')
        return replace(source,target)
    monkeypatch.setattr(common.os,'replace',interrupt)
    with pytest.raises(OSError,match='sequential activation interrupted'):collect.recover_disk()
    assert collect.disk_note()['recovery_id']==second_note['recovery_id']
    monkeypatch.setattr(common.os,'replace',replace)
    collect.recover_disk()
    for j in jobs:
        p=collect.completion_path(j)
        assert sha(p)==receipts[p]
        collect.completion_identity(p,read(p),sha(collect.ledger_path()))
    assert sha(first_ledger)==first_hash
    first_ledger.write_text('{}')
    with pytest.raises(RuntimeError,match='preserved evidence drift'):collect.check()
