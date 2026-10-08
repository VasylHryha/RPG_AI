#pragma once
#include "cast.h"
namespace net_slice {
struct Collector {
 std::string fight="fixture";js::Args events;
 void record(uint64_t tick,UnitId unit,const std::string& stage,js::V value,uint64_t volley=0,uint64_t decision=0,uint64_t cast=0);
 js::V drain();
};
}
