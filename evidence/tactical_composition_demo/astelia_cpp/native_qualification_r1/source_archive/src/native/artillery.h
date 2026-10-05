#pragma once
#include "search.h"
namespace astelia {
struct PredictedShell {Vec2 point;double at=0,damage=0,splash=0;uint8_t team=0;};
struct PredictedUnit {Vec2 point;double hp=0;};
struct Prediction {std::vector<double> per,value;std::vector<PredictedUnit> snapshot;double own=0;bool hasSnapshot=false;};
struct Attack {AttackFamily family=AttackFamily::Singles;uint16_t variant=0;std::vector<PlannedShot> shots;std::vector<double> per;double score=0;};
bool busyUnit(const World& w,uint32_t slot);
bool gunReach(const World& w,uint32_t slot,Vec2 point);
double lobSpeed(const World& w,uint32_t slot);
double blastRadius(const World& w,uint32_t slot);
double threatWorth(const World& w,uint32_t slot);
PredictedShell shellOf(const World& w,uint8_t team,const PlannedShot& shot,double flight);
Prediction predictVolley(const World& w,uint8_t team,const std::vector<PredictedShell>& planned,double snapTime=-1,double step=.1);
double smartVolley(const World& w,uint8_t team,const std::vector<PredictedShell>& planned);
bool fireGate(World& w,uint32_t slot);
void launch(World& w,uint8_t team,const Attack& attack);
double artilleryOutcome(World& w,uint8_t team,const Attack& attack,const ArtilleryRollout& rollout);
void artilleryVolley(World& w,uint8_t team);
const char* attackName(AttackFamily family);
AttackFamily attackByName(const std::string& name);
} // namespace astelia
