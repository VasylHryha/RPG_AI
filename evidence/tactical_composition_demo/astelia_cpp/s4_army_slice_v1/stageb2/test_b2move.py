"""Focused ordinary geometry, input purity, record layout and envelope checks."""
import copy,math,time
import numpy as np
import pytest
from test_stageb2 import frame
from candidates import bank,MAX_MOVE,FEATURES
from movement import ordinary_points
from native_candidates import batch,unpack,packed

def points(row,id):
    units=sorted(row['units'],key=lambda u:u[0]);own=next(u for u in units if u[0]==id)
    return ordinary_points(row,own,units)

def has(values,p,typ):
    return any(t==typ and np.linalg.norm(np.asarray(q)-p)<1e-10 for q,t,_ in values)

def test_known_anchor_escort_body_band_and_repulsion():
    row=frame();units=row['units'];units[0][3:5]=[100.,100.];units[1][3:5]=[150.,100.]
    units[2][3:5]=[400.,100.];units[3][3:5]=[350.,100.]
    row['width']=600.;row['height']=400.
    ranged=points(row,4);assert has(ranged,[160.,100.],18)
    # Body-expanded reach180+8+8 => nearest enemy350, radial point154.
    assert has(ranged,[154.,100.],23)
    artillery=points(row,1);assert has(artillery,[172.,100.],19)
    assert has(ranged,[350.,100.],21);assert has(ranged,[350.,100.],23)
    gun=copy.deepcopy(units[0]);gun[0]=6;gun[3:5]=[100.,100.]
    row['units'].append(gun);state=copy.deepcopy(row['own'][0]);state[0]=6;row['own'].append(state)
    artillery=points(row,1);assert has(artillery,[40.,100.],24)
    assert has(artillery,[112.,100.],20)

def test_full_public_velocity_continuation_and_label_independence():
    row=frame();row['units'][0][5:7]=[3.,4.];row['longVelocity']={'1':[0.,10.]}
    a=points(row,1);assert has(a,[155.,200.],22);assert has(a,[35.,240.],22)
    assert has(a,[38.,44.],22);assert has(a,[35.,50.],22)
    changed=copy.deepcopy(row);changed['labels']=[{'private':'bad'}];changed['history']={'1':[999]*16};changed['pairModes']={'1:7':True};changed['networkState']=[[999]];changed['shadowLabels']=[{'goal':[999,999]}]
    assert points(changed,1)==a
    b=packed(unpack(batch(row)),[1,4]);c=packed(unpack(batch(changed)),[1,4])
    for key in b:np.testing.assert_array_equal(b[key],c[key])

@pytest.mark.parametrize('empty',[False,True])
def test_native_python_descriptor_types_sources_and_record_width(empty):
    row=frame();row['longVelocity']={'1':[10.,-2.],'4':[0.,5.]}
    if empty:row['units']=row['units'][:2]
    row['units'].reverse();native=packed(unpack(batch(row)),[1,4])
    for i,id in enumerate((1,4)):
        reference,_=bank(row,id)
        for key in reference:np.testing.assert_allclose(reference[key],native[key][i],atol=1e-11,rtol=1e-12)
        assert native['move_features'].shape[-1]==FEATURES==26
        count=int(reference['move_valid'].sum());assert 0<count<=MAX_MOVE
        assert native['move_valid'][i,0]==1

def test_maximum_public_envelope_and_all_new_types_are_selectable():
    row=frame();own=row['units'][0];enemy=row['units'][2];state=row['own'][0]
    row['units']=[];row['own']=[]
    for i in range(64):
        u=copy.deepcopy(own);u[0]=i+1;u[3:5]=[40.+i%8*3,40.+i//8*3];row['units'].append(u)
        s=copy.deepcopy(state);s[0]=i+1;row['own'].append(s)
        e=copy.deepcopy(enemy);e[0]=i+101;e[3:5]=[210.+i%8*5,140.+i//8*5];row['units'].append(e)
    row['shots']=row['shots']*64;row['fields']=row['fields']*32;row['shells']=row['shells']*64;row['casts']=row['casts']*32
    arrays,items=bank(row,1);assert len(items['move'])<=1226<=MAX_MOVE
    native=unpack(batch(row));assert len(native)==64
    assert max(len(v[1]) for v in native.values())<=MAX_MOVE
    for key,value in packed(native,[1]).items():np.testing.assert_allclose(value[0],arrays[key],atol=1e-10,rtol=1e-12)
    types={t for _,_,t,_ in items['move']};assert {19,20,21,22,23,24,25}<=types
    ranged=copy.deepcopy(row);ranged['units'][0][2]=1
    assert 18 in {t for _,t,_ in points(ranged,1)}

def test_direction_ring_error_and_clamp_are_bounded():
    row=frame();row['width']=1400;row['height']=800;row['units'][0][3:5]=[700.,400.]
    ring=[q for q,t,s in points(row,1) if t==25 and s==-1]
    assert len(ring)==64
    error=400*math.sin(math.pi/128)
    for j in range(257):
        angle=j*2*math.pi/257;p=np.array([700+200*math.cos(angle),400+200*math.sin(angle)])
        assert min(np.linalg.norm(np.asarray(q)-p) for q in ring)<=error+1e-10

def test_lazy_chunks_bitwise_ragged_reuse_and_corruption(tmp_path,monkeypatch):
    import candidate_cache as cc
    rows=[]
    for tick in range(12):
        row=frame();row['t']=(tick+1)/30;row['units'][0][3]+=tick/7
        if tick%3==1:row['units']=row['units'][:-1]
        rows.append(row)
    raw=tmp_path/'raw';raw.write_text('fixture');f=dict(tag='chunks',raw_file=str(raw),raw_sha256=__import__('common').sha(raw),frames=len(rows));index=dict(fights=[f])
    def stream(path):yield from copy.deepcopy(rows)
    monkeypatch.setattr(cc,'MAX_CHUNK_BYTES',80_000)
    receipt=cc.prepare(tmp_path,index,stream,time.monotonic()+30)
    chunks=receipt['records'][0]['chunks'];assert len(chunks)>1
    cc.activate(tmp_path,index,stream);loaded=list(cc.frames(raw));assert cc.LOADED is None
    assert all(isinstance(row['_candidate_banks'],cc.LazyBank) for row in loaded)
    for at in (11,0,7,1,3,6,4,5,2,8,9,10):
        expected=unpack(batch(rows[at]));actual=loaded[at]['_candidate_banks']
        for id in expected:
            for a,b in zip(actual[id],expected[id]):np.testing.assert_array_equal(a,b)
    timestamps=[(tmp_path/q['file']).stat().st_mtime_ns for q in chunks]
    reused=cc.prepare(tmp_path,index,stream,time.monotonic()+30)
    assert [q['sha256'] for q in reused['records'][0]['chunks']]==[q['sha256'] for q in chunks]
    assert timestamps==[(tmp_path/q['file']).stat().st_mtime_ns for q in chunks]
    (tmp_path/chunks[-1]['file']).write_bytes(b'corrupt')
    with pytest.raises(RuntimeError,match='content drift'):list(cc.frames(raw))
    cc.ACTIVE=None;cc.LOADED=cc.LAST_BANK=None

def test_cache_windows_keep_full_prefix_and_state_only_never_loads(tmp_path,monkeypatch):
    import candidate_cache as cc
    from models import Policy,initial
    from training import forward
    import torch
    raw=tmp_path/'raw';raw.write_text('fixture');f=dict(tag='prefix',raw_file=str(raw),raw_sha256=__import__('common').sha(raw),frames=501);index=dict(fights=[f])
    def stream(path):
        for tick in range(501):
            row=frame();row['t']=(tick+1)/30;yield row
    monkeypatch.setattr(cc,'batch',lambda row:np.asarray([1.,0.,0.]))
    cc.prepare(tmp_path,index,stream,time.monotonic()+30);cc.activate(tmp_path,index,stream)
    loaded=list(cc.frames(raw));assert len(loaded)==501
    cached={i for i,row in enumerate(loaded) if '_candidate_banks' in row}
    assert cached==set(range(180))|set(range(270,360))|set(range(450,501))
    monkeypatch.setattr(cc.LazyBank,'values_for_frame',lambda self:(_ for _ in ()).throw(AssertionError('state-only loaded bank')))
    model=Policy('N2').double();context=(initial('N2',[],torch.float64),[],None,(0,[]))
    with torch.no_grad():
        for row in loaded[:4]:
            _,state,ids,_,cache,clock,_=forward(model,row,*context,state_only=True);context=(state,ids,cache,clock)
    assert cc.LOADED is None
    cc.ACTIVE=None

def test_coverage_preserves_stale_receipt_and_refuses_same_code(tmp_path):
    import common as c
    from coverage import preserve_previous
    path=tmp_path/'COVERAGE.json';old=dict(sources={'old':'hash'},index_sha256='index',status='DONE')
    c.write(path,old);original=path.read_bytes();digest=c.sha(path)
    archive=preserve_previous(tmp_path,{'new':'hash'},'index')
    assert not path.exists() and c.read(archive['path'])==old
    assert __import__('pathlib').Path(archive['path']).read_bytes()==original and archive['sha256']==digest
    c.write(path,dict(sources={'new':'hash'},index_sha256='index'))
    with pytest.raises(RuntimeError,match='same-code'):preserve_previous(tmp_path,{'new':'hash'},'index')
