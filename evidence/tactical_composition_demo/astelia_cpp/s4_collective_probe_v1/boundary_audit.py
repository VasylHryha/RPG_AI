"""Correct only the wrong derived-boundary diagnostic; preserve verified combat measurements."""
import pathlib,json,time,sys,signal
HERE=pathlib.Path(__file__).resolve().parent;sys.path.insert(0,str(HERE));import recount_final as final
sha=final.sha;write=final.write
start=time.time();awake=time.monotonic();used=60+sum(json.loads(p.read_text())['awake_seconds'] for p in HERE.glob('STAGE_*.json'))
def stop(*args):raise TimeoutError('boundary audit remaining compute cap')
signal.signal(signal.SIGALRM,stop);signal.alarm(max(1,int(min(1200,3600-used))))
old=json.loads((HERE/'SUMMARY.json').read_text());fights={r['id']:r for r in json.loads((HERE/'FIGHTS.json').read_text())};changed=[]
for i,row in enumerate(old['fights']):
 if row['arm']=='P5':continue
 r=fights[row['id']];assert sha(HERE/'raw'/(r['id']+'.jsonl.gz'))==r['raw_sha256'];a=final.geometry(r)
 for key,value in a.items():
  if key!='post_outside_gun_ticks':assert row[key]==value,(row['id'],key,row[key],value)
 if row['post_outside_gun_ticks']!=a['post_outside_gun_ticks']:changed.append(dict(id=row['id'],before=row['post_outside_gun_ticks'],after=a['post_outside_gun_ticks']))
 row['post_outside_gun_ticks']=a['post_outside_gun_ticks']
 if (i+1)%20==0:print(json.dumps(dict(audited=i+1,elapsed_s=time.monotonic()-awake)),flush=True)
aggregates=final.aggregate(old['fights'])
for before,after in zip(old['rows'],aggregates):
 for key,value in after.items():
  if key!='post_outside_gun_ticks':assert before[key]==value,(before['arm'],before['head'],key)
old['rows']=aggregates;assert old['outcome_reading']==final.reading(aggregates);write(HERE/'SUMMARY.json',old);write(HERE/'COMPACT.json',{k:v for k,v in old.items() if k!='fights'})
write(HERE/'BOUNDARY_VERIFICATION.json',dict(status='PASS',native_width=final._WIDTH,native_height=final._HEIGHT,scope='all120 intervention traces; only post_outside counter changed',changed=changed,all_other_measured_fields_identical=True,all_outcomes_identical=True,elapsed_seconds=time.time()-start,awake_seconds=time.monotonic()-awake,correct_script_sha256=sha(HERE/'recount_final.py'),auditor_sha256=sha(HERE/'boundary_audit.py'),factory_sha256=sha(final._CONFIG),codec_sha256=sha(final._CODEC)))
write(HERE/'FINAL_ANALYSIS_SOURCE_PINS.json',dict(recount_final_sha256=sha(HERE/'recount_final.py'),boundary_audit_sha256=sha(HERE/'boundary_audit.py'),native_arena_width=final._WIDTH,native_arena_height=final._HEIGHT,world_factory_sha256=sha(final._CONFIG),codec_sha256=sha(final._CODEC),original_fight_code_pins_preserved=True))
print(json.dumps(dict(status='CORRECTED_BOUNDARY_ONLY',changed_fights=len(changed),elapsed_s=time.monotonic()-awake)))
