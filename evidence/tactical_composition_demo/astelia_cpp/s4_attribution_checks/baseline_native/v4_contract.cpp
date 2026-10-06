// Section-15 synthetic contracts: no World and no combat.
#include "native/s3_controller.h"
#include <cmath>
#include <iostream>
#include <stdexcept>
using namespace astelia::control;
void need(bool x,const char* why){if(!x)throw std::runtime_error(why);}
void equal(double a,double b){need(std::abs(a-b)<1e-10,"numeric mismatch");}
class Probe:public S3Controller{public:using S3Controller::S3Controller;void commitment(double c){memory_[1].state=arm_==Arm::Resonator?std::acos(c):c;}};
Observation scene(){Observation o;o.dt=.1;o.width=1200;o.height=700;
  ObservedUnit self;self.id=1;self.hp=self.maxhp=100;self.radius=10;self.range=100;self.speed=100;self.x=300;self.y=300;
  auto a=self;a.id=20;a.team=1;a.range=400;a.x=500;auto b=a;b.id=21;b.x=100;o.units={self,a,b};return o;}
int historicalV4Contract(){try{
  auto o=scene();auto self=o.units[0],enemy=o.units[1];Knobs k;k.w=1;PairModes modes;PairHolds holds;std::vector<HoldEvent> events;
  auto distance=[&](double c,double t){return v4Preferred(self,enemy,k,c,modes,holds,t,events);};
  equal(distance(1,0),.78);need(holds.empty(),"initial hold");
  equal(distance(-1,1),5.4);equal(holds.at({1,20}).until,5.62);equal(events.back().planned,4.62);
  equal(distance(1,2),5.4);need(!modes.at({1,20}),"hold crossed");
  equal(distance(1,5.62),.78);need(modes.at({1,20}),"expiry did not restore hysteresis");
  need(events[1].reason=="expired","expiry event");
  enemy.x=self.x+78;equal(distance(-1,5.72),5.4);need(events[3].reason=="target_band","early release absent");equal(events[3].duration,.1);
  // Closed hysteresis band remains closed after expiry.
  equal(distance(.2,holds.at({1,20}).until),5.4);
  for(double speed:{0.,1.}){self.speed=speed;modes.clear();holds.clear();distance(1,0);distance(-1,1);need(holds.empty(),"immobile hold");}
  self.speed=100;modes.clear();holds.clear();distance(1,0);distance(-1,1);self.speed=1;distance(1,2);need(holds.empty(),"rooted active hold retained");
  // Own artillery uses the effective distance and pixel-to-model conversion.
  self.role=ObservedRole::Artillery;self.range=320;self.minRange=400;self.speed=100;enemy.range=500;modes.clear();holds.clear();
  equal(distance(1,0),4.2);distance(-1,1);equal(holds.at({1,20}).until-1,(5.2+3.2-4.2));
  // Kite path creates no binary mode or hold.
  enemy.range=10;modes.clear();holds.clear();equal(distance(-1,0),v2Preferred(self,enemy,k,-1));need(modes.empty()&&holds.empty(),"kite state mutated");
  for(auto arm:{Arm::Resonator,Arm::Morale,Arm::PushPull}){
    ControllerParams params{{"G",2.5},{"w",1}};
    if(arm==Arm::PushPull)params.erase("w");
    else {params["K"]=params["K_t"]=params["kappa"]=0;
      if(arm==Arm::Resonator)params["omega_melee"]=params["omega_ranged"]=0;else params["lambda_melee"]=params["lambda_ranged"]=0;}
    o=scene();Probe p(7,0,arm,params,"v4");if(arm!=Arm::PushPull)p.commitment(1);p.prepare(o);
    auto action=p.decide(o,1);need(action.x>o.units[0].x&&action.multiplier>0,"symmetric committed force cancelled");need(p.focus().at(1)==20,"focus tie not low id");
    // Highest damage weight outranks id; with no commit fallback remains symmetric.
    if(arm!=Arm::PushPull){o.t=.1;o.units[2].dealtToEnemy=100;p.prepare(o);need(p.focus().at(1)==21,"focus ignored damage weight");
      p.commitment(-1);o.t=.2;p.prepare(o);need(p.focus().empty(),"escape retained focus");
      need(!p.pairHolds().empty(),"switch hold missing");p.commitment(1);o.t=.3;p.prepare(o);need(!p.pairModes().at({1,20}),"production hold reversed");
    }
    auto branch=p.clone();auto* copy=dynamic_cast<S3Controller*>(branch.get());need(copy&&copy->focus()==p.focus()&&copy->pairModes()==p.pairModes()&&copy->pairHolds().size()==p.pairHolds().size(),"clone lost memory");
    auto dead=o;dead.units[1].hp=0;branch->prepare(dead);need(!copy->pairModes().count({1,20})&&p.pairModes().count({1,20}),"clone death leaked");need(!copy->pairHolds().count({1,20}),"clone hold death");
    dead.units[0].hp=0;p.prepare(dead);need(p.pairModes().empty()&&p.pairHolds().empty()&&p.focus().empty(),"own death retained memory");
  }
  DecisionDiagnostic d;need(v4Feasibility(d,1,0).reason=="no_reference","no_reference");d.reference=20;need(v4Feasibility(d,1,0).reason=="coincident","coincident");
  d.dx=10;d.preferred=10;need(v4Feasibility(d,1,0).reason=="at_distance","at_distance");d.preferred=5;need(v4Feasibility(d,0,0).reason=="zero_displacement","zero_displacement");
  equal(v4Feasibility(d,1,0).cosine,1);equal(v4Feasibility(d,-1,0).cosine,-1);equal(v4Feasibility(d,0,1).cosine,0);d.preferred=20;equal(v4Feasibility(d,-1,0).cosine,1);
  std::cout<<"{\"status\":\"passed\",\"fights\":0,\"checks\":[\"hold switch/crossing/expiry/band\",\"speed threshold\",\"symmetric focus/damage/ties\",\"clone/death\",\"feasibility boundaries\"]}\n";
return 0;
}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}
