#pragma once
#include "types.h"
#include <algorithm>
#include <cmath>
#include <stdexcept>

namespace astelia {
inline double squared(Vec2 v) { return v.x*v.x + v.y*v.y; }
inline Vec2 operator+(Vec2 a, Vec2 b) { return {a.x+b.x,a.y+b.y}; }
inline Vec2 operator-(Vec2 a, Vec2 b) { return {a.x-b.x,a.y-b.y}; }
inline Vec2 operator*(Vec2 a, double n) { return {a.x*n,a.y*n}; }
inline double length(Vec2 a) {
  const double q=squared(a);
  if (std::isfinite(q) && q>=std::numeric_limits<double>::min()) return std::sqrt(q);
  return std::hypot(a.x,a.y);
}
inline double distance(Vec2 a, Vec2 b) { return length(a-b); }
inline double gap(const UnitHot& a, const UnitHot& b) { return distance(a.pos,b.pos)-a.radius-b.radius; }
inline double clamp(double v,double lo,double hi) { return std::max(lo,std::min(hi,v)); }
inline double dot(Vec2 a,Vec2 b) { return a.x*b.x+a.y*b.y; }
inline void validateBody(const UnitHot& u) {
  if (!std::isfinite(u.pos.x) || !std::isfinite(u.pos.y) ||
      !std::isfinite(u.radius) || u.radius<0) throw std::invalid_argument("invalid body geometry");
}
// The narrow phase is independent of the grid and can serve the scan oracle.
inline bool blockerParameter(Vec2 a,Vec2 direction,double maximum,const UnitHot& u,double& t) {
  const Vec2 p=u.pos-a; t=dot(p,direction);
  return t>0 && t<=maximum && std::abs(p.x*direction.y-p.y*direction.x)<u.radius+1.5;
}
inline bool segmentParameter(Vec2 a,Vec2 direction,double segmentLength,const UnitHot& u,double& t) {
  const Vec2 p=u.pos-a; t=clamp(dot(p,direction),0,segmentLength);
  return length(p-direction*t)<=u.radius;
}
} // namespace astelia
