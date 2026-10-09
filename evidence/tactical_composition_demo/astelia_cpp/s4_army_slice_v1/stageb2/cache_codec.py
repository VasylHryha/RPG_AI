"""Lossless bank predictors and typed temporal bit coding; never round outputs.

Geometry merely predicts bits for compression. Stored modular corrections make
all reconstructed float32 inputs bit-identical even when a prediction is wrong.
"""
import numpy as np

def direction(delta):
    length=np.hypot(delta[...,0],delta[...,1])
    out=delta/np.where(length>0,length,1)[...,None]
    return np.where((length>0)[...,None],out,np.array([1.,0.]))

def context(packet):
    units=packet[9:9+int(packet[2])*23].reshape(-1,23)
    units=units[np.argsort(units[:,0])];own=units[units[:,1]==0];enemy=units[units[:,1]==1]
    n=len(own)
    nearest=enemy[np.hypot(*(own[:,None,3:5]-enemy[None,:,3:5]).transpose(2,0,1)).argmin(1)] if len(enemy) else own
    d=own[:,None,3:5]-own[None,:,3:5];length=np.hypot(d[:,:,0],d[:,:,1])
    same=np.eye(n,dtype=bool)
    friend=(~same)&((own[:,None,2]!=2)|(own[None,:,2]==2))
    fallback=np.stack((np.where(own[:,None,0]<own[None,:,0],-1.,1.),np.zeros_like(length)),-1)
    dirs=np.where((length>0)[...,None],direction(d),fallback)
    shift=(dirs*np.maximum(0.,60-length)[...,None]*friend[...,None]).sum(1)
    guns=own[own[:,2]==2]
    gun=guns[np.hypot(*(own[:,None,3:5]-guns[None,:,3:5]).transpose(2,0,1)).argmin(1)] if len(guns) else own
    centre=enemy[:,3:5].sum(0)/len(enemy) if len(enemy) else np.zeros(2)
    artillery=enemy[enemy[:,2]==2]
    artcentre=artillery[:,3:5].sum(0)/len(artillery) if len(artillery) else centre
    offset=9+int(packet[2:8]@np.array([23,10,9,7,5,7]))
    velocities=packet[offset:].reshape(-1,3)
    long=own[:,5:7].copy()
    if len(velocities):
        velocities=velocities[np.argsort(velocities[:,0])]
        index=np.searchsorted(velocities[:,0],own[:,0]);safe=np.minimum(index,len(velocities)-1)
        match=(index<len(velocities))&(velocities[safe,0]==own[:,0])
        long[match]=velocities[safe[match],1:]
    reach=np.maximum(1.,enemy[:,11]);cycle=np.maximum(.001,enemy[:,14])
    threat=np.column_stack((enemy[:,3:5]+enemy[:,5:7]*.5,enemy[:,12]/cycle/100,1/(reach*reach)))
    return dict(codec_threat=threat,codec_velocity=np.stack((own[:,5:7],long),1),codec_units=units,codec_own=own,codec_nearest=nearest,codec_shift=shift,codec_gun=gun,codec_centre=centre,codec_artcentre=artcentre)

def image_mask(arrays):
    types=arrays['move_types'];previous=np.pad(types[:,:-1],((0,0),(1,0)),constant_values=-1)
    return (types==23)&np.isin(previous,[24,21,19,20,18,22])


def compress_banks(arrays):
    if 'native_packet' not in arrays:return arrays
    out=dict(arrays);out.update(context(arrays['native_packet']));out['codec_arena']=out.pop('native_packet')[:2].copy()
    from native_cache_codec import bank,mapping
    for head in ('aim','move'):
        out.pop(head+'_points');points=out.pop(head+'_codec_points');numeric=out.pop(head+'_numeric')
        predicted_points,predicted_numeric=bank(out,head,points)
        out[head+'_point_bits']=points.view(np.uint64)-predicted_points.view(np.uint64)
        out[head+'_numeric_bits']=numeric.view(np.uint32)-predicted_numeric.view(np.uint32)
        out.pop(head+'_mapping')
    return out

def expand_banks(arrays):
    if 'codec_arena' not in arrays:return arrays
    from native_cache_codec import bank,mapping
    for head in ('aim','move'):
        points,numeric=bank(arrays,head)
        arrays.pop(head+'_point_bits');arrays.pop(head+'_numeric_bits')
        arrays[head+'_points']=points.astype(np.float32);arrays[head+'_numeric']=numeric
        arrays[head+'_mapping']=mapping(arrays[head+'_members'],arrays[head+'_valid'].shape[1])
    return arrays

def encode_arrays(arrays,history):
    descriptors=[];pieces=[];offset=0
    for absent in set(history)-set(arrays):del history[absent]
    for name,value in arrays.items():
        value=np.ascontiguousarray(value);dtype=np.dtype('u'+str(value.dtype.itemsize));bits=value.view(dtype).ravel()
        signature=(value.dtype.str,value.shape);old=history.get(name);mode=0
        if old is not None and old[2]==signature:
            mode=1 if old[1] is None else 2
            residual=bits-old[0] if mode==1 else bits-old[0]*2+old[1]
            residual=(residual<<1)^(np.zeros_like(residual)-(residual>>(8*dtype.itemsize-1)))
        else:residual=bits
        history[name]=(bits.copy(),old[0] if mode else None,signature)
        b=residual.view(np.uint8).reshape(-1,dtype.itemsize).T.copy().tobytes()
        descriptors.append([name,value.dtype.str,list(value.shape),offset,len(b),mode]);pieces.append(b);offset+=len(b)
    return b''.join(pieces),descriptors

def decode_frame(value,layout,history):
    names={q[0] for q in layout}
    for absent in set(history)-names:del history[absent]
    for name,dtype,shape,at,size,mode in layout:
        original=np.dtype(dtype);unsigned=np.dtype('u'+str(original.itemsize))
        if at<0 or size<0 or at+size>len(value) or size!=int(np.prod(shape))*original.itemsize:raise RuntimeError('prepared codec array bounds')
        signature=(dtype,tuple(shape));old=history.get(name)
        if mode and (mode not in (1,2) or old is None or old[2]!=signature or (mode==2 and old[1] is None)):raise RuntimeError('prepared codec history drift')
        from native_cache_codec import plane
        bits=plane(value[at:at+size],original.itemsize,mode,None if old is None else old[0],None if old is None else old[1])
        history[name]=(bits,old[0] if mode else None,signature)
        value[at:at+size]=bits.view(np.uint8)
