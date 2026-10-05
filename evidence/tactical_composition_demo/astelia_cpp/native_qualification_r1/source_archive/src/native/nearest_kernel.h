#pragma once
#include "spatial.h"
namespace astelia {
// This exact kernel serves production and the layout comparison. Stable ties
// follow the candidate index order; no layout-specific predicate or shortcut.
template<class Storage>
UnitRef nearestKernel(const Storage& units,const std::vector<uint32_t>& candidates,uint32_t slot,
                      double minRange,bool outsideMinimum,bool meleeOnly,double maximum,double minimumHp){
  const auto& u=units[slot];UnitRef best;double bd=INFINITY;
  for(auto i:candidates){const auto& e=units[i];if(!e.alive||(meleeOnly&&!melee(e.role))||e.hp<minimumHp)continue;
    const double d=distance(u.pos,e.pos);if(d>maximum||(outsideMinimum&&d<minRange))continue;
    if(d<bd){bd=d;best={i,e.generation};}}
  return best;
}
} // namespace astelia
