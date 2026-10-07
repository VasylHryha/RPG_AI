// Reuse the unchanged implementation; observe the returned goal once.
#define dodgeGoal observerV1BaseDodgeGoal
#include "dodge.cpp"
#undef dodgeGoal
#include "observer_v1.h"
namespace astelia {
bool dodgeGoal(const World& w,uint32_t i,Vec2& goal){
 const bool result=observerV1BaseDodgeGoal(w,i,goal);
 observer_v1::dodge(w,i,result,result?goal:Vec2{});return result;
}
}
