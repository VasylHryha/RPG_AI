#include "escort.h"
#include <algorithm>
namespace astelia::control {
unsigned splashValue(const Observation& o,uint8_t side,const ObservedUnit& g){
 unsigned n=0;for(const auto& u:o.units)if(u.hp>0&&u.team!=side&&std::hypot(u.x-g.x,u.y-g.y)<=40+u.radius)++n;return n;
}
std::vector<EscortPoint> meleeEscortPoints(const Observation& o,uint8_t side){
 // Geometry-only role projection lets the unchanged P12 function process melee.
 // Enemy ranged and all guns stay untouched; never passed into a controller.
 auto geometry=o;for(auto& u:geometry.units)if(u.team==side){if(u.role==ObservedRole::Melee)u.role=ObservedRole::Ranged;else if(u.role==ObservedRole::Ranged)u.role=ObservedRole::Melee;}
 return escortPoints(geometry,side,60);
}
void EscortProbeV3::prepare(const Observation& o){
 base_.prepare(o);actions_.clear();guns_.clear();if(!base_.base().lastTick().accepted)return;
 std::vector<const ObservedUnit*> own,enemy;
 for(const auto& u:o.units)if(u.hp>0&&u.role==ObservedRole::Artillery)(u.team==side_?own:enemy).push_back(&u);
 if(own.empty()||enemy.empty())return;
 if(arm_==17){
  for(const auto& p:meleeEscortPoints(o,side_))if(p.direction){auto d=base_.decide(o,p.id);d.x=p.clipX;d.y=p.clipY;d.multiplier=std::hypot(p.x-d.x,p.y-d.y)>2?1:0;d.stop=0;actions_.emplace(p.id,d);}return;
 }
 auto reachable=[](const auto& a,const auto& b){const double d=std::hypot(a.x-b.x,a.y-b.y);return d>=a.minRange&&d<=a.range;};
 std::sort(enemy.begin(),enemy.end(),[&](auto a,auto b){const auto av=splashValue(o,side_,*a),bv=splashValue(o,side_,*b);return av>bv||(av==bv&&(a->hp<b->hp||(a->hp==b->hp&&a->id<b->id)));});
 auto anchor=enemy.front();for(auto e:enemy)if(std::any_of(own.begin(),own.end(),[&](auto g){return reachable(*g,*e);})){anchor=e;break;}
 std::sort(own.begin(),own.end(),[](auto a,auto b){return a->id<b->id;});
 for(auto g:own){
  auto target=std::find_if(enemy.begin(),enemy.end(),[&](auto e){return reachable(*g,*e);});
  auto d=base_.decide(o,g->id);GunFocus record;record.p12=d;record.reachable=target!=enemy.end();
  if(target!=enemy.end())d.target=(*target)->id;
  const auto focus=target!=enemy.end()?*target:anchor;
  const double dx=g->x-focus->x,dy=g->y-focus->y,distance=std::hypot(dx,dy);
  const double preferred=std::max(g->minRange,g->range-SpacingProbeV1::marginPx);
  const double nx=distance>0?dx/distance:1,ny=distance>0?dy/distance:0;
  d.x=focus->x+preferred*nx;d.y=focus->y+preferred*ny;d.multiplier=std::abs(distance-preferred)>1e-9?1:0;d.stop=0;
  auto& a=record.geometry;a.id=g->id;a.focus=focus->id;a.x=g->x;a.y=g->y;a.bx=d.x;a.by=d.y;a.multiplier=d.multiplier;a.minRange=g->minRange;a.range=g->range;
  for(auto n:own)if(n->id!=g->id){const double dx=g->x-n->x,dy=g->y-n->y,distance=std::hypot(dx,dy);if(distance<60){++a.neighbours;const double nx=distance>0?dx/distance:(g->id<n->id?-1:1),ny=distance>0?dy/distance:0;a.sx+=(60-distance)*nx;a.sy+=(60-distance)*ny;a.coincident+=distance==0;}}
  d.x+=a.sx;d.y+=a.sy;a.gx=d.x;a.gy=d.y;a.cx=std::clamp(d.x,0.0,o.width);a.cy=std::clamp(d.y,0.0,o.height);a.radial=std::hypot(d.x-focus->x,d.y-focus->y);
  record.target=d.target;record.anchor=anchor->id;record.anchorValue=splashValue(o,side_,*anchor);record.focusValue=splashValue(o,side_,*focus);record.command=d;
  for(auto e:enemy)if(e->id==d.target)record.targetValue=splashValue(o,side_,*e);
  guns_.push_back(record);actions_.emplace(g->id,d);
 }
}
UnitDecision EscortProbeV3::decide(const Observation& o,UnitId id){auto i=actions_.find(id);return i==actions_.end()?base_.decide(o,id):i->second;}
Controller* p12Base(Controller* c){auto* e=dynamic_cast<EscortProbeV3*>(c);return e?&e->baseline():c;}
Controller* probeBaseV3(Controller* c){return probeBase(p12Base(c));}
}
