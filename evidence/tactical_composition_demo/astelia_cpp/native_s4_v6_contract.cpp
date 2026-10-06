#include "native/s4_v6_controller.h"
#include "js_value.h"
#include <iostream>
#include <stdexcept>
using namespace astelia::control;
namespace {
void require(bool b,const char* reason){if(!b)throw std::runtime_error(reason);}
void close(double a,double b,double eps=1e-12){require(std::isfinite(a)&&std::isfinite(b)&&std::abs(a-b)<=eps,"numeric mismatch");}
class Probe:public S4V6Controller {
public:
  using S4V6Controller::S4V6Controller;
  double testBound=0;
  v6::Tick integrateTick(const std::vector<v6::Unit>& a,double dt)override{return testBound?v6::trials(a,{mu_,knobs_.K,knobs_.Kt},dt,testBound):S4V6Controller::integrateTick(a,dt);}
  void inject(UnitId id,v6::Complex z){complexStates_.at(id)=z;}
  void target(UnitId id,UnitId target){memory_.at(id).target=target;}
  void refinement(unsigned n){refinement_=n;}
  void answered(UnitId id,bool unanswered){memory_.at(id).hadUnansweredThreat=unanswered;}
  std::unique_ptr<Controller> clone()const override{return std::make_unique<Probe>(*this);}
};
Observation fixture(){Observation o;o.dt=1.0/30;o.t=0;o.width=1200;o.height=700;
  for(uint32_t id=1;id<=4;++id){ObservedUnit u;u.id=id;u.team=id<=2?0:1;u.x=300+40*id;u.y=300;u.hp=u.maxhp=100;u.radius=10;u.range=200;u.speed=60;o.units.push_back(u);}return o;}
std::string actions(Controller& c,const Observation& o){js::Args rows;for(auto& u:o.units)if(u.team==0&&u.hp>0){auto d=c.decide(o,u.id);rows.push_back(js::arr({double(u.id),d.x,d.y,d.multiplier,d.stop,double(d.target),d.controllerFailure}));}return js::stringify(js::arr(std::move(rows)));}
std::string snapshot(const Probe& c){js::Args rows;for(const auto& p:c.memory()){const auto& m=p.second;rows.push_back(js::arr({double(p.first),m.zIn,m.zOut,m.zInAnswered,m.zInUnanswered,m.lastIn,m.lastOut,double(m.target),m.hadLegalTarget,m.hadUnansweredThreat}));}
  js::Args states;for(const auto& p:c.complexStates())states.push_back(js::arr({double(p.first),p.second.real(),p.second.imag()}));
  js::Args modes;for(const auto& p:c.pairModes())modes.push_back(js::arr({double(p.first.first),double(p.first.second),p.second}));
  js::Args diagnostics;for(auto d:c.complexDiagnostic())diagnostics.push_back(js::arr({double(d.id),d.real,d.imag,d.amplitude,d.argValid,d.rateValid,d.arg,d.argRate,d.rateReason}));
  js::Args history;for(auto p:c.argMemory())history.push_back(js::arr({double(p.first),p.second.arg,p.second.time,p.second.valid}));
  return js::stringify(js::arr({js::arr(std::move(rows)),js::arr(std::move(states)),js::arr(std::move(modes)),js::arr(std::move(diagnostics)),js::arr(std::move(history)),double(c.retryCount()),double(c.failureCount())}));}
}
int v6ControllerContract(){try{
  auto o=fixture();ControllerParams quiet{{"K",0},{"K_t",0},{"kappa",0},{"mu",-1},{"omega_ranged",1}};
  Probe p(7,0,quiet);p.prepare(o);for(auto v:p.complexStates())require(v.second==v6::Complex{},"zero birth");
  p.inject(1,{2,3});p.inject(2,{-.5,.8});o.t+=o.dt;p.prepare(o);require(p.complexStates().at(1).imag()!=0&&p.complexStates().at(1).real()>1,"state components must persist without clipping");
  const auto parent=snapshot(p);const auto parentActions=actions(p,o);auto child=p.clone();auto* clone=dynamic_cast<Probe*>(child.get());require(clone&&snapshot(*clone)==parent,"clone exact initial identity");
  auto branch=o;branch.units[0].takenFromEnemy+=3;branch.units[2].x=1100;branch.units[1].id=88;branch.t+=branch.dt;
  clone->prepare(branch);require(snapshot(p)==parent&&actions(p,o)==parentActions,"advancing clone changed parent state/counters/status/targets/modes/diagnostics");
  require(!p.memory().count(88)&&!p.complexStates().count(88),"new identity leaked");
  const auto lastFinite=p.complexStates();p.inject(1,{NAN,0});p.prepare(o);require(!p.lastTick().accepted&&p.decide(o,1).controllerFailure&&p.decide(o,1).target==0&&p.decide(o,1).multiplier==0,"nonfinite failure hold");
  require(p.complexStates()==lastFinite,"last finite state retained");
  o.units.erase(o.units.begin());p.prepare(o);require(!p.memory().count(1)&&!p.complexStates().count(1)&&!p.argMemory().count(1),"death/absence cleanup");
  // Counter classification comes from the producing tick, not current geometry.
  auto damage=fixture();damage.units[2].x=1100;Probe counter(7,0,{{"mu",-1},{"K",0},{"K_t",0},{"kappa",1}});counter.prepare(damage);counter.answered(1,true);
  damage.units[2].x=damage.units[0].x+100;damage.units[0].takenFromEnemy+=3;damage.t+=damage.dt;counter.prepare(damage);
  const double q=std::exp(-damage.dt/2),incoming=(1-q)*3/damage.dt/100;
  close(counter.memory().at(1).zInUnanswered,incoming);close(counter.memory().at(1).zInAnswered,0);close(counter.complexModel()[0].pressure,-incoming);
  // Force a synthetic stage-bound retry without changing production policy.
  auto retried=fixture();Probe retry(7,0,{{"mu",0},{"K",0},{"K_t",0},{"kappa",50},{"beta",0}});retry.prepare(retried);retry.testBound=1;
  retried.units[0].takenFromEnemy=60/(50*(1-q)/retried.dt/100);retried.t+=retried.dt;
  retry.answered(1,false);retry.prepare(retried);require(retry.lastTick().accepted&&retry.lastTick().retries==1,"controller stage retry");
  close(retry.memory().at(1).zIn,retried.units[0].takenFromEnemy*(1-q)/retried.dt/100);close(retry.memory().at(1).lastIn,retried.units[0].takenFromEnemy);
  auto before=retry.complexStates();retry.testBound=.1;retried.units[0].takenFromEnemy+=1;retried.t+=retried.dt;retry.prepare(retried);
  require(!retry.lastTick().accepted&&retry.lastTick().reason=="retry_exhausted"&&retry.complexStates()==before,"exhaustion cannot publish rejected states");
  close(retry.memory().at(1).lastIn,retried.units[0].takenFromEnemy);require(retry.failureCount()==1,"terminal failure count");
  // Exact threshold margins and target hysteresis: empty groups tie by id;
  // 0.199999 retains incumbent; 0.2 and 0.200001 switch.
  for(double distance:{.199999,.200001}){auto targetFixture=fixture();Probe t(7,0,{{"K",0},{"K_t",0},{"kappa",0},{"mu",0}});t.prepare(targetFixture);t.target(1,4);t.target(2,3);
    // dt small keeps prescribed ODE change below the explicit threshold margin.
    targetFixture.dt=1e-12;targetFixture.t+=targetFixture.dt;t.inject(1,{});t.inject(2,{1-distance,0});t.prepare(targetFixture);
    require(t.decide(targetFixture,1).target==(distance<.2?4:3),"eta=.2 target switch/tie");}
  require(v6RetainedTarget(.2,0,4,3)==3&&v6RetainedTarget(.199999,0,4,3)==4&&v6RetainedTarget(.200001,0,4,3)==3&&v6RetainedTarget(0,0,4,3)==4,"exact eta and incumbent tie");
  auto self=fixture().units[0],enemy=fixture().units[2];self.range=100;enemy.range=300;PairModes modes;
  v3Preferred(self,enemy,Knobs{},0,modes);require(modes.at({self.id,enemy.id}),"new c=0 pair starts commit");
  v3Preferred(self,enemy,Knobs{},-.200001,modes);require(!modes.at({self.id,enemy.id}),"escape crossing");
  for(double c:{-.2,0.0,.2}){v3Preferred(self,enemy,Knobs{},c,modes);require(!modes.at({self.id,enemy.id}),"closed dead band preserves escape");}
  v3Preferred(self,enemy,Knobs{},.200001,modes);require(modes.at({self.id,enemy.id}),"commit crossing");
  // Diagnostics on/off, valid segment gaps, rate reset, and real-axis A.
  auto sequence=fixture();for(auto& u:sequence.units)u.role=ObservedRole::Melee;
  Probe on(7,0),off(7,0);on.attributionDiagnostics(true);
  for(unsigned tick=0;tick<20;++tick){sequence.t+=sequence.dt;if(tick>0)sequence.units[0].takenFromEnemy+=.3;on.prepare(sequence);off.prepare(sequence);require(actions(on,sequence)==actions(off,sequence),"diagnostics change action bytes");for(auto z:on.complexStates())require(z.second.imag()==0,"stage A real axis");}
  auto arg=fixture();arg.units[0].role=ObservedRole::Ranged;Probe phase(7,0,quiet);phase.prepare(arg);
  require(!phase.complexDiagnostic()[0].argValid&&!phase.complexDiagnostic()[0].rateValid,"zero has no phase");
  phase.inject(1,{0,1});arg.t+=arg.dt;phase.prepare(arg);require(phase.complexDiagnostic()[0].argValid&&!phase.complexDiagnostic()[0].rateValid,"first valid endpoint");
  arg.t+=arg.dt;phase.prepare(arg);require(phase.complexDiagnostic()[0].rateValid,"contiguous valid rate");close(phase.complexDiagnostic()[0].argRate,1,1e-5);
  phase.inject(1,{.001,0});arg.t+=arg.dt;phase.prepare(arg);require(!phase.complexDiagnostic()[0].rateValid,"gap invalidates rate");
  phase.inject(1,{0,1});arg.t+=arg.dt;phase.prepare(arg);require(!phase.complexDiagnostic()[0].rateValid,"gap resets phase rate");
  for(double radius:{.199999,.2,.200001}){auto exact=fixture();Probe boundary(7,0,{{"mu",radius*radius},{"omega_ranged",0},{"K",0},{"K_t",0},{"kappa",0}});boundary.prepare(exact);boundary.inject(1,{radius,0});exact.t+=exact.dt;boundary.prepare(exact);
    require(boundary.complexDiagnostic()[0].argValid==(radius>=.2),"amplitude validity exact boundary");}
  // Matched damping converges; differing drives need not. Antiphase is a
  // declared positive-mu counterexample to universal equalization.
  for(bool oppositeDrive:{false,true}){std::vector<v6::Unit> pair{{1,0,0,0,1,oppositeDrive?1.0:0,{.6,.8}},{2,0,0,0,1,oppositeDrive?-1.0:0,{-.6,-.8}}};
    for(unsigned tick=0;tick<180;++tick){auto r=v6::step(pair,{-1,1,0},1.0/30);require(r.accepted,"damped pair");pair=r.units;}
    require(oppositeDrive?std::abs(pair[0].z-pair[1].z)>.1:std::abs(pair[0].z-pair[1].z)<1e-6,"equalization scope/counterexample");}
  std::vector<v6::Unit> antiphase{{1,0,0,0,1,0,{1,0}},{2,0,0,0,1,0,{-1,0}}};
  for(unsigned tick=0;tick<180;++tick){auto r=v6::step(antiphase,{2,.5,0},1.0/30);require(r.accepted,"antiphase tick");antiphase=r.units;}
  close(std::abs(antiphase[0].z),1,1e-5);require(std::abs(antiphase[0].z+antiphase[1].z)<1e-12&&std::abs(antiphase[0].z-antiphase[1].z)>1.9,"positive-mu antiphase counterexample");
  auto pressure=fixture();Probe outside(7,0);outside.prepare(pressure);pressure.units[0].takenFromEnemy=1e6;pressure.t+=pressure.dt;outside.prepare(pressure);
  require(!outside.lastTick().accepted&&outside.lastTick().reason=="pressure_envelope"&&outside.lastTick().n==0&&outside.decide(pressure,1).controllerFailure,"pressure failure before integration");
  size_t bytes=0;for(auto arm:{"morale","pushpull","nearest"}){
    auto a=makeController({arm,{},"v5"},7,0),b=makeController({arm,{},"v6"},7,0);auto f=fixture();
    for(unsigned tick=0;tick<80;++tick){f.t+=f.dt;f.units[0].takenFromEnemy+=tick%3;f.units[1].dealtToEnemy+=tick%2;f.units[2].x=400+tick;a->prepare(f);b->prepare(f);auto left=actions(*a,f),right=actions(*b,f);require(left==right,"unchanged arm action bytes");bytes+=left.size();}
  }
  for(auto key:{"omega_melee","unknown","lambda_melee"}){bool rejected=false;try{makeController({"resonator",{{key,0}},"v6"},7,0);}catch(...){rejected=true;}require(rejected,"removed/unknown resonator knob rejected");}
  for(auto arm:{"morale","pushpull","nearest"}){bool rejected=false;try{makeController({arm,{{"mu",0}},"v6"},7,0);}catch(...){rejected=true;}require(rejected,"mu on unchanged arm rejected");}
  for(auto key:{"mu","omega_ranged","K","K_t","kappa","beta","G","w","f_c","m_k","lambda_th"})for(double value:{double(NAN),double(INFINITY),double(-INFINITY),1e100}){bool rejected=false;try{makeController({"resonator",{{key,value}},"v6"},7,0);}catch(...){rejected=true;}require(rejected,"nonfinite/out-of-bounds knob");}
  std::cout<<"{\"status\":\"passed\",\"fights\":0,\"unchanged_arm_action_bytes\":"<<bytes<<"}\n";return 0;
}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}
