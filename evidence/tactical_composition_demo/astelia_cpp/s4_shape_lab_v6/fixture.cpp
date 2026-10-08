// Persisted value-only planner states and isolated unit seams. Never coreStep.
#include "shapes.h"
#include "react.h"
#include "controller_bridge.h"
#include "geometry.h"
#include <iostream>
using namespace astelia;
using namespace shapes_v6;
namespace {
unsigned checks=0;
void check(bool p,const char* m){++checks;if(!p)throw std::runtime_error(m);}
void near(double a,double b,const char* m){check(std::abs(a-b)<1e-8,m);}
control::ObservedUnit observed(UnitId id,uint8_t team,Vec2 p){control::ObservedUnit u;u.id=id;u.team=team;u.role=ObservedRole::Ranged;u.x=p.x;u.y=p.y;u.hp=u.maxhp=90;u.radius=9;u.range=280;u.speed=100;u.dmg=18;u.cdMax=1.4;return u;}
react_v1::Snapshot sample(){react_v1::Snapshot s;s.units.t=0;s.units.dt=1.0/30;s.units.width=1400;s.units.height=800;s.units.units={observed(1,0,{400,400}),observed(2,0,{350,400}),observed(101,1,{650,400})};s.units.units[0].target=101;s.units.units[1].target=101;s.own={{1,0,0,.55,1,100,6,false},{2,0,0,.55,1,100,6,false}};return s;}
void movement(){auto s=sample();auto d=UnitDecision{100,400,1,0,101};s.units.units[0].x=200;
 auto e=floor(s,1,d,false);near(e.x,650-(280+18-1),"E1 real body gap and inside margin");check(e.target==101&&e.stop==0&&e.multiplier==1,"E1 selector unchanged");
 near(floor(s,1,d,true).x,d.x,"reaction precedes floor");s.own[0].prep=.2;near(floor(s,1,d,false).x,d.x,"committed attack precedes floor");s.own[0].prep=0;s.own[0].guardUntil=1;near(floor(s,1,d,false).x,d.x,"body/terminal precedes floor");s.own[0].guardUntil=0;auto invalid=d;invalid.controllerFailure=true;near(floor(s,1,invalid,false).x,d.x,"failure precedes floor");
 s.units.units[0].x=400;near(floor(s,1,d,false).x,d.x,"in reach inherits move without kiting");s.units.units[0].role=ObservedRole::Melee;near(floor(s,1,d,false).x,d.x,"melee unchanged");s.units.units[0].role=ObservedRole::Ranged;
 s.units.units[0].x=900;s.units.units[0].y=700;s.units.units[2].x=8;s.units.units[2].y=8;auto edge=floor(s,1,d,false);auto copy=s.units.units[0];copy.x=edge.x;copy.y=edge.y;check(edge.x>=copy.radius&&edge.y>=copy.radius&&reach(copy,s.units.units[2]),"floor legal at arena corner");
}
void aimLegality(){auto s=sample();auto& u=s.units.units[0];u.role=ObservedRole::Artillery;u.range=320;s.units.dt=1.0/30;UnitDecision moving{300,400,1,0,101};
 check(!legalAim(s.units,1,moving,{720,400}),"planner at range edge falls back rather than delaying fire after inherited move");
 check(legalAim(s.units,1,moving,{700,400}),"planner aim legal before and after inherited move");
 u.x=100;check(!legalAim(s.units,1,moving,{-1,400}),"planner out-of-arena aim falls back");}
void rotation(){auto s=sample();UnitDecision base{400,400,0,0,101};s.threats.push_back({{500,400},{},1,0,110,120});
 auto r=rotate(s,1,base);check(r.active&&r.base>=90&&r.candidate<90,"lethal base trajectory and safe candidate");check(distance(r.point,{400,400})<=retreatMax&&r.point.x<350,"bounded behind friend retreat");check(r.participation=="next_legal_shot"&&r.nextShot<=participationHorizon,"participation horizon includes movement/windup");
 auto reacting=base;reacting.x=420;reacting.multiplier=1;check(damage(s,1,reacting)>=90&&rotate(s,1,reacting).active,"post-react lethal counterfactual");reacting.x=300;check(damage(s,1,reacting)<90&&!rotate(s,1,reacting).active,"successful reaction prevents extraction");
 s.threats[0].damage=80;check(!rotate(s,1,base).active,"HP threshold alone does not trigger");s.threats[0].damage=120;s.own[0].prep=.2;check(!rotate(s,1,base).active,"committed own cast kept");s.own[0].prep=0;s.units.units[1].x=150;check(!rotate(s,1,base).active,"no remote friend / edge-running");
 s=sample();for(auto& u:s.units.units)u.y=20;s.threats={{{500,20},{},1,0,110,120}};check(!rotate(s,1,base).active,"edge friend cannot draw unit to edge");
 s=sample();s.threats={{{500,400},{},1,0,110,120}};s.own[0].windup=1.15;auto horizon=rotate(s,1,base);check(horizon.active&&horizon.participation=="nearest_bounded_survival", "windup after re-entry, not during retreat");
 s=sample();s.threats={{{500,400},{},1,0,110,120}};s.own[0].energy=0;check(!rotate(s,1,base).active,"unknown own energy readiness fails closed");s.regeneration[1]=20;auto energy=rotate(s,1,base);check(energy.active&&energy.participation=="next_legal_shot", "own public regeneration participates");
 s=sample();s.threats={{ {500,400},{},1,0,110,120}};s.units.units[0].range=30;s.units.units[0].speed=100;auto fallback=rotate(s,1,base);check(fallback.active&&fallback.participation=="nearest_bounded_survival","bounded survival fallback when no participating point");
 s=sample();s.threats={{ {500,400},{},1,0,110,120}};s.protection[1]=.5;check(!rotate(s,1,base).active,"own visible protection avoids false lethal");
 s=sample();s.threats={{{600,400},{-1,0},0,0,3,120,200,400,0,true,false}};check(damage(s,1,base)>=90,"continuous shot intersection");auto dodge=base;dodge.y=500;dodge.multiplier=1;check(damage(s,1,dodge)<90,"same shot on reachable dodge trajectory");
 s=sample();s.threats={{{400,400},{},1,.6,40,120,0,0,1,false,true}};auto away=base;away.x=300;away.multiplier=1;check(damage(s,1,away)>=90,"committed target cast tracks until release");
}
void planner(js::V states){for(auto row:states.p->items){PlannerInput in;in.units.t=js::num(js::get(row,"t"));in.units.width=1400;in.units.height=800;for(auto g:js::get(row,"guns").p->items){const auto id=UnitId(js::num(js::get(g,"id")));auto u=observed(id,0,{js::num(js::get(g,"x")),js::num(js::get(g,"y"))});u.role=ObservedRole::Artillery;u.hp=u.maxhp=181;u.radius=10;u.range=320;u.target=UnitId(js::num(js::get(g,"target")));in.units.units.push_back(u);in.guns.push_back({id,u.target,js::num(js::get(g,"windup")),js::num(js::get(g,"lob")),js::num(js::get(g,"splash")),js::truth(js::get(g,"ready"))});}
 for(auto e:js::get(row,"enemies").p->items){auto u=observed(UnitId(js::num(js::get(e,"id"))),1,{js::num(js::get(e,"x")),js::num(js::get(e,"y"))});u.hp=js::num(js::get(e,"hp"));u.vx=js::num(js::get(e,"vx"));u.vy=js::num(js::get(e,"vy"));in.units.units.push_back(u);}
 auto engine=project(in);auto copy=project(in);artilleryVolley(engine,0);copiedPlanner(copy,0);auto planned=copy.packs[0].artilleryQueue;check(!planned.empty(),"recorded planner state activates");check(engine.shells.size()==planned.size(),"planner-copy engine shell count parity");
 for(size_t i=0;i<planned.size();++i){const auto& q=planned[i];const auto& sh=engine.shells[i];check(copy.units[q.gun.slot].id==engine.units[sh.source.slot].id,"planner assignment parity");near(q.point.x,sh.pos.x,"planner x parity");near(q.point.y,sh.pos.y,"planner y parity");near(q.prediction,sh.prediction,"planner score parity");check(q.family==sh.family&&q.variant==sh.variant,"planner family parity");near(q.at,in.units.t,"no geometry timing change");}
 // A projection has only fixed assumptions, public records and its own seed.
 check(engine.random.state==1&&!engine.config->skills[0].rollout.enabled,"no enemy RNG/clone rollout");check(std::none_of(planned.begin(),planned.end(),[&](const PlannedShot& q){return !in.guns[q.gun.slot].eligible;}),"unready guns excluded");
 }}
void requests(js::V payload){for(auto req:js::get(payload,"requests").p->items){auto cfg=std::make_shared<Config>(configuration(req));auto w=create(cfg,req);react_v1::prepare(w);battery_v1::prepareDummies(w);prepareControllers(w);for(auto i:w.active)if(w.controllers[w.units[i].team])react_v1::decide(w,i);check(w.time==0,"request boundary zero fights");}}
}
int main(){try{std::string input;std::getline(std::cin,input);auto p=js::parse(input);movement();aimLegality();rotation();planner(js::get(p,"planner_states"));requests(p);std::cout<<js::stringify(js::obj({{"status","PASS"},{"checks",double(checks)},{"fights",0},{"scope","recorded planner parity + E1 arbitration/legality + R1 counterfactual/participation/bounded retreat"}}))<<'\n';}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}
