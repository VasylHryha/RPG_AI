"""Read saved exact fixture results; never execute, replay or change verdicts."""
import gzip,json,math,hashlib
from pathlib import Path
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[4]
PIN='e66c8969d434f475c4289b6d09b048940d148055567c7c1acfc8bd2652fde357'
def load(n):return json.loads((OUT/n).read_text())
def write(n,v):
 with (OUT/n).open('x') as f:json.dump(v,f,indent=2,sort_keys=True,allow_nan=False);f.write('\n')
def slim(v):
 if isinstance(v,dict):return {k:slim(x) for k,x in v.items() if k not in ('records','episodes','events','native','reference','slots','within_memory','reward_updates','positions','stages')}
 if isinstance(v,list):return [slim(x) for x in v]
 return v

def full_path(row, neighbor_key, roots):
 incoming=row[neighbor_key]; reached=set(map(str,roots)); output=str(max(map(int,row['positions'])))
 while True:
  more={str(target) for target,sources in incoming.items() if any(str(source) in reached for source in sources)}-reached
  if not more:break
  reached.update(more)
 return output in reached

def main():
 from evidence.tactical_composition_demo.growing_shapes.runner.rev7_identity import assert_inputs
 from evidence.tactical_composition_demo.growing_shapes.runner.rev7_protocol import STOP_ROWS
 assert assert_inputs()['pin_sha256']==PIN
 m=load('MEASUREMENT_RECEIPT.json')
 with gzip.open(OUT/'HARNESS_RECEIPT.json.gz','rt') as f:receipt=json.load(f)
 results=receipt['results'];summary={n:slim(v) for n,v in results.items()}
 for n,v in results.items():
  if n in m['artifacts']:
   with gzip.open(OUT/(n+'.json.gz'),'rt') as f:assert json.load(f)==v
 holds=results.get('N1',{}).get('cases',{}).get('N1f',{}).get('entry_hold_through_24')
 agree=holds[0]==holds[1] if holds is not None else None
 f1c=results.get('F1',{}).get('configurations',{}).get('F1c',{})
 summary['F1c_numerical_hold']=dict(coarse_fine=holds,agree=agree,harness_verdict_preserved=f1c.get('verdict'),reported_F1c_verdict='NUMERICALLY_UNRESOLVED' if agree is False else f1c.get('verdict','NOT_RUN'))
 if 'F1' in results and 'configurations' in results['F1']:
  for n in ('F1a','F1b','F1c'):
   c=results['F1']['configurations'][n];rows=c['records'];out=str(max(map(int,rows[0]['positions'])))
   g=dict(first_endpoint_time=rows[0]['time'],final_time=rows[-1]['time'],ordinary_span_initial_declared={'F1a':0.,'F1b':1.112,'F1c':2.78}[n],ordinary_span_first_final=[r['ordinary_span']['span'] for r in (rows[0],rows[-1])],ordinary_radius_first_final=[r['ordinary_span']['radius'] for r in (rows[0],rows[-1])],source_site_distance_first_final=[r['source_site_distance'] for r in (rows[0],rows[-1])],output_radius_first_final=[math.hypot(*r['positions'][out]) for r in (rows[0],rows[-1])],source_access_fraction=sum(r['drive_access'] for r in rows)/len(rows),source_drive_fraction=sum(r['exposure']['0']['drive'] for r in rows)/len(rows),output_drive_fraction=sum(r['exposure'][out]['drive'] for r in rows)/len(rows),pins_invariant=all(r['pin_invariant'] for r in rows),minimum_distances={k:min(vals) if (vals:=[r['minimum_distances'][k] for r in rows if r['minimum_distances'][k] is not None]) else None for k in ('element_element','element_site')},unique_phase_topologies=len({json.dumps(r['neighbors'],sort_keys=True) for r in rows}),shortcut_directed_edges_first_final=[sum(abs(int(i)-int(j))>1 for i,js in r['neighbors'].items() for j in js) for r in (rows[0],rows[-1])])
   g['full_graph_path_fraction']=sum(full_path(r,'neighbors',[0] if r['drive_access'] and r['exposure']['0']['drive'] else []) for r in rows)/len(rows)
   g['strong_graph_path_fraction']=c['path_exposure']
   g['graph_definition']='G_s: live lambda*K*exp(-r*r)/full_receiver_degree >= 0.5 /s; full G uses unchanged directed held Ntheta lists'
   summary['F1']['configurations'][n]['geometry']=g
  for scale,c in results['F1']['configurations']['F1d']['runs'].items():
   rows=c['records'];summary['F1']['configurations']['F1d']['runs'][scale]['exposure_geometry']=dict(path_fraction=sum(any(r['paths']) for r in rows)/len(rows),source_access_fraction=sum(r['exposure']['0']['sensor_access'] for r in rows)/len(rows),source_drive_fraction=sum(r['exposure']['0']['drive'] for r in rows)/len(rows),positions_first_final=[r['positions'] for r in (rows[0],rows[-1])],unique_phase_topologies=len({json.dumps(r['phase_topology'],sort_keys=True) for r in rows}),full_graph_path_fraction=sum(full_path(r,'phase_topology',[i for ids in r['effective_roots'].values() for i in ids]) for r in rows)/len(rows),path_fraction_graph='G_s')
 if 'F5' in results and 'starts' in results['F5']:
  for start,c in results['F5']['starts'].items():
   selected=[e for e in c['events'] if e['rule'] in ('B-out','B-path') or e.get('values',{}).get('birth_rule') in ('B-out','B-path')]
   write('F5'+start+'_BIRTH_EVENTS.json',selected)
   summary['F5']['starts'][start]['birth_event_evidence']='F5'+start+'_BIRTH_EVENTS.json'
   pooled=[]
   for checkpoint in (40,45,50):
    rows=[e for e in c['episodes'] if e['checkpoint']==checkpoint]
    # These descriptive checkpoint means do not replace the harness pooled gate.
    def wrap(v):return (v+math.pi)%(2*math.pi)-math.pi
    aa=[];bb=[];ee=[]
    for e in rows:
     own=e['own']['decisions'];other=e['other']['decisions'];lesion=e['lesion']['decisions']
     absent=not any(d['has_output'] for d in own)
     aa.append(0. if absent else sum(abs(wrap(a['angle']-b['angle'])) for a,b in zip(own,other))/len(own))
     bb.append(0. if absent else sum(abs(wrap(a['angle']-b['angle'])) for a,b in zip(own,lesion))/len(own))
     ee.append([sum(d['paths'][j] for d in own)/len(own) for j in range(8)])
    pooled.append(dict(checkpoint=checkpoint,paired_episodes=len(rows),A=sum(aa)/len(aa),B=sum(bb)/len(bb),E=[sum(v[j] for v in ee)/len(ee) for j in range(8)],used_in_verdict=False))
   summary['F5']['starts'][start]['checkpoint_descriptive']=pooled
   deferred=[e for e in c['events'] if e['rule']=='birth_terminal' and e.get('values',{}).get('birth_rule')=='B1' and e['values'].get('outcome')=='deferred_output_first']
   summary['F5']['starts'][start]['deferred_output_first']=dict(total=len(deferred),per_site={str(s):sum(e['values'].get('site')==s for e in deferred) for s in range(8)})
   summary['F5']['starts'][start]['birth_counts']={rule:sum(e['rule']==rule for e in c['events']) for rule in ('B-out','B-path')}
   summary['F5']['starts'][start]['birth_times']={rule:[e['time'] for e in c['events'] if e['rule']==rule] for rule in ('B-out','B-path')}
   # Validate descriptive reconstruction of pooled means, without deciding a verdict.
   assert abs(sum(v['A'] for v in pooled)/3-c['A'])<1e-12
   assert abs(sum(v['B'] for v in pooled)/3-c['B'])<1e-12
 for name in ('F3','F4'):
  if name in results and 'stages' in results[name]:
   stages=[stage for trace in results[name]['stages'] for stage in trace]
   summary[name]['RK4_stages']=len(stages)
   summary[name]['exact_zero_output_checked_in_harness']=results[name]['verdict']=='PASS'
 stop_rows=[]
 evaluations=dict(integration_not_tested_reviewed=False,source_unit_endpoint_mismatch=False,engines_not_ready_reviewed=False,protocol_changed_after_results=False)
 if 'N1' in results:evaluations['N1_failed_or_invalid']=results['N1']['verdict'] in ('FAIL','INVALID')
 evaluations['fixture_invalid']=any(v['verdict']=='INVALID' for v in results.values())
 if any(results.get(n,{}).get('verdict')=='FAIL' for n in ('F1','F2','F3','F4')):evaluations['F1_F4_failed']=True
 elif all(n in results for n in ('F1','F2','F3','F4')):evaluations['F1_F4_failed']=False
 if 'F5' in results:evaluations['F5_failed']=results['F5']['verdict']=='FAIL'
 if 'F7' in results:evaluations['F7_unmatched']=results['F7']['verdict']=='FAIL'
 for q,a,role in STOP_ROWS:stop_rows.append(dict(question=q,outcome='YES' if evaluations.get(q) is True else 'NO' if evaluations.get(q) is False else 'NOT_EVALUATED',action=a,role=role))
 write('STOP_ROW_OUTCOMES.json',stop_rows)
 old=ROOT/'evidence/tactical_composition_demo/growing_shapes/runner/rev75_fixture_run_20261006/A7_DEVELOPMENT_COST_PROJECTION.json'
 work=json.loads(old.read_text())['workload'];cost=m['timings']
 nrate=cost['N1']['awake_seconds']/120000 if 'N1' in cost and results['N1']['verdict']!='INVALID' else None
 frate=cost['F1']['awake_seconds']/192000 if 'F1' in cost and results['F1']['verdict']!='INVALID' else None
 assay=cost['F4']['awake_seconds']/10 if 'F4' in cost and results['F4']['verdict']!='INVALID' else None
 projection=dict(measured_substep_denominators=dict(N1=120000,F1=192000),status='A7_PARTIAL_TOTAL_NOT_QUALIFIED',workload=work,N1_composite_awake_seconds_per_substep=nrate,F1_composite_awake_seconds_per_substep=frate,F4_mixed_native_reference_awake_seconds_per_assay_episode=assay,training_hours_N1_proxy=None if nrate is None else work['training_world_frames']*20*nrate/3600,training_hours_F1_proxy=None if frate is None else work['training_world_frames']*20*frate/3600,all_assay_hours_F4_proxy=None if assay is None else work['total_assay_episodes_max_all_four_tasks']*assay/3600,site_body_off_added_hours_F4_proxy=None if assay is None else 2048*assay/3600,F5_composite_awake_seconds=cost.get('F5',{}).get('awake_seconds'),F5_measured_workload=dict(live_world_frames=16000,frozen_assay_episodes=180) if 'F5' in results and 'starts' in results['F5'] else None,F6_frozen_assay_composite_seconds_per_episode=cost['F6']['awake_seconds']/140 if 'F6' in results and results['F6']['verdict']!='INVALID' else None,F7_control_M_live_composite_seconds_per_frame=cost['F7']['awake_seconds']/8000 if 'F7' in results and results['F7']['verdict']!='INVALID' else None,F8_move_memory_live_composite_seconds_per_frame=cost['F8']['awake_seconds']/6400 if 'F8' in results and results['F8']['verdict']!='INVALID' else None,grown_population_training_rate=None,grown_population_assay_rate=None,qualification_rate=None,recovery_rate=None,B_path_rate=None,donor_capture_rate=None,qualified_total_hours=None,lower_or_upper_bound=False,limitation='Whole-call composites include setup, diagnostics, growth/recovery and task work. F5 mixes live growth with frozen assays and cannot isolate their rates. F6 frozen memory, F7 control-M and F8 reward tasks are different workloads. Training proxies are alternatives, not additive; site-body-off is already included in all-assay workload. Shared-machine load prevents isolated timing claims. No development executed.')
 write('A7_DEVELOPMENT_COST_PROJECTION.json',projection)
 write('MEASURED_SUMMARY.json',dict(verdict=m['verdict'],results=summary,timings=cost,total=m['total'],not_run=receipt['not_run'],harness_stops=receipt['stops']))
 report=[m['verdict'],'',f'Revision 7.11 measurement-tool re-run at pinned identity `{PIN}`. All 69 pinned scientific inputs matched at start and after execution. The unchanged pinned Harness.run_all was called ONCE, with no line or bytecode observation hooks. Every returned field and the exact harness receipt are persisted; F5 start status and any stop-blocked fixtures are recorded below. All earlier evidence is preserved. This is new outcome-informed engineering evidence under the reviewed revision 7.11 output-first B1/B-path scheduler. Historical F5/F7 fixture reuse is disclosed by design sections 13–18; it is not independent replication. F5 results of the first attempt were never persisted or observed. This re-run repairs measurement-tool evidence; it is not independent replication.','', 'Execution grant: approval_reference = docs/decisions/0031-owner-run-approval-policy.md; integration_review = evidence/tactical_composition_demo/growing_shapes_review_claude/REV711_FIXTURE_READINESS.md (READY_FOR_FIXTURES, Claude). Owner explicitly approved this run in the task despite the estimate. C6 quiet timing was deliberately cancelled by Claude on owner instruction; the stopped session and BrokenPipeError are expected and unrelated. No wait for C6. Clarification is recorded in C6_START_BOUNDARY.json. Recorded planning estimate: 5460 s / 91 min; with 20% scheduling allowance: 6552 s / 109.2 min. These are planning scenarios, not bounds.','', 'Owner reported concurrency with 0g v5 development and C6 performance analysis. Load averages and CPU count are recorded at call boundaries and in OBSERVED_LOAD_SAMPLES.jsonl; per-task CPU attribution is unavailable. Actual contention is included in timings; no quiet-machine claim. Execution used caffeinate.','', 'The new wrapper first passed a tiny fabricated harness persistence test for complete and failed F5 gates, retaining both starts and opaque nested data exactly. The tested rev75c whole-call wrapper was adapted for this pin and execution grant. The passing synthetic check binds the executed wrapper hash. No real fixture was used to test the wrapper.','', '| Fixture/call | Verdict | Start UTC | End UTC | Awake s | Elapsed UTC s |','|---|---|---|---|---:|---:|']
 for n in ('N1','F1','F1a','F1b','F1c','F1d','F2','F3','F4','F5','F5i','F5ii','F6','F7','F8','F9'):
  c=cost.get(n);verdict=results.get(n,{}).get('verdict','NOT_RUN')
  if n in ('F1a','F1b','F1c','F1d'):verdict=results.get('F1',{}).get('configurations',{}).get(n,{}).get('verdict','NOT_RUN')
  if n in ('F5i','F5ii'):verdict=results.get('F5',{}).get('starts',{}).get('i' if n=='F5i' else 'ii',{}).get('verdict','NOT_RUN')
  if n=='F1c' and agree is False:verdict='NUMERICALLY_UNRESOLVED (harness '+verdict+')'
  report.append(f"| {n} | {verdict} | {c['start_utc'] if c else 'null'} | {c['end_utc'] if c else 'null'} | {c['awake_seconds'] if c else 'null'} | {c['elapsed_utc_seconds'] if c else 'null'} |")
 report+=['', 'Individual clocks for inline F1a–c and F5i–ii are unavailable: the pinned harness returns no such clocks. Their enclosing whole calls are timed. No subfixture boundaries are inferred. F1 includes nested F1d and its persistence; do not sum them. Each call excludes its own subsequent persistence, while harness total includes stage persistence/cleanup and excludes final receipt serialization. Awake uses mach_absolute_time, continuous uses mach_continuous_time, elapsed is UTC end minus start.','', 'Total harness execution envelope: `'+json.dumps(m['total'],sort_keys=True)+'`','', 'N1 criterion: h=.005 vs .00125 at λ=32; wrapped/unwrapped phase max each ≤.01 rad; free-position max ≤.01 m.u.; phase and motion topology agreement each ≥.99; pins invariant; applicable entry times within .1 s or both absent. N1a–e 16 s; N1f 24 s. N1g 16 s is descriptive, SENSITIVITY_NOT_ACCURACY, used_in_verdict=False. Missing/nonfinite data remain INVALID.','', '| N1 case | Verdict | Wrapped rad | Unwrapped rad | Position m.u. | Entry coarse/fine s | Nθ | Nx | Pins |','|---|---|---:|---:|---:|---|---:|---:|---|']
 for n,c in results.get('N1',{}).get('cases',{}).items():
  report.append(f"| {n} | {c['verdict']} | {c['maximum_wrapped_phase']} | {c['maximum_unwrapped_phase']} | {c['maximum_free_position']} | {c['entry_times'] if c['entry_applicable'] else 'N/A'} | {c['Ntheta_agreement']} | {c['Nx_agreement']} | {c['pins_invariant']} |")
 report+=['',f'N1f F1c hold through t=24 coarse/fine = {holds}; agreement = {agree}. Reported F1c verdict = {summary["F1c_numerical_hold"]["reported_F1c_verdict"]}; harness verdict preserved = {f1c.get("verdict")}. A disagreement marks F1c numerically unresolved and prevents development readiness; the original harness verdict is never rewritten.','', 'N1g exactly specified slip: member 0 first endpoint departure ≥.5 rad from initial unwrapped carrier-relative π; direction is displacement sign; time is first crossing, bracketed by preceding endpoint (initial t=0 if first). No crossing means NOT_OBSERVED with null direction/time/bracket. Escape is not a completed 2π winding. Actual returned measurements:','']
 for row in results.get('N1',{}).get('cases',{}).get('N1g',{}).get('slip',[]):report.append('`'+json.dumps(row,sort_keys=True)+'`\n')
 report+=['N1 descriptive estimator validity and minimum-distance measurements (coarse/fine):','']
 for n,c in results.get('N1',{}).get('cases',{}).items():
  mins=[{k:min(vals) if (vals:=[r['minimum_distances'][k] for r in rows if r['minimum_distances'][k] is not None]) else None for k in ('element_element','element_site')} for rows in c['records']]
  report.append(n+': `'+json.dumps(dict(validity=c['validity'],minimum_distances=mins),sort_keys=True)+'`\n')
 report+=['F1a/b: entry ≤.3 rad by t=16 after t=8 step, hold every endpoint through 16, directed path ≥.8 over 160 s. F1c: entry by 16, hold through 24, path and source access ≥.8 over 160 s, response persistence ≥.8 over [16,160]; output pin invariant. Descriptive sustained delay/error at 12/four-second margin do not change the gate. F1 path fractions are measured on the strong-link graph G_s, with the full-graph G fraction beside it below. Full-graph fractions are descriptive reconstruction from recorded directed held lists and identical effective roots; no dynamics replay. Actual values and compaction geometry (first endpoint t=.1, not t=0):','']
 for n in ('F1a','F1b','F1c'):
  report.append(n+': `'+json.dumps(summary.get('F1',{}).get('configurations',{}).get(n,{'status':'NOT_RUN'}),sort_keys=True)+'`\n')
 report+=['F1d same F1b scaffold/input at λ=1 vs 8 and 32, h=.005, descriptive; absent entry is deadline-censored. Delays, holds, deadline errors, paths/access and endpoint geometry:','']
 for scale,c in summary.get('F1',{}).get('configurations',{}).get('F1d',{}).get('runs',{}).items():report.append('λ='+scale+': `'+json.dumps(c,sort_keys=True)+'`\n')
 report+=['F2 criterion: exact zero empty angle/magnitude, no path, bitwise-identical disconnected stepped/unstepped phase streams for 160 endpoints. F3: output site drive exactly +0.0 at all 80 RK4 stages. F4: output internal phase coupling exactly zero at all 80 stages; exact site0/oracle decoder angles; native/reference magnitude/choice/path/output-presence exact, wrapped-angle tolerance 1e-12. Measured exactness:','']
 for n in ('F2','F3','F4'):report.append(n+': `'+json.dumps(summary.get(n,{'status':'NOT_RUN'}),sort_keys=True)+'`\n')
 report+=['F5 both starts: pooled paired frozen assays at checkpoints 40/45/50 require A≥.3, B≥.3, max(E)≥.5; i requires a B-out birth, ii a B-path birth. Individual checkpoint means are descriptive, not separate cuts. All events are retained in F5.json.gz and extracted B-out/B-path opportunity/terminal/birth events in the per-start BIRTH_EVENTS files.','']
 for start,c in summary.get('F5',{}).get('starts',{}).items():
  # Identity already pinned in exact receipt; avoid repeating long inventory in prose.
  row={k:v for k,v in c.items() if k!='identity_snapshot'}
  report.append('F5('+start+'): `'+json.dumps(row,sort_keys=True)+'`\n')
 report+=['Per-site F5 E and B-path waiting for both starts (descriptive; no finite waiting bound):','', '| Start | Site | E | Eligible | Unserved | Current wait | Maximum wait | Accepted births | Last outcome |','|---|---:|---:|---:|---:|---:|---:|---:|---|']
 for start,c in results.get('F5',{}).get('starts',{}).items():
  for site in range(8):
   waiting=c['B_path_waiting']['sites'][str(site)];cnt=waiting['lifetime_counters'] or {}
   report.append('| '+str(start)+' | '+str(site)+' | '+str(c['E'][site])+' | '+' | '.join(str(cnt.get(k)) for k in ('eligible_checks','unserved_checks','current_wait_checks','maximum_wait_checks','accepted_births'))+' | '+str(waiting['last_outcome'])+' |')
 report+=['F5 descriptive not-qualified summary uses check-endpoint intervals (0,640], (640,720], (720,800] and whole (0,800] s. All starts, including small cohorts, remain in denominators; zero denominator=null; fast-transient frames count once; recovery skips excluded. The returned qualification_validity above gives window counts, not-qualified invalid-pair counts/fractions and frame counts. used_in_verdict=False; no tolerance changed.','', 'F6 descriptive encoding/retention/circular correlations need ≥5 defined pairs; baselines count unique recipient episodes. F7 gate requires every requested control-M B1 birth matched, unmatched=0; zero requests means matched_fraction=null. F8 descriptive move then memory reward/eligibility/B1 demand from live F5(i). F9 four literal descriptive decoder observations, demands/actions. Measurements:','']
 for n in ('F6','F7','F8','F9'):report.append(n+': `'+json.dumps({k:v for k,v in summary.get(n,{'status':'NOT_RUN'}).items() if k!='identity_snapshot'},sort_keys=True)+'`\n')
 report+=['Order and stop policy: N1 first, FAIL/INVALID blocks all later. F1a–c then descriptive F1d; F2–F4 still run after F1 FAIL; any F1–F4 FAIL stops before F5. Then F5 both starts; F5 FAIL stops; then F6/F7; F7 FAIL stops; then F8/F9. Any INVALID stops the next stage. Actual not_run = '+str(receipt['not_run'])+'; exact harness stops = `'+json.dumps(receipt['stops'],sort_keys=True)+'`.','', '| Stop question (§9.7 + §10.1) | Outcome | Yes action | Responsible role |','|---|---|---|---|']
 for row in stop_rows:report.append(f"| {row['question']} | {row['outcome']} | {row['action']} | {row['role']} |")
 report+=['', 'A7 development-run cost projection from measured whole-call rates: `'+json.dumps(projection,sort_keys=True)+'`','', 'Qualified total remains null: whole-call measurement cannot separate live, frozen assay, qualification, recovery, B-path and donor-capture costs. Small-scaffold N1/F1 training projections are alternative arithmetic proxies. F4 mixed native/reference assay proxy is unqualified for grown populations. F6/F7/F8 composites describe their actual tasks only. Never sum alternatives or add site-body-off twice. No pricing execution, training, development, evaluation panels, judging entropy or registration occurred. Only authorized fixture growth and fixture frozen assays ran.','', 'Review/disposition are tracked beside this attempt because the owner explicitly prohibits edits to docs/PLAN_CURRENT.md. Delivery verification and preservation are in the delivery note and adjacent manifest. Fixture pass/fail is distinct from scientific acceptance and authorization for development.','', 'Assisted-by: Codex:GPT-6']
 with (OUT.parent/'REV711_FIXTURE_REPORT.md').open('x') as f:f.write('\n'.join(report)+'\n')
 print(json.dumps(dict(verdict=m['verdict'],stages={n:r['verdict'] for n,r in results.items()},not_run=receipt['not_run'],hold_agree=agree)))
if __name__=='__main__':
 import sys
 sys.path.insert(0,str(ROOT));main()
