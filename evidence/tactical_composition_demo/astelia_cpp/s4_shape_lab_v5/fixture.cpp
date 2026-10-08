// Hand-built states and command/preparation seams only. Never coreStep/fights.
#include "react.h"
#include "timing.h"
#include "artillery.h"
#include "controller_bridge.h"
#include "geometry.h"
#include <iostream>
using namespace astelia;
using namespace battery_v1;
namespace {
unsigned checks=0;
void check(bool p,const char* message){++checks;if(!p)throw std::runtime_error(message);}
void near(double a,double b,const char* msg){check(std::abs(a-b)<1e-10,msg);}
void equations(){
 Battery b;b.k=1;b.radius=200;b.states[1].phi=.3;b.states[2].phi=1.2;b.states[3].phi=2;
 std::vector<Gun> g={{1,{0,0},4,false,true},{2,{100,0},8,false,true},{3,{400,0},3,false,true}};
 b.step(g,.001,.001);near(b.states[1].phi,.3+.001*(tau/4+std::sin(.9)/4),"normalized local equation i");
 near(b.states[2].phi,1.2+.001*(tau/8+std::sin(-.9)/8),"synchronous equation j");near(b.states[3].phi,2+.001*tau/3,"isolated gun omega");
 check(b.states[1].neighbours==1&&b.states[3].neighbours==0,"radius excludes remote/self");
 Battery inf;inf.radius=INFINITY;inf.states[1].phi=.3;inf.states[2].phi=1.2;inf.states[3].phi=2;inf.step(g,.001,.001);
 near(inf.states[1].phi,.3+.001*(tau/4+(std::sin(.9)+std::sin(1.7))/8),"infinity mean normalization");
 b.step({g[0]},.002,.001);check(b.states.size()==1&&b.states[1].neighbours==0,"dead guns removed; single gun decouples");
 Battery one;one.states[1].phi=tau-.01;auto r=one.step({{1,{0,0},4,true,true}},.02,.02);check(r[1],"single gun ready crossing");
 check(one.states[1].phi!=0,"reset is not request time");one.fired(1);near(one.states[1].phi,0,"actual launch reset");check(one.states[1].waiting==-1,"release clears hold timer");
 one.states[1].phi=tau-.01;r=one.step({{1,{0,0},4,false,true}},.04,.02);check(!r[1],"unready crossing not released");
 r=one.step({{1,{0,0},4,true,true}},.06,.02);check(!r[1],"crossing not queued from unready step");
 one.states[1].phi=tau-.01;r=one.step({{1,{0,0},4,true,false}},.08,.02);check(!r[1],"illegal crossing vetoed");
 one.states[1].waiting=0;one.states[1].phi=1;r=one.step({{1,{0,0},4,true,true}},4,.001);check(r[1]&&one.states[1].reason=="one_cycle_bound","bound ready gun one cycle");
 one.states[1].waiting=0;r=one.step({{1,{0,0},4,true,false}},5,.001);check(!r[1],"bound never overrides legality");
 r=one.step({{1,{0,0},4,true,true}},5.001,.001);check(r[1],"overdue releases at next legal tick");
 auto clone=one;clone.fired(1);check(one.states[1].phi!=clone.states[1].phi,"battery copy independent");
}
// Exact engine waves block evaluated on recorded state (no coreStep).
bool engineWaves(World& w,uint32_t i){auto& s=w.state[i];const auto& sk=w.config->skills[w.units[i].team];const auto* t=w.resolve(w.units[i].target);
 if(sk.waves>0&&!(s.prep>0)&&w.units[i].cooldown<=0&&s.inReach&&t&&t->alive&&s.energy>=s.cost&&windup(w,i)>0){
 uint32_t n=0;for(auto j:w.teams[w.units[i].team])if(w.units[j].alive&&w.state[j].inReach&&w.units[j].cooldown<=0&&!(w.state[j].prep>0)&&w.state[j].windup>0)++n;
 auto& ts=w.tactical[i];if(ts.waitFrom<0)ts.waitFrom=w.time;if(n<sk.waves&&w.time-ts.waitFrom<1)return false;else ts.waitFrom=-1;}
 return true;}
void centralStates(js::V input){for(auto row:js::get(input,"states").p->items){auto c=std::make_shared<Config>(gameConfig());c->abilities=false;c->skills[0].holdSync=.5;c->skills[0].waves=3;
 World w(c);w.time=js::num(js::get(row,"time"));auto enemy=w.add(1,Role::Ranged,{550,400});
 auto cds=js::get(row,"cooldowns").p->items;auto prep=js::get(row,"preps").p->items;auto reach=js::get(row,"reach").p->items;
 for(size_t n=0;n<cds.size();++n){auto gun=w.add(0,Role::Artillery,{350,380+20*double(n)});w.units[gun.slot].target=enemy;w.units[gun.slot].cooldown=js::num(cds[n]);w.state[gun.slot].prep=js::num(prep[n]);w.state[gun.slot].inReach=js::truth(reach[n]);w.tactical[gun.slot].waitFrom=js::num(js::get(row,"waitFrom"));}
 w.rebuildTeams();w.packs[0].enabled=true;const auto until=js::num(js::get(row,"cachedUntil"));if(until>0){w.packs[0].gateTime=w.time;w.packs[0].gateUntil=until;}
 World oracle(c);oracle.copyFrom(w);
 for(auto i:w.teams[0]){check(copiedFireGate(w,i)==fireGate(oracle,i),"central gate oracle parity");near(w.packs[0].gateUntil,oracle.packs[0].gateUntil,"central cached hold parity");check(copiedWaves(w,i)==engineWaves(oracle,i),"waves ready/timeout parity");near(w.tactical[i].waitFrom,oracle.tactical[i].waitFrom,"waves timer parity");}
}}
void requestConstruction(js::V root){for(auto req:js::get(root,"requests").p->items){auto config=std::make_shared<Config>(battery_v1::configuration(req));auto w=battery_v1::create(config,req);check(dynamic_cast<react_v1::Controller*>(w.controllers[0].get())!=nullptr,"request reaches adapter");check(w.time==0,"construct request no simulation");}}
void adapterSeam(js::V root){control::ControllerParams p;for(auto key:js::keys(js::get(root,"selected_params")))p[js::str(key)]=js::num(js::get(js::get(root,"selected_params"),key));
 auto c=std::make_shared<Config>(gameConfig());c->abilities=false;World w(c);w.time=1;w.dt=1./30;
 auto gun=w.add(0,Role::Artillery,{350,400});auto target=w.add(1,Role::Ranged,{550,400});w.rebuildTeams();w.units[gun.slot].target=target;
 w.controllers[0]=std::make_unique<react_v1::Controller>(7,0,p,control::V7Selector::P16);auto* ctl=dynamic_cast<react_v1::Controller*>(w.controllers[0].get());ctl->battery.mode=2;
 react_v1::prepare(w);prepareControllers(w);react_v1::decide(w,gun.slot);w.state[gun.slot].prep=w.state[gun.slot].windup;w.state[gun.slot].inReach=true;
 ctl->battery.states[w.units[gun.slot].id].phi=1;ctl->battery.states[w.units[gun.slot].id].waiting=0;
 w.time=w.state[gun.slot].cooldownMax+w.state[gun.slot].windup+1;
 oscillator(w);check(ctl->command(w.units[gun.slot].id)->fire==react_v1::FireIntent::Release,"bounded oscillator reaches command adapter");
 auto cmd=*ctl->command(w.units[gun.slot].id);check(cmd.movement.target==w.units[target.slot].id,"P16 target preserved");check(cmd.hasAim&&cmd.aim.x==550&&cmd.aim.y==400,"P16 aim preserved");
 fired(w,gun.slot);near(ctl->battery.states.at(w.units[gun.slot].id).phi,0,"engine launch callback reset");
 auto invalid=cmd;invalid.aim.x=NAN;bool rejected=false;try{ctl->submit(w.units[gun.slot].id,invalid);}catch(const std::invalid_argument&){rejected=true;}check(rejected,"adapter illegal aim rejected");
 auto cloned=ctl->clone();auto* copy=dynamic_cast<react_v1::Controller*>(cloned.get());copy->battery.states.at(w.units[gun.slot].id).phi=3;check(ctl->battery.states.at(w.units[gun.slot].id).phi==0,"native clone preserves independent battery state");
}
}
int main(){try{auto root=js::parse(std::string(std::istreambuf_iterator<char>(std::cin),{}));equations();centralStates(js::get(root,"central_states"));adapterSeam(root);requestConstruction(root);std::cout<<"{\"status\":\"PASS\",\"assertions\":"<<checks<<",\"fights\":0}\n";return 0;}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}
