#pragma once
#include "host.h"
#include "teacher.h"
namespace s1_script {
struct Provenance {astelia::UnitId focus=0;astelia::Vec2 center;};
extern std::map<astelia::UnitId,Provenance> plannerSources;
extern Provenance selectedSource;
struct Command {astelia::UnitId focus=0;astelia::Vec2 shape,absolute;double expiry=0;bool refreshed=false;uint64_t plan=0;};
extern std::map<astelia::UnitId,Command> commands;
extern bool wrapper;
void reset(bool);
}
