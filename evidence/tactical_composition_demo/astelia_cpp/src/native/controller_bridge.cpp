#include "controller_bridge.h"
#include "geometry.h"
#include <stdexcept>
namespace astelia {
namespace {
// TEST ONLY. The world pointer is rebound at each call (including branch calls).
// Built-in decisions contain private flags; leave them verbatim in the engine.
class TestPassthrough final : public Controller {
public:
  World* world=nullptr;
  using Controller::Controller;
  UnitDecision decide(const control::Observation&,UnitId id) override {
    if(!world)throw std::logic_error("unbound test passthrough");
    for(auto i:world->active)if(world->units[i].id==id){decideUnit(*world,i);const auto& d=world->state[i].decision;
      const auto* t=world->resolve(world->units[i].target);return {d.goal.x,d.goal.y,d.multiplier,d.stop,t?t->id:0};}
    throw std::logic_error("missing test passthrough unit");
  }
  std::unique_ptr<Controller> clone() const override {auto copy=std::make_unique<TestPassthrough>(*this);copy->world=nullptr;return copy;}
};
UnitRef livingTarget(const World& w,UnitId id,uint8_t team){
  if(!id)return {};
  for(auto i:w.active){const auto& u=w.units[i];if(u.id==id&&u.alive&&u.team!=team){const auto r=w.reference(i);if(w.resolve(r))return r;}}
  return {};
}
}
namespace control {
std::unique_ptr<Controller> makeTestPassthrough(double seed,uint8_t side){return std::make_unique<TestPassthrough>(seed,side);}
}
bool externalSide(const World& w,uint8_t team){return w.controllers[team]&&w.config->controllers[team].name!="passthrough";}
void prepareControllers(World& w){
  for(uint8_t side=0;side<2;++side)if(w.controllers[side]){
    auto& o=w.observations[side];o.t=w.time;o.dt=w.dt;o.width=w.config->width;o.height=w.config->height;o.units.clear();
    for(auto i:w.active){const auto& u=w.units[i];if(!u.alive)continue;const auto& s=w.state[i];const auto* t=w.resolve(u.target);
      const auto role=melee(u.role)?ObservedRole::Melee:u.role==Role::Artillery?ObservedRole::Artillery:ObservedRole::Ranged;
      o.units.push_back({u.id,u.team,role,u.pos.x,u.pos.y,u.velocity.x,u.velocity.y,u.hp,u.maxhp,u.radius,u.speed,u.range,u.damage,u.cooldown,s.cooldownMax,t&&t->alive?t->id:0,s.damageDealt,s.damageTaken});}
    w.controllers[side]->prepare(o);
  }
}
void applyControllerDecision(World& w,uint32_t i,UnitDecision decision){
  auto& u=w.units[i];auto& s=w.state[i];s.decision={};s.inReach=false;
  // Invalid numeric decisions fail closed to hold/no target; no NaNs reach physics.
  if(!std::isfinite(decision.x)||!std::isfinite(decision.y)||!std::isfinite(decision.multiplier)||!std::isfinite(decision.stop))decision={u.pos.x,u.pos.y,0,0,0};
  decision.x=clamp(decision.x,0,w.config->width);decision.y=clamp(decision.y,0,w.config->height);
  decision.multiplier=clamp(decision.multiplier,0,1);decision.stop=std::max(0.0,decision.stop);
  u.target=livingTarget(w,decision.target,u.team);
  // Guard is a body reflex, as in decideUnit. It holds movement and release.
  if(s.guardUntil>w.time)return;
  auto& d=s.decision;d.move=true;d.goal={decision.x,decision.y};d.multiplier=decision.multiplier;d.stop=decision.stop;
  const auto* target=w.resolve(u.target);
  if(melee(u.role)){d.release=Release::Melee;s.inReach=target&&gap(u,*target)<=u.range;}
  else if(u.role==Role::Artillery){d.release=Release::Artillery;s.inReach=target&&distance(u.pos,target->pos)<=u.range&&distance(u.pos,target->pos)>=s.minRange;}
  else{d.release=Release::Direct;d.post=true;s.inReach=target&&gap(u,*target)<=u.range;}
}
void controllerDecision(World& w,uint32_t i){
  const auto side=w.units[i].team;
  if(auto* pass=dynamic_cast<TestPassthrough*>(w.controllers[side].get())){
    pass->world=&w;pass->decide(w.observations[side],w.units[i].id);pass->world=nullptr;return;
  }
  applyControllerDecision(w,i,w.controllers[side]->decide(w.observations[side],w.units[i].id));
}
} // namespace astelia
