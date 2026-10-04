#pragma once
#include "rng.h"
#include "config.h"
#include "spatial.h"
#include <memory>

namespace astelia {
Config sandboxConfig();
Config gameConfig();
const char* roleName(Role role);
struct WorkCounters {
  uint64_t outerSteps=0, branchSteps=0, forks=0, unitActions=0, projectileSteps=0;
  uint64_t searchCalls=0, inferenceCalls=0, candidateModels=0,artilleryRollouts=0;
};
// Typed authority. Configuration is immutable; all mutable state belongs to
// the world and is copied when a branch is leased.
class BranchPool;
class World {
  std::vector<uint32_t> free_;
  std::vector<uint8_t> retained_;
  mutable std::array<std::vector<uint32_t>,2> foes_;
  mutable std::array<uint64_t,2> foesVersion_{UINT64_MAX,UINT64_MAX};
  mutable std::array<double,2> foesTime_{-1,-1};
  void retain(UnitRef ref);
  std::unique_ptr<BranchPool> ownedBranches_;
  BranchPool* branches_=nullptr;
public:
  std::shared_ptr<const Config> config;
  std::vector<UnitHot> units;
  std::vector<UnitState> state;
  std::vector<TacticalState> tactical;
  std::array<Pack,2> packs;
  std::vector<uint32_t> active, order;
  std::array<std::vector<uint32_t>,2> teams;
  std::vector<Shot> shots;
  std::vector<Shell> shells;
  std::vector<Field> fields;
  std::vector<Dot> dots;
  std::vector<AbilityState> abilities;
  std::vector<PlayerState> players;
  std::vector<uint32_t> freeAbilities, freePlayers;
  std::vector<Spawn> spawnQueue;
  std::vector<MeleeHit> meleeHits;
  std::vector<Hit> hitLog;
  std::vector<OrderEvent> orderEvents;
  std::vector<Vec2> pushes;
  SpatialGrid liveGrid, shotGrid, separationGrid;
  Rng random;
  Rng spawnRandom{1};
  Stats stats;
  WorkCounters counters;
  std::shared_ptr<WorkCounters> work=std::make_shared<WorkCounters>();
  double dt=0,duration=0;
  std::array<Brain,2> brains;
  Tactics forced;uint8_t forcedTeam=0,thinkTeams=0;bool hasForced=false;
  double time=0;
  UnitId nextId=1;
  uint64_t nextShot=1;
  uint64_t membershipVersion=0;
  uint32_t skirmishLeft=0;
  double timeReference=0, lastHit=-99;
  bool branch=false, burnTick=false,skirmishActive=false;
  mutable std::array<double,2> ratesTime{-1,-1};
  mutable std::array<uint64_t,2> ratesVersion{UINT64_MAX,UINT64_MAX};
  mutable std::array<std::array<double,4>,2> rates{};

  explicit World(std::shared_ptr<const Config> c);
  ~World();
  World(World&&) noexcept;
  World& operator=(World&&) noexcept;
  World(const World&)=delete;
  World& operator=(const World&)=delete;
  BranchPool& branches();
  UnitHot* resolve(UnitRef r);
  const UnitHot* resolve(UnitRef r) const;
  UnitRef reference(uint32_t slot) const { return {slot,units.at(slot).generation}; }
  UnitRef add(uint8_t team,Role role,Vec2 pos,uint32_t kind=invalidSlot);
  UnitRef spawnHunter(Role role);
  UnitRef spawnSkirmish();
  void rebuildTeams();
  const std::vector<uint32_t>& foes(uint8_t team) const;
  void reclaim();
  void copyFrom(const World& parent);
  void move(uint32_t slot,Vec2 goal,double dt,double stop=0);
  double damage(UnitRef source,UnitRef target,double amount);
  bool done() const;
  uint32_t survivors(uint8_t team) const;
  static World create(std::shared_ptr<const Config> c);
};
void coreStep(World& world);
UnitRef nearest(const World& w,uint32_t slot,bool outsideMinimum=false,bool meleeOnly=false,double maximum=INFINITY,double minimumHp=0);
bool laneClear(const World& w,uint32_t slot,UnitRef target);
Vec2 leadVelocity(const World& w,UnitRef target,uint8_t team);
Vec2 interceptPoint(const World& w,Vec2 source,UnitRef target,double speed,uint8_t team);
double windup(const World& w,uint32_t slot);
bool prepared(const World& w,uint32_t slot);
void released(World& w,uint32_t slot);
void fireShot(World& w,uint32_t slot,UnitRef target,double damage=0);
void fireShellAt(World& w,uint32_t slot,Vec2 point);
void gamePrep(World& w,uint32_t slot,double dt);
void gameReflexes(World& w,uint32_t slot);
bool abilityReady(const World& w,uint32_t slot,Ability name,bool byHand=false);
bool triggerAbility(World& w,uint32_t slot,Ability name,UnitRef target={},Vec2 point={},bool byHand=false);
bool busyAct(World& w,uint32_t slot,double dt);
bool defaultAbilities(World& w,uint32_t slot);
void playerBrain(World& w,uint32_t slot,double dt);
void decideUnit(World& w,uint32_t slot);

// Stable allocations across nested leases; a child cannot overwrite its parent.
class BranchPool {
  std::vector<std::unique_ptr<World>> worlds_;
  std::vector<bool> leased_;
public:
  class Lease {
    BranchPool* pool_; size_t index_;
  public:
    Lease(BranchPool* p,size_t i):pool_(p),index_(i){}
    Lease(const Lease&)=delete;
    Lease& operator=(const Lease&)=delete;
    Lease(Lease&& other) noexcept:pool_(other.pool_),index_(other.index_) {other.pool_=nullptr;}
    ~Lease() { if (pool_) pool_->leased_[index_]=false; }
    World& world() { return *pool_->worlds_[index_]; }
  };
  Lease fork(const World& parent);
};
} // namespace astelia
