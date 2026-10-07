#pragma once
#include "../s4_escort_probe_v1/escort.h"
namespace astelia::control {
UnitId escortThreatTarget(const Observation&,uint8_t,const ObservedUnit&);
std::pair<double,double> escortShift(const Observation&,uint8_t,const ObservedUnit&);
std::vector<EscortPoint> escortPointsV2(const Observation&,uint8_t,int);
class EscortProbeV2 final:public Controller {
 EscortProbeV1 base_;int arm_;std::map<UnitId,UnitDecision> actions_;
public:
 EscortProbeV2(double seed,uint8_t side,const ControllerParams& p,int arm):Controller(seed,side),base_(seed,side,p,12),arm_(arm){if(arm!=14&&arm!=15)throw std::invalid_argument("unknown escort v2 arm");}
 void prepare(const Observation&)override;
 UnitDecision decide(const Observation&,UnitId)override;
 std::unique_ptr<Controller> clone()const override{return std::make_unique<EscortProbeV2>(*this);}
 EscortProbeV1& baseline(){return base_;}
 int arm()const{return arm_;}
};
Controller* probeBaseV2(Controller*);
Controller* p12Base(Controller*);
}
