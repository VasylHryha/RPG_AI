#pragma once
#include "host.h"
#include "teacher.h"
#include "public_mechanics.h"
namespace s1_script {
struct Provenance {astelia::UnitId focus=0;astelia::Vec2 center;};
extern std::map<astelia::UnitId,Provenance> plannerSources;
extern Provenance selectedSource;
struct Command {astelia::UnitId focus=0;astelia::Vec2 shape,absolute;double expiry=0;bool refreshed=false;uint64_t plan=0;};
extern std::map<astelia::UnitId,Command> commands;
extern bool wrapper;
void reset(bool);
net_slice::Intent autonomous(js::V,astelia::UnitId locked=0);
bool reacting(js::V);
net_public::Snapshot publicView(js::V);
}
