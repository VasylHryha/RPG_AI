// JSON boundary only. The simulation modules never include the legacy value API.
#include "world.h"
#include "observer_v1.h"
#include "config_codec.h"
#include "formation.h"
#include "search.h"
#include "api.h"
#include "catalog_data.h"
#include "s3_diagnostics.h"
#include "s4_v6_controller.h"
#include "js_value.h"
#include "collective.h"
#include <set>
#include <map>
#include <iomanip>

int attributionContract();
int v6ControllerContract();
namespace {
using js::V;
V encodeSummary(const astelia::World& w,bool extended,bool endCounts) {
  const auto s=astelia::summary(w);
  auto out=js::obj({{"mode",w.config->mode},{"melee",s.melee},{"ranged",s.ranged},{"artillery",s.artillery},
    {"total",s.total},{"wasted",s.wasted},{"monsterDeaths",double(s.monsterDeaths)},
    {"hunterKills",double(s.hunterKills)},{"aliveSeconds",s.aliveSeconds},{"enemyDamage",s.enemyDamage},
    {"survivors",double(s.survivors)},{"enemySurvivors",double(s.enemySurvivors)},{"t",s.t}});
  if(extended){const auto& stats=w.stats;js::set(out,"controllerFailures",js::arr({double(stats.controllerFailures[0]),double(stats.controllerFailures[1])}));
    js::set(out,"controllerStatus",stats.controllerFailures[0]||stats.controllerFailures[1]?"controller_failure":"completed");
    js::set(out,"crossTeamDealt",js::arr({stats.dealtToEnemy[0],stats.dealtToEnemy[1]}));js::set(out,"crossTeamTaken",js::arr({stats.takenFromEnemy[0],stats.takenFromEnemy[1]}));
    js::set(out,"friendlyDealt",js::arr({stats.friendlyDealt[0],stats.friendlyDealt[1]}));js::set(out,"friendlyTaken",js::arr({stats.friendlyTaken[0],stats.friendlyTaken[1]}));}
  if(endCounts){std::array<unsigned,2> guns{};for(const auto& u:w.units)if(u.occupied&&u.alive&&u.role==astelia::Role::Artillery)++guns[u.team];
    js::set(out,"artilleryAlive",js::arr({double(guns[0]),double(guns[1])}));}
  return out;
}
V state(const astelia::World& w,std::map<astelia::UnitId,V>& history,bool debug) {
  for (const auto& u:w.units) if (u.id && (u.occupied || !history.count(u.id) || js::truth(js::get(history.at(u.id),"alive")))) {
    const auto* t=w.resolve(u.target);
    history[u.id]=js::obj({{"id",double(u.id)},{"team",double(u.team)},
      {"role",astelia::roleName(u.role)},
      {"x",u.pos.x},{"y",u.pos.y},{"hp",u.hp},{"cd",u.cooldown},{"alive",u.alive},
      {"target",t?V(double(t->id)):V(nullptr)}});
    const auto kind=w.state[size_t(&u-w.units.data())].kind;
    if(kind!=astelia::invalidSlot)js::set(history[u.id],"kind",w.config->kinds.at(kind).name);
    if(debug){const auto& s=w.state[size_t(&u-w.units.data())];js::set(history[u.id],"debug",js::obj({{"prep",s.prep},{"ep",s.energy},{"epMax",s.energyMax},{"r",u.radius},{"maxhp",u.maxhp},{"slotX",s.slot.x},{"slotY",s.slot.y},{"hasSlot",s.hasSlot}}));}
  }
  js::Args units;for (const auto& entry:history) units.push_back(entry.second);
  auto out=js::obj({{"t",w.time},{"units",js::arr(std::move(units))}});
  if(w.config->decisionTrace){js::Args decisions;for(const auto& row:w.decisionTrace){const auto& d=row.decision;
    decisions.push_back(js::obj({{"id",double(row.id)},{"team",double(row.team)},{"target",row.target?V(double(row.target)):V(nullptr)},
      {"x",d.goal.x},{"y",d.goal.y},{"multiplier",d.multiplier},{"stop",d.stop},{"release",double(d.release)},
      {"move",d.move},{"keep",d.keep},{"post",d.post},{"bound",d.bound},{"inReach",row.inReach}}));}
    js::set(out,"decisions",js::arr(std::move(decisions)));}
  if(debug){V packs=js::obj({});for(uint8_t team=0;team<2;++team){const auto& p=w.packs[team];if(!p.enabled)continue;
    V entry=js::obj({{"plan",astelia::planName(p.plan)},{"anchor",js::obj({{"x",p.anchor.x},{"y",p.anchor.y},{"ax",p.facing.x},{"ay",p.facing.y}})},{"formed",p.formed}});
    const auto features=astelia::bcFeatures(w,team,w.config->lookahead[team].plans);js::Args encoded;for(auto x:features)encoded.emplace_back(x);js::set(entry,"features",js::arr(std::move(encoded)));
    js::set(entry,"search",js::obj({{"hasChoice",p.search.hasChoice},{"score",p.search.score},{"last",p.search.last}}));js::set(packs,std::to_string(team),entry);}
    js::Args records;for(const auto& record:w.bcData){js::Args features;for(auto x:record.features)features.emplace_back(x);records.push_back(js::arr({js::arr(std::move(features)),double(record.choice)}));}
    js::set(out,"debug",js::obj({{"packs",packs},{"bcData",js::arr(std::move(records))},{"eventCount",double(w.events.size())}}));}return out;
}
V fight(V request,astelia::WorkCounters& counts,uint64_t& fights,bool testControllers,bool capture) {
  try {
  const auto operation=js::str(js::get(request,"operation"));
  if(operation=="rng"){const auto seed=js::get(request,"seed"),rounds=js::get(request,"rounds");if(seed.tag!=V::Number||!std::isfinite(seed.n)||rounds.tag!=V::Number||!std::isfinite(rounds.n)||rounds.n<0||rounds.n>1000000||rounds.n!=std::floor(rounds.n))throw std::invalid_argument("invalid opponent draw");js::Args names;for(auto& name:astelia::drawOpponents(seed.n,uint32_t(rounds.n),js::str(js::get(request,"drawMode"))=="pool"))names.emplace_back(name);return js::arr(std::move(names));}
  if(operation=="catalog")return js::parse(astelia::catalogJSON);
  auto config=std::make_shared<const astelia::Config>(astelia::configuration(request));
  for(const auto& p:config->controllers)if(p.name=="passthrough"&&!testControllers)throw std::invalid_argument("passthrough is test-only");
  bool extended=js::truth(js::get(request,"s3"));for(const auto& p:config->controllers)if(p.name=="resonator"||p.name=="morale"||p.name=="pushpull")extended=true;
  auto w=astelia::World::create(config); ++fights;
  const bool killerTelemetry=js::truth(js::get(request,"killerTelemetry"));
  astelia::observer_v1::Sink observer;observer.world=killerTelemetry?&w:nullptr;
  astelia::observer_v1::Scope observerScope(observer);
  const auto dumpObserver=[&](uint64_t step){
    if(!killerTelemetry)return;
    js::Args damage,dodges,launches,units,actions,entries;
    for(const auto& d:observer.damage){js::Args reach,inside,support;for(auto id:d.inReach)reach.push_back(double(id));for(auto id:d.insideBand)inside.push_back(double(id));for(auto g:d.support)support.push_back(js::arr({double(g.id),g.pos.x,g.pos.y,g.range,g.minimum}));damage.push_back(js::obj({{"source",double(d.source)},{"sourceRole",astelia::roleName(d.sourceRole)},{"sourceTeam",double(d.sourceTeam)},
      {"target",double(d.target)},{"targetRole",astelia::roleName(d.targetRole)},{"targetTeam",double(d.targetTeam)},{"amount",d.amount},{"dealt",d.dealt},{"t",d.time},{"distance",d.centreDistance},{"died",d.died},
      {"killer",d.died?V(double(d.source)):V(nullptr)},{"sourceX",d.sourcePos.x},{"sourceY",d.sourcePos.y},{"targetX",d.targetPos.x},{"targetY",d.targetPos.y},{"lethalGunInReach",js::arr(std::move(reach))},{"lethalGunInsideBand",js::arr(std::move(inside))},{"lethalGunSupport",js::arr(std::move(support))}}));}
    for(const auto& d:observer.dodges)dodges.push_back(js::arr({double(d.id),double(d.team),d.from.x,d.from.y,d.goal.x,d.goal.y}));
    for(const auto& l:observer.launches)launches.push_back(js::arr({double(l.source),double(l.target),double(l.team),l.point.x,l.point.y,l.born,l.at,l.splash,l.barrage,l.slow}));
    for(const auto& e:observer.entries){js::Args reach,inside,others;for(auto id:e.inReach)reach.push_back(double(id));for(auto id:e.insideBand)inside.push_back(double(id));for(auto v:e.otherGuns)others.push_back(js::arr({v.x,v.y}));
      entries.push_back(js::obj({{"unit",double(e.unit)},{"gun",double(e.gun)},{"role",astelia::roleName(e.role)},{"t",e.time},{"distance",e.distance},{"from",js::arr({e.from.x,e.from.y})},{"pos",js::arr({e.pos.x,e.pos.y})},{"gunPos",js::arr({e.gunPos.x,e.gunPos.y})},{"cover",double(e.cover)},{"inReach",js::arr(std::move(reach))},{"insideBand",js::arr(std::move(inside))},{"otherGuns",js::arr(std::move(others))}}));}
    for(auto i:w.active){const auto& u=w.units[i];if(!u.alive)continue;const auto& a=w.state[i];const auto* target=w.resolve(u.target);
      units.push_back(js::arr({double(u.id),double(u.team),double(uint8_t(u.role)),u.pos.x,u.pos.y,u.hp,u.radius,u.range,a.minRange,a.hasSlot,a.slot.x,a.slot.y,a.prep,target?V(double(target->id)):V(nullptr)}));}
    for(const auto& row:w.decisionTrace){const auto& d=row.decision;actions.push_back(js::arr({double(row.id),double(row.team),double(row.target),d.goal.x,d.goal.y,d.multiplier,d.stop,double(d.release),d.move,d.keep,d.post,d.bound,row.inReach}));}
    js::V collective=js::V(nullptr);
    for(const auto& controller:w.controllers)if(auto* c=dynamic_cast<astelia::control::CollectiveProbeV1*>(controller.get())){
      const auto& p=c->probe();js::Args guns,escorts,enemies;
      for(const auto& g:p.guns)guns.push_back(js::arr({double(g.id),g.x,g.y,g.gx,g.gy,g.px,g.py,g.solved,g.staged,g.inReach,g.outside}));
      for(const auto& e:p.escorts)escorts.push_back(js::arr({double(e.id),e.x,e.y,e.gx,e.gy,e.arrived,double(e.focus)}));
      for(const auto& e:p.enemies)enemies.push_back(js::arr({double(e.id),e.x,e.y,e.minRange,e.range}));
      collective=js::obj({{"t",p.t},{"firstSight",p.firstSight},{"wave",p.wave},{"waveTime",p.waveTime},{"target",double(p.target)},{"ready",double(p.ready)},{"living",double(p.living)},{"reason",p.reason},{"guns",js::arr(std::move(guns))},{"escorts",js::arr(std::move(escorts))},{"enemyGuns",js::arr(std::move(enemies))}});
    }
    std::cout<<js::stringify(js::obj({{"observerV1",true},{"step",double(step)},{"t",w.time},{"units",js::arr(std::move(units))},{"actions",js::arr(std::move(actions))},{"entries",js::arr(std::move(entries))},{"damage",js::arr(std::move(damage))},{"dodges",js::arr(std::move(dodges))},{"launches",js::arr(std::move(launches))}}))<<'\n';
    if(collective.tag!=js::V::Null)std::cout<<js::stringify(js::obj({{"collectiveProbe",collective}}))<<'\n';
    observer.damage.clear();observer.dodges.clear();observer.launches.clear();observer.entries.clear();
  };
  dumpObserver(0);
  const bool attributionDiagnostics=js::truth(js::get(request,"attributionDiagnostics"));
  if(attributionDiagnostics)for(auto& controller:w.controllers)if(auto* c=dynamic_cast<astelia::control::S3Controller*>(controller.get()))c->attributionDiagnostics(true);
  std::array<uint64_t,2> amplitudeSamples{},lowAmplitude{},argRateSamples{};std::array<double,2> absArgRate{};
  uint64_t tick=0; const bool trace=js::truth(js::get(request,"trace"));
  std::map<astelia::UnitId,V> history;
  const bool debug=js::truth(js::get(request,"debug"));
  const auto dump=[&](){std::cout<<js::stringify(js::obj({{"step",double(tick)},{"state",state(w,history,debug)}}))<<'\n';};
  if (trace) dump();
  const bool decisionDiagnostics=js::truth(js::get(request,"decisionDiagnostics"));
  const bool diagnostics=js::truth(js::get(request,"diagnostics"));std::array<astelia::control::DiagnosticHistory,2> histories;uint64_t second=1;
  const auto numeric=[](double n){return std::isfinite(n)?V(n):V(nullptr);};
  while (!w.done()) {astelia::coreStep(w);++tick;dumpObserver(tick);if (trace) dump();
    for(uint8_t side=0;side<2;++side)if(auto* c=dynamic_cast<astelia::control::S4V6Controller*>(w.controllers[side].get()))
      for(const auto& d:c->complexDiagnostic()){++amplitudeSamples[side];if(d.amplitude<.2)++lowAmplitude[side];if(d.rateValid){++argRateSamples[side];absArgRate[side]+=std::abs(d.argRate);}}
    // Output-only: read prepare(k) records after coreStep(k), including collision and clipping.
    if(decisionDiagnostics)for(uint8_t side=0;side<2;++side)if(auto* c=dynamic_cast<astelia::control::S3Controller*>(w.controllers[side].get())){
      js::Args rows,events;
      for(const auto& d:c->decisionDiagnostic()){
        double mx=0,my=0;for(const auto& u:w.units)if(u.id==d.id){mx=u.pos.x-d.x;my=u.pos.y-d.y;break;}
        const auto feasibility=astelia::control::v4Feasibility(d,mx,my);const auto& reason=feasibility.reason;const double cosine=feasibility.cosine;
        js::Args pairs;for(const auto& p:d.pairs)pairs.push_back(js::obj({{"enemy",double(p.enemy)},{"mode",p.commit?"commit":"escape"},{"remainingHold",p.remaining},{"preferred",p.preferred}}));
        rows.push_back(js::obj({{"id",double(d.id)},{"focus",d.focus?V(double(d.focus)):V(nullptr)},{"reference",d.reference?V(double(d.reference)):V(nullptr)},{"c",d.c},{"pairs",js::arr(std::move(pairs))},{"feasibility",reason.empty()?V(cosine):V(nullptr)},{"undefinedReason",reason.empty()?V(nullptr):V(reason)}}));
      }
      if(attributionDiagnostics){
        // Observer-only prepare geometry and release identities. Keep legacy trace bytes unchanged.
        for(auto& row:rows){const auto id=astelia::UnitId(js::num(js::get(row,"id")));const astelia::ObservedUnit* self=nullptr;
          for(const auto& u:w.observations[side].units)if(u.id==id){self=&u;break;}
          bool gunReach=false;if(self)for(const auto& enemy:w.observations[side].units)if(enemy.hp>0&&enemy.team!=side&&enemy.role==astelia::ObservedRole::Artillery&&astelia::control::v2Legal(enemy,*self)){gunReach=true;break;}
          js::set(row,"insideGunReach",gunReach);
        }
      }
      for(const auto& e:c->holdEvents())events.push_back(js::obj({{"id",double(e.id)},{"enemy",double(e.enemy)},{"reason",e.reason},{"duration",e.duration},{"planned",e.planned}}));
      if(attributionDiagnostics){
        for(auto& event:events){const auto id=astelia::UnitId(js::num(js::get(event,"id"))),enemy=astelia::UnitId(js::num(js::get(event,"enemy")));
          bool ownKnown=false,enemyKnown=false,ownDead=false,enemyDead=false;
          for(const auto& u:w.observations[side].units){if(u.id==id){ownKnown=true;ownDead=u.hp<=0;}if(u.id==enemy){enemyKnown=true;enemyDead=u.hp<=0;}}
          // Observation omits dead slots: the native world retains monotonic dead identities.
          for(const auto& u:w.units){if(u.id==id&&!ownKnown){ownKnown=true;ownDead=!u.alive;}if(u.id==enemy&&!enemyKnown){enemyKnown=true;enemyDead=!u.alive;}}
          js::set(event,"releaseCause",ownDead&&enemyDead?"both_death":ownDead?"own_death":enemyDead?"enemy_death":!ownKnown||!enemyKnown?"missing":"none");
        }
      }
      std::cout<<js::stringify(js::obj({{"decisionDiagnostics",true},{"step",double(tick)},{"prepareTime",w.observations[side].t},{"t",w.time},{"dt",w.dt},{"side",double(side)},{"units",js::arr(std::move(rows))},{"holdEvents",js::arr(std::move(events))}}))<<'\n';
    }
    if(capture)for(uint8_t side=0;side<2;++side)if(auto* c=dynamic_cast<astelia::control::S4V6Controller*>(w.controllers[side].get())){
      js::Args rows;for(const auto& u:c->complexModel())rows.push_back(js::obj({{"id",double(u.id)},{"target",double(u.target)},{"x",u.x},{"y",u.y},{"real",u.z.real()},{"imag",u.z.imag()},{"rate",u.omega},{"pressure",u.pressure}}));
      js::Args commitments;for(const auto& u:c->complexDiagnostic())commitments.push_back(js::arr({double(u.id),std::max(-1.0,std::min(1.0,u.real))}));
      std::cout<<js::stringify(js::obj({{"captureV6",true},{"side",double(side)},{"dt",w.dt},{"mu",c->mu()},{"K",c->knobs().K},{"K_t",c->knobs().Kt},{"n",double(c->lastTick().n)},{"units",js::arr(std::move(rows))},{"commitments",js::arr(std::move(commitments))}}))<<'\n';}
    if(capture)for(uint8_t side=0;side<2;++side)if(auto* c=dynamic_cast<astelia::control::S3Controller*>(w.controllers[side].get()))if(c->arm()!=astelia::control::Arm::PushPull&&!dynamic_cast<astelia::control::S4V6Controller*>(c)){js::Args rows;size_t i=0;for(const auto& u:c->model()){rows.push_back(js::obj({{"id",double(u.id)},{"target",double(u.target)},{"x",u.x},{"y",u.y},{"state",u.state},{"rate",u.rate},{"pressure",u.pressure},{"commitment",numeric(c->diagnostic()[i++].commitment)}}));}std::cout<<js::stringify(js::obj({{"capture",true},{"arm",c->arm()==astelia::control::Arm::Resonator?"resonator":"morale"},{"side",double(side)},{"dt",w.dt},{"K",c->knobs().K},{"K_t",c->knobs().Kt},{"units",js::arr(std::move(rows))}}))<<'\n';}
    if(diagnostics){js::Args sides;
      for(uint8_t side=0;side<2;++side)if(w.controllers[side]){
        if(auto* c=dynamic_cast<astelia::control::S4V6Controller*>(w.controllers[side].get())){
          if(w.time+1e-9<second)continue;js::Args members;
          for(const auto& u:c->complexDiagnostic())members.push_back(js::obj({{"id",double(u.id)},{"target",double(u.target)},{"real",u.real},{"imag",u.imag},{"amplitude",u.amplitude},{"arg",u.argValid?V(u.arg):V(nullptr)},{"argValid",u.argValid},{"argRate",u.rateValid?V(u.argRate):V(nullptr)},{"argRateReason",u.rateValid?V(nullptr):V(u.rateReason)}}));
          sides.push_back(js::obj({{"side",double(side)},{"skeleton","v6"},{"phaseCoherence",V(nullptr)},{"phaseCoherenceStatus","not_run"},{"distinctTargetPhases",V(nullptr)},{"distinctTargetPhasesStatus","not_run"},{"candidates",V(nullptr)},{"candidatesStatus","not_run"},{"reason","v5 scalar phase diagnostics do not apply to complex v6"},{"units",js::arr(std::move(members))}}));continue;
        }
        auto* controller=dynamic_cast<astelia::control::S3Controller*>(w.controllers[side].get());std::vector<astelia::control::DiagnosticUnit> units;
        if(controller)units=controller->diagnostic();else for(const auto& u:w.observations[side].units)if(u.team==side){astelia::UnitId target=0;for(const auto& actual:w.units)if(actual.id==u.id){const auto* t=w.resolve(actual.target);target=t?t->id:0;break;}units.push_back({u.id,target,u.x,u.y,0,1,0,0});}
        auto& history=histories[side];history.append(w.time,units);if(w.time+1e-9<second)continue;const bool phases=controller&&controller->arm()==astelia::control::Arm::Resonator;auto d=history.summarize(phases);
        js::Args members,candidates;for(const auto& c:d.candidates){js::Args ids;for(auto id:c)ids.push_back(double(id));candidates.push_back(js::arr(std::move(ids)));}
        for(const auto& u:units)members.push_back(js::obj({{"id",double(u.id)},{"target",double(u.target)},{"x",u.x},{"y",u.y},{"state",controller?numeric(u.state):V(nullptr)},{"commitment",numeric(u.commitment)},{"zOut",numeric(u.zOut)},{"zIn",numeric(u.zIn)}}));
        sides.push_back(js::obj({{"side",double(side)},{"phaseCoherence",d.coherenceValid?numeric(d.coherence):V(nullptr)},{"distinctTargetPhases",phases?V(double(d.distinct)):V(nullptr)},{"targetConcentration",d.concentration},{"windowReady",d.windowReady},{"candidates",js::arr(std::move(candidates))},{"units",js::arr(std::move(members))}}));}
      if(w.time+1e-9>=second){std::cout<<js::stringify(js::obj({{"diagnostics",true},{"t",w.time},{"second",double(second)},{"sides",js::arr(std::move(sides))}}))<<'\n';++second;}}
  }
  counts.branchUnitActions+=w.work->branchUnitActions;counts.branchProjectileSteps+=w.work->branchProjectileSteps;counts.branchSteps+=w.work->branchSteps;counts.forks+=w.work->forks;counts.searchCalls+=w.work->searchCalls;counts.inferenceCalls+=w.work->inferenceCalls;counts.candidateModels+=w.work->candidateModels;counts.artilleryRollouts+=w.work->artilleryRollouts;counts.artilleryPredictions+=w.work->artilleryPredictions;counts.artilleryCandidates+=w.work->artilleryCandidates;counts.predictionSteps+=w.work->predictionSteps;counts.predictionUnitSteps+=w.work->predictionUnitSteps;
  for(auto setting:w.work->branchSettings)counts.branchSettings[setting.first]+=setting.second;
  counts.outerSteps+=w.counters.outerSteps;counts.unitActions+=w.counters.unitActions;counts.projectileSteps+=w.counters.projectileSteps;
  auto result=encodeSummary(w,extended,js::truth(js::get(request,"endCounts")));
  for(uint8_t side=0;side<2;++side)if(auto* c=dynamic_cast<astelia::control::S4V6Controller*>(w.controllers[side].get())){
    js::set(result,"complexDiagnostics",js::obj({{"side",double(side)},{"samples",double(amplitudeSamples[side])},{"lowAmplitudeSamples",double(lowAmplitude[side])},{"fractionBelow02",amplitudeSamples[side]?V(double(lowAmplitude[side])/amplitudeSamples[side]):V(nullptr)},{"argRateSamples",double(argRateSamples[side])},{"argRateAbsSum",absArgRate[side]},{"argRateAbsMean",argRateSamples[side]?V(absArgRate[side]/argRateSamples[side]):V(nullptr)},{"argRateNullReason",argRateSamples[side]?V(nullptr):V("no_consecutive_valid_endpoints")},{"argValidityThreshold",.2},{"retryCount",double(c->retryCount())},{"numericalFailureTicks",double(c->failureCount())},{"mu",c->mu()},{"omega_ranged",c->knobs().rateR},{"omega_melee",0}}));}
  return result;
  } catch (const std::exception& e) { return js::obj({{"error",e.what()}}); }
}
} // namespace
int main(int argc,char** argv) {
  bool metrics=false,testControllers=false,capture=false;for (int i=1;i<argc;++i) {
    if (std::string(argv[i])=="--attribution-contract")return attributionContract();
    if (std::string(argv[i])=="--v6-contract")return v6ControllerContract();
    if (std::string(argv[i])=="--catalog") {std::cout<<astelia::catalogJSON<<'\n';return 0;}
    if (std::string(argv[i])=="--capture-s3")capture=true;else if (std::string(argv[i])=="--test-controllers")testControllers=true;else if (std::string(argv[i])=="--metrics") metrics=true;else {std::cerr<<"unknown argument\n";return 1;}
  }
  astelia::WorkCounters counts;uint64_t fights=0;
  std::string line;while (std::getline(std::cin,line)) {
    if (line.find_first_not_of(" \t\r\n")==std::string::npos) continue;
    try {
      V request=js::parse(line), result;
      if (request.tag==V::Heap && request.p->kind==js::Object::Array) {
        js::Args rows;for (auto r:request.p->items) rows.push_back(fight(r,counts,fights,testControllers,capture));result=js::arr(std::move(rows));
      } else result=fight(request,counts,fights,testControllers,capture);
      std::cout<<js::stringify(result)<<std::endl;
    } catch (const std::exception& e) {std::cout<<js::stringify(js::obj({{"error",e.what()}}))<<std::endl;}
    js::collect({},0);
  }
  if (metrics) std::cerr<<"{\"executed_fights\":"<<fights<<",\"executed_steps\":"<<counts.outerSteps
    <<",\"branch_steps\":"<<counts.branchSteps<<",\"forks\":"<<counts.forks<<",\"search_calls\":"<<counts.searchCalls<<",\"inference_calls\":"<<counts.inferenceCalls<<",\"candidate_models\":"<<counts.candidateModels<<",\"artillery_rollouts\":"<<counts.artilleryRollouts<<",\"artillery_predictions\":"<<counts.artilleryPredictions<<",\"artillery_candidates\":"<<counts.artilleryCandidates<<",\"prediction_steps\":"<<counts.predictionSteps<<",\"prediction_unit_steps\":"<<counts.predictionUnitSteps<<",\"branch_unit_actions\":"<<counts.branchUnitActions<<",\"branch_projectile_steps\":"<<counts.branchProjectileSteps<<",\"unit_actions\":"<<counts.unitActions<<",\"projectile_steps\":"<<counts.projectileSteps
    <<",\"cache_hits\":0,\"scope\":\"native_complete_engine\",\"fork_settings\":[";
  if(metrics){bool first=true;for(const auto& entry:counts.branchSettings){if(!first)std::cerr<<',';first=false;std::cerr<<'['<<std::setprecision(17)<<entry.first.first<<','<<entry.first.second<<','<<entry.second<<']';}std::cerr<<"]}\n";}
}
