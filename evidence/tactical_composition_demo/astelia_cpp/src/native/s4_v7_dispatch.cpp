#define makeController makeV6Controller
#include "s4_v6_dispatch.cpp"
#undef makeController
#include "s4_focus_probe_v1.h"
#include "spacing.h"
namespace astelia::control {
std::unique_ptr<Controller> makeSpacingController(const ControllerProfile& p,double seed,uint8_t side){
 if(p.skeleton=="spacing_probe_v1"){
  if(p.name=="P5")return std::make_unique<FocusProbeV1>(seed,side,p.params,5);
  if(p.name=="P10"||p.name=="P11")return std::make_unique<SpacingProbeV1>(seed,side,p.params,p.name=="P10"?10:11);
  throw std::invalid_argument("unknown spacing arm");
 }
 if(p.skeleton=="focus_probe_v1"){
  if(p.name=="P0")return std::make_unique<S4V6Controller>(seed,side,p.params);
  if(p.name=="P4"||p.name=="P5"||p.name=="P6")return std::make_unique<FocusProbeV1>(seed,side,p.params,p.name[1]-'0');
  throw std::invalid_argument("unknown focus arm");
 }return makeV6Controller(p,seed,side);
}
}
#include "../../s4_escort_probe_v3/escort.h"
namespace astelia::control {
std::unique_ptr<Controller> makeDeliveredEscortController(const ControllerProfile& p,double seed,uint8_t side){
 if(p.skeleton=="escort_probe_v3"){
  if(p.name=="P12")return std::make_unique<EscortProbeV1>(seed,side,p.params,12);
  if(p.name=="P16"||p.name=="P17")return std::make_unique<EscortProbeV3>(seed,side,p.params,p.name=="P16"?16:17);
  throw std::invalid_argument("unknown escort arm");
 }
 return makeSpacingController(p,seed,side);
}
}

#include "s4_v7_controller.h"
namespace astelia::control {
std::unique_ptr<Controller> makeController(const ControllerProfile& p,double seed,uint8_t side){
 if(p.skeleton!="v7")return makeDeliveredEscortController(p,seed,side);
 if(p.name=="historicalP16")return std::make_unique<EscortProbeV3>(seed,side,p.params,16);
 auto params=p.params;
 if(p.name=="omega0")params["omega_ranged"]=0;
 if(p.name=="v7"||p.name=="omega0")return std::make_unique<S4V7Controller>(seed,side,params);
 if(p.name=="forcedP16")return std::make_unique<S4V7Controller>(seed,side,params,V7Selector::P16);
 if(p.name=="forcedv6")return std::make_unique<S4V7Controller>(seed,side,params,V7Selector::V6);
 throw std::invalid_argument("unknown v7 arm");
}
}
