#include "native/world.h"
#include <iostream>
using namespace astelia;
int main() {
  auto c=std::make_shared<Config>(sandboxConfig());c->army={1,1,0};c->seed=2026100409;
  c->dt=1e-310;c->duration=1e-309;
  auto tiny=World::create(c);coreStep(tiny);
  size_t invalid=0;
  for (auto i:tiny.active) if (!std::isfinite(tiny.units[i].velocity.x) ||
      !std::isfinite(tiny.units[i].smoothVelocity.x)) ++invalid;

  auto d=std::make_shared<Config>(sandboxConfig());d->army={0,0,0};World spawned(d);
  auto shooter=spawned.add(0,Role::Ranged,{20,100});
  auto target=spawned.add(1,Role::Melee,{200,100});spawned.rebuildTeams();
  spawned.liveGrid.build(spawned.units,spawned.active,400,400,40);
  auto blocker=spawned.add(0,Role::Melee,{100,100});
  auto found=lineBlocker(spawned.units,spawned.liveGrid,{20,100},{200,100},8,shooter,target);
  bool throws=false;
  try {spawned.move(blocker.slot,{120,100},.1);} catch (const std::out_of_range&) {throws=true;}

  auto e=std::make_shared<Config>(sandboxConfig());e->army={1,1,0};
  auto fresh=World::create(e);bool freshThrows=false;
  try {fresh.move(fresh.active[0],{600,400},.1);} catch (const std::out_of_range&) {freshThrows=true;}

  std::cout<<"{\"tiny_dt_invalid_velocity_units\":"<<invalid
    <<",\"spawned_blocker_found\":"<<(found==blocker?"true":"false")
    <<",\"move_after_spawn_throws\":"<<(throws?"true":"false")
    <<",\"move_before_first_step_throws\":"<<(freshThrows?"true":"false")<<"}\n";
}
