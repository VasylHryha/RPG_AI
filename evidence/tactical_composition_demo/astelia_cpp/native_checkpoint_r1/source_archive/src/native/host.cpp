// JSON boundary only. The simulation modules never include the legacy value API.
#include "world.h"
#include "../js_value.h"
#include <set>
#include <map>

namespace {
using js::V;
void only(V value,std::initializer_list<const char*> allowed) {
  if (value.tag!=V::Heap || value.p->kind!=js::Object::Plain) throw std::invalid_argument("expected JSON object");
  std::set<std::string> names;for (auto name:allowed) names.insert(name);
  for (auto key:js::keys(value)) if (!names.count(js::str(key))) throw std::invalid_argument("unsupported core slice field: "+js::str(key));
}
double number(V o,const char* key,double fallback) {
  V v=js::get(o,key);if (v.tag==V::Undefined) return fallback;
  if (v.tag!=V::Number || !std::isfinite(v.n)) throw std::invalid_argument(std::string("invalid numeric field: ")+key);
  return v.n;
}
bool boolean(V o,const char* key,bool fallback) {
  V v=js::get(o,key);if (v.tag==V::Undefined) return fallback;
  if (v.tag!=V::Boolean) throw std::invalid_argument(std::string("invalid boolean field: ")+key);
  return bool(v.n);
}
astelia::Config configuration(V request) {
  only(request,{"mode","options","trace"});
  if (js::str(js::get(request,"mode"))!="alone") throw std::invalid_argument("core slice requires mode=alone");
  V o=js::get(request,"options");only(o,{"seed","dt","duration","width","height","army","scenario","swapSides","rules","abilities","sandboxAbilities","ai","shots","shotSpeed","windUp"});
  if (js::str(js::get(o,"scenario"))!="mirror") throw std::invalid_argument("core slice requires mirror scenario");
  V rules=js::get(o,"rules");if (rules.tag!=V::Undefined && js::str(rules)!="sandbox") throw std::invalid_argument("game rules not implemented in core slice");
  if (boolean(o,"abilities",false) || boolean(o,"sandboxAbilities",false) || boolean(o,"windUp",false)) throw std::invalid_argument("abilities/windup not implemented in core slice");
  V profiles=js::get(o,"ai");
  if (profiles.tag!=V::Heap || profiles.p->kind!=js::Object::Array || profiles.p->items.size()!=2)
    throw std::invalid_argument("core slice requires two explicit novice profiles");
  for (auto p:profiles.p->items) {only(p,{"level"});if (js::str(js::get(p,"level"))!="novice") throw std::invalid_argument("core slice requires novice profiles");}
  auto c=astelia::sandboxConfig();
  c.seed=number(o,"seed",c.seed);c.dt=number(o,"dt",c.dt);c.duration=number(o,"duration",c.duration);
  c.width=number(o,"width",c.width);c.height=number(o,"height",c.height);c.shotSpeed=number(o,"shotSpeed",c.shotSpeed);
  c.swapSides=boolean(o,"swapSides",false);
  V shots=js::get(o,"shots");if (shots.tag!=V::Undefined) {
    const auto s=js::str(shots);if (s!="aimed" && s!="homing") throw std::invalid_argument("unknown shot mode");c.aimedShots=s=="aimed";
  }
  V army=js::get(o,"army");if (army.tag!=V::Undefined) {
    only(army,{"melee","ranged","artillery"});size_t i=0;
    for (const char* role:{"melee","ranged","artillery"}) {
      const double n=number(army,role,0);
      if (n<0 || n>1000000 || n!=std::floor(n)) throw std::invalid_argument("invalid army count");c.army[i++]=uint32_t(n);
    }
  }
  if (!(c.shotSpeed>0)) throw std::invalid_argument("shot speed must be positive");
  return c;
}
V summary(const astelia::World& w) {
  const auto& s=w.stats;
  return js::obj({{"mode","alone"},{"melee",s.melee},{"ranged",s.ranged},{"artillery",s.artillery},
    {"total",s.melee+s.ranged+s.artillery},{"wasted",s.wasted},{"monsterDeaths",double(s.monsterDeaths)},
    {"hunterKills",double(s.hunterKills)},{"aliveSeconds",s.aliveSeconds},{"enemyDamage",s.enemyDamage},
    {"survivors",double(w.survivors(0))},{"enemySurvivors",double(w.survivors(1))},{"t",w.time}});
}
V state(const astelia::World& w,std::map<astelia::UnitId,V>& history) {
  for (const auto& u:w.units) if (u.id && (u.occupied || !history.count(u.id) || js::truth(js::get(history.at(u.id),"alive")))) {
    const auto* t=w.resolve(u.target);
    history[u.id]=js::obj({{"id",double(u.id)},{"team",double(u.team)},
      {"role",u.role==astelia::Role::Melee?"melee":u.role==astelia::Role::Ranged?"ranged":"artillery"},
      {"x",u.pos.x},{"y",u.pos.y},{"hp",u.hp},{"cd",u.cooldown},{"alive",u.alive},
      {"target",t?V(double(t->id)):V(nullptr)}});
  }
  js::Args units;for (const auto& entry:history) units.push_back(entry.second);
  return js::obj({{"t",w.time},{"units",js::arr(std::move(units))}});
}
V fight(V request,astelia::WorkCounters& counts,uint64_t& fights) {
  try {
  auto config=std::make_shared<const astelia::Config>(configuration(request));
  auto w=astelia::World::create(config); ++fights;
  uint64_t tick=0; const bool trace=js::truth(js::get(request,"trace"));
  std::map<astelia::UnitId,V> history;
  const auto dump=[&](){std::cout<<js::stringify(js::obj({{"step",double(tick)},{"state",state(w,history)}}))<<'\n';};
  if (trace) dump();
  while (!w.done()) {astelia::coreStep(w);++tick;if (trace) dump();}
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
    <<",\"branch_steps\":0,\"forks\":0,\"unit_actions\":"<<counts.unitActions<<",\"projectile_steps\":"<<counts.projectileSteps
    <<",\"cache_hits\":0,\"scope\":\"native_core_slice\"}\n";
}
