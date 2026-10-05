#include "world.h"
#include "formation.h"
#include "nearest_kernel.h"

namespace astelia {
UnitRef nearest(const World& w,uint32_t slot,bool outsideMinimum,bool meleeOnly,double maximum,double minimumHp) {
  return nearestKernel(w.units,w.foes(w.units[slot].team),slot,w.state[slot].minRange,outsideMinimum,meleeOnly,maximum,minimumHp);
}
bool laneClear(const World& w,uint32_t i,UnitRef target) {
  const auto* t=w.resolve(target);if(!t)return false;
  const auto blocker=lineBlocker(w.units,w.liveGrid,w.units[i].pos,t->pos,t->radius,w.reference(i),target);
  return !blocker||w.units[blocker.slot].team!=w.units[i].team;
}
Vec2 leadVelocity(const World& w,UnitRef target,uint8_t team) {
  const auto* t=w.resolve(target);if(!t)return {};
  switch(w.config->skills[team].lead){case Lead::Raw:return t->velocity;case Lead::Smooth:return t->smoothVelocity;default:return {};}
}
Vec2 interceptPoint(const World& w,Vec2 source,UnitRef target,double speed,uint8_t team) {
  const auto* t=w.resolve(target);if(!t)return source;
  const auto v=leadVelocity(w,target,team);double tau=distance(source,t->pos)/speed;
  for(int i=0;i<3;++i)tau=std::min(1.5,distance(source,t->pos+v*tau)/speed);
  return t->pos+v*tau;
}
double windup(const World& w,uint32_t i) {
  if(w.config->rules==Rules::Game)return w.state[i].windup;
  if(!w.config->windUp)return 0;
  const auto r=w.units[i].role;return r==Role::Artillery?1:(r==Role::Ranged||r==Role::Archer?.5:0);
}
bool prepared(const World& w,uint32_t i) {
  return (w.config->rules==Rules::Game?w.state[i].prep>0:w.units[i].cooldown<=0)&&w.state[i].prep>=windup(w,i)-1e-9;
}
void released(World& w,uint32_t i) {
  w.state[i].prep=0;if(w.config->rules==Rules::Sandbox)w.units[i].cooldown=w.state[i].cooldownMax-windup(w,i);
}
void fireShot(World& w,uint32_t i,UnitRef target,double damage) {
  const auto* t=w.resolve(target);if(!t)return;
  const auto& u=w.units[i];const auto& s=w.state[i];
  Shot p;p.pos=u.pos;p.source=w.reference(i);p.target=target;p.damage=p.pending=damage>0?damage:u.damage;
  p.born=w.time;p.aimed=w.config->aimedShots;p.ordinal=w.nextShot++;
  p.speed=p.aimed?(w.config->rules==Rules::Game?(s.shotSpeed>0?s.shotSpeed:w.config->shotSpeed)*s.launch:w.config->shotSpeed):s.shotSpeed;
  if(!(p.speed>0)||!std::isfinite(p.speed))throw std::logic_error("invalid shot speed");
  auto point=p.aimed?interceptPoint(w,u.pos,target,p.speed,u.team):t->pos;
  const auto& tactical=w.tactical[i];
  if(p.aimed&&tactical.aimOffset!=0&&tactical.fireOrder==target){const auto delta=point-u.pos;const double d=length(delta);
    point=point+Vec2{-delta.y,delta.x}*(tactical.aimOffset/(d>0?d:1));}
  p.dodgeable=canDodge(w,target,w.reference(i));
  if(p.aimed&&w.packs[u.team].enabled&&(w.config->skills[u.team].fireControl||w.config->skills[u.team].leaderFire))p.pending=p.damage*hitProbability(w,u.team,target,w.reference(i));
  const Vec2 delta=point-u.pos;
  const double d=length(delta);p.direction=delta*(1/(d>0?d:1));p.left=u.range*1.3;addPending(w,p.source,target,p.pending);w.shots.push_back(std::move(p));
}
void fireShellAt(World& w,uint32_t i,Vec2 point,double prediction,bool hasPrediction,AttackFamily family,bool finisher,uint16_t variant) {
  const auto& u=w.units[i];const auto& s=w.state[i];Shell sh;
  ++w.stats.shellOut[u.team].shells;sh.prediction=prediction;sh.hasPrediction=hasPrediction;sh.family=family;sh.finisher=finisher;sh.variant=variant;
  sh.pos=point;sh.source=w.reference(i);sh.born=w.time;sh.lob=w.config->rules==Rules::Game;
  sh.at=w.time+(sh.lob?distance(u.pos,point)/((s.lobSpeed>0?s.lobSpeed:300)*s.launch):w.config->roles[2].flight);
  sh.damage=u.damage;sh.splash=s.splash>0?s.splash:w.config->roles[2].splash;w.shells.push_back(sh);
}
void gamePrep(World& w,uint32_t i,double dt) {
  auto& u=w.units[i];auto& s=w.state[i];if(!u.alive||!windup(w,i))return;
  if(!(s.prep>0)) {
    const auto* t=w.resolve(u.target);
    if(u.cooldown>0||!s.inReach||!t||!t->alive||s.energy<s.cost||!s.castOk)return;
    if(w.config->attackerCap){uint32_t n=0;for(auto j:w.teams[u.team])if(w.units[j].alive&&w.state[j].prep>0)++n;
      if(n>=w.config->attackerCap)return;}
    if(u.role==Role::Ranged&&!laneClear(w,i,u.target))return;
    s.energy-=s.cost;u.cooldown=s.cooldownMax;s.prep=0;s.castTime=w.time;
  }
  s.prep+=dt;
}
void gameReflexes(World& w,uint32_t i) {
  auto& u=w.units[i];auto& s=w.state[i];if(!u.alive)return;
  if(s.dodge!=Dodge::None && s.dashReady<=w.time) {
    const bool low=u.hp<=.35*u.maxhp;
    for(const auto& shot:w.shots) {
      const auto* src=w.resolve(shot.source);
      if(!shot.aimed||!src||src->team==u.team||src->role!=Role::Player||!(shot.manual||s.dodge==Dodge::Skittish||low))continue;
      const Vec2 p=u.pos-shot.pos;const double along=dot(p,shot.direction);
      if(along<=0||along>std::min(shot.left,shot.speed*.6)||along/shot.speed<.05||std::abs(p.x*shot.direction.y-p.y*shot.direction.x)>28)continue;
      if(std::find(s.rolledShots.begin(),s.rolledShots.end(),shot.ordinal)!=s.rolledShots.end())continue;
      s.rolledShots.push_back(shot.ordinal);
      Rng roll(toUint32(w.config->seed*9301)^toUint32(std::floor(w.time*30+.5)*49297)^toUint32(double(u.id)*233280));
      const double chance=low?1:s.dodge==Dodge::Kiter?.8:s.dodge==Dodge::Storm?.9:1;
      if(roll()>=chance)continue;
      const double cooldown=s.dodge==Dodge::Kiter?.9:s.dodge==Dodge::Storm?1:.7;
      s.dashReady=w.time+cooldown/s.timeRate;
      const auto* t=w.resolve(u.target);const Vec2 ref=melee(u.role)&&t?t->pos-u.pos:u.pos-src->pos;
      const double side=shot.direction.y*ref.x-shot.direction.x*ref.y>=0?1:-1;
      const double d=s.dodge==Dodge::Storm?110:60;
      u.pos={clamp(u.pos.x+shot.direction.y*d*side,u.radius,w.config->width-u.radius),
        clamp(u.pos.y-shot.direction.x*d*side,u.radius,w.config->height-u.radius)};
      w.liveGrid.moved(i,u.pos);break;
    }
  }
  if(s.block&&s.guardUntil<=w.time&&s.blockReady<=w.time&&s.energy>=w.config->kinds.at(s.kind).blockCost)for(const auto& shot:w.shots) {
    const auto* src=w.resolve(shot.source);if(!shot.aimed||!src||src->role!=Role::Player||!shot.manual)continue;
    const Vec2 p=u.pos-shot.pos;const double along=dot(p,shot.direction),ttc=along/shot.speed;
    if(along<=0||ttc<.05||ttc>.6||std::abs(p.x*shot.direction.y-p.y*shot.direction.x)>u.radius+4)continue;
    const auto& k=w.config->kinds.at(s.kind);s.energy-=k.blockCost;s.blockReady=w.time+k.blockCooldown/s.timeRate;s.guardUntil=w.time+k.blockDuration/s.timeRate;
    s.guardDirection=std::atan2(src->pos.y-u.pos.y,src->pos.x-u.pos.x);break;
  }
}
} // namespace astelia
