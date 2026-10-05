#pragma once
#include "search.h"
namespace astelia {
// Native controller API: worlds own mutable state; no process-global network.
struct Summary {
  std::string mode;
  double melee,ranged,artillery,total,wasted,aliveSeconds,enemyDamage,t;
  uint32_t monsterDeaths,hunterKills,survivors,enemySurvivors;
};
struct Opponent { Brain brain; Formation formation; };
struct Profile {Brain brain;Formation formation;CombatSkills skills;Lookahead lookahead;AbilityThresholds abilities;std::vector<Plan> disabledPlans;Plan fewPlan;ControllerProfile controller;};
inline Profile buildProfile(const Config& c,uint8_t team){if(team>1)throw std::invalid_argument("invalid profile team");return {c.brains[team],c.formations[team],c.skills[team],c.lookahead[team],c.abilityThresholds[team],c.disabledPlans[team],c.fewPlan[team],c.controllers[team]};}
const std::vector<std::string>& opponentPool();
Opponent enemyOf(const std::string& name,const Formation* overrideFormation=nullptr);
std::vector<std::string> drawOpponents(double seed,uint32_t rounds,bool withoutReplacement=false);
void setNet(Config& config,std::shared_ptr<const Network> network);
inline World create(Config config){return World::create(std::make_shared<const Config>(std::move(config)));}
inline void step(World& w){coreStep(w);}
inline bool done(const World& w){return w.done();}
inline bool ready(const World& w,UnitRef unit,Ability name,bool byHand=true){return w.resolve(unit)&&abilityReady(w,unit.slot,name,byHand);}
inline bool triggerAbility(World& w,UnitRef unit,Ability name,UnitRef target={},Vec2 point={}){return w.resolve(unit)&&triggerAbility(w,unit.slot,name,target,point,true);}
inline std::vector<uint32_t> liveTeam(const World& w,uint8_t team){std::vector<uint32_t> out;for(auto i:w.teams.at(team))if(w.units[i].alive)out.push_back(i);return out;}
inline std::vector<uint32_t> monsters(const World& w){return liveTeam(w,0);}
inline std::vector<uint32_t> hunters(const World& w){return liveTeam(w,1);}
inline BranchPool::Lease fork(World& w){return w.branches().fork(w);}
Summary summary(const World& w);
Summary run(World& w);
} // namespace astelia
