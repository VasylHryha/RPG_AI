#pragma once
#include "react.h"
#include <random>
namespace stageb2 {
// Collection-only teacher commands. A separate seeded stream never touches the
// simulation RNG. Clean O labels remain in shadowLabels before perturbation.
inline std::pair<react_v1::Command,bool> teacherCommand(react_v1::Controller& c,astelia::control::UnitId id){
 const auto& s=c.stage;const auto& o=c.snapshot().units;
 for(auto v:s.shadowLabels.p->items)if(js::num(js::get(v,"id"))==id){
  auto e=js::get(v,"executed");react_v1::Command cmd;auto goal=js::get(e,"goal");
  cmd.movement.x=js::num(goal.p->items.at(0));cmd.movement.y=js::num(goal.p->items.at(1));
  cmd.movement.target=astelia::control::UnitId(js::num(js::get(e,"target")));
  cmd.movement.multiplier=js::num(js::get(e,"multiplier"));cmd.movement.stop=js::num(js::get(e,"stop"));
  auto fire=js::str(js::get(e,"fire"));cmd.fire=fire=="hold"?react_v1::FireIntent::Hold:fire=="release"?react_v1::FireIntent::Release:react_v1::FireIntent::Automatic;
  auto aim=js::get(e,"aim");if(aim.tag!=js::V::Null&&aim.tag!=js::V::Undefined){cmd.hasAim=true;cmd.aim={js::num(aim.p->items.at(0)),js::num(aim.p->items.at(1))};}
  std::seed_seq seeds{uint32_t(s.daggerSeed),uint32_t(id),uint32_t(s.ticks),uint32_t(s.ticks>>32)};std::mt19937 rng(seeds);
  double radius=0;for(auto& u:o.units)if(u.id==id)radius=u.radius;
  if(s.dartSigma>0){std::normal_distribution<double> noise(0,s.dartSigma);cmd.movement.x=std::clamp(cmd.movement.x+noise(rng),radius,o.width-radius);cmd.movement.y=std::clamp(cmd.movement.y+noise(rng),radius,o.height-radius);}
  if(s.dartTarget>0&&std::uniform_real_distribution<double>(0,1)(rng)<s.dartTarget){std::vector<astelia::control::UnitId> targets;for(auto& u:o.units)if(u.team!=0&&u.hp>0)targets.push_back(u.id);std::sort(targets.begin(),targets.end());if(!targets.empty())cmd.movement.target=targets[std::uniform_int_distribution<size_t>(0,targets.size()-1)(rng)];}
  return {cmd,js::truth(js::get(v,"active"))};
 }
 throw std::runtime_error("missing clean DAgger teacher label");
}
}
