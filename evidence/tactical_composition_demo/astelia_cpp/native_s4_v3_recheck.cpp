// Adversarial section-14 checks. Synthetic observations only; no World or fights.
#include "native/s3_controller.h"
#include <algorithm>
#include <cmath>
#include <iostream>
#include <stdexcept>
using namespace astelia::control;
void need(bool x,const char* why){if(!x)throw std::runtime_error(why);}
void equal(double a,double b){need(std::abs(a-b)<1e-12,"distance mismatch");}
class Probe:public S3Controller {
public:using S3Controller::S3Controller;
  void commitment(double c){memory_.at(1).state=arm_==Arm::Resonator?std::acos(c):c;}
};
Observation scene(){Observation o;o.dt=1./30;o.width=1200;o.height=700;
  ObservedUnit self;self.id=1;self.hp=self.maxhp=100;self.radius=10;self.range=20;self.x=300;self.y=300;
  o.units.push_back(self);
  for(unsigned n=0;n<20;++n){auto e=self;e.id=20+n;e.team=1;e.range=400;e.x=400+10*n;o.units.push_back(e);}return o;
}
int main(){try {
  for(auto arm:{Arm::Resonator,Arm::Morale}){
    ControllerParams k{{"K",0},{"K_t",0},{"kappa",0}};
    if(arm==Arm::Resonator){k["omega_melee"]=0;k["omega_ranged"]=0;}
    else{k["lambda_melee"]=0;k["lambda_ranged"]=0;}
    auto o=scene();Probe p(7,0,arm,k,"v3");p.prepare(o);p.commitment(1);p.prepare(o);
    // The far pair is outside the nearest-eight set and is not a threat (zOut=0).
    auto selected=v2EnemySet(o.units[0],[&]{std::vector<const ObservedUnit*> es;for(size_t i=1;i<o.units.size();++i)es.push_back(&o.units[i]);return es;}(),p.memory());
    need(selected.size()==8&&selected.back()->id==27,"unexpected cap fixture");
    p.commitment(-1);p.prepare(o);need(!p.pairModes().at({1,39}),"excluded pair missed crossing");
    p.commitment(.1);o.units.back().x=350;p.prepare(o);
    need(!p.pairModes().at({1,39}),"reentry reinitialized retained mode");
    // Real base-class clone(), rather than a test subclass clone override.
    auto branch=p.clone();auto* copy=dynamic_cast<S3Controller*>(branch.get());
    need(copy&&copy->pairModes()==p.pairModes(),"production clone lost modes");
    auto removed=o;removed.units.back().hp=0;branch->prepare(removed);
    need(!copy->pairModes().count({1,39})&&p.pairModes().count({1,39}),"clone death leaked");
    p.prepare(removed);o.units.back().hp=100;p.prepare(o);
    need(p.pairModes().at({1,39}),"revived pair inherited escape");
    removed.units[0].hp=0;p.prepare(removed);need(p.pairModes().empty(),"own death retained pairs");
    // Omission also drops memory; changing input order cannot change decisions.
    Probe a(7,0,arm,k,"v3"),b(7,0,arm,k,"v3");a.prepare(o);std::reverse(o.units.begin(),o.units.end());b.prepare(o);
    need(a.pairModes()==b.pairModes(),"observation order changed modes");equal(a.decide(o,1).x,b.decide(o,1).x);
    o.units.erase(std::find_if(o.units.begin(),o.units.end(),[](auto& u){return u.id==39;}));a.prepare(o);
    need(!a.pairModes().count({1,39}),"absent enemy retained mode");
  }
  auto o=scene();auto self=o.units[0],enemy=o.units[1];Knobs k;k.w=0;
  PairModes m;
  equal(v3Preferred(self,enemy,k,-.01,m),4.2); // negative initial value inside band
  equal(v3Preferred(self,enemy,k,.2,m),4.2);
  equal(v3Preferred(self,enemy,k,std::nextafter(.2,1.),m),k.fc*.4);
  equal(v3Preferred(self,enemy,k,-.2,m),k.fc*.4);
  equal(v3Preferred(self,enemy,k,std::nextafter(-.2,-1.),m),4.2);
  // Coincident motion skips a direction; prepare still updates that pair's mode.
  self.role=ObservedRole::Artillery;self.range=320;self.minRange=80;
  enemy.role=ObservedRole::Artillery;enemy.range=320;enemy.x=self.x;enemy.y=self.y;
  m.clear();equal(v3Preferred(self,enemy,k,1,m),k.fc*3.2);
  std::map<UnitId,Memory> mem;mem[enemy.id]={};auto force=v3EnemyMotion(self,{&enemy},mem,k,1,m);
  equal(force[0],0);equal(force[1],0);
  // Equal reaches belong to the binary case; the kite law remains inherited.
  enemy.range=319;auto prior=m;equal(v3Preferred(self,enemy,k,-1,m),v2Preferred(self,enemy,k,-1));need(m==prior,"kite mutated memory");
  enemy.range=320;equal(v3Preferred(self,enemy,k,-1,m),3.2);
  self.minRange=400;equal(v3Preferred(self,enemy,k,1,m),4.2); // effective lower bound > enemy reach
  // Binary individual distances do not forbid cancellation of different enemies.
  self.role=ObservedRole::Ranged;self.range=100;self.minRange=0;self.x=300;
  enemy.role=ObservedRole::Ranged;enemy.range=400;enemy.x=500;
  auto second=enemy;second.id=40;second.x=100;mem[second.id]={};m.clear();k.w=1;
  force=v3EnemyMotion(self,{&enemy,&second},mem,k,1,m);equal(force[0],0);equal(force[1],0);
  std::cout<<"{\"status\":\"passed\",\"scope\":\"synthetic v3 pair lifecycle, clone, boundaries and cancellation\",\"fights\":0}\n";
}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}
