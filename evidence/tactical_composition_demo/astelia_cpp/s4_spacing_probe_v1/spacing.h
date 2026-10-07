#pragma once
#include "s4_v6_controller.h"
#include <stdexcept>
namespace astelia::control {
struct SpacingGun {
 UnitId id=0,focus=0;double x=0,y=0,bx=0,by=0,gx=0,gy=0,cx=0,cy=0,sx=0,sy=0,multiplier=0,radial=0,minRange=0,range=0;
 unsigned neighbours=0,coincident=0;
};
class SpacingProbeV1 final:public S4V6Controller {
 int arm_;std::vector<SpacingGun> audit_;
public:
 static constexpr double marginPx=12;
 SpacingProbeV1(double seed,uint8_t side,const ControllerParams& p,int arm):S4V6Controller(seed,side,p),arm_(arm){if(arm!=10&&arm!=11)throw std::invalid_argument("unknown spacing arm");}
 void prepare(const Observation&)override;
 const auto& audit()const{return audit_;}
 double spacing()const{return arm_==10?100:60;}
 std::unique_ptr<Controller> clone()const override{return std::make_unique<SpacingProbeV1>(*this);}
};
}
