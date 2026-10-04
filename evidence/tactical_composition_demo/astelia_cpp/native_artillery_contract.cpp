#include "native/artillery.h"
#include <iostream>
#include <sstream>
#include <iomanip>
using namespace astelia;
namespace {
void require(bool b,const char* text){if(!b)throw std::runtime_error(text);}
World empty(Config c){c.army={0,0,0};return World::create(std::make_shared<const Config>(c));}
void predictionOracle(){for(bool game:{false,true})for(bool exact:{false,true})for(int dodge=0;dodge<3;++dodge)for(bool lock:{false,true}){
  auto c=game?gameConfig():sandboxConfig();c.army={2,2,2};c.width=650;c.brains={Brain::Formation,Brain::Formation};c.skills[0].artyExact=exact;c.skills[0].artyOwn=true;c.skills[1].dodgeShells=dodge==1;c.skills[1].smartShells=dodge==2;
  auto w=World::create(std::make_shared<const Config>(c));for(size_t j=0;j<w.teams[1].size();++j){auto& u=w.units[w.teams[1][j]];u.pos={380+j*15.0,300+j*10.0};u.smoothVelocity={-20,5};}
  w.units[w.teams[0][0]].pos={390,300};if(lock)w.units[w.teams[1][0]].target=w.reference(w.teams[0][0]);
  std::vector<PredictedShell> planned{{{380,300},.6,30,45,0},{{410,310},.9,22,40,0}};const auto p=predictVolley(w,0,planned,.9);
  std::cout<<"{\"per\":["<<p.per[0]<<','<<p.per[1]<<"],\"val\":["<<p.value[0]<<','<<p.value[1]<<"],\"own\":"<<p.own<<",\"smart\":"<<smartVolley(w,0,planned)<<",\"snap\":[";
  for(size_t i=0;i<p.snapshot.size();++i){if(i)std::cout<<',';const auto& q=p.snapshot[i];std::cout<<'['<<q.point.x<<','<<q.point.y<<','<<q.hp<<']';}std::cout<<"]}\n";}}
void mechanics(){auto c=sandboxConfig();c.brains[0]=Brain::Formation;c.skills[0].artyPlan=true;c.skills[1].dodgeShells=false;auto w=empty(c);const auto gun=w.add(0,Role::Artillery,{100,200}),target=w.add(1,Role::Ranged,{250,200});w.units[gun.slot].target=target;
  const PredictedShell shell{{250,200},1,26,45,0};auto prediction=predictVolley(w,0,{shell},1);require(prediction.per[0]==26&&prediction.snapshot[0].hp==90,"stationary prediction damage/snapshot order incorrect");
  artilleryVolley(w,0);require(w.shots.empty()&&w.shells.size()==1&&w.units[gun.slot].cooldown>0,"sandbox null-coming repair did not fire a real shell");
  require(w.shells[0].hasPrediction,"planner dropped prediction from launched shell");
  Attack delayed;delayed.family=AttackFamily::Sweep;PlannedShot q;q.gun=gun;q.point={250,200};q.at=2;delayed.shots.push_back(q);w.units[gun.slot].cooldown=0;launch(w,0,delayed);
  require(w.packs[0].artilleryQueue.size()==1&&w.tactical[gun.slot].reservedUntil==2.3,"delayed gun did not reserve");w.time=2;artilleryVolley(w,0);require(w.packs[0].artilleryQueue.empty()&&w.shells.size()==2,"delayed sandbox shot did not drain");
  auto cg=gameConfig();cg.brains[0]=Brain::Formation;cg.skills[0].artyPlan=true;auto g=empty(cg);const auto gg=g.add(0,Role::Artillery,{100,200}),gt=g.add(1,Role::Ranged,{250,200});g.units[gg.slot].target=gt;
  delayed.shots[0].gun=gg;delayed.shots[0].at=.5;launch(g,0,delayed);g.time=.3;g.state[gg.slot].prep=windup(g,gg.slot)+.01;artilleryVolley(g,0);
  require(g.shells.size()==1&&g.packs[0].artilleryQueue.empty()&&g.state[gg.slot].prep==0,"game queue held prepared cast past release");
  auto source=g.reference(gg.slot);g.stats.artillery=99;auto branch=g.branches().fork(g);branch.world().packs[0].artilleryQueue.push_back(delayed.shots[0]);branch.world().shells[0].prediction=999;
  require(g.packs[0].artilleryQueue.empty()&&g.shells[0].prediction!=999&&branch.world().stats.artillery==0,"branch shared artillery queue/prediction/telemetry");
  require(source==gg,"stable gun handle changed");
}
void gates(){auto c=gameConfig();c.skills[0].holdWave=.45;c.brains[0]=Brain::Formation;auto w=empty(c);const auto one=w.add(0,Role::Artillery,{100,200}),two=w.add(0,Role::Artillery,{110,240}),player=w.add(1,Role::Player,{250,200});
  w.units[one.slot].target=w.units[two.slot].target=player;w.state[one.slot].prep=.1;w.state[one.slot].castTime=0;w.time=.2;
  require(!fireGate(w,two.slot),"wave gate did not hold behind player bait");w.time=.46;require(fireGate(w,two.slot),"wave gate did not release on schedule");
  w.players[w.state[player.slot].player].dashReady=4;w.time=.2;require(fireGate(w,two.slot),"wave held while player dash unavailable");
}
void rollout(){auto c=gameConfig();c.width=650;c.dt=.05;c.duration=2;c.brains[0]=Brain::Formation;c.skills[0].artyPlan=true;c.skills[0].artyBattery=true;c.skills[0].artyFollow=true;
  auto& ro=c.skills[0].rollout;ro.enabled=ro.ltd2=true;ro.top=5;ro.horizon=.15;ro.dt=.05;ro.shape={AttackFamily::Battery,AttackFamily::Split,AttackFamily::Herd};auto w=empty(c);
  for(int i=0;i<4;++i)w.add(0,Role::Artillery,{200,260+i*20.0});for(int i=0;i<8;++i)w.add(1,i<6?Role::Ranged:Role::Artillery,{350+i*3.0,300+i*2.0});
  for(auto i:w.teams[0]){w.units[i].target=w.reference(w.teams[1][0]);w.state[i].prep=windup(w,i)+.01;}w.packs[0].anchor={220,300};
  const auto rng=w.random.state;artilleryVolley(w,0);require(w.work->artilleryRollouts>=5&&w.work->forks==w.work->artilleryRollouts&&w.work->branchSteps>=3*w.work->forks,"artillery rollout skipped shortlist or horizon work");
  require(w.time==0&&w.random.state==rng&&w.shells.size()+w.packs[0].artilleryQueue.size()==4,"rollout changed parent or fired gun more than once");
  auto copied=w.branches().fork(w);copied.world().time=1;const auto before=w.work->artilleryRollouts;artilleryVolley(copied.world(),0);require(w.work->artilleryRollouts==before,"light branch recursively rolled out");
  Attack attack;attack.family=AttackFamily::Focus;PlannedShot q;q.gun=w.reference(w.teams[0][0]);q.point={350,300};q.at=w.time;attack.shots.push_back(q);
  const auto hps=w.units[w.teams[1][0]].hp;artilleryOutcome(w,0,attack,ro);require(w.units[w.teams[1][0]].hp==hps&&w.time==0,"outcome branch changed parent health/time");
}
}
int main(int argc,char** argv){try{std::cout<<std::setprecision(17);if(argc>1&&std::string(argv[1])=="--oracle"){predictionOracle();return 0;}mechanics();gates();rollout();std::cout<<"native artillery contracts passed\n";}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}
