"""Focused cache parity, label isolation, dynamic N2 targets and corruption checks."""
import copy,time
import numpy as np
import pytest,torch
import runtime as r
import prepared_cache as pc
from hierarchy import partition,partition_batch
from native_candidates import batch,unpack,packed
from test_stageb2 import frame
from models import Policy,initial
import training
from loss import install

@pytest.fixture
def prepared(tmp_path):
    original=[frame() for _ in range(3)]
    original[1]['longVelocity']={'7':[8.,-12.]}
    original[1]['units'][0][3]+=1
    original[2]['shots']=[]
    raw=tmp_path/'raw';raw.write_bytes(b'fixture')
    f=dict(tag='fixture',raw_file=str(raw),raw_sha256=r.sha(raw),frames=len(original))
    def stream(path):
        assert str(path)==str(raw)
        return iter(copy.deepcopy(original))
    receipt=pc.prepare(tmp_path,dict(fights=[f]),stream,time.monotonic()+30)
    pc.activate(tmp_path,dict(fights=[f]),stream)
    cached=list(pc.frames(raw))
    yield original,cached,receipt,tmp_path,f,stream
    pc.ACTIVE=pc.LOADED=pc.LAST=None

@pytest.mark.parametrize('arm',r.ARMS)
def test_forward_loss_gradients_and_no_epoch_regeneration(prepared,arm,monkeypatch):
    originals,cached,*_=prepared
    install({role:dict(weights=[1.3,2.7]) for role in ('melee','ranged','artillery')})
    torch.manual_seed(73);a=Policy(arm).float();b=copy.deepcopy(a)
    contexts=[(initial(arm,[]),[],None,(0,[])) for _ in range(2)]
    loss=[0,0]
    # Native exact banks as the old loader would produce, outside the timed path.
    for row in originals:row['_candidate_banks']=unpack(batch(row))
    import native_candidates,hierarchy
    monkeypatch.setattr(native_candidates,'batch_packet',lambda *a,**k:(_ for _ in ()).throw(AssertionError('epoch regeneration')))
    monkeypatch.setattr(hierarchy,'partition_batch',lambda *a,**k:(_ for _ in ()).throw(AssertionError('epoch partition')))
    for rows in zip(originals,cached):
        outputs=[]
        for i,(row,model) in enumerate(zip(rows,(a,b))):
            y,state,ids,enemies,cache,clock,_=training.forward(model,row,*contexts[i],supervised=True)
            contexts[i]=(state,ids,cache,clock);outputs.append(y)
            value,heads=training.objective(y,row,ids,enemies);loss[i]=loss[i]+value
        for key in outputs[0]:torch.testing.assert_close(outputs[0][key],outputs[1][key],rtol=0,atol=0)
        torch.testing.assert_close(contexts[0][0],contexts[1][0],rtol=0,atol=0)
    torch.testing.assert_close(loss[0],loss[1],rtol=0,atol=0)
    for value in loss:value.backward()
    for (ka,pa),(kb,pb) in zip(a.named_parameters(),b.named_parameters()):
        assert ka==kb
        if pa.grad is not None:torch.testing.assert_close(pa.grad,pb.grad,rtol=1e-6,atol=1e-7)

@pytest.mark.parametrize('arm',r.ARMS)
def test_labels_never_enter_inference_and_prefixes(prepared,arm):
    original,cached,*_=prepared;model=Policy(arm).float().eval()
    row=cached[0];changed=dict(row,labels=[])
    with torch.no_grad():
        a,*_=training.forward(model,row,initial(arm,[]),[],None,(0,[]))
        b,*_=training.forward(model,changed,initial(arm,[]),[],None,(0,[]))
        for key in a:torch.testing.assert_close(a[key],b[key],rtol=0,atol=0)
        a,*_=training.forward(model,original[0],initial(arm,[]),[],None,(0,[]),state_only=True)
        b,*_=training.forward(model,row,initial(arm,[]),[],None,(0,[]),state_only=True)
        torch.testing.assert_close(a['drift'],b['drift'],rtol=0,atol=0)

def test_family_batch_exact_ties_and_boundaries():
    row=frame();row['units'][0][11]=400
    banks=packed(unpack(batch(row)),[1,4])
    for head in ('aim','move'):
        f=banks[head+'_features'];v=banks[head+'_valid']
        # Equal bins exercise original ordinal tie breaking.
        f[:,:,13]=np.floor(f[:,:,13]*2)/2
        old=partition(f,v,head);new=partition_batch(f,v,head)
        for a,b in zip(old,new):np.testing.assert_array_equal(a,b)

def test_reuse_and_corruption_refused(prepared):
    _,_,receipt,root,f,stream=prepared
    again=pc.prepare(root,dict(fights=[f]),stream,time.monotonic()+30)
    assert again['compressed_bytes']==receipt['compressed_bytes']
    meta=r.read(pc.location(root,f));chunk=root/meta['chunks'][0]['file']
    chunk.write_bytes(chunk.read_bytes()+b'corruption')
    with pytest.raises(RuntimeError,match='content drift'):list(pc.frames(f['raw_file']))

def test_metadata_corruption_refused(prepared):
    _,_,_,root,f,_=prepared
    meta=pc.location(root,f);meta.write_text(meta.read_text()+' ')
    with pytest.raises(RuntimeError,match='metadata content drift'):list(pc.frames(f['raw_file']))

@pytest.mark.parametrize('kind',('N1b','N1rb','N2'))
def test_batched_peer_readout_matches_original_loop(kind):
    torch.manual_seed(123)
    n,e,k=11,7,8
    order=torch.randint(n,(n,k));mask=torch.rand(n,k)>.2
    assignments=torch.randint(e+1,(n,));enemy=torch.arange(1,e+1)
    base=torch.randn(n,e+1,requires_grad=True)
    theta=torch.randn(n,requires_grad=True);z=torch.stack((torch.sin(theta),torch.cos(theta)),-1)
    old=base.clone()
    for i,target in enumerate(enemy):
        peers=mask & (assignments[order]==target)
        if kind=='N2':
            group=(z[order]*peers[...,None]).sum(1)/peers.sum(1).clamp_min(1)[:,None]
            length=torch.linalg.vector_norm(group,dim=-1)
            old[:,i+1]=old[:,i+1]+2*(z*group/length.clamp_min(1e-6)[:,None]).sum(1)*(length>=1e-6)
        else:old[:,i+1]=old[:,i+1]+2*peers.any(1)
    peers=mask[...,None] & (assignments[order][...,None]==enemy[None,None,:])
    if kind=='N2':
        group=(z[order][:,:,None,:]*peers[...,None]).sum(1)/peers.sum(1).clamp_min(1)[...,None]
        length=torch.linalg.vector_norm(group,dim=-1)
        adjustment=2*(z[:,None,:]*group/length.clamp_min(1e-6)[...,None]).sum(-1)*(length>=1e-6)
    else:adjustment=2*peers.any(1)
    new=torch.cat((base[:,:1],base[:,1:]+adjustment),-1)
    torch.testing.assert_close(old,new,rtol=0,atol=0)
    if kind=='N2':
        ga=torch.autograd.grad(old.sum(),theta,retain_graph=True)[0]
        gb=torch.autograd.grad(new.sum(),theta)[0]
        torch.testing.assert_close(ga,gb,rtol=1e-6,atol=1e-6)

def test_n2_nearest_is_recomputed_from_current_drift(prepared):
    originals,cached,*_=prepared
    # Poison the static movement nearest: N2 must never consume it.
    for law in (-8.,8.):
        model=Policy('N2').float()
        with torch.no_grad():model.law.fill_(law)
        row=cached[0];arrays=row['_prepared'].arrays();arrays['move_nearest'][:]=-999
        with torch.no_grad():
            a,*_=training.forward(model,originals[0],initial('N2',[]),[],None,(0,[]),supervised=True)
            b,*_=training.forward(model,row,initial('N2',[]),[],None,(0,[]),supervised=True)
        for key in a:torch.testing.assert_close(a[key],b[key],rtol=0,atol=0)

def test_declared_head_windows_prefix_coverage_and_memory_bound(tmp_path):
    raw=tmp_path/'raw';raw.write_bytes(b'fixture')
    f=dict(tag='prefix',raw_file=str(raw),raw_sha256=r.sha(raw),frames=540)
    row=frame();stream=lambda path:(copy.deepcopy(row) for _ in range(f['frames']))
    result=pc.prepare(tmp_path,dict(fights=[f]),stream,time.monotonic()+60)
    assert result['cached_frames']==360
    pc.activate(tmp_path,dict(fights=[f]),stream)
    for tick,row in enumerate(pc.frames(raw)):
        arrays=row['_prepared'].arrays()
        assert ('codec_arena' in arrays)==(tick in pc.selected_ticks(f['frames']))
        assert 'tokens' in arrays and 'graph_order' in arrays
    meta=r.read(pc.location(tmp_path,f))
    assert all(q['uncompressed_bytes']<=pc.MAX_CHUNK_BYTES for q in meta['chunks'])
    pc.ACTIVE=pc.LOADED=pc.LAST=None


def test_codec_all_bits_shape_resets_disappearance_and_chunks():
    from cache_codec import encode_arrays,decode_frame
    rng=np.random.default_rng(4001)
    # Include signed zeros, arbitrary float mantissas and nonfinite bit patterns:
    # the codec is integer transport, not numeric quantization.
    originals=[]
    for tick,size in enumerate((23,23,23,13,13,0,23,23)):
        arrays=dict(f=rng.integers(0,2**32,size,dtype=np.uint32).view(np.float32),
                    d=rng.integers(0,2**64,size,dtype=np.uint64).view(np.float64),
                    i=rng.integers(0,65536,size,dtype=np.uint16).view(np.int16),
                    b=rng.integers(0,2,size,dtype=np.uint8).view(np.bool_))
        if tick==4:arrays.pop('i')
        originals.append(arrays)
    for group in (originals[:4],originals[4:]):
        encoder={};decoder={}
        for arrays in group:
            blob,layout=encode_arrays(arrays,encoder)
            value=np.frombuffer(blob,dtype=np.uint8).copy()
            decode_frame(value,layout,decoder)
            for name,dtype,shape,at,size,mode in layout:
                rebuilt=np.frombuffer(value[at:at+size],dtype=dtype).reshape(shape)
                np.testing.assert_array_equal(rebuilt.view(np.uint8).ravel(),arrays[name].view(np.uint8).ravel())


def test_geometry_predictors_are_lossless_bit_corrections():
    from cache_codec import compress_banks,expand_banks,image_mask
    row=frame();row['units'][0][11]=400;row['units'][0][18]=130
    row['units'][0][5:7]=[500.,-800.];row['longVelocity']={'1':[1111.,2222.]}
    value=pc.build(row,True);compressed=compress_banks(value)
    assert image_mask(compressed).any()
    original={k:v.copy() for k,v in value.items() if not k.endswith('_codec_points') and k!='native_packet'}
    expanded=expand_banks(compressed)
    for k,v in original.items():np.testing.assert_array_equal(expanded[k].view(np.uint8).ravel(),v.view(np.uint8).ravel())

def test_training_tensors_do_not_retain_whole_shards(prepared):
    _,cached,*_=prepared
    obj=cached[0]['_prepared']
    for values in (obj.tensors(torch.float32),obj.label_tensors(torch.float32)):
        for tensor in values.values():assert tensor.untyped_storage().nbytes()==tensor.numel()*tensor.element_size()


@pytest.mark.parametrize('arm',('N1','N1b','N1r','N1rb','N2'))
def test_sparse_windows_preserve_physical_prefix_contexts(arm,monkeypatch):
    original=[frame() for _ in range(181)]
    for i,row in enumerate(original):
        row['tick']=i;row['units'][0][3]+=i*.02
    monkeypatch.setattr(training,'frames',lambda path:iter(copy.deepcopy(original)))
    monkeypatch.setattr(training,'live_check',lambda:None)
    fight=dict(raw_file='fixture',frames=len(original))
    torch.manual_seed(701);model=Policy(arm).float().eval()
    expected={};context=(initial(arm,[]),[],None,(0,[]))
    with torch.no_grad():
        for i,row in enumerate(original):
            if i in training.selected_starts(len(original),2):expected[i]=copy.deepcopy(context)
            if arm not in ('N1','N1b'):
                y,state,ids,enemies,cache,clock,_=training.forward(model,row,*context,state_only=True)
                context=(state,ids,cache,clock)
    rows,saved,_=training.stored(model,fight,2,time.monotonic()+30)
    assert len(rows)==181 and set(rows.rows)==set(range(90))|{180}
    assert [q['tick'] for q in rows[0:90]]==list(range(90))
    assert [q['tick'] for q in rows[180:270]]==[180]
    with pytest.raises(KeyError):rows[100]
    reloaded=training.window_rows(fight,2)
    assert set(reloaded.rows)==set(rows.rows)
    for tick,values in expected.items():
        got=saved[tick]
        for a,b in zip(values,got):
            if torch.is_tensor(a):torch.testing.assert_close(a,b,rtol=0,atol=0)
            elif a is None:assert b is None
            else:assert a==b


def test_deferred_heads_expand_after_prefix_access(prepared):
    _,cached,*_=prepared
    obj=cached[0]['_prepared'];pc.LAST=None
    assert 'aim_points' not in obj.arrays(heads=False)
    assert 'aim_points' in obj.arrays(heads=True)


def test_compact_rows_skip_raw_epoch_reads_and_authenticate(prepared,monkeypatch):
    _,_,_,root,f,_=prepared
    monkeypatch.setattr(pc,'BASE_FRAMES',lambda path:(_ for _ in ()).throw(AssertionError('raw epoch read')))
    rows=list(pc.frames(f['raw_file']))
    assert rows[0]['labels'][0]['executed']
    assert rows[0]['own'] and all(len(u)==10 for u in rows[0]['own'])
    with pytest.raises(RuntimeError,match='original raw frames'):
        training.forward(Policy('N1').double(),rows[0],initial('N1',[],torch.float64),[],None,(0,[]))
    meta=r.read(pc.location(root,f));path=root/meta['rows_file']
    path.write_bytes(path.read_bytes()+b'drift')
    with pytest.raises(RuntimeError,match='row metadata drift'):list(pc.frames(f['raw_file']))


@pytest.mark.parametrize('arm',r.ARMS)
def test_compact_rows_preserve_calibration_safety(prepared,arm,monkeypatch):
    from calibration import collect_scores
    originals,cached,_,_,fight,_=prepared
    torch.manual_seed(908);model=Policy(arm).float().eval()
    monkeypatch.setattr(r.data,'frames',lambda path:iter(copy.deepcopy(originals)))
    a=collect_scores(model,[fight],time.monotonic()+30)
    monkeypatch.setattr(r.data,'frames',lambda path:iter(cached))
    b=collect_scores(model,[fight],time.monotonic()+30)
    assert a==b


def test_native_parity_uses_raw_rows_after_training_cache_activation(prepared,monkeypatch):
    _,_,_,_,fight,_=prepared
    monkeypatch.setattr(r.data,'frames',pc.frames)
    import parity,calibrated_parity,importlib
    # Cover imports after activation, not just the usual CLI import order.
    importlib.reload(parity);importlib.reload(calibrated_parity)
    assert parity.frames is r.frames and calibrated_parity.frames is r.frames


def test_native_reverse_mapping_refuses_invalid_members():
    from native_cache_codec import mapping
    members=np.full((2,3,64),-1,dtype=np.int16);members[1,2,61]=19
    with pytest.raises(ValueError,match='out of bounds'):mapping(members,19)
    members[1,2,61]=18;out=mapping(members,19)
    np.testing.assert_array_equal(out[1,18],[2,61])
    assert (out[0]==-1).all()
