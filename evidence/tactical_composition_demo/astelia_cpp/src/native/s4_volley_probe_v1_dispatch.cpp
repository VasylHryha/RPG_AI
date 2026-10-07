#define makeController makeV6Controller
#include "s4_v6_dispatch.cpp"
#undef makeController
#include "s4_volley_probe_v1.h"
namespace astelia::control {
std::unique_ptr<Controller> makeController(const ControllerProfile&p,double seed,uint8_t side){
 if(p.skeleton=="volley_probe_v1"){
  if(p.name=="P0")return std::make_unique<S4V6Controller>(seed,side,p.params);
  if(p.name=="P1"||p.name=="P2"||p.name=="P3")return std::make_unique<VolleyProbeV1>(seed,side,p.params,p.name[1]-'0');
  throw std::invalid_argument("unknown volley arm");
 }return makeV6Controller(p,seed,side);
}
}
