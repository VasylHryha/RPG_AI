#define makeController makeV6Controller
#include "s4_v6_dispatch.cpp"
#undef makeController
#include "s4_focus_probe_v1.h"
namespace astelia::control {
std::unique_ptr<Controller> makeController(const ControllerProfile& p,double seed,uint8_t side){
 if(p.skeleton=="focus_probe_v1"){
  if(p.name=="P0")return std::make_unique<S4V6Controller>(seed,side,p.params);
  if(p.name=="P4"||p.name=="P5"||p.name=="P6")return std::make_unique<FocusProbeV1>(seed,side,p.params,p.name[1]-'0');
  throw std::invalid_argument("unknown focus arm");
 }return makeV6Controller(p,seed,side);
}
}
