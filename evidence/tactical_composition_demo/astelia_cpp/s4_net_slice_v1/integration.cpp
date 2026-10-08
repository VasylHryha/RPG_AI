// Bounded scripted lifecycle fixtures through the actual overlay. No outcome reads.
#include "integration.h"
#include "teacher.h"
#include "controller_bridge.h"
using namespace astelia;using namespace net_slice;
namespace {
void require(bool b,const char* why){if(!b)throw std::runtime_error(why);}
// Fixture-only controller: perturb geometry between decision and action at tick13.
class Perturb final:public control::Controller {
public:
 World* world;std::string mode;
 Perturb(World* w,std::string m):Controller(1,1),world(w),mode(m){}
 void prepare(const control::Observation&)override{}
 UnitDecision decide(const control::Observation&,UnitId)override {
  auto* h=dynamic_cast<Host*>(world->controllers[0].get());
  if(h->tick==13&&h->projected.at(world->units[0].id).release&&world->state[0].decision.release==Release::Artillery){
   if(mode=="aim_veto")world->units[0].pos={200,400};
   if(mode=="no_launch")world->units[1].pos={900,400};
   if(mode=="walk_across"){world->units[1].pos={719,400};auto& c=h->casts.at(world->units[0].id);c.lockedAim={719,400};auto& d=world->state[0].decision;d.move=true;d.goal={300,400};d.multiplier=1;}
  }
  const auto& u=world->units[1];return {u.pos.x,u.pos.y,0,0,0};
 }
 std::unique_ptr<control::Controller> clone()const override{return std::make_unique<Perturb>(*this);}
};
unsigned ownerFirstSeed(){for(unsigned seed=1;seed<100;++seed){Rng rng(toUint32(seed*73856093.)^toUint32(13.*19349663.));rng();rng();if(rng()>=.5)return seed;}throw std::logic_error("shuffle seed");}
js::V run(const Weights& source,const std::string& mode){
 auto cfg=std::make_shared<Config>(gameConfig());cfg->seed=ownerFirstSeed();cfg->abilities=false;cfg->skills[0]=CombatSkills{};cfg->skills[1]=CombatSkills{};cfg->width=1400;cfg->height=800;cfg->dt=1./30;
 World w(cfg);auto own=w.add(0,Role::Artillery,{400,400});auto enemy=w.add(1,Role::Artillery,{650,400});
 w.units[own.slot].range=320;w.units[own.slot].speed=80;w.units[own.slot].damage=0;w.state[own.slot].minRange=30;w.state[own.slot].windup=.3;w.state[own.slot].energy=100;w.state[own.slot].cost=6;w.state[own.slot].cooldownMax=10;
 Weights weights=source;if(mode=="auto_hold"||mode=="death"||mode=="body")weights.values["readout.bias"][47]=-1;
 if(mode=="cooldown")w.units[own.slot].cooldown=3./30;
 auto h=std::make_unique<Host>(0,std::make_shared<const Weights>(weights));w.controllers[0]=std::move(h);
 // Both bodies are non-firing on the opposite side; fixture perturbation is explicit.
 w.controllers[1]=std::make_unique<Perturb>(&w,mode);w.rebuildTeams();w.liveGrid.build(w.units,w.active,1400,800,40);
 Collector all;uint64_t start=0,launch=0,cancel=0,consume=0,noLaunch=0,veto=0;bool winding=false,hold=false;
 for(unsigned tick=1;tick<=60;++tick){
  if(mode=="death"&&tick==5){w.units[enemy.slot].alive=false;w.units[enemy.slot].hp=0;}
  if(mode=="body"&&tick==10)w.state[own.slot].guardUntil=2.5;
  coreStep(w);auto* host=dynamic_cast<Host*>(w.controllers[0].get());
  for(auto e:host->collector.drain().p->items){auto stage=js::str(js::get(e,"stage"));auto t=uint64_t(js::num(js::get(e,"tick")));if(stage=="cast_start"&&!start)start=t;if(stage=="launch"&&!launch)launch=t;if(stage=="consume")consume=t;if(stage=="cancel")cancel=t;if(stage=="consumed_without_launch")noLaunch=t;if(stage=="act_veto")veto=t;if(stage=="projection"){auto state=js::str(js::get(js::get(e,"value"),"state"));require(state!="released","projection cannot claim release before action");if((t==7||t==13)&&state=="winding")winding=true;if(state=="prepared")hold=true;}all.events.push_back(e);}
 }
 require(start&&winding,"integration start/winding across cadence");
 if(mode=="permission")require(start==1&&launch==13&&consume==13,"first decision-ready permission release timing");
 if(mode=="auto_hold")require(hold&&launch==15,"hold expires six ticks after tick9 ready");
 if(mode=="cooldown")require(start==7&&launch==19,"cooldown expiration cannot use tick1 permission");
 if(mode=="death"||mode=="body")require(cancel==15&&!launch,"illegal/dead target cancel bound");
 if(mode=="aim_veto")require(veto==13&&launch!=13&&consume!=13,"failed entry aim has no consume or launch");
 if(mode=="no_launch")require(consume==13&&noLaunch==13&&!launch,"native pre-walk target failure consumes without launch");
 if(mode=="walk_across")require(launch==13,"entry aim legal even when walk crosses range");
 return js::obj({{"scenario",mode},{"ticks",60.},{"start",double(start)},{"launch",double(launch)},{"cancel",double(cancel)},{"consume",double(consume)},{"no_launch",double(noLaunch)},{"veto",double(veto)},{"events",all.drain()}});
}
js::V drillDispatch(const Weights& weights,const std::string& cell){
 auto cfg=std::make_shared<Config>(gameConfig());cfg->abilities=false;cfg->skills[0]=CombatSkills{};cfg->skills[1]=CombatSkills{};cfg->width=1400;cfg->height=800;cfg->dt=1./30;
 World w(cfg);w.add(0,Role::Artillery,{400,400});w.add(1,Role::Artillery,{650,400});
 for(double y:{360.,440.})w.add(0,Role::Melee,{240,y});
 if(cell=="D1-static")for(double y:{360.,440.})w.add(1,Role::Melee,{900,y});
 for(unsigned i=0;i<2;++i){w.units[i].damage=0;w.units[i].range=320;w.state[i].windup=.3;w.state[i].cooldownMax=10;}
 auto h=std::make_unique<Host>(0,std::make_shared<const Weights>(weights),true);h->cell=cell;w.controllers[0]=std::move(h);w.rebuildTeams();w.liveGrid.build(w.units,w.active,1400,800,40);
 bool preparedEnemy=false,enemyShell=false;
 for(unsigned tick=1;tick<=60;++tick){coreStep(w);preparedEnemy|=w.state[1].prep>0;for(const auto& sh:w.shells){auto* src=w.resolve(sh.source);if(src&&src->team==1)enemyShell=true;}for(auto i:w.active)if(w.units[i].role!=Role::Artillery){require(w.state[i].prep==0&&!w.units[i].target,"real scaffolds do not prepare or target");require(w.units[i].pos.x==(w.units[i].team?900:240),"real scaffolds remain stationary");}}
 if(cell=="D1-static")require(!preparedEnemy&&!enemyShell,"D1 actual dispatch emits no enemy preparation or shells");else require(preparedEnemy&&enemyShell,"D2 actual dispatch prepares and launches native shells");
 return js::obj({{"cell",cell},{"ticks",60.},{"enemy_prepared",preparedEnemy},{"enemy_launched",enemyShell},{"scaffold_entry_gate",true}});
}

void provisionalAndReset(const Weights& weights){
 auto cfg=std::make_shared<Config>(gameConfig());cfg->abilities=false;World w(cfg);w.add(0,Role::Artillery,{400,400});w.add(1,Role::Artillery,{650,400});w.rebuildTeams();w.liveGrid.build(w.units,w.active,1400,800,40);
 auto h=std::make_unique<Host>(0,std::make_shared<const Weights>(weights));auto* host=h.get();w.controllers[0]=std::move(h);bind(w);prepareControllers(w);
 auto id=w.units[0].id;auto c=host->cache.at(id);c.release=false;c.aim={900,400};host->casts[id].startedAck(1,c);w.state[0].prep=.1;w.state[0].windup=.3;
 c.aim={600,400};host->cache[id]=c;net_slice::decide(w,0);require(host->casts[id].lockedAim.x==600&&!host->casts[id].aimLocked,"latest cached provisional aim replaces stale start aim");require(host->projected[id].reason=="native_progress","provisional aim does not create stale range block");
 c.aim={700,400};c.release=true;c.releaseOpportunity=true;host->cache[id]=c;w.state[0].prep=.3;net_slice::decide(w,0);require(host->casts[id].aimLocked&&host->casts[id].lockedAim.x==700,"permission locks latest cached aim");
 Shell shell;shell.pos={700,400};shell.born=w.time;shell.at=1;
 for(const char* ab:{"intact","K0","no_geometry_to_mode","frozen_phase","no_reset"}){host->ablation=ab;host->phases[id]=.7;launchedAck(w,0,shell);bool retain=std::string(ab)=="frozen_phase"||std::string(ab)=="no_reset";require(host->phases[id]==(retain?.7:0),"actual-launch reset intervention ledger");}
}

void boundary(const Weights& source){auto a=std::make_shared<Config>(gameConfig()),b=std::make_shared<Config>(*a);a->abilities=b->abilities=false;b->skills[1].artyPlan=true;b->skills[1].dodgeShells=true;b->skills[1].lobLead=true;World x(a),y(b);for(auto* w:{&x,&y}){w->add(0,Role::Artillery,{400,400});w->add(1,Role::Artillery,{650,400});w->rebuildTeams();}y.state[1].energy=987;y.state[1].cost=99;y.random.state=12345;y.spawnRandom.state=98765;auto s=snapshot(x,0,1,1,"boundary",{},{}),t=snapshot(y,0,1,1,"boundary",{},{});require(js::stringify(s)==js::stringify(t),"private native changes must not alter wire");Host hx(0,std::make_shared<const Weights>(source)),hy(0,std::make_shared<const Weights>(source));hx.tick=hy.tick=1;hx.views={s};hy.views={t};hx.prepare({});hy.prepare({});require(js::stringify(json(hx.cache.at(1)))==js::stringify(json(hy.cache.at(1))),"private native changes must not alter policy");}
void permissions(){auto cfg=std::make_shared<Config>(gameConfig());World w(cfg);w.add(0,Role::Artillery,{400,400});w.add(1,Role::Artillery,{650,400});w.rebuildTeams();std::vector<double> logits(81,-1);logits[0]=logits[34]=logits[46]=logits[47]=logits[48]=1;
 for(bool winding:{false,true}){w.units[0].cooldown=winding?0:2./30;w.state[0].prep=winding?.2:0;w.state[0].windup=.3;auto s=snapshot(w,0,1,1,"permission",{},{});auto student=intent(decode(s,logits));auto teacher=slice_teacher::query({s}).actions.at(1);require(!student.start&&!student.release&&!teacher.start&&!teacher.release,"cooldown/winding decisions cannot authorize future opportunity");Cast networkCast,teacherCast;for(unsigned tick=1;tick<=6;++tick){CastInput input{tick,true,false,true,true,true,tick<3&&!winding?.05:0,100,0,winding?.2+(tick-1)/30.:0,.3,1./30};auto n=networkCast.project(input,student),t=teacherCast.project(input,teacher);require(n.start==t.start&&n.release==t.release&&n.cancel==t.cancel,"equal cached permissions must have equal cooldown/winding lifecycle");require(!n.start&&!n.release,"no later opportunity without permission; auto bound beyond cache");}}
}
}
js::V integratedFixtures(const Weights& weights){boundary(weights);permissions();provisionalAndReset(weights);auto drills=js::arr({drillDispatch(weights,"D1-static"),drillDispatch(weights,"D2-shellfire")});js::Args rows;for(const char* mode:{"permission","auto_hold","cooldown","aim_veto","no_launch","walk_across","death","body"})rows.push_back(run(weights,mode));return js::obj({{"drill_dispatch",drills},{"boundary_invariance",true},{"decision_permission_parity",true},{"provisional_aim_and_reset",true},{"scenarios",js::arr(std::move(rows))},{"scope","eight scripted 60-tick lifecycle fixtures; no fight outcomes read"}});}
