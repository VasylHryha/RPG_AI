"""Host-only full-army network integration; excluded from sandbox execution."""
import os
from pathlib import Path
import sys
import time
import pytest
import torch
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import BINARY,LOCAL,write,sha
from collect import a0,execute,identity
from jobs import admitted
from models import Policy,export
from readout import mechanism

@pytest.mark.skipif(os.environ.get('STAGEA_HOST_TEST')!='1',reason='real fights prohibited in sandbox; run once on host')
def test_real_full_army_network_arm(tmp_path):
    # Deterministic fixed weights are a wiring fixture, no learned quality claim.
    identity();model=Policy('N2').float()
    with torch.no_grad():
        for p in model.parameters():p.zero_()
        model.out.bias[3]=3;model.out.bias[8]=-3
    weights=export(model,tmp_path/'fixture.weights.json')
    req=a0().request('O','regular',__import__('secrets').randbelow(2**32-1)+1,0);req['options']['duration']=3;req['stageA']={'collect':True,'weights':weights,'parity':True}
    tag='host_fixture_'+__import__('secrets').token_hex(8);request=LOCAL/'requests'/(tag+'.json');write(request,req,exclusive=True)
    job=dict(tag=tag,seed=req['seed'] if 'seed' in req else 0,request_sha256=sha(request),split='integration',arm='N2')
    with admitted(120) as (deadline,monitor):result=execute(job,deadline,monitor,'INTEGRATION_ONLY')
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
    assert proof['categorical_mismatches']==0 and proof['max_abs_error']<1e-8
