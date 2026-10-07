#include "spacing.h"
#include <algorithm>
namespace astelia::control {
namespace {
bool gunReach(const ObservedUnit& a,const ObservedUnit& b){const double d=std::hypot(a.x-b.x,a.y-b.y);return d>=a.minRange&&d<=a.range;}
bool directReach(const ObservedUnit& a,const ObservedUnit& b){return std::hypot(a.x-b.x,a.y-b.y)-a.radius-b.radius<=a.range;}
}
void SpacingProbeV1::prepare(const Observation& o){
 audit_.clear();S4V6Controller::prepare(o);if(!lastTick_.accepted)return;
 std::vector<const ObservedUnit*> guns,enemies;
 for(const auto& u:o.units)if(u.hp>0&&u.role==ObservedRole::Artillery)(u.team==side_?guns:enemies).push_back(&u);
 if(enemies.empty())return;
 std::sort(enemies.begin(),enemies.end(),[](auto a,auto b){return a->hp<b->hp||(a->hp==b->hp&&a->id<b->id);});
 // Shared anchor for approach and P6. Per-gun legal focus remains P4's rule.
 auto anchor=enemies.front();
 for(auto e:enemies)if(std::any_of(guns.begin(),guns.end(),[&](auto g){return gunReach(*g,*e);})){anchor=e;break;}
 std::sort(guns.begin(),guns.end(),[](auto a,auto b){return a->id<b->id;});
 for(auto g:guns){
  auto target=std::find_if(enemies.begin(),enemies.end(),[&](auto e){return gunReach(*g,*e);});
  auto& d=prepared_.at(g->id);
  if(target!=enemies.end())d.target=(*target)->id; // otherwise retain complete v6 target, including soft targets
  if(arm_>=5){
   const auto focus=target!=enemies.end()?*target:anchor;
   const double dx=g->x-focus->x,dy=g->y-focus->y,distance=std::hypot(dx,dy);
   const double preferred=std::max(g->minRange,g->range-marginPx);
   const double nx=distance>0?dx/distance:1,ny=distance>0?dy/distance:0;
   d.x=focus->x+preferred*nx;d.y=focus->y+preferred*ny;
   d.multiplier=std::abs(distance-preferred)>1e-9?1:0;d.stop=0;
   SpacingGun a;a.id=g->id;a.focus=focus->id;a.x=g->x;a.y=g->y;a.bx=d.x;a.by=d.y;a.multiplier=d.multiplier;a.minRange=g->minRange;a.range=g->range;
   for(auto n:guns)if(n->id!=g->id){
    const double dx=g->x-n->x,dy=g->y-n->y,distance=std::hypot(dx,dy);
    if(distance<spacing()){
     ++a.neighbours;const double nx=distance>0?dx/distance:(g->id<n->id?-1:1),ny=distance>0?dy/distance:0;
     a.sx+=(spacing()-distance)*nx;a.sy+=(spacing()-distance)*ny;a.coincident+=distance==0;
    }
   }
   d.x+=a.sx;d.y+=a.sy;a.gx=d.x;a.gy=d.y;
   a.cx=std::max(0.0,std::min(o.width,d.x));a.cy=std::max(0.0,std::min(o.height,d.y));
   a.radial=std::hypot(d.x-focus->x,d.y-focus->y);audit_.push_back(a);
  }
 }
 if(arm_==6)for(const auto& u:o.units)if(u.hp>0&&u.team==side_&&u.role==ObservedRole::Ranged&&directReach(u,*anchor))prepared_.at(u.id).target=anchor->id;
}
}
