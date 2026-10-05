#pragma once
// Controller-facing API: deliberately independent of world.h and types.h.
#include "rng.h"
#include <map>
#include <memory>
#include <string>
#include <vector>

namespace astelia::control {
using UnitId = uint32_t; // 0 is none; ids are monotonic, never slot numbers.
enum class ObservedRole : uint8_t { Melee, Ranged, Artillery };
struct ObservedUnit {
  UnitId id=0;
  uint8_t team=0;
  ObservedRole role=ObservedRole::Melee;
  double x=0,y=0,vx=0,vy=0,hp=0,maxhp=0,radius=0,speed=0,range=0,dmg=0,cd=0,cdMax=0;
  UnitId target=0;
  double damageDealt=0,damageTaken=0;
};
struct Observation {
  double t=0,dt=0,width=0,height=0;
  std::vector<ObservedUnit> units;
};
struct UnitDecision {
  double x=0,y=0,multiplier=1,stop=0;
  UnitId target=0;
};
using ControllerParams = std::map<std::string,double>;
struct ControllerProfile { std::string name; ControllerParams params; };
class Controller {
protected:
  Rng random_;
  uint8_t side_;
public:
  Controller(double seed,uint8_t side):random_(toUint32(seed*2654435761.0)^uint32_t(side+1)*2246822519u),side_(side){}
  virtual ~Controller()=default;
  virtual void prepare(const Observation&) {}
  virtual UnitDecision decide(const Observation&,UnitId self)=0;
  // Branches copy per-fight state and RNG, never share it with their parent.
  virtual std::unique_ptr<Controller> clone() const=0;
};
std::unique_ptr<Controller> makeController(const ControllerProfile&,double seed,uint8_t side);
const std::vector<std::string>& controllerNames();
} // namespace astelia::control
namespace astelia {
using control::ObservedRole;
using control::ObservedUnit;
using control::UnitDecision;
using control::ControllerParams;
using control::ControllerProfile;
using control::Controller;
using control::makeController;
using control::controllerNames;
} // namespace astelia
