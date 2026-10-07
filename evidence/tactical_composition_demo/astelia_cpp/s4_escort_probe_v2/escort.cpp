#include "escort.h"
#include <algorithm>
namespace astelia::control {
namespace {
bool phase(const Observation& o,uint8_t side){bool own=false,enemy=false;for(const auto& u:o.units)if(u.hp>0&&u.role==ObservedRole::Artillery)(u.team==side?own:enemy)=true;return own&&enemy;}
bool reach(const ObservedUnit& a,const ObservedUnit& b){return std::hypot(a.x-b.x,a.y-b.y)<=a.range+a.radius+b.radius;}
}
UnitId escortThreatTarget(const Observation& o,uint8_t side,const ObservedUnit& self){
 const ObservedUnit* best=nullptr;double nearest=0;
 for(const auto& e:o.units)if(e.hp>0&&e.team!=side&&e.role==ObservedRole::Ranged&&reach(self,e)){
  bool threatens=false;for(const auto& g:o.units)if(g.hp>0&&g.team==side&&g.role==ObservedRole::Artillery&&reach(e,g)){threatens=true;break;}
  if(!threatens)continue;
  const double d=std::hypot(self.x-e.x,self.y-e.y);
  if(!best||d<nearest||(d==nearest&&e.id<best->id)){best=&e;nearest=d;}
 }
 return best?best->id:0;
}
std::pair<double,double> escortShift(const Observation& o,uint8_t side,const ObservedUnit& self){
 std::vector<const ObservedUnit*> others;
 for(const auto& u:o.units)if(u.hp>0&&u.team==side&&u.role==ObservedRole::Ranged&&u.id!=self.id)others.push_back(&u);
 std::sort(others.begin(),others.end(),[](auto a,auto b){return a->id<b->id;});double sx=0,sy=0;
 for(auto u:others){const double dx=self.x-u->x,dy=self.y-u->y,d=std::hypot(dx,dy);if(d<58){sx+=(58-d)*(d>0?dx/d:(self.id<u->id?-1:1));sy+=(58-d)*(d>0?dy/d:0);}}
 return {sx,sy};
}
std::vector<EscortPoint> escortPointsV2(const Observation& o,uint8_t side,int arm){
 auto points=escortPoints(o,side,60);
 if(arm==15)for(auto& p:points)if(p.direction){const auto u=std::find_if(o.units.begin(),o.units.end(),[&](const auto& u){return u.id==p.id;});const auto s=escortShift(o,side,*u);p.rawX+=s.first;p.rawY+=s.second;p.clipX=std::clamp(p.rawX,0.0,o.width);p.clipY=std::clamp(p.rawY,0.0,o.height);}
 return points;
}
void EscortProbeV2::prepare(const Observation& o){
 base_.prepare(o);actions_.clear();if(!base_.base().lastTick().accepted||!phase(o,side_))return;
 if(arm_==14){for(const auto& u:o.units)if(u.hp>0&&u.team==side_&&u.role==ObservedRole::Ranged){auto target=escortThreatTarget(o,side_,u);if(target){auto d=base_.decide(o,u.id);d.target=target;actions_.emplace(u.id,d);}}}
 else for(const auto& p:escortPointsV2(o,side_,arm_))if(p.direction){auto d=base_.decide(o,p.id);d.x=p.clipX;d.y=p.clipY;d.multiplier=std::hypot(p.x-d.x,p.y-d.y)>2?1:0;d.stop=0;actions_.emplace(p.id,d);}
}
UnitDecision EscortProbeV2::decide(const Observation& o,UnitId id){auto i=actions_.find(id);return i==actions_.end()?base_.decide(o,id):i->second;}
Controller* p12Base(Controller* c){auto* e=dynamic_cast<EscortProbeV2*>(c);return e?&e->baseline():c;}
Controller* probeBaseV2(Controller* c){return probeBase(p12Base(c));}
}
