#include "world.h"

namespace astelia {
namespace {
UnitRef nearest(const World& w,uint32_t slot,bool outsideMinimum=false) {
  const auto& u=w.units[slot];
  UnitRef best; double bd=INFINITY;
  for (auto i:w.teams[1-u.team]) {
    const auto& e=w.units[i]; if (!e.alive) continue;
    const double d=distance(u.pos,e.pos);
    if (outsideMinimum && d<w.state[slot].minRange) continue;
    if (d<bd) {bd=d;best=w.reference(i);}
  }
  return best;
}
bool laneClear(const World& w,uint32_t i,UnitRef target) {
  const auto* t=w.resolve(target); if (!t) return false;
  const UnitRef blocker=lineBlocker(w.units,w.liveGrid,w.units[i].pos,t->pos,t->radius,w.reference(i),target);
  return !blocker || w.units[blocker.slot].team!=w.units[i].team;
}
void decideNovice(World& w,uint32_t i) {
  auto& u=w.units[i]; auto& s=w.state[i]; auto& d=s.decision; d=Decision{};
  UnitRef target;
  if (melee(u.role)) {
    const auto* a=w.resolve(s.meleeAttacker);
    if (a && a->alive && w.time-s.meleeAt<1 && gap(*a,u)<24) target=s.meleeAttacker;
  }
  if (!target) {target=nearest(w,i,u.role==Role::Artillery);if (!target) target=nearest(w,i);}
  u.target=target; const auto* t=w.resolve(target); if (!t) return;
  if (melee(u.role)) {
    d.release=Release::Melee;
    if (gap(u,*t)>u.range*.9) {d.move=true;d.goal=t->pos;d.stop=u.range*.8+t->radius+u.radius;}
  } else if (u.role==Role::Artillery) {
    d.release=Release::Artillery;
    const double l=distance(u.pos,t->pos);
    if (l>u.range) {d.move=true;d.goal=t->pos;d.stop=u.range*.9;}
    else if (l<s.minRange+20) {d.move=true;d.goal=u.pos*2-t->pos;}
  } else {
    d.release=Release::Direct;d.post=true;d.move=true;d.goal=u.pos;
    if (gap(u,*t)>u.range) {d.goal=t->pos;d.stop=u.range*.85+t->radius+u.radius;}
    else if (!laneClear(w,i,target)) {
      const Vec2 delta=t->pos-u.pos; const double l=length(delta)>0?length(delta):1;
      d.goal={u.pos.x-delta.y/l*20*s.strafe,u.pos.y+delta.x/l*20*s.strafe};
    }
  }
}
void actNovice(World& w,uint32_t i,double dt) {
  auto& u=w.units[i]; auto& s=w.state[i]; const auto& d=s.decision;
  const auto* t=w.resolve(u.target);
  // Melee and free artillery use pre-walk reach, direct fire uses post-walk reach.
  const double before=t?(melee(u.role)?gap(u,*t):distance(u.pos,t->pos)):INFINITY;
  if (d.move) w.move(i,d.goal,dt*d.multiplier,d.stop);
  if (!t) return;
  if (d.release==Release::Melee && before<=u.range && u.cooldown<=0) {
    u.cooldown=s.cooldownMax; w.meleeHits.push_back({w.reference(i),u.target,1});
  } else if (d.release==Release::Direct && u.cooldown<=0 && gap(u,*t)<=u.range && laneClear(w,i,u.target)) {
    u.cooldown=s.cooldownMax;
    const Vec2 delta=t->pos-u.pos; const double l=length(delta)>0?length(delta):1;
    Shot shot;shot.pos=u.pos;shot.source=w.reference(i);shot.target=u.target;
    shot.direction=delta*(1/l);shot.speed=w.config->aimedShots?w.config->shotSpeed:s.shotSpeed;
    shot.left=u.range*1.3;shot.born=w.time;shot.damage=shot.pending=u.damage;shot.aimed=w.config->aimedShots;
    w.shots.push_back(std::move(shot));
  } else if (d.release==Release::Artillery && u.cooldown<=0 && before<=u.range && before>=s.minRange) {
    u.cooldown=s.cooldownMax;
    Shell shell;shell.pos=t->pos;shell.source=w.reference(i);shell.at=w.time+s.lobSpeed;
    shell.born=w.time;shell.damage=u.damage;shell.splash=s.splash;w.shells.push_back(shell);
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
          if (!u.alive || r==s.source) return;
          double t; if (!segmentParameter(s.pos,s.direction,step,u,t)) return;
          if (t<ht || (hit && t==ht && u.id<w.units[hit.slot].id)) {hit=r;ht=t;}
        });
      if (hit) {
        if (w.units[hit.slot].team!=src->team) w.damage(s.source,hit,s.damage);
        else if (src->team==0) w.stats.wasted+=s.damage;
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
  if (w.config->rules!=Rules::Sandbox || w.config->windUp) throw std::invalid_argument("unsupported core slice rules");
  if (w.branch) ++w.counters.branchSteps;else ++w.counters.outerSteps;
  const double dt=w.config->dt;w.time+=dt;
  for (auto i:w.active) {
    auto& u=w.units[i];auto& s=w.state[i];if (u.cooldown>0) u.cooldown-=dt;
    s.previous=u.pos;s.stepTime=w.time;
  }
  w.rebuildTeams();w.liveGrid.build(w.units,w.active,w.config->width,w.config->height,40);
  w.order=w.active;
  const uint32_t tick=toUint32(std::floor(w.time/dt+.5));
  Rng shuffle(toUint32(w.config->seed*73856093.0) ^ toUint32(double(tick)*19349663.0));
  shuffle();shuffle();
  for (size_t i=w.order.size();i>1;--i) {const size_t j=size_t(std::floor(shuffle()*double(i)));std::swap(w.order[i-1],w.order[j]);}
  for (auto i:w.order) decideNovice(w,i);
  w.meleeHits.clear();for (auto i:w.order) if (w.units[i].alive) {++w.counters.unitActions;actNovice(w,i,dt);}
  for (const auto& hit:w.meleeHits) {
    const auto* src=w.resolve(hit.source);if (src) w.damage(hit.source,hit.target,src->damage*hit.multiplier);
  }
  if (!w.shots.empty()) shots(w,dt);
  for (auto& shell:w.shells) if (w.time>=shell.at) {
    const auto* src=w.resolve(shell.source);if (!src) throw std::logic_error("missing shell source");
    bool hit=false;
    for (auto i:w.teams[1-src->team]) if (w.units[i].alive && distance(w.units[i].pos,shell.pos)<=shell.splash+w.units[i].radius) {
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
    u.velocity=(u.pos-s.previous)*(1/dt);
    u.smoothVelocity=u.smoothVelocity+(u.velocity-u.smoothVelocity)*smooth;
    const double k=std::min(1.0,dt);
    s.longVelocity=s.longVelocity+(u.velocity-s.longVelocity)*k;
    s.longSpeed+=(length(u.velocity)-s.longSpeed)*k;
  }
  w.stats.aliveSeconds+=w.survivors(0)*dt;w.reclaim();w.rebuildTeams();
}
} // namespace astelia
