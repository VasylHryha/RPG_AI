#include "s4_volley_probe_v1.h"
#include <algorithm>
#include <functional>
namespace astelia::control {
namespace {
bool reach(const ObservedUnit&a,const ObservedUnit&b){double d=std::hypot(a.x-b.x,a.y-b.y);return d>=a.minRange&&d<=a.range;}
}
void VolleyProbeV1::prepare(const Observation&o){
 S4V6Controller::prepare(o);if(arm_==0||!lastTick_.accepted)return;
 std::vector<const ObservedUnit*> guns,enemies;
 for(auto&u:o.units)if(u.hp>0&&u.role==ObservedRole::Artillery)(u.team==side_?guns:enemies).push_back(&u);
 auto byId=[](auto a,auto b){return a->id<b->id;};std::sort(guns.begin(),guns.end(),byId);std::sort(enemies.begin(),enemies.end(),byId);
 if(enemies.empty()){chosen_=0;wait_=-1;releaseUntil_=-1;assignments_.clear();return;} // baseline finishes non-guns
 auto target=std::find_if(enemies.begin(),enemies.end(),[&](auto e){return e->id==chosen_;});
 if(target==enemies.end()||std::none_of(guns.begin(),guns.end(),[&](auto g){return reach(*g,**target);})){int best=-1;chosen_=0;
  for(auto e:enemies){int n=0;for(auto g:guns)n+=reach(*g,*e);if(n>best){best=n;chosen_=e->id;}}
  wait_=-1;releaseUntil_=-1;assignments_.clear();target=std::find_if(enemies.begin(),enemies.end(),[&](auto e){return e->id==chosen_;});}
 const auto center=*target;std::vector<const ObservedUnit*> eligible,ready;
 for(auto g:guns)if(reach(*g,*center)){eligible.push_back(g);if(g->cd<=0)ready.push_back(g);}
 if(o.t>=releaseUntil_){assignments_.clear();if(eligible.empty())wait_=-1;else if(wait_<0)wait_=o.t;
  // Net = chosen gun and its two closest living gun neighbours (distance, ID ties).
  auto adjacent=enemies;std::stable_sort(adjacent.begin(),adjacent.end(),[&](auto a,auto b){double da=std::hypot(a->x-center->x,a->y-center->y),db=std::hypot(b->x-center->x,b->y-center->y);return da<db||(da==db&&a->id<b->id);});if(adjacent.size()>3)adjacent.resize(3);
  std::map<UnitId,UnitId> matched;std::map<UnitId,const ObservedUnit*> owners;
  std::function<bool(const ObservedUnit*,std::set<UnitId>&)> augment=[&](const ObservedUnit*g,std::set<UnitId>&seen){for(auto e:adjacent)if(reach(*g,*e)&&seen.insert(e->id).second){if(!owners.count(e->id)||augment(owners[e->id],seen)){owners[e->id]=g;return true;}}return false;};
  for(auto g:ready){std::set<UnitId> seen;augment(g,seen);}for(auto&pair:owners)matched[pair.second->id]=pair.first;
  const bool sufficient=arm_==1?ready.size()>=3:matched.size()>=3;
  const bool expired=wait_>=0&&o.t-wait_>=1.5-1e-9;
  if(!ready.empty()&&(sufficient||expired)){
   if(arm_==1)for(auto g:eligible)assignments_[g->id]=center->id;
   else {assignments_=matched;for(auto g:eligible)if(!assignments_.count(g->id)){auto e=std::find_if(adjacent.begin(),adjacent.end(),[&](auto e){return reach(*g,*e);});if(e!=adjacent.end())assignments_[g->id]=(*e)->id;}}
   releaseUntil_=o.t+.8;wait_=-1;
  }
 }
 for(auto g:guns){auto&d=prepared_.at(g->id);d.target=assignments_.count(g->id)?assignments_.at(g->id):0;}
 // P3: park every direct (ranged) unit while >=4 enemy guns live. Inside-band
 // starts retreat to the nearest safe 20-px grid point; no state teleportation.
 if(arm_==3&&enemies.size()>=4)for(auto&u:o.units)if(u.hp>0&&u.team==side_&&u.role==ObservedRole::Ranged){
  auto safe=[&](double x,double y){for(auto e:enemies){double d=std::hypot(x-e->x,y-e->y);if(d>=std::max(0.0,e->minRange-12)&&d<=e->range+12)return false;}return true;};
  auto&d=prepared_.at(u.id);const auto originalTarget=d.target;d={u.x,u.y,0,0,originalTarget};if(!safe(u.x,u.y)){double best=INFINITY;
   auto safePath=[&](double x,double y){for(auto e:enemies){double initial=std::hypot(u.x-e->x,u.y-e->y);if(initial<=e->range+12&&initial>=std::max(0.0,e->minRange-12))continue;
    double dx=x-u.x,dy=y-u.y,len=dx*dx+dy*dy;double f=len>0?std::clamp(((e->x-u.x)*dx+(e->y-u.y)*dy)/len,0.0,1.0):0;
    double near=std::hypot(u.x+f*dx-e->x,u.y+f*dy-e->y);double far=std::max(initial,std::hypot(x-e->x,y-e->y));if(near<=e->range+12&&far>=std::max(0.0,e->minRange-12))return false;}return true;};
   for(double x=u.radius;x<=o.width-u.radius;x+=20)for(double y=u.radius;y<=o.height-u.radius;y+=20)if(safe(x,y)&&safePath(x,y)){double r=std::hypot(x-u.x,y-u.y);if(r<best){best=r;d={x,y,1,0,originalTarget};}}}
 }
}
}
