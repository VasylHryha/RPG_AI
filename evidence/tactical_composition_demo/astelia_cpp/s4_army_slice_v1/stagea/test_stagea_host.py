"""Real-binary full-army wiring fixtures, including sandbox fixture mode."""
import os
from pathlib import Path
import sys
import pytest
import torch
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import BINARY,LOCAL,write,sha
from collect import a0,identity
from fixture_host import execute_fixture, sample
from models import Policy,export
from readout import mechanism

@pytest.mark.skipif(os.environ.get('STAGEA_HOST_TEST')!='1',reason='opt-in real binary fixtures')
@pytest.mark.parametrize('arm', ('N1','N1h','N1r','N2','N2J0'))
def test_real_full_army_network_arm(tmp_path, arm):
    # Deterministic fixed weights are a wiring fixture, no learned quality claim.
    identity();model=Policy(arm).float()
    with torch.no_grad():
        for p in model.parameters():p.zero_()
        model.out.bias[3]=3;model.out.bias[8]=-3
    weights=export(model,tmp_path/'fixture.weights.json')
    req=a0().request('O','regular',__import__('secrets').randbelow(2**32-1)+1,0);req['options']['duration']=3;req['stageA']={'collect':True,'weights':weights,'parity':True}
    tag='host_fixture_'+__import__('secrets').token_hex(8);request=LOCAL/'requests'/(tag+'.json');write(request,req,exclusive=True)
    job=dict(tag=tag,seed=req['seed'] if 'seed' in req else 0,request_sha256=sha(request),split='integration',arm=arm)
    result=execute_fixture(job)
    print(__import__('json').dumps(dict(arm=arm,peak_rss_bytes=result['peak_rss_bytes'],compressed_bytes=result['compressed_bytes'],frames=result['frames'])))
    assert result['frames']>=90 and 3<=result['stats']['t_end']<3.1
    m=mechanism(LOCAL/result['raw_file']);assert m['label_rows']>=4500
    import gzip,json
    from parity import compare,sequence
    rows=[];native=[]
    with gzip.open(LOCAL/result['raw_file'],'rt') as f:
        for line in f:
            row=json.loads(line)
            if row.get('stageAParity'):rows.append(row['input']);native.append(__import__('numpy').asarray(row['output']))
    model=model.double();proof=compare(sequence(model,rows),native)
    write(LOCAL/(tag+'_PARITY.json'),dict(proof,arm=arm,frames=len(rows),completion_sha256=sha(LOCAL/'raw'/(tag+'_COMPLETE.json'))),exclusive=True)
    assert len(rows)==result['frames'] and proof['categorical_mismatches']==0 and proof['max_abs_error']<1e-8


@pytest.mark.skipif(os.environ.get('STAGEA_HOST_TEST')!='1',reason='opt-in real binary fixtures')
def test_real_teacher_sample_record_validate_convert():
    proof=sample()
    assert len(proof['fights'])==2
    assert all(r['recording']=='STAGEASLIM1' and r['frames']>=90 for r in proof['fights'])
    from data import frames
    from parity import sequence, replay, compare
    # Replay real teacher compact prefixes, including encoder refresh boundaries.
    model=Policy('N2').double()
    weights=export(model,LOCAL/('sample_fixture_'+__import__('secrets').token_hex(8)+'.weights.json'))
    for result in proof['fights']:
        rows=list(frames(LOCAL/result['raw_file']))
        parity=compare(sequence(model,rows),replay(weights,rows,timeout=120))
        write(LOCAL/(result['job']['tag']+'_PARITY.json'),parity,exclusive=True)
        assert parity['categorical_mismatches']==0 and parity['max_abs_error']<1e-8
