"""Historical bootstrap helper; final analyze.py includes subsequent pre-fight review fixes."""
from pathlib import Path
HERE=Path(__file__).resolve().parent;OLD=HERE.parent/'s4_volley_probe_v1'
s=(OLD/'analyze.py').read_text().replace("('P0','P1','P2','P3')","('P0','P4','P5','P6')")
s=s.replace('import pathlib,json,gzip,hashlib,time,collections','import pathlib,json,gzip,hashlib,time,collections,statistics,signal')
s=s.replace('holdInside=holdTicks=0;releaseGroups=[];arms=r[\'arm\']','releaseGroups=[];terminal=None;gunKills=[];ownGunDeaths=[]')
s=s.replace("if d['died']:deaths.append(d)","""if d['died']:
     deaths.append(d)
     if d['targetTeam']==1 and d['targetRole']=='artillery':gunKills.append(d)
     if d['targetTeam']==0 and d['targetRole']=='artillery':ownGunDeaths.append(d)""")
a=s.index("   enemy=[u for u in units.values()");b=s.index(' assert terminal==r[\'summary\']',a);s=s[:a]+s[b:]
s=s.replace(" assert len({d['target'] for d in deaths})==len(deaths)"," assert len({d['target'] for d in deaths})==len(deaths)\n assert sum(d['targetTeam']==1 for d in deaths)==50-s['enemySurvivors']")
s=s.replace('p3_held_unit_ticks_inside_enemy_band=holdInside,p3_held_unit_ticks=holdTicks,',"time_to_first_enemy_gun_kill_s=min((d['t'] for d in gunKills),default=None),own_gun_killers=[dict(source=d['source'],team=d['sourceTeam'],role=d['sourceRole'],target=d['target'],t=d['t']) for d in ownGunDeaths],enemy_gun_killers=[dict(source=d['source'],team=d['sourceTeam'],role=d['sourceRole'],target=d['target'],t=d['t']) for d in gunKills],")
s=s.replace(",'p3_held_unit_ticks_inside_enemy_band','p3_held_unit_ticks'",'')
s=s.replace("wins=[r['win_time_s'] for r in a if r['elimination_win']];aggregates.append", """wins=[r['win_time_s'] for r in a if r['elimination_win']]
   first=[r['time_to_first_enemy_gun_kill_s'] for r in a if r['time_to_first_enemy_gun_kill_s'] is not None]
   killers=collections.Counter((d['team'],d['role']) for r in a for d in r['own_gun_killers']);assert sum(killers.values())==sums['own_gun_losses']
   enemyKillers=collections.Counter((d['team'],d['role']) for r in a for d in r['enemy_gun_killers']);assert sum(enemyKillers.values())==sums['enemy_guns_destroyed']
   aggregates.append""")
s=s.replace("mean_S=sum(r['S'] for r in a)/20,","mean_S=sum(r['S'] for r in a)/20,first_gun_kill_fights=len(first),no_enemy_gun_kill_fights=20-len(first),mean_first_enemy_gun_kill_s=sum(first)/len(first) if first else None,median_first_enemy_gun_kill_s=statistics.median(first) if first else None,own_gun_killers=[dict(team=t,role=k,kills=v) for (t,k),v in sorted(killers.items())],enemy_gun_killers=[dict(team=t,role=k,kills=v) for (t,k),v in sorted(enemyKillers.items())],")
s=s.replace("start=time.time();awake=time.monotonic();fights=", """start=time.time();awake=time.monotonic()
 used=sum(json.loads((HERE/n).read_text())['awake_seconds'] for n in ('BUILD_TIMING.json','CHECK_TIMING.json','RUN_TIMING.json'))
 assert used<3600,'1h compute budget exhausted'
 def stop(signum,frame):raise TimeoutError('stored-only recount compute cap')
 signal.signal(signal.SIGALRM,stop);signal.alarm(max(1,int(min(1200,3600-used))))
 fights=""")
s=s.replace("own_losses_and_gun_deaths_reconciled=True,","own_losses_and_gun_deaths_reconciled=True,first_gun_kill_and_killers_reconciled=True,")
(HERE/'analyze.py').write_text(s)
