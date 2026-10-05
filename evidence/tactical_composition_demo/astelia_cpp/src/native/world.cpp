#include "world.h"
#include "formation.h"
#include <utility>

namespace astelia {
World::World(std::shared_ptr<const Config> c):config(std::move(c)),random(toUint32(config->seed)),dt(config->dt),duration(config->duration),brains(config->brains),forced(config->forcePlan),forcedTeam(config->forceTeam),hasForced(config->hasForcePlan) {}
World::~World()=default;
World::World(World&&) noexcept=default;
World& World::operator=(World&&) noexcept=default;
BranchPool& World::branches(){if(!branches_){ownedBranches_=std::make_unique<BranchPool>();branches_=ownedBranches_.get();}return *branches_;}

Config sandboxConfig() {
  Config c; c.width=1400; c.height=800;
  c.roles={RoleStats{300,70,8,18,30,.8}, RoleStats{90,62,6,190,14,1,0,420},
    RoleStats{70,48,7,330,26,3,90,0,1,45}, RoleStats{420,76,9,20,40,1},
    RoleStats{200,66,7,220,20,1.2,0,420}, RoleStats{763,120,9,666,24,0}};
  return c;
}
const char* roleName(Role r) {
  constexpr const char* names[]={"melee","ranged","artillery","hunter","archer","player"};
  return names[size_t(r)];
}
Config gameConfig() {
  Config c=sandboxConfig();c.rules=Rules::Game;c.shotSpeed=240;c.windUp=true;
  auto kind=[](const char* name,Role role,double hp,double speed,double radius,double damage,double reach,
      double windup,double cooldown,double energy,double regen,double cost,double protection,double acc,Dodge dodge) {
    Kind k;k.name=name;k.role=role;k.hp=hp;k.speed=speed;k.radius=radius;k.damage=damage;k.reach=reach;
    k.windup=windup;k.cooldown=cooldown;k.energy=energy;k.regen=regen;k.cost=cost;k.protection=protection;
    k.acc=acc;k.dodge=dodge;return k;
  };
  c.kinds={kind("brute",Role::Melee,258,40,16,19.5,64,.45,1.8,0,0,0,.2033,2.62,Dodge::None),
    kind("spitter",Role::Ranged,92,55,9,10.4,280,.55,1.4,168,22.3,6,.1524,2.62,Dodge::Kiter),
    kind("shaman",Role::Artillery,181,55,10,18,320,.7,1.2,324.8,34,10,.1547,4.48,Dodge::Storm),
    kind("warden",Role::Melee,258,40,16,19.5,64,.45,1.8,176.25,21.4,0,.2033,2.62,Dodge::None),
    kind("hound",Role::Melee,106,95,6,7.5,56,.2,.8,0,0,0,.0017,3.31,Dodge::None),
    kind("runner",Role::Melee,53,110,6,9,60,.25,1,0,0,0,.0009,3.31,Dodge::Skittish)};
  c.kinds[1].shot=240;c.kinds[2].lob=300;c.kinds[2].splash=40;c.kinds[3].block=true;
  for (size_t r=0;r<3;++r) {
    const auto& k=c.kinds[r];auto& s=c.roles[r];
    s.hp=k.hp;s.speed=k.speed;s.radius=k.radius;s.damage=k.damage;s.cooldown=k.cooldown;
    s.range=r==2?k.reach:k.reach-k.radius-12;
    if(r==1)s.shotSpeed=k.shot;
    if(r==2){s.minRange=0;s.splash=k.splash;s.flight=.8;}
  }
  c.skirmishKinds={1,4,0,2,5,3};return c;
}
UnitHot* World::resolve(UnitRef r) {
  if (r.slot>=units.size()) return nullptr;
  auto& u=units[r.slot]; return u.occupied && u.generation==r.generation?&u:nullptr;
}
const UnitHot* World::resolve(UnitRef r) const {
  if (r.slot>=units.size()) return nullptr;
  const auto& u=units[r.slot]; return u.occupied && u.generation==r.generation?&u:nullptr;
}
UnitRef World::add(uint8_t team,Role role,Vec2 pos,uint32_t kind) {
  if (team>1 || size_t(role)>=config->roles.size() || nextId==0) throw std::invalid_argument("invalid unit identity or role");
  if(role==Role::Player&&controllers[team]&&config->controllers[team].name!="passthrough")
    throw std::invalid_argument("S2 external controllers do not support the special player body");
  uint32_t slot; uint32_t generation=1;
  if (free_.empty()) {
    if (units.size()>=invalidSlot) throw std::length_error("unit slot limit");
    slot=uint32_t(units.size()); units.emplace_back(); state.emplace_back();tactical.emplace_back();
  } else { slot=free_.back(); free_.pop_back(); generation=units[slot].generation+1;
    if (!generation) throw std::overflow_error("unit generation exhausted"); }
  auto& u=units[slot]; u=UnitHot{}; u.generation=generation; u.id=nextId++; u.pos=pos;
  u.team=team; u.role=role; u.alive=u.occupied=true;
  const auto& r=config->roles[size_t(role)];
  u.hp=u.maxhp=r.hp; u.speed=r.speed; u.radius=r.radius; u.range=r.range; u.damage=r.damage;
  auto& s=state[slot]; s=UnitState{}; s.slot=pos; s.cooldownMax=r.cooldown; s.baseSpeed=r.speed;
  tactical[slot]=TacticalState{};
  for(auto& p:packs){p.pending.resize(units.size());p.pending[slot]=0;}
  s.minRange=r.minRange; s.shotSpeed=r.shotSpeed; s.lobSpeed=r.flight; s.splash=r.splash;
  s.strafe=u.id%2?1:-1;
  if (config->rules==Rules::Game && role==Role::Player) {
    s.energy=s.energyMax=689.5;s.energyRegen=42.1;s.protection=.0122;
    if(freePlayers.empty()){s.player=uint32_t(players.size());players.emplace_back();}
    else{s.player=freePlayers.back();freePlayers.pop_back();players[s.player]=PlayerState{};}
  } else if(config->rules==Rules::Game) {
    if(kind==invalidSlot && size_t(role)<3)kind=uint32_t(role);
    if(kind!=invalidSlot) {
      const auto& k=config->kinds.at(kind);if(k.role!=role)throw std::invalid_argument("kind role mismatch");
      s.kind=kind;u.hp=u.maxhp=k.hp;u.radius=k.radius;u.damage=k.damage;s.baseSpeed=k.speed;
      u.range=role==Role::Artillery?k.reach:k.reach-k.radius-12;
      s.cooldownMax=k.cooldown;s.windup=k.windup;s.energy=s.energyMax=k.energy;s.energyRegen=k.regen;
      s.cost=k.cost;s.protection=k.protection;s.dodge=k.dodge;s.block=k.block;
      s.standoff=role==Role::Ranged||role==Role::Artillery?std::min(.6*std::max(150.0,.9*k.reach),.8*k.reach):0;
      s.minRange=k.minRange;s.shotSpeed=k.shot;s.lobSpeed=k.lob;s.splash=k.splash;
      s.launch=k.launch>0?k.launch:clamp(1+.2*(k.acc-1),1,8);
      s.timeRate=timeReference>0?std::min(4.0,(k.acc>0?k.acc:timeReference)/timeReference):1;
      u.speed=k.speed*s.timeRate;
    }
  }
  if(config->abilities && role!=Role::Player) {
    if(freeAbilities.empty()){s.ability=uint32_t(abilities.size());abilities.emplace_back();}
    else{s.ability=freeAbilities.back();freeAbilities.pop_back();abilities[s.ability]=AbilityState{};}
  }
  validateBody(u);
  if(!(u.hp>0)||!std::isfinite(u.hp)||!std::isfinite(u.speed)||u.radius*2>std::min(config->width,config->height))
    throw std::invalid_argument("invalid unit stats");
  active.push_back(slot);
  ++membershipVersion;
  teams[team].push_back(slot);
  if (liveGrid.ready()) liveGrid.insert(slot,u);
  return {slot,generation};
}
void World::rebuildTeams() {
  teams[0].clear(); teams[1].clear();
  for (auto i:active) if (units[i].alive) teams[units[i].team].push_back(i);
  foesVersion_={UINT64_MAX,UINT64_MAX};ratesVersion={UINT64_MAX,UINT64_MAX};
}
const std::vector<uint32_t>& World::foes(uint8_t team) const {
  if(foesVersion_[team]==membershipVersion&&foesTime_[team]==time)return foes_[team];
  auto& out=foes_[team];out.clear();bool player=false;
  for(auto i:teams[team])if(units[i].alive&&units[i].role==Role::Player){player=true;break;}
  const bool perception=config->rules==Rules::Game&&config->perception&&!player;
  for(auto i:teams[1-team])if(units[i].alive){
    bool seen=!perception;
    if(perception)for(auto j:teams[team])if(units[j].alive&&squared(units[j].pos-units[i].pos)<=768*768){seen=true;break;}
    if(seen)out.push_back(i);
  }
  foesVersion_[team]=membershipVersion;foesTime_[team]=time;return out;
}
uint32_t World::survivors(uint8_t team) const {
  uint32_t n=0; for (auto i:active) if (units[i].alive && units[i].team==team) ++n; return n;
}
bool World::done() const {
  if(skirmishActive)return time>=duration||!survivors(1)||(!survivors(0)&&skirmishLeft==0);
  return time>=duration||!survivors(0)||(config->mirror&&!survivors(1));
}
World World::create(std::shared_ptr<const Config> c) {
  if(!c->controllers[0].name.empty()||!c->controllers[1].name.empty()){
    auto adjusted=std::make_shared<Config>(*c);
    for(uint8_t side=0;side<2;++side)if(!c->controllers[side].name.empty()&&c->controllers[side].name!="passthrough")adjusted->skills[side].abilities=AbilityPolicy::Auto;
    c=std::move(adjusted);
  }
  if (!(c->dt>0) || !std::isfinite(c->dt) || !(c->duration>=0) || !std::isfinite(c->duration) ||
      !(c->width>0) || !(c->height>0) || !std::isfinite(c->width) || !std::isfinite(c->height) || !std::isfinite(c->seed) ||
      c->width>1e9 || c->height>1e9 || c->duration/c->dt>1e7)
    throw std::invalid_argument("invalid world configuration");
  World w(c);
  for(uint8_t side=0;side<2;++side)if(!c->controllers[side].name.empty())w.controllers[side]=makeController(c->controllers[side],c->seed,side);
  w.spawnRandom=Rng(toUint32(c->seed*7919));
  constexpr std::array<Vec2,3> zones{Vec2{240,60},Vec2{150,90},Vec2{80,60}};
  constexpr std::array<double,3> band{120,150,120};
  struct Placement{Role role;uint32_t kind;Vec2 pos;};std::vector<Placement> layout;
  const auto place=[&](Role role,uint32_t kind,uint32_t count){
    if(size_t(role)>2)throw std::invalid_argument("army layout requires formation roles");
    for(uint32_t j=0;j<count;++j)layout.push_back({role,kind,{zones[size_t(role)].x+w.random()*zones[size_t(role)].y,
      c->height/2-band[size_t(role)]+w.random()*2*band[size_t(role)]}});
  };
  if(c->hasCustomArmy)for(const auto& a:c->customArmy)place(a.role,a.kind,a.count);
  else for(size_t r=0;r<3;++r)place(Role(r),invalidSlot,c->army[r]);
  if(c->hasCarried) {
    auto left=layout;
    for(const auto& carry:c->carried){
      auto p=std::find_if(left.begin(),left.end(),[&](const Placement& p){return p.role==carry.role&&p.kind==carry.kind;});
      const auto ref=w.add(0,carry.role,p==left.end()?Vec2{200,c->height/2}:p->pos,carry.kind);
      w.units[ref.slot].hp=carry.hp;if(p!=left.end())left.erase(p);
    }
  } else if(c->scenario==Scenario::Skirmish) {
    if(c->rules!=Rules::Game||c->skirmishKinds.empty()||!c->skirmishMaxAlive)throw std::invalid_argument("invalid skirmish configuration");
    w.skirmishActive=true;if(c->temporal)w.timeReference=6.62;
    w.skirmishLeft=c->skirmishCount;
    while(w.skirmishLeft && w.survivors(0)<c->skirmishMaxAlive)w.spawnSkirmish();
    w.add(1,Role::Player,{c->width-260,c->height/2});
  } else for(const auto& p:layout)w.add(0,p.role,p.pos,p.kind);
  if(c->scenario==Scenario::Mirror && c->hasEnemyArmy){
    const double k=std::max(1.0,(double(c->enemyArmy[0])+c->enemyArmy[1]+c->enemyArmy[2])/50);
    for(size_t r=0;r<3;++r){const double tall=std::min(c->height-40,band[r]*2*std::sqrt(k));
      for(uint32_t j=0;j<c->enemyArmy[r];++j)w.add(1,Role(r),{c->width-(zones[r].x+w.random()*zones[r].y*k),c->height/2-tall/2+w.random()*tall});}
  } else if(c->scenario==Scenario::Mirror)for(size_t j=0;j<layout.size();++j){
    const auto& p=layout[j];const auto ref=w.add(1,p.role,{c->width-p.pos.x,p.pos.y},p.kind);
    w.state[ref.slot].strafe=-(j<w.active.size() && w.units[w.active[j]].team==0?w.state[w.active[j]].strafe:1);
  } else if(c->scenario==Scenario::Hunters){
    for(uint32_t j=0;j<c->hunterMelee;++j)w.spawnHunter(Role::Hunter);
    for(uint32_t j=0;j<c->hunterArchers;++j)w.spawnHunter(Role::Archer);
  }
  if (c->swapSides) for (auto i:w.active) {
    auto& u=w.units[i]; u.pos.x=c->width-u.pos.x; w.state[i].slot=u.pos; w.state[i].strafe=-w.state[i].strafe;
  }
  for(uint8_t team=0;team<2;++team) {
    auto& p=w.packs[team];p.enabled=c->brains[team]!=Brain::Alone&&(team==0||c->scenario==Scenario::Mirror);
    if(w.controllers[team]&&c->controllers[team].name!="passthrough")p.enabled=false;
    p.base=p.formation=c->formations[team];p.anchor={team==0?240:c->width-240,c->height/2};p.facing={team==0?1.0:-1.0,0};
    if(c->swapSides){p.anchor.x=c->width-p.anchor.x;p.facing.x=-p.facing.x;}
  }
  for (auto i:w.active) {
    validateBody(w.units[i]);
    if (w.units[i].radius*2>std::min(c->width,c->height)) throw std::invalid_argument("body larger than arena");
  }
  w.rebuildTeams();w.liveGrid.build(w.units,w.active,c->width,c->height,40);return w;
}
UnitRef World::spawnHunter(Role role) {
  return add(1,role,{config->width-60-random()*80,80+random()*(config->height-160)});
}
UnitRef World::spawnSkirmish() {
  if(!skirmishLeft || config->skirmishKinds.empty())throw std::logic_error("invalid skirmish spawn");
  const uint32_t kind=config->skirmishKinds[size_t(spawnRandom()*config->skirmishKinds.size())];
  const auto role=config->kinds.at(kind).role;
  const Vec2 p{90+spawnRandom()*160,120+spawnRandom()*(config->height-240)};
  const auto ref=add(0,role,p,kind);--skirmishLeft;return ref;
}
void World::move(uint32_t slot,Vec2 goal,double dt,double stop) {
  if (!std::isfinite(goal.x) || !std::isfinite(goal.y) || !std::isfinite(dt) || dt<0 || !std::isfinite(stop) || stop<0)
    throw std::invalid_argument("invalid movement request");
  auto& u=units.at(slot); const Vec2 delta=goal-u.pos; const double l=length(delta);
  if (l<=stop+.5) return;
  if (!liveGrid.ready()) liveGrid.build(units,active,config->width,config->height,40);
  u.pos=u.pos+delta*(std::min(u.speed*dt,l-stop)/l); liveGrid.moved(slot,u.pos);
}
double World::damage(UnitRef source,UnitRef target,double amount,bool barrage) {
  auto* src=resolve(source); auto* dst=resolve(target);
  if (!src || !dst || !dst->alive) return 0;
  if (!std::isfinite(amount) || amount<0) throw std::logic_error("invalid damage");
  if (config->rules==Rules::Game) {
    const auto& s=state[target.slot];amount*=1-(burnTick?0:s.protection);
    if(s.block&&s.guardUntil>time){const auto& k=config->kinds.at(s.kind);const double d=std::atan2(src->pos.y-dst->pos.y,src->pos.x-dst->pos.x)-s.guardDirection;
      if(std::abs(std::atan2(std::sin(d),std::cos(d)))<=k.blockHalfArc)amount*=k.blockMultiplier;}
    amount=std::floor(amount);
  }
  if(!melee(src->role)) {
    state[target.slot].lastShotHit=time;const auto a=state[target.slot].ability;
    if(a!=invalidSlot&&abilities[a].shieldUntil>time){stats.abilities[dst->team][size_t(Ability::Shield)].blocked+=amount*.8;amount*=.2;}
  }
  const double dealt=std::min(amount,dst->hp); dst->hp-=amount;
  state[source.slot].damageDealt+=dealt;state[target.slot].damageTaken+=dealt;
  const size_t kind=melee(src->role)?(amount>src->damage*1.2?1:0):src->role==Role::Artillery?(barrage?3:2):(amount>src->damage*1.2?5:4);
  stats.bySource[kind]+=dealt;if(dst->team==0&&src->team==1)stats.takenBy[kind]+=dealt;
  if(kind==1||kind==3||kind==5)stats.abilities[src->team][size_t(kind==1?Ability::Charge:kind==3?Ability::Barrage:Ability::Aimed)].damage+=dealt;
  hitLog.push_back({time,dealt,src->team,dst->team});
  lastHit=time;
  if (melee(src->role)) { state[target.slot].meleeAttacker=source; state[target.slot].meleeAt=time; }
  if (src->team==0) {
    if (src->role==Role::Melee) stats.melee+=dealt;
    else if (src->role==Role::Ranged) stats.ranged+=dealt;
    else if (src->role==Role::Artillery) stats.artillery+=dealt;
    state[source.slot].dealt+=dealt;
  } else stats.enemyDamage+=dealt;
  if(src->role==Role::Player&&dealt>0&&!burnTick) {
    size_t n=0;for(const auto& d:dots)if(d.target==target&&d.until>time)++n;
    if(n<5)dots.push_back({source,target,.2*dealt/4,time+4,0});
  }
  if (dst->hp<=0) {dst->alive=false;++membershipVersion;liveGrid.remove(target.slot);if (dst->team==1) {
    ++stats.hunterKills;if(config->scenario==Scenario::Hunters)spawnQueue.push_back({time+config->respawn,dst->role});
    }else {++stats.monsterDeaths;note("lost "+std::string(roleName(dst->role))+" #"+std::to_string(dst->id)+" to "+roleName(src->role));}}
  return dealt;
}
void World::note(std::string text,uint8_t team){if(events.size()==80)events.erase(events.begin());events.push_back({time,team,std::move(text)});}
void World::retain(UnitRef ref) { if (resolve(ref)) retained_[ref.slot]=1; }
void World::reclaim() {
  retained_.assign(units.size(),0);
  for (auto i:active) if (units[i].alive) {
    retained_[i]=1; retain(units[i].target); retain(state[i].meleeAttacker);
    const auto& s=state[i];
    const auto& t=tactical[i];retain(t.assigned);retain(t.fireOrder);retain(t.squadFocus);retain(t.order.target);
    if(s.ability!=invalidSlot){const auto& a=abilities[s.ability];retain(a.chargeTarget);retain(a.aimTarget);}
    if(s.player!=invalidSlot){const auto& p=players[s.player];retain(p.manualTarget);for(const auto& l:p.limbs)retain(l.target);}
  }
  for (const auto& s:shots) {retain(s.source);retain(s.target);for (auto h:s.hitSet) retain(h);}
  for (const auto& s:shells) retain(s.source);
  for (const auto& d:dots) {retain(d.source);retain(d.target);}
  for(const auto& p:packs){retain(p.focus);retain(p.surroundTarget);for(const auto& wing:p.wings)retain(wing.unit);for(const auto& q:p.artilleryQueue)retain(q.gun);for(auto ref:p.cutOff)retain(ref);}
  for (auto i:active) if (!units[i].alive) liveGrid.remove(i);
  active.erase(std::remove_if(active.begin(),active.end(),[&](auto i){return !units[i].alive;}),active.end());
  for (uint32_t i=0;i<units.size();++i) if (units[i].occupied && !retained_[i]) {
    auto& s=state[i];if(s.ability!=invalidSlot){abilities[s.ability]=AbilityState{};freeAbilities.push_back(s.ability);s.ability=invalidSlot;}
    if(s.player!=invalidSlot){players[s.player]=PlayerState{};freePlayers.push_back(s.player);s.player=invalidSlot;}
    units[i].occupied=false;free_.push_back(i);
  }
  rebuildTeams();
}
void World::copyAuthorityFrom(const World& p) {
  decisionTrace.clear();
  for(uint8_t side=0;side<2;++side){auto cloned=p.controllers[side]?p.controllers[side]->clone():nullptr;
    if(p.controllers[side]&&!cloned)throw std::logic_error("controller clone returned null");
    controllers[side]=std::move(cloned);observations[side]={};}
  config=p.config;dt=p.dt;duration=p.duration;brains=p.brains;forced=p.forced;forcedTeam=p.forcedTeam;hasForced=p.hasForced;thinkTeams=0;work=p.work;branches_=p.branches_;
  state=p.state;tactical=p.tactical;packs=p.packs; active=p.active; free_=p.free_;
  shots=p.shots; shells=p.shells; fields=p.fields; dots=p.dots; hitLog=p.hitLog;
  abilities=p.abilities;players=p.players;freeAbilities=p.freeAbilities;freePlayers=p.freePlayers;spawnQueue=p.spawnQueue;
  spawnRandom=p.spawnRandom;skirmishLeft=p.skirmishLeft;timeReference=p.timeReference;lastHit=p.lastHit;nextShot=p.nextShot;burnTick=false;
  skirmishActive=p.skirmishActive;orderEvents=p.orderEvents;ratesTime={-1,-1};ratesVersion={UINT64_MAX,UINT64_MAX};
  stats=Stats{}; random=p.random; time=p.time; nextId=p.nextId; branch=true;
  counters=WorkCounters{}; meleeHits.clear(); order.clear(); pushes.clear();
  events.clear();bcData.clear();
  membershipVersion=p.membershipVersion;foesVersion_={UINT64_MAX,UINT64_MAX};foesTime_={-1,-1};
  for(auto& f:foes_)f.clear();teams=p.teams;
}
void World::copyFrom(const World& p) {
  units=p.units;copyAuthorityFrom(p);
  // Derived indexes are rebuilt from copied authority, never shared.
  rebuildTeams(); liveGrid.build(units,active,config->width,config->height,40);
}
BranchPool::Lease BranchPool::fork(const World& parent) {
  size_t i=0; while (i<leased_.size() && leased_[i]) ++i;
  if (i==leased_.size()) {worlds_.push_back(std::make_unique<World>(parent.config));leased_.push_back(false);}
  // Do not mark a failed copy leased. unique_ptr pointees survive pool growth.
  worlds_[i]->copyFrom(parent);if(parent.work)++parent.work->forks; leased_[i]=true; return Lease(this,i);
}
} // namespace astelia
