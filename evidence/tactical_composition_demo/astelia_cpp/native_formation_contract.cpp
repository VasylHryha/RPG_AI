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
}
int main(){shapes();plansAndForks();targeting();std::cout<<"native formation contracts passed\n";}
