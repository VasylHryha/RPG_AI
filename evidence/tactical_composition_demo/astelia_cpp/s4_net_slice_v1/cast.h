#pragma once
#include "world.h"
#include "js_value.h"

namespace net_slice {
using namespace astelia;
struct Intent {UnitId target=0;Vec2 goal,aim;bool hasAim=false,start=false,release=false;double multiplier=0,stop=0;unsigned moveIndex=0,aimIndex=0,targetIndex=0;uint64_t volley=0;};
struct CastInput {uint64_t tick=0;bool alive=true,body=false,target=false,targetReach=false,aimReach=false;double cooldown=0,energy=0,cost=0,prep=0,windup=1;};
struct CastOutput {std::string state,reason;bool start=false,release=false,cancel=false;};
class Cast {
public:
 bool pending=false,aimLocked=false;UnitId lockedTarget=0;Vec2 lockedAim;uint64_t readySince=0,started=0,originDecision=0,originVolley=0;Intent last;
 CastOutput project(const CastInput&,const Intent&);
 void startedAck(uint64_t,const Intent&,uint64_t decision=0);
 void consumedAck();
};
Intent intent(js::V);
js::V json(const Intent&);
}
