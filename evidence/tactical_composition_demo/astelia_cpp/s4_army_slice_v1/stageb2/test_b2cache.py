"""Lossless regeneration, window isolation, bounded storage and training parity."""
import copy,time
import numpy as np
import pytest
import torch
import runtime as r
import candidate_cache as cc
from native_candidates import batch,batch_packet,packet,unpack
from test_stageb2 import frame
from models import Policy,initial
from training import forward

@pytest.mark.parametrize('kind',r.ARMS)
def test_cached_full_heads_labels_and_prefix_exact(kind,tmp_path):
    rows=[frame(),frame()];rows[1]['longVelocity']={'7':[8.,-12.]}
    raw=tmp_path/'raw';raw.write_bytes(b'fixture')
    f=dict(tag='fixture',raw_file=str(raw),raw_sha256=r.sha(raw),frames=len(rows))
    stream=lambda path:iter(copy.deepcopy(rows))
    receipt=cc.prepare(tmp_path,dict(fights=[f]),stream,time.monotonic()+30)
    assert receipt['compressed_bytes']<100_000
    cc.activate(tmp_path,dict(fights=[f]),stream)
    cached=list(cc.frames(raw))
    torch.manual_seed(73);model=Policy(kind).float().eval()
    contexts=[(initial(kind,[]),[],None,(0,[])) for _ in range(2)]
    from candidates import mapped_labels
    with torch.no_grad():
        for original,loaded in zip(rows,cached):
            for id,v in unpack(batch(original)).items():
                for a,b in zip(v,loaded['_candidate_banks'][id]):np.testing.assert_array_equal(a.view(np.uint64),b.view(np.uint64))
            outs=[]
            for i,row in enumerate((original,loaded)):
                y,state,ids,enemies,cache,clock,_=forward(model,row,*contexts[i]);contexts[i]=(state,ids,cache,clock);outs.append(y)
            for key in outs[0]:torch.testing.assert_close(outs[0][key],outs[1][key],rtol=0,atol=0)
            torch.testing.assert_close(contexts[0][0],contexts[1][0],rtol=0,atol=0)
            assert mapped_labels(original,ids,outs[0]['drift'].numpy())==mapped_labels(loaded,ids,outs[1]['drift'].numpy())
    cc.ACTIVE=None


def test_only_declared_windows_and_inputs_are_cached(tmp_path,monkeypatch):
    # 720 physical frames; four 90-frame windows, with uncached state prefixes.
    row=frame();raw=tmp_path/'raw';raw.write_bytes(b'fixture')
    f=dict(tag='windows',raw_file=str(raw),raw_sha256=r.sha(raw),frames=720)
    def stream(path):
        for tick in range(720):
            value=copy.deepcopy(row);value['t']=tick/30;yield value
    calls=[];original=cc.packet
    monkeypatch.setattr(cc,'packet',lambda row:(calls.append(row['t']),original(row))[1])
    receipt=cc.prepare(tmp_path,dict(fights=[f]),stream,time.monotonic()+30)
    assert receipt['cached_frames']==360 and len(calls)==360
    cc.activate(tmp_path,dict(fights=[f]),stream)
    loaded=list(cc.frames(raw))
    assert len(loaded)==720
    assert [i for i,row in enumerate(loaded) if '_candidate_banks' in row]==cc.selected_ticks(720)
    assert all(isinstance(row['_candidate_banks'],cc.LazyBank) for row in loaded if '_candidate_banks' in row)
    # Candidate generation is deferred, not part of prefix iteration.
    assert cc.LAST_BANK is None
    a=frame();b=copy.deepcopy(a);b['labels']=[];b['history']={};b['dt']=.1
    np.testing.assert_array_equal(packet(a).view(np.uint64),packet(b).view(np.uint64))
    cc.ACTIVE=None


def test_multichunk_xor_and_old_cache_isolation(tmp_path,monkeypatch):
    row=frame();raw=tmp_path/'raw';raw.write_bytes(b'fixture')
    f=dict(tag='chunks',raw_file=str(raw),raw_sha256=r.sha(raw),frames=5)
    rows=[copy.deepcopy(row) for _ in range(5)]
    for tick,value in enumerate(rows):value['units'][0][3]+=tick
    rows[2]['shots']=[] # changed packet length resets XOR dependency
    monkeypatch.setattr(cc,'MAX_CHUNK_BYTES',len(packet(row))*8*2)
    stream=lambda path:iter(copy.deepcopy(rows))
    receipt=cc.prepare(tmp_path,dict(fights=[f]),stream,time.monotonic()+30)
    assert len(receipt['records'][0]['chunks'])>=3
    assert cc.identity(f)['schema']==3
    cc.activate(tmp_path,dict(fights=[f]),stream)
    for original,cached in zip(rows,cc.frames(raw)):
        for id,v in unpack(batch(original)).items():
            for a,b in zip(v,cached['_candidate_banks'][id]):np.testing.assert_array_equal(a.view(np.uint64),b.view(np.uint64))
    cc.ACTIVE=None


@pytest.mark.parametrize('change',[lambda x:x.__setitem__(2,-1),lambda x:x.__setitem__(3,.5),lambda x:x.__setitem__(0,float('nan')),lambda x:x.__setitem__(8,129)])
def test_malformed_packet_refused(change):
    value=packet(frame());change(value)
    with pytest.raises(ValueError,match='packet'):batch_packet(value)


def test_representative_recorded_rows_exact_and_size(tmp_path):
    """Small real-data replay; no fights, optimizer, or production admissions."""
    from train import timing_fights
    index=r.read(r.LOCAL/'round0/INDEX.json')
    chosen=sum((timing_fights([f for f in index['fights'] if f['split']==split]) for split in ('train','validation')),[])
    samples=[];report=[];started=time.monotonic()
    for fight in chosen:
        wanted={cc.selected_ticks(fight['frames'])[0],cc.selected_ticks(fight['frames'])[-1]}
        selected=[]
        for tick,row in enumerate(r.frames(fight['raw_file'])):
            if tick in wanted:selected.append(row)
        raw=tmp_path/(fight['tag']+'.json')
        # Explicitly a new two-row fixture; never label it as a full raw fight.
        r.write(raw,dict(status='TEST_ONLY',source_sha256=fight['raw_sha256'],rows=selected))
        sample=dict(tag=fight['tag'],frames=len(selected),raw_file=str(raw),raw_sha256=r.sha(raw))
        def stream(path):yield from copy.deepcopy(r.read(path)['rows'])
        receipt=cc.prepare(tmp_path,dict(fights=[sample]),stream,time.monotonic()+60)
        cc.activate(tmp_path,dict(fights=[sample]),stream)
        reference_bytes=0;max_input=0
        for original,cached in zip(selected,cc.frames(raw)):
            reference=batch(original);reference_bytes+=reference.nbytes;max_input=max(max_input,packet(original).nbytes)
            for id,v in unpack(reference).items():
                for a,b in zip(v,cached['_candidate_banks'][id]):np.testing.assert_array_equal(a.view(np.uint64),b.view(np.uint64))
        report.append(dict(tag=fight['tag'],split=fight['split'],panel=fight['panel'],sample_ticks=sorted(wanted),sample_rows=len(selected),input_uncompressed_bytes=receipt['records'][0]['uncompressed_bytes'],compressed_bytes=receipt['compressed_bytes'],candidate_float64_bytes=reference_bytes,build_seconds=receipt['seconds'],max_input_bytes=max_input))
        samples.append(receipt);cc.ACTIVE=None
    total_selected=sum(len(cc.selected_ticks(f['frames'])) for f in index['fights'])
    # Existing valid public envelope: 64 actors per side, capped threat banks;
    # longVelocity has at most one row per actor. Lossless uncompressed upper
    # bound for every window row, before compression/container overhead.
    envelope_bytes=8*(9+128*23+64*10+64*9+64*7+32*5+32*7+128*3)
    upper=total_selected*envelope_bytes
    assert upper<cc.DISK_LIMIT_BYTES
    result=dict(status='TEST_ONLY',parity='bitwise float64 all candidates/features/types/sources on recorded window endpoints',records=report,seconds=time.monotonic()-started,full_index_sha256=r.sha(r.LOCAL/'round0/INDEX.json'),full_window_rows=total_selected,full_input_uncompressed_upper_bytes=upper,full_compressed_projection_bytes=sum(x['compressed_bytes'] for x in report)/sum(x['sample_rows'] for x in report)*total_selected,limits='Four timing fights, two endpoints each; not full cache or fit timing. ZIP/meta overhead excluded from uncompressed input upper bound. Native regeneration is timed by host measure.')
    r.write(r.HERE/'B2CACHE_RECORDED_SAMPLE.json',result)
