#include "observer_v1.h"
#include "world.h"
#include "formation.h"

namespace astelia {
namespace {
constexpr double cooldowns[]={8,10,8,10,20,12};
bool owns(Role r,Ability a) {
  if(melee(r))return a==Ability::Charge||a==Ability::Shield;
  if(r==Role::Ranged||r==Role::Archer)return a==Ability::Aimed||a==Ability::Disengage;
  if(r==Role::Artillery)return a==Ability::Barrage||a==Ability::Slow;
  return false;
}
bool busy(const World& w,uint32_t i) {
  const auto index=w.state[i].ability;if(index==invalidSlot)return false;
  const auto& a=w.abilities[index];return a.chargeEnd>w.time||a.aimUntil>w.time||a.disengageEnd>w.time;
}
void spend(World& w,uint32_t i,Ability name) {
  ++w.stats.abilities[w.units[i].team][size_t(name)].uses;
  auto& a=w.abilities[w.state[i].ability];a.ready[size_t(name)]=w.time+cooldowns[size_t(name)];a.lock=w.time+1.5;
}
} // namespace
bool abilityReady(const World& w,uint32_t i,Ability name,bool byHand) {
  const auto& u=w.units.at(i);const auto a=w.state[i].ability;
  return w.config->abilities&&u.alive&&a!=invalidSlot&&owns(u.role,name)&&!w.config->abilityOff[u.team][size_t(name)]&&
    (!w.abilities[a].manual||byHand)&&w.abilities[a].ready[size_t(name)]<=w.time&&w.abilities[a].lock<=w.time;
}
bool triggerAbility(World& w,uint32_t i,Ability name,UnitRef target,Vec2 point,bool byHand) {
  if(!abilityReady(w,i,name,byHand)||busy(w,i))return false;
  auto& u=w.units[i];auto& s=w.state[i];auto& a=w.abilities[s.ability];
  if(!target)target=nearest(w,i);const auto* t=w.resolve(target);
  const bool living=t&&t->alive;
  switch(name) {
    case Ability::Charge:
      if(!living||gap(u,*t)<50||gap(u,*t)>200)return false;
      spend(w,i,name);a.chargeTarget=target;a.chargeEnd=w.time+1;u.target=target;return true;
    case Ability::Shield:spend(w,i,name);a.shieldUntil=w.time+3;return true;
    case Ability::Aimed:
      if(!living||gap(u,*t)>u.range)return false;
      spend(w,i,name);a.aimTarget=target;a.aimUntil=w.time+1;return true;
    case Ability::Disengage: {
      if(!living)return false;
      const auto delta=u.pos-t->pos;const double d=length(delta);const auto goal=u.pos+delta*(120/(d>0?d:1));
      spend(w,i,name);s.prep=0;a.disengageGoal={clamp(goal.x,u.radius,w.config->width-u.radius),clamp(goal.y,u.radius,w.config->height-u.radius)};
      a.disengageEnd=w.time+.55;return true;
    }
    case Ability::Barrage: {
      if(!living)return false;const double d=distance(u.pos,t->pos);
      if(d>u.range||d<w.config->roles[2].minRange)return false;
      spend(w,i,name);u.cooldown=s.cooldownMax;
      const double lead=w.config->roles[2].flight;const Vec2 center=t->pos+leadVelocity(w,target,u.team)*lead;
      const Vec2 delta=t->pos-u.pos;const Vec2 perp{-delta.y/(d>0?d:1),delta.x/(d>0?d:1)};
      for(int j=0;j<2;++j){Shell sh;sh.pos=center+perp*((j-.5)*40);sh.at=w.time+lead+j*.25;
        sh.source=w.reference(i);sh.damage=u.damage*.6;sh.splash=w.config->roles[2].splash;sh.barrage=true;w.shells.push_back(sh);observer_v1::launch(w,i,sh);}
      return true;
    }
    case Ability::Slow: {
      const double d=distance(u.pos,point);if(d>u.range||d<w.config->roles[2].minRange)return false;
      spend(w,i,name);Shell sh;sh.pos=point;sh.source=w.reference(i);sh.at=w.time+w.config->roles[2].flight;sh.slow=true;w.shells.push_back(sh);observer_v1::launch(w,i,sh);return true;
    }
  }
  return false;
}
bool busyAct(World& w,uint32_t i,double dt) {
  const auto observerFrom=w.units[i].pos;
  auto& u=w.units[i];auto& s=w.state[i];if(s.ability==invalidSlot)return false;
  auto& a=w.abilities[s.ability];
  if(a.chargeEnd>w.time) {
    const auto* t=w.resolve(a.chargeTarget);
    if(!t||!t->alive||gap(u,*t)<=u.range*.8){a.chargeEnd=0;a.chargeBonus=t&&t->alive;a.chargeTarget={};return false;}
    const auto delta=t->pos-u.pos;const double d=length(delta),step=std::min(230*dt,d-u.radius-t->radius);
    if(d>0)u.pos=u.pos+delta*(step/d);w.liveGrid.moved(i,u.pos);observer_v1::movement(w,i,observerFrom);return true;
  }
  if(a.aimUntil>w.time){Vec2 goal;if(w.packs[u.team].enabled&&shellDodge(w,u.team)&&dodgeGoal(w,i,goal)){a.aimUntil=0;a.aimTarget={};return false;}return true;}
  if(a.aimTarget) {
    auto target=a.aimTarget;a.aimTarget={};const auto* t=w.resolve(target);
    if(!t||!t->alive||gap(u,*t)>u.range+20||!laneClear(w,i,target)) {
      target={};double health=-1;
      for(auto j:w.teams[1-u.team])if(w.units[j].alive&&gap(u,w.units[j])<=u.range&&laneClear(w,i,w.reference(j))&&w.units[j].hp>health){health=w.units[j].hp;target=w.reference(j);}
    }
    if(target){fireShot(w,i,target,u.damage*3);released(w,i);}return true;
  }
  if(a.disengageEnd>w.time) {
    const auto delta=a.disengageGoal-u.pos;const double d=length(delta);
    if(d<1){a.disengageEnd=0;return false;}
    u.pos=u.pos+delta*(std::min(240*dt,d)/d);w.liveGrid.moved(i,u.pos);observer_v1::movement(w,i,observerFrom);return true;
  }
  a.chargeTarget={};return false;
}
bool defaultAbilities(World& w,uint32_t i) {
  const auto& u=w.units[i];const auto& s=w.state[i];
  if(s.ability==invalidSlot||w.config->skills[u.team].abilities==AbilityPolicy::Off)return false;
  if(melee(u.role)) {
    if(abilityReady(w,i,Ability::Charge)) {
      bool close=false;for(auto j:w.teams[1-u.team])if(w.units[j].alive&&gap(u,w.units[j])<=u.range){close=true;break;}
      auto target=u.target;const auto* t=w.resolve(target);if(!t||!t->alive)target=nearest(w,i);
      if(!close&&triggerAbility(w,i,Ability::Charge,target))return true;
    }
    if(abilityReady(w,i,Ability::Shield)&&w.time-s.lastShotHit<1) {
      bool close=false;for(auto j:w.teams[1-u.team])if(w.units[j].alive&&melee(w.units[j].role)&&gap(u,w.units[j])<40){close=true;break;}
      if(!close)triggerAbility(w,i,Ability::Shield);
    }
  } else if(u.role==Role::Ranged||u.role==Role::Archer) {
    if(!abilityReady(w,i,Ability::Disengage)&&!abilityReady(w,i,Ability::Aimed))return false;
    const auto m=nearest(w,i,false,true);const auto* threat=w.resolve(m);
    if(threat&&distance(u.pos,threat->pos)<60&&triggerAbility(w,i,Ability::Disengage,m))return true;
    const auto* t=w.resolve(u.target);
    if(t&&t->alive&&!(threat&&distance(u.pos,threat->pos)<100)&&triggerAbility(w,i,Ability::Aimed,u.target))return true;
  } else if(u.role==Role::Artillery) {
    if(!abilityReady(w,i,Ability::Barrage)&&!abilityReady(w,i,Ability::Slow))return false;
    UnitRef best;uint32_t count=0;
    for(auto j:w.teams[1-u.team]) {
      const auto& t=w.units[j];if(!t.alive)continue;const double d=distance(u.pos,t.pos);
      if(d>u.range||d<w.config->roles[2].minRange)continue;
      uint32_t n=0;for(auto k:w.teams[1-u.team])if(w.units[k].alive&&distance(w.units[k].pos,t.pos)<w.config->roles[2].splash)++n;
      if(n>count){count=n;best=w.reference(j);}
    }
    if(best&&count>=3&&triggerAbility(w,i,Ability::Barrage,best))return true;
    if(best&&count>=2&&triggerAbility(w,i,Ability::Slow,{},w.units[best.slot].pos))return true;
  }
  return false;
}
} // namespace astelia
