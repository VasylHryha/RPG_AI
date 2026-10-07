#include "escort.h"
#include <algorithm>
#include <limits>
namespace astelia::control {
std::vector<EscortPoint> escortPoints(const Observation& o,uint8_t side,double dose){
 std::vector<const ObservedUnit*> own,enemy,ranged,units;
 for(const auto& u:o.units)if(u.hp>0){
  if(u.role==ObservedRole::Artillery)(u.team==side?own:enemy).push_back(&u);
  if(u.role==ObservedRole::Ranged)(u.team==side?units:ranged).push_back(&u);
 }
 auto order=[](auto a,auto b){return a->id<b->id;};
 for(auto* v:{&own,&enemy,&ranged,&units})std::sort(v->begin(),v->end(),order);
 std::vector<EscortPoint> out;if(own.empty()||enemy.empty())return out;
 double ex=0,ey=0;for(auto e:enemy){ex+=e->x;ey+=e->y;}ex/=enemy.size();ey/=enemy.size();
 auto nearest=[](const auto& list,double x,double y,double limit){
  const ObservedUnit* best=nullptr;double distance=limit;
  for(auto u:list){double d=std::hypot(x-u->x,y-u->y);if(d<=limit&&(!best||d<distance||(d==distance&&u->id<best->id))){best=u;distance=d;}}
  return best;
 };
 for(auto u:units){
  auto g=nearest(own,u->x,u->y,std::numeric_limits<double>::infinity());
  EscortPoint p;p.id=u->id;p.gun=g->id;p.x=u->x;p.y=u->y;p.gx=g->x;p.gy=g->y;
  auto threat=nearest(ranged,g->x,g->y,400);double dx=0,dy=0;
  if(threat){p.threat=threat->id;dx=threat->x-g->x;dy=threat->y-g->y;p.direction=1;}
  if(!threat||std::hypot(dx,dy)<1e-9){dx=ex-g->x;dy=ey-g->y;p.direction=2;}
  if(std::hypot(dx,dy)<1e-9){auto e=nearest(enemy,g->x,g->y,std::numeric_limits<double>::infinity());dx=e->x-g->x;dy=e->y-g->y;p.direction=3;}
  const double n=std::hypot(dx,dy);
  if(n<1e-9)p.direction=0;
  else {p.rawX=g->x+dose*dx/n;p.rawY=g->y+dose*dy/n;p.clipX=std::clamp(p.rawX,0.0,o.width);p.clipY=std::clamp(p.rawY,0.0,o.height);}
  out.push_back(p);
 }
 return out;
}
void EscortProbeV1::prepare(const Observation& o){
 base_.prepare(o);actions_.clear();if(!base_.lastTick().accepted)return;
 for(const auto& p:escortPoints(o,side_,dose_))if(p.direction){auto d=base_.decide(o,p.id);d.x=p.clipX;d.y=p.clipY;d.multiplier=std::hypot(p.x-d.x,p.y-d.y)>2?1:0;d.stop=0;actions_.emplace(p.id,d);}
}
UnitDecision EscortProbeV1::decide(const Observation& o,UnitId id){auto i=actions_.find(id);return i==actions_.end()?base_.decide(o,id):i->second;}
Controller* probeBase(Controller* c){auto* e=dynamic_cast<EscortProbeV1*>(c);return e?&e->base():c;}
}
