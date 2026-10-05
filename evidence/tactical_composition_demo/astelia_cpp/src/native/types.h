#pragma once
#include <array>
#include <cstdint>
#include <limits>
#include <string>
#include <vector>

namespace astelia {
constexpr uint32_t invalidSlot = std::numeric_limits<uint32_t>::max();
using UnitId = uint32_t;
enum class Role : uint8_t { Melee, Ranged, Artillery, Hunter, Archer, Player };
enum class Rules : uint8_t { Sandbox, Game };
enum class Scenario : uint8_t { Mirror, Hunters, Skirmish };
enum class Lead : uint8_t { None, Raw, Smooth };
enum class Dodge : uint8_t { None, Kiter, Storm, Skittish };
enum class Ability : uint8_t { Charge, Shield, Aimed, Disengage, Barrage, Slow };
enum class AbilityPolicy : uint8_t { Off, Auto, Coordinated };
enum class PlayerStyle : uint8_t { Kite, Orbit, Press };
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
struct DecisionTrace { UnitId id=0,target=0; uint8_t team=0; Decision decision; bool inReach=false; };
struct UnitState {
  Vec2 previous, slot, longVelocity;
  double cooldownMax=0, prep=0, windup=0, baseSpeed=0;
  double energy=0, energyMax=0, energyRegen=0, cost=0, protection=0;
  double minRange=0, shotSpeed=0, lobSpeed=0, splash=0, launch=1, timeRate=1;
  double longSpeed=0, stepTime=0, dealt=0, meleeAt=-1;
  double damageDealt=0, damageTaken=0; // actual HP, all teams; resets on slot reuse
  UnitRef meleeAttacker;
  int8_t strafe=1;
  uint32_t kind=invalidSlot, ability=invalidSlot, player=invalidSlot;
  double castTime=-1;
  double standoff=0, dashReady=0, guardUntil=0, blockReady=0, guardDirection=0, lastShotHit=-9;
  Dodge dodge=Dodge::None;
  bool hasSlot=false, inReach=false, castOk=true, block=false;
  std::vector<uint64_t> rolledShots;
  Decision decision;
};
struct Shot {
  Vec2 pos, direction;
  UnitRef source, target;
  double speed=0, damage=0, pending=0, left=0, born=0;
  uint64_t ordinal=0;
  uint32_t pierce=0;
  bool aimed=true, dodgeable=true, done=false, manual=false;
  std::vector<UnitRef> hitSet;
};
enum class AttackFamily : uint8_t { Singles,Focus,Net,Wall,Herd,Split,Trap,Sweep,Battery,Dashnet,Left,Own,Count };
struct PlannedShot {Vec2 point;UnitRef gun;double at=0,prediction=0;bool finisher=false,hasPrediction=false;AttackFamily family=AttackFamily::Own;uint16_t variant=0;};
struct ArtilleryRollout {uint32_t top=5;double horizon=2,dt=0,every=0;bool enabled=false,ltd2=false;std::vector<AttackFamily> shape;};
struct Shell {
  AttackFamily family=AttackFamily::Own;uint16_t variant=0;bool finisher=false;
  Vec2 pos;
  UnitRef source;
  double at=0, born=0, damage=0, splash=0, prediction=0;
  bool slow=false, lob=false, barrage=false, hasPrediction=false, done=false;
};
struct Field { Vec2 pos; double radius=0, from=0, until=0; uint8_t team=0; };
struct Dot { UnitRef source, target; double dps=0, until=0, accumulated=0; };
struct MeleeHit { UnitRef source, target; double multiplier=1; };
struct Hit { double time=0, amount=0; uint8_t from=0, to=0; };
struct AttackStats {uint64_t used=0,shells=0,kills=0;double damage=0,own=0;};
struct ShellStats {uint64_t shells=0,hits=0,planShells=0;double damage=0,planPred=0,planDamage=0;};
struct AbilityStats {uint64_t uses=0;double damage=0,blocked=0;};
struct Stats {
  std::array<std::array<AbilityStats,6>,2> abilities;
  std::array<double,6> bySource{},takenBy{}; // melee, charge, shell, barrage, shot, aimed
  std::array<std::array<AttackStats,size_t(AttackFamily::Count)*2>,2> attacks;std::array<ShellStats,2> shellOut;
  double melee=0, ranged=0, artillery=0, wasted=0, aliveSeconds=0, enemyDamage=0;
  uint32_t monsterDeaths=0, hunterKills=0;
};
struct RoleStats {
  double hp=0, speed=0, radius=0, range=0, damage=0, cooldown=0;
  double minRange=0, shotSpeed=0, flight=0, splash=0;
};
struct Kind {
  std::string name;
  Role role=Role::Melee;
  double hp=0, speed=0, radius=0, damage=0, reach=0, windup=0, cooldown=0;
  double energy=0, regen=0, cost=0, protection=0, shot=0, lob=0, splash=0, minRange=0, acc=1, launch=0;
  Dodge dodge=Dodge::None;
  bool block=false;
  double blockCost=40, blockCooldown=2, blockDuration=1, blockMultiplier=.5, blockHalfArc=1.5707963267948966;
};
struct ArmyEntry { Role role; uint32_t kind=invalidSlot, count=0; };
struct CarriedUnit { Role role; uint32_t kind=invalidSlot; double hp=0; };
struct AbilityState {
  std::array<double,6> ready{};
  double lock=0, chargeEnd=0, shieldUntil=0, aimUntil=0, disengageEnd=0;
  UnitRef chargeTarget, aimTarget;
  Vec2 disengageGoal;
  bool chargeBonus=false, manual=false;
};
struct Limb { double multiplier=1, prep=0; uint8_t sequence=0; UnitRef target; };
struct PlayerState {
  std::array<Limb,4> limbs{Limb{1},Limb{1},Limb{1.1025},Limb{1.1025}};
  Vec2 dashDirection;
  double dashReady=0, dashUntil=0, manualPrep=0;
  UnitRef manualTarget;
  uint8_t manual=0; // 0 idle, 1 ember, 2 pulse
};
struct Spawn { double at=0; Role role=Role::Hunter; };
enum class ComboKind : uint8_t { Tchain, Fixlob };
enum class OrderKind : uint8_t { None, Move, Attack, Hold, Retreat };
struct UnitOrder {OrderKind kind=OrderKind::None;Vec2 point;UnitRef target;double until=0,radius=14;};
struct OrderEvent {double time;UnitId id;OrderKind kind;uint8_t reason;};
struct CombatSkills {
  Lead lead=Lead::None;
  AbilityPolicy abilities=AbilityPolicy::Off;
  double kite=0, shotReact=.3,holdWave=0,holdSync=0;
  ArtilleryRollout rollout;
  bool pursuitCut=false, dodgeShots=false, dodgeSoft=false, dodgeShells=false;
  bool lobLead=false, adaptiveLobLead=false;
  double leaderBracket=12, fireDepth=0, jink=0, saveWounded=0, artyRobust=.5, artyHerd=0, artyEvery=.25;
  uint32_t waves=0;
  bool leaderFire=false,lockedDodge=false,reactAim=true,fireControl=false,killSpeed=false;
  bool planShells=false,smartShells=false,artyPlan=false,artyBattery=false,artyOwn=false,artyExact=false;
  bool meleeFocus=false,weaponsFree=false,castDodge=false,artyFollow=false,followShooters=false;
  bool combosEnabled=false;std::vector<ComboKind> combos;
};

} // namespace astelia
