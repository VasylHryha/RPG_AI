#pragma once
#include "s4_v7_controller.h"
#include "world.h"
#include "js_value.h"

namespace react_v1 {
using namespace astelia;
// Value-only controller API. No world handles, config, RNG or enemy private state.
struct ShellView { Vec2 position, landing; double at=0,radius=0; bool slow=false; };
struct ShotView { Vec2 position,direction; double born=0,speed=0,left=0; };
struct FieldView { Vec2 position; double radius=0,from=0,until=0; };
struct CastView { UnitId gun=0,target=0; Vec2 landing; double releaseAt=0,landingAt=0,radius=0; };
struct OwnView { UnitId id=0; double guardUntil=0,prep=0,windup=0,timeRate=1,energy=0,cost=0; bool busy=false; };
struct Snapshot {
 control::Observation units;
 std::vector<ShellView> shells;
 std::vector<ShotView> shots;
 std::vector<FieldView> fields;
 std::vector<CastView> casts;
 std::vector<OwnView> own;
 bool game=true;
};
Snapshot observe(const World&,uint8_t);
enum class FireIntent { Automatic, Hold, Release };
struct Command {
 UnitDecision movement;
 bool hasAim=false;
 Vec2 aim;
 FireIntent fire=FireIntent::Automatic;
 uint64_t volley=0; // 0 = no membership; metadata, never an implicit scheduler.
};
struct Reaction { bool active=false; Vec2 goal; std::string kind="none"; };
Reaction react(const Snapshot&,UnitId,double shotReact=.12);
// Constrain a rotation/withdrawal endpoint to our own reachable engagement band.
UnitDecision participate(const control::Observation&,UnitId,UnitDecision);
struct Record {
 UnitId id=0; std::string role,winner,reason,primitive,readinessReason;
 Release engineRelease=Release::None;
 Command candidate,reactCandidate,executed;
 bool active=false,ready=false,wasReacting=false;
 Reaction teacher;
};
class Controller final:public control::S4V7Controller {
 std::shared_ptr<const Snapshot> snapshot_;
 std::map<UnitId,Record> records_;
 std::map<UnitId,bool> reacting_;
 bool shadow_=false;
 Rng shadowRandom_{1};
public:
 Controller(double seed,uint8_t side,const ControllerParams& p,control::V7Selector s):S4V7Controller(seed,side,p,s),shadowRandom_(toUint32(seed*2654435761.0)^uint32_t(side+1)*2246822519u){}
 void shadow(bool on){shadow_=on;}
 bool shadow()const{return shadow_;}
 Rng& shadowRandom(){return shadowRandom_;}
 uint32_t studentRandomState()const{return random_.state;}
 void snapshot(Snapshot s){snapshot_=std::make_shared<const Snapshot>(std::move(s));records_.clear();}
 const Snapshot& snapshot()const;
 void prepare(const control::Observation&)override;
 UnitDecision decide(const control::Observation&,UnitId)override;
 std::unique_ptr<control::Controller> clone()const override{return std::make_unique<Controller>(*this);}
 const auto& records()const{return records_;}
 const Command* command(UnitId)const;
 void teacher(UnitId,Reaction);
 void submit(UnitId,Command); // future aim/volley primitive, validated before authority.
 void readiness(UnitId);
 void executed(UnitId,const World&,uint32_t);
};
Config configuration(js::V);
World create(std::shared_ptr<const Config>,js::V);
void prepare(World&);
void shadows(World&);
void decide(World&,uint32_t);
void constrainPrep(World&);
Vec2 aimPoint(const World&,uint32_t,Vec2);
bool aimReach(const World&,uint32_t);
void telemetry(const World&);
} // namespace react_v1
