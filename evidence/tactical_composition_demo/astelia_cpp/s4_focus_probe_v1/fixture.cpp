#include "native/s4_focus_probe_v1.h"
#include <cassert>
#include <iostream>
using namespace astelia::control;
ObservedUnit u(unsigned id,int team,ObservedRole role,double x,double y,double hp=181){ObservedUnit a;a.id=id;a.team=team;a.role=role;a.x=x;a.y=y;a.hp=hp;a.maxhp=181;a.range=320;a.minRange=80;a.radius=10;a.speed=55;a.cdMax=1.2;return a;}
bool equal(UnitDecision a,UnitDecision b){return a.x==b.x&&a.y==b.y&&a.multiplier==b.multiplier&&a.stop==b.stop&&a.target==b.target&&a.controllerFailure==b.controllerFailure;}
bool movement(UnitDecision a,UnitDecision b){a.target=b.target;return equal(a,b);}
int main(){
 Observation o;o.dt=1.0/30;o.width=1400;o.height=800;
 o.units={u(1,0,ObservedRole::Artillery,300,300),u(2,0,ObservedRole::Artillery,200,350),u(3,0,ObservedRole::Artillery,50,600),u(4,0,ObservedRole::Ranged,180,300),u(5,0,ObservedRole::Melee,100,150),u(11,1,ObservedRole::Artillery,550,300,90),u(12,1,ObservedRole::Artillery,550,346,90),u(13,1,ObservedRole::Artillery,330,300,1),u(15,1,ObservedRole::Ranged,180,600)};
 // Gun1 excludes closest gun13 inside minRange; HP tie picks11. Gun2 reaches13; gun3 keeps a soft target.
 S4V6Controller base(77,0,{});FocusProbeV1 p4(77,0,{},4),p5(77,0,{},5),p6(77,0,{},6);
 for(auto c:{static_cast<Controller*>(&base),static_cast<Controller*>(&p4),static_cast<Controller*>(&p5),static_cast<Controller*>(&p6)})c->prepare(o);
 assert(p4.decide(o,1).target==11&&p4.decide(o,2).target==13);
 assert(base.decide(o,3).target==15&&equal(p4.decide(o,3),base.decide(o,3)));
 for(unsigned id:{1,2,3})assert(movement(p4.decide(o,id),base.decide(o,id)));
 for(unsigned id:{4,5})assert(equal(p4.decide(o,id),base.decide(o,id))&&equal(p5.decide(o,id),base.decide(o,id)));
 for(unsigned id:{1,2,3}){
  auto a=p5.decide(o,id);auto target=id==1?o.units[5]:o.units[7];assert(std::abs(std::hypot(a.x-target.x,a.y-target.y)-308)<1e-9&&a.multiplier==1&&a.stop==0);assert(a.target==p4.decide(o,id).target);
 }
 assert(p6.decide(o,4).target==13&&movement(p6.decide(o,4),base.decide(o,4))&&equal(p6.decide(o,5),base.decide(o,5)));
 // Direct native reach includes both radii; cooldown does not suppress focus; P6 fallback outside reach.
 o.units[3].range=130;o.units[0].cd=2;o.t+=o.dt;base.prepare(o);p6.prepare(o);assert(p6.decide(o,4).target==13&&p6.decide(o,1).target==11);
 o.units[3].x=179;o.t+=o.dt;base.prepare(o);p6.prepare(o);assert(equal(p6.decide(o,4),base.decide(o,4)));
 // No reachable enemy gun: P5 approaches weakest overall but P4/P5 retain all v6 targets.
 for(auto& a:o.units)if(a.team==1&&a.role==ObservedRole::Artillery)a.x=1200;
 o.t+=o.dt;base.prepare(o);p4.prepare(o);p5.prepare(o);for(unsigned id:{1,2,3})assert(p4.decide(o,id).target==base.decide(o,id).target&&p5.decide(o,id).target==base.decide(o,id).target);
 auto a=p5.decide(o,1);assert(std::abs(std::hypot(a.x-1200,a.y-300)-308)<1e-9);auto copy=p5.clone();assert(equal(copy->decide(o,1),a));
 // All enemy guns dead: full baseline actions, including movement.
 for(auto& a:o.units)if(a.team==1&&a.role==ObservedRole::Artillery)a.hp=0;
 o.t+=o.dt;base.prepare(o);p4.prepare(o);p5.prepare(o);p6.prepare(o);for(unsigned id:{1,2,3,4,5})assert(equal(p4.decide(o,id),base.decide(o,id))&&equal(p5.decide(o,id),base.decide(o,id))&&equal(p6.decide(o,id),base.decide(o,id)));
 // Boundary: inclusive gun min/max reach and coincident position is finite.
 Observation edge;edge.dt=o.dt;edge.width=1400;edge.height=800;edge.units={u(1,0,ObservedRole::Artillery,300,300),u(11,1,ObservedRole::Artillery,380,300),u(12,1,ObservedRole::Artillery,620,300,1)};
 FocusProbeV1 boundary(77,0,{},4);boundary.prepare(edge);assert(boundary.decide(edge,1).target==12);edge.units[2].x=620.01;edge.t+=edge.dt;boundary.prepare(edge);assert(boundary.decide(edge,1).target==11);
 edge.units.resize(2);edge.units[1].x=300;FocusProbeV1 coincident(77,0,{},5);coincident.prepare(edge);a=coincident.decide(edge,1);assert(std::isfinite(a.x)&&std::isfinite(a.y)&&a.x==608&&a.y==300);
 std::cout<<"PASS: independent HP focus, id tie, min/max reach, cooldown no-hold, soft fallback, radial commit, native direct gap, no-gun baseline, clone, finite coincident goal\n";
}
