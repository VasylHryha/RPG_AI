// Synthetic controller snapshots only. Never constructs a World or advances combat.
#include "native/s3_controller.h"
#include "native/config_codec.h"
#include "js_value.h"
#include <cstring>
#include <iostream>
#include <stdexcept>
#include "s4_attribution_checks/baseline_native/s3_controller.cpp"
namespace historical_v4_contract {
#include "s4_attribution_checks/baseline_native/v4_contract.cpp"
}
namespace {
using namespace astelia::control;
namespace baseline=astelia::control::attribution_baseline;
void need(bool ok,const char* message){if(!ok)throw std::runtime_error(message);}
std::string bytes(const UnitDecision& d){return js::stringify(js::obj({{"x",d.x},{"y",d.y},{"multiplier",d.multiplier},{"stop",d.stop},{"target",double(d.target)},{"failure",d.controllerFailure}}));}
Observation fixture(int tick,uint8_t side){Observation o;o.t=tick*.1;o.dt=.1;o.width=1400;o.height=800;
  for(unsigned i=0;i<24;++i){ObservedUnit u;u.id=i+1;u.team=i<6?side:1-side;u.role=ObservedRole(i%3);u.x=70+(i%8)*160+((tick*7+i)%13);u.y=90+(i/8)*240;
    u.hp=u.maxhp=100;u.radius=10;u.range=u.role==ObservedRole::Melee?35:u.role==ObservedRole::Ranged?260:320;u.minRange=u.role==ObservedRole::Artillery?80:0;u.speed=tick%9==0?1:40+(i%4)*25;
    u.dealtToEnemy=tick*(i%5);u.takenFromEnemy=tick*(i%7);
    if(tick>20&&(i==1||i==9))u.hp=0;
    if(tick%7==0&&i==7)continue; // disappearing/reappearing reference
    if(i==8&&tick%5==0){u.x=70+((tick*7)%13);u.y=90;} // coincident centres
    o.units.push_back(u);
  }return o;
}
class Probe:public S3Controller {public:using S3Controller::S3Controller;void commitment(double c){memory_[1].state=c;}};
Observation symmetric(){Observation o;o.dt=.1;ObservedUnit u;u.id=1;u.x=300;u.y=300;u.hp=u.maxhp=100;u.range=100;u.radius=10;u.speed=100;
  auto a=u;a.id=20;a.team=1;a.range=400;a.x=500;auto b=a;b.id=21;b.x=100;o.units={u,a,b};return o;}
}
int attributionContract(){try{
  need(historical_v4_contract::historicalV4Contract()==0,"historical v4 contracts");
  unsigned compared=0;
  for(const auto& skeleton:{"v0","v1","v2","v3","v4","v5"})for(auto arm:{Arm::Resonator,Arm::Morale,Arm::PushPull})for(uint8_t side:{0,1})for(int seed:{7,177,3201}){
    S3Controller current(seed,side,arm,{},skeleton),traced(seed,side,arm,{},skeleton);
    traced.attributionDiagnostics(true);
    baseline::S3Controller prior(seed,side,baseline::Arm(int(arm)),{},std::string(skeleton)=="v5"?"v3":skeleton);
    for(int tick=0;tick<32;++tick){auto o=fixture(tick,side);current.prepare(o);traced.prepare(o);prior.prepare(o);
      for(const auto& u:o.units)if(u.hp>0&&u.team==side){auto a=current.decide(o,u.id),b=prior.decide(o,u.id),t=traced.decide(o,u.id);
        need(bytes(a)==bytes(b)&&bytes(a)==bytes(t),"v0-v4 synthetic fixture bytes changed");
        // JSON compares encoded output, bit checks preserve signed zero and exact IEEE values too.
        need(std::memcmp(&a.x,&b.x,sizeof(double))==0&&std::memcmp(&a.y,&b.y,sizeof(double))==0&&std::memcmp(&a.multiplier,&b.multiplier,sizeof(double))==0&&std::memcmp(&a.stop,&b.stop,sizeof(double))==0,"fixture numeric bits changed");++compared;}
      need(current.pairModes()==prior.pairModes()&&current.pairModes()==traced.pairModes(),"pair memory drift");
      need(current.pairHolds().size()==prior.pairHolds().size(),"hold memory drift");
      for(const auto& h:current.pairHolds()){const auto& old=prior.pairHolds().at(h.first);need(h.second.started==old.started&&h.second.until==old.until,"hold time drift");}
    }
  }
  // Isolate each factor with nonzero ally force before holds or focus can activate.
  for(const auto& cell:{"H","F"}){Probe test(7,0,Arm::Morale,{},cell),v3(7,0,Arm::Morale,{},"v3");
    test.commitment(std::string(cell)=="H"?1:-1);v3.commitment(std::string(cell)=="H"?1:-1);
    auto o=symmetric();auto ally=o.units[0];ally.id=2;ally.x+=30;o.units.push_back(ally);test.prepare(o);v3.prepare(o);
    need(bytes(test.decide(o,1))==bytes(v3.decide(o,1)),"factor altered inherited summation");}
  ControllerParams params{{"K",0},{"K_t",0},{"kappa",0},{"lambda_melee",0},{"lambda_ranged",0},{"G",2.5},{"w",1}};
  for(const auto& cell:{"v3","v5","H","F","HF","v4"}){
    Probe p(7,0,Arm::Morale,params,cell),plain(7,0,Arm::Morale,params,cell);p.attributionDiagnostics(true);auto o=symmetric();
    p.commitment(1);plain.commitment(1);p.prepare(o);plain.prepare(o);
    const bool focus=std::string(cell)=="F"||std::string(cell)=="HF"||std::string(cell)=="v4";
    const bool hold=std::string(cell)=="H"||std::string(cell)=="HF"||std::string(cell)=="v4";
    need(p.focus().empty()!=focus,"cell focus flag");need(p.pairHolds().empty(),"first mode held");
    need((p.decide(o,1).multiplier>0)==focus,"symmetric focus/cancellation");
    need(bytes(p.decide(o,1))==bytes(plain.decide(o,1)),"trace affected action");
    p.commitment(-1);o.t=.1;p.prepare(o);need(!p.pairModes().at({1,20}),"escape crossing");need(p.pairHolds().empty()!=hold,"cell hold flag");
    p.commitment(1);o.t=.2;p.prepare(o);need(p.pairModes().at({1,20})!=hold,"held crossing");
    auto branch=p.clone();auto* copy=dynamic_cast<S3Controller*>(branch.get());auto dead=o;dead.units[1].hp=0;branch->prepare(dead);
    need(!copy->pairModes().count({1,20})&&p.pairModes().count({1,20}),"clone cleanup isolation");
    if(hold){o.t=10;p.prepare(o);need(p.pairModes().at({1,20}),"expiry crossing");need(!p.holdEvents().empty(),"expiry events absent");}
  }
  for(const auto& cell:{"v3","v5","H","F","HF","v4"}){
    auto request=js::obj({{"mode","alone"},{"trace",true},{"decisionDiagnostics",true},{"attributionDiagnostics",true},{"options",js::obj({{"ai",js::arr({js::obj({{"controller","morale"},{"skeleton",cell}}),js::obj({})})}})}});
    auto config=astelia::configuration(request);auto c=makeController(config.controllers[0],7,0);need(dynamic_cast<S3Controller*>(c.get())!=nullptr,"production configuration/factory rejected cell");
    js::set(request,"trace",false);bool rejected=false;try{astelia::configuration(request);}catch(const std::invalid_argument&){rejected=true;}need(rejected,"attribution trace precondition missing");
  }
  // HF is the exact historical v4 policy, not a replacement rule.
  for(auto arm:{Arm::Resonator,Arm::Morale}){S3Controller hf(17,0,arm,{},"HF"),v4(17,0,arm,{},"v4");
    for(int tick=0;tick<32;++tick){auto o=fixture(tick,0);hf.prepare(o);v4.prepare(o);for(const auto& u:o.units)if(u.team==0&&u.hp>0)need(bytes(hf.decide(o,u.id))==bytes(v4.decide(o,u.id)),"HF/v4 drift");}}
  // Artillery legal annulus includes both boundaries, excludes dead zone.
  auto o=symmetric();o.units[1].role=ObservedRole::Artillery;o.units[1].minRange=100;o.units[1].range=200;
  need(v2Legal(o.units[1],o.units[0]),"gun reach boundary");o.units[0].x=450;need(!v2Legal(o.units[1],o.units[0]),"gun dead zone");o.units[0].x=400;need(v2Legal(o.units[1],o.units[0]),"gun minimum boundary");
  std::cout<<"{\"status\":\"passed\",\"fights\":0,\"fixture_action_bytes_compared\":"<<compared<<",\"legacy_skeletons\":[\"v0\",\"v1\",\"v2\",\"v3\",\"v4\"],\"cells\":[\"v3\",\"H\",\"F\",\"HF\"],\"scope\":\"synthetic_prepare_decide_not_combat\"}\n";return 0;
}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}
