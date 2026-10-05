#pragma once
#include "formation_types.h"
#include <memory>
namespace astelia {
struct Network {
  uint32_t inputs=0,hidden=0,outputs=0;
  std::vector<double> w1,b1,w2,b2;
  void validate() const;
};
std::shared_ptr<const Network> frozenNetwork();
enum class EnemyModel : uint8_t { Oracle, Continue, Rush, Rules };
struct Lookahead {
  double every=1,horizon=3,dt=.1,k=1.5,inertia=30,contact=450,terminal=0,stall=0,everyStable=0,tweakMargin=0,blend=1;
  double urgencyFrom=0,urgencyMin=0;
  uint32_t netPrune=0,budget=8,robustTop=2;
  bool enabled=false,mind=false,urgency=false,deaths=false,hasObjective=false;
  std::vector<EnemyModel> models{EnemyModel::Continue};
  std::vector<Plan> plans{Plan::Hold,Plan::Siege,Plan::Counter,Plan::Intercept,Plan::Push,Plan::Hunt,Plan::Flank,Plan::Advance,Plan::Skirmish,Plan::Spread,Plan::Widehold,Plan::Meleehunt,Plan::Bait},extra;
  std::shared_ptr<const Network> network;
};
} // namespace astelia
