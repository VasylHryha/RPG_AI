#pragma once
#include "js_value.h"
#include <set>

#include "world.h"
namespace net_slice {
using astelia::UnitId;
constexpr unsigned width=1008,outputs=81;
struct Encoding {std::vector<double> x;std::vector<UnitId> enemies;unsigned friendsOverflow=0,enemiesOverflow=0,threatOverflow=0;};
void validate(js::V);
Encoding encode(js::V);
js::V decode(js::V,const std::vector<double>&);
js::V snapshot(const astelia::World&,uint8_t,astelia::UnitId,uint64_t,const std::string&,const std::map<astelia::UnitId,double>&,const std::set<astelia::UnitId>&);
}
