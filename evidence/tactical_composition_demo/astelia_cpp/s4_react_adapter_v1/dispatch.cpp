#include "../s4_shape_lab_v1/build/lab_v7_dispatch.cpp"
#include "../s4_shape_lab_v1/lab_native.h"
#include "react.h"
namespace astelia::control {
std::unique_ptr<Controller> makeController(const ControllerProfile& p,double seed,uint8_t side){
 if(p.name=="v7+react"||p.name=="forcedP16+react"){
  if(p.skeleton!="v7")throw std::invalid_argument("react requires v7 skeleton");
  return std::make_unique<react_v1::Controller>(seed,side,p.params,p.name=="v7+react"?V7Selector::Gate:V7Selector::P16);
 }
 if(p.name.rfind("dummy_",0)==0)return std::make_unique<shape_lab::Dummy>(p,seed,side);
 return makeDeliveredV7Controller(p,seed,side);
}
}
