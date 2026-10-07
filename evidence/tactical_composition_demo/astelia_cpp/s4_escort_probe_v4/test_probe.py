"""Noncombat native preparation and synthetic provenance/measurement cases only."""
import importlib.util,gzip,pytest
from common import *
from metrics import point_for,reading

def load(name):
 spec=importlib.util.spec_from_file_location('escort_test_'+name,HERE/(name+'.py'));m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def test_native_prepare_fixture():
 m=json.loads(BINARY.with_suffix('.build.json').read_text());argv=m['commands'][0];obj=CPP/'build/escort_v4_fixture.o';argv=argv[:argv.index('-c')]+['-c',str(HERE/'fixture.cpp'),'-o',str(obj)];subprocess.run(argv,check=True,timeout=120)
 objects=[o for o in m['link'][1:-2] if not o.endswith('escort_v3_host.o')];exe=CPP/'build/escort_v4_fixture';subprocess.run([m['link'][0],str(obj),*objects,'-o',str(exe)],check=True,timeout=120)
 r=subprocess.run([str(exe)],capture_output=True,text=True,check=True,timeout=30);(HERE/'FIXTURE.log').write_text(r.stdout)

def test_pgrep_fail_closed_and_receipts(monkeypatch,tmp_path):
 import common
 monkeypatch.setattr(common,'HERE',tmp_path)
 for rc,out,err in ((3,'','Cannot get process list'),(1,'','sysmon error'),(1,'malformed no-match output',''),(0,'12 python pilot rev711_diag','')):
  monkeypatch.setattr(common.subprocess,'run',lambda *a,**k:subprocess.CompletedProcess([],rc,out,err))
  with pytest.raises(RuntimeError):common.pilot_gate(wait=False)
 monkeypatch.setattr(common.subprocess,'run',lambda *a,**k:subprocess.CompletedProcess([],1,'',''));common.pilot_gate()
 assert len(list(tmp_path.glob('PILOT_GATE_*.json')))==5

def test_receipt_skip_and_ambiguous_refusal(monkeypatch,tmp_path):
 import run
 monkeypatch.setattr(run,'RAW',tmp_path);monkeypatch.setattr(run,'HERE',tmp_path);monkeypatch.setattr(run,'admit',lambda p:dict(binary='test'))
 req=dict(options=dict(seed=1));write(tmp_path/'DECLARATION.json',{})
 assert run.verified('a',req) is None
 gate=tmp_path/'gate.json';write(gate,dict(status='CLEAR',declaration_sha256=sha(tmp_path/'DECLARATION.json'),binary=dict(binary='test'),attempts=[dict(argv=['pgrep'],returncode=1,stderr='',stdout='')]))
 exclusive(tmp_path/'a_CLAIM.json',dict(declaration_sha256=sha(tmp_path/'DECLARATION.json'),binary=dict(binary='test'),request_sha256=__import__('hashlib').sha256((json.dumps(req,indent=2)+'\n').encode()).hexdigest(),gate=dict(path='gate.json',sha256=sha(gate))))
 with pytest.raises(AssertionError,match='ambiguous'):run.verified('a',req)
 exclusive(tmp_path/'a_request.json',req);(tmp_path/'a.jsonl.gz').write_bytes(b'synthetic');metrics=dict(executed_fights=1,executed_steps=1,fork_settings=[],**{k:0 for k in run.HIDDEN_WORK});write(tmp_path/'a_stderr.log',metrics)
 r=dict(metrics=metrics,claim_sha256=sha(tmp_path/'a_CLAIM.json'),binary=dict(binary='test'),request_sha256=sha(tmp_path/'a_request.json'),raw_bytes=9,raw_sha256=sha(tmp_path/'a.jsonl.gz'),stderr_sha256=sha(tmp_path/'a_stderr.log'),summary=dict(controllerStatus='completed',controllerFailures=[0,0],complexDiagnostics=dict(numericalFailureTicks=0)))
 exclusive(tmp_path/'a_COMPLETE.json',r);assert run.verified('a',req)==r
 # Even matching receipt hashes cannot bless hidden work on resume.
 bad=dict(metrics,branch_steps=1);write(tmp_path/'a_stderr.log',bad);altered=dict(r,metrics=bad,stderr_sha256=sha(tmp_path/'a_stderr.log'));write(tmp_path/'a_COMPLETE.json',altered)
 with pytest.raises(AssertionError,match='hidden native work'):run.verified('a',req)
 write(tmp_path/'a_stderr.log',metrics);write(tmp_path/'a_COMPLETE.json',r)
 (tmp_path/'a.jsonl.gz').write_bytes(b'tampered')
 with pytest.raises(AssertionError):run.verified('a',req)

def test_independent_oracle_zero_and_ties():
 u=[3,0,1,500,400,100,9,259,0];own=[[2,0,2,500,400,100,10,320,0]];enemy=[[12,1,2,400,400,100,10,320,0],[11,1,2,600,400,100,10,320,0]]
 p=point_for(u,own,enemy,[],60,1400,800);assert p['direction']==3 and p['raw']==[560,400]
 enemy=[[11,1,2,500,400,100,10,320,0]];assert point_for(u,own,enemy,[],60,1400,800)['direction']==0

def test_stage_failure_budget(monkeypatch,tmp_path):
 import common
 monkeypatch.setattr(common,'HERE',tmp_path)
 @common.stage('failure',.01)
 def work():time.sleep(.1)
 with pytest.raises(TimeoutError):work()
 r=json.loads(next(tmp_path.glob('STAGE_failure_*.json')).read_text());assert r['status']=='STOP' and r['awake_seconds']>0 and r['utc_start'] and r['utc_end']

def test_pins_and_catalog():
 d=pins();assert d['arms']==['P12','P16'];assert len(set(d['development_seeds']+[d['engineering_seed']]))==21
 assert d['parameters']['d_P12']==60 and d['parameters']['S_P11']==60
 assert not d['judging_ledger_read'];admit(BINARY)

def test_shell_multiplicity_and_ambiguity():
 from metrics import ShellAudit,shell_summary
 guns=[1,0,2,0,0,100,10,320,0];r=[2,0,1,0,0,100,9,259,0];r2=[3,0,1,0,0,100,9,259,0];e=[11,1,2,0,0,100,10,320,0]
 a=ShellAudit();a.observe(dict(t=0,units=[guns,r,r2,e],damage=[]))
 launch=[11,2,1,0,0,1/30,2/30,40,False,False]
 a.observe(dict(t=1/30,launches=[launch],damage=[]))
 def damage(uid,hp):return dict(source=11,sourceTeam=1,sourceRole='artillery',target=uid,targetTeam=0,targetRole='ranged',dealt=hp,t=2/30)
 a.observe(dict(t=2/30,launches=[],damage=[damage(2,8),damage(2,4),damage(3,10)]))
 result=shell_summary(a.counts());assert result['own_ranged_victims_per_successful_enemy_escort_targeted_shell']==2
 assert result['counts']['escort_targeted_own_ranged_hp']==22
 assert shell_summary({})['own_ranged_victims_per_successful_enemy_escort_targeted_shell'] is None
 b=ShellAudit();b.observe(dict(t=0,units=[guns,r,r2,e],damage=[]));b.observe(dict(t=1/30,launches=[launch,launch],damage=[]))
 with pytest.raises(AssertionError,match='ambiguous'):b.observe(dict(t=2/30,launches=[],damage=[damage(2,8)]))

def test_exact_survival_event_boundary_and_terminal_hold():
 from metrics import gun_curve
 initial={1:[1,0,2],2:[2,0,2],3:[3,0,1]}
 c=gun_curve(initial,[dict(target=1,t=10),dict(target=3,t=5)])
 assert c==[dict(t=t,alive=1) for t in (10,20,30,45,60)]

def test_new_raw_file_without_completion_is_ambiguous(monkeypatch,tmp_path):
 import run
 monkeypatch.setattr(run,'RAW',tmp_path)
 (tmp_path/'fight_request.json').write_text('{}')
 with pytest.raises(AssertionError,match='ambiguous'):run.verified('fight',{})


def test_replication_conjunction_boundaries_and_cluster_uncertainty():
 from metrics import paired_clusters,cluster_uncertainty
 def row(a,h,w=26,S=1,f=0):return dict(arm=a,head=h,elimination_wins=w,mean_S=S,failure_count=f)
 rows=[row(a,h) for a in ('P12','P16') for h in ('regular','novice')]
 pairs=[dict(head=h,cluster=c,wins=dict(P12=0,P16=2 if c<12 else 0),win_difference=dict(P16=2 if c<12 else 0)) for h in ('regular','novice') for c in range(20)]
 assert reading(rows,pairs)['replicated']
 rows[3]['elimination_wins']=21;assert reading(rows,pairs)['replicated']
 for index,key,value in ((2,'elimination_wins',25),(2,'mean_S',0),(3,'mean_S',0),(3,'elimination_wins',20),(0,'failure_count',1)):
  original=rows[index][key];rows[index][key]=value;assert not reading(rows,pairs)['replicated'];rows[index][key]=original
 pairs[11]['win_difference']['P16']=0;assert not reading(rows,pairs)['replicated'];pairs[11]['win_difference']['P16']=2
 rows[2]['elimination_wins']=20;assert reading(rows,pairs)['reading']=='Not replicated'
 rows[2]['elimination_wins']=21;assert reading(rows,pairs)['reading'].startswith('Descriptive')
 u=cluster_uncertainty(pairs);assert len(u)==6 and u[1]['mean']==.6 and u[1]['cluster_standard_error']>0


def test_python_focus_oracle_and_splash_boundaries():
 from metrics import splash_value,gun_focus_oracle
 gun=[1,0,2,500,400,100,10,320,0];enemy=[11,1,2,800,400,100,10,320,0];low=[12,1,2,800,500,10,10,320,0];r=[13,1,1,849,400,100,9,259,0]
 assert splash_value(enemy,[enemy,low,r])==2
 q=gun_focus_oracle([gun,enemy,low,r],1400,800,True)[1];assert q['target']==11 and q['command']==[492,400,1,0]
 r[3]+=1e-4;assert gun_focus_oracle([gun,enemy,low,r],1400,800,True)[1]['target']==12
 gun[8]=320.1;q=gun_focus_oracle([gun,enemy,low,r],1400,800,True)[1];assert q['target'] is None and q['anchor']==12

def test_all_role_shell_multiplicity_friendly_and_zero():
 from metrics import ShellAudit,shell_summary
 g=[1,0,2,0,0,100,10,320,0];enemy=[[11,1,2,0,0,100,10,320,0],[12,1,1,0,0,100,9,259,0],[13,1,0,0,0,100,9,40,0]]
 a=ShellAudit();a.observe(dict(t=0,units=[g,*enemy],damage=[]));a.observe(dict(t=1/30,launches=[[1,11,0,0,0,1/30,2/30,40,False,False]],damage=[]))
 def damage(uid,role,team=1):return dict(source=1,sourceTeam=0,sourceRole='artillery',target=uid,targetTeam=team,targetRole=role,dealt=4,t=2/30)
 a.observe(dict(t=2/30,damage=[damage(11,'artillery'),damage(12,'ranged'),damage(12,'ranged'),damage(13,'melee'),damage(1,'artillery',0)]))
 s=shell_summary(a.counts());assert s['all_opposing_victims_per_successful_own_gun_targeted_shell']==3
 assert s['role_victims_per_successful_own_gun_targeted_shell']==dict(melee=1,ranged=1,artillery=1)
 assert s['counts']['own_gun_targeted_friendly_hp']==4 and s['counts']['own_gun_targeted_ranged_hp']==8
 assert shell_summary({})['all_opposing_victims_per_successful_own_gun_targeted_shell'] is None

@pytest.mark.parametrize('arm',[12,16])
def test_synthetic_role_arrival_and_gun_oracle(monkeypatch,tmp_path,arm):
 from metrics import gun_focus_oracle
 a=load('analyze');folder=tmp_path/'raw';folder.mkdir();monkeypatch.setattr(a,'HERE',tmp_path)
 gun=[1,0,2,500,400,100,10,320,0];r=[2,0,1,540,400,100,9,259,0];m=[3,0,0,540,400,100,9,40,0];e=[11,1,2,900,400,100,10,320,0];er=[12,1,1,778,400,100,9,259,0];prepare=[gun,r,m,e,er]
 points=[];actions=[];postunits=[gun,e,er]
 for u in (r,m):
  p=point_for(u,[gun],[e],[er],60,1400,800);base=[550,400,1,0,12,False];p12=[560,400,1,0,12,False] if u[2]==1 else base
  command=[560,400,1,0,12,False] if u[2]==1 or arm==17 else base
  points.append(dict(id=u[0],role=u[2],gun=p['gun'],threat=p['threat'],direction=p['direction'],raw=p['raw'],clipped=p['clipped'],baseTarget=12,base=base,p12=p12,command=command))
  actions.append([u[0],0,12,*command[:4],0,True]);postunits.append([*u[:3],command[0],400,*u[5:]])
 q=gun_focus_oracle(prepare,1400,800,arm==16)[1];gd=[*q['command'],0,False];actions.append([1,0,0,*gd[:4],0,True])
 initial=dict(observerV1=True,step=0,t=10-1/30,units=prepare,damage=[],actions=[])
 post=dict(observerV1=True,step=1,t=10,units=postunits,damage=[],actions=actions)
 audit=dict(escortProbe=True,arm=arm,step=1,t=10,prepareTime=10-1/30,prepare=prepare,points=points,dose=60,width=1400,height=800,applied=True,accepted=True,gunFocus=[dict(id=1,p12=gd,command=gd)])
 terminal=dict(controllerStatus='completed',t=10);fight=dict(id='fixture',summary=terminal)
 def save():
  with gzip.open(folder/'fixture.jsonl.gz','wt') as f:
   for row in (initial,post,audit,terminal):f.write(json.dumps(row)+'\n')
 save();g=a.escort_geometry(fight);melee=a.escort_geometry(fight,0)
 assert g['counts']['prepare_living_ranged_ticks']==1 and g['counts']['clipped_arrival_ticks']==1
 assert melee['counts']['prepare_living_ranged_ticks']==1 and melee['counts']['first_arrival_units']==1
 # Post death is retained in prepare denominator and unavailable/nonarrived.
 post['units']=[u for u in post['units'] if u[0]!=3];save();melee=a.escort_geometry(fight,0)
 assert melee['counts']['arrival_unavailable_ticks']==1 and melee['counts']['clipped_arrival_ticks']==0
 # Fail closed on the altered actual gun action.
 actions[-1][3]+=1;save()
 with pytest.raises(AssertionError):a.escort_geometry(fight)

def test_paired_clusters_preserve_orientation_pairing():
 from metrics import paired_clusters
 per=[dict(arm=a,head=h,cluster=c,orientation=o,elimination_win=(a!='P12' and o==0),S=(1 if a!='P12' else -1)) for a in ('P12','P16') for h in ('regular','novice') for c in range(20) for o in (0,1)]
 rows=paired_clusters(per);assert len(rows)==40 and rows[0]['win_difference']==dict(P16=1)
 assert rows[0]['mean_S_difference']==dict(P16=2)
 per.pop()
 with pytest.raises(AssertionError):paired_clusters(per)

def test_control_receipt_order_invariant_on_resume():
 from run import sanity
 rows=[dict(id=f'P12_{h}_c{c:02d}_o{o}',arm='P12',head=h,summary=dict(enemySurvivors=0,survivors=1,t=20,artilleryAlive=[1,0])) for h in ('regular','novice') for c in range(20) for o in (0,1)]
 first=sanity(rows);resumed=sanity(list(reversed(rows)))
 assert {k:v for k,v in first.items() if k!='utc'}=={k:v for k,v in resumed.items() if k!='utc'}

def test_directory_sync_after_receipt_create_replace_and_raw_creation(monkeypatch,tmp_path):
 import common
 synced=[];monkeypatch.setattr(common,'sync_directory',lambda p:synced.append(p))
 common.exclusive(tmp_path/'claim.json',{});common.write(tmp_path/'receipt.json',{});common.make_directory(tmp_path/'raw')
 assert synced==[tmp_path,tmp_path,tmp_path]
