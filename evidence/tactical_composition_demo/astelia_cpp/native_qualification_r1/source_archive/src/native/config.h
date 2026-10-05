#pragma once
#include "types.h"
#include "search_types.h"

namespace astelia {
struct Config {
  double seed=7, dt=1.0/30, duration=90, width=1200, height=700;
  double shotSpeed=350;
  std::array<uint32_t,3> army{10,30,10};
  std::array<RoleStats,6> roles;
  std::vector<Kind> kinds;
  std::vector<ArmyEntry> customArmy;
  std::vector<CarriedUnit> carried;
  std::array<uint32_t,3> enemyArmy{};
  std::array<CombatSkills,2> skills;
  std::array<Brain,2> brains{Brain::Alone,Brain::Alone};
  std::array<Formation,2> formations;
  std::array<AbilityThresholds,2> abilityThresholds;
  std::array<Lookahead,2> lookahead;
  std::array<std::vector<Plan>,2> disabledPlans;
  std::array<Plan,2> fewPlan{Plan::Surround,Plan::Surround};
  Tactics forcePlan;
  uint8_t forceTeam=0;
  bool hasForcePlan=false, reactiveDodge=true;
  std::array<std::array<bool,6>,2> abilityOff{};
  std::vector<uint32_t> skirmishKinds;
  uint32_t hunterMelee=10, hunterArchers=4, skirmishCount=18, skirmishMaxAlive=8, attackerCap=0;
  double respawn=3;
  Rules rules=Rules::Sandbox;
  Scenario scenario=Scenario::Mirror;
  PlayerStyle playerStyle=PlayerStyle::Kite;
  std::string mode="alone";
  bool mirror=true, swapSides=false, aimedShots=true, windUp=false;
  bool abilities=false, temporal=true, perception=false, hasEnemyArmy=false, hasCarried=false, hasCustomArmy=false;
  bool bcRecord=false;
};
} // namespace astelia
