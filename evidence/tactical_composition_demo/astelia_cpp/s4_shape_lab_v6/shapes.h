#pragma once
#include "world.h"
#include "js_value.h"
#include "artillery.h"
namespace react_v1 {struct Snapshot;class Controller;}
namespace shapes_v6 {
using namespace astelia;
constexpr double margin=1, retreatMax=100, participationHorizon=2, edgeMargin=24;
struct Threat {Vec2 point,direction;double at=0,release=0,radius=0,damage=0,speed=0,left=0;UnitId target=0;bool shot=false,cast=false;};
struct Rotation {bool active=false;Vec2 point;double base=0,candidate=0,nextShot=0;std::string participation="none";};
struct State {std::string arm="base";js::Args audit;std::map<UnitId,bool> rotating;js::Args shotEvents;};
struct GunView {UnitId id=0,target=0;double windup=0,lob=0,splash=0;bool eligible=false;};
struct PlannerInput {control::Observation units;std::vector<GunView> guns;std::vector<PredictedShell> shells;};
World project(const PlannerInput&);
void copiedPlanner(World&,uint8_t);
std::vector<PlannedShot> plan(const PlannerInput&);
bool reach(const control::ObservedUnit&,const control::ObservedUnit&);
bool legalAim(const control::Observation&,UnitId,const UnitDecision&,Vec2);
Vec2 trajectory(const control::ObservedUnit&,const UnitDecision&,double);
UnitDecision floor(const react_v1::Snapshot&,UnitId,UnitDecision,bool reaction);
double damage(const react_v1::Snapshot&,UnitId,const UnitDecision&);
Rotation rotate(const react_v1::Snapshot&,UnitId,const UnitDecision&);
void threats(const World&,uint8_t,react_v1::Snapshot&);
void augment(react_v1::Controller&);
Config configuration(js::V);World create(std::shared_ptr<const Config>,js::V);
void geometry(World&);js::V audit(World&);js::V shots(World&);void shot(World&,uint32_t,const Shot&);
}
