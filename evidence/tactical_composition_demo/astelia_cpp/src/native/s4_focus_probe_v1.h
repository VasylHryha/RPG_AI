#pragma once
#include "s4_v6_controller.h"
#include <stdexcept>
namespace astelia::control {
// Scripted action overlay only; base v6 state evolves with its original target memory.
class FocusProbeV1 final : public S4V6Controller {
 int arm_;
public:
 static constexpr double marginPx=12;
 FocusProbeV1(double seed,uint8_t side,const ControllerParams& p,int arm):S4V6Controller(seed,side,p),arm_(arm){
  if(arm<4||arm>6)throw std::invalid_argument("unknown focus arm");
 }
 void prepare(const Observation&) override;
 std::unique_ptr<Controller> clone()const override{return std::make_unique<FocusProbeV1>(*this);}
};
}
