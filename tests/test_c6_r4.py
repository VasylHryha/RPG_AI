"""Recheck witnesses and forward repair contracts. Deterministic fixtures only."""
import copy
import gzip
import hashlib
import json
from pathlib import Path
import shutil
from types import SimpleNamespace

import numpy as np
import pytest

from geomind import c4_detect as D, c6_r3_assay as A, c6_r3_protocol as R3
from geomind import c6_r3_background as B3
from geomind import c6_r4_analysis as R4, c6_r4_integrity as I
from tools import c6_r3_design_gate as old_gate, verify


def settings():
    s=R3.load_settings()
    s['qualification']['causal_numerical_relative_tolerance']=.1
    s['statistics']['bootstrap_resamples']=300
    s['statistics']['primary_ci_level']=1-(1-s['statistics']['nominal_ci_level'])/R4.PRIMARY_COUNT
    return s


def form(qualified):
    if not qualified:
        return {'qualified':False,'candidates':[],'selected_digest':None,'selected_members':None,'causal':None}
    members=[0,1,2];digest=A.member_digest(members)
    stats={'size':3,'membership_jaccard':1.,'shape_cv':0.,'lock_std':0.,'freq_change':0.,
        'pattern_change':0.,'recovery_jaccard':1.,'recovery_original_to_control':1.,
        'recovery_original_to_kicked':1.,'recovery_control_to_kicked':1.,'recovery_pattern_error':0.,
        'state_error_position':0.,'state_error_size':0.,'state_error_frequency':0.,'collective_frequency':.13}
    causal={direction:{'intact':.2,'ablated':0.,'intact_by_dt':[.2,.2,.2],
        'ablated_by_dt':[0.,0.,0.],'dt_values':[.02,.01,.005]} for direction in ('g_to_m','m_to_g')}
    candidate={'members':members,'digest':digest,'stats':stats,'accepted':True,'attribution':'source'}
    return {'qualified':True,'candidates':[candidate],'selected_digest':digest,'selected_members':members,'causal':causal}


def publication(formation):
    candidate=formation['candidates'][0]
    pub=D.active_unit(np.array([[0.,0.],[1.,0.],[0.,1.]]),np.zeros(3),.13,
                      np.array(candidate['members']),candidate['stats'])
    pub.update(member_digest=formation['selected_digest'],qualification=formation['causal'])
    return pub


def numeric_proof():
    i=settings()['integration']
    scopes={'qualification':i['formation'], **{f'operation/{c}':i['formation'] for c in R4.CONDITIONS},
        'probes':i['descriptor'],'causality':10.,**{f'candidates/{c}':i['formation']+i['recovery'] for c in R4.CONDITIONS}}
    return {'passed':True,'checks':{scope:{'duration':duration,'integration_dt':.02,'fine_dt':.005,
        'fine_replay_dt':.005,'position_error_over_L':.01,'phase_error_rad':.01,'native_reference_error':1e-15,
        'equivariance_position_over_L':1e-14,'equivariance_phase_rad':1e-14} for scope,duration in scopes.items()}}


def records(n=10,turns=2):
    rows=[]
    for world in range(n):
        cells=[]
        for turn in range(turns):
            prefix=f'w{world}/t{turn}'
            f=form(True)
            episodes={condition:[{'episode':index,'persistent_unit':condition=='intact',
                'candidate_initial_digest':f'{prefix}/candidate{index}',
                'reference_digest':f'{prefix}/reference/{condition}',
                'prior_digest':f'{prefix}/prior','qualification_flow_digest':f'{prefix}/flow/{condition}/{index}',
                'qualification_bath_after_digest':f'{prefix}/bath_end/{condition}/{index}',
                'formation':form(condition=='intact')} for index in range(4)] for condition in R4.CONDITIONS}
            bg={condition:{'b_phase':.4 if condition=='intact' else .1,'b_position':.2} for condition in R4.CONDITIONS}
            bg['before']={'b_phase':.1,'b_position':.2}
            cells.append({'qualified':True,'formation':{'intact':f,'no_r':form(False),'no_backreaction':form(True)},
                'controls':{'sham_source_error':0.,'sham_outgoing_mask':0.,'sham_preserved':True,'no_r_qualifies':False},
                'publication':publication(f),'numerics':numeric_proof(),'background':bg,
                'episodes':episodes,'before_episodes':[{'persistent_unit':False} for _ in range(4)],
                'bath_before_digest':prefix+'/before','bath_after_digest':prefix+'/after',
                'inherited_bath_digest':prefix+'/inherit','source_input_digest':prefix+'/source',
                'timeline':{'qualification_completed_at':100.,'treatment_started_at':100.,
                    'qualification_snapshot_digest':prefix+'/snapshot','treatment_initial_snapshot_digest':prefix+'/snapshot'}})
        link=None
        if turns==2:
            first,second=cells;ep=first['episodes']['intact'][0]
            second['inherited_bath_digest']=first['bath_after_digest']
            second['source_input_digest']=ep['candidate_initial_digest']
            second['qualification_reference_digest']=ep['reference_digest']
            second['qualification_prior_digest']=ep['prior_digest']
            second['qualification_flow_digest']=ep['qualification_flow_digest']
            second['bath_before_digest']=ep['qualification_bath_after_digest']
            link={'first_after':first['bath_after_digest'],'second_before':second['inherited_bath_digest'],
                'first_episode_source':ep['candidate_initial_digest'],'second_source_input':second['source_input_digest'],
                'intact_episode_reused':True}
        rows.append({'world':world,'turns':cells,'chain_link':link,'seconds':1.})
    return rows


def evaluate(rows):
    return R4.evaluate(rows,settings(),list(range(len(rows))),42)


def old_evaluate(rows):
    s=settings();s['statistics']['primary_ci_level']=.99375
    return R3.evaluate(rows,s,42)


def test_duplicate_world_witness_old_accepts_new_rejects():
    rows=records()
    for row in rows:row['world']=0
    assert old_evaluate(rows)['hypotheses']['H-RBG']=='SUPPORTED_WITHIN_SCOPE'
    with pytest.raises(ValueError,match='world IDs'):evaluate(rows)


def test_copied_links_witness_old_accepts_new_detects_wrong_actual_bath():
    rows=records();rows[0]['turns'][1]['inherited_bath_digest']='different actual bath'
    # Old code compares only the two copies inside chain_link, not these real records.
    assert old_evaluate(rows)['gates']['chain_provenance']
    repaired=evaluate(rows)
    assert not repaired['gates']['chain_provenance']
    assert repaired['hypotheses']['H-RBG']=='INCONCLUSIVE'


def test_unpaired_candidate_witness_old_accepts_new_rejects():
    rows=records();rows[0]['turns'][0]['episodes']['no_r'][1]['candidate_initial_digest']='different'
    assert old_evaluate(rows)['hypotheses']['H-PS_turn1']=='SUPPORTED_WITHIN_SCOPE'
    with pytest.raises(ValueError,match='initial states differ'):evaluate(rows)


def test_unqualified_candidate_flag_witness_old_accepts_new_rejects():
    rows=records();rows[0]['turns'][0]['formation']['intact']['causal']['g_to_m']['intact']=0.
    assert old_evaluate(rows)['hypotheses']['H-BG_turn1']=='SUPPORTED_WITHIN_SCOPE'
    with pytest.raises(ValueError,match='causal evidence'):evaluate(rows)


def test_old_replay_hash_aliases_different_time_grids_new_digest_separates():
    x=np.arange(8.).reshape(2,2,2);th=np.arange(4.).reshape(2,2)
    a=B3.Replay(x,th,.02);b=B3.Replay(x.reshape(4,1,2),th.reshape(4,1),.02)
    assert a.duration!=b.duration and a.digest==b.digest
    assert I.array_digest('replay',a.x,a.theta,metadata={'dt':a.dt})!=I.array_digest('replay',b.x,b.theta,metadata={'dt':b.dt})


def fake_release(root):
    folder=root/'research/rrg/v0.2.1';folder.mkdir(parents=True)
    names=sorted(I.REQUIRED_SOURCE_NAMES-{'MANIFEST.json'})+[f'extra/{i}.txt' for i in range(12)]
    for name in names:
        p=folder/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text('fixture source '+name)
    entries=[{'path':name,'bytes':(folder/name).stat().st_size,'sha256':I.sha256(folder/name)} for name in names]
    (folder/'MANIFEST.json').write_text(json.dumps({'file_count_excluding_manifest_and_checksums':23,'files':entries}))
    hashes={name:I.sha256(folder/name) for name in names+['MANIFEST.json']}
    (folder/'SHA256SUMS.txt').write_text(''.join(f'{digest}  {name}\n' for name,digest in hashes.items()))
    hashes['SHA256SUMS.txt']=I.sha256(folder/'SHA256SUMS.txt')
    handoff=root/'docs/RRG_V0_2_1_ALIGNMENT_HANDOFF.md';handoff.parent.mkdir(parents=True)
    handoff.write_text(''.join(f'| `{name}` | `{hashes[name]}` |\n' for name in sorted(I.REQUIRED_SOURCE_NAMES)))
    owner={name:hashes[name] for name in I.REQUIRED_SOURCE_NAMES}
    expected={'release':'fixture v0.2.1','verification_status':'VERIFIED','expected_sha256':owner,'handoff_sha256':I.sha256(handoff)}
    imported={'release':'fixture v0.2.1','verification_status':'VERIFIED','file_sha256':hashes,'release_files_copied':25}
    (folder.parent/'v0.2.1.expected.json').write_text(json.dumps(expected))
    (folder.parent/'v0.2.1.import.json').write_text(json.dumps(imported))
    return folder,expected,imported


def test_empty_import_witness_old_accepts_new_rejects(tmp_path,monkeypatch):
    folder,expected,imported=fake_release(tmp_path)
    imported['file_sha256']={};(folder.parent/'v0.2.1.import.json').write_text(json.dumps(imported))
    monkeypatch.setattr(old_gate,'ROOT',tmp_path)
    assert old_gate.validate_pin()['verdict']=='PASS'
    assert old_gate.validate_pin()['source_files_verified']==0
    with pytest.raises(ValueError,match='inventory'):I.validate_pin(tmp_path)


def test_full_source_validation_and_missing_additional_file(tmp_path):
    folder,_,_=fake_release(tmp_path)
    assert I.validate_pin(tmp_path)['source_files_verified']==25
    (folder/'extra/0.txt').unlink()
    with pytest.raises(ValueError,match='release files'):I.validate_pin(tmp_path)


@pytest.mark.parametrize('fault',['owner','handoff','manifest','checksum','extra','metadata_count'])
def test_source_pin_rejects_conflicting_authorities(tmp_path,fault):
    folder,expected,imported=fake_release(tmp_path)
    if fault=='owner':
        expected['expected_sha256'].pop('README.md')
        (folder.parent/'v0.2.1.expected.json').write_text(json.dumps(expected))
    elif fault=='handoff':(tmp_path/'docs/RRG_V0_2_1_ALIGNMENT_HANDOFF.md').write_text('changed handoff')
    elif fault=='manifest':
        manifest=json.loads((folder/'MANIFEST.json').read_text());manifest['files'][0]['bytes']=0
        (folder/'MANIFEST.json').write_text(json.dumps(manifest))
    elif fault=='checksum':(folder/'SHA256SUMS.txt').write_text('wrong')
    elif fault=='extra':(folder/'unexpected.txt').write_text('extra')
    else:
        imported['release_files_copied']=24
        (folder.parent/'v0.2.1.import.json').write_text(json.dumps(imported))
    with pytest.raises(ValueError):I.validate_pin(tmp_path)


def test_coherent_manifest_or_checksum_tampering_cannot_override_owner(tmp_path):
    folder,expected,imported=fake_release(tmp_path)
    # Changing both import and source is still inconsistent with the separate owner table.
    (folder/'README.md').write_text('modified')
    imported['file_sha256']['README.md']=I.sha256(folder/'README.md')
    (folder.parent/'v0.2.1.import.json').write_text(json.dumps(imported))
    with pytest.raises(ValueError,match='conflicting'):I.validate_pin(tmp_path)


def test_scalar_array_and_nested_nonfinite_values_are_rejected():
    for value in (np.array([np.nan]),{'x':np.array([1.,np.inf])},[float('nan')]):assert not I.finite(value)
    assert R3.finite(np.array([np.nan]))  # Old scalar-only check silently accepts an array.
    with pytest.raises(ValueError):I.array_digest('state',np.array([np.nan]))


def test_array_identity_binds_kind_metadata_shape_and_array_boundaries():
    a=np.array([1.,2.]);b=np.array([3.,4.])
    baseline=I.array_digest('replay',a,b,metadata={'dt':.02,'ids':[1,2]})
    variants=[I.array_digest('state',a,b,metadata={'dt':.02,'ids':[1,2]}),
        I.array_digest('replay',a,b,metadata={'dt':.01,'ids':[1,2]}),
        I.array_digest('replay',a,b,metadata={'dt':.02,'ids':[2,1]}),
        I.array_digest('replay',a.reshape(1,2),b,metadata={'dt':.02,'ids':[1,2]}),
        I.array_digest('replay',np.r_[a,b],metadata={'dt':.02,'ids':[1,2]})]
    assert all(digest!=baseline for digest in variants)


def artifact(folder,world=0,entry_world=None,payload_world=None):
    raw=(json.dumps({'world':world if payload_world is None else payload_world,'value':1.})+'\n').encode()
    payload=gzip.compress(raw,mtime=0);path=folder/f'world_{world:03d}.json.gz';path.write_bytes(payload)
    return {'world':world if entry_world is None else entry_world,'path':path.name,
        'sha256':hashlib.sha256(payload).hexdigest(),'uncompressed_sha256':hashlib.sha256(raw).hexdigest()}


def test_artifact_index_raw_identity_and_duplicate_check(tmp_path):
    entry=artifact(tmp_path)
    assert I.load_worlds(tmp_path,{'world_artifacts':[entry]},[0])[0]['world']==0
    with pytest.raises(ValueError,match='duplicate'):I.load_worlds(tmp_path,{'world_artifacts':[entry,entry]},[0])
    entry['world']=1
    with pytest.raises(ValueError,match='index/name'):I.load_worlds(tmp_path,{'world_artifacts':[entry]},[1])
    entry=artifact(tmp_path,payload_world=1)
    with pytest.raises(ValueError,match='raw world identity'):I.load_worlds(tmp_path,{'world_artifacts':[entry]},[0])


@pytest.mark.parametrize('name',['../outside','/tmp/outside','world/../outside','./world_000.json.gz'])
def test_artifact_paths_are_canonical_and_stay_inside_evidence(tmp_path,name):
    with pytest.raises(ValueError):I.safe_file(tmp_path,name)


def test_artifact_symlinks_rejected(tmp_path):
    outside=tmp_path/'real';outside.write_text('data')
    (tmp_path/'link').symlink_to(outside)
    with pytest.raises(ValueError,match='symlink'):I.safe_file(tmp_path,'link')


def test_dependency_identity_rechecks_all_files(tmp_path):
    (tmp_path/'x').write_text('original');hashes={'x':I.sha256(tmp_path/'x')}
    assert not I.dependency_problems(tmp_path,hashes)
    (tmp_path/'x').write_text('changed')
    assert I.dependency_problems(tmp_path,hashes)==['x']
    assert I.dependency_problems(tmp_path,{})==['empty dependency inventory']


def test_pipeline_stage_budget_preserves_default_and_honors_registration(monkeypatch,tmp_path):
    observed=[];artifact_path=tmp_path/'artifact.json';artifact_path.write_text('{}')
    def run(*args,**kwargs):
        observed.append(kwargs['timeout']);return SimpleNamespace(returncode=0)
    monkeypatch.setattr(verify.subprocess,'run',run)
    cfg={'stages':{'panel':{'cmd':['unused'],'artifacts':[str(artifact_path)]}}}
    verify.run_stage(cfg,'panel',{})
    cfg['stages']['panel']['timeout_seconds']=10800
    verify.run_stage(cfg,'panel',{})
    assert observed==[3600,10800]


@pytest.mark.parametrize('budget',[0,-1,True,None,1.5,'10800'])
def test_invalid_stage_budget_rejected_before_execution(monkeypatch,budget):
    monkeypatch.setattr(verify.subprocess,'run',lambda *args,**kw:pytest.fail('must not execute'))
    cfg={'stages':{'panel':{'cmd':['unused'],'artifacts':[],'timeout_seconds':budget}}}
    with pytest.raises(verify.StageFailed,match='positive integer'):verify.run_stage(cfg,'panel',{})


def test_complete_positive_fixture_coverage_and_original_world_bootstrap():
    rows=records();e=evaluate(rows);coverage=e['endpoint_coverage']
    assert set(coverage['evaluated'])|set(coverage['not_run'])==set(R4.ENDPOINTS)
    assert set(coverage['evaluated']).isdisjoint(coverage['not_run'])
    assert e['hypotheses']['H-RBG']=='SUPPORTED_WITHIN_SCOPE'
    assert e['primary_contrasts']==16
    assert e['hypotheses']['H-COMP']=='NOT_TESTED'
    endpoint=coverage['evaluated']['b_chain_background_phase_vs_no_r_turn1']['value']
    assert endpoint['world_ids']==list(range(10))
    reversed_rows=R4.evaluate(list(reversed(rows)),settings(),list(range(10)),42)
    assert e==reversed_rows


def test_chain_effects_use_same_worlds_and_detect_selected_subset_counterexample():
    rows=records(n=20)
    for row in rows[:10]:
        row['turns'][0]['background']['intact']['b_phase']=.1  # No first-turn BG on complete chains.
    for row in rows[10:]:
        row['turns']=row['turns'][:1];row['chain_link']=None
        row['turns'][0]['background']['intact']['b_phase']=.7
    old=old_evaluate(rows)
    assert old['hypotheses']['H-RBG']=='SUPPORTED_WITHIN_SCOPE'
    new=evaluate(rows)
    assert new['hypotheses']['H-BG_turn1']=='SUPPORTED_WITHIN_SCOPE'
    assert new['hypotheses']['H-RBG']=='NOT_SUPPORTED'
    endpoint=new['endpoint_coverage']['evaluated']['b_chain_background_phase_vs_no_r_turn1']['value']
    assert endpoint['world_ids']==list(range(10)) and endpoint['mean']==0.


def test_second_turn_engineering_failure_preserves_valid_first_turn_claim():
    rows=records()
    rows[0]['turns'][1]['numerics']['passed']=False
    rows[0]['turns'][1]['numerics']['checks']['operation/intact']['phase_error_rad']=.08
    assert old_evaluate(rows)['hypotheses']['H-BG_turn1']=='INCONCLUSIVE'
    new=evaluate(rows)
    assert new['hypotheses']['H-BG_turn1']=='SUPPORTED_WITHIN_SCOPE'
    assert new['hypotheses']['H-BG_turn2']=='INCONCLUSIVE'
    assert new['hypotheses']['H-RBG']=='INCONCLUSIVE'
    assert not new['gates']['numerical_checks']  # Whole revision still cannot pass engineering.


@pytest.mark.parametrize('fault',['source','reference','prior','flow','qualification_end','reuse'])
def test_chain_provenance_binds_actual_continuation_inputs(fault):
    rows=records();second=rows[0]['turns'][1]
    keys={'source':'source_input_digest','reference':'qualification_reference_digest',
          'prior':'qualification_prior_digest','flow':'qualification_flow_digest','qualification_end':'bath_before_digest'}
    if fault=='reuse':rows[0]['chain_link']['intact_episode_reused']=False
    else:second[keys[fault]]='changed'
    e=evaluate(rows)
    assert not e['gates']['chain_provenance']
    assert e['hypotheses']['H-RBG']=='INCONCLUSIVE'


@pytest.mark.parametrize('fault',['episode_count','episode_order','condition','persistence','publication','candidate','control','timing','snapshot','numerics_type'])
def test_record_schema_rejects_inconsistent_or_incomplete_evidence(fault):
    rows=records();cell=rows[0]['turns'][0]
    if fault=='episode_count':cell['episodes']['no_r'].pop()
    elif fault=='episode_order':cell['episodes']['intact'][0]['episode']=2
    elif fault=='condition':cell['episodes'].pop('no_backreaction')
    elif fault=='persistence':cell['episodes']['intact'][0]['persistent_unit']=False
    elif fault=='publication':cell['publication']['member_digest']='another unit'
    elif fault=='candidate':cell['formation']['intact']['candidates'][0]['stats']['membership_jaccard']=0.
    elif fault=='control':cell['controls']['no_r_qualifies']=True
    elif fault=='timing':cell['timeline']['treatment_started_at']=0.
    elif fault=='snapshot':cell['timeline']['treatment_initial_snapshot_digest']='changed'
    else:cell['numerics']['passed']=1
    with pytest.raises(ValueError):evaluate(rows)


def test_no_source_worlds_and_unreached_turns_remain_in_inventory():
    rows=records(turns=1)
    c=rows[0]['turns'][0];c['qualified']=False;c['formation']['intact']=form(False);c['publication']=None
    c['background']=None;c['episodes']=None;c['before_episodes']=None
    e=evaluate(rows)
    cov=e['endpoint_coverage']
    assert cov['evaluated']['b_source_qualification_turn1']['value']=={'qualified':9,'total_worlds':10}
    assert e['hypotheses']['H-BG_turn1']=='INCONCLUSIVE'
    assert e['hypotheses']['H-RBG']=='INCONCLUSIVE'
    assert cov['evaluated']['b_background_phase_vs_no_r_turn1']['value']['per_world'][0] is None
    assert 'b_chain_background_phase_vs_no_r_turn2' in cov['not_run']


@pytest.mark.parametrize('ci,n,expected',[([.06,.1],10,'PASS'),([-.1,-.06],10,'PASS'),
    ([-.04,.04],10,'FAIL'),([.05,.1],10,'INCONCLUSIVE'),([-.1,-.05],10,'INCONCLUSIVE'),
    ([-.05,.04],10,'INCONCLUSIVE'),([.06,.1],9,'INCONCLUSIVE'),(None,10,'INCONCLUSIVE')])
def test_registered_two_sided_change_rule(ci,n,expected):
    assert R4.change_verdict(ci,.05,n,10)==expected


def test_sign_not_selected_from_data_and_more_than_eight_contrasts_corrected():
    rows=records()
    for row in rows:
        for c in row['turns']:
            c['background']['intact']['b_phase']=.1
            c['background']['no_r']['b_phase']=.4
            c['background']['no_backreaction']['b_phase']=.4
            for condition,episodes in c['episodes'].items():
                for ep in episodes:
                    ep['persistent_unit']=condition!='intact' or ep['episode']==0
                    ep['formation']=form(ep['persistent_unit'])
    assert evaluate(rows)['hypotheses']['H-RBG']=='SUPPORTED_WITHIN_SCOPE'
    bad=settings();bad['statistics']['primary_ci_level']=.99375
    with pytest.raises(ValueError,match='sixteen'):R4.evaluate(rows,bad,list(range(10)),42)


@pytest.mark.parametrize('fault',['stability','frequency','empty_snapshot','missing_timeline'])
def test_incomplete_publication_or_qualification_snapshot_rejected(fault):
    rows=records();c=rows[0]['turns'][0]
    if fault=='stability':c['publication']['stability']={}
    elif fault=='frequency':c['publication']['mode_signature']['collective_frequency']=7.
    elif fault=='empty_snapshot':
        c['timeline']['qualification_snapshot_digest']='';c['timeline']['treatment_initial_snapshot_digest']=''
    else:c.pop('timeline')
    with pytest.raises(ValueError):evaluate(rows)


@pytest.mark.parametrize('fault',['resamples','quorum','level','margin','episodes'])
def test_invalid_analysis_settings_rejected(fault):
    s=settings()
    if fault=='resamples':s['statistics']['bootstrap_resamples']=True
    elif fault=='quorum':s['statistics']['minimum_qualified_worlds']=0
    elif fault=='level':s['statistics']['primary_ci_level']=1.
    elif fault=='margin':s['statistics']['phase_margin']=float('nan')
    else:s['episodes']=0
    with pytest.raises(ValueError):R4.evaluate(records(),s,list(range(10)),42)


def test_readonly_recheck_verifies_artifacts_source_and_unchanged_dependencies(tmp_path):
    from tools import c6_r3_recheck as recheck
    folder,_,_=fake_release(tmp_path)
    dependency=tmp_path/'fixture.py';dependency.write_text('# immutable fixture')
    evidence=tmp_path/'evidence';evidence.mkdir()
    artifacts=[]
    for world in range(2):
        windows={'initial':{'dt_error':.01 if world==0 else .08,'native_reference_error':1e-15,'equivariance_error':1e-14},
                 'formation_snapshot':{'dt_error':.01,'native_reference_error':1e-15,'equivariance_error':1e-14}}
        groups=[{'attribution':'mixed_or_prior','accepted':False,'recovery_status':'NOT_RUN'}]
        row={'world':world,'turns':[{'qualified':False,'numerics':windows,
            'formation':{'intact':{'candidates':groups}},'controls':{'sham_preserved':True,'no_r_qualifies':False}}]}
        raw=json.dumps(row).encode();path=evidence/f'world_{world:03d}.json.gz';path.write_bytes(gzip.compress(raw,mtime=0))
        artifacts.append({'world':world,'path':path.name,'sha256':I.sha256(path),'uncompressed_sha256':hashlib.sha256(raw).hexdigest()})
    receipt={'kind':'DEVELOPMENT_ONLY','status':'STOP','source_commit':'fixture-only',
        'protocol':{'development_worlds':2,'qualification':{'dt_tolerance':.05}},'world_artifacts':artifacts,
        'file_hashes':{'fixture.py':I.sha256(dependency)},
        'source_pin':{'import_record_sha256':I.sha256(folder.parent/'v0.2.1.import.json')}}
    (evidence/'results.json').write_text(json.dumps(receipt))
    before=I.sha256(evidence/'results.json')
    result=recheck.inspect(evidence,tmp_path)
    assert result['mixed_candidates_without_recovery_assay']==2
    assert result['qualified_sources']==0
    assert result['dt_failures']==[{'world':1,'scope':'initial','error':.08}]
    assert I.sha256(evidence/'results.json')==before
    dependency.write_text('changed')
    with pytest.raises(ValueError,match='implementation changed'):recheck.inspect(evidence,tmp_path)


@pytest.mark.parametrize('fault',['error_flag','short_window','coarse_replay','missing_scope','wrong_dt','negative_error'])
def test_numerical_gate_is_bound_to_measured_errors_and_entire_reached_assay(fault):
    rows=records();numeric=rows[0]['turns'][0]['numerics'];check=numeric['checks']['operation/intact']
    if fault=='error_flag':check['phase_error_rad']=.08
    elif fault=='short_window':check['duration']=2.
    elif fault=='coarse_replay':check['fine_replay_dt']=.02
    elif fault=='missing_scope':numeric['checks'].pop('causality')
    elif fault=='wrong_dt':check['fine_dt']=.01
    else:check['position_error_over_L']=-1.
    with pytest.raises(ValueError):evaluate(rows)


@pytest.mark.parametrize('fault',['negative_refinement','large_spread','nonvanishing_ablation','grid_mismatch','missing_values'])
def test_local_causal_qualification_requires_refined_positive_effects(fault):
    rows=records();direction=rows[0]['turns'][0]['formation']['intact']['causal']['g_to_m']
    if fault=='negative_refinement':direction['intact_by_dt'][2]=-.1
    elif fault=='large_spread':direction['intact_by_dt'][2]=.4
    elif fault=='nonvanishing_ablation':direction['ablated_by_dt'][2]=.1
    elif fault=='grid_mismatch':direction['dt_values']=[.02,.01,.0025]
    else:direction.pop('intact_by_dt')
    with pytest.raises(ValueError):evaluate(rows)


@pytest.mark.parametrize('fault',['unqualified_episode_zero','different_unit'])
def test_continuation_requires_qualified_episode_zero_and_same_unit(fault):
    rows=records();first,second=rows[0]['turns']
    if fault=='unqualified_episode_zero':
        ep=first['episodes']['intact'][0];ep['persistent_unit']=False;ep['formation']=form(False)
    else:
        selected=second['formation']['intact'];candidate=selected['candidates'][0]
        candidate['members']=[3,4,5];candidate['digest']=A.member_digest(candidate['members'])
        selected['selected_members']=candidate['members'];selected['selected_digest']=candidate['digest']
        second['publication']['member_digest']=candidate['digest']
    e=evaluate(rows)
    assert not e['gates']['chain_provenance']
    assert e['hypotheses']['H-RBG']=='INCONCLUSIVE'
