#include "controller.h"
#include "s3_controller.h"
#include <functional>
#include <algorithm>
#include <stdexcept>

namespace astelia::control {
// Implemented in the engine bridge. This is the ONLY privileged controller.
std::unique_ptr<Controller> makeTestPassthrough(double,uint8_t);
namespace {
const ObservedUnit& findSelf(const Observation& o,UnitId id) {
  for(const auto& u:o.units)if(u.id==id)return u;
  throw std::invalid_argument("controller self absent from observation");
}
class Nearest final : public Controller {
public:
  using Controller::Controller;
  UnitDecision decide(const Observation& o,UnitId id) override {
    const auto& self=findSelf(o,id);const ObservedUnit* target=nullptr;double best=INFINITY;
    for(const auto& u:o.units)if(u.team!=self.team){const double dx=u.x-self.x,dy=u.y-self.y,d=dx*dx+dy*dy;
      if(d<best){best=d;target=&u;}}
    if(!target)return {self.x,self.y,1,0,0};
    // Range is a surface gap for melee/direct weapons, centre distance for art.
    const double stop=.9*self.range+(self.role==ObservedRole::Artillery?0:self.radius+target->radius);
    return {target->x,target->y,1,stop,target->id};
  }
  std::unique_ptr<Controller> clone() const override { return std::make_unique<Nearest>(*this); }
};
class Hold final : public Controller {
public:
  using Controller::Controller;
  UnitDecision decide(const Observation& o,UnitId id) override {const auto& self=findSelf(o,id);return {self.x,self.y,0,0,0};}
  std::unique_ptr<Controller> clone() const override { return std::make_unique<Hold>(*this); }
};
using Factory=std::function<std::unique_ptr<Controller>(double,uint8_t)>;
const std::map<std::string,Factory>& registry(){static const std::map<std::string,Factory> factories={
  {"nearest",[](double seed,uint8_t side){return std::make_unique<Nearest>(seed,side);}},
  {"hold",[](double seed,uint8_t side){return std::make_unique<Hold>(seed,side);}},
  {"passthrough",makeTestPassthrough}};return factories;}
}
const std::vector<std::string>& controllerNames(){static const std::vector<std::string> names=[](){std::vector<std::string> out;for(const auto& f:registry())out.push_back(f.first);for(auto name:{"resonator","morale","pushpull"})out.push_back(name);std::sort(out.begin(),out.end());return out;}();return names;}
std::unique_ptr<Controller> makeController(const ControllerProfile& p,double seed,uint8_t side){
  if(p.skeleton!="v0"&&p.skeleton!="v1"&&p.skeleton!="v2"&&p.skeleton!="v3"&&p.skeleton!="v4")throw std::invalid_argument("invalid skeleton");
  if(side>1)throw std::invalid_argument("invalid controller side");
  if(p.name=="resonator"||p.name=="morale"||p.name=="pushpull")return std::make_unique<S3Controller>(seed,side,p.name=="resonator"?Arm::Resonator:p.name=="morale"?Arm::Morale:Arm::PushPull,p.params,p.skeleton);
  const auto f=registry().find(p.name);if(f==registry().end())throw std::invalid_argument("unknown controller: "+p.name);
  if(!p.params.empty())throw std::invalid_argument("S2 controllers accept only empty params");
  return f->second(seed,side);
}
} // namespace astelia::control
