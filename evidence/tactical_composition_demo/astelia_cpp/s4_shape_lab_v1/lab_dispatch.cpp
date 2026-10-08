#include "build/lab_v7_dispatch.cpp"
#include "lab_native.h"
namespace astelia::control {
std::unique_ptr<Controller> makeController(const ControllerProfile& p,double seed,uint8_t side) {
 if(p.name.rfind("dummy_",0)==0)return std::make_unique<shape_lab::Dummy>(p,seed,side);
 return makeDeliveredV7Controller(p,seed,side);
}
}
