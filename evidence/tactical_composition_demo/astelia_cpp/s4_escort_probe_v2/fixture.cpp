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
int historicalPrepareFixture(){
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
 return 0;
}
void overlayCheck(Observation o){
 for(int arm:{14,15}){
  EscortProbeV1 p12(7,0,{},12);EscortProbeV2 v2(7,0,{},arm);
  for(int tick=0;tick<3;++tick){
   p12.prepare(o);v2.prepare(o);const bool active=p12.base().lastTick().accepted&&!escortPoints(o,0,60).empty();auto points=escortPointsV2(o,0,arm);
   for(const auto& u:o.units)if(u.hp>0&&u.team==0){
    auto expected=p12.decide(o,u.id),actual=v2.decide(o,u.id);
    if(active&&u.role==ObservedRole::Ranged){
     if(arm==14){auto target=escortThreatTarget(o,0,u);if(target)expected.target=target;}
     else {auto p=std::find_if(points.begin(),points.end(),[&](auto q){return q.id==u.id;});if(p->direction){expected.x=p->clipX;expected.y=p->clipY;expected.multiplier=std::hypot(u.x-expected.x,u.y-expected.y)>2?1:0;expected.stop=0;}}
    }
    assert(eq(actual,expected));auto clone=v2.clone();assert(eq(clone->decide(o,u.id),actual));
   }
   o.t+=o.dt;
  }
 }
}
int main(){
 historicalPrepareFixture();
 Observation o;o.width=1400;o.height=800;o.dt=1./30;
 o.units={unit(1,0,ObservedRole::Artillery,500,400),unit(2,0,ObservedRole::Ranged,560,400),unit(3,0,ObservedRole::Ranged,560,400),unit(4,0,ObservedRole::Melee,560,410),unit(11,1,ObservedRole::Artillery,1000,400),unit(13,1,ObservedRole::Ranged,700,400),unit(12,1,ObservedRole::Ranged,420,400)};
 assert(escortThreatTarget(o,0,o.units[1])==12); // self-distance tie, lowest id
 auto a=escortShift(o,0,o.units[1]),b=escortShift(o,0,o.units[2]);assert(a.first==-58&&a.second==0&&b.first==58);overlayCheck(o);
 // Multiple terms from current centres, input permutation cannot change sum.
 o.units[2].x=570;o.units.push_back(unit(5,0,ObservedRole::Ranged,560,410));a=escortShift(o,0,o.units[1]);assert(a.first==-48&&a.second==-48);overlayCheck(o);
 std::reverse(o.units.begin(),o.units.end());overlayCheck(o);
 // strict58 cutoff and dead neighbours.
 o.units={unit(1,0,ObservedRole::Artillery,500,400),unit(2,0,ObservedRole::Ranged,560,400),unit(3,0,ObservedRole::Ranged,618,400),unit(11,1,ObservedRole::Artillery,1000,400)};
 assert(escortShift(o,0,o.units[1]).first==0);o.units[2].x=560;o.units[2].hp=0;assert(escortShift(o,0,o.units[1]).first==0);overlayCheck(o);
 // P14 reaches any gun, not just assigned gun; inclusive range, outside direction400.
 o.units={unit(1,0,ObservedRole::Artillery,0,400),unit(2,0,ObservedRole::Ranged,500,400),unit(3,0,ObservedRole::Artillery,1000,400),unit(11,1,ObservedRole::Artillery,1300,400),unit(12,1,ObservedRole::Ranged,777,400)};
 assert(escortThreatTarget(o,0,o.units[1])==12);o.units[4].x=777.0001;assert(escortThreatTarget(o,0,o.units[1])==0);overlayCheck(o);
 // All direction vectors zero; targeting still applies, P15 complete P12.
 o.units={unit(1,0,ObservedRole::Artillery,500,400),unit(2,0,ObservedRole::Ranged,500,400),unit(3,0,ObservedRole::Ranged,500,400),unit(11,1,ObservedRole::Artillery,500,400),unit(12,1,ObservedRole::Ranged,500,400)};
 assert(escortPoints(o,0,60)[0].direction==0);EscortProbeV2 p14(7,0,{},14);p14.prepare(o);assert(p14.decide(o,2).target==12);overlayCheck(o);
 o.units[3].hp=0;overlayCheck(o);o.units[3].hp=100;o.units[0].hp=0;overlayCheck(o);
 // Shift RAW point before clipping (raw1450-58=1392, not clipped1400-58).
 o.units={unit(1,0,ObservedRole::Artillery,1390,400),unit(2,0,ObservedRole::Ranged,1390,400),unit(3,0,ObservedRole::Ranged,1390,400),unit(11,1,ObservedRole::Artillery,1400,400)};
 auto ps=escortPointsV2(o,0,15);assert(ps[0].rawX==1392&&ps[0].clipX==1392);EscortProbeV2 p15(7,0,{},15);p15.prepare(o);assert(p15.decide(o,2).multiplier==0);overlayCheck(o);
 o.units[1].x=1389.999;overlayCheck(o);
 // Sequential phase exit clears prepared overrides; rejected integration clears too.
 EscortProbeV1 base(7,0,{},12);EscortProbeV2 e(7,0,{},15);base.prepare(o);e.prepare(o);o.t+=o.dt;o.units[3].hp=0;base.prepare(o);e.prepare(o);for(auto u:o.units)if(u.team==0&&u.hp>0)assert(eq(base.decide(o,u.id),e.decide(o,u.id)));
 std::cout<<"PASS v2 prepare-only: exact P12 reuse, single-field target change, movement-only spacing, ordered simultaneous sum, strict58, id coincidence, inclusive reach/any gun, preclip order, degenerate/phase/dead fallthrough, clone\n";
}
