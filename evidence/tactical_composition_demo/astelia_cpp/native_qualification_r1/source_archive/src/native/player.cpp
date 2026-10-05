#include "world.h"

namespace astelia {
namespace {
struct PlayerAttack {double damage,cost,cast,speed,range;uint32_t pierce=0;};
constexpr PlayerAttack bolt{24,20,.4,765,666},lance{48,40,.8,893,778,2},ember{140,116.7,2.33,893,666};
void playerShot(World& w,uint32_t i,UnitRef target,const PlayerAttack& spec,bool manual) {
  const auto* t=w.resolve(target);if(!t||!t->alive)return;
  const auto& u=w.units[i];const auto delta=t->pos-u.pos;const double d=length(delta);
  Shot s;s.pos=u.pos;s.direction=delta*(1/(d>0?d:1));s.source=w.reference(i);s.target=target;
  s.left=spec.range;s.born=w.time;s.speed=spec.speed;s.damage=s.pending=spec.damage;s.manual=manual;
  s.pierce=spec.pierce;s.ordinal=w.nextShot++;w.shots.push_back(std::move(s));
}
}
void playerBrain(World& w,uint32_t i,double dt) {
  auto& u=w.units[i];auto& s=w.state[i];auto& p=w.players.at(s.player);
  if(!w.survivors(1-u.team))return;
  if(p.dashUntil>w.time){u.speed=112/.45;w.move(i,u.pos+p.dashDirection*50,dt);u.speed=120;return;}
  uint32_t nearCount=0;for(auto j:w.teams[1-u.team])if(w.units[j].alive&&distance(u.pos,w.units[j].pos)<=40)++nearCount;
  const double mob=std::min(1.0,nearCount/8.0);u.speed=120*(1-.4*mob);if(mob>=.66)p.manual=0;
  Vec2 threat;bool danger=false;
  for(auto j:w.teams[1-u.team]){const auto& e=w.units[j];const auto& es=w.state[j];
    if(e.alive&&melee(e.role)&&es.prep>0&&e.target==w.reference(i)&&es.windup-es.prep<=.25&&gap(e,u)<=e.range+12){threat=u.pos-e.pos;danger=true;}}
  for(const auto& sh:w.shells){const auto* src=w.resolve(sh.source);
    if(src&&src->team!=u.team&&sh.at-w.time<.45&&distance(u.pos,sh.pos)<=sh.splash+u.radius){threat=u.pos-sh.pos;danger=true;}}
  for(const auto& sh:w.shots){const auto* src=w.resolve(sh.source);if(!src||src->team==u.team)continue;
    const auto delta=u.pos-sh.pos;const double along=dot(delta,sh.direction),cross=delta.x*sh.direction.y-delta.y*sh.direction.x;
    if(along>0&&along<sh.speed*.3&&std::abs(cross)<=u.radius+2){const double side=cross>=0?1:-1;threat={sh.direction.y*side,-sh.direction.x*side};danger=true;}}
  if(danger&&w.time>=p.dashReady&&s.energy>=10){const double d=length(threat);p.dashDirection=threat*(1/(d>0?d:1));
    s.energy-=10;p.dashReady=w.time+.3;p.dashUntil=w.time+.45;return;}
  Vec2 motion;
  for(auto j:w.teams[1-u.team]){const auto& e=w.units[j];if(!e.alive||!melee(e.role))continue;
    const double d=distance(u.pos,e.pos);if(d<160)motion=motion+(u.pos-e.pos)*((160-d)/(d>0?d:1));}
  if(u.pos.x<120)motion.x+=(120-u.pos.x)*2;if(u.pos.x>w.config->width-120)motion.x-=(u.pos.x-w.config->width+120)*2;
  if(u.pos.y<120)motion.y+=(120-u.pos.y)*2;if(u.pos.y>w.config->height-120)motion.y-=(u.pos.y-w.config->height+120)*2;
  const auto near=nearest(w,i);const auto* t=w.resolve(near);
  if(t&&w.config->playerStyle==PlayerStyle::Orbit){const auto delta=t->pos-u.pos;const double d=length(delta),den=d>0?d:1;
    motion=motion+Vec2{-delta.y/den*60,delta.x/den*60}+delta*((d-400)*.5/den);
  } else if(t&&w.config->playerStyle==PlayerStyle::Press&&distance(u.pos,t->pos)>250&&!motion.x&&!motion.y)motion=t->pos-u.pos;
  else if(t&&distance(u.pos,t->pos)>450&&!motion.x&&!motion.y)motion=t->pos-u.pos;
  if(motion.x||motion.y)w.move(i,u.pos+motion*(40/length(motion)),dt);
  for(auto& l:p.limbs) {
    const auto& spec=l.sequence==0?bolt:lance;const double cost=spec.cost*l.multiplier;
    if(l.prep>0){l.prep+=dt;if(l.prep>=spec.cast){auto target=l.target;const auto* e=w.resolve(target);
      if(!e||!e->alive||distance(e->pos,u.pos)>spec.range)target=nearest(w,i,false,false,spec.range);
      if(target)playerShot(w,i,target,spec,false);l.prep=0;l.sequence=1-l.sequence;l.target={};}continue;}
    const auto target=nearest(w,i,false,false,spec.range);
    if(target&&s.energy-cost>=.1*s.energyMax){s.energy-=cost;l.prep=dt;l.target=target;}
  }
  if(p.manual){p.manualPrep+=dt;if(p.manualPrep>=(p.manual==2?4.3:ember.cast)){
    if(p.manual==2){for(auto j:w.teams[1-u.team])if(w.units[j].alive&&distance(w.units[j].pos,u.pos)<=130+w.units[j].radius)w.damage(w.reference(i),w.reference(j),180);}
    else{auto target=p.manualTarget;const auto* e=w.resolve(target);if(!e||!e->alive||distance(e->pos,u.pos)>ember.range)target=nearest(w,i,false,false,ember.range);
      if(target)playerShot(w,i,target,ember,true);}
    p.manual=0;p.manualTarget={};p.manualPrep=0;
  }}else{
    uint32_t count=0;for(auto j:w.teams[1-u.team])if(w.units[j].alive&&distance(w.units[j].pos,u.pos)<=130+w.units[j].radius)++count;
    const auto big=nearest(w,i,false,false,ember.range,100);
    if(count>=3&&s.energy-215.2>=100){s.energy-=215.2;p.manual=2;p.manualPrep=dt;}
    else if(big&&s.energy-ember.cost>=100){s.energy-=ember.cost;p.manual=1;p.manualPrep=dt;p.manualTarget=big;}
  }
}
} // namespace astelia
