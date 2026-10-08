#pragma once
#include "controller.h"
#include "js_value.h"
#include <array>
namespace react_v1 {class Controller;struct Command;}
namespace stagea {
using Vec=std::vector<double>;using Matrix=std::vector<Vec>;using astelia::control::UnitId;
struct Weights {std::string kind;std::map<std::string,Vec> p;explicit Weights(js::V);Vec linear(const std::string&,const Vec&)const;};
struct State {std::shared_ptr<const Weights> weights;std::map<UnitId,Vec> memory;Matrix cache;std::vector<UnitId> cachedIds;double nextFrame=0;uint64_t ticks=0;bool collect=false,parity=false;js::V input;std::map<UnitId,Vec> outputs;};
void configure(react_v1::Controller&,js::V);
void begin(react_v1::Controller&);
react_v1::Command command(react_v1::Controller&,UnitId);
void record(react_v1::Controller&);
js::V replay(js::V);
}
