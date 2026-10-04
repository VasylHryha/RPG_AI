#include "world.h"
#include "formation.h"
#include "search.h"

namespace astelia {
namespace {
void actNovice(World& w,uint32_t i,double dt) {
  auto& u=w.units[i]; auto& s=w.state[i]; const auto& d=s.decision;
  const auto* t=w.resolve(u.target);
  if(d.release==Release::Player){playerBrain(w,i,dt);return;}
  // Melee and free artillery use pre-walk reach, direct fire uses post-walk reach.
  double before=t?(melee(u.role)?gap(u,*t):distance(u.pos,t->pos)):INFINITY;
  if (d.move) w.move(i,d.goal,dt*d.multiplier,d.stop);
  if(d.post&&t)before=melee(u.role)?gap(u,*t):distance(u.pos,t->pos);
  if (!t) return;
  auto* ability=s.ability==invalidSlot?nullptr:&w.abilities[s.ability];
  if(d.release==Release::Melee) {
    if(w.config->rules==Rules::Game){if(prepared(w,i)){released(w,i);if(before<=u.range){
      w.meleeHits.push_back({w.reference(i),u.target,ability&&ability->chargeBonus?1.5:1});if(ability)ability->chargeBonus=false;}}}
    else if(before<=u.range&&u.cooldown<=0&&!(ability&&ability->shieldUntil>w.time)){
      u.cooldown=s.cooldownMax;w.meleeHits.push_back({w.reference(i),u.target,ability&&ability->chargeBonus?1.5:1});if(ability)ability->chargeBonus=false;}
  } else if((d.release==Release::Direct||d.release==Release::DodgeFire)&&prepared(w,i)&&gap(u,*t)<=u.range&&!w.tactical[i].fireHold&&aimClear(w,i,u.target)) {
    released(w,i);fireShot(w,i,u.target);
  } else if(d.release==Release::Artillery&&prepared(w,i)) {
    if(w.tactical[i].reservedUntil>w.time)return;
    if(w.packs[u.team].enabled&&w.config->skills[u.team].artyPlan&&w.config->rules==Rules::Sandbox)return;
    if(w.config->rules==Rules::Game){released(w,i);if(before<=u.range&&before>=s.minRange){
      const auto& sk=w.config->skills[u.team];const auto& ts=w.state[u.target.slot];
      const bool steady=ts.longSpeed>30&&length(ts.longVelocity)/ts.longSpeed>.8;
      const double fl=distance(u.pos,t->pos)/((s.lobSpeed>0?s.lobSpeed:300)*s.launch);
      fireShellAt(w,i,t->pos+(sk.lobLead||(sk.adaptiveLobLead&&steady)?ts.longVelocity*fl:Vec2{}));}}
    else if(before<=u.range&&before>=s.minRange){released(w,i);fireShellAt(w,i,t->pos+leadVelocity(w,u.target,u.team)*w.config->roles[2].flight);}
  }
}
void shots(World& w,double dt) {
  w.shotGrid.build(w.units,w.active,w.config->width,w.config->height,64);
  for (auto& s:w.shots) {
    ++w.counters.projectileSteps;
    const auto* src=w.resolve(s.source);const auto* target=w.resolve(s.target);
    if (!src) throw std::logic_error("missing shot source");
    const auto settle=[&](bool hitTarget){s.done=true;addPending(w,s.source,s.target,-s.pending);
      auto& p=w.packs[src->team];if(p.enabled&&s.aimed&&s.dodgeable)p.hitRate=p.hitRate*.97+(hitTarget?.03:0);};
    if (s.aimed) {
      const double step=std::min(s.speed*dt,s.left); const Vec2 end=s.pos+s.direction*step;
      UnitRef hit;double ht=INFINITY; const double pad=w.shotGrid.maximumRadius();
      w.shotGrid.query({std::min(s.pos.x,end.x)-pad,std::min(s.pos.y,end.y)-pad},
        {std::max(s.pos.x,end.x)+pad,std::max(s.pos.y,end.y)+pad},[&](uint32_t i) {
          const auto& u=w.units[i];const UnitRef r=w.reference(i);
          if (!u.alive || r==s.source || std::find(s.hitSet.begin(),s.hitSet.end(),r)!=s.hitSet.end()) return;
          double t; if (!segmentParameter(s.pos,s.direction,step,u,t)) return;
          if (t<ht || (hit && t==ht && u.id<w.units[hit.slot].id)) {hit=r;ht=t;}
        });
      if (hit) {
        if(w.units[hit.slot].team!=src->team&&s.pierce>0){s.hitSet.push_back(hit);--s.pierce;w.damage(s.source,hit,s.damage);
          s.pos=end;s.left-=step;if(s.left<=0)settle(false);continue;}
        if (w.units[hit.slot].team!=src->team) w.damage(s.source,hit,s.damage);
        else {if(src->team==0)w.stats.wasted+=s.damage;if(w.config->rules==Rules::Game)w.damage(s.source,hit,s.damage);}
        settle(hit==s.target);
      } else {
        s.pos=end;s.left-=step;
        if (s.left<=0) {settle(false);if (src->team==0) w.stats.wasted+=s.damage;}
      }
    } else {
      if (!target) {settle(false);continue;}
      const Vec2 delta=target->pos-s.pos;const double l=length(delta),step=s.speed*dt;
      UnitRef blocker=lineBlocker(w.units,w.shotGrid,s.pos,target->pos,target->radius,s.source,s.target);
      if (blocker && distance(w.units[blocker.slot].pos,s.pos)<=step+w.units[blocker.slot].radius) {
        if (w.units[blocker.slot].team!=src->team) w.damage(s.source,blocker,s.damage);
        else if (src->team==0) w.stats.wasted+=s.damage;
        settle(false);
      } else if (l<=step+target->radius) {
        if (target->alive) w.damage(s.source,s.target,s.damage);else if (src->team==0) w.stats.wasted+=s.damage;
        settle(true);
      } else s.pos=s.pos+delta*(step/l);
    }
  }
  w.shots.erase(std::remove_if(w.shots.begin(),w.shots.end(),[](const Shot& s){return s.done;}),w.shots.end());
}
} // namespace
void coreStep(World& w) {
  if (w.branch){++w.counters.branchSteps;if(w.work)++w.work->branchSteps;}else ++w.counters.outerSteps;
  const double dt=w.dt,nextTime=w.time+dt;
  if (!std::isfinite(nextTime) || nextTime<=w.time) throw std::overflow_error("step cannot advance finite time");
  w.time=nextTime;
  for (auto i:w.active) {
    auto& u=w.units[i];auto& s=w.state[i];const double local=dt*s.timeRate;
    if (u.cooldown>0) u.cooldown-=w.config->rules==Rules::Game?local:dt;
    else if(w.config->rules==Rules::Sandbox&&w.config->windUp&&windup(w,i)>0)s.prep+=dt;
    if(s.energyRegen>0)s.energy=std::min(s.energyMax,s.energy+s.energyRegen*local);
    s.previous=u.pos;s.stepTime=w.time;
    if(w.config->abilities){double mul=1;
      if(s.ability!=invalidSlot&&w.abilities[s.ability].shieldUntil>w.time)mul=.5;
      for(const auto& f:w.fields)if(f.from<=w.time&&f.until>w.time&&f.team!=u.team&&distance(u.pos,f.pos)<=f.radius){mul*=.5;break;}
      u.speed=s.baseSpeed*s.timeRate*mul;
    }
    if(!s.rolledShots.empty())s.rolledShots.erase(std::remove_if(s.rolledShots.begin(),s.rolledShots.end(),[&](uint64_t id){
      return std::none_of(w.shots.begin(),w.shots.end(),[&](const Shot& shot){return shot.ordinal==id;});}),s.rolledShots.end());
  }
  w.fields.erase(std::remove_if(w.fields.begin(),w.fields.end(),[&](const Field& f){return f.until<=w.time;}),w.fields.end());
  w.rebuildTeams();w.liveGrid.build(w.units,w.active,w.config->width,w.config->height,40);
  const uint32_t packTick=toUint32(std::floor(w.time/dt+.5));
  Rng packRandom(toUint32(w.config->seed*2654435761.0)^toUint32(double(packTick)*40503));packRandom();packRandom();
  const std::array<uint8_t,2> packOrder=packRandom()<.5?std::array<uint8_t,2>{0,1}:std::array<uint8_t,2>{1,0};
  for(auto team:packOrder)if(w.packs[team].enabled){lookahead(w,team);directorStep(w,team);commander(w,team);formationPlan(w,team);
    if(w.config->abilities&&w.config->skills[team].abilities==AbilityPolicy::Coordinated&&
      (w.brains[team]!=Brain::Rules||w.packs[team].formation.coordAbilities))coordAbilities(w,team);}
  w.order=w.active;
  const uint32_t tick=toUint32(std::floor(w.time/dt+.5));
  Rng shuffle(toUint32(w.config->seed*73856093.0) ^ toUint32(double(tick)*19349663.0));
  shuffle();shuffle();
  for (size_t i=w.order.size();i>1;--i) {const size_t j=size_t(std::floor(shuffle()*double(i)));std::swap(w.order[i-1],w.order[j]);}
  if(w.config->rules==Rules::Game)for(auto i:w.order)gameReflexes(w,i);
  for (auto i:w.order) decideUnit(w,i);
  if(w.config->rules==Rules::Game){for(auto i:w.order){auto& s=w.state[i];s.castOk=true;const auto& sk=w.config->skills[w.units[i].team];
      const auto* t=w.resolve(w.units[i].target);if(sk.waves>0&&!(s.prep>0)&&w.units[i].cooldown<=0&&s.inReach&&t&&t->alive&&s.energy>=s.cost&&windup(w,i)>0){
        uint32_t n=0;for(auto j:w.teams[w.units[i].team])if(w.units[j].alive&&w.state[j].inReach&&w.units[j].cooldown<=0&&!(w.state[j].prep>0)&&w.state[j].windup>0)++n;
        auto& ts=w.tactical[i];if(ts.waitFrom<0)ts.waitFrom=w.time;if(n<sk.waves&&w.time-ts.waitFrom<1)s.castOk=false;else ts.waitFrom=-1;}}
    for(auto i:w.active)gamePrep(w,i,dt*w.state[i].timeRate);}
  w.meleeHits.clear();for (auto i:w.order) if (w.units[i].alive) {
    ++w.counters.unitActions;
    if(w.config->abilities){if(busyAct(w,i,dt))continue;const auto team=w.units[i].team;
      const bool coordinated=w.packs[team].enabled&&w.config->skills[team].abilities==AbilityPolicy::Coordinated&&
        (w.brains[team]!=Brain::Rules||w.packs[team].formation.coordAbilities);
      if(!coordinated&&defaultAbilities(w,i)){
      const auto& a=w.abilities[w.state[i].ability];if(a.chargeEnd>w.time||a.aimUntil>w.time||a.disengageEnd>w.time)continue;}}
    actNovice(w,i,dt);
  }
  for (const auto& hit:w.meleeHits) {
    const auto* src=w.resolve(hit.source);if (src) w.damage(hit.source,hit.target,src->damage*hit.multiplier);
  }
  if (!w.shots.empty()) shots(w,dt);
  for (auto& shell:w.shells) if (w.time>=shell.at) {
    const auto* src=w.resolve(shell.source);if (!src) throw std::logic_error("missing shell source");
    if(shell.slow){w.fields.push_back({shell.pos,45,w.time,w.time+3,src->team});shell.done=true;continue;}
    bool hit=false;
    const auto& candidates=shell.lob?w.active:w.teams[1-src->team];
    for (auto i:candidates) if (w.reference(i)!=shell.source && w.units[i].alive && distance(w.units[i].pos,shell.pos)<=shell.splash+w.units[i].radius) {
      w.damage(shell.source,w.reference(i),shell.damage);hit=true;
    }
    if (!hit && src->team==0) w.stats.wasted+=shell.damage;shell.done=true;
  }
  w.shells.erase(std::remove_if(w.shells.begin(),w.shells.end(),[](const Shell& s){return s.done;}),w.shells.end());
  w.hitLog.erase(std::remove_if(w.hitLog.begin(),w.hitLog.end(),[&](const Hit& h){return w.time-h.time>=3;}),w.hitLog.end());
  separate(w.units,w.active,w.separationGrid,w.config->width,w.config->height,w.pushes);
  const double smooth=std::min(1.0,dt/.3);
  for (auto i:w.active) {
    auto& u=w.units[i];auto& s=w.state[i];if (!u.alive) continue;
    // Direct division preserves zero displacement even for subnormal dt;
    // multiplying by its overflowing reciprocal would produce 0 * infinity.
    u.velocity={(u.pos.x-s.previous.x)/dt,(u.pos.y-s.previous.y)/dt};
    u.smoothVelocity=u.smoothVelocity+(u.velocity-u.smoothVelocity)*smooth;
    const double k=std::min(1.0,dt);
    s.longVelocity=s.longVelocity+(u.velocity-s.longVelocity)*k;
    s.longSpeed+=(length(u.velocity)-s.longSpeed)*k;
  }
  const double aliveSeconds=w.stats.aliveSeconds+w.survivors(0)*dt;
  if (!std::isfinite(aliveSeconds)) throw std::overflow_error("alive seconds overflow");
  w.stats.aliveSeconds=aliveSeconds;
  for(const auto& spawn:w.spawnQueue)if(spawn.at<=w.time)w.spawnHunter(spawn.role);
  w.spawnQueue.erase(std::remove_if(w.spawnQueue.begin(),w.spawnQueue.end(),[&](const Spawn& q){return q.at<=w.time;}),w.spawnQueue.end());
  if(w.skirmishActive)while(w.skirmishLeft&&w.survivors(0)<w.config->skirmishMaxAlive)w.spawnSkirmish();
  w.burnTick=true;for(auto& d:w.dots){const auto* target=w.resolve(d.target);if(!target||!target->alive||d.until<=w.time)continue;
    d.accumulated+=d.dps*dt;if(d.accumulated>=1){const double n=std::floor(d.accumulated);d.accumulated-=n;w.damage(d.source,d.target,n);}}
  w.burnTick=false;
  w.dots.erase(std::remove_if(w.dots.begin(),w.dots.end(),[&](const Dot& d){const auto* t=w.resolve(d.target);return !t||!t->alive||d.until<=w.time;}),w.dots.end());
  for(auto& p:w.packs)for(uint32_t i=0;i<p.pending.size();++i)if(!w.units[i].alive)p.pending[i]=0;
  w.reclaim();
}
} // namespace astelia
