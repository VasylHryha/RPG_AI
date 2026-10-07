#include "s4_focus_probe_v1.h"
#include <algorithm>
namespace astelia::control {
namespace {
bool gunReach(const ObservedUnit& a,const ObservedUnit& b){const double d=std::hypot(a.x-b.x,a.y-b.y);return d>=a.minRange&&d<=a.range;}
bool directReach(const ObservedUnit& a,const ObservedUnit& b){return std::hypot(a.x-b.x,a.y-b.y)-a.radius-b.radius<=a.range;}
}
void FocusProbeV1::prepare(const Observation& o){
 S4V6Controller::prepare(o);if(!lastTick_.accepted)return;
 std::vector<const ObservedUnit*> guns,enemies;
 for(const auto& u:o.units)if(u.hp>0&&u.role==ObservedRole::Artillery)(u.team==side_?guns:enemies).push_back(&u);
 if(enemies.empty())return;
 std::sort(enemies.begin(),enemies.end(),[](auto a,auto b){return a->hp<b->hp||(a->hp==b->hp&&a->id<b->id);});
 // Shared anchor for approach and P6. Per-gun legal focus remains P4's rule.
 auto anchor=enemies.front();
 for(auto e:enemies)if(std::any_of(guns.begin(),guns.end(),[&](auto g){return gunReach(*g,*e);})){anchor=e;break;}
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
  }
 }
 if(arm_==6)for(const auto& u:o.units)if(u.hp>0&&u.team==side_&&u.role==ObservedRole::Ranged&&directReach(u,*anchor))prepared_.at(u.id).target=anchor->id;
}
}
