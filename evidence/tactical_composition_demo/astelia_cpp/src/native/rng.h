#pragma once
#include <cmath>
#include <cstdint>
namespace astelia {
inline uint32_t toUint32(double n) {
  if (!std::isfinite(n) || n==0) return 0;
  const double m=std::fmod(std::trunc(n),4294967296.0);
  return uint32_t(m<0?m+4294967296.0:m);
}
struct Rng {
  uint32_t state=1;
  explicit Rng(uint32_t seed=1):state(seed?seed:1){}
  double operator()() {
    state^=state<<13; state^=state>>17; state^=state<<5;
    return double(state)/4294967296.0;
  }
};
} // namespace astelia
