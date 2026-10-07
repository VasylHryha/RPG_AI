"""One-time scaffold/declare helper. Never rerun once a fight exists."""
import pathlib,json,secrets,hashlib,subprocess,time,sys
HERE=pathlib.Path(__file__).resolve().parent;CPP=HERE.parent;REPO=CPP.parents[2];OLD=CPP/'s4_focus_probe_v1'
sys.path.insert(0,str(CPP));from build_admission import sha
write=lambda p,v:p.write_text(json.dumps(v,indent=2,allow_nan=False)+'\n')
assert not (HERE/'DECLARATION.json').exists()
prior=json.loads((OLD/'DECLARATION.json').read_text());used=set();ledgers={}
def collect(v):
 if isinstance(v,int):used.add(v)
 elif isinstance(v,list):
  for x in v:collect(x)
 elif isinstance(v,dict):
  for x in v.values():collect(x)
for name in [*prior['previous_development_ledgers'],str((OLD/'DECLARATION.json').relative_to(REPO))]:
 if pathlib.Path(name).name=='S4_SEED_LEDGER.json':continue
 p=REPO/name;collect(json.loads(p.read_text()));ledgers[name]=sha(p)
seeds=[]
while len(seeds)<11:
 x=0xC0000000+secrets.randbelow(0x40000000)
 if x not in used and x not in seeds:seeds.append(x)
tracked=subprocess.check_output(['git','ls-files','-z'],cwd=REPO).decode().split('\0')
# Protect engine/controller inputs, frozen state and historical outputs; unrelated living project docs may evolve independently.
protected={n:sha(REPO/n) for n in tracked if n and (REPO/n).is_file() and (n.startswith(('evidence/tactical_composition_demo/astelia_cpp/','geomind/','experiments/','milestones/','research/rrg/')) or n in ('AGENTS.md','STATUS.json','pyproject.toml','uv.lock','evidence/tactical_composition_demo/DESIGN_0G.md'))}
params=dict(staging_margin_px=30,ready_fraction=.8,arrival_px=20,fallback_s=20,escort_px=60,arc_degrees=60,post_radius_px=308,commit_margin_px=12,workers=2,total_compute_cap_s=3600,stage_cap_s=1200,axis_lifetime='fixed per acquired target; target position follows observations',target_lifetime='initial shared anchor retained until death',arc_assignment='recomputed each tick by angle relative to acquired axis; id ties',one_gun_arc='zero angle',single_enemy_axis='enemy to own gun centroid, +x if coincident',zero_vector='+x',staging='outermost nonnegative intersection of all equal-radius enemy exclusion disks on positive ray',readiness='theoretical un-clipped staging point; missing solution ineligible; ceil(.8*n), n>0',first_sight='first prepare snapshot with own and enemy guns; full sight, normally 1/30s',line_angle='PCA of living enemy centres; smallest axis change modulo pi; pre-death prepare endpoint',exposure='inclusive native enemy band, sampled at post-step positions of living committed own guns',simultaneity='first post-wave prepare snapshot with ceil(.8*n) living guns reaching current shared target; P5 not applicable',outcome='descriptive matched patterns, bundled mechanisms not causally identified; mixed patterns inconclusive',beat_p5='greater mean enemy gun kills and greater mean gun exchange (kills minus own gun losses)',p9_adds_nothing='does not improve both mean kills and exchange above best qualifying P7/P8',sanity='regular P5 mean own gun losses [7,10], enemy guns destroyed [1,6]; report before reading others')
write(HERE/'DECLARATION.json',dict(status='DECLARED_BEFORE_FIGHTS',created_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),design_commit='d100332',entropy='fresh OS secrets; high development partition; judging ledger never read',development_seeds=seeds[:10],engineering_seed=seeds[10],previous_development_ledgers=ledgers,arms=['P5','P7','P8','P9'],heads=['regular','novice'],orientations=[0,1],controlled_team=0,knobs=prior['knobs'],parameters=params,protected=protected))
write(HERE/'DEVELOPMENT_SEED_LEDGER.json',dict(status='fresh development only; single use; not judging',seeds=seeds[:10],engineering_seed=seeds[10],previous_development_ledgers=ledgers))
from s3_v6_runner import request
for head in ('regular','novice'):
 req=request(dict(arm='resonator',skeleton='v6',params=prior['knobs'],opponent=head,seed=seeds[0],swapSides=False,controlledSide=0,setting='s4_full_head',endCounts=True));req['options']['ai'][0].update(controller='P5',skeleton='collective_probe_v1');req.update(killerTelemetry=True,decisionTrace=True);write(HERE/(head.upper()+'_REQUEST_TEMPLATE.json'),req)
# Copy observer host, adding output-only controller-owned probe telemetry. Old host and objects stay untouched.
host=(CPP/'src/native/host_observer_v1.cpp').read_text().replace('#include "../js_value.h"','#include "js_value.h"\n#include "collective.h"')
needle='    std::cout<<js::stringify(js::obj({{"observerV1",true}'
pos=host.index(needle)
insert='''    js::V collective=js::V(nullptr);
    for(const auto& controller:w.controllers)if(auto* c=dynamic_cast<astelia::control::CollectiveProbeV1*>(controller.get())){
      const auto& p=c->probe();js::Args guns,escorts,enemies;
      for(const auto& g:p.guns)guns.push_back(js::arr({double(g.id),g.x,g.y,g.gx,g.gy,g.px,g.py,g.solved,g.staged,g.inReach,g.outside}));
      for(const auto& e:p.escorts)escorts.push_back(js::arr({double(e.id),e.x,e.y,e.gx,e.gy,e.arrived,double(e.focus)}));
      for(const auto& e:p.enemies)enemies.push_back(js::arr({double(e.id),e.x,e.y,e.minRange,e.range}));
      collective=js::obj({{"t",p.t},{"firstSight",p.firstSight},{"wave",p.wave},{"waveTime",p.waveTime},{"target",double(p.target)},{"ready",double(p.ready)},{"living",double(p.living)},{"reason",p.reason},{"guns",js::arr(std::move(guns))},{"escorts",js::arr(std::move(escorts))},{"enemyGuns",js::arr(std::move(enemies))}});
    }
'''
host=host[:pos]+insert+host[pos:]
# Preserve the legacy output byte format for P5 and original controllers. New metadata is a separate line.
needle='    observer.damage.clear();'
pos=host.index(needle);host=host[:pos]+'    if(collective.tag!=js::V::Null)std::cout<<js::stringify(js::obj({{"collectiveProbe",collective}}))<<\'\\n\';\n'+host[pos:]
(HERE/'host.cpp').write_text(host)
