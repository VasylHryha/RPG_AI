#pragma once
#include "world.h"
#include "formation_types.h"
namespace astelia {
Formation presetFormation(const std::string& preset);
Plan planByName(const std::string& name);
const char* planName(Plan plan);
Formation composeFormation(const Formation& base,Brain brain,const Tactics& combo);
void setPlan(World& w,uint8_t team,const Tactics& combo);
const GoalPlace* placeGoal(const World& w,uint8_t team);
const GoalPlan* planGoal(const World& w,uint8_t team);
const GoalIds* engageGoal(const World& w,uint8_t team);
const GoalIds* releaseGoal(const World& w,uint8_t team);
bool containsId(const GoalIds* goal,UnitId id);
Observation observe(const World& w,uint8_t team);
std::string briefing(const Observation& observation);
void directorStep(World& w,uint8_t team);
void issueOrder(World& w,UnitRef unit,const UnitOrder& order);
void formationPlan(World& w,uint8_t team);
void commander(World& w,uint8_t team);
bool inZone(const World& w,uint8_t team,uint32_t enemy);
bool threatens(const World& w,uint8_t team,uint32_t enemy);
bool pinned(const World& w,uint32_t slot);
UnitRef artilleryTarget(const World& w,uint32_t slot);
UnitRef shooterTarget(const World& w,uint32_t slot,bool released);
void leaderFire(World& w,uint8_t team);
void coordAbilities(World& w,uint8_t team);
double reachOf(const World& w,uint8_t team,Role role);
double paceOf(const World& w,uint8_t team);
bool canDodge(const World& w,UnitRef target,UnitRef shooter={});
double hitProbability(const World& w,uint8_t team,UnitRef target,UnitRef shooter={});
double hitLineProbability(const World& w,uint8_t team,UnitRef target,UnitRef shooter);
bool aimClear(const World& w,uint32_t slot,UnitRef target);
void addPending(World& w,UnitRef source,UnitRef target,double amount);
bool shellDodge(const World& w,uint8_t team);
bool dodgeGoal(const World& w,uint32_t slot,Vec2& goal);
} // namespace astelia
