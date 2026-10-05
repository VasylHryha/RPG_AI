#pragma once
#include "world.h"
namespace astelia {
bool externalSide(const World&,uint8_t team);
void prepareControllers(World&);
void controllerDecision(World&,uint32_t slot);
void applyControllerDecision(World&,uint32_t slot,UnitDecision);
} // namespace astelia
