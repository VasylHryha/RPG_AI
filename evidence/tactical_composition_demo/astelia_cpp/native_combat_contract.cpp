#include "native/world.h"
#include <iostream>

using namespace astelia;
namespace {
void require(bool b,const char* message){if(!b)throw std::runtime_error(message);}
void close(double a,double b,const char* message){require(std::abs(a-b)<1e-9,message);}
World empty(Config c){c.army={0,0,0};return World::create(std::make_shared<const Config>(std::move(c)));}
void stationary(World& w){for(auto i:w.active){w.units[i].speed=w.state[i].baseSpeed=0;w.units[i].cooldown=99;}}
void casts() {
  auto c=gameConfig();c.dt=.1;auto w=empty(c);
  auto a=w.add(0,Role::Melee,{100,200}),b=w.add(1,Role::Melee,{150,200});
  coreStep(w);close(w.state[a.slot].prep,.1,"game cast did not start in reach");close(w.units[a.slot].cooldown,1.8,"cooldown did not run from cast start");
  for(int i=0;i<3;++i)coreStep(w);close(w.units[b.slot].hp,258,"cast hit before windup");
  coreStep(w);close(w.units[b.slot].hp,243,"cast damage/protection/floor incorrect");close(w.state[a.slot].prep,0,"released cast kept prep");
  auto committed=empty(c);a=committed.add(0,Role::Melee,{100,200});b=committed.add(1,Role::Melee,{150,200});
  coreStep(committed);committed.units[b.slot].pos={1000,200};committed.liveGrid.moved(b.slot,committed.units[b.slot].pos);
  for(int i=0;i<4;++i)coreStep(committed);
  close(committed.state[a.slot].prep,0,"committed cast stopped progressing out of reach");close(committed.units[b.slot].hp,258,"out of reach committed swing landed");
  auto energy=empty(c);a=energy.add(0,Role::Ranged,{100,200});b=energy.add(1,Role::Melee,{240,200});
  energy.state[a.slot].energy=5;energy.state[a.slot].energyRegen=0;coreStep(energy);close(energy.state[a.slot].prep,0,"cast admitted without energy");
  energy.state[a.slot].energy=6;coreStep(energy);close(energy.state[a.slot].energy,0,"cast did not pay energy at start");
  energy.units[b.slot].pos={1000,200};energy.liveGrid.moved(b.slot,energy.units[b.slot].pos);
  for(int i=0;i<5;++i)coreStep(energy);require(!energy.shots.size(),"out of reach direct cast released projectile");
  auto capped=c;capped.attackerCap=1;auto cap=empty(capped);
  a=cap.add(0,Role::Melee,{100,200});auto a2=cap.add(0,Role::Melee,{100,240});b=cap.add(1,Role::Melee,{150,220});coreStep(cap);
  require((cap.state[a.slot].prep>0)+(cap.state[a2.slot].prep>0)==1,"attacker cap not enforced");
  auto sb=sandboxConfig();sb.windUp=true;sb.dt=.1;auto warm=empty(sb);
  a=warm.add(0,Role::Ranged,{100,200});b=warm.add(1,Role::Melee,{220,200});
  for(int i=0;i<4;++i)coreStep(warm);require(warm.shots.empty(),"sandbox shot skipped windup");coreStep(warm);
  close(warm.units[a.slot].cooldown,.5,"sandbox reload was not shortened by windup");
}
void projectiles() {
  auto c=gameConfig();c.dt=.1;auto w=empty(c);
  auto src=w.add(0,Role::Ranged,{20,200}),ally=w.add(0,Role::Ranged,{60,200}),enemy=w.add(1,Role::Ranged,{130,200});stationary(w);
  Shot shot;shot.source=src;shot.target=enemy;shot.pos={20,200};shot.direction={1,0};shot.speed=500;shot.left=200;shot.damage=10;
  w.shots.push_back(shot);coreStep(w);close(w.units[ally.slot].hp,84,"game straight shot spared ally");close(w.units[enemy.slot].hp,92,"shot flew through ally");
  auto piercing=empty(c);src=piercing.add(0,Role::Player,{20,200});auto first=piercing.add(1,Role::Ranged,{60,200});enemy=piercing.add(1,Role::Ranged,{130,200});stationary(piercing);
  piercing.players[piercing.state[src.slot].player].dashUntil=100; // suppress autonomous casts
  shot.source=src;shot.target=enemy;shot.pierce=2;shot.ordinal=1;piercing.shots.push_back(shot);coreStep(piercing);
  close(piercing.units[first.slot].hp,84,"piercing first hit missing");require(piercing.shots.size()==1&&piercing.shots[0].pierce==1,"piercing shot stopped at first enemy");
  coreStep(piercing);coreStep(piercing);require(piercing.units[enemy.slot].hp<=84,"piercing second hit missing");
  require(piercing.units[first.slot].hp>=83,"piercing hit same body repeatedly");
  auto lob=empty(c);src=lob.add(0,Role::Artillery,{100,200});ally=lob.add(0,Role::Ranged,{160,200});enemy=lob.add(1,Role::Ranged,{185,200});stationary(lob);
  Shell shell;shell.pos={165,200};shell.source=src;shell.at=.1;shell.damage=18;shell.splash=40;shell.lob=true;lob.shells.push_back(shell);coreStep(lob);
  close(lob.units[ally.slot].hp,77,"game lob spared ally");close(lob.units[enemy.slot].hp,77,"game lob missed enemy");close(lob.units[src.slot].hp,181,"game lob hit source");
}
void defenses() {
  auto c=gameConfig();auto w=empty(c);auto player=w.add(1,Role::Player,{100,200}),ward=w.add(0,Role::Melee,{200,200},3);
  Shot sh;sh.source=player;sh.pos={100,200};sh.direction={1,0};sh.speed=300;sh.left=500;sh.manual=true;sh.ordinal=1;w.shots.push_back(sh);
  gameReflexes(w,ward.slot);require(w.state[ward.slot].guardUntil>0,"warden did not guard manual shot");close(w.state[ward.slot].energy,136.25,"guard did not pay energy");
  w.damage(player,ward,100);close(w.units[ward.slot].hp,219,"guard arc/protection damage incorrect");
  w.units[player.slot].pos={300,200};w.damage(player,ward,100);close(w.units[ward.slot].hp,140,"rear guard incorrectly mitigated hit");
  auto dodge=empty(c);player=dodge.add(1,Role::Player,{100,200});auto runner=dodge.add(0,Role::Melee,{200,200},5);
  sh.source=player;sh.manual=false;sh.ordinal=42;dodge.shots.push_back(sh);const double before=dodge.units[runner.slot].pos.y;gameReflexes(dodge,runner.slot);
  require(std::abs(dodge.units[runner.slot].pos.y-before)==60,"chip dodge did not use kind distance");
  const auto pos=dodge.units[runner.slot].pos;dodge.state[runner.slot].dashReady=0;gameReflexes(dodge,runner.slot);
  close(dodge.units[runner.slot].pos.y,pos.y,"same shot rolled twice");
  auto burn=empty(c);player=burn.add(1,Role::Player,{100,200});runner=burn.add(0,Role::Melee,{200,200},5);
  burn.damage(player,runner,10);require(burn.dots.size()==1,"player hit did not seed burn");close(burn.dots[0].dps,.45,"burn seed did not use landed mitigation");
  for(int i=0;i<8;++i)burn.damage(player,runner,2);require(burn.dots.size()==5,"burn stack cap not enforced");
}
void abilityLifecycle() {
  auto c=sandboxConfig();c.abilities=true;auto w=empty(c);auto a=w.add(0,Role::Melee,{100,200}),b=w.add(1,Role::Melee,{220,200});
  require(triggerAbility(w,a.slot,Ability::Charge,b),"charge in legal interval rejected");
  require(!triggerAbility(w,a.slot,Ability::Shield),"ability lock did not exclude second action");
  require(busyAct(w,a.slot,.1),"charge did not own tick");close(w.units[a.slot].pos.x,123,"charge speed incorrect");
  w.units[a.slot].pos={200,200};w.liveGrid.moved(a.slot,w.units[a.slot].pos);
  require(!busyAct(w,a.slot,.1)&&w.abilities[w.state[a.slot].ability].chargeBonus,"charge did not arm impact bonus");
  w.time=2;require(triggerAbility(w,a.slot,Ability::Shield),"shield ready after shared lock rejected");
  const auto shooter=w.add(1,Role::Ranged,{300,200});w.damage(shooter,a,10);close(w.units[a.slot].hp,298,"shield did not mitigate non-melee damage");
  w.damage(b,a,10);close(w.units[a.slot].hp,288,"shield wrongly mitigated melee");
  auto reused=empty(c);const auto killer=reused.add(1,Role::Melee,{100,200});size_t high=0;
  for(int n=0;n<1000;++n){auto unit=reused.add(0,Role::Ranged,{200,200});high=std::max(high,reused.abilities.size());
    reused.damage(killer,unit,1000);reused.reclaim();}
  require(high<=2,"reclaimed ability pool grew with historical spawns");
}
void spawningAndForks() {
  auto c=gameConfig();c.scenario=Scenario::Skirmish;c.mirror=false;c.skirmishCount=4;c.skirmishMaxAlive=2;
  auto w=World::create(std::make_shared<const Config>(c));require(w.survivors(0)==2&&w.survivors(1)==1&&w.skirmishLeft==2,"skirmish admission incorrect");
  for(auto i:w.teams[0]){const auto& k=c.kinds[w.state[i].kind];close(w.state[i].timeRate,k.acc/6.62,"temporal reference mismatch");}
  BranchPool pool;auto fork=pool.fork(w);auto& f=fork.world();const auto p=w.teams[1][0];
  f.players[f.state[p].player].limbs[0].prep=1;f.spawnRandom();f.spawnSkirmish();
  require(w.players[w.state[p].player].limbs[0].prep==0&&w.skirmishLeft==2&&w.survivors(0)==2,"fork mutated parent player/spawn state");
  const auto victim=w.reference(w.teams[0][0]),player=w.reference(p);w.damage(player,victim,10000);coreStep(w);
  require(w.survivors(0)==2&&w.skirmishLeft==1,"skirmish did not refill dead monster");
  auto h=sandboxConfig();h.scenario=Scenario::Hunters;h.mirror=false;h.army={1,0,0};h.hunterMelee=1;h.hunterArchers=0;h.respawn=.1;h.dt=.1;
  auto hunters=World::create(std::make_shared<const Config>(h));auto a=hunters.reference(hunters.teams[0][0]),b=hunters.reference(hunters.teams[1][0]);
  hunters.damage(a,b,10000);require(!hunters.done()&&hunters.spawnQueue.size()==1,"hunters stopped on empty enemy side");coreStep(hunters);
  require(hunters.survivors(1)==1&&hunters.spawnQueue.empty(),"hunter respawn queue not drained");
}
}
int main(){casts();projectiles();defenses();abilityLifecycle();spawningAndForks();std::cout<<"native combat contracts passed\n";}
