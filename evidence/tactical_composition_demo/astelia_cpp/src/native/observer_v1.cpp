#include "observer_v1.h"
namespace astelia::observer_v1 {
thread_local Sink* sink=nullptr;
static bool observing(const World& w){return sink&&sink->world==&w&&!w.branch;}
void movement(const World& w,uint32_t i,Vec2 from){
 if(!observing(w))return;const auto& u=w.units[i];if(u.team!=0||!u.alive)return;
 for(auto j:w.active){const auto& gun=w.units[j];const auto& gs=w.state[j];if(!gun.alive||gun.team!=1||gun.role!=Role::Artillery)continue;
  const double before=distance(from,gun.pos),after=distance(u.pos,gun.pos);
  if(!(before>gun.range&&after<=gun.range&&after>=gs.minRange))continue;
  if(dot(u.pos-from,gun.pos-from)<=0)continue;
  Entry e{u.id,gun.id,u.role,w.time,after,from,u.pos,gun.pos,0,{},{},{}};
  for(auto k:w.active){const auto& a=w.units[k];if(!a.alive)continue;
   const double d=distance(a.pos,gun.pos);
   if(a.team==0){if(d>=gs.minRange&&d<=gun.range)e.insideBand.push_back(a.id);
    if(a.role==Role::Artillery?(d>=w.state[k].minRange&&d<=a.range):(d<=a.range+a.radius+gun.radius))e.inReach.push_back(a.id);}
   if(a.team==1&&a.role==Role::Artillery&&a.id!=gun.id){e.otherGuns.push_back(a.pos);const double r=distance(a.pos,u.pos);if(r>=w.state[k].minRange&&r<=a.range)++e.cover;}
  }sink->entries.push_back(std::move(e));
 }
}
void hit(const World& w,const UnitHot& src,const UnitHot& dst,double amount,double dealt){
 if(!observing(w))return;
 Damage event{src.id,dst.id,src.team,dst.team,src.role,dst.role,amount,dealt,w.time,distance(src.pos,dst.pos),!dst.alive,src.pos,dst.pos,{},{},{}};
 if(!dst.alive&&dst.team==1&&dst.role==Role::Artillery){
  for(auto k:w.active){const auto& a=w.units[k];if(!a.alive)continue;const double d=distance(a.pos,dst.pos);
   if(a.team==0){if(d>=w.state[size_t(&dst-w.units.data())].minRange&&d<=dst.range)event.insideBand.push_back(a.id);
    if(a.role==Role::Artillery?(d>=w.state[k].minRange&&d<=a.range):(d<=a.range+a.radius+dst.radius))event.inReach.push_back(a.id);}
   if(a.team==1&&a.role==Role::Artillery)event.support.push_back({a.id,a.pos,a.range,w.state[k].minRange});
  }
 }sink->damage.push_back(std::move(event));
}
void dodge(const World& w,uint32_t i,bool result,Vec2 goal){if(observing(w)&&result){const auto& u=w.units[i];sink->dodges.push_back({u.id,u.team,u.pos,goal});}}
void launch(const World& w,uint32_t i,const Shell& sh){if(observing(w)){const auto& u=w.units[i];const auto* t=w.resolve(u.target);sink->launches.push_back({u.id,t?t->id:0,u.team,sh.pos,sh.born,sh.at,sh.splash,sh.barrage,sh.slow});}}
}
