// Synthetic observations only. Never call coreStep(), fight() or create().
#include "a0_oracle.h"
#include "shapes.h"
#include "controller_bridge.h"
#include "geometry.h"
#include <iostream>
#include <stdexcept>
using namespace astelia;
void require(bool x,const char* message){if(!x)throw std::runtime_error(message);}
struct GroupCheck{bool joint=false;unsigned eligible=0,applied=0;std::vector<Vec2> aims;};
GroupCheck group(const std::string& arm,unsigned ready){
 auto config=std::make_shared<Config>(gameConfig());config->width=1400;config->height=800;config->abilities=false;
 World w(config);w.dt=1.0/30;
 auto g1=w.add(0,Role::Artillery,{200,360}),g2=w.add(0,Role::Artillery,{200,440});
 auto e=w.add(1,Role::Artillery,{750,400});w.add(1,Role::Ranged,{710,430});
 for(auto ref:{g1,g2}){auto& u=w.units[ref.slot];auto& st=w.state[ref.slot];u.range=600;u.speed=10;st.minRange=100;st.windup=.2;st.prep=0;st.cost=0;st.energy=100;}
 auto controller=std::make_unique<react_v1::Controller>(1,0,ControllerParams{},control::V7Selector::P16);
 auto* c=controller.get();c->shape.arm=arm;w.controllers[0]=std::move(controller);
 auto snap=react_v1::observe(w,0);c->snapshot(snap);w.observations[0]=snap.units;c->prepare(snap.units);
 for(auto ref:{g1,g2})react_v1::decide(w,ref.slot);
 army_a0::geometry(w);
 for(const auto& row:c->shape.audit)require(!js::truth(js::get(row,"a0Event")),"no event before native preparation");
 // Manually cross the native prepared boundary, without advancing combat or
 // refreshing the 5 Hz base proposal. Geometry must see this physical event.
 w.state[g1.slot].prep=ready>=1?.2:0;w.state[g2.slot].prep=ready>=2?.2:0;
 army_a0::geometry(w);GroupCheck out;unsigned count=0;
 for(const auto& row:c->shape.audit)if(js::truth(js::get(row,"a0Event"))){++count;
  out.joint=js::truth(js::get(row,"joint"));out.eligible=unsigned(js::num(js::get(row,"eligible")));out.applied=unsigned(js::num(js::get(row,"applied")));}
 require(count==(ready?1:0),"one event per physical ready set");
 for(auto ref:{g1,g2}){const auto* cmd=c->command(w.units[ref.slot].id);if(cmd->hasAim)out.aims.push_back(cmd->aim);}
 const auto before=*c->command(w.units[g1.slot].id);
 require(!army_a0::applyAim(w,*c,w.units[g1.slot].id,{-1,400}),"illegal group point rejected");
 const auto after=*c->command(w.units[g1.slot].id);
 require(after.hasAim==before.hasAim&&distance(after.aim,before.aim)==0&&after.movement.target==before.movement.target,"rejected aim falls back without changing autonomous action");
 return out;
}
int main(){try{
 control::Observation o;o.t=0;o.dt=1.0/30;o.width=1400;o.height=800;
 control::ObservedUnit g;g.id=1;g.team=0;g.role=ObservedRole::Artillery;g.x=200;g.y=400;g.hp=g.maxhp=100;g.range=600;g.minRange=100;g.radius=10;
 auto r=g;r.id=2;r.role=ObservedRole::Ranged;r.range=100;r.minRange=0;r.x=250;
 auto e=g;e.id=3;e.team=1;e.x=700;
 auto enemy=r;enemy.id=4;enemy.team=1;enemy.x=650;
 o.units={g,r,e,enemy};
 auto raw=army_a0::oracle(o,0);require(raw.size()==2,"full unit oracle");
 auto projected=react_v1::participate(o,r.id,raw.at(r.id));
 require(std::hypot(projected.x-raw.at(r.id).x,projected.y-raw.at(r.id).y)>1,"escort must be participation-projected");
 react_v1::Snapshot s;s.units=o;s.own={{1,0,0,.2,1,100,0,false},{2,0,0,.2,1,100,0,false}};
 s.shots.push_back({{200,400},{1,0},-1,300,200});
 react_v1::Controller c(1,0,{},control::V7Selector::P16);c.shape.arm="O";c.snapshot(s);c.prepare(o);
 auto before=*c.command(2);require(c.records().at(2).active,"shot reaction present");
 auto commanded=before;commanded.movement.x=900;commanded.movement.y=700;commanded.fire=react_v1::FireIntent::Release;
 c.submit(2,commanded);auto after=*c.command(2);
 require(after.fire==react_v1::FireIntent::Hold&&after.movement.x==before.movement.x&&after.movement.y==before.movement.y,"react overrides present command");
 s.shots.clear();s.own[1].busy=true;c.snapshot(s);c.prepare(o);before=*c.command(2);c.submit(2,commanded);
 require(c.command(2)->fire==react_v1::FireIntent::Hold,"body precedence");
 react_v1::Controller a(1,0,{},control::V7Selector::P16),b(1,0,{},control::V7Selector::P16);
 a.shape.arm="O";b.shape.arm="O+G";s.own[1].busy=false;a.snapshot(s);b.snapshot(s);a.prepare(o);b.prepare(o);
 for(auto id:{1u,2u})require(a.command(id)->movement.x==b.command(id)->movement.x&&a.command(id)->movement.target==b.command(id)->movement.target,"empty group command parity");
 auto first=a.a0Base.at(2);s.units.t=.1;s.units.units[3].x=900;a.snapshot(s);a.prepare(s.units);
 require(a.a0Base.at(2).x==first.x,"5Hz cached base");
 s.units.t=.21;a.snapshot(s);a.prepare(s.units);require(a.a0NextBase>.4,"5Hz refresh");
 s.units.units[2].hp=0;s.units.units[3].hp=0;s.units.t=.22;a.snapshot(s);a.prepare(s.units);require(a.command(2)->movement.target==0,"dead-target invalidation before cadence");
 auto empty=group("O+G",0);require(empty.applied==0&&!empty.joint,"empty command no-op");
 auto singleO=group("O",1),singleG=group("O+G",1);require(singleO.eligible==1&&!singleG.joint&&singleO.applied>0,"single event autonomous");
 require(singleO.aims.size()==singleG.aims.size(),"single point count parity");
 for(size_t i=0;i<singleO.aims.size();++i)require(distance(singleO.aims[i],singleG.aims[i])<1e-12,"single point parity");
 auto multiO=group("O",2),multiG=group("O+G",2);
 require(multiO.eligible==2&&!multiO.joint&&multiG.joint&&multiG.applied>0,"multi event joint routing");
 std::cout<<"A0_FIXTURE_PASS no fights\n";return 0;
}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}
