#pragma once
#include "../s4_escort_probe_v1/escort.h"
namespace astelia::control {
unsigned splashValue(const Observation&,uint8_t,const ObservedUnit&);
std::vector<EscortPoint> meleeEscortPoints(const Observation&,uint8_t);
struct GunFocus { SpacingGun geometry; UnitId target=0,anchor=0; unsigned targetValue=0,focusValue=0,anchorValue=0; bool reachable=false; UnitDecision p12,command; };
class EscortProbeV3 final:public Controller {
 EscortProbeV1 base_;int arm_;std::map<UnitId,UnitDecision> actions_;std::vector<GunFocus> guns_;
public:
 EscortProbeV3(double seed,uint8_t side,const ControllerParams& p,int arm):Controller(seed,side),base_(seed,side,p,12),arm_(arm){if(arm!=16&&arm!=17)throw std::invalid_argument("unknown escort v3 arm");}
 void prepare(const Observation&)override;
 UnitDecision decide(const Observation&,UnitId)override;
 std::unique_ptr<Controller> clone()const override{return std::make_unique<EscortProbeV3>(*this);}
 EscortProbeV1& baseline(){return base_;}
 int arm()const{return arm_;}
 const auto& gunAudit()const{return guns_;}
};
Controller* p12Base(Controller*);
Controller* probeBaseV3(Controller*);
}
