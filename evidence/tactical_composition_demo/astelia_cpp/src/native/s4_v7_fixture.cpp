#include "s4_v7_controller.h"
#include <cassert>
#include <cstring>
#include <iostream>
using namespace astelia::control;
bool bits(double a,double b){return std::memcmp(&a,&b,sizeof(a))==0;}
bool eq(UnitDecision a,UnitDecision b){return bits(a.x,b.x)&&bits(a.y,b.y)&&bits(a.multiplier,b.multiplier)&&bits(a.stop,b.stop)&&a.target==b.target&&a.controllerFailure==b.controllerFailure;}
ObservedUnit unit(unsigned id,int team,ObservedRole role,double x,double y){ObservedUnit u;u.id=id;u.team=team;u.role=role;u.x=x;u.y=y;u.hp=u.maxhp=100;u.range=role==ObservedRole::Artillery?320:259;u.radius=role==ObservedRole::Artillery?10:9;u.speed=55;u.cdMax=1.2;return u;}
void state(const S4V6Controller& a,const S4V6Controller& b){
 assert(a.complexStates().size()==b.complexStates().size());
 for(auto [id,z]:a.complexStates()){auto w=b.complexStates().at(id);assert(bits(z.real(),w.real())&&bits(z.imag(),w.imag()));}
 assert(a.pairModes()==b.pairModes()&&a.memory().size()==b.memory().size());
 for(auto [id,m]:a.memory()){auto n=b.memory().at(id);assert(m.target==n.target&&m.hadLegalTarget==n.hadLegalTarget&&m.hadUnansweredThreat==n.hadUnansweredThreat);assert(bits(m.state,n.state)&&bits(m.zOut,n.zOut)&&bits(m.zIn,n.zIn)&&bits(m.lastOut,n.lastOut)&&bits(m.lastIn,n.lastIn)&&bits(m.zInAnswered,n.zInAnswered)&&bits(m.zInUnanswered,n.zInUnanswered));}
 assert(a.argMemory().size()==b.argMemory().size());for(auto [id,m]:a.argMemory()){auto n=b.argMemory().at(id);assert(bits(m.arg,n.arg)&&bits(m.time,n.time)&&m.valid==n.valid);}
 assert(a.retryCount()==b.retryCount()&&a.failureCount()==b.failureCount());
 auto& x=a.lastTick();auto& y=b.lastTick();assert(x.accepted==y.accepted&&x.reason==y.reason&&x.n==y.n&&x.retries==y.retries&&bits(x.Z,y.Z)&&bits(x.maxStageAmplitude,y.maxStageAmplitude));
 assert(a.complexModel().size()==b.complexModel().size());for(size_t i=0;i<a.complexModel().size();++i){const auto& u=a.complexModel()[i];const auto& v=b.complexModel()[i];assert(u.id==v.id&&u.target==v.target&&bits(u.pressure,v.pressure)&&bits(u.omega,v.omega)&&bits(u.z.real(),v.z.real())&&bits(u.z.imag(),v.z.imag()));}
}
struct Inject: S4V7Controller {using S4V7Controller::S4V7Controller;void seed(UnitId id,double c){complexStates_[id]={c,0};lastFiniteStates_[id]={c,0};}};
int main(){
 assert(v7Mode(0,false,false)&&!v7Mode(-.01,true,false));
 for(double c:{-.2,0.,.2}){assert(v7Mode(c,true,true));assert(!v7Mode(c,false,true));}
 assert(v7Mode(.200001,false,true)&&!v7Mode(-.200001,true,true));
 Knobs k;PairModes pairs;auto a=unit(1,0,ObservedRole::Ranged,500,400),e=unit(11,1,ObservedRole::Artillery,800,400);a.range=100;
 v3Preferred(a,e,k,-.5,pairs);v3Preferred(a,e,k,0,pairs);assert(!pairs.at({1,11}));e.id=12;v3Preferred(a,e,k,0,pairs);assert(pairs.at({1,12}));
 // Historical theta, both bound corners, fixed-seed interior point (four vectors).
 const char* names[]={"K","K_t","kappa","beta","G","w","f_c","m_k","lambda_th","mu","omega_ranged"};
 double lows[]={0,0,0,0,0,0,.3,.2,0,-2,-2}, highs[]={5,5,50,3,5,3,1,1,3,2,2};
 double historical[]={3.566896608697073,3.727239438188206,28.18188378050727,.1344978184970619,4.529277505112292,1.8368755705836595,.9115160242941771,.20353322914295716,1.250917647665491,-1.8154310511852993,1.3914459541507074};
 uint32_t rng=20261007;std::vector<ControllerParams> vectors(4);
 for(int i=0;i<11;++i){rng=1664525u*rng+1013904223u;vectors[0][names[i]]=historical[i];vectors[1][names[i]]=lows[i];vectors[2][names[i]]=highs[i];vectors[3][names[i]]=lows[i]+(highs[i]-lows[i])*(double(rng)/4294967296.);}
 for(const auto& p:vectors){
  S4V7Controller commit(7,0,p,V7Selector::P16),escape(7,0,p,V7Selector::V6),gate(7,0,p);S4V6Controller v6(7,0,p);EscortProbeV3 p16(7,0,p,16);
  commit.attributionDiagnostics(true);escape.attributionDiagnostics(true);gate.attributionDiagnostics(true);v6.attributionDiagnostics(true);p16.baseline().base().attributionDiagnostics(true);
  Observation o;o.width=1400;o.height=800;o.dt=1./30;
  o.units={unit(1,0,ObservedRole::Artillery,500,400),unit(2,0,ObservedRole::Artillery,500,400),unit(3,0,ObservedRole::Ranged,530,400),unit(4,0,ObservedRole::Melee,540,400),unit(11,1,ObservedRole::Artillery,808,400),unit(12,1,ObservedRole::Ranged,850,400)};
  for(int tick=0;tick<15;++tick){
   if(tick==1){o.units[0].takenFromEnemy+=10;o.units[1].dealtToEnemy+=8;}
   if(tick==2)o.units[4].x=1300; // no reachable gun; retained v6 firing
   if(tick==3){o.units[4].x=500;o.units[5].x=500;} // degenerate direction
   if(tick==4){o.units[4].x=1400;o.units[0].x=1390;o.units[1].x=1380;} // boundary/raw clips
   if(tick==5){o.units[0].hp=0;} // nearest-gun reassignment and memory death
   if(tick==6){o.units[4].hp=0;} // battery exit, complete fallthrough
   if(tick==7){o.units[4]=unit(13,1,ObservedRole::Artillery,900,450);} // target death/reassignment
   if(tick==8){o.units[1].minRange=320;o.units[1].x=580;o.units[4].x=900;o.units[4].y=400;}
   if(tick==9)o.units[1].minRange=320.0001;
   if(tick==10)o.dt=-1; // fail-safe: no stale overlay, no scoring
   if(tick==11){o.dt=1./30;o.units[1].minRange=0;}
   for(auto* c:std::vector<Controller*>{&commit,&escape,&gate,&v6,&p16})c->prepare(o);
   state(commit,v6);state(escape,v6);state(gate,v6);state(commit,p16.baseline().base());
   for(auto u:o.units)if(u.hp>0&&u.team==0){assert(eq(commit.decide(o,u.id),p16.decide(o,u.id)));assert(eq(escape.decide(o,u.id),v6.decide(o,u.id)));}
   auto clone=gate.clone();auto snapshot=gate.complexStates();auto originalModes=gate.modes();auto next=o;next.t+=.1;next.dt=1./30;clone->prepare(next);assert(gate.complexStates()==snapshot&&gate.modes()==originalModes);
   if(o.dt>0){auto twin=gate.clone();twin->prepare(next);auto* other=dynamic_cast<S4V7Controller*>(clone.get());auto* equal=dynamic_cast<S4V7Controller*>(twin.get());state(*equal,*other);assert(equal->modes()==other->modes());for(auto u:next.units)if(u.team==0&&u.hp>0)assert(eq(equal->decide(next,u.id),clone->decide(next,u.id)));}
   o.t+=.2;
  }
 }
 // Explicit mixed modes: escaping gun still assigns escorts/anchor and repels commit gun.
 Observation o;o.width=1400;o.height=800;o.dt=1./30;o.units={unit(1,0,ObservedRole::Artillery,500,400),unit(2,0,ObservedRole::Artillery,520,400),unit(3,0,ObservedRole::Ranged,520,400),unit(4,0,ObservedRole::Melee,530,400),unit(11,1,ObservedRole::Artillery,830,400),unit(12,1,ObservedRole::Ranged,700,400)};
 Inject mixed(7,0,{});mixed.seed(1,.7);mixed.seed(2,-.7);mixed.seed(3,.7);mixed.prepare(o);
 assert(mixed.modes().at(1)&&!mixed.modes().at(2)&&mixed.modes().at(3));assert(escortPoints(o,0,60)[0].gun==2);assert(mixed.gunAudit()[0].anchor==11&&mixed.gunAudit()[0].geometry.neighbours==1&&!mixed.gunAudit()[0].reachable);
 for(auto q:mixed.choices()){assert(eq(q.selected,q.selectedP16?q.p16:q.baseline));if(q.id==4)assert(eq(q.p16,q.baseline));}
 auto clone=mixed.clone();auto* copied=dynamic_cast<S4V7Controller*>(clone.get());assert(copied->modes()==mixed.modes());o.units[1].hp=0;o.t+=o.dt;mixed.prepare(o);assert(!mixed.modes().count(2)&&escortPoints(o,0,60)[0].gun==1&&copied->modes().count(2));
 o.units[4].hp=0;o.t+=o.dt;mixed.prepare(o);for(auto q:mixed.choices())assert(eq(q.p16,q.baseline));
 std::cout<<"PASS observation-only: four knob vectors, complete bit-exact forced commands/inherited state, P16 edge/failure cases, mixed assignments, hysteresis, pair histories, target death, clone/isolation, once-only z integration\n";
}
