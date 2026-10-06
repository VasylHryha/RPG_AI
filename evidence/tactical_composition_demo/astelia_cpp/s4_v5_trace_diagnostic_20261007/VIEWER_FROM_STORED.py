"""Create a new viewer copy from already recorded traces; no fights or edits to existing viewer."""
import json,re,gzip,math
from COMMON import CPP,write,sha,HERE
VIZ=CPP.parent/'viz_0g';TARGET=VIZ/'v5_trace_diagnostic_20261007'
replays=json.loads((TARGET/'replays_v5.json').read_text())
records={r['id']:r for r in json.loads((HERE/'FIGHTS.json').read_text())}
for fight in replays['fights']:
    rec=records[fight['source_fight_id']];last_state=last_capture=None
    for chunk in rec['trace_files'][-2:]:
        with gzip.open(HERE/chunk,'rt') as f:
            for line in f:
                if '"state":{' in line[:55]:last_state=json.loads(line)['state']
                elif line.startswith('{"capture":'):last_capture=json.loads(line)
    assert abs(last_state['t']-fight['summary']['t'])<1e-9
    if fight['frames'][-1][0]<last_state['t']-1e-6:
        cap={u['id']:u for u in last_capture['units']}
        fight['frames'].append([round(last_state['t'],6),[[u['id'],u['team'],replays['role_codes'][u['role']],round(u['x']),round(u['y']),round(u['hp']/u['debug']['maxhp'],3),
           u['target'] if u['target'] is not None else -1,
           round(cap[u['id']]['state']%(2*math.pi) if fight['arm']=='resonator' else cap[u['id']]['state'],3) if u['id'] in cap else None,
           round(cap[u['id']]['commitment'],3) if u['id'] in cap else None] for u in last_state['units'] if u['alive']]])
    assert abs(fight['frames'][-1][0]-fight['summary']['t'])<1e-6
write(TARGET/'replays_v5.json',replays)
html=(VIZ/'index.html').read_text()
stories={}
for f in replays['fights']:
    s=f['summary'];score=s['survivors']-s['enemySurvivors'];timeout=s['t']>=150
    stories[f['name']]=dict(label=f['arm'].title()+' vs '+f['opponent'],chip=['stall' if timeout else 'win' if score>0 else 'loss','Timeout' if timeout else 'Win' if score>0 else 'Loss'],
        title='Selected v5 stage-B knobs: '+f['source_fight_id'],
        text=f"Predeclared cluster 0, orientation 0. Survivor score {score:+d}; original recorded fight, not selected for its outcome. Enemy gun removal and phase rotation are descriptive. Killer identities were not exported. Read S4_V5_TRACE_DIAGNOSTIC.md for the full 60-fight comparison.")
html=re.sub(r'const STORIES = \{.*?\n\};', 'const STORIES = '+json.dumps(stories)+';',html,flags=re.S)
html=html.replace("fetch('replays_small.json')","fetch('replays_v5.json')")
html=html.replace('<h1>Resonator Battle Replays</h1>','<h1>v5 trace diagnostic replays</h1>')
html=re.sub(r'<p class="lede">.*?</p>','<p class="lede">Three predeclared fresh development fights at the unchanged v5 stage-B knobs. Use the full diagnostic report for the 60-fight comparison.</p>',html,count=1,flags=re.S)
html=re.sub(r'<p class="note">Seeds .*?</p>','<p class="note">Development only. Frames sampled at 5 Hz; phase is pre-integration and commitment is post-integration. Original viewer and its data remain unchanged.</p>',html,count=1,flags=re.S)
html=html.replace("Our units: the colour is the unit's beat (its phase). Units with the same colour are in step.", "Our colours show phase for resonator fights and the scalar morale state for morale fights. Matching colours alone do not establish synchronization.")
html=html.replace("Bright outline: committed (attack). Faded: pulling back.", "Outline brightness shows commitment c. It does not show the stored commit/escape pair mode: morale can retain escape while c is near zero.")
(TARGET/'index.html').write_text(html)
assert len(replays['fights'])==3 and all(len(f['frames'])>10 for f in replays['fights'])
assert 'replays_small.json' not in html and all(k in stories for k in ('resonator_vs_novice','resonator_vs_regular','morale_vs_regular'))
write(HERE/'VIEWER_VERIFICATION.json',dict(status='PASS_STRUCTURAL',browser_render_check=False,
     source_html_sha256=sha(VIZ/'index.html'),new_html_sha256=sha(TARGET/'index.html'),data_sha256=sha(TARGET/'replays_v5.json'),
     fights=[dict(id=f['source_fight_id'],frames=len(f['frames']),S=f['summary']['survivors']-f['summary']['enemySurvivors']) for f in replays['fights']]))
