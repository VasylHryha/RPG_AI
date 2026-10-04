#include "formation.h"

namespace astelia {
namespace {
void goTo(Decision& d,Vec2 goal,double stop=0,double multiplier=1){if(!d.keep){d.move=true;d.goal=goal;d.stop=stop;d.multiplier=multiplier;}}
bool saveWounded(World& w,uint32_t i){const auto& u=w.units[i];const auto& sk=w.config->skills[u.team];
  if(w.config->rules!=Rules::Game||sk.saveWounded<=0||u.hp>sk.saveWounded*u.maxhp)return false;
  const auto& es=w.foes(u.team);const auto ours=w.survivors(u.team);if(es.empty()||es.size()<=2||ours>=4*es.size())return false;
  uint32_t wounded=0;for(auto j:w.teams[u.team])if(w.units[j].alive&&w.units[j].hp<=sk.saveWounded*w.units[j].maxhp)++wounded;if(wounded*2>=ours)return false;
  const auto near=nearest(w,i);const auto* t=w.resolve(near);if(!t||distance(u.pos,t->pos)>t->range+t->speed*1.5+60)return false;
  const auto delta=u.pos-t->pos;const double d=length(delta);const double home=u.team==0?40:w.config->width-40;
  goTo(w.state[i].decision,u.pos+delta*(60/(d>0?d:1))+Vec2{(home-u.pos.x)*.2,0});return true;
}
UnitRef releasedMelee(const World& w,uint32_t i){const auto& u=w.units[i];const auto& s=w.state[i];const auto* attacker=w.resolve(s.meleeAttacker);
  if(attacker&&attacker->alive&&w.time-s.meleeAt<1&&gap(*attacker,u)<24)return s.meleeAttacker;
  const auto* old=w.resolve(u.target);if(old&&old->alive&&!melee(old->role))return u.target;
  UnitRef best;double bd=INFINITY;const auto& es=w.foes(u.team);
  for(auto j:es){const auto& h=w.units[j];if(w.packs[u.team].formation.raidTarget==SoftTarget::Artillery?h.role!=Role::Artillery:melee(h.role))continue;
    uint32_t claimed=0;for(auto k:w.teams[u.team])if(w.units[k].alive&&w.units[k].role==Role::Melee&&w.units[k].target==w.reference(j))++claimed;
    if(claimed>=2)continue;const double d=distance(u.pos,h.pos);if(d<bd){bd=d;best=w.reference(j);}}
  return best?best:nearest(w,i);
}
}
void decideUnit(World& w,uint32_t i){
  auto& u=w.units[i];auto& s=w.state[i];auto& d=s.decision;auto& ts=w.tactical[i];d=Decision{};s.inReach=false;
  const auto& sk=w.config->skills[u.team];const auto& pack=w.packs[u.team];const bool formed=pack.enabled;
  if(ts.assignedSet)u.target=ts.assigned;if(s.guardUntil>w.time)return;
  const auto* prior=w.resolve(u.target);const bool engaged=melee(u.role)&&prior&&prior->alive&&gap(u,*prior)<=u.range;
  if(sk.dodgeShots&&!(sk.dodgeSoft&&melee(u.role))&&!engaged){const Shot* best=nullptr;double bt=INFINITY,side=0;
    for(const auto& sh:w.shots){const auto* src=w.resolve(sh.source);if(!sh.aimed||!src||src->team==u.team||w.time-sh.born<sk.shotReact)continue;
      const auto delta=u.pos-sh.pos;const double along=dot(delta,sh.direction),cross=delta.x*sh.direction.y-delta.y*sh.direction.x;
      if(along>0&&along<=std::min(sh.left,sh.speed*.4)&&std::abs(cross)<=u.radius+3&&along<bt){best=&sh;bt=along;side=cross;}}
    if(best){const double k=side>=0?1:-1;goTo(d,u.pos+Vec2{best->direction.y*30*k,-best->direction.x*30*k});return;}}
  if(u.role==Role::Player){d.release=Release::Player;return;}
  if(formed&&saveWounded(w,i))return;
  if(w.config->rules==Rules::Game&&s.standoff>0){const auto near=nearest(w,i);const auto* t=w.resolve(near);
    if(t){const double l=distance(u.pos,t->pos);if(l<s.standoff){goTo(d,t->pos+(u.pos-t->pos)*(s.standoff/(l>0?l:1)),0,.5);d.keep=true;}}}
  const bool surround=formed&&pack.formation.surround&&ts.hasSurroundGoal&&prior&&prior->alive;
  const bool released=formed&&(pack.formation.release&(1<<size_t(u.role)))&&!(u.role==Role::Melee&&ts.wing);
  if(surround){if(!engaged)goTo(d,ts.surroundGoal);d.keep=true;if(melee(u.role))d.post=true;}
  else if(shellDodge(w,u.team)&&(released||(formed&&sk.lockedDodge)||!engaged)){Vec2 goal;if(dodgeGoal(w,i,goal)){goTo(d,goal);if(formed&&!released&&u.role==Role::Ranged)d.release=Release::DodgeFire;return;}}
  UnitRef target;
  if(formed&&surround)target=u.target;
  else if(formed&&u.role==Role::Melee){if(ts.hasFlankGoal&&!ts.answering){goTo(d,ts.flankGoal);return;}target=released?releasedMelee(w,i):u.target;
    if(!target){goTo(d,s.slot);return;}}
  else if(formed&&u.role==Role::Artillery){const auto* old=w.resolve(u.target);target=u.cooldown>0&&!released?(old&&old->alive?u.target:UnitRef{}):artilleryTarget(w,i);}
  else if(formed)target=shooterTarget(w,i,released);
  else{if(melee(u.role)){const auto* a=w.resolve(s.meleeAttacker);if(a&&a->alive&&w.time-s.meleeAt<1&&gap(*a,u)<24)target=s.meleeAttacker;}
    if(!target){target=nearest(w,i,u.role==Role::Artillery);if(!target)target=nearest(w,i);}
    if(u.role==Role::Hunter){const auto* a=w.resolve(s.meleeAttacker);if(!(a&&a->alive&&w.time-s.meleeAt<1&&gap(*a,u)<24)){
      const auto* near=w.resolve(target);UnitRef soft;double bd=INFINITY;for(auto j:w.foes(u.team))if(!melee(w.units[j].role)){const double l=distance(u.pos,w.units[j].pos);if(l<bd){bd=l;soft=w.reference(j);}}
      if(near&&soft&&bd<distance(u.pos,near->pos)+60)target=soft;
      const auto block=nearest(w,i,false,true);const auto* b=w.resolve(block);if(b&&gap(u,*b)<6)target=block;}}}
  if(melee(u.role)&&w.config->rules==Rules::Game){const auto* t=w.resolve(target);
    if(t&&sk.weaponsFree&&gap(u,*t)>u.range){double bd=u.range;for(auto j:w.foes(u.team)){const double g=gap(u,w.units[j]);if(g<=bd){bd=g;target=w.reference(j);}}}
    if(sk.meleeFocus&&!(s.prep>0)){double best=INFINITY;UnitRef focus;
      for(auto j:w.foes(u.team)){const auto& h=w.units[j];if(gap(u,h)>u.range)continue;double left=h.hp;
        for(auto k:w.teams[u.team])if(k!=i&&w.units[k].alive&&melee(w.units[k].role)&&w.state[k].prep>0&&w.units[k].target==w.reference(j))left-=w.units[k].damage*(1-w.state[j].protection);
        const double key=left>0?left:1e6+h.hp;if(key<best){best=key;focus=w.reference(j);}}if(focus)target=focus;}}
  u.target=target;const auto* t=w.resolve(target);
  if(melee(u.role)){if(!t)return;d.release=Release::Melee;s.inReach=gap(u,*t)<=u.range;
    if(w.config->rules==Rules::Game){if(!s.inReach){const double radius=std::max(2*u.radius,.65*(u.range+u.radius+12)),a=u.id*2.399963;goTo(d,t->pos+Vec2{std::cos(a)*radius,std::sin(a)*radius});}}
    else if(gap(u,*t)>u.range*.9)goTo(d,sk.pursuitCut&&gap(u,*t)>30?interceptPoint(w,u.pos,target,u.speed,u.team):t->pos,u.range*.8+t->radius+u.radius);
    return;}
  if(u.role==Role::Artillery){d.release=Release::Artillery;d.bound=formed&&!released;d.post=d.bound;
    if(d.bound)goTo(d,surround?u.pos:s.slot);if(!t)return;const double l=distance(u.pos,t->pos);s.inReach=l<=u.range&&l>=s.minRange;
    if(!d.bound){if(l>u.range)goTo(d,t->pos,u.range*.9);else if(l<s.minRange+20)goTo(d,u.pos*2-t->pos);}return;}
  d.release=Release::Direct;d.post=true;s.inReach=t&&gap(u,*t)<=u.range;
  const bool free=!formed||released;const Vec2 base=free||surround?u.pos:s.slot;const double leash=surround?0:pack.formation.laneLeash+pack.formation.kiteLeash;
  Vec2 goal=base;double stop=0;bool slot=!free;
  const auto near=nearest(w,i,false,true);const auto* threat=w.resolve(near);
  if(threat&&distance(u.pos,threat->pos)<sk.kite){const auto delta=u.pos-threat->pos;const double l=length(delta);goal=u.pos+delta*(40/(l>0?l:1));slot=false;}
  else if(t&&free&&gap(u,*t)>u.range){goal=t->pos;stop=u.range*.85+t->radius+u.radius;slot=false;}
  else if(t&&gap(u,*t)<=u.range&&!laneClear(w,i,target)){const auto delta=t->pos-u.pos;const double l=length(delta);goal=u.pos+Vec2{-delta.y,delta.x}*(20*s.strafe/(l>0?l:1));slot=false;
    if(!free&&distance(goal,base)>leash)s.strafe=-s.strafe;}
  else if(free)goal=u.pos;
  if(formed&&sk.jink>0&&slot&&t){if(!(ts.jinkUntil>w.time)){ts.jinkUntil=w.time+.3+std::fmod(double(u.id)*7919+std::floor(w.time*10+.5)*104729,1000)/2500;ts.jinkSide=-ts.jinkSide;}
    const auto delta=t->pos-u.pos;const double l=length(delta);goal=base+Vec2{-delta.y,delta.x}*(sk.jink*ts.jinkSide/(l>0?l:1));}
  if(!free&&distance(goal,base)>leash){const auto delta=goal-base;goal=base+delta*(leash/length(delta));}goTo(d,goal,stop);
}
} // namespace astelia
