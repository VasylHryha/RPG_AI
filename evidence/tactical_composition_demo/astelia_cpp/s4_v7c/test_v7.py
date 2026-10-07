"""No fights: native observation fixtures and fake protocol/process/receipt records."""
import importlib.util,json,pathlib,re,subprocess,sys
import pytest
HERE=pathlib.Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import common,protocol,run

def test_request_builder_against_actual_native_diagnostic_constraints():
 from request_audit import parse_only
 t=common.inherited_tuning()['selected_params']
 requests=[run.request(a,h,0xc1234567,o,t,True) for a in protocol.ARMS for h in protocol.HEADS for o in (0,1)]
 assert all(r['trace'] and r['decisionDiagnostics'] and r['attributionDiagnostics'] for r in requests)
 assert all(r.get('status')=='VALID' for r in parse_only(requests))
 # Reproduce both native constraints separately; the previous bug is rejected.
 q=json.loads(json.dumps(requests[0]));q['trace']=False
 assert parse_only([q])[0]['error']=='attributionDiagnostics requires trace and decisionDiagnostics'
 q['attributionDiagnostics']=False
 assert parse_only([q])[0]['error']=='decisionDiagnostics requires trace'
 q['decisionDiagnostics']=False;q['killerTelemetry']=False
 assert parse_only([q])[0]['error']=='decisionTrace requires trace'
 q=run.request('v7','regular',0xc1234567,0,t,False)
 assert parse_only([q])[0]['status']=='VALID'

def test_exactly_one_request_change_from_v7b():
 import ast
 old=HERE.parent/'s4_v7b/run.py'
 function=next(n for n in ast.parse(old.read_text()).body if isinstance(n,ast.FunctionDef) and n.name=='request')
 scope=dict(read=common.read,HERE=HERE)
 exec(compile(ast.Module(body=[function],type_ignores=[]),str(old),'exec'),scope)
 t=common.inherited_tuning()['selected_params']
 for a in protocol.ARMS:
  for h in protocol.HEADS:
   for o in (0,1):
    before=scope['request'](a,h,0xc1234567,o,t,True);after=run.request(a,h,0xc1234567,o,t,True)
    before['trace']=True
    assert before==after

def test_all_actual_requests_native_parse_before_seal():
 from request_audit import audit
 result=audit()
 assert result['requests']==400 and result['templates']==20
 assert result['executed_fights']==result['executed_steps']==result['worlds_created']==0
 assert result['binary_dry_validation']['status']=='NOT_SUPPORTED'
 cells=list(run.validation_plan(common.read(HERE/'THETA_ORIGIN.json')))
 expected={(a,h,c,o) for a in protocol.ARMS for h in protocol.HEADS for c in range(20) for o in (0,1)}
 assert {(m['arm'],m['head'],m['cluster'],m['orientation']) for _,_,m in cells}==expected
 t=common.inherited_tuning()['selected_params'];historical=common.read(HERE/'THETA_ORIGIN.json')['historical_theta']
 for _,rs,m in cells:
  assert rs[0]['options']['ai'][0]['params']==(historical if m['arm']=='historicalP16' else t)
  assert rs[0]['options']['ai'][1]['level']==m['head']

@pytest.mark.parametrize('field,value',[
 ('unknown',True),('s3','yes'),('mode','invalid'),('trace','yes'),
 ('options.rules','invalid'),('options.scenario','invalid'),('options.seed','invalid'),
 ('options.dt',0),('options.duration',-1),('options.swapSides',1),
 ('options.army.melee',-1),('options.army.ranged',1.5),('options.army.artillery',1000001),
 ('options.perception',0),('options.sandboxAbilities','no'),
 ('options.ai.0.controller','invalid'),('options.ai.0.skeleton','invalid'),
 ('options.ai.0.params.mu',3),('options.ai.0.params.omega_ranged',3),
 ('options.ai.0.params.extra',1),('options.ai.1.level','invalid')])
def test_native_rejects_other_invalid_request_fields(field,value):
 from request_audit import parse_only
 q=run.request('v7','regular',0xc1234567,0,common.inherited_tuning()['selected_params'],True)
 target=q;parts=field.split('.')
 for part in parts[:-1]:target=target[int(part)] if isinstance(target,list) else target[part]
 target[parts[-1]]=value
 assert 'error' in parse_only([q])[0]

def test_no_tuning_entrypoint_and_committed_theta():
 t=common.inherited_tuning();assert t['selected']['ordinal']==161
 assert not hasattr(run,'tuning') and not hasattr(run,'candidate')
 assert not (HERE/'TUNING.json').exists()
 p=subprocess.run([sys.executable,str(HERE/'run.py'),'tune'],env=dict(common.os.environ,S4_V7_CAFFEINATED='1'),capture_output=True,text=True,timeout=10)
 assert p.returncode==2 and 'invalid choice' in p.stderr

def test_historical_origin_drift_rejected(monkeypatch,tmp_path):
 origin=common.read(HERE/'THETA_ORIGIN.json')
 origin['historical_theta']=dict(origin['selected_params'])
 (tmp_path/'THETA_ORIGIN.json').write_text(json.dumps(origin))
 monkeypatch.setattr(common,'HERE',tmp_path)
 with pytest.raises(RuntimeError,match='historical theta'):common.inherited_tuning()

def test_fresh_entropy_and_preservation():
 from verify_delivery import entropy,preservation
 entropy();preservation()

def test_validation_budget_excludes_tuning_and_engineering(monkeypatch,tmp_path):
 monkeypatch.setattr(common,'HERE',tmp_path)
 (tmp_path/'ENGINEERING.json').write_text(json.dumps(dict(total_seconds=5000)))
 (tmp_path/'SEAL.json').write_text(json.dumps(dict(seconds=5)))
 assert common.spent()==0
 (tmp_path/'ATTEMPT_x.json').write_text(json.dumps(dict(status='PASS',stage='validate',seconds=10)))
 assert common.spent()==10
 (tmp_path/'ATTEMPT_y.json').write_text(json.dumps(dict(status='STOP',stage='analyze_validate',seconds=3)))
 assert common.spent()==13

def test_unknown_raw_cell_stops_before_execution(monkeypatch,tmp_path):
 monkeypatch.setattr(run,'RAW',tmp_path);monkeypatch.setattr(run,'pins',lambda:{})
 monkeypatch.setattr(run,'validation_plan',lambda _:[])
 (tmp_path/'unknown_CLAIM.json').write_text('{}')
 with pytest.raises(RuntimeError,match='unexpected validation cell'):run.audit_raw()

@pytest.mark.parametrize('field,value',[('status','STOP'),('fights',399),('selected_params',{}),('omega0_duplicate',True),('tuning_sha256','changed'),('declaration_sha256','changed'),('records',{})])
def test_cached_validation_receipt_drift_fails_closed(monkeypatch,tmp_path,field,value):
 theta=dict(omega_ranged=1.5775291057474368)
 monkeypatch.setattr(run,'HERE',tmp_path);monkeypatch.setattr(run,'RAW',tmp_path)
 monkeypatch.setattr(run,'pins',lambda:{})
 monkeypatch.setattr(run,'audit_raw',lambda:None)
 monkeypatch.setattr(run,'tuning_receipt',lambda:dict(selected_params=theta))
 monkeypatch.setattr(run,'tuning_hash',lambda:'tuning')
 monkeypatch.setattr(run,'sha',lambda _:'hash')
 cells=[(str(i),[dict(request=i)],dict(cell=i)) for i in range(400)]
 monkeypatch.setattr(run,'validation_plan',lambda _:cells)
 monkeypatch.setattr(run,'verified',lambda tag,requests:dict(tag=tag,meta=dict(cell=int(tag))))
 records=[dict(tag=tag,meta=meta) for tag,_,meta in cells]
 correct=run.validation_result(records)
 (tmp_path/'VALIDATION.json').write_text(json.dumps(correct))
 assert run.validation_receipt()==correct
 wrong=dict(correct);wrong[field]=value
 (tmp_path/'VALIDATION.json').write_text(json.dumps(wrong))
 with pytest.raises(RuntimeError,match='validation receipt drift'):run.validation_receipt()

def test_unclosed_attempt_blocks_cached_run_before_any_execution(monkeypatch):
 monkeypatch.setattr(sys,'argv',['run.py','validate'])
 monkeypatch.setattr(run,'pins',lambda:{})
 def unclosed():raise RuntimeError('unclosed attempt')
 monkeypatch.setattr(run,'spent',unclosed)
 with pytest.raises(RuntimeError,match='unclosed'):run.main()

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
 with pytest.raises(TimeoutError,match='projected'):common.project(0,0,10,1000,10,500)
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

def test_native_timeout_overshoot_never_becomes_a_win():
 s=summary();s['t']=150.0333333333274
 r=protocol.measure(s);assert r['win']==0 and r['timeout']==1 and r['termination_time']==s['t']
 s['t']=150+1/30+1e-8;assert protocol.measure(s)['timeout']==1
 s['t']=150+1/30+2e-8
 with pytest.raises(ValueError):protocol.measure(s)
 s=summary();s['t']=149.999;assert protocol.measure(s)['win']==1


@pytest.mark.parametrize('slow',[False,True])
def test_ten_parallel_workers_warmup_and_measured_rate(monkeypatch,tmp_path,slow):
 """Ten concurrent fake workers, two records each; never launches a native fight."""
 import threading,time,types
 monkeypatch.setattr(common,'HERE',tmp_path)
 clock=[2.6]
 monkeypatch.setattr(common,'time',types.SimpleNamespace(monotonic=lambda:clock[0]))
 barrier=threading.Barrier(10);release=[threading.Event() for _ in range(10)]
 def fake_worker(index,deadline):
  barrier.wait(timeout=5)
  if index:assert release[index].wait(timeout=5)
  return dict(summaries=[{},{}])
 monkeypatch.setattr(run,'execute',fake_worker)
 dl=run.Deadline(time.monotonic()+10)
 executor=run.Executor(dl,{},64.311132083,0,8624,4112)
 rows=executor.tasks(range(10))
 try:
  # The old formula projects 11,396 s here. Nine other workers are in flight.
  next(rows)
  first=common.read(tmp_path/'PROJECTION.json')
  assert first['status']=='WARMUP' and first['projected_seconds'] is None
  assert first['completed_this_attempt']==2 and first['warmup_batches']==10
  assert executor.pool.maximum_pending==10
  for i in range(1,9):
   release[i].set();next(rows)
   assert common.read(tmp_path/'PROJECTION.json')['status']=='WARMUP'
  clock[0]=30 if slow else 2.7
  release[9].set()
  if slow:
   with pytest.raises(TimeoutError,match='projected compute'):next(rows)
  else:next(rows)
  measured=common.read(tmp_path/'PROJECTION.json')
  assert measured['status']=='PROJECTED'
  assert measured['completed_batches_this_attempt']==10
  assert measured['completed_this_attempt']==20
  assert measured['completed_fights_per_wall_second']==pytest.approx(20/clock[0])
  expected=64.311132083+clock[0]+(8624-20)/(20/clock[0])+120
  assert measured['projected_seconds']==pytest.approx(expected)
  assert (measured['projected_seconds']>3600)==slow
 finally:
  for event in release:event.set()
  rows.close();executor.close()


def test_projection_small_stage_resume_and_hard_cap(monkeypatch,tmp_path):
 import types
 monkeypatch.setattr(common,'HERE',tmp_path)
 monkeypatch.setattr(common,'time',types.SimpleNamespace(monotonic=lambda:100))
 assert common.projection_warmup(400)==10
 assert common.projection_warmup(4112)==10
 assert common.projection_warmup(20)==1
 assert common.projection_warmup(21)==2
 # Only the new attempt's one completed batch counts; total includes later stages.
 common.project(5,0,2,20,1,20)
 r=common.read(tmp_path/'PROJECTION.json')
 assert r['completed_fights_per_wall_second']==.02
 assert r['projected_seconds']==pytest.approx(1125)

 with pytest.raises(TimeoutError,match='cumulative'):common.project(3500,0,2,8624,1,4112)
 assert common.read(tmp_path/'PROJECTION.json')['status']=='WARMUP'
 for done,total,batches in ((0,100,1),(2,1,1),(2,100,0)):
  with pytest.raises(ValueError):common.project(0,0,done,total,batches,4112)
 monkeypatch.setattr(common,'time',types.SimpleNamespace(monotonic=lambda:float('nan')))
 with pytest.raises(ValueError):common.project(0,0,2,100,1,4112)


def test_scientific_rules_and_native_sources_unchanged():
 old=HERE.parent/'s4_v7b'
 assert (HERE/'protocol.py').read_bytes()==(old/'protocol.py').read_bytes()
 assert common.admit(common.BINARY)==common.read(old/'DECLARATION.json')['binary']
 assert common.sha(HERE/'build/fixture')==common.read(old/'ENGINEERING.json')['fixture_sha256']
 assert common.FORBIDDEN=={'PLAN_CURRENT.md','DESIGN_0G.md','DESIGN_0H_REV7.md'}

def test_validation_analysis_and_render_scientific_functions_unchanged():
 import ast
 class OriginHashRouting(ast.NodeTransformer):
  def visit_Call(self,node):
   if isinstance(node.func,ast.Name) and node.func.id=='tuning_hash':return ast.parse("sha(HERE/'TUNING.json')").body[0].value
   if isinstance(node.func,ast.Name) and node.func.id=='validation_receipt':return ast.parse("read(HERE/'VALIDATION.json')").body[0].value
   return self.generic_visit(node)
 for name in ('analyze.py','render.py'):
  current=ast.parse((HERE/name).read_text());original=ast.parse((HERE.parent/'s4_v7b'/name).read_text())
  for function in current.body:
   if isinstance(function,ast.FunctionDef):
    baseline=next(f for f in original.body if isinstance(f,ast.FunctionDef) and f.name==function.name)
    assert ast.dump(OriginHashRouting().visit(function))==ast.dump(baseline)


def test_projection_counts_completions_ahead_of_fifo_consumer(monkeypatch,tmp_path):
 import threading,time,types
 monkeypatch.setattr(common,'HERE',tmp_path)
 monkeypatch.setattr(common,'time',types.SimpleNamespace(monotonic=lambda:2.7))
 barrier=threading.Barrier(10);others_counted=threading.Event()
 def fake_worker(index,deadline):
  barrier.wait(timeout=5)
  if index==0:assert others_counted.wait(timeout=5)
  return dict(index=index,summaries=[{},{}])
 monkeypatch.setattr(run,'execute',fake_worker)
 class ObservedExecutor(run.Executor):
  def completed(self,task,deadline):
   row=super().completed(task,deadline)
   with self.completion_lock:
    if self.batches==9:others_counted.set()
   return row
 executor=ObservedExecutor(run.Deadline(time.monotonic()+10),{},64,0,8624,4112)
 rows=executor.tasks(range(10))
 try:
  assert next(rows)['index']==0
  r=common.read(tmp_path/'PROJECTION.json')
  assert r['status']=='PROJECTED'
  assert r['completed_this_attempt']==20 and r['completed_batches_this_attempt']==10
  assert r['completed_fights_per_wall_second']==pytest.approx(20/2.7)
  assert r['projected_seconds']<3600
 finally:
  others_counted.set();rows.close();executor.close()
