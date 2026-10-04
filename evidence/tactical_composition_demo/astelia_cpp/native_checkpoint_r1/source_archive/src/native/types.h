#pragma once
#include <array>
#include <cstdint>
#include <limits>
#include <vector>

namespace astelia {
constexpr uint32_t invalidSlot = std::numeric_limits<uint32_t>::max();
using UnitId = uint32_t;
enum class Role : uint8_t { Melee, Ranged, Artillery, Hunter, Archer, Player };
enum class Rules : uint8_t { Sandbox, Game };
enum class Release : uint8_t { None, Melee, Direct, DodgeFire, Artillery, Player };
inline bool melee(Role r) { return r == Role::Melee || r == Role::Hunter; }
struct Vec2 { double x=0, y=0; };
struct UnitRef {
  uint32_t slot=invalidSlot, generation=0;
  explicit operator bool() const { return slot != invalidSlot; }
  friend bool operator==(UnitRef a, UnitRef b) { return a.slot==b.slot && a.generation==b.generation; }
  friend bool operator!=(UnitRef a, UnitRef b) { return !(a==b); }
};
// The layout checkpoint compares this complete candidate with column storage.
// All references are world-local handles; no pointers survive buffer growth.
struct UnitHot {
  Vec2 pos, velocity, smoothVelocity;
  double hp=0, maxhp=0, radius=0, speed=0, range=0, damage=0, cooldown=0;
  UnitRef target;
  UnitId id=0;
  uint32_t generation=1;
  uint8_t team=0;
  Role role=Role::Melee;
  bool alive=false, occupied=false;
};
struct Decision {
  Vec2 goal;
  double stop=0, multiplier=1;
  Release release=Release::None;
  bool move=false, keep=false, post=false, bound=false;
};
struct UnitState {
  Vec2 previous, slot, longVelocity;
  double cooldownMax=0, prep=0, windup=0, baseSpeed=0;
  double energy=0, energyMax=0, energyRegen=0, cost=0, protection=0;
  double minRange=0, shotSpeed=0, lobSpeed=0, splash=0, launch=1, timeRate=1;
  double longSpeed=0, stepTime=0, dealt=0, meleeAt=-1;
  UnitRef meleeAttacker;
  int8_t strafe=1;
  bool hasSlot=false;
  Decision decision;
};
struct Shot {
  Vec2 pos, direction;
  UnitRef source, target;
  double speed=0, damage=0, pending=0, left=0, born=0;
  uint32_t ordinal=0, pierce=0;
  bool aimed=true, dodgeable=true, done=false;
  std::vector<UnitRef> hitSet;
};
struct Shell {
  Vec2 pos;
  UnitRef source;
  double at=0, born=0, damage=0, splash=0, prediction=0;
  bool slow=false, lob=false, barrage=false, hasPrediction=false, done=false;
};
struct Field { Vec2 pos; double radius=0, from=0, until=0; uint8_t team=0; };
struct Dot { UnitRef source, target; double dps=0, until=0, accumulated=0; };
struct MeleeHit { UnitRef source, target; double multiplier=1; };
struct Hit { double time=0, amount=0; uint8_t from=0, to=0; };
struct Stats {
  double melee=0, ranged=0, artillery=0, wasted=0, aliveSeconds=0, enemyDamage=0;
  uint32_t monsterDeaths=0, hunterKills=0;
};
struct RoleStats {
  double hp=0, speed=0, radius=0, range=0, damage=0, cooldown=0;
  double minRange=0, shotSpeed=0, flight=0, splash=0;
};
struct Config {
  double seed=7, dt=1.0/30, duration=90, width=1200, height=700;
  double shotSpeed=350;
  std::array<uint32_t,3> army{10,30,10};
  std::array<RoleStats,6> roles;
  Rules rules=Rules::Sandbox;
  bool mirror=true, swapSides=false, aimedShots=true, windUp=false;
};
} // namespace astelia
