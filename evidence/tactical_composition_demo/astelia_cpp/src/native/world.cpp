#include "world.h"
#include <utility>

namespace astelia {
Config sandboxConfig() {
  Config c; c.width=1400; c.height=800;
  c.roles={RoleStats{300,70,8,18,30,.8}, RoleStats{90,62,6,190,14,1,0,420},
    RoleStats{70,48,7,330,26,3,90,0,1,45}, RoleStats{420,76,9,20,40,1},
    RoleStats{200,66,7,220,20,1.2,0,420}, RoleStats{}};
  return c;
}
UnitHot* World::resolve(UnitRef r) {
  if (r.slot>=units.size()) return nullptr;
  auto& u=units[r.slot]; return u.occupied && u.generation==r.generation?&u:nullptr;
}
const UnitHot* World::resolve(UnitRef r) const {
  if (r.slot>=units.size()) return nullptr;
  const auto& u=units[r.slot]; return u.occupied && u.generation==r.generation?&u:nullptr;
}
UnitRef World::add(uint8_t team,Role role,Vec2 pos) {
  if (team>1 || size_t(role)>=config->roles.size() || nextId==0) throw std::invalid_argument("invalid unit identity or role");
  uint32_t slot; uint32_t generation=1;
  if (free_.empty()) {
    if (units.size()>=invalidSlot) throw std::length_error("unit slot limit");
    slot=uint32_t(units.size()); units.emplace_back(); state.emplace_back();
  } else { slot=free_.back(); free_.pop_back(); generation=units[slot].generation+1;
    if (!generation) throw std::overflow_error("unit generation exhausted"); }
  auto& u=units[slot]; u=UnitHot{}; u.generation=generation; u.id=nextId++; u.pos=pos;
  u.team=team; u.role=role; u.alive=u.occupied=true;
  const auto& r=config->roles[size_t(role)];
  u.hp=u.maxhp=r.hp; u.speed=r.speed; u.radius=r.radius; u.range=r.range; u.damage=r.damage;
  auto& s=state[slot]; s=UnitState{}; s.slot=pos; s.cooldownMax=r.cooldown; s.baseSpeed=r.speed;
  s.minRange=r.minRange; s.shotSpeed=r.shotSpeed; s.lobSpeed=r.flight; s.splash=r.splash;
  s.strafe=u.id%2?1:-1;
  active.push_back(slot);
  if (liveGrid.ready()) liveGrid.insert(slot,u);
  return {slot,generation};
}
void World::rebuildTeams() {
  teams[0].clear(); teams[1].clear();
  for (auto i:active) if (units[i].alive) teams[units[i].team].push_back(i);
}
uint32_t World::survivors(uint8_t team) const {
  uint32_t n=0; for (auto i:active) if (units[i].alive && units[i].team==team) ++n; return n;
}
bool World::done() const { return time>=config->duration || !survivors(0) || (config->mirror && !survivors(1)); }
World World::create(std::shared_ptr<const Config> c) {
  if (!(c->dt>0) || !std::isfinite(c->dt) || !(c->duration>=0) || !std::isfinite(c->duration) ||
      !(c->width>0) || !(c->height>0) || !std::isfinite(c->width) || !std::isfinite(c->height) || !std::isfinite(c->seed) ||
      c->width>1e9 || c->height>1e9 || c->duration/c->dt>1e7)
    throw std::invalid_argument("invalid world configuration");
  if (!c->mirror || c->rules!=Rules::Sandbox) throw std::invalid_argument("core slice supports sandbox mirror only");
  World w(c);
  constexpr std::array<Vec2,3> zones{Vec2{240,60},Vec2{150,90},Vec2{80,60}};
  constexpr std::array<double,3> band{120,150,120};
  for (size_t r=0;r<3;++r) for (uint32_t j=0;j<c->army[r];++j)
    w.add(0,Role(r),{zones[r].x+w.random()*zones[r].y,c->height/2-band[r]+w.random()*2*band[r]});
  const size_t count=w.active.size();
  for (size_t j=0;j<count;++j) {
    const UnitHot u=w.units[w.active[j]];
    auto ref=w.add(1,u.role,{c->width-u.pos.x,u.pos.y}); w.state[ref.slot].strafe=-w.state[w.active[j]].strafe;
  }
  if (c->swapSides) for (auto i:w.active) {
    auto& u=w.units[i]; u.pos.x=c->width-u.pos.x; w.state[i].slot=u.pos; w.state[i].strafe=-w.state[i].strafe;
  }
  for (auto i:w.active) {
    validateBody(w.units[i]);
    if (w.units[i].radius*2>std::min(c->width,c->height)) throw std::invalid_argument("body larger than arena");
  }
  w.rebuildTeams();w.liveGrid.build(w.units,w.active,c->width,c->height,40);return w;
}
void World::move(uint32_t slot,Vec2 goal,double dt,double stop) {
  if (!std::isfinite(goal.x) || !std::isfinite(goal.y) || !std::isfinite(dt) || dt<0 || !std::isfinite(stop) || stop<0)
    throw std::invalid_argument("invalid movement request");
  auto& u=units.at(slot); const Vec2 delta=goal-u.pos; const double l=length(delta);
  if (l<=stop+.5) return;
  if (!liveGrid.ready()) liveGrid.build(units,active,config->width,config->height,40);
  u.pos=u.pos+delta*(std::min(u.speed*dt,l-stop)/l); liveGrid.moved(slot,u.pos);
}
double World::damage(UnitRef source,UnitRef target,double amount) {
  auto* src=resolve(source); auto* dst=resolve(target);
  if (!src || !dst || !dst->alive) return 0;
  if (!std::isfinite(amount) || amount<0) throw std::logic_error("invalid damage");
  if (config->rules==Rules::Game) amount=std::floor(amount*(1-state[target.slot].protection));
  const double dealt=std::min(amount,dst->hp); dst->hp-=amount;
  hitLog.push_back({time,dealt,src->team,dst->team});
  if (melee(src->role)) { state[target.slot].meleeAttacker=source; state[target.slot].meleeAt=time; }
  if (src->team==0) {
    if (src->role==Role::Melee) stats.melee+=dealt;
    else if (src->role==Role::Ranged) stats.ranged+=dealt;
    else if (src->role==Role::Artillery) stats.artillery+=dealt;
    state[source.slot].dealt+=dealt;
  } else stats.enemyDamage+=dealt;
  if (dst->hp<=0) {dst->alive=false;liveGrid.remove(target.slot);if (dst->team==1) ++stats.hunterKills;else ++stats.monsterDeaths;}
  return dealt;
}
void World::retain(UnitRef ref) { if (resolve(ref)) retained_[ref.slot]=1; }
void World::reclaim() {
  retained_.assign(units.size(),0);
  for (auto i:active) if (units[i].alive) {
    retained_[i]=1; retain(units[i].target); retain(state[i].meleeAttacker);
  }
  for (const auto& s:shots) {retain(s.source);retain(s.target);for (auto h:s.hitSet) retain(h);}
  for (const auto& s:shells) retain(s.source);
  for (const auto& d:dots) {retain(d.source);retain(d.target);}
  for (auto i:active) if (!units[i].alive) liveGrid.remove(i);
  active.erase(std::remove_if(active.begin(),active.end(),[&](auto i){return !units[i].alive;}),active.end());
  for (uint32_t i=0;i<units.size();++i) if (units[i].occupied && !retained_[i]) {units[i].occupied=false;free_.push_back(i);}
}
void World::copyFrom(const World& p) {
  config=p.config; units=p.units; state=p.state; active=p.active; free_=p.free_;
  shots=p.shots; shells=p.shells; fields=p.fields; dots=p.dots; hitLog=p.hitLog;
  stats=p.stats; random=p.random; time=p.time; nextId=p.nextId; branch=true;
  counters=WorkCounters{}; meleeHits.clear(); order.clear(); pushes.clear();
  // Derived indexes are rebuilt from copied authority, never shared.
  rebuildTeams(); liveGrid.build(units,active,config->width,config->height,40);
}
BranchPool::Lease BranchPool::fork(const World& parent) {
  size_t i=0; while (i<leased_.size() && leased_[i]) ++i;
  if (i==leased_.size()) {worlds_.push_back(std::make_unique<World>(parent.config));leased_.push_back(false);}
  // Do not mark a failed copy leased. unique_ptr pointees survive pool growth.
  worlds_[i]->copyFrom(parent); leased_[i]=true; return Lease(this,i);
}
} // namespace astelia
