#pragma once
#include "s4_v6_controller.h"
namespace astelia::control {
// Scripted diagnostic overlay. No engine state or shell observations.
class VolleyProbeV1 final:public S4V6Controller {
 int arm_;UnitId chosen_=0;double wait_=-1,releaseUntil_=-1;
 std::map<UnitId,UnitId> assignments_;
public:
 VolleyProbeV1(double seed,uint8_t side,const ControllerParams& p,int arm):S4V6Controller(seed,side,p),arm_(arm){}
 void prepare(const Observation&) override;
 std::unique_ptr<Controller> clone()const override{return std::make_unique<VolleyProbeV1>(*this);}
};
}
