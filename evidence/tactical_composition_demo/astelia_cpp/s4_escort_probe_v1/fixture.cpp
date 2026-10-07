#include "escort.h"
#include <cassert>
#include <algorithm>
#include <iostream>
using namespace astelia::control;
ObservedUnit unit(unsigned id,int team,ObservedRole role,double x,double y,double hp=100){ObservedUnit u;u.id=id;u.team=team;u.role=role;u.x=x;u.y=y;u.hp=u.maxhp=hp;u.range=role==ObservedRole::Artillery?320:259;u.radius=role==ObservedRole::Artillery?10:9;u.speed=55;u.cdMax=1.2;return u;}
bool eq(UnitDecision a,UnitDecision b){return a.x==b.x&&a.y==b.y&&a.multiplier==b.multiplier&&a.stop==b.stop&&a.target==b.target&&a.controllerFailure==b.controllerFailure;}
void verify(Observation o){
 for(int arm:{12,13}){
  SpacingProbeV1 base(7,0,{},11);EscortProbeV1 e(7,0,{},arm);base.prepare(o);e.prepare(o);
  auto points=escortPoints(o,0,arm==12?60:120);
  for(auto u:o.units)if(u.team==0&&u.hp>0){
   auto a=e.decide(o,u.id),b=base.decide(o,u.id);assert(a.target==b.target);
   auto p=std::find_if(points.begin(),points.end(),[&](auto p){return p.id==u.id;});
   if(p==points.end()||!p->direction)assert(eq(a,b));
   else {assert(a.x==p->clipX&&a.y==p->clipY&&a.stop==0);assert(a.multiplier==(std::hypot(u.x-a.x,u.y-a.y)>2?1:0));}
  }
  auto clone=e.clone();for(auto u:o.units)if(u.team==0&&u.hp>0)assert(eq(e.decide(o,u.id),clone->decide(o,u.id)));
  // Stateful sequential prepare/clone: baseline continues identical gun decisions.
  o.t+=o.dt;e.prepare(o);base.prepare(o);for(auto u:o.units)if(u.team==0&&u.hp>0&&u.role!=ObservedRole::Ranged)assert(eq(e.decide(o,u.id),base.decide(o,u.id)));
 }
}
int main(){
 Observation o;o.width=1400;o.height=800;o.dt=1./30;
 o.units={unit(2,0,ObservedRole::Artillery,500,400),unit(1,0,ObservedRole::Artillery,560,400),unit(3,0,ObservedRole::Ranged,530,400),unit(4,0,ObservedRole::Melee,500,450),unit(12,1,ObservedRole::Artillery,1000,400),unit(11,1,ObservedRole::Ranged,700,400)};
 verify(o);auto p=escortPoints(o,0,60)[0];assert(p.gun==1&&p.direction==1&&p.rawX==620); // own tie lowest id
 o.units[2].x=500;verify(o);p=escortPoints(o,0,60)[0];assert(p.gun==2&&p.rawX==560); // raw point coincides with other gun; no correction
 o.units.push_back(unit(10,1,ObservedRole::Ranged,300,400));p=escortPoints(o,0,60)[0];assert(p.threat==10&&p.rawX==440); // enemy tie lowest id
 o.units.back().hp=0;p=escortPoints(o,0,60)[0];assert(p.threat==11);
 o.units[5].x=900;p=escortPoints(o,0,60)[0];assert(p.threat==11); // inclusive400
 o.units[5].x=900.0001;p=escortPoints(o,0,60)[0];assert(p.direction==2);
 o.units[5].x=500;p=escortPoints(o,0,60)[0];assert(p.direction==2);verify(o); // coincident ranged
 o.units[4].x=500;p=escortPoints(o,0,60)[0];assert(p.direction==0);verify(o);
 o.units[4].x=400;o.units.push_back(unit(13,1,ObservedRole::Artillery,600,400));p=escortPoints(o,0,60)[0];assert(p.direction==3&&p.rawX==440);verify(o); // centroid zero, nearest tie
 o.units[4].hp=0;o.units.back().hp=0;assert(escortPoints(o,0,60).empty());verify(o);
 // Clipping uses raw point; error tolerance exact2; no body-inset repair.
 o.units={unit(1,0,ObservedRole::Artillery,1390,400),unit(3,0,ObservedRole::Ranged,1398,400),unit(12,1,ObservedRole::Artillery,1400,400)};
 p=escortPoints(o,0,60)[0];assert(p.rawX==1450&&p.clipX==1400);verify(o);
 EscortProbeV1 e(7,0,{},12);e.prepare(o);assert(e.decide(o,3).multiplier==0);o.units[1].x=1397.999;e.prepare(o);assert(e.decide(o,3).multiplier==1);
 o.units[0].hp=0;assert(escortPoints(o,0,60).empty());verify(o);
 std::cout<<"PASS prepare-only: exact P11 gun/melee, v6 target, doses, dead units, assignment/threat ties, inclusive400, ordered centroid, coincident/degenerate fallback, shared/other-gun collision, clip, exact2 tolerance, clone and sequential fallthrough\n";
}
