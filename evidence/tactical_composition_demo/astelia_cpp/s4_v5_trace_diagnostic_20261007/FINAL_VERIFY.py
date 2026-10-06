"""One final focused stored-data validation after the review-driven correction batch."""
import gzip,json,time
from COMMON import CPP,HERE,RAW,REPO,pins,sha,write

def main():
    start=time.time();awake=time.monotonic();pins()
    identity=json.loads((HERE/'INPUT_IDENTITY.json').read_text())
    for n,h in identity['script_hashes'].items():assert sha(HERE/n)==h,n
    completed=json.loads((HERE/'FIGHTS.json').read_text());assert len(completed)==60
    finals={f['id']:json.loads((HERE/(f['id']+'_SUMMARY.json')).read_text()) for f in completed}
    supplements=json.loads((HERE/'SUPPLEMENT.json').read_text())
    assert len(supplements['fights'])==60 and supplements['awake_seconds']>0
    for f in supplements['fights']:
        m=finals[f['id']]
        assert {(d['id'],d['time_s'],d['role']) for d in f['deaths']}=={(d['id'],d['time_s'],d['role']) for d in m['deaths']}
        assert len(f['deaths'])==len(m['deaths'])
    assert sum(len(f['deaths']) for f in supplements['fights'])==2424
    original_count=0
    with gzip.open(RAW/'PRE_FIX_COMPACT_SUMMARIES.jsonl.gz','rt') as source:
        for line in source:
            original_count+=1;r=json.loads(line);old=r['original']
            for u in old['units']:assert u.pop('nearest_gun_mode_switches')==0
            assert old==finals[old['id']]
    assert original_count==60
    summary=json.loads((HERE/'SUMMARY.json').read_text())
    assert all(len(e['time_series_2s'])==75 for e in summary['endpoints'].values())
    for f in finals.values():
        assert len(f['units'])==50 and len(f['enemy_guns'])==10
        assert len(f['deaths'])==50-f['terminal']['survivors']
        assert all(d[k] is None for d in f['deaths'] for k in ('killer_id','killer_role','distance_to_killer_px','pair_mode_toward_killer'))
    viz=CPP.parent/'viz_0g/v5_trace_diagnostic_20261007';replay=json.loads((viz/'replays_v5.json').read_text())
    for f in replay['fights']:
        assert f['source_fight_id'] in ('p0_c00_o0','p1_c00_o0','p2_c00_o0')
        assert abs(f['frames'][-1][0]-f['summary']['t'])<1e-6
        assert sum(u[1]==0 for u in f['frames'][-1][1])==f['summary']['survivors']
        assert sum(u[1]==1 for u in f['frames'][-1][1])==f['summary']['enemySurvivors']
    original_viewer=CPP.parent/'viz_0g/index.html'
    assert sha(original_viewer)==json.loads((HERE/'VIEWER_VERIFICATION.json').read_text())['source_html_sha256']
    inventory=[dict(path=str(p.relative_to(REPO)),bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(RAW.rglob('*')) if p.is_file()]
    inventory += [dict(path=str(p.relative_to(REPO)),bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(HERE.glob('*.log'))]
    assert all(f['bytes']<45_000_000 for f in inventory)
    write(HERE/'RAW_FILES_OUTSIDE_GIT.json',dict(policy='All original raw traces, requests, seeds, claim, correction snapshots and logs remain local; each <45 MB.',files=inventory))
    write(HERE/'FINAL_VERIFICATION.json',dict(status='PASS_WITH_EXPLICIT_KILLER_TELEMETRY_GAP',stored_only=True,combat_executions=0,
       fights=60,own_deaths=2424,own_units=3000,enemy_guns=600,simultaneous_death_coverage_complete=True,
       measured_main_values_identical_to_original=True,original_execution_script_pins_unchanged=True,
       new_script_hashes={p.name:sha(p) for p in HERE.glob('*.py')},raw_inventory_files=len(inventory),
       raw_inventory_bytes=sum(f['bytes'] for f in inventory),raw_file_bytes_max=max(f['bytes'] for f in inventory),
       original_viewer_unchanged=True,replay_terminal_states_match=True,killer_fields_available=False,
       elapsed_seconds=time.time()-start,awake_seconds=time.monotonic()-awake))
    print('PASS: 60 fights, 2424 deaths including simultaneous victims, 3000 own units, 600 guns; zero combat')

if __name__=='__main__':main()
