#include "collective.h"
#include "s4_focus_probe_v1.h"
#include <cassert>
#include <iostream>
using namespace astelia::control;
ObservedUnit u(unsigned id,int team,ObservedRole role,double x,double y,double hp=181){ObservedUnit a;a.id=id;a.team=team;a.role=role;a.x=x;a.y=y;a.hp=hp;a.maxhp=181;a.range=320;a.minRange=80;a.radius=10;a.speed=55;a.cdMax=1.2;return a;}
bool equal(UnitDecision a,UnitDecision b){return a.x==b.x&&a.y==b.y&&a.multiplier==b.multiplier&&a.stop==b.stop&&a.target==b.target;}
int main(){
 Observation o;o.dt=1./30;o.width=1400;o.height=800;o.units={u(1,0,ObservedRole::Artillery,100,300),u(2,0,ObservedRole::Artillery,100,350),u(3,0,ObservedRole::Ranged,100,200),u(11,1,ObservedRole::Artillery,550,300,80),u(12,1,ObservedRole::Artillery,550,346,100),u(13,1,ObservedRole::Ranged,350,200)};
 CollectiveProbeV1 p7(77,0,{},7);p7.prepare(o);assert(!p7.probe().wave&&p7.probe().target==11&&p7.decide(o,1).target!=11&&p7.decide(o,1).target!=12);
 for(auto g:p7.probe().guns){assert(g.solved);double nearest=INFINITY;for(auto e:p7.probe().enemies)nearest=std::min(nearest,std::hypot(g.gx-e.x,g.gy-e.y));assert(std::abs(nearest-350)<1e-7);}
 o.t=20.1;p7.prepare(o);assert(p7.probe().wave&&p7.probe().reason=="fallback20s");o.units[0].x=300;o.units[4].hp=1;o.t+=o.dt;p7.prepare(o);assert(p7.probe().target==11&&p7.decide(o,1).target==11);o.units[3].hp=0;o.t+=o.dt;p7.prepare(o);assert(p7.probe().target==12&&p7.probe().waveTime==20.1);
 auto clone=p7.clone();assert(equal(clone->decide(o,1),p7.decide(o,1)));
 // Readiness triggers immediately at the mathematical boundary, without a fallback wait.
 Observation ready=o;ready.units.resize(4);ready.units[3]=u(11,1,ObservedRole::Artillery,550,300);ready.units[0].x=200;ready.units[0].y=300;ready.units[1].x=200;ready.units[1].y=300;ready.t=0;
 CollectiveProbeV1 trigger(77,0,{},7);trigger.prepare(ready);assert(trigger.probe().wave&&trigger.probe().reason=="ready"&&trigger.probe().ready==2);
 // P8 screen replaces ranged movement and picks nearest reachable enemy direct, id ties.
 o.units[3].hp=80;o.units[4].hp=100;o.t=0;CollectiveProbeV1 p8(77,0,{},8);p8.prepare(o);o.t=21;p8.prepare(o);assert(p8.probe().wave&&!p8.probe().escorts.empty());assert(p8.decide(o,3).target==13);auto escort=p8.probe().escorts[0];double cx=(o.units[0].x+o.units[1].x)/2,cy=(o.units[0].y+o.units[1].y)/2;assert(std::abs(std::hypot(escort.gx-cx,escort.gy-cy)-60)<1e-9);
 // P9 picks line end, uses full arc commitment radius and retains acquired axis.
 o.units[4].hp=80;o.units.push_back(u(14,1,ObservedRole::Artillery,550,392,80));o.t=0;CollectiveProbeV1 p9(77,0,{},9);p9.prepare(o);assert(p9.probe().target==11);o.t=21;p9.prepare(o);assert(p9.probe().wave);for(auto g:p9.probe().guns)assert(std::abs(std::hypot(g.px-550,g.py-300)-308)<1e-9);
 for(auto g:p9.probe().guns){assert(std::abs(g.py-146)<1e-8);assert(std::abs(std::abs(g.px-550)-308*std::sin(3.14159265358979323846/3))<1e-8);}
 o.units[4].x=596;o.units[4].y=300;o.units.back().x=642;o.units.back().y=300;o.t=22;p9.prepare(o);assert(p9.probe().target==11);for(auto g:p9.probe().guns)assert(std::abs(g.py-146)<1e-8);
 // Full v6 fallthrough on no enemy guns; no-gun cohort never triggers a wave.
 for(auto& a:o.units)if(a.team==1&&a.role==ObservedRole::Artillery)a.hp=0;S4V6Controller base(77,0,{});CollectiveProbeV1 empty(77,0,{},9);base.prepare(o);empty.prepare(o);for(unsigned id:{1,2,3})assert(equal(base.decide(o,id),empty.decide(o,id)));
 for(auto& a:o.units)if(a.role==ObservedRole::Artillery)a.hp=a.team==1?181:0;CollectiveProbeV1 noGuns(77,0,{},7);noGuns.prepare(o);assert(!noGuns.probe().wave);
 // Single enemy and coincident direction remain finite, with n=1 zero arc offset.
 o.units={u(1,0,ObservedRole::Artillery,550,300),u(11,1,ObservedRole::Artillery,550,300)};o.t=0;CollectiveProbeV1 degenerate(77,0,{},9);degenerate.prepare(o);assert(degenerate.probe().guns.size()==1);auto g=degenerate.probe().guns[0];assert(std::isfinite(g.px)&&g.px==858&&g.py==300);
 std::cout<<"PASS staging outer boundary, target lock/death, timer/readiness, clone, escort, end selection/arc, no-gun fallthrough, degeneracy\n";
}
