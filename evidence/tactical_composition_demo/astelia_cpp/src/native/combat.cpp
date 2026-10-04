#include "world.h"

namespace astelia {
namespace {
void goTo(Decision& d,Vec2 goal,double stop=0,double multiplier=1) {
  if(!d.keep){d.move=true;d.goal=goal;d.stop=stop;d.multiplier=multiplier;}
}
void decideNovice(World& w,uint32_t i) {
  auto& u=w.units[i]; auto& s=w.state[i]; auto& d=s.decision; d=Decision{};
  s.inReach=false;const auto& skills=w.config->skills[u.team];
  if(s.guardUntil>w.time)return;
  const auto* previous=w.resolve(u.target);const bool engaged=melee(u.role)&&previous&&previous->alive&&gap(u,*previous)<=u.range;
  if(skills.dodgeShots&&!(skills.dodgeSoft&&melee(u.role))&&!engaged) {
    const Shot* best=nullptr;double bt=INFINITY,side=0;
    for(const auto& shot:w.shots){const auto* src=w.resolve(shot.source);
      if(!shot.aimed||!src||src->team==u.team||w.time-shot.born<skills.shotReact)continue;
      const auto p=u.pos-shot.pos;const double along=dot(p,shot.direction),cross=p.x*shot.direction.y-p.y*shot.direction.x;
      if(along>0&&along<=std::min(shot.left,shot.speed*.4)&&std::abs(cross)<=u.radius+3&&along<bt){best=&shot;bt=along;side=cross;}}
    if(best){const double k=side>=0?1:-1;goTo(d,u.pos+Vec2{best->direction.y*30*k,-best->direction.x*30*k});return;}
  }
  if(u.role==Role::Player){d.release=Release::Player;return;}
  if(w.config->rules==Rules::Game&&s.standoff>0) {
    const auto r=nearest(w,i);const auto* t=w.resolve(r);
    if(t){const double l=distance(u.pos,t->pos);if(l<s.standoff){goTo(d,t->pos+(u.pos-t->pos)*(s.standoff/(l>0?l:1)),0,.5);d.keep=true;}}
  }
  if(skills.dodgeShells&&!engaged){
    for(const auto& f:w.fields)if(f.team!=u.team&&f.from<=w.time&&f.until>=w.time+.5&&distance(u.pos,f.pos)<=f.radius+u.radius){
      const auto delta=u.pos-f.pos;const double l=length(delta);goTo(d,l<.5?u.pos+Vec2{30,0}:u.pos+delta*(40/l));return;}
    const Shell* best=nullptr;double bt=INFINITY,bd=0;
    for(const auto& sh:w.shells){const auto* src=w.resolve(sh.source);if(!src||src->team==u.team)continue;
      const double l=distance(u.pos,sh.pos),need=sh.splash+u.radius+4-l,left=sh.at-w.time;
      if(need>0&&left>0&&u.speed>0&&need/u.speed<left+.1&&left<bt){best=&sh;bt=left;bd=l;}}
    if(best){goTo(d,bd<.5?u.pos+Vec2{30,0}:u.pos+(u.pos-best->pos)*(40/bd));return;}
  }
  UnitRef target;
  if (melee(u.role)) {
    const auto* a=w.resolve(s.meleeAttacker);
    if (a && a->alive && w.time-s.meleeAt<1 && gap(*a,u)<24) target=s.meleeAttacker;
  }
  if (!target) {target=nearest(w,i,u.role==Role::Artillery);if (!target) target=nearest(w,i);}
  if(u.role==Role::Hunter){
    const auto* answer=w.resolve(s.meleeAttacker);
    if(!(answer&&answer->alive&&w.time-s.meleeAt<1&&gap(*answer,u)<24)){
      const auto* near=w.resolve(target);UnitRef soft;double best=INFINITY;
      for(auto j:w.teams[1-u.team])if(w.units[j].alive&&!melee(w.units[j].role)){const double l=distance(u.pos,w.units[j].pos);if(l<best){best=l;soft=w.reference(j);}}
      if(near&&soft&&best<distance(u.pos,near->pos)+60)target=soft;
      const auto block=nearest(w,i,false,true);const auto* b=w.resolve(block);if(b&&gap(u,*b)<6)target=block;
    }
  }
  u.target=target; const auto* t=w.resolve(target); if (!t) return;
  if (melee(u.role)) {
    d.release=Release::Melee;
    s.inReach=gap(u,*t)<=u.range;
    if(w.config->rules==Rules::Game){if(!s.inReach){const double rr=std::max(2*u.radius,.65*(u.range+u.radius+12)),a=u.id*2.399963;
      goTo(d,t->pos+Vec2{std::cos(a)*rr,std::sin(a)*rr});}}
    else if(gap(u,*t)>u.range*.9)goTo(d,skills.pursuitCut&&gap(u,*t)>30?interceptPoint(w,u.pos,target,u.speed,u.team):t->pos,u.range*.8+t->radius+u.radius);
  } else if (u.role==Role::Artillery) {
    d.release=Release::Artillery;
    const double l=distance(u.pos,t->pos);
    s.inReach=l<=u.range&&l>=s.minRange;
    if (l>u.range)goTo(d,t->pos,u.range*.9);
    else if (l<s.minRange+20)goTo(d,u.pos*2-t->pos);
  } else {
    d.release=Release::Direct;d.post=true;s.inReach=gap(u,*t)<=u.range;
    const auto threat=nearest(w,i,false,true);const auto* m=w.resolve(threat);
    if(m&&distance(u.pos,m->pos)<skills.kite){const auto delta=u.pos-m->pos;const double l=length(delta);goTo(d,u.pos+delta*(40/(l>0?l:1)));}
    else if (gap(u,*t)>u.range)goTo(d,t->pos,u.range*.85+t->radius+u.radius);
    else if (!laneClear(w,i,target)) {
      const Vec2 delta=t->pos-u.pos; const double l=length(delta)>0?length(delta):1;
      goTo(d,{u.pos.x-delta.y/l*20*s.strafe,u.pos.y+delta.x/l*20*s.strafe});
    }else goTo(d,u.pos);
  }
}
void actNovice(World& w,uint32_t i,double dt) {
  auto& u=w.units[i]; auto& s=w.state[i]; const auto& d=s.decision;
  const auto* t=w.resolve(u.target);
  if(d.release==Release::Player){playerBrain(w,i,dt);return;}
  // Melee and free artillery use pre-walk reach, direct fire uses post-walk reach.
  const double before=t?(melee(u.role)?gap(u,*t):distance(u.pos,t->pos)):INFINITY;
  if (d.move) w.move(i,d.goal,dt*d.multiplier,d.stop);
  if (!t) return;
  auto* ability=s.ability==invalidSlot?nullptr:&w.abilities[s.ability];
  if(d.release==Release::Melee) {
    if(w.config->rules==Rules::Game){if(prepared(w,i)){released(w,i);if(before<=u.range){
      w.meleeHits.push_back({w.reference(i),u.target,ability&&ability->chargeBonus?1.5:1});if(ability)ability->chargeBonus=false;}}}
    else if(before<=u.range&&u.cooldown<=0&&!(ability&&ability->shieldUntil>w.time)){
      u.cooldown=s.cooldownMax;w.meleeHits.push_back({w.reference(i),u.target,ability&&ability->chargeBonus?1.5:1});if(ability)ability->chargeBonus=false;}
  } else if(d.release==Release::Direct&&prepared(w,i)&&gap(u,*t)<=u.range&&laneClear(w,i,u.target)) {
    released(w,i);fireShot(w,i,u.target);
  } else if(d.release==Release::Artillery&&prepared(w,i)) {
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
          s.pos=end;s.left-=step;if(s.left<=0)s.done=true;continue;}
        if (w.units[hit.slot].team!=src->team) w.damage(s.source,hit,s.damage);
        else {if(src->team==0)w.stats.wasted+=s.damage;if(w.config->rules==Rules::Game)w.damage(s.source,hit,s.damage);}
        s.done=true;
      } else {
        s.pos=end;s.left-=step;
        if (s.left<=0) {s.done=true;if (src->team==0) w.stats.wasted+=s.damage;}
      }
    } else {
      if (!target) {s.done=true;continue;}
      const Vec2 delta=target->pos-s.pos;const double l=length(delta),step=s.speed*dt;
      UnitRef blocker=lineBlocker(w.units,w.shotGrid,s.pos,target->pos,target->radius,s.source,s.target);
      if (blocker && distance(w.units[blocker.slot].pos,s.pos)<=step+w.units[blocker.slot].radius) {
        if (w.units[blocker.slot].team!=src->team) w.damage(s.source,blocker,s.damage);
        else if (src->team==0) w.stats.wasted+=s.damage;
        s.done=true;
      } else if (l<=step+target->radius) {
        if (target->alive) w.damage(s.source,s.target,s.damage);else if (src->team==0) w.stats.wasted+=s.damage;
        s.done=true;
      } else s.pos=s.pos+delta*(step/l);
    }
  }
  w.shots.erase(std::remove_if(w.shots.begin(),w.shots.end(),[](const Shot& s){return s.done;}),w.shots.end());
}
} // namespace
void coreStep(World& w) {
  if (w.branch) ++w.counters.branchSteps;else ++w.counters.outerSteps;
  const double dt=w.config->dt,nextTime=w.time+dt;
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
  w.order=w.active;
  const uint32_t tick=toUint32(std::floor(w.time/dt+.5));
  Rng shuffle(toUint32(w.config->seed*73856093.0) ^ toUint32(double(tick)*19349663.0));
  shuffle();shuffle();
  for (size_t i=w.order.size();i>1;--i) {const size_t j=size_t(std::floor(shuffle()*double(i)));std::swap(w.order[i-1],w.order[j]);}
  if(w.config->rules==Rules::Game)for(auto i:w.order)gameReflexes(w,i);
  for (auto i:w.order) decideNovice(w,i);
  if(w.config->rules==Rules::Game)for(auto i:w.active)gamePrep(w,i,dt*w.state[i].timeRate);
  w.meleeHits.clear();for (auto i:w.order) if (w.units[i].alive) {
    ++w.counters.unitActions;
    if(w.config->abilities){if(busyAct(w,i,dt))continue;if(defaultAbilities(w,i)){
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
  if(w.config->scenario==Scenario::Skirmish)while(w.skirmishLeft&&w.survivors(0)<w.config->skirmishMaxAlive)w.spawnSkirmish();
  w.burnTick=true;for(auto& d:w.dots){const auto* target=w.resolve(d.target);if(!target||!target->alive||d.until<=w.time)continue;
    d.accumulated+=d.dps*dt;if(d.accumulated>=1){const double n=std::floor(d.accumulated);d.accumulated-=n;w.damage(d.source,d.target,n);}}
  w.burnTick=false;
  w.dots.erase(std::remove_if(w.dots.begin(),w.dots.end(),[&](const Dot& d){const auto* t=w.resolve(d.target);return !t||!t->alive||d.until<=w.time;}),w.dots.end());
  w.reclaim();w.rebuildTeams();
}
} // namespace astelia
