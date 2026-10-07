#include "../s4_escort_probe_v3/escort.h"
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

void compareUnchanged(Observation o,int arm){
 EscortProbeV1 p12(7,0,{},12);EscortProbeV3 v3(7,0,{},arm);
 for(int tick=0;tick<3;++tick){
  p12.prepare(o);v3.prepare(o);auto points=meleeEscortPoints(o,0);
  for(auto u:o.units)if(u.hp>0&&u.team==0){
   auto b=p12.decide(o,u.id),a=v3.decide(o,u.id);
   if(arm==16&&u.role!=ObservedRole::Artillery)assert(eq(a,b));
   if(arm==17){assert(a.target==b.target&&a.controllerFailure==b.controllerFailure);auto it=std::find_if(points.begin(),points.end(),[&](auto p){return p.id==u.id;});
    if(it==points.end()||!it->direction)assert(eq(a,b));else {assert(a.x==it->clipX&&a.y==it->clipY&&a.multiplier==(std::hypot(u.x-a.x,u.y-a.y)>2?1:0)&&a.stop==0);}}
   auto clone=v3.clone();assert(eq(a,clone->decide(o,u.id)));
  }
  o.t+=o.dt;
 }
 // Phase exit and rejected integration cannot retain stale actions.
 o.units.erase(std::remove_if(o.units.begin(),o.units.end(),[](auto u){return u.team==1&&u.role==ObservedRole::Artillery;}),o.units.end());o.t+=o.dt;p12.prepare(o);v3.prepare(o);
 for(auto u:o.units)if(u.team==0&&u.hp>0)assert(eq(p12.decide(o,u.id),v3.decide(o,u.id)));
}
int main(){
 historicalPrepareFixture();Observation o;o.width=1400;o.height=800;o.dt=1./30;
 // Higher V wins despite higher HP; exact radius boundary includes victim.
 o.units={unit(1,0,ObservedRole::Artillery,500,400),unit(2,0,ObservedRole::Ranged,560,400),unit(3,0,ObservedRole::Melee,540,400),unit(11,1,ObservedRole::Artillery,800,400,100),unit(12,1,ObservedRole::Artillery,800,500,10),unit(13,1,ObservedRole::Ranged,849,400)};
 assert(splashValue(o,0,o.units[3])==2&&splashValue(o,0,o.units[4])==1);
 EscortProbeV3 p16(7,0,{},16);EscortProbeV1 p12(7,0,{},12);p16.prepare(o);p12.prepare(o);assert(p16.decide(o,1).target==11&&p12.decide(o,1).target==12);
 assert(p16.gunAudit()[0].geometry.focus==11&&p16.gunAudit()[0].geometry.bx==492);compareUnchanged(o,16);compareUnchanged(o,17);
 o.units[5].x=849.0001;assert(splashValue(o,0,o.units[3])==1);p16.prepare(o);assert(p16.decide(o,1).target==12);
 o.units[4].hp=100;p16.prepare(o);assert(p16.decide(o,1).target==11); // equal V/HP -> id
 o.units[5].hp=0;assert(splashValue(o,0,o.units[3])==1);
 // Gun coincidence/radial zero, P11 pre-spacing multiplier, no reachable target.
 o.units={unit(1,0,ObservedRole::Artillery,500,400),unit(2,0,ObservedRole::Artillery,500,400),unit(3,0,ObservedRole::Melee,540,400),unit(11,1,ObservedRole::Artillery,808,400)};
 p16.prepare(o);p12.prepare(o);assert(p16.decide(o,1).multiplier==0&&p16.decide(o,1).x==440);assert(eq(p16.decide(o,1),p12.decide(o,1)));assert(eq(p16.decide(o,2),p12.decide(o,2)));
 o.units[3].x=500;p16.prepare(o);assert(p16.gunAudit()[0].geometry.bx==808);compareUnchanged(o,16);
 // Union-reachable anchor precedes unreachable larger footprint; inclusive min/max.
 o.units={unit(1,0,ObservedRole::Artillery,500,400),unit(2,0,ObservedRole::Artillery,0,400),unit(11,1,ObservedRole::Artillery,820,400),unit(12,1,ObservedRole::Artillery,1000,400),unit(13,1,ObservedRole::Ranged,1000,400)};
 p16.prepare(o);assert(p16.decide(o,1).target==11&&p16.gunAudit()[1].geometry.focus==11);
 o.units[0].minRange=320;p16.prepare(o);assert(p16.gunAudit()[0].reachable);o.units[0].minRange=320.0001;p16.prepare(o);assert(!p16.gunAudit()[0].reachable&&p16.gunAudit()[0].geometry.focus==12);
 // Melee ties, zero vectors, native clipping and exact2 tolerance use same helper.
 o.units={unit(1,0,ObservedRole::Artillery,1390,400),unit(2,0,ObservedRole::Melee,1398,400),unit(3,0,ObservedRole::Ranged,1200,400),unit(11,1,ObservedRole::Artillery,1400,400)};
 auto point=meleeEscortPoints(o,0)[0];assert(point.rawX==1450&&point.clipX==1400);EscortProbeV3 p17(7,0,{},17);p17.prepare(o);assert(p17.decide(o,2).multiplier==0);o.units[1].x=1397.999;p17.prepare(o);assert(p17.decide(o,2).multiplier==1);compareUnchanged(o,17);
 o.units[0].x=1400;o.units[1].x=1400;assert(meleeEscortPoints(o,0)[0].direction==0);compareUnchanged(o,17);
 o.units[0].hp=0;compareUnchanged(o,17);
 // A rejected integration after an active tick must clear every override.
 for(int arm:{16,17}){EscortProbeV1 b(7,0,{},12);EscortProbeV3 e(7,0,{},arm);o.units[0].hp=100;o.units[0].x=1390;o.dt=1./30;b.prepare(o);e.prepare(o);o.t+=o.dt;o.dt=-1;b.prepare(o);e.prepare(o);assert(!b.base().lastTick().accepted);for(auto u:o.units)if(u.team==0&&u.hp>0)assert(eq(b.decide(o,u.id),e.decide(o,u.id)));}
 o.dt=1./30;
 // Clone continues through subsequent prepares with copied state.
 o.units[0].hp=100;o.units[0].x=1390;p17.prepare(o);auto clone=p17.clone();o.t+=o.dt;p17.prepare(o);clone->prepare(o);for(auto u:o.units)if(u.team==0&&u.hp>0)assert(eq(p17.decide(o,u.id),clone->decide(o,u.id)));
 std::cout<<"PASS v3 prepare-only: exact P12, splash footprint inclusive/dead/HP/id, reach/anchor/global fallback, radial/spacing coincidence, pre-spacing multiplier, melee-only movement, clip/error/degenerate/phase fallthrough, stateful clone\n";
}
