#pragma once
#include "react.h"
namespace army_a0 {
using namespace astelia;
std::map<UnitId,UnitDecision> oracle(const control::Observation&,uint8_t);
UnitDecision base(const control::Observation&,uint8_t,UnitId);
bool applyAim(World&,react_v1::Controller&,UnitId,Vec2);
void geometry(World&);
}
