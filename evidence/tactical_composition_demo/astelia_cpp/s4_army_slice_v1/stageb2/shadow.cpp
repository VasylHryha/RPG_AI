#include "shadow.h"
#include "a0_oracle.h"
#include "controller_bridge.h"
#include "geometry.h"
#include <set>
namespace stageb {
using namespace astelia;
namespace {
std::unique_ptr<react_v1::Controller> oracle;
std::unique_ptr<World> offline;
js::V cmd(const react_v1::Command& c){return js::obj({{"target",double(c.movement.target)},{"goal",js::arr({c.movement.x,c.movement.y})},{"multiplier",c.movement.multiplier},{"stop",c.movement.stop},{"fire",c.fire==react_v1::FireIntent::Hold?"hold":c.fire==react_v1::FireIntent::Release?"release":"automatic"},{"aim",c.hasAim?js::arr({c.aim.x,c.aim.y}):js::V(nullptr)}});}
js::V label(World& w,react_v1::Snapshot snapshot){
 if(!oracle)throw std::logic_error("oracle not reset");
 w.controllers[0]=std::move(oracle);w.controllers[1].reset();
 auto& c=*static_cast<react_v1::Controller*>(w.controllers[0].get());
 c.snapshot(std::move(snapshot));c.prepare(c.snapshot().units);
 for(auto i:w.active)if(w.units[i].team==0){w.state[i].castOk=true;react_v1::decide(w,i);}
 react_v1::constrainPrep(w);
 for(auto i:w.active)if(w.units[i].team==0)gamePrep(w,i,w.dt*w.state[i].timeRate);
 army_a0::geometry(w);
 js::Args labels;
 for(auto& p:c.records()){const auto& v=p.second;labels.push_back(js::obj({{"id",double(v.id)},{"role",v.role},{"executed",cmd(v.executed)},{"raw",cmd(v.stageRaw)},{"ready",v.ready},{"active",v.active},{"winner",v.winner},{"engineRelease",double(v.engineRelease)}}));}
 c.shape.audit.clear();oracle.reset(static_cast<react_v1::Controller*>(w.controllers[0].release()));
 return js::arr(std::move(labels));
}
std::vector<double> nums(js::V v){std::vector<double> a;for(auto x:v.p->items){double n=js::num(x);if(!std::isfinite(n))throw std::invalid_argument("nonfinite shadow snapshot");a.push_back(n);}return a;}
}
void reset(World& w,js::V){
 oracle=std::make_unique<react_v1::Controller>(w.config->seed,0,w.config->controllers[0].params,control::V7Selector::P16);oracle->shape.arm="O";
}
void shadow(World& w){
 auto* c=dynamic_cast<react_v1::Controller*>(w.controllers[0].get());if(!c||!c->stage.shadow)return;
 // Only this branch gets O commands. No coreStep, no action or RNG transfer back.
 World copy(w.config);copy.copyFrom(w);copy.work=std::make_shared<WorkCounters>();
 c->stage.shadowLabels=label(copy,react_v1::observe(w,0));
}
js::V replay(js::V request){
 auto init=js::get(request,"request");if(init.tag!=js::V::Undefined){
  auto config=std::make_shared<const Config>(shapes_v6::configuration(init));
  offline=std::make_unique<World>(shapes_v6::create(config,init));reset(*offline,init);
 }
 if(!offline)throw std::invalid_argument("oracle replay reset required");
 auto row=js::get(request,"frame");World& w=*offline;react_v1::Snapshot s;
 auto& o=s.units;o.t=js::num(js::get(row,"t"));o.dt=js::num(js::get(row,"dt"));o.width=js::num(js::get(row,"width"));o.height=js::num(js::get(row,"height"));w.time=o.t;w.dt=o.dt;
 w.active.clear();std::map<UnitId,uint32_t> slots;
 for(uint32_t i=0;i<w.units.size();++i){slots[w.units[i].id]=i;w.units[i].alive=false;}
 for(auto v:js::get(row,"units").p->items){auto a=nums(v);if(a.size()!=23||!slots.count(UnitId(a[0])))throw std::invalid_argument("shadow unit schema");
  auto i=slots.at(UnitId(a[0]));auto& u=w.units[i];auto& st=w.state[i];u.alive=true;w.active.push_back(i);
  u.pos={a[3],a[4]};u.velocity={a[5],a[6]};u.hp=a[7];u.maxhp=a[8];u.radius=a[9];u.speed=a[10];u.range=a[11];u.damage=a[12];u.cooldown=a[13];u.target=a[15]?w.reference(slots.at(UnitId(a[15]))):UnitRef{};
  st.cooldownMax=a[14];st.damageDealt=a[16];st.damageTaken=a[17];st.minRange=a[18];st.dealtToEnemy=a[19];st.takenFromEnemy=a[20];st.friendlyDealt=a[21];st.friendlyTaken=a[22];st.longVelocity=u.velocity;
  o.units.push_back({u.id,u.team,ObservedRole(uint8_t(a[2])),a[3],a[4],a[5],a[6],a[7],a[8],a[9],a[10],a[11],a[12],a[13],a[14],UnitId(a[15]),a[16],a[17],a[18],a[19],a[20],a[21],a[22]});
 }
 ++w.membershipVersion;w.rebuildTeams();w.shells.clear();
 for(auto v:js::get(row,"own").p->items){auto a=nums(v);auto i=slots.at(UnitId(a[0]));auto& st=w.state[i];st.guardUntil=a[1];st.prep=a[2];st.windup=a[3];st.timeRate=a[4];st.energy=a[5];st.cost=a[6];st.lobSpeed=a[8]*100;st.launch=1;st.splash=a[9]*100;
  s.own.push_back({UnitId(a[0]),a[1],a[2],a[3],a[4],a[5],a[6],bool(a[7])});s.stageGuns[UnitId(a[0])]={a[8]*100,a[9]*100};
 }
 for(auto v:js::get(row,"shells").p->items){auto a=nums(v);if(a[7]==1)s.shells.push_back({{a[0]*o.width,a[1]*o.height},{a[2]*o.width,a[3]*o.height},o.t+a[4],a[5]*100,bool(a[6])});
  for(auto i:w.active)if(w.units[i].team==a[7]){Shell sh;sh.pos={a[0]*o.width,a[1]*o.height};sh.source=w.reference(i);sh.at=o.t+a[4];sh.splash=a[5]*100;sh.slow=a[6];sh.damage=a[8]*100;w.shells.push_back(sh);break;}
 }
 for(auto v:js::get(row,"shots").p->items){auto a=nums(v);s.shots.push_back({{a[0]*o.width,a[1]*o.height},{a[2],a[3]},o.t-a[4],a[5]*100,a[6]*100});}
 for(auto v:js::get(row,"fields").p->items){auto a=nums(v);s.fields.push_back({{a[0]*o.width,a[1]*o.height},a[2]*100,o.t+a[3],o.t+a[4]});}
 for(auto v:js::get(row,"casts").p->items){auto a=nums(v);s.casts.push_back({UnitId(a[0]*256),UnitId(a[1]*256),{a[2]*o.width,a[3]*o.height},o.t+a[4],o.t+a[5],a[6]*100});}
 auto labels=label(w,std::move(s));return js::obj({{"shadowLabels",labels},{"combat_steps",0},{"reconstruction","public_snapshot; singleton aim uses velocity instead of unrecorded longVelocity"}});
}
}
