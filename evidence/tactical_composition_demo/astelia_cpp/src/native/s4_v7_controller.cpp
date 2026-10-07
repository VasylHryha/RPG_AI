#include "s4_v7_controller.h"
#include <algorithm>
namespace astelia::control {
bool v7Mode(double c,bool previous,bool initialized){
 if(!initialized)return c>=0;
 return c>.2?true:c<-.2?false:previous;
}
void S4V7Controller::prepare(const Observation& o){
 // The inherited prepared_ map is never overwritten by overlays.
 S4V6Controller::prepare(o);actions_.clear();choices_.clear();guns_.clear();
 std::set<UnitId> living;
 for(const auto& u:o.units)if(u.hp>0&&u.team==side_)living.insert(u.id);
 for(auto it=modes_.begin();it!=modes_.end();)if(!living.count(it->first))it=modes_.erase(it);else ++it;
 if(!lastTick_.accepted)return;
 std::map<UnitId,UnitDecision> overlay;
 for(auto id:living)overlay[id]=baseline(o,id);
 for(const auto& p:escortPoints(o,side_,60))if(p.direction){auto d=baseline(o,p.id);d.x=p.clipX;d.y=p.clipY;d.multiplier=std::hypot(p.x-d.x,p.y-d.y)>2?1:0;d.stop=0;overlay[p.id]=d;}
 std::vector<const ObservedUnit*> own,enemy;
 for(const auto& u:o.units)if(u.hp>0&&u.role==ObservedRole::Artillery)(u.team==side_?own:enemy).push_back(&u);
 if(!own.empty()&&!enemy.empty()){
 auto reachable=[](const auto& a,const auto& b){const double d=std::hypot(a.x-b.x,a.y-b.y);return d>=a.minRange&&d<=a.range;};
 std::sort(enemy.begin(),enemy.end(),[&](auto a,auto b){const auto av=splashValue(o,side_,*a),bv=splashValue(o,side_,*b);return av>bv||(av==bv&&(a->hp<b->hp||(a->hp==b->hp&&a->id<b->id)));});
 auto anchor=enemy.front();for(auto e:enemy)if(std::any_of(own.begin(),own.end(),[&](auto g){return reachable(*g,*e);})){anchor=e;break;}
 std::sort(own.begin(),own.end(),[](auto a,auto b){return a->id<b->id;});
 for(auto g:own){
  auto target=std::find_if(enemy.begin(),enemy.end(),[&](auto e){return reachable(*g,*e);});
  auto d=baseline(o,g->id);GunFocus record;record.p12=d;record.reachable=target!=enemy.end();
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
  guns_.push_back(record);overlay[g->id]=d;
 }
 }
 for(auto id:living){
  auto old=modes_.find(id);const bool known=old!=modes_.end(),previous=known?old->second:true;
  const bool mode=v7Mode(v6::commitment(complexStates_.at(id)),previous,known);modes_[id]=mode;
  const bool select=selector_==V7Selector::P16||(selector_==V7Selector::Gate&&mode);
  auto b=baseline(o,id),p=overlay.at(id),a=select?p:b;
  actions_[id]=a;choices_.push_back({id,mode,select,known&&mode!=previous,b,p,a});
 }
}
UnitDecision S4V7Controller::decide(const Observation& o,UnitId id){auto it=actions_.find(id);return it==actions_.end()?baseline(o,id):it->second;}
}
