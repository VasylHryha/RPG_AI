#pragma once
#include "schema.h"
#include "cast.h"
#include "artillery.h"
namespace slice_teacher {
using namespace astelia;
struct GunView {UnitId id=0,target=0;double windup=0,lob=0,splash=0;bool eligible=false;};
struct PlannerInput {control::Observation units;std::vector<GunView> guns;std::vector<PredictedShell> shells;};
World project(const PlannerInput&);
void copiedPlanner(World&,uint8_t);
struct Labels {std::map<UnitId,net_slice::Intent> actions;unsigned aimSupportSnaps=0;js::Args diagnostics;};
Labels query(const std::vector<js::V>&);
}
