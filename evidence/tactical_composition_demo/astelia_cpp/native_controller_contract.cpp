#include "native/controller_bridge.h"
#include "native/api.h"
#include <iostream>
#include <type_traits>
#include <utility>
using namespace astelia;
using ControllerObservation = astelia::control::Observation;
namespace {
void require(bool b,const char* message){if(!b)throw std::runtime_error(message);}
template<class T,class=void>struct hasWorld:std::false_type{};
template<class T>struct hasWorld<T,std::void_t<decltype(std::declval<T>().world)>>:std::true_type{};
static_assert(!hasWorld<ControllerObservation>::value,"observation exposes World");
static_assert(!hasWorld<ObservedUnit>::value,"unit view exposes World");
static_assert(std::is_aggregate_v<ControllerObservation>&&std::is_aggregate_v<ObservedUnit>);
// Structured bindings assert the COMPLETE aggregate field counts. Unlike a
// hand-written list alone this fails compilation if a hidden member is added.
void fieldContract(const ControllerObservation& o){
  const auto& [t,dt,width,height,units]=o;
  require(t==o.t&&dt==o.dt&&width==o.width&&height==o.height&&&units==&o.units,"world view fields");
  const auto& [id,team,role,x,y,vx,vy,hp,maxhp,radius,speed,range,dmg,cd,cdMax,target,dealt,taken,minRange,dealtToEnemy,takenFromEnemy,friendlyDealt,friendlyTaken]=units.front();
  require(id==units.front().id&&dealt==units.front().damageDealt&&taken==units.front().damageTaken,"unit view fields");
  require(minRange==units.front().minRange&&dealtToEnemy==units.front().dealtToEnemy&&takenFromEnemy==units.front().takenFromEnemy&&friendlyDealt==units.front().friendlyDealt&&friendlyTaken==units.front().friendlyTaken,"S3 unit view fields");
  std::cout<<"{\"world_fields\":[\"t\",\"dt\",\"width\",\"height\"],\"unit_fields\":[\"id\",\"team\",\"role\",\"x\",\"y\",\"vx\",\"vy\",\"hp\",\"maxhp\",\"radius\",\"speed\",\"range\",\"dmg\",\"cd\",\"cdMax\",\"target\",\"damageDealt\",\"damageTaken\",\"minRange\",\"dealtToEnemy\",\"takenFromEnemy\",\"friendlyDealt\",\"friendlyTaken\"],\"status\":\"passed\"}\n";
}
class Recording final:public Controller {
public:
  int prepares=0;std::vector<UnitId> calls;double firstX=0;bool nullClone=false;
  using Controller::Controller;
  void prepare(const ControllerObservation& o)override{++prepares;firstX=o.units.front().x;}
  UnitDecision decide(const ControllerObservation& o,UnitId id)override{calls.push_back(id);require(o.units.front().x==firstX,"snapshot mutated during decisions");
    for(const auto& u:o.units)if(u.id==id)return {u.x,u.y,0,0,0};throw std::runtime_error("missing observed self");}
  std::unique_ptr<Controller> clone()const override{return nullClone?nullptr:std::make_unique<Recording>(*this);}
  double draw(){return random_();}
};
Config empty(){auto c=sandboxConfig();c.army={0,0,0};c.controllers[0].name="hold";return c;}
}
int main(){try{
  auto w=create(empty());const auto a=w.add(0,Role::Melee,{100,100}),b=w.add(1,Role::Ranged,{110,100}),ally=w.add(0,Role::Ranged,{100,120});
  w.rebuildTeams();prepareControllers(w);fieldContract(w.observations[0]);
  require(w.observations[0].units.size()==3,"missing observed unit");
  const auto snapshot=w.observations[0];w.units[a.slot].pos.x=101;require(snapshot.units[0].x==100,"view aliases world");
  w.units[a.slot].target=b;w.damage(a,b,7);w.damage(b,a,11);prepareControllers(w);
  const auto& av=w.observations[0].units[0];const auto& bv=w.observations[0].units[1];
  require(av.damageDealt==7&&av.damageTaken==11&&bv.damageDealt==11&&bv.damageTaken==7&&av.target==w.units[b.slot].id,"damage counters must include both teams");
  require(av.vx==w.units[a.slot].velocity.x&&av.cdMax==w.state[a.slot].cooldownMax&&av.maxhp==w.units[a.slot].maxhp,"view values differ from authority");
  const auto enemy=w.units[b.slot].id;
  applyControllerDecision(w,a.slot,{-10,1e9,2,-1,enemy});const auto& clipped=w.state[a.slot].decision;
  require(clipped.goal.x==0&&clipped.goal.y==w.config->height&&clipped.multiplier==1&&clipped.stop==0&&w.units[a.slot].target==b,"clipping/target validation");
  applyControllerDecision(w,a.slot,{100,100,-1,0,enemy});require(w.state[a.slot].decision.multiplier==0,"negative speed");
  for(auto value:{NAN,INFINITY,-INFINITY})for(int field=0;field<4;++field){UnitDecision d{110,110,1,0,enemy};
    if(field==0)d.x=value;if(field==1)d.y=value;if(field==2)d.multiplier=value;if(field==3)d.stop=value;
    applyControllerDecision(w,a.slot,d);require(!w.units[a.slot].target&&w.state[a.slot].decision.multiplier==0&&w.state[a.slot].decision.goal.x==w.units[a.slot].pos.x,"non-finite decision did not hold");}
  applyControllerDecision(w,a.slot,{110,110,1,0,w.units[ally.slot].id});require(!w.units[a.slot].target,"own target accepted");
  w.damage(a,b,1000);applyControllerDecision(w,a.slot,{110,110,1,0,enemy});require(!w.units[a.slot].target,"dead target accepted");
  applyControllerDecision(w,a.slot,{110,110,1,0,999999});require(!w.units[a.slot].target,"unknown target accepted");
  w.units[a.slot].target={};w.reclaim();const auto replacement=w.add(1,Role::Ranged,{115,100});require(replacement.slot==b.slot&&replacement.generation!=b.generation&&w.units[replacement.slot].id!=enemy&&!w.resolve(b),"slot identity reused");
  applyControllerDecision(w,a.slot,{110,110,1,0,enemy});require(!w.units[a.slot].target,"stale id accepted after slot reuse");
  prepareControllers(w);require(w.observations[0].units.back().damageDealt==0&&w.observations[0].units.back().damageTaken==0,"reused slot inherited damage");
  const auto record=std::make_unique<Recording>(w.config->seed,0);w.controllers[0]=record->clone();
  coreStep(w);auto* observed=dynamic_cast<Recording*>(w.controllers[0].get());std::vector<UnitId> expected;
  for(auto slot:w.order)if(w.units[slot].team==0)expected.push_back(w.units[slot].id);
  require(observed&&observed->prepares==1&&observed->calls==expected,"prepare/order contract");
  auto branch=fork(w);auto* copied=dynamic_cast<Recording*>(branch.world().controllers[0].get());require(copied&&copied!=observed&&copied->calls==observed->calls,"controller state not cloned");
  require(copied->draw()==observed->draw(),"branch RNG not copied");coreStep(branch.world());require(observed->prepares==1&&copied->prepares==2,"branch state aliases parent");
  observed->nullClone=true;bool failedClone=false;try{auto failed=fork(w);}catch(const std::logic_error& e){failedClone=std::string(e.what())=="controller clone returned null";}
  require(failedClone&&observed->prepares==1,"null clone silently fell back to built-in brain");observed->nullClone=false;
  {auto recovered=fork(w);require(recovered.world().controllers[0]!=nullptr,"failed clone leaked branch lease");}
  const auto external=makeController({"nearest",{}},123,0);const auto hold=makeController({"hold",{}},123,1);
  ControllerObservation test{0,.1,650,700,{{1,0,ObservedRole::Melee,100,100,0,0,10,10,5,10,20},{2,1,ObservedRole::Ranged,200,100,0,0,10,10,6},{3,1,ObservedRole::Artillery,150,100}}};
  const auto nearestDecision=external->decide(test,1);require(nearestDecision.target==3&&nearestDecision.x==150&&nearestDecision.multiplier==1&&nearestDecision.stop==23,"nearest floor decision");
  const auto holdDecision=hold->decide(test,2);require(holdDecision.x==200&&holdDecision.multiplier==0&&!holdDecision.target,"hold decision");
  auto cc=gameConfig();cc.army={2,4,2};cc.brains[0]=Brain::Rules;cc.controllers[0].name="nearest";cc.skills[0].abilities=AbilityPolicy::Coordinated;cc.lookahead[0].enabled=true;
  auto controlled=create(cc);require(!controlled.packs[0].enabled&&controlled.config->skills[0].abilities==AbilityPolicy::Auto,"external planning/abilities policy");
  const auto profile=buildProfile(*controlled.config,0);require(profile.controller.name=="nearest"&&profile.controller.params.empty()&&buildProfile(*controlled.config,1).controller.name.empty(),"native profile dropped controller");
  coreStep(controlled);require(controlled.work->searchCalls==0&&controlled.work->artilleryRollouts==0,"external side ran pack planners");
  auto nearestClone=external->clone();require(nearestClone->decide(test,1).target==3,"nearest clone");
  for(auto role:{Role::Melee,Role::Ranged,Role::Artillery}){w.units[a.slot].role=role;applyControllerDecision(w,a.slot,{100,100,0,0,w.units[replacement.slot].id});
    require(w.state[a.slot].decision.release==(role==Role::Melee?Release::Melee:role==Role::Ranged?Release::Direct:Release::Artillery),"role release relation");}
  w.state[a.slot].guardUntil=w.time+1;applyControllerDecision(w,a.slot,{200,200,1,0,w.units[replacement.slot].id});require(!w.state[a.slot].decision.move&&w.state[a.slot].decision.release==Release::None,"guard body reflex changed");
  const auto sizeBefore=w.units.size();bool rejectedPlayer=false;try{w.add(0,Role::Player,{300,300});}catch(const std::invalid_argument&){rejectedPlayer=true;}
  require(rejectedPlayer&&w.units.size()==sizeBefore,"unsupported player body mutated external world");
  w.units[a.slot].role=Role::Player;rejectedPlayer=false;try{applyControllerDecision(w,a.slot,{100,100,0,0,0});}catch(const std::invalid_argument&){rejectedPlayer=true;}
  require(rejectedPlayer,"direct bridge accepted special player weapon path");
  std::cout<<"native controller contracts passed\n";return 0;
}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}
