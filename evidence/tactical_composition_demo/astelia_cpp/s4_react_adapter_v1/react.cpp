#include "react.h"
#include "../s4_shape_lab_v1/lab_native.h"
#include "geometry.h"
#include "artillery.h"
#include "observer_v1.h"
#include "controller_bridge.h"
#include <iostream>

namespace react_v1 {
namespace {
const control::ObservedUnit& unit(const control::Observation& o,UnitId id){
 for(const auto& u:o.units)if(u.id==id)return u;
 throw std::invalid_argument("react self absent");
}
const OwnView& own(const Snapshot& o,UnitId id){for(const auto& u:o.own)if(u.id==id)return u;throw std::invalid_argument("react own state absent");}
bool reach(const control::ObservedUnit& u,const control::ObservedUnit& t){
 const double d=distance({u.x,u.y},{t.x,t.y});
 return u.role==ObservedRole::Artillery?d>=u.minRange&&d<=u.range:d-u.radius-t.radius<=u.range;
}
Controller* controller(World& w,uint8_t side){return dynamic_cast<Controller*>(w.controllers[side].get());}
const Controller* controller(const World& w,uint8_t side){return dynamic_cast<const Controller*>(w.controllers[side].get());}
bool boolean(js::V v,const char* key,bool fallback){if(v.tag==js::V::Undefined)return fallback;auto x=js::get(v,key);if(x.tag==js::V::Undefined)return fallback;if(x.tag!=js::V::Boolean)throw std::invalid_argument("react boolean required");return js::truth(x);}
js::V commandJSON(const Command& c){const auto& d=c.movement;return js::obj({{"target",double(d.target)},{"goal",js::arr({d.x,d.y})},{"multiplier",d.multiplier},{"stop",d.stop},{"failure",d.controllerFailure},{"aim",c.hasAim?js::arr({c.aim.x,c.aim.y}):js::V(nullptr)},{"fire",c.fire==FireIntent::Hold?"hold":c.fire==FireIntent::Release?"release":"automatic"},{"volley",double(c.volley)}});}
}
Snapshot observe(const World& w,uint8_t side){
 if(side>1)throw std::invalid_argument("invalid react side");
 Snapshot out;auto& o=out.units;o.t=w.time;o.dt=w.dt;o.width=w.config->width;o.height=w.config->height;out.game=w.config->rules==Rules::Game;
 for(auto i:w.active){const auto& u=w.units[i];if(!u.alive)continue;const auto& s=w.state[i];const auto* t=w.resolve(u.target);
  const auto role=melee(u.role)?ObservedRole::Melee:u.role==Role::Artillery?ObservedRole::Artillery:ObservedRole::Ranged;
  o.units.push_back({u.id,u.team,role,u.pos.x,u.pos.y,u.velocity.x,u.velocity.y,u.hp,u.maxhp,u.radius,u.speed,u.range,u.damage,u.cooldown,s.cooldownMax,t&&t->alive?t->id:0,s.damageDealt,s.damageTaken,s.minRange,s.dealtToEnemy,s.takenFromEnemy,s.friendlyDealt,s.friendlyTaken});
  if(u.team==side)out.own.push_back({u.id,s.guardUntil,s.prep,windup(w,i),s.timeRate,s.energy,s.cost,busyUnit(w,i)});
  else if(out.game&&u.role==Role::Artillery&&s.prep>0&&t&&t->alive&&t->team==side){
   const double release=w.time+std::max(0.0,windup(w,i)-s.prep)/s.timeRate;
   out.casts.push_back({u.id,t->id,t->pos,release,release+distance(t->pos,u.pos)/((s.lobSpeed>0?s.lobSpeed:300)*s.launch),s.splash>0?s.splash:w.config->roles[2].splash});
  }
 }
 // Same resolve/team predicates as dodge.cpp / decideUnit's dodgeShots block.
 for(const auto& sh:w.shells){const auto* src=w.resolve(sh.source);if(src&&src->team!=side&&sh.at>w.time)out.shells.push_back({sh.pos,sh.pos,sh.at,sh.splash,sh.slow});}
 for(const auto& sh:w.shots){const auto* src=w.resolve(sh.source);if(sh.aimed&&src&&src->team!=side)out.shots.push_back({sh.pos,sh.direction,sh.born,sh.speed,sh.left});}
 for(const auto& f:w.fields)if(f.team!=side)out.fields.push_back({f.pos,f.radius,f.from,f.until});
 return out;
}
Reaction react(const Snapshot& o,UnitId id,double latency){
 const auto& u=unit(o.units,id);const auto& s=own(o,id);const Vec2 pos{u.x,u.y};
 if(s.guardUntil>o.units.t)return {};
 bool engaged=false;for(const auto& t:o.units.units)if(t.id==u.target&&t.team!=u.team&&u.role==ObservedRole::Melee&&reach(u,t))engaged=true;
 // Copied decideUnit dodgeShots. dodgeSoft=false; engaged melee keeps attacking.
 if(!engaged){const ShotView* best=nullptr;double bt=INFINITY,side=0;
  for(const auto& sh:o.shots){if(o.units.t-sh.born<latency)continue;const auto delta=pos-sh.position;const double along=dot(delta,sh.direction),cross=delta.x*sh.direction.y-delta.y*sh.direction.x;
   if(along>0&&along<=std::min(sh.left,sh.speed*.4)&&std::abs(cross)<=u.radius+3&&along<bt){best=&sh;bt=along;side=cross;}}
  if(best){const double k=side>=0?1:-1;return {true,pos+Vec2{best->direction.y*30*k,-best->direction.x*30*k},"dodgeShots"};}
 }
 // External side is unformed: shell dodge is skipped for engaged melee, as in decideUnit.
 if(engaged)return {};
 for(const auto& f:o.fields)if(f.from<=o.units.t&&f.until>=o.units.t+.5){const auto delta=pos-f.position;const double d=length(delta);
  if(d<=f.radius+u.radius)return {true,d<.5?pos+Vec2{30,0}:pos+delta*(40/d),"slowField"};}
 struct Blast{Vec2 pos;double at,radius;};std::vector<Blast> blasts;
 for(const auto& sh:o.shells)if(!sh.slow)blasts.push_back({sh.landing,sh.at,sh.radius});
 for(const auto& c:o.casts)if(c.target!=id)blasts.push_back({c.landing,c.landingAt,c.radius});
 double first=INFINITY;for(const auto& b:blasts)if(distance(pos,b.pos)<=b.radius+u.radius+4)first=std::min(first,b.at);
 if(!std::isfinite(first))return {};
 const auto cover=[&](Vec2 p){uint32_t count=0;for(const auto& b:blasts)if(distance(p,b.pos)<=b.radius+u.radius+4)++count;return count;};
 uint32_t best=cover(pos);double bd=0;Reaction result;const double extent=std::max(8.0,u.speed*(first-o.units.t+.1));
 for(double f:{1.0,.6})for(int j=0;j<16;++j){const double a=j*3.14159265358979323846/8;const auto point=pos+Vec2{std::cos(a),std::sin(a)}*(extent*f);
  const Vec2 candidate{clamp(point.x,u.radius,o.units.width-u.radius),clamp(point.y,u.radius,o.units.height-u.radius)};const auto k=cover(candidate);const double d=distance(candidate,pos);
  if(k<best||(k==best&&result.active&&d<bd)){result={true,candidate,"smartShells+castDodge"};best=k;bd=d;}}
 return result;
}
UnitDecision participate(const control::Observation& o,UnitId id,UnitDecision d){
 const auto& u=unit(o,id);const control::ObservedUnit* nearest=nullptr;double bd=INFINITY;
 for(const auto& t:o.units)if(t.team!=u.team&&t.hp>0){const double x=std::hypot(u.x-t.x,u.y-t.y);if(x<bd){bd=x;nearest=&t;}}
 if(!nearest)return d;
 // Preserve any endpoint in an enemy's own-weapon engagement band.
 for(const auto& t:o.units)if(t.team!=u.team&&t.hp>0){auto q=u;q.x=d.x;q.y=d.y;if(reach(q,t))return d;}
 const auto& t=*nearest;double dx=d.x-t.x,dy=d.y-t.y,len=std::hypot(dx,dy);
 if(len==0){dx=u.x-t.x;dy=u.y-t.y;len=std::hypot(dx,dy);if(len==0){dx=1;len=1;}}
 const double hi=u.role==ObservedRole::Artillery?u.range:u.range+u.radius+t.radius;
 const double lo=u.role==ObservedRole::Artillery?u.minRange:0;
 const double radius=std::clamp(len,lo,hi);d.x=std::clamp(t.x+dx/len*radius,u.radius,o.width-u.radius);d.y=std::clamp(t.y+dy/len*radius,u.radius,o.height-u.radius);
 // Arena clipping can enter a gun's minimum range. If already participating,
 // hold rather than replace a legal position with an illegal clipped endpoint.
 auto q=u;q.x=d.x;q.y=d.y;bool valid=false;for(const auto& e:o.units)if(e.team!=u.team&&e.hp>0&&reach(q,e))valid=true;
 if(!valid)for(const auto& e:o.units)if(e.team!=u.team&&e.hp>0&&reach(u,e)){d.x=u.x;d.y=u.y;d.multiplier=0;d.stop=0;return d;}
 // If already outside range, ensure movement closes distance instead of running away.
 if(!reach(u,t)){d.multiplier=1;d.stop=0;}return d;
}
const Snapshot& Controller::snapshot()const{if(!snapshot_)throw std::logic_error("react snapshot not bound");return *snapshot_;}
void Controller::prepare(const control::Observation& o){
 if(snapshot().units.t!=o.t)throw std::logic_error("react stale snapshot");
 S4V7Controller::prepare(o);
 std::set<UnitId> live;for(const auto& u:o.units)if(u.team==side_&&u.hp>0)live.insert(u.id);
 for(auto it=reacting_.begin();it!=reacting_.end();)if(!live.count(it->first))it=reacting_.erase(it);else ++it;
 for(const auto& u:o.units)if(live.count(u.id)){
  Record r;r.id=u.id;r.role=u.role==ObservedRole::Melee?"melee":u.role==ObservedRole::Artillery?"artillery":"ranged";
  r.candidate.movement=S4V7Controller::decide(o,u.id);r.executed=r.candidate;r.wasReacting=reacting_[u.id];
  auto useful=participate(o,u.id,r.candidate.movement);r.executed.movement=useful;
  r.winner="move";r.reason=r.wasReacting?"return_to_current_useful_position":"v7_useful_position";
  if(useful.x!=r.candidate.movement.x||useful.y!=r.candidate.movement.y){r.winner="participation";r.reason="rotation_or_withdrawal_constrained_to_own_range";}
  const auto reaction=react(snapshot(),u.id);r.active=reaction.active;r.primitive=reaction.kind;
  r.reactCandidate=r.candidate;
  if(reaction.active){auto& d=r.reactCandidate.movement;d.x=reaction.goal.x;d.y=reaction.goal.y;d.multiplier=1;d.stop=0;r.reactCandidate.fire=FireIntent::Hold;
   if(!r.candidate.movement.controllerFailure){r.executed=r.reactCandidate;r.winner="react";r.reason="temporary_movement_precedence_attack_release_paused";}}
  const auto& s=own(snapshot(),u.id);
  if(s.guardUntil>o.t||s.busy||r.candidate.movement.controllerFailure){r.executed.fire=FireIntent::Hold;r.winner=s.guardUntil>o.t?"guard":s.busy?"body_ability":"failure";r.reason="body_or_failure_precedence";}
  reacting_[u.id]=reaction.active;records_[u.id]=r;readiness(u.id);
 }
}
UnitDecision Controller::decide(const control::Observation&,UnitId id){return records_.at(id).executed.movement;}
const Command* Controller::command(UnitId id)const{auto it=records_.find(id);return it==records_.end()?nullptr:&it->second.executed;}
void Controller::teacher(UnitId id,Reaction r){records_.at(id).teacher=std::move(r);}
void Controller::readiness(UnitId id){
 auto& r=records_.at(id);const auto& o=snapshot().units;const auto& u=unit(o,id);const auto& s=own(snapshot(),id);const auto& cmd=r.executed;
 r.ready=false;r.readinessReason="out_of_range_or_no_target";
 if(r.active||cmd.fire==FireIntent::Hold||s.guardUntil>o.t||s.busy||cmd.movement.controllerFailure){r.readinessReason="reaction_hold_or_body_block";return;}
 bool inReach=false;
 for(const auto& t:o.units)if(t.id==cmd.movement.target&&t.team!=u.team&&t.hp>0)inReach=reach(u,t);
 if(cmd.hasAim&&u.role==ObservedRole::Artillery){const double d=distance({u.x,u.y},cmd.aim);inReach=inReach&&d>=u.minRange&&d<=u.range;}
 if(!inReach)return;
 r.ready=s.prep>0?s.prep>=s.windup-1e-9:u.cd<=0&&s.energy>=s.cost;
 r.readinessReason=s.prep>0?(r.ready?"prepared_prerequisites":"winding_up"):(r.ready?"start_preparation_prerequisites":u.cd>0?"cooldown":"energy");
}
void Controller::submit(UnitId id,Command cmd){
 const auto& o=snapshot().units;const auto& u=unit(o,id);
 if(u.team!=side_||!std::isfinite(cmd.movement.x)||!std::isfinite(cmd.movement.y)||!std::isfinite(cmd.movement.multiplier)||!std::isfinite(cmd.movement.stop)||
    cmd.movement.stop<0||cmd.movement.multiplier<0||cmd.movement.multiplier>1||cmd.movement.controllerFailure||
    (cmd.hasAim&&(!std::isfinite(cmd.aim.x)||!std::isfinite(cmd.aim.y)||cmd.aim.x<0||cmd.aim.y<0||cmd.aim.x>o.width||cmd.aim.y>o.height))||
    (cmd.hasAim&&u.role==ObservedRole::Artillery&&(distance({u.x,u.y},cmd.aim)<u.minRange||distance({u.x,u.y},cmd.aim)>u.range))||
    (cmd.volley&&u.role!=ObservedRole::Artillery)||cmd.volley>9007199254740991ULL||
    (cmd.fire!=FireIntent::Automatic&&cmd.fire!=FireIntent::Hold&&cmd.fire!=FireIntent::Release))throw std::invalid_argument("invalid adapter command");
 if(cmd.movement.target){bool legal=false;for(const auto& t:o.units)if(t.id==cmd.movement.target&&t.team!=side_&&t.hp>0)legal=true;if(!legal)throw std::invalid_argument("invalid adapter target");}
 auto& r=records_.at(id);r.candidate=cmd;
 // New attack commands cannot override a live reaction/body/failure winner.
 if(r.winner=="react"||r.winner=="guard"||r.winner=="body_ability"||r.winner=="failure"){
  r.executed.volley=cmd.volley;r.executed.hasAim=cmd.hasAim;r.executed.aim=cmd.aim;readiness(id);return;
 }
 r.executed=cmd;r.executed.movement=participate(o,id,cmd.movement);r.winner="command";r.reason="explicit_adapter_command";
 readiness(id);
}
void Controller::executed(UnitId id,const World& w,uint32_t i){auto& r=records_.at(id);const auto& d=w.state[i].decision;r.engineRelease=d.release;r.executed.movement.x=d.move?d.goal.x:w.units[i].pos.x;r.executed.movement.y=d.move?d.goal.y:w.units[i].pos.y;r.executed.movement.multiplier=d.move?d.multiplier:0;r.executed.movement.stop=d.stop;const auto* t=w.resolve(w.units[i].target);r.executed.movement.target=t&&t->alive?t->id:0;if(!w.state[i].inReach){r.ready=false;r.readinessReason="post_bridge_not_in_reach";}}
Config configuration(js::V request){
 auto clean=js::obj({});for(auto k:js::keys(request))if(js::str(k)!="labReact")js::set(clean,k,js::get(request,k));
 auto extension=js::get(request,"labReact");if(extension.tag!=js::V::Undefined){shape_lab::only(extension,{"shadow"});boolean(extension,"shadow",false);}
 auto config=shape_lab::configuration(clean);
 for(const auto& p:config.controllers)if(p.name=="v7+react"||p.name=="forcedP16+react")if(config.rules!=Rules::Game)throw std::invalid_argument("react adapter v1 requires Game rules");
 return config;
}
World create(std::shared_ptr<const Config> c,js::V request){auto w=shape_lab::create(c,request);const bool shadow=boolean(js::get(request,"labReact"),"shadow",false);for(uint8_t side=0;side<2;++side)if(auto* p=controller(w,side))p->shadow(shadow);return w;}
void prepare(World& w){for(uint8_t side=0;side<2;++side)if(auto* c=controller(w,side))c->snapshot(react_v1::observe(w,side));}
void shadows(World& w){for(uint8_t side=0;side<2;++side)if(auto* c=controller(w,side))if(c->shadow()){
 // Isolated teacher REACT only, not a full T-elite planner. No simulation/search.
 World teacher(w.config);teacher.copyFrom(w);teacher.work=std::make_shared<WorkCounters>();teacher.random=c->shadowRandom();
 auto config=std::make_shared<Config>(*w.config);auto& sk=config->skills[side];sk=CombatSkills{};sk.smartShells=sk.castDodge=sk.dodgeShots=true;sk.shotReact=.12;teacher.config=config;teacher.packs[side].enabled=false;
 for(auto i:w.active)if(w.units[i].team==side){teacher.state[i].standoff=0;teacher.tactical[i]=TacticalState{};decideUnit(teacher,i);const auto& d=teacher.state[i].decision;
  const bool active=d.move&&d.release==Release::None&&teacher.state[i].guardUntil<=teacher.time;
  c->teacher(w.units[i].id,{active,active?d.goal:Vec2{},active?"engine_decideUnit_REACT":"none"});}
 c->shadowRandom()=teacher.random;
}}
void decide(World& w,uint32_t i){
 auto* c=controller(w,w.units[i].team);if(!c){astelia::controllerDecision(w,i);return;}
 auto d=c->decide(w.observations[w.units[i].team],w.units[i].id);applyControllerDecision(w,i,d);
 const auto* cmd=c->command(w.units[i].id);
 if(cmd->hasAim&&w.units[i].role==Role::Artillery){const double dist=distance(w.units[i].pos,cmd->aim);if(dist<w.state[i].minRange||dist>w.units[i].range){w.state[i].decision.release=Release::None;w.state[i].inReach=false;}}
 if(cmd->fire==FireIntent::Hold){w.state[i].decision.release=Release::None;w.state[i].inReach=false;}
 if(c->records().at(w.units[i].id).winner=="react")observer_v1::dodge(w,i,true,{d.x,d.y});
 c->executed(w.units[i].id,w,i);
}
void constrainPrep(World& w){for(auto i:w.active)if(auto* c=controller(w,w.units[i].team)){const auto* cmd=c->command(w.units[i].id);if(cmd&&cmd->fire==FireIntent::Hold)w.state[i].castOk=false;}}
Vec2 aimPoint(const World& w,uint32_t i,Vec2 fallback){if(auto* c=controller(w,w.units[i].team))if(auto* cmd=c->command(w.units[i].id))if(cmd->hasAim)return cmd->aim;return fallback;}
bool aimReach(const World& w,uint32_t i){if(auto* c=controller(w,w.units[i].team))if(auto* cmd=c->command(w.units[i].id))if(cmd->hasAim){const double d=distance(w.units[i].pos,cmd->aim);return d>=w.state[i].minRange&&d<=w.units[i].range;}return true;}
void telemetry(const World& w){
 js::Args rows;for(uint8_t side=0;side<2;++side)if(auto* c=controller(w,side))for(const auto& kv:c->records()){const auto& r=kv.second;
 rows.push_back(js::obj({{"id",double(r.id)},{"team",double(side)},{"role",r.role},{"primitive",r.primitive},{"active",r.active},{"candidate",commandJSON(r.candidate)},{"reactCandidate",commandJSON(r.reactCandidate)},{"executed",commandJSON(r.executed)},{"engineRelease",double(r.engineRelease)},{"winner",r.winner},{"reason",r.reason},{"ready",r.ready},{"readinessReason",r.readinessReason},{"volley",double(r.executed.volley)},{"shadowEnabled",c->shadow()},{"teacherReact",c->shadow()?js::obj({{"active",r.teacher.active},{"goal",js::arr({r.teacher.goal.x,r.teacher.goal.y})},{"kind",r.teacher.kind}}):js::V(nullptr)}}));}
 if(!rows.empty())std::cout<<js::stringify(js::obj({{"reactV1",true},{"t",w.time},{"rows",js::arr(std::move(rows))}}))<<'\n';
}
} // namespace react_v1
