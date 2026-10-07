"""No fights: native observation fixtures and fake protocol/process/receipt records."""
import importlib.util,json,pathlib,re,subprocess,sys
import pytest
HERE=pathlib.Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import common,protocol,run

def summary(win=True,S=10):
 return dict(controllerStatus='completed',controllerFailures=[0,0],complexDiagnostics=dict(numericalFailureTicks=0),survivors=10 if win else 25+S,enemySurvivors=0 if win else 25,t=100 if win else 150)
def fake(novice=8,regular=8):
 return [dict(head=h,cluster=c,orientation=o,summary=summary(2*c+o<(novice if h=='novice' else regular))) for h in protocol.HEADS for c in range(8) for o in (0,1)]

def test_native_observation_fixture():
 p=subprocess.run([str(HERE/'build/fixture')],capture_output=True,text=True,timeout=120)
 assert p.returncode==0,p.stdout+p.stderr
 assert 'PASS observation-only' in p.stdout
 (HERE/'FIXTURE.log').write_text(p.stdout+p.stderr)

def test_inherited_bounds_order():
 sys.path.insert(0,str(HERE.parent));import s4_v6
 assert list(protocol.BOUNDS.items())==list(s4_v6.BOUNDS['resonator'].items())
 p=protocol.knobs([.25]*11)
 assert protocol.normalized(p)==s4_v6.normalized('resonator',p)
 assert protocol.knobs([.25]*11)==s4_v6.knobs('resonator',[.25]*11)

def test_rank_and_cross_generation_retention():
 initial=protocol.selection(fake(),0);late=protocol.selection(fake(),17)
 assert min([late,initial],key=protocol.rank)==initial
 assert protocol.cma_losses([late,initial])==[1,0]
 eligible=protocol.selection(fake(novice=8,regular=0),256);ineligible=protocol.selection(fake(novice=7,regular=16),1)
 assert protocol.rank(eligible)<protocol.rank(ineligible)
 assert not min([ineligible,protocol.selection(fake(novice=0),0)],key=protocol.rank)['eligible']
 assert protocol.selection(fake(novice=8),0)['eligible']
 assert not protocol.selection(fake(novice=7),0)['eligible']
 assert protocol.EVALUATIONS==1+protocol.POPULATION*protocol.GENERATIONS==257
 assert protocol.FIGHTS==257*32+20*2*5*2
 low=protocol.selection(fake(8,8),1);high=dict(low,regular_S=low['regular_S']+1,ordinal=2)
 assert protocol.rank(high)<protocol.rank(low)
 losses=dict(low,regular_losses=low['regular_losses']-1,ordinal=3)
 assert protocol.rank(losses)<protocol.rank(low)

def test_failure_and_allocation_rows():
 rows=fake();rows[0]['summary']['controllerFailures']=[1,0]
 with pytest.raises(ValueError,match='failure'):protocol.selection(rows,0)
 rows=fake();rows[0]['summary']['complexDiagnostics']['numericalFailureTicks']=1
 with pytest.raises(ValueError,match='failure'):protocol.selection(rows,0)
 with pytest.raises(ValueError):protocol.selection(fake()[:-1],0)
 rows=fake();rows[-1]=rows[0]
 with pytest.raises(ValueError):protocol.selection(rows,0)
 with pytest.raises(ValueError):protocol.knobs([float('nan')]*11)
 assert protocol.measure(summary())['win']==1
 s=summary();s['t']=150;assert protocol.measure(s)['win']==0

def test_exhaustive_readings_ceiling_floor_and_owner_boundaries():
 cell=lambda n,s=1:dict(wins=n,mean_S=s)
 assert protocol.readings(cell(40),cell(40),cell(34))['relative']=='Observed improvement'
 for difference in range(-40,41):
  a=max(0,difference);b=a-difference
  r=protocol.readings(cell(a),cell(21),cell(b))
  assert r['relative'] in ('Observed improvement','Observed match','Observed worse','the panel does not support a comparison')
 for n in (20,21):
  r=protocol.readings(cell(21),cell(21),cell(n));assert r['observed_owner_criterion'];assert r['comparator_underperformance']==(n==20)
 assert not protocol.readings(cell(20),cell(21),cell(21))['observed_owner_criterion']
 assert not protocol.readings(cell(21),cell(20),cell(21))['observed_owner_criterion']
 for head in (0,1):
  args=[cell(21),cell(21),cell(21)];args[head]['mean_S']=0
  assert not protocol.readings(*args)['observed_owner_criterion']
 assert not protocol.readings(cell(21),cell(21),cell(21),1)['observed_owner_criterion']
 for diff,expected in ((-4,'Observed worse'),(-3,'Observed match'),(3,'Observed match'),(4,'Observed improvement')):
  assert protocol.readings(cell(25+diff),cell(21),cell(25))['relative']==expected

def test_cluster_bootstrap():
 assert protocol.bootstrap([0]*20)['low']==protocol.bootstrap([0]*20)['high']==0
 assert protocol.bootstrap([1]*20)['low']==1
 x=[-.5]*10+[.5]*10;assert protocol.bootstrap(x)==protocol.bootstrap(x)
 with pytest.raises(ValueError):protocol.bootstrap([0]*19)

def test_anchored_process_pattern():
 # POSIX ERE here uses the same operators as Python after translating whitespace class.
 pattern=re.compile(common.process_pattern().replace('[^[:space:]]',r'\S').replace('[[:space:]]',r'\s'))
 repo=str(common.REPO)
 samples=[repo+'/.venv/bin/python -c worker',repo+'/.venv/bin/python evidence/tactical_composition_demo/growing_shapes_review_claude/rev711_diag/medium_variants/run_economy.py','/usr/bin/python3 '+repo+'/evidence/tactical_composition_demo/growing_shapes_review_claude/rev711_diag/medium_variants/pilot.py','python3 evidence/tactical_composition_demo/growing_shapes_review_claude/rev711_diag/medium_variants/run.py',repo+'/evidence/tactical_composition_demo/astelia_cpp/s4_v7/build/astelia_native_v7 --metrics','./.venv/bin/python worker.py']
 assert all(pattern.search(s) for s in samples)
 assert not pattern.search('/usr/bin/pgrep -fl '+common.process_pattern())
 assert not pattern.search('pgrep -fl '+samples[2])
 assert not pattern.search('/usr/bin/python3 /another/repo/pilot.py')

def test_process_gate_fails_closed_and_ignores_only_self(monkeypatch,tmp_path):
 monkeypatch.setattr(common,'HERE',tmp_path);monkeypatch.setattr(common,'sha',lambda _: 'hash');monkeypatch.setattr(common,'admit',lambda _: {'binary':'same'})
 response=lambda rc,stdout='',stderr='':subprocess.CompletedProcess([],rc,stdout,stderr)
 monkeypatch.setattr(common.subprocess,'run',lambda *a,**k:response(3,stderr='Operation not permitted'))
 with pytest.raises(RuntimeError,match='unavailable'):common.process_gate(False)
 assert json.loads(next(tmp_path.glob('GATE*')).read_text())['status']=='UNAVAILABLE'
 monkeypatch.setattr(common.subprocess,'run',lambda *a,**k:response(0,str(common.os.getpid())+' python own\n'))
 assert common.process_gate(False)['sha256']=='hash'
 monkeypatch.setattr(common.subprocess,'run',lambda *a,**k:response(0,'999999 python pilot\n'))
 with pytest.raises(RuntimeError,match='active'):common.process_gate(False)
 monkeypatch.setattr(common.subprocess,'run',lambda *a,**k:response(1))
 assert common.process_gate(False)['sha256']=='hash'

def test_ambiguous_receipts_never_replay(monkeypatch,tmp_path):
 monkeypatch.setattr(run,'RAW',tmp_path)
 assert run.verified('x') is None
 (tmp_path/'x_CLAIM.json').write_text('{}')
 with pytest.raises(RuntimeError,match='never replay'):run.verified('x')

def test_unclosed_attempt_and_projection_stop(monkeypatch,tmp_path):
 monkeypatch.setattr(common,'HERE',tmp_path)
 (tmp_path/'ATTEMPT_x.json').write_text(json.dumps(dict(status='RUNNING')))
 with pytest.raises(RuntimeError,match='unclosed'):common.spent()
 monkeypatch.setattr(common.time,'monotonic',lambda:100)
 with pytest.raises(TimeoutError,match='projected'):common.project(0,0,1,100)
 assert json.loads((tmp_path/'PROJECTION.json').read_text())['cap_seconds']==3600

def test_zero_exit_empty_process_output_is_unavailable(monkeypatch,tmp_path):
 monkeypatch.setattr(common,'HERE',tmp_path);monkeypatch.setattr(common,'sha',lambda _: 'hash');monkeypatch.setattr(common,'admit',lambda _: {})
 monkeypatch.setattr(common.subprocess,'run',lambda *a,**k:subprocess.CompletedProcess([],0,'',''))
 with pytest.raises(RuntimeError,match='unavailable'):common.process_gate(False)

def test_fake_analysis_mixed_sources_and_simultaneous_band(monkeypatch,tmp_path):
 import gzip,analyze
 monkeypatch.setattr(analyze,'RAW',tmp_path)
 unit=lambda i,side,role,x,y,r=10:[i,side,role,x,y,100,r,320 if role==2 else 259,0]
 before=[unit(1,0,2,500,400),unit(2,0,2,560,400),unit(11,1,2,800,400),unit(12,1,2,800,500),unit(13,1,1,849,400,9)]
 post=[list(u) for u in before];post[2][3]=900
 observer=lambda step,units:dict(observerV1=True,step=step,t=step/30,units=units,damage=[],launches=[])
 oracle=analyze.legacy.gun_focus_oracle(before,1400,800,True)
 choices=[];guns=[]
 for i in (1,2):
  q=oracle[i];p=q['command']+[q['target'],False];b=[before[i-1][3],400,0,0,12,False];commit=i==1
  choices.append(dict(id=i,mode='commit' if commit else 'escape',source='P16' if commit else 'v6',transition=False,baseline=b,p16=p,command=p if commit else b))
  guns.append(dict(id=i,focus=q['focus'],anchor=q['anchor'],target=q['target'],targetV=q['values_by_gun'][q['target']],command=p,raw=p[:2],clipped=p[:2],minimum=0,range=320))
 rows=[observer(0,before),observer(1,post),dict(v7Telemetry=True,step=1,t=1/30,prepareTime=0,accepted=True,width=1400,height=800,prepare=before,choices=choices,guns=guns,escorts=[])]
 with gzip.open(tmp_path/'fake.jsonl.gz','wt') as f:
  for row in rows:f.write(json.dumps(row)+'\n')
 r=analyze.telemetry(dict(tag='fake',meta=dict(arm='v7'),summaries=[summary()]))
 assert r['chosen_target_V']==1.5
 assert r['P16_selected_chosen_target_V']==2
 assert r['actual_in_focus_band_fraction']==0 # post-focus moved to900; prepare distance300 would falsely pass
 assert r['counts']['post_alive_gun_and_focus_ticks']==1

def test_completion_metadata_drift_fails_closed(monkeypatch,tmp_path):
 monkeypatch.setattr(run,'RAW',tmp_path)
 (tmp_path/'x_COMPLETE.json').write_text(json.dumps(dict(meta=dict(head='novice'))))
 (tmp_path/'x_CLAIM.json').write_text(json.dumps(dict(meta=dict(head='regular'))))
 monkeypatch.setattr(run,'pins',lambda: {})
 with pytest.raises(RuntimeError,match='metadata drift'):run.verified('x')

def test_engineering_accounts_build_and_each_check_once(monkeypatch,tmp_path):
 import engineering
 monkeypatch.setattr(engineering,'HERE',tmp_path);monkeypatch.setattr(engineering,'admit',lambda _:{});monkeypatch.setattr(engineering,'sha',lambda _:'abc')
 (tmp_path/'BUILD.json').write_text(json.dumps(dict(identity={},fixture_sha256='abc',seconds=10)))
 (tmp_path/'CHECK_ATTEMPT_prior.json').write_text(json.dumps(dict(seconds=3)))
 clock=iter((0,1,4));monkeypatch.setattr(engineering.time,'monotonic',lambda:next(clock))
 monkeypatch.setattr(engineering.subprocess,'run',lambda *a,**k:subprocess.CompletedProcess([],0,'fake fixture suite\n',''))
 engineering.engineering()
 r=json.loads((tmp_path/'ENGINEERING.json').read_text());assert r['test_seconds']==3;assert r['total_seconds']==16
 assert len(list(tmp_path.glob('CHECK_ATTEMPT_*.json')))==2

def test_tuning_analysis_does_not_require_validation(monkeypatch,tmp_path):
 import analyze
 monkeypatch.setattr(analyze,'HERE',tmp_path);monkeypatch.setattr(analyze,'sha',lambda _:'tuninghash')
 metric=protocol.selection(fake(),0)
 candidates=[]
 for i in range(257):
  r=dict(ordinal=i,params={},selection=dict(metric,ordinal=i));candidates.append(r)
  (tmp_path/f'CANDIDATE_{i:03d}.json').write_text(json.dumps(r))
 monkeypatch.setattr(analyze,'tuning_receipt',lambda:dict(status='SELECTED',selected=candidates[0],selected_params={}))
 result=analyze.analyze_tuning()
 assert result['ranked_ordinals']==list(range(257))
 assert result['validation_used'] is False and result['fights']==8224
 assert not (tmp_path/'VALIDATION.json').exists()

def test_native_timeout_overshoot_never_becomes_a_win():
 s=summary();s['t']=150.0333333333274
 r=protocol.measure(s);assert r['win']==0 and r['timeout']==1 and r['termination_time']==s['t']
 s['t']=150+1/30+1e-8;assert protocol.measure(s)['timeout']==1
 s['t']=150+1/30+2e-8
 with pytest.raises(ValueError):protocol.measure(s)
 s=summary();s['t']=149.999;assert protocol.measure(s)['win']==1
