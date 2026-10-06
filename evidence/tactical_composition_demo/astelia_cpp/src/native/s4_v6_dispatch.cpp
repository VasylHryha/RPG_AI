// Historical factory is compiled under a distinct symbol, without editing it.
#include "s4_v6_controller.h"
#include <stdexcept>
namespace astelia::control {
std::unique_ptr<Controller> makeHistoricalController(const ControllerProfile&,double,uint8_t);
std::unique_ptr<Controller> makeController(const ControllerProfile& profile,double seed,uint8_t side){
  if(profile.skeleton!="v6")return makeHistoricalController(profile,seed,side);
  if(side>1)throw std::invalid_argument("invalid controller side");
  if(profile.name=="resonator")return std::make_unique<S4V6Controller>(seed,side,profile.params);
  auto historical=profile;historical.skeleton="v5";return makeHistoricalController(historical,seed,side);
}
}
