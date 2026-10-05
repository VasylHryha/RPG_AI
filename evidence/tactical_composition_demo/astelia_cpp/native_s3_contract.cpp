#include "native/s3_controller.h"
#include "native/s3_diagnostics.h"
#include "native/controller_bridge.h"
#include "native/config_codec.h"
#include "native/api.h"
#include "js_value.h"
#include <iostream>
#include <stdexcept>
using namespace astelia;using namespace astelia::control;
using js::V;
namespace {
void require(bool b,const char* why){if(!b)throw std::runtime_error(why);}
void close(double a,double b,double eps=1e-12){require(std::isfinite(a)&&std::isfinite(b)&&std::abs(a-b)<=eps,"numeric contract mismatch");}
class Probe : public S3Controller {
public:using S3Controller::S3Controller;
 void inject(UnitId id,double state){memory_.at(id).state=state;}
 void target(UnitId id,UnitId target){memory_.at(id).target=target;}
 void substeps(unsigned n){substeps_=n;}
 void assignments(const std::map<UnitId,Memory>& source){for(auto& m:memory_){auto s=source.find(m.first);m.second.target=s==source.end()?0:s->second.target;}}
 std::unique_ptr<Controller> clone() const override{return std::make_unique<Probe>(*this);}
};
astelia::control::Observation fixture(){astelia::control::Observation o;o.dt=1.0/30;o.width=1200;o.height=700;
 for(uint32_t i=1;i<=4;++i){ObservedUnit u;u.id=i;u.team=i<=2?0:1;u.x=300+40*i;u.y=300;u.hp=u.maxhp=100;u.radius=10;u.range=200;u.speed=60;o.units.push_back(u);}return o;}
V equations(V request){auto arr=js::get(request,"units");std::vector<ModelUnit> a;for(auto u:arr.p->items){ModelUnit x;x.x=js::num(js::get(u,"x"));x.y=js::num(js::get(u,"y"));x.state=js::num(js::get(u,"state"));x.rate=js::num(js::get(u,"rate"));x.pressure=js::num(js::get(u,"pressure"));x.id=uint32_t(js::num(js::get(u,"id")));x.target=uint32_t(js::num(js::get(u,"target")));a.push_back(x);}
 double dt=js::num(js::get(request,"dt"));const auto operation=js::str(js::get(request,"operation"));js::Args rhs,step;
 if(operation=="reference"){double K=js::num(js::get(request,"K")),J=js::num(js::get(request,"J")),eps=js::num(js::get(request,"eps"));auto d=allyRhs(a,K,J,eps);auto b=coupledReferenceStep(a,dt,K,J,eps);for(size_t i=0;i<a.size();++i){rhs.push_back(js::arr({d[i].x,d[i].y,d[i].state}));step.push_back(js::arr({b[i].x,b[i].y,b[i].state}));}}
 else{Knobs k;k.K=js::num(js::get(request,"K"));k.Kt=js::num(js::get(request,"K_t"));Arm arm=js::str(js::get(request,"arm"))=="resonator"?Arm::Resonator:Arm::Morale;auto d=stateRhs(a,arm,k);auto n=js::get(request,"substeps");auto b=frozenStep(a,arm,k,dt,n.tag==V::Undefined?1:uint32_t(js::num(n)));for(size_t i=0;i<a.size();++i){rhs.push_back(d[i]);step.push_back(b[i].state);}}
 return js::obj({{"rhs",js::arr(std::move(rhs))},{"step",js::arr(std::move(step))}});
}
void contracts(){
 for(auto arm:{Arm::Resonator,Arm::Morale,Arm::PushPull}){auto o=fixture();Probe p(7,0,arm);p.prepare(o);auto a=p.decide(o,1),b=p.decide(o,2);close(p.decide(o,2).x,b.x);close(p.decide(o,1).x,a.x);require(!a.controllerFailure&&!b.controllerFailure,"default prepare failure");
  auto parent=p.memory();auto clone=p.clone();o.units[0].takenFromEnemy=10;o.units[0].dealtToEnemy=4;clone->prepare(o);close(p.memory().at(1).zIn,parent.at(1).zIn);close(p.memory().at(1).state,parent.at(1).state);
  Probe same=p;o.units[0].takenFromEnemy=o.units[0].dealtToEnemy=0;same.prepare(o);p.prepare(o);close(same.decide(o,1).x,p.decide(o,1).x); // copied state and RNG
  auto ca=p.clone(),cb=p.clone();auto expanded=o;auto fresh=expanded.units[0];fresh.id=77;fresh.x=500;expanded.units.push_back(fresh);ca->prepare(expanded);cb->prepare(expanded);auto* ma=dynamic_cast<S3Controller*>(ca.get());auto* mb=dynamic_cast<S3Controller*>(cb.get());close(ma->memory().at(77).state,mb->memory().at(77).state);require(!p.memory().count(77),"clone new-id RNG/memory leaked to parent");
  p.inject(1,NAN);p.prepare(o);require(p.decide(o,1).controllerFailure&&p.decide(o,1).target==0&&p.decide(o,1).multiplier==0,"NaN must report hold");
  o.units.erase(o.units.begin());p.prepare(o);require(!p.memory().count(1),"departed memory");
  auto empty=fixture();empty.units.resize(2);Probe terminal(7,0,arm);terminal.prepare(empty);require(terminal.decide(empty,1).target==0&&terminal.decide(empty,1).multiplier==0,"terminal hold");
  auto tiny=fixture();tiny.units[2].x=tiny.units[3].x=1100;Probe outside(7,0,arm);outside.prepare(tiny);require(outside.decide(tiny,1).target==0,"empty legal set");
  auto coincident=fixture();for(auto& u:coincident.units)u.x=350;Probe together(7,0,arm);together.prepare(coincident);require(!together.decide(coincident,1).controllerFailure,"coincident unit failure");
 }
 // Production ally motion shares the reference kernel, with the declared true-unit regularization.
 for(auto arm:{Arm::Resonator,Arm::Morale,Arm::PushPull}){auto a=fixture();a.units[0].x=300;a.units[1].x=350;a.units[2].x=a.units[3].x=1100;ControllerParams params{{"G",0}};if(arm!=Arm::PushPull){params["K"]=0;params["K_t"]=0;params["kappa"]=0;}Probe p(7,0,arm,params);p.prepare(a);p.inject(1,0);p.inject(2,0);p.prepare(a);auto d=p.decide(a,1);close(d.x,100);close(d.multiplier,.2);}
 // Damage step, constant rate and decay: update once per observation, reset on departure/new id.
 auto o=fixture();Probe damage(7,0,Arm::Morale);damage.prepare(o);double z=0,q=std::exp(-o.dt/2);
 for(int tick=1;tick<=5;++tick){o.t+=o.dt;o.units[0].takenFromEnemy+=3;damage.prepare(o);z=q*z+(1-q)*3/o.dt/100;close(damage.memory().at(1).zIn,z);}
 for(int tick=0;tick<5;++tick){o.t+=o.dt;damage.prepare(o);z*=q;close(damage.memory().at(1).zIn,z);}
 // v1 scripted attribution deliberately changes reach BETWEEN the producing and consuming snapshots.
 for(auto arm:{Arm::Resonator,Arm::Morale}){
  auto seq=fixture();seq.units={seq.units[0],seq.units[2]};seq.units[1].x=1100;
  seq.units[0].takenFromEnemy=17; // first prepare baselines counters, no fabricated damage
  Probe split(7,0,arm);split.prepare(seq);close(split.memory().at(1).zInAnswered,0);close(split.memory().at(1).zInUnanswered,0);
  double answered=0,unanswered=0,outgoing=0;
  for(int tick=1;tick<=6;++tick){bool priorLegal=split.memory().at(1).hadLegalTarget;
   seq.units[1].x=tick%2?seq.units[0].x+100:1100;
   double increment=tick<=4?3:0;seq.units[0].takenFromEnemy+=increment;seq.units[0].dealtToEnemy+=1;
   split.prepare(seq);double input=(1-q)*increment/seq.dt/100;
   answered=q*answered+(priorLegal?input:0);unanswered=q*unanswered+(priorLegal?0:input);outgoing=q*outgoing+(1-q)/seq.dt/100;
   const auto& m=split.memory().at(1);close(m.zInAnswered,answered);close(m.zInUnanswered,unanswered);close(m.zIn,answered+unanswered);
   close(split.model()[0].pressure,25*(answered-1.5*outgoing-unanswered));require(m.hadLegalTarget==bool(tick%2),"legality not retained at frozen snapshot");
  }
  auto branch=split.clone();auto* copy=dynamic_cast<S3Controller*>(branch.get());require(copy->memory().at(1).hadLegalTarget==split.memory().at(1).hadLegalTarget,"clone lost legality");
  close(copy->memory().at(1).zInAnswered,answered);close(copy->memory().at(1).zInUnanswered,unanswered);
  seq.units[0].takenFromEnemy+=7;seq.units[1].x=seq.units[0].x+100;branch->prepare(seq);
  close(copy->memory().at(1).zInUnanswered,q*unanswered+(1-q)*7/seq.dt/100);close(split.memory().at(1).zInUnanswered,unanswered);
  seq.units.erase(seq.units.begin());split.prepare(seq);require(!split.memory().count(1),"split memory not dropped at departure");
  // Outranged under-fire commitment rises in v1; v0 remains the retreat negative control.
  auto fire=fixture();fire.units={fire.units[0],fire.units[2]};fire.units[1].x=1100;
  ControllerParams noCoupling{{"K",0},{"K_t",0}};
  if(arm==Arm::Morale){noCoupling["lambda_melee"]=0;noCoupling["lambda_ranged"]=0;}
  Probe v1(7,0,arm,noCoupling,"v1"),v0(7,0,arm,noCoupling,"v0");v1.prepare(fire);v0.prepare(fire);
  double initial=arm==Arm::Resonator?1:0;v1.inject(1,initial);v0.inject(1,initial);
  fire.units[0].takenFromEnemy=10;v1.prepare(fire);v0.prepare(fire);
  double before=arm==Arm::Resonator?std::cos(initial):initial;
  require(v1.diagnostic()[0].commitment>before&&v0.diagnostic()[0].commitment<before,"unanswered fire must raise commitment only in v1");
  require(v1.decide(fire,1).target==0,"outranged synthetic unit acquired target");
  // A legal enemy's outgoing damage raises its v1 target score; v0 penalizes it.
  auto hit=fixture();hit.units={hit.units[0],hit.units[2],hit.units[3]};
  Probe engage(7,0,arm,{{"K",0},{"K_t",0}},"v1"),old(7,0,arm,{{"K",0},{"K_t",0}},"v0");engage.prepare(hit);old.prepare(hit);
  require(engage.decide(hit,1).target==3,"stable initial target tie");hit.units[2].dealtToEnemy=10;hit.units[0].takenFromEnemy=10;
  engage.prepare(hit);old.prepare(hit);require(engage.decide(hit,1).target==4&&old.decide(hit,1).target==3,"enemy damage target preference and v0 negative control");
 }
 { // v2 threat geometry: both radii for direct/melee, inclusive artillery min/max, living engaged enemies only.
 auto threat=fixture();auto self=threat.units[0],enemy=threat.units[2];enemy.x=self.x+220;
 for(auto role:{ObservedRole::Melee,ObservedRole::Ranged}){enemy.role=role;require(v2Threat(self,enemy,.1),"direct threat boundary");enemy.x+=.01;require(!v2Threat(self,enemy,.1),"direct threat outside");enemy.x-=.01;}
 require(!v2Threat(self,enemy,0),"inactive enemy is not a threat");enemy.hp=0;require(!v2Threat(self,enemy,.1),"dead threat");enemy.hp=100;enemy.team=0;require(!v2Threat(self,enemy,.1),"ally threat");enemy.team=1;
 enemy.role=ObservedRole::Artillery;enemy.minRange=80;
 for(double distance:{79.0,80.0,200.0,200.01}){enemy.x=self.x+distance;require(v2Threat(self,enemy,.1)==(distance>=80&&distance<=200),"artillery threat dead zone/boundaries");}
 // Both centre-reach cases, mixed roles, extreme bounds: committed distances stay in own legal reach.
 for(auto ownRole:{ObservedRole::Melee,ObservedRole::Ranged,ObservedRole::Artillery})for(auto enemyRole:{ObservedRole::Melee,ObservedRole::Ranged,ObservedRole::Artillery})for(double er:{100.0,400.0})for(double fc:{.3,1.0})for(double mk:{.2,1.0}){
  self.role=ownRole;self.range=250;self.minRange=80;enemy.role=enemyRole;enemy.range=er;enemy.minRange=40;
  Knobs k;k.fc=fc;k.mk=mk;k.w=1.5;double Ri=(self.range+(ownRole==ObservedRole::Artillery?0:self.radius+enemy.radius))/100;
  double Re=(enemy.range+(enemyRole==ObservedRole::Artillery?0:self.radius+enemy.radius))/100;
  double committed=ownRole==ObservedRole::Artillery?std::max(fc*Ri,.84):Re<Ri?Re+mk*(Ri-Re):fc*Ri;
  close(v2Preferred(self,enemy,k,1),committed);require(committed<=Ri,"v2 commit exceeds reach");
  if(ownRole==ObservedRole::Artillery)require(committed>=.84,"gun commit below minimum");
  close(v2Preferred(self,enemy,k,0),Re<Ri?committed+k.w*(Ri-Re)/2:(committed+Re+k.w*Ri)/2);
  if(Re>=Ri)close(v2Preferred(self,enemy,k,-1),Re+k.w*Ri);
  for(double ratio:{.5,1.0,2.0}){enemy.x=self.x+100*committed*ratio;enemy.y=self.y;std::map<UnitId,Memory> memory;memory[enemy.id].zOut=.5;k.lambdaTh=0;
   auto force=v2EnemyMotion(self,{&enemy},memory,k,1);close(force[0],k.G*(1-1/ratio));close(force[1],0);require(ratio==1?std::abs(force[0])<1e-12:force[0]*(ratio-1)>0,"v2 restoring sign");}
 }
 // Deterministic cap keeps the eight nearest; added threats sort by damage, distance and id.
 auto many=fixture();many.units.resize(1);self=many.units[0];self.range=20;
 for(unsigned n=0;n<18;++n){enemy.id=10+n;enemy.role=ObservedRole::Artillery;enemy.range=2000;enemy.minRange=0;enemy.x=self.x+100+n*10;enemy.y=self.y;many.units.push_back(enemy);}
 std::map<UnitId,Memory> mm;std::vector<const ObservedUnit*> ordered;
 for(size_t n=1;n<many.units.size();++n){auto* u=&many.units[n];ordered.push_back(u);mm[u->id].zOut=n<=8?0:.2;}
 mm[27].zOut=.9;mm[26].zOut=.8;many.units[15].x=many.units[14].x; // equal distance: id tie
 auto selected=v2EnemySet(self,ordered,mm);require(selected.size()==16,"v2 cap");
 for(size_t n=0;n<8;++n)require(selected[n]->id==10+n,"nearest not retained");
 require(selected[8]->id==27&&selected[9]->id==26&&selected[10]->id==18,"threat priority");
 require(selected[14]->id==22&&selected[15]->id==23,"threat distance/id tie");
 Knobs zeroWeight;zeroWeight.lambdaTh=0;auto mean=v2EnemyMotion(self,selected,mm,zeroWeight,1);double plain=0;
 for(auto u:selected)plain+=zeroWeight.G*(1-v2Preferred(self,*u,zeroWeight,1)/(std::hypot(u->x-self.x,u->y-self.y)/100))/selected.size();close(mean[0],plain);close(mean[1],0);
 zeroWeight.lambdaTh=3;auto weighted=v2EnemyMotion(self,selected,mm,zeroWeight,1);double numerator=0,denominator=0;
 for(auto u:selected){double weight=1+3*std::tanh(mm[u->id].zOut);denominator+=weight;numerator+=weight*zeroWeight.G*(1-v2Preferred(self,*u,zeroWeight,1)/(std::hypot(u->x-self.x,u->y-self.y)/100));}close(weighted[0],numerator/denominator);
 // Full threat attribution remains independent of the movement cap and of unrelated legal targets.
 for(auto arm:{Arm::Resonator,Arm::Morale}){
  auto seq=fixture();seq.units={seq.units[0],seq.units[2],seq.units[3]};seq.units[0].range=20;seq.units[1].x=seq.units[0].x+30;seq.units[2].x=seq.units[0].x+150;seq.units[2].range=200;
  Probe split(7,0,arm,{},"v2");split.prepare(seq);require(!split.memory().at(1).hadUnansweredThreat,"fabricated initial threat");
  seq.units[2].dealtToEnemy+=3;split.prepare(seq);require(split.memory().at(1).hadLegalTarget&&split.memory().at(1).hadUnansweredThreat,"reachable decoy masked threat");
  seq.units[2].x=1100;seq.units[0].takenFromEnemy+=3;split.prepare(seq);close(split.memory().at(1).zInUnanswered,(1-q)*3/seq.dt/100);close(split.memory().at(1).zInAnswered,0);
  require(!split.memory().at(1).hadUnansweredThreat,"outside enemy still a threat");
  seq.units[0].takenFromEnemy+=3;split.prepare(seq);close(split.memory().at(1).zInAnswered,(1-q)*3/seq.dt/100);
  seq.units[2].x=seq.units[0].x+30;split.prepare(seq);require(!split.memory().at(1).hadUnansweredThreat,"reachable threat labeled unanswered");
  auto branch=split.clone();seq.units[2].x=seq.units[0].x+150;branch->prepare(seq);require(dynamic_cast<S3Controller*>(branch.get())->memory().at(1).hadUnansweredThreat&&!split.memory().at(1).hadUnansweredThreat,"v2 clone attribution leaked");
  auto overflow=many;overflow.units[0].range=240;overflow.units.back().role=ObservedRole::Artillery;overflow.units.back().minRange=0;
  Probe capped(7,0,arm,{},"v2");capped.prepare(overflow);
  for(size_t n=1;n<overflow.units.size();++n)overflow.units[n].dealtToEnemy=double(100-n);
  capped.prepare(overflow);require(capped.memory().at(1).hadUnansweredThreat,"full threat label was capped");
  // No active threat: damage is answered even with an empty own legal set.
  auto inactive=fixture();inactive.units={inactive.units[0],inactive.units[2]};inactive.units[1].x=1100;Probe quiet(7,0,arm,{},"v2");quiet.prepare(inactive);inactive.units[0].takenFromEnemy=3;quiet.prepare(inactive);close(quiet.memory().at(1).zInUnanswered,0);close(quiet.memory().at(1).zInAnswered,(1-q)*3/inactive.dt/100);
 }
 }
 // Section 14 v3: effective-distance exclusion, exact hysteresis boundaries and unchanged kite band.
 {auto scene=fixture();auto self=scene.units[0],enemy=scene.units[2];
 for(auto ownRole:{ObservedRole::Melee,ObservedRole::Ranged,ObservedRole::Artillery})for(auto enemyRole:{ObservedRole::Melee,ObservedRole::Ranged,ObservedRole::Artillery})for(double er:{100.0,250.0,400.0})for(double fc:{.3,1.0})for(double width:{0.0,3.0})for(double minRange:{80.0,300.0}){
  self.role=ownRole;self.range=250;self.minRange=minRange;enemy.role=enemyRole;enemy.range=er;
  Knobs k;k.fc=fc;k.w=width;PairModes modes;
  const double Ri=(self.range+(ownRole==ObservedRole::Artillery?0:self.radius+enemy.radius))/100;
  const double Re=(enemy.range+(enemyRole==ObservedRole::Artillery?0:self.radius+enemy.radius))/100;
  const double dc=ownRole==ObservedRole::Artillery?std::max(fc*Ri,1.05*minRange/100):fc*Ri;
  for(double c:{0.0,.2,-.2,.200001,0.0,-.2,-.200001,0.0,.2}){
   double d=v3Preferred(self,enemy,k,c,modes);
   if(Re<Ri){close(d,v2Preferred(self,enemy,k,c));require(modes.empty(),"kite creates binary mode");}
   else{require(d==dc||d==Re+width*Ri,"v3 distance not binary");require(dc>=Re||!(dc<d&&d<Re),"v3 preferred distance in effective kill zone");}
  }
 }
 self=scene.units[0];enemy=scene.units[2];self.range=100;enemy.range=400;Knobs k;PairModes modes;
 const double dc=k.fc*1.2,de=4.2+k.w*1.2;
 close(v3Preferred(self,enemy,k,0,modes),dc); // c=0 initializes commit
 for(double c:{-.2,-.199,0.,.199,.2})close(v3Preferred(self,enemy,k,c,modes),dc);
 close(v3Preferred(self,enemy,k,-.200001,modes),de);
 for(double c:{.2,.199,0.,-.199,-.2})close(v3Preferred(self,enemy,k,c,modes),de);
 close(v3Preferred(self,enemy,k,.200001,modes),dc);
 auto second=enemy;second.id=90;close(v3Preferred(self,second,k,-.1,modes),de);
 close(v3Preferred(self,enemy,k,-.1,modes),dc);require(modes.size()==2,"pair modes merged");
 // Motion uses the binary distance with the unchanged weights and restoring sign.
 std::map<UnitId,Memory> memories;memories[enemy.id].zOut=.5;
 for(double c:{1.,-1.})for(double ratio:{.5,1.,2.}){double d=c>0?dc:de;enemy.x=self.x+100*d*ratio;enemy.y=self.y;
  auto force=v3EnemyMotion(self,{&enemy},memories,k,c,modes);close(force[0],k.G*(1-1/ratio));close(force[1],0);}
 }
 // Production memory is updated outside the movement cap, cloned independently, and removed on either death.
 for(auto arm:{Arm::Resonator,Arm::Morale,Arm::PushPull}){
  auto seq=fixture();seq.units[0].range=20;seq.units[1].range=20;seq.units[2].range=seq.units[3].range=400;
  ControllerParams params;if(arm!=Arm::PushPull){params={{"K",0},{"K_t",0},{"kappa",0}};
   if(arm==Arm::Resonator)params.insert({{"omega_melee",0},{"omega_ranged",0}});else params.insert({{"lambda_melee",0},{"lambda_ranged",0}});}
  Probe original(7,0,arm,params,"v3");original.prepare(seq);if(arm!=Arm::PushPull){original.inject(1,0);original.inject(2,0);}original.prepare(seq);
  const auto parentModes=original.pairModes();auto branch=original.clone();auto* copy=dynamic_cast<Probe*>(branch.get());
  require(copy&&copy->pairModes()==parentModes,"v3 clone lost modes");
  if(arm!=Arm::PushPull){copy->inject(1,arm==Arm::Resonator?3.141592653589793:-1);copy->prepare(seq);
   require(!copy->pairModes().at({1,3})&&original.pairModes()==parentModes,"v3 clone modes leaked");
   copy->inject(1,arm==Arm::Resonator?std::acos(.1):.1);copy->prepare(seq);require(!copy->pairModes().at({1,3}),"v3 production hysteresis lost escape");}
  seq.units[2].hp=0;original.prepare(seq);for(auto entry:original.pairModes())require(entry.first.second!=3,"dead enemy mode retained");
  seq.units[0].hp=0;original.prepare(seq);for(auto entry:original.pairModes())require(entry.first.first!=1,"dead own mode retained");
  seq.units[0].hp=seq.units[2].hp=100;original.prepare(seq);if(arm!=Arm::PushPull)original.inject(1,0);original.prepare(seq);
  require(original.pairModes().at({1,3}),"revived pair inherited dead mode");
  auto expanded=fixture();expanded.units.resize(1);expanded.units[0].range=20;
  for(unsigned n=0;n<20;++n){auto enemy=seq.units[2];enemy.id=20+n;enemy.x=400+10*n;expanded.units.push_back(enemy);}
  Probe capped(7,0,arm,params,"v3");capped.prepare(expanded);require(capped.pairModes().size()==20,"v3 modes truncated with movement cap");
 }
 // Artillery legality uses centre-distance min/max range, retained for attribution.
 auto gun=fixture();gun.units={gun.units[0],gun.units[2]};gun.units[0].role=ObservedRole::Artillery;gun.units[0].minRange=80;gun.units[1].x=gun.units[0].x+40;
 Probe splitGun(7,0,Arm::Morale);splitGun.prepare(gun);require(!splitGun.memory().at(1).hadLegalTarget,"inside artillery min range must be unanswered");
 gun.units[1].x=gun.units[0].x+120;gun.units[0].takenFromEnemy=3;splitGun.prepare(gun);close(splitGun.memory().at(1).zInUnanswered,(1-q)*3/gun.dt/100);
 // One enemy radial sign for all commitments, no ally term.
 for(double c:{-1.0,0.0,1.0})for(double ratio:{.5,1.0,2.0}){auto one=fixture();one.units={one.units[0],one.units[2]};double d=.75*one.units[0].range*(1+1.5*(1-c)/2);one.units[1].x=one.units[0].x+20+d*ratio;Probe p(7,0,Arm::Morale,{{"K",0},{"K_t",0},{"lambda_melee",0},{"lambda_ranged",0},{"kappa",0}});p.prepare(one);p.inject(1,c);p.prepare(one);auto action=p.decide(one,1);if(ratio==1)require(action.multiplier<1e-9,"rest point");else require((action.x-one.units[0].x)*(ratio-1)>0,"enemy sign");}
 // Empty group alignment is zero; target pressure selects the beaten enemy, not fallback phase 0.
 auto targets=fixture();Probe targeting(7,0,Arm::Resonator,{{"K",0},{"K_t",0},{"kappa",1},{"beta",0}});targeting.prepare(targets);targeting.inject(1,3.141592653589793);targets.units[2].takenFromEnemy=10;targeting.prepare(targets);require(targeting.decide(targets,1).target==3,"empty group score");targets.units.pop_back();targets.units.pop_back();targeting.prepare(targets);require(targeting.memory().at(1).target==0,"dead target reset");
 // Fallback alignment must be zero rather than an invented zero group state.
 auto fallback=fixture();Probe fp(7,0,Arm::Resonator,{{"K",0},{"K_t",0},{"kappa",0}});fp.prepare(fallback);fp.inject(1,3.141592653589793);fp.inject(2,0);fp.target(1,0);fp.target(2,3);fp.prepare(fallback);require(fp.decide(fallback,1).target==4,"resonator empty alignment is not zero");
 Probe fm(7,0,Arm::Morale,{{"K",0},{"K_t",0},{"lambda_melee",0},{"lambda_ranged",0},{"kappa",0}});fm.prepare(fallback);fm.inject(1,0);fm.inject(2,.8);fm.target(1,0);fm.target(2,3);fm.prepare(fallback);require(fm.decide(fallback,1).target==3,"morale empty alignment is not zero");
 auto hysteresis=fixture();hysteresis.units={hysteresis.units[0],hysteresis.units[2],hysteresis.units[3]};hysteresis.units[1].x=hysteresis.units[0].x+100;hysteresis.units[2].x=hysteresis.units[0].x+90;Probe pp(7,0,Arm::PushPull);pp.prepare(hysteresis);pp.target(1,3);pp.prepare(hysteresis);require(pp.decide(hysteresis,1).target==3,"pushpull hysteresis retain");hysteresis.units[2].x=hysteresis.units[0].x+50;pp.prepare(hysteresis);require(pp.decide(hysteresis,1).target==4,"pushpull hysteresis switch");
 auto art=fixture();art.units={art.units[0],art.units[2],art.units[3]};art.units[0].role=ObservedRole::Artillery;art.units[0].minRange=80;art.units[1].x=art.units[0].x+40;art.units[2].x=art.units[0].x+120;Probe arty(7,0,Arm::PushPull);arty.prepare(art);require(arty.decide(art,1).target==4,"artillery minimum range");
 // A nonempty exact zero-resultant group has no target torque.
 std::vector<ModelUnit> group{{0,0,.7,0,0,1,9},{0,0,0,0,0,2,9},{0,0,3.141592653589793,0,0,3,9}};Knobs k;k.K=0;k.Kt=3;close(stateRhs(group,Arm::Resonator,k)[0],0);
 // Clone inside a real world, cross-team/friendly accounting, raw-action sanitization.
 auto config=gameConfig();config.army={0,0,0};config.controllers[0].name="morale";auto w=World::create(std::make_shared<const Config>(config));auto own=w.add(0,Role::Melee,{100,100}),ally=w.add(0,Role::Melee,{110,100}),enemy=w.add(1,Role::Melee,{120,100});w.rebuildTeams();w.state[enemy.slot].protection=w.state[ally.slot].protection=0;w.damage(own,enemy,7);w.damage(own,ally,3);close(w.state[own.slot].dealtToEnemy,7);close(w.state[own.slot].friendlyDealt,3);close(w.stats.dealtToEnemy[0],7);close(w.stats.takenFromEnemy[1],7);close(w.stats.friendlyDealt[0],3);prepareControllers(w);
 auto* parent=dynamic_cast<S3Controller*>(w.controllers[0].get());auto memory=parent->memory();{auto branch=fork(w);coreStep(branch.world());}close(parent->memory().at(w.units[own.slot].id).state,memory.at(w.units[own.slot].id).state);
 applyControllerDecision(w,own.slot,{NAN,0,0,0,0});require(w.stats.controllerFailures[0]==1,"raw failure count");applyControllerDecision(w,own.slot,{100,100,0,0,0,true});require(w.stats.controllerFailures[0]==2,"flag failure count");
 // Diagnostics separate concentration from global synchrony; no phase data for morale.
 DiagnosticHistory history;std::vector<DiagnosticUnit> du{{1,7,100,100,0},{2,8,120,100,0},{3,8,140,100,0}};for(int i=0;i<=90;++i)history.append(i/30.0,du);auto dg=history.summarize(true);require(dg.windowReady&&dg.distinct==1&&dg.candidates.size()==1&&dg.candidates[0].size()==3,"diagnostic clustering");close(dg.coherence,1);close(dg.concentration,2.0/3);require(!history.summarize(false).coherenceValid&&history.summarize(false).candidates.empty(),"nonphase diagnostics");
 std::cout<<"{\"status\":\"passed\",\"checks\":[\"enemy_sign\",\"damage_recurrence\",\"decide_order\",\"degenerate\",\"failure\",\"clone\",\"diagnostics\"]}\n";
}
}
int main(int argc,char** argv){try{if(argc==1){contracts();return 0;}std::string line;std::map<UnitId,double> states;double maximum=0;uint64_t samples=0;while(std::getline(std::cin,line)){auto request=js::parse(line);if(std::string(argv[1])=="--equations")std::cout<<js::stringify(equations(request))<<'\n';
 else if(std::string(argv[1])=="--refinement"){std::vector<ModelUnit> a;std::set<UnitId> live;auto arr=js::get(request,"units");for(auto u:arr.p->items){ModelUnit x;x.x=js::num(js::get(u,"x"));x.y=js::num(js::get(u,"y"));x.state=js::num(js::get(u,"state"));x.rate=js::num(js::get(u,"rate"));x.pressure=js::num(js::get(u,"pressure"));x.id=uint32_t(js::num(js::get(u,"id")));x.target=uint32_t(js::num(js::get(u,"target")));live.insert(x.id);if(states.count(x.id))x.state=states.at(x.id);a.push_back(x);}
 for(auto it=states.begin();it!=states.end();)if(!live.count(it->first))it=states.erase(it);else ++it;
 Arm arm=js::str(js::get(request,"arm"))=="resonator"?Arm::Resonator:Arm::Morale;Knobs k;k.K=js::num(js::get(request,"K"));k.Kt=js::num(js::get(request,"K_t"));auto half=frozenStep(a,arm,k,js::num(js::get(request,"dt")),2);for(size_t i=0;i<a.size();++i){states[a[i].id]=half[i].state;double c=arm==Arm::Resonator?std::cos(half[i].state):half[i].state;double full=js::num(js::get(arr.p->items[i],"commitment"));require(std::isfinite(c)&&std::isfinite(full),"nonfinite refinement");maximum=std::max(maximum,std::abs(c-full));++samples;}}
 else throw std::invalid_argument("unknown contract mode");js::collect({},0);}if(std::string(argv[1])=="--refinement")std::cout<<js::stringify(js::obj({{"maximum",maximum},{"samples",double(samples)}}))<<'\n';return 0;}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}
