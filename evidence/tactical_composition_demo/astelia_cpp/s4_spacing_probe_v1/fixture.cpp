#include "spacing.h"
#include "s4_focus_probe_v1.h"
#include <cassert>
#include <iostream>
using namespace astelia::control;
ObservedUnit unit(unsigned id,int team,ObservedRole role,double x,double y,double hp=181){ObservedUnit u;u.id=id;u.team=team;u.role=role;u.x=x;u.y=y;u.hp=u.maxhp=hp;u.range=320;u.minRange=80;u.radius=10;u.speed=55;u.cdMax=1.2;return u;}
bool equal(UnitDecision a,UnitDecision b){return a.x==b.x&&a.y==b.y&&a.multiplier==b.multiplier&&a.stop==b.stop&&a.target==b.target;}
void verify(Observation o,int arm){
 FocusProbeV1 base(7,0,{},5);SpacingProbeV1 shifted(7,0,{},arm);base.prepare(o);shifted.prepare(o);
 for(const auto& u:o.units)if(u.team==0&&u.hp>0){
  auto b=base.decide(o,u.id),a=shifted.decide(o,u.id);
  if(u.role!=ObservedRole::Artillery){assert(equal(a,b));continue;}
  double sx=0,sy=0;
  for(const auto& v:o.units)if(v.hp>0&&v.team==0&&v.role==ObservedRole::Artillery&&v.id!=u.id){double x=u.x-v.x,y=u.y-v.y,d=std::hypot(x,y),S=arm==10?100:60;if(d<S){sx+=(S-d)*(d>0?x/d:(u.id<v.id?-1:1));sy+=(S-d)*(d>0?y/d:0);}}
  assert(std::abs(a.x-b.x-sx)<1e-9&&std::abs(a.y-b.y-sy)<1e-9);assert(a.target==b.target&&a.multiplier==b.multiplier&&a.stop==b.stop);
 }
 auto clone=shifted.clone();for(const auto& u:o.units)if(u.team==0&&u.hp>0)assert(equal(clone->decide(o,u.id),shifted.decide(o,u.id)));
}
int main(){
 Observation o;o.width=1400;o.height=800;o.dt=1./30;
 o.units={unit(1,0,ObservedRole::Artillery,100,300),unit(2,0,ObservedRole::Artillery,120,300),unit(3,0,ObservedRole::Artillery,100,340),unit(4,0,ObservedRole::Artillery,100,301,0),unit(5,0,ObservedRole::Ranged,101,300),unit(11,1,ObservedRole::Artillery,500,300)};
 verify(o,10);verify(o,11);
 o.units[1].x=o.units[0].x;o.units[1].y=o.units[0].y;verify(o,10);verify(o,11);
 // Exact preferred radius preserves zero multiplier despite a crowded battery.
 o.units.resize(2);o.units[0]=unit(1,0,ObservedRole::Artillery,808,300);o.units[1]=unit(2,0,ObservedRole::Artillery,788,300);o.units.push_back(unit(11,1,ObservedRole::Artillery,500,300));
 SpacingProbeV1 zero(7,0,{},10);zero.prepare(o);auto z=zero.decide(o,1);assert(z.multiplier==0&&z.x==888);assert(zero.audit()[0].radial==388);
 o.units[0].x=809;verify(o,10);verify(o,11);SpacingProbeV1 range(7,0,{},10);range.prepare(o);assert(range.audit()[0].radial>320);
 // Native goal clipping is recorded, never baked into the controller action.
 o.width=820;SpacingProbeV1 clipped(7,0,{},10);clipped.prepare(o);assert(clipped.audit()[0].gx>o.width&&clipped.audit()[0].cx==o.width);
 // Threshold equality contributes no term; dead guns do not count.
 o.units[0].x=100;o.units[1].x=200;verify(o,10);o.units[1].hp=0;verify(o,11);
 o.units.back().hp=0;FocusProbeV1 base(7,0,{},5);SpacingProbeV1 gone(7,0,{},10);base.prepare(o);gone.prepare(o);assert(gone.audit().empty());assert(equal(base.decide(o,1),gone.decide(o,1)));
 o.units.clear();SpacingProbeV1 empty(7,0,{},11);empty.prepare(o);assert(empty.audit().empty());
 std::cout<<"PASS prepare-only: exact P5 targets/multiplier/stop, simultaneous sum, dose, dead/self filtering, coincidence, clone, range conflict, zero multiplier, clipping audit, threshold and v6 fallthrough\n";
}
