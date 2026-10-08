#pragma once
#include "world.h"
namespace net_public {
using namespace astelia;
struct ShellView {Vec2 position,landing;double at=0,radius=0;bool slow=false;};
struct ShotView {Vec2 position,direction;double born=0,speed=0,left=0;};
struct FieldView {Vec2 position;double radius=0,from=0,until=0;};
struct CastView {UnitId gun=0,target=0;Vec2 landing;double releaseAt=0,landingAt=0,radius=0;};
struct OwnView {UnitId id=0;double guardUntil=0,prep=0,windup=0,timeRate=1,energy=0,cost=0;bool busy=false;};
struct Snapshot {control::Observation units;std::vector<ShellView> shells;std::vector<ShotView> shots;std::vector<FieldView> fields;std::vector<CastView> casts;std::vector<OwnView> own;bool game=true;};
struct Reaction {bool active=false;Vec2 goal;std::string kind="none";};
Reaction react(const Snapshot&,UnitId,double latency=.12);
UnitDecision participate(const control::Observation&,UnitId,UnitDecision);
}
