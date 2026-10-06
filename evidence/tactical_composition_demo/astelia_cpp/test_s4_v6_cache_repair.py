"""Repair checks use stored engineering summaries, never execute combat."""
import copy,gzip,json
from types import SimpleNamespace
import pytest
import s4_v6_cache_repair as V
from result_cache_v6 import Cache,identity
from result_schema_v6 import validate_rows
from result_schema import validate_rows as historical_validate_rows

@pytest.mark.parametrize('index',[0,1,2])
def test_stored_engineering_roundtrip_and_real_worker_cache_hit(tmp_path,index):
    engineering=json.loads((V.ROOT/'s4_v6_checks/ENGINEERING_REFINEMENT.json').read_text())['rows'][index]
    req=engineering['request'];summary=engineering['summary']
    with pytest.raises(ValueError,match='schema'):historical_validate_rows(req,[summary])
    assert validate_rows(req,[summary])=='completed'
    engine=identity('cpp',[str(V.BINARY),'--metrics']);cache=Cache(tmp_path,engine)
    stderr=V.ROOT/'s4_v6_checks/engineering'/f"{engineering['name']}.stderr.txt"
    metrics=json.loads(stderr.read_text())
    cache.put(req,[summary],dict(metrics=metrics,purpose='stored engineering repair fixture, no combat'))
    assert cache.load(req)==[summary]
    with gzip.open(cache.path(req),'rt') as f:assert json.load(f)['rows'][0]['complexDiagnostics']==summary['complexDiagnostics']
    seed=req['options']['seed'];setting='s4_melee10' if index==0 else 's4_full_head';head='regular' if index==2 else 'novice'
    spec=dict(arm='resonator',params=V.defaults('resonator'),skeleton='v6',setting=setting,opponent=head,seed=seed,endCounts=True,diagnostics=True)
    assert V.request(spec)==req
    class NoCombat:
        def remaining(self,*args):return 30
        def run(self,*args):pytest.fail('repair must not execute combat')
    rows=V.execute((engine,tmp_path,[spec]),NoCombat())
    assert len(rows)==1 and rows[0]['cache_hit'] and rows[0]['summary']==summary
    assert rows[0]['S']==summary['survivors']-summary['enemySurvivors']
    class StoredReplay(NoCombat):
        calls=0
        def run(self,*args):
            self.calls+=1
            return SimpleNamespace(returncode=0,stdout=json.dumps([summary])+'\n',stderr=stderr.read_text())
    replay=StoredReplay();fresh=tmp_path/'fresh'
    fresh_rows=V.execute((engine,fresh,[spec]),replay)
    assert replay.calls==1 and not fresh_rows[0]['cache_hit']
    assert fresh_rows[0]['summary']==summary
    assert Cache(fresh,engine).load(req)==[summary]

@pytest.mark.parametrize('fault',['missing','extra','nonfinite','counter','low_count','fraction','rate_count','rate_mean','threshold','mu','melee','failure_ticks','wrong_side','wrong_version','missing_status','missing_failures','missing_native_fields','mu_mismatch','omega_mismatch','invalid_endpoint_rates','excess_retries','excess_failure_ticks'])
def test_strict_complex_diagnostic_rejection(fault):
    stored=json.loads((V.ROOT/'s4_v6_checks/ENGINEERING_REFINEMENT.json').read_text())['rows'][0]
    req=copy.deepcopy(stored['request']);summary=copy.deepcopy(stored['summary']);d=summary['complexDiagnostics']
    if fault=='missing':del summary['complexDiagnostics']
    elif fault=='extra':d['unknown']=0
    elif fault=='nonfinite':d['argRateAbsSum']=float('nan')
    elif fault=='counter':d['samples']=True
    elif fault=='low_count':d['lowAmplitudeSamples']=d['samples']+1
    elif fault=='fraction':d['fractionBelow02']=2
    elif fault=='rate_count':d['argRateSamples']=d['samples']+1
    elif fault=='rate_mean':d['argRateAbsMean']=float('inf')
    elif fault=='threshold':d['argValidityThreshold']=.1
    elif fault=='mu':d['mu']=3
    elif fault=='melee':d['omega_melee']=1
    elif fault=='failure_ticks':d['numericalFailureTicks']=1
    elif fault=='wrong_side':d['side']=1
    elif fault=='wrong_version':req['options']['ai'][0]['skeleton']='v5'
    elif fault=='missing_status':del summary['controllerStatus']
    elif fault=='missing_failures':del summary['controllerFailures']
    elif fault=='missing_native_fields':
        from result_schema import S3_FIELDS
        for field in S3_FIELDS:del summary[field]
    elif fault=='mu_mismatch':d['mu']=1
    elif fault=='omega_mismatch':d['omega_ranged']=-1
    elif fault=='invalid_endpoint_rates':d['lowAmplitudeSamples']=d['samples'];d['fractionBelow02']=1
    elif fault=='excess_retries':d['retryCount']=100000
    else:
        summary['controllerStatus']='controller_failure';summary['controllerFailures']=[1,0];d['numericalFailureTicks']=100000
    with pytest.raises(ValueError):validate_rows(req,[summary])

def test_historical_schema_and_unchanged_arm_passthrough():
    stored=json.loads((V.ROOT/'s4_v6_checks/ENGINEERING_REFINEMENT.json').read_text())['rows'][0]
    summary=dict(stored['summary']);summary.pop('complexDiagnostics');req=copy.deepcopy(stored['request'])
    for version in ('v0','v1','v2','v3','v4','v5'):
        req['options']['ai'][0]['skeleton']=version
        assert validate_rows(req,[summary])==historical_validate_rows(req,[summary])=='completed'
    req['options']['ai'][0]['skeleton']='v6';req['options']['ai'][0]['controller']='morale'
    assert validate_rows(req,[summary])=='completed'

def test_null_denominators_failure_status_and_tampered_cache(tmp_path):
    from result_cache import encoded,digest
    stored=json.loads((V.ROOT/'s4_v6_checks/ENGINEERING_REFINEMENT.json').read_text())['rows'][0]
    req=copy.deepcopy(stored['request']);summary=copy.deepcopy(stored['summary']);d=summary['complexDiagnostics']
    d.update(samples=0,lowAmplitudeSamples=0,fractionBelow02=None,argRateSamples=0,argRateAbsSum=0,argRateAbsMean=None,argRateNullReason='no_consecutive_valid_endpoints')
    assert validate_rows(req,[summary])=='completed'
    for key in ('mu','omega_ranged'):del req['options']['ai'][0]['params'][key]
    assert validate_rows(req,[summary])=='completed'
    summary['controllerStatus']='controller_failure';summary['controllerFailures']=[1,0];d['numericalFailureTicks']=1
    assert validate_rows(req,[summary])=='controller_failure'
    engine=identity('cpp',[str(V.BINARY),'--metrics']);cache=Cache(tmp_path,engine);cache.put(req,[summary])
    assert cache.load(req)==[summary]
    path=cache.path(req)
    record=json.loads(gzip.decompress(path.read_bytes()))
    del record['rows'][0]['controllerStatus'];record['rows_sha256']=digest(record['rows'])
    path.write_bytes(gzip.compress(encoded(record),mtime=0))
    assert cache.load(req) is None and cache.rejected==1
