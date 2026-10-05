#include "native/formation.h"
#include <iostream>

using namespace astelia;
namespace {
void require(bool b,const char* text){if(!b)throw std::runtime_error(text);}
void close(double a,double b,const char* text){require(std::abs(a-b)<1e-8,text);}
World empty(Config c){c.army={0,0,0};return World::create(std::make_shared<const Config>(std::move(c)));}
void shapes(){
  for(auto shape:{Shape::Line,Shape::Wedge,Shape::Box,Shape::Column,Shape::Screen,Shape::Crescent,Shape::Ring}){
    auto c=sandboxConfig();c.army={3,5,2};c.brains[0]=Brain::Formation;c.formations[0].shape=shape;
    auto w=World::create(std::make_shared<const Config>(c));formationPlan(w,0);const auto& p=w.packs[0];
    for(size_t r=0;r<3;++r)require(p.shape.role[r].size()==c.army[r],"shape did not publish one slot per member");
    for(auto i:w.teams[0]){require(w.state[i].hasSlot,"formation member missing slot");require(std::isfinite(w.state[i].slot.x)&&std::isfinite(w.state[i].slot.y),"nonfinite formation slot");}
    const auto version=p.shapeVersion;formationPlan(w,0);require(p.shapeVersion==version,"unchanged formation rebuilt shape version");
  }
  const auto wide=presetFormation("wide line");close(wide.frontSpacing,38,"wide-line authored table mismatch");close(wide.screenGap,21,"wide-line gap mismatch");
  auto base=presetFormation("line");Tactics mix;mix.role={Plan::Siege,Plan::Hunt,Plan::Focus,Plan::Siege};
  auto composed=composeFormation(base,Brain::Rules,mix);require(composed.anchorMode==AnchorMode::Siege&&composed.meleeDoctrine==MeleeDoctrine::Zone&&composed.shooterFocus==ShooterFocus::Squads&&composed.artilleryDoctrine==ArtilleryDoctrine::Soft,"role tactic composition overwrote wrong role");
  mix.role={Plan::Hold,Plan::Meleehunt,Plan::Skirmish,Plan::Engage};composed=composeFormation(base,Brain::Rules,mix);require(composed.release==7,"mixed-role releases were not joined");
}
void plansAndForks(){
  auto c=gameConfig();c.scenario=Scenario::Skirmish;c.mirror=false;c.brains[0]=Brain::Rules;
  auto w=World::create(std::make_shared<const Config>(c));commander(w,0);require(w.packs[0].plan==Plan::Surround,"rules did not select finishing surround");formationPlan(w,0);
  for(auto i:w.teams[0])require(w.tactical[i].hasSurroundGoal&&w.tactical[i].assigned==w.reference(w.teams[1][0]),"surround missed member or focus");
  auto raid=sandboxConfig();raid.army={12,2,2};raid.brains[0]=Brain::Rules;raid.hasEnemyArmy=true;raid.enemyArmy={0,3,2};raid.hasForcePlan=true;raid.forcePlan.role.fill(Plan::Raidart);
  auto flank=World::create(std::make_shared<const Config>(raid));coreStep(flank);require(flank.packs[0].plan==Plan::Raidart&&flank.packs[0].wings.size()==12,"forced raid did not assign flank wings");
  BranchPool pool;auto lease=pool.fork(flank);lease.world().packs[0].wings.clear();lease.world().packs[0].anchor.x+=100;lease.world().tactical[0].hasFlankGoal=false;
  require(flank.packs[0].wings.size()==12&&flank.tactical[0].hasFlankGoal,"branch overwrote formation authority");
  auto storm=sandboxConfig();storm.brains[0]=Brain::Storm;auto attack=World::create(std::make_shared<const Config>(storm));
  for(size_t j=25;j<attack.teams[1].size();++j)attack.units[attack.teams[1][j]].alive=false;attack.rebuildTeams();commander(attack,0);
  require(attack.packs[0].plan==Plan::Rush,"storm numerical superiority did not choose rush");
}
void targeting(){
  auto c=sandboxConfig();c.brains[0]=Brain::Formation;c.skills[0].fireControl=true;c.skills[1].dodgeShots=true;c.skills[1].shotReact=.12;
  auto w=empty(c);const auto src=w.add(0,Role::Ranged,{100,200}),target=w.add(1,Role::Ranged,{250,200});
  formationPlan(w,0);require(canDodge(w,target,src),"shot chance incorrectly treated dodger as stationary");
  fireShot(w,src.slot,target);close(w.packs[0].pending[target.slot],14*.3,"pending fire did not use hit probability");
  const auto parentPending=w.packs[0].pending;BranchPool pool;auto branch=pool.fork(w);branch.world().packs[0].pending[target.slot]=999;
  require(w.packs[0].pending==parentPending,"branch shared pending fire");
  auto smart=c;smart.skills[0].smartShells=true;auto dodger=empty(smart);const auto unit=dodger.add(0,Role::Melee,{200,200}),gun=dodger.add(1,Role::Artillery,{500,200});
  Shell shell;shell.source=gun;shell.pos={200,200};shell.at=2;shell.splash=45;dodger.shells.push_back(shell);Vec2 goal;
  require(dodgeGoal(dodger,unit.slot,goal)&&distance(goal,shell.pos)>shell.splash+dodger.units[unit.slot].radius,"smart dodge selected covered spot");
  const auto current=dodger.units[unit.slot].pos;dodger.units[unit.slot].pos=goal;require(!dodgeGoal(dodger,unit.slot,goal),"smart dodge moved although already safe");dodger.units[unit.slot].pos=current;
}
void lifecycleAndOrders(){
  auto c=gameConfig();c.scenario=Scenario::Skirmish;c.mirror=false;c.skirmishCount=2;c.skirmishMaxAlive=1;
  auto w=World::create(std::make_shared<const Config>(c));require(w.skirmishActive&&w.skirmishLeft==1,"skirmish setup lost reserve");
  const auto monster=w.reference(w.teams[0][0]),player=w.reference(w.teams[1][0]);w.damage(player,monster,1e9);require(!w.done(),"skirmish ended before reserve refill");
  coreStep(w);require(w.survivors(0)==1&&w.skirmishLeft==0,"reserve monster was not spawned");w.damage(player,w.reference(w.teams[0][0]),1e9);require(w.done(),"exhausted skirmish did not finish");
  c.hasCarried=true;c.carried={{Role::Melee,0,100}};auto carry=World::create(std::make_shared<const Config>(c));require(!carry.skirmishActive&&carry.timeReference==0&&!carry.done(),"carried skirmish incorrectly started player/time scaling");
  auto config=sandboxConfig();config.brains[0]=Brain::Formation;auto ordered=empty(config);const auto unit=ordered.add(0,Role::Ranged,{100,200}),enemy=ordered.add(1,Role::Melee,{200,200});formationPlan(ordered,0);
  UnitOrder retreat;retreat.kind=OrderKind::Retreat;retreat.point={40,200};retreat.until=10;issueOrder(ordered,unit,retreat);decideUnit(ordered,unit.slot);
  require(ordered.state[unit.slot].decision.move&&ordered.state[unit.slot].decision.release==Release::None,"retreat order attacked or lost walk");
  UnitOrder hold;hold.kind=OrderKind::Hold;hold.until=10;issueOrder(ordered,unit,hold);decideUnit(ordered,unit.slot);require(!ordered.state[unit.slot].decision.move&&ordered.units[unit.slot].target==enemy,"hold order did not stay and select reachable enemy");
  UnitOrder attack;attack.kind=OrderKind::Attack;attack.until=10;attack.target=enemy;issueOrder(ordered,unit,attack);ordered.damage(unit,enemy,1e9);decideUnit(ordered,unit.slot);
  require(ordered.tactical[unit.slot].order.kind==OrderKind::None&&ordered.orderEvents.back().reason==2,"dead attack order did not unwind to own AI");
  ordered.tactical[unit.slot].order=retreat;ordered.units[unit.slot].pos=retreat.point;decideUnit(ordered,unit.slot);require(ordered.orderEvents.back().reason==1,"arrival order did not finish");
  ordered.tactical[unit.slot].order=hold;ordered.time=11;decideUnit(ordered,unit.slot);require(ordered.orderEvents.back().reason==0,"expired order did not finish");
  ordered.packs[0].director.goals.plan.until=20;ordered.packs[0].director.goals.plan.tactics.role.fill(Plan::Widehold);ordered.packs[0].commands.plan.until=12;ordered.packs[0].commands.plan.tactics.role.fill(Plan::Push);
  require(planGoal(ordered,0)->tactics.role[0]==Plan::Push,"external goals did not override director");ordered.time=13;require(planGoal(ordered,0)->tactics.role[0]==Plan::Widehold,"expired external goal did not fall back to director");
  auto leased=BranchPool{};auto clone=leased.fork(ordered);clone.world().packs[0].director.goals.plan.until=0;clone.world().orderEvents.clear();require(planGoal(ordered,0)&&!ordered.orderEvents.empty(),"branch shared commands or order event history");
  ordered.units[enemy.slot].alive=false;const auto before=ordered.shots.size();fireShot(ordered,unit.slot,enemy);require(ordered.shots.size()==before+1,"ordinary release silently skipped a dead resolved target");
}
void directors(){
  auto c=sandboxConfig();c.width=2200;c.brains[0]=Brain::Rules;c.skills[0].combosEnabled=true;c.skills[0].combos={ComboKind::Tchain};auto w=empty(c);
  for(int i=0;i<6;++i)w.add(0,Role::Melee,{1200+double(i),350});for(int i=0;i<10;++i)w.add(0,Role::Ranged,{1250,250+i*20.0});
  for(int i=0;i<6;++i){const auto r=w.add(1,Role::Melee,{500+i*10.0,350});w.units[r.slot].velocity={40,0};}
  for(int i=0;i<8;++i){const auto r=w.add(1,Role::Ranged,{450+i*10.0,350});w.units[r.slot].velocity={40,0};}
  w.packs[0].anchor={1200,350};directorStep(w,0);auto& d=w.packs[0].director;
  require(d.active&&d.starts==1&&d.roles.size()==16&&placeGoal(w,0),"tchain did not select typed roles and lure goal");
  require(d.observation.columnRatio>2.2&&d.observation.chaseShare==1,"column/chase observation incorrect");
  w.time=2;w.units[w.teams[1][0]].pos={1000,350};directorStep(w,0);require(d.phase==1&&planGoal(w,0)->tactics.role[0]==Plan::Widehold,"tchain did not switch to cross");
  w.time=3.5;w.units[w.teams[1][0]].pos={1150,350};directorStep(w,0);require(d.phase==2&&releaseGoal(w,0)->ids.size()==5&&engageGoal(w,0)->ids.size()==6,"envelop did not release wings or rank engaged melee");
  for(size_t i=0;i<6;++i)w.units[w.teams[1][i]].alive=false;w.rebuildTeams();w.time=6;directorStep(w,0);
  require(!d.active&&d.successes==1&&!releaseGoal(w,0)&&d.cool[0]==14,"success did not clear goals or schedule cooldown");
  auto fix=c;fix.skills[0].combos={ComboKind::Fixlob};auto f=empty(fix);for(int i=0;i<6;++i)f.add(0,Role::Melee,{480,320+i*10.0});
  for(int i=0;i<3;++i)f.add(0,Role::Artillery,{450,320+i*20.0});for(int i=0;i<6;++i)f.add(1,Role::Melee,{500,320+i*10.0});for(int i=0;i<6;++i)f.add(1,Role::Melee,{650,350.0+i});
  f.packs[0].anchor={400,350};directorStep(f,0);require(f.packs[0].director.active&&f.packs[0].director.combo==ComboKind::Fixlob,"fixlob did not detect contact plus separated clump");
  f.time=1.5;directorStep(f,0);require(f.packs[0].director.phase==1,"fixlob did not switch to lob");f.time=7;directorStep(f,0);require(!f.packs[0].director.active&&f.packs[0].director.aborts==1,"timed-out director did not abort");
  BranchPool pool;auto branch=pool.fork(w);branch.world().time=30;directorStep(branch.world(),0);require(branch.world().packs[0].director.starts==1,"branch recursively ran the director");
}

}
int main(){shapes();plansAndForks();targeting();lifecycleAndOrders();directors();std::cout<<"native formation contracts passed\n";return 0;}
