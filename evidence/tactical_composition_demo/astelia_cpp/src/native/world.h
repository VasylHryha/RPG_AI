#pragma once
#include "rng.h"
#include "spatial.h"
#include <memory>

namespace astelia {
Config sandboxConfig();
struct WorkCounters {
  uint64_t outerSteps=0, branchSteps=0, forks=0, unitActions=0, projectileSteps=0;
  uint64_t searchCalls=0, inferenceCalls=0, candidateModels=0;
};
// Stage B: a complete typed vertical slice, limited to the declared novice,
// sandbox mirror configuration. The host must reject unsupported features.
class World {
  std::vector<uint32_t> free_;
  std::vector<uint8_t> retained_;
  void retain(UnitRef ref);
public:
  std::shared_ptr<const Config> config;
  std::vector<UnitHot> units;
  std::vector<UnitState> state;
  std::vector<uint32_t> active, order;
  std::array<std::vector<uint32_t>,2> teams;
  std::vector<Shot> shots;
  std::vector<Shell> shells;
  std::vector<Field> fields;
  std::vector<Dot> dots;
  std::vector<MeleeHit> meleeHits;
  std::vector<Hit> hitLog;
  std::vector<Vec2> pushes;
  SpatialGrid liveGrid, shotGrid, separationGrid;
  Rng random;
  Stats stats;
  WorkCounters counters;
  double time=0;
  UnitId nextId=1;
  bool branch=false;

  explicit World(std::shared_ptr<const Config> c):config(std::move(c)),random(toUint32(config->seed)){}
  UnitHot* resolve(UnitRef r);
  const UnitHot* resolve(UnitRef r) const;
  UnitRef reference(uint32_t slot) const { return {slot,units.at(slot).generation}; }
  UnitRef add(uint8_t team,Role role,Vec2 pos);
  void rebuildTeams();
  void reclaim();
  void copyFrom(const World& parent);
  void move(uint32_t slot,Vec2 goal,double dt,double stop=0);
  double damage(UnitRef source,UnitRef target,double amount);
  bool done() const;
  uint32_t survivors(uint8_t team) const;
  static World create(std::shared_ptr<const Config> c);
};
void coreStep(World& world);

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
