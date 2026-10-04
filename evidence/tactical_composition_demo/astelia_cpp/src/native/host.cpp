// JSON boundary only. The simulation modules never include the legacy value API.
#include "world.h"
#include "config_codec.h"
#include "formation.h"
#include "search.h"
#include "../js_value.h"
#include <set>
#include <map>

namespace {
using js::V;
V summary(const astelia::World& w) {
  const auto& s=w.stats;
  return js::obj({{"mode",w.config->mode},{"melee",s.melee},{"ranged",s.ranged},{"artillery",s.artillery},
    {"total",s.melee+s.ranged+s.artillery},{"wasted",s.wasted},{"monsterDeaths",double(s.monsterDeaths)},
    {"hunterKills",double(s.hunterKills)},{"aliveSeconds",s.aliveSeconds},{"enemyDamage",s.enemyDamage},
    {"survivors",double(w.survivors(0))},{"enemySurvivors",double(w.survivors(1))},{"t",w.time}});
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
    if(debug){const auto& s=w.state[size_t(&u-w.units.data())];js::set(history[u.id],"debug",js::obj({{"prep",s.prep},{"ep",s.energy},{"slotX",s.slot.x},{"slotY",s.slot.y},{"hasSlot",s.hasSlot}}));}
  }
  js::Args units;for (const auto& entry:history) units.push_back(entry.second);
  auto out=js::obj({{"t",w.time},{"units",js::arr(std::move(units))}});
  if(debug){V packs=js::obj({});for(uint8_t team=0;team<2;++team){const auto& p=w.packs[team];if(!p.enabled)continue;
    V entry=js::obj({{"plan",astelia::planName(p.plan)},{"anchor",js::obj({{"x",p.anchor.x},{"y",p.anchor.y},{"ax",p.facing.x},{"ay",p.facing.y}})},{"formed",p.formed}});
    const auto features=astelia::bcFeatures(w,team,w.config->lookahead[team].plans);js::Args encoded;for(auto x:features)encoded.emplace_back(x);js::set(entry,"features",js::arr(std::move(encoded)));
    js::set(entry,"search",js::obj({{"hasChoice",p.search.hasChoice},{"score",p.search.score},{"last",p.search.last}}));js::set(packs,std::to_string(team),entry);}
    js::set(out,"debug",js::obj({{"packs",packs}}));}return out;
}
V fight(V request,astelia::WorkCounters& counts,uint64_t& fights) {
  try {
  auto config=std::make_shared<const astelia::Config>(astelia::configuration(request));
  auto w=astelia::World::create(config); ++fights;
  uint64_t tick=0; const bool trace=js::truth(js::get(request,"trace"));
  std::map<astelia::UnitId,V> history;
  const bool debug=js::truth(js::get(request,"debug"));
  const auto dump=[&](){std::cout<<js::stringify(js::obj({{"step",double(tick)},{"state",state(w,history,debug)}}))<<'\n';};
  if (trace) dump();
  while (!w.done()) {astelia::coreStep(w);++tick;if (trace) dump();}
  counts.branchUnitActions+=w.work->branchUnitActions;counts.branchProjectileSteps+=w.work->branchProjectileSteps;counts.branchSteps+=w.work->branchSteps;counts.forks+=w.work->forks;counts.searchCalls+=w.work->searchCalls;counts.inferenceCalls+=w.work->inferenceCalls;counts.candidateModels+=w.work->candidateModels;counts.artilleryRollouts+=w.work->artilleryRollouts;counts.artilleryPredictions+=w.work->artilleryPredictions;counts.artilleryCandidates+=w.work->artilleryCandidates;counts.predictionSteps+=w.work->predictionSteps;counts.predictionUnitSteps+=w.work->predictionUnitSteps;
  counts.outerSteps+=w.counters.outerSteps;counts.unitActions+=w.counters.unitActions;counts.projectileSteps+=w.counters.projectileSteps;
  return summary(w);
  } catch (const std::exception& e) { return js::obj({{"error",e.what()}}); }
}
} // namespace
int main(int argc,char** argv) {
  bool metrics=false;for (int i=1;i<argc;++i) {
    if (std::string(argv[i])=="--metrics") metrics=true;else {std::cerr<<"unknown argument\n";return 1;}
  }
  astelia::WorkCounters counts;uint64_t fights=0;
  std::string line;while (std::getline(std::cin,line)) {
    if (line.find_first_not_of(" \t\r\n")==std::string::npos) continue;
    try {
      V request=js::parse(line), result;
      if (request.tag==V::Heap && request.p->kind==js::Object::Array) {
        js::Args rows;for (auto r:request.p->items) rows.push_back(fight(r,counts,fights));result=js::arr(std::move(rows));
      } else result=fight(request,counts,fights);
      std::cout<<js::stringify(result)<<std::endl;
    } catch (const std::exception& e) {std::cout<<js::stringify(js::obj({{"error",e.what()}}))<<std::endl;}
    js::collect({},0);
  }
  if (metrics) std::cerr<<"{\"executed_fights\":"<<fights<<",\"executed_steps\":"<<counts.outerSteps
    <<",\"branch_steps\":"<<counts.branchSteps<<",\"forks\":"<<counts.forks<<",\"search_calls\":"<<counts.searchCalls<<",\"inference_calls\":"<<counts.inferenceCalls<<",\"candidate_models\":"<<counts.candidateModels<<",\"artillery_rollouts\":"<<counts.artilleryRollouts<<",\"artillery_predictions\":"<<counts.artilleryPredictions<<",\"artillery_candidates\":"<<counts.artilleryCandidates<<",\"prediction_steps\":"<<counts.predictionSteps<<",\"prediction_unit_steps\":"<<counts.predictionUnitSteps<<",\"branch_unit_actions\":"<<counts.branchUnitActions<<",\"branch_projectile_steps\":"<<counts.branchProjectileSteps<<",\"unit_actions\":"<<counts.unitActions<<",\"projectile_steps\":"<<counts.projectileSteps
    <<",\"cache_hits\":0,\"scope\":\"native_artillery_checkpoint\"}\n";
}
