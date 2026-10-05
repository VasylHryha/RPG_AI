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
