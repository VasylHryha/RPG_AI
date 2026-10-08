#include "shapes.h"
#include "react.h"
#include "geometry.h"
#include "controller_bridge.h"
#include "../s4_shape_lab_v1/lab_native.h"
#include <set>
namespace shapes_v6 {
namespace {
const control::ObservedUnit& unit(const control::Observation& o,UnitId id){for(const auto& u:o.units)if(u.id==id)return u;throw std::invalid_argument("shape unit missing");}
const react_v1::OwnView& own(const react_v1::Snapshot& s,UnitId id){for(const auto& u:s.own)if(u.id==id)return u;throw std::invalid_argument("shape own missing");}
bool blocked(const react_v1::Snapshot& s,UnitId id,const UnitDecision& d){const auto& u=unit(s.units,id);const auto& v=own(s,id);return u.hp<=0||v.guardUntil>s.units.t||v.busy||d.controllerFailure;}
const control::ObservedUnit* target(const control::Observation& o,const control::ObservedUnit& u,UnitId id){for(const auto& t:o.units)if(t.id==id&&t.team!=u.team&&t.hp>0)return &t;return nullptr;}
Vec2 pos(const control::ObservedUnit& u){return {u.x,u.y};}
// With a radial reach disk intersecting the body-safe arena, the nearest
// endpoint is on its circle or a rectangle edge (including corners).
Vec2 nearestReach(const control::Observation& o,const control::ObservedUnit& u,const control::ObservedUnit& t){
 const double r=u.range+u.radius+t.radius-1;const auto c=pos(t),p=pos(u);const double len=distance(p,c);
 std::vector<Vec2> candidates;if(len>0)candidates.push_back(c+(p-c)*(r/len));
 const double xmin=u.radius,xmax=o.width-u.radius,ymin=u.radius,ymax=o.height-u.radius;
 const auto add=[&](Vec2 q){if(q.x>=xmin-1e-8&&q.x<=xmax+1e-8&&q.y>=ymin-1e-8&&q.y<=ymax+1e-8&&distance(q,c)<=r+1e-8)candidates.push_back(q);};
 add({std::clamp(p.x,xmin,xmax),ymin});add({std::clamp(p.x,xmin,xmax),ymax});add({xmin,std::clamp(p.y,ymin,ymax)});add({xmax,std::clamp(p.y,ymin,ymax)});
 for(double x:{xmin,xmax})if(std::abs(x-c.x)<=r){const double y=std::sqrt(std::max(0.0,r*r-(x-c.x)*(x-c.x)));add({x,c.y-y});add({x,c.y+y});}
 for(double y:{ymin,ymax})if(std::abs(y-c.y)<=r){const double x=std::sqrt(std::max(0.0,r*r-(y-c.y)*(y-c.y)));add({c.x-x,y});add({c.x+x,y});}
 Vec2 best=p;double bd=INFINITY;for(auto q:candidates)if(q.x>=xmin&&q.x<=xmax&&q.y>=ymin&&q.y<=ymax&&distance(q,c)<=r+1e-7&&distance(q,p)<bd){best=q;bd=distance(q,p);}return best;
}
double nextShot(const react_v1::Snapshot& s,const control::ObservedUnit& u,Vec2 q){
 const auto& v=own(s,u.id);double best=INFINITY;
 for(const auto& t:s.units.units)if(t.team!=u.team&&t.hp>0){
  const double reachRadius=u.range+u.radius+t.radius;
  const double moveTime=u.speed>0?distance(pos(u),q)/u.speed:INFINITY;
  const double cd=std::max(0.0,u.cd)/v.timeRate;
  const double windup=std::max(0.0,v.windup-v.prep)/v.timeRate;
  const auto rg=s.regeneration.find(u.id);const double regen=rg==s.regeneration.end()?0:rg->second;
  const double energy=v.prep>0||v.energy>=v.cost?0:regen>0?(v.cost-v.energy)/regen:INFINITY;
  // Conservative target displacement over the participation horizon uses
  // only observed velocity. Windup starts after returning to legal range.
  const double gap=std::max(0.0,distance(q,pos(t))+std::hypot(t.vx,t.vy)*participationHorizon-reachRadius);
  const double close=gap==0?0:u.speed>0?gap/u.speed:INFINITY;
  best=std::min(best,std::max({moveTime+close,cd,energy})+windup);

 }return best;
}
}
bool reach(const control::ObservedUnit& u,const control::ObservedUnit& t){const double d=distance(pos(u),pos(t));return u.role==ObservedRole::Artillery?d>=u.minRange&&d<=u.range:d<=u.range+u.radius+t.radius;}
Vec2 trajectory(const control::ObservedUnit& u,const UnitDecision& d,double dt){const auto delta=Vec2{d.x,d.y}-pos(u);const double len=length(delta);if(len<=d.stop+.5||d.multiplier<=0)return pos(u);return pos(u)+delta*(std::min(u.speed*d.multiplier*std::max(0.0,dt),std::max(0.0,len-d.stop))/len);}
bool legalAim(const control::Observation& o,UnitId id,const UnitDecision& movement,Vec2 aim){
 const auto& u=unit(o,id);const double before=distance(pos(u),aim),after=distance(trajectory(u,movement,o.dt),aim);
 return std::isfinite(aim.x)&&std::isfinite(aim.y)&&aim.x>=0&&aim.y>=0&&aim.x<=o.width&&aim.y<=o.height&&before>=u.minRange&&before<=u.range&&after>=u.minRange&&after<=u.range;
}

UnitDecision floor(const react_v1::Snapshot& s,UnitId id,UnitDecision d,bool reaction){const auto& u=unit(s.units,id);if(blocked(s,id,d)||reaction||own(s,id).prep>0||u.role!=ObservedRole::Ranged)return d;const auto* t=target(s.units,u,d.target);if(!t||reach(u,*t))return d;const auto q=nearestReach(s.units,u,*t);d.x=q.x;d.y=q.y;d.multiplier=1;d.stop=0;return d;}
void threats(const World& w,uint8_t side,react_v1::Snapshot& s){
 for(auto i:w.active)if(w.units[i].team==side){s.protection[w.units[i].id]=w.state[i].protection;s.regeneration[w.units[i].id]=w.state[i].energyRegen*w.state[i].timeRate;}
 for(const auto& sh:w.shells){const auto* src=w.resolve(sh.source);if(src&&src->team!=side&&!sh.slow&&sh.at>w.time)s.threats.push_back({sh.pos,{},sh.at,0,sh.splash,sh.damage});}
 for(const auto& sh:w.shots){const auto* src=w.resolve(sh.source);if(src&&src->team!=side&&sh.aimed)s.threats.push_back({sh.pos,sh.direction,w.time,0,3,sh.damage,sh.speed,sh.left,0,true,false});}
 for(const auto& c:s.casts){const auto& u=unit(s.units,c.gun);s.threats.push_back({c.landing,{},c.landingAt,c.releaseAt,c.radius,u.dmg,0,0,c.target,false,true});}
}
double damage(const react_v1::Snapshot& s,UnitId id,const UnitDecision& d){const auto& u=unit(s.units,id);double total=0;
 for(const auto& th:s.threats){if(th.damage<=0)continue;bool hit=false;
  if(th.shot){const double end=th.speed>0?th.left/th.speed:0;Vec2 previous=pos(u)-th.point;
   // Continuous closest approach on each <=1/120 s reachable segment.
   for(double t=0;t<end&&!hit;){const double next=std::min(end,t+1.0/120);const auto rel=trajectory(u,d,next)-(th.point+th.direction*(th.speed*next));const auto delta=rel-previous;const double dd=dot(delta,delta);const double f=dd>0?std::clamp(-dot(previous,delta)/dd,0.0,1.0):0;
    hit=length(previous+delta*f)<=u.radius+th.radius;previous=rel;t=next;}
  }else{Vec2 center=th.point;if(th.cast&&th.target==id)center=trajectory(u,d,std::max(0.0,th.release-s.units.t));
   hit=distance(trajectory(u,d,th.at-s.units.t),center)<=u.radius+th.radius;}
  // Own protection is known; shields and future body interactions are
  // not forecast. Triggered survival remains observational.
  if(hit){auto p=s.protection.find(id);total+=std::floor(th.damage*(1-(p==s.protection.end()?0:p->second)));}
 }return total;
}
Rotation rotate(const react_v1::Snapshot& s,UnitId id,const UnitDecision& base){const auto& u=unit(s.units,id);Rotation result;result.base=result.candidate=damage(s,id,base);
 if(blocked(s,id,base)||own(s,id).prep>0||u.role!=ObservedRole::Ranged||result.base<u.hp)return result;
 struct Candidate {Vec2 q;double loss,next,dist;std::string participation;};std::vector<Candidate> active,fallback;
 // Behind each living friend relative to the visible enemy centroid. Endpoints
 // are body-safe, within 100 px of this unit and away from arena edges.
 Vec2 enemies;unsigned count=0;for(const auto& e:s.units.units)if(e.team!=u.team&&e.hp>0){enemies=enemies+pos(e);++count;}if(!count)return result;enemies=enemies*(1.0/count);
 for(const auto& f:s.units.units)if(f.team==u.team&&f.id!=id&&f.hp>0){auto away=pos(f)-enemies;const double len=length(away);if(len==0)continue;away=away*(1/len);
  for(double space:{u.radius+f.radius+2,u.radius+f.radius+22}){auto q=pos(f)+away*space;const double dist=distance(q,pos(u));
   if(dot(q-pos(u),away)<=0||dist>retreatMax||q.x<u.radius+edgeMargin||q.x>s.units.width-u.radius-edgeMargin||q.y<u.radius+edgeMargin||q.y>s.units.height-u.radius-edgeMargin)continue;
   bool bodySafe=true;for(const auto& body:s.units.units)if(body.id!=id&&body.hp>0&&distance(q,pos(body))<u.radius+body.radius)bodySafe=false;if(!bodySafe)continue;
   auto d=base;d.x=q.x;d.y=q.y;d.multiplier=1;d.stop=0;const double loss=damage(s,id,d),next=nextShot(s,u,q);bool in=false;auto copy=u;copy.x=q.x;copy.y=q.y;for(const auto& t:s.units.units)if(t.team!=u.team&&t.hp>0&&reach(copy,t))in=true;
   Candidate c{q,loss,next,dist,in?"in_reach":next<=participationHorizon?"next_legal_shot":"nearest_bounded_survival"};if(in||next<=participationHorizon)active.push_back(c);else if(loss<u.hp)fallback.push_back(c);
  }
 }
 if(own(s,id).energy<own(s,id).cost&&!s.regeneration.count(id))return result;
 // Fallback exists only if NO participation candidate exists, even if those
 // candidates would fail the margin. Never evade participation to buy safety.
 auto& candidates=active.empty()?fallback:active;
 std::stable_sort(candidates.begin(),candidates.end(),[&](const Candidate& a,const Candidate& b){if(active.empty())return a.dist<b.dist;const bool safeA=a.loss<u.hp,safeB=b.loss<u.hp;if(safeA!=safeB)return safeA;return a.loss==b.loss?a.dist<b.dist:a.loss<b.loss;});
 for(const auto& c:candidates)if(c.loss<result.base-margin){result.active=true;result.point=c.q;result.candidate=c.loss;result.nextShot=c.next;result.participation=c.participation;break;}return result;
}
void augment(react_v1::Controller& c){const auto& s=c.snapshot();const auto& o=s.units;for(auto& entry:c.mutableRecords()){auto& r=entry.second;const auto& u=unit(o,r.id);auto before=r.executed;bool engaged=false;
 if(c.shape.arm=="E1"||c.shape.arm=="E1+R1"){auto d=floor(s,r.id,before.movement,r.active);engaged=d.x!=before.movement.x||d.y!=before.movement.y;if(engaged){r.executed.movement=d;r.winner="engagement_floor";r.reason="unchanged_selector_nearest_legal_reach";}}
 const auto counterfactualBase=r.executed.movement;
 Rotation rotation;if(c.shape.arm=="R1"||c.shape.arm=="E1+R1"){rotation=rotate(s,r.id,r.executed.movement);if(rotation.active){r.executed.movement.x=rotation.point.x;r.executed.movement.y=rotation.point.y;r.executed.movement.multiplier=1;r.executed.movement.stop=0;r.winner="predicted_lethal_rotation";r.reason=rotation.participation;}}
 if(u.role==ObservedRole::Ranged){const auto* t=target(o,u,r.executed.movement.target);const bool in=t&&reach(u,*t);const auto& v=own(s,r.id);const bool ready=u.cd<=0&&v.prep<=0&&v.energy>=v.cost;
  const bool start=rotation.active&&!c.shape.rotating[r.id];c.shape.rotating[r.id]=rotation.active;
  js::Args threatRows;
  if(start)for(const auto& th:s.threats)threatRows.push_back(js::obj({{"point",js::arr({th.point.x,th.point.y})},{"direction",js::arr({th.direction.x,th.direction.y})},{"at",th.at},{"release",th.release},{"radius",th.radius},{"damage",th.damage},{"speed",th.speed},{"left",th.left},{"target",double(th.target)},{"shot",th.shot},{"cast",th.cast}}));
  c.shape.audit.push_back(js::obj({{"threatsAtActivation",js::arr(std::move(threatRows))},{"selfAtActivation",start?js::arr({u.x,u.y,u.radius,u.speed,s.protection.count(u.id)?s.protection.at(u.id):0}):js::V(nullptr)},{"counterfactualBase",start?js::arr({counterfactualBase.x,counterfactualBase.y,counterfactualBase.multiplier,counterfactualBase.stop}):js::V(nullptr)},{"candidateTrajectory",start?js::arr({r.executed.movement.x,r.executed.movement.y,r.executed.movement.multiplier,r.executed.movement.stop}):js::V(nullptr)},{"id",double(r.id)},{"t",o.t},{"hp",u.hp},{"winner",r.winner},{"reason",r.reason},{"target",double(r.executed.movement.target)},{"baseGoal",js::arr({before.movement.x,before.movement.y})},{"goal",js::arr({r.executed.movement.x,r.executed.movement.y})},{"react",r.active},{"floor",engaged},{"inRange",in},{"ready",ready},{"eligible",in&&ready&&!r.active&&!blocked(s,r.id,r.executed.movement)},{"rotating",rotation.active},{"activation",start},{"D_base",rotation.base},{"D_p",rotation.candidate},{"nextShot",std::isfinite(rotation.nextShot)?js::V(rotation.nextShot):js::V(nullptr)}}));}
 c.readiness(r.id);
 }}
World project(const PlannerInput& input){auto config=std::make_shared<Config>(gameConfig());config->seed=1;config->width=input.units.width;config->height=input.units.height;config->abilities=false;config->skills[0]=CombatSkills{};config->skills[1]=CombatSkills{};
 auto& sk=config->skills[0];sk.artyPlan=true;sk.artyExact=false;sk.artyRobust=.5;sk.artyHerd=0;sk.artyBattery=true;sk.artyFollow=false;sk.rollout.enabled=false;sk.lead=Lead::Raw;config->skills[1].dodgeShells=true;
 World model(config);model.time=input.units.t;std::map<UnitId,UnitRef> refs;Vec2 anchor;unsigned guns=0;
 for(const auto& observed:input.units.units){const auto ref=model.add(observed.team,Role(observed.role),pos(observed));refs[observed.id]=ref;auto& u=model.units[ref.slot];auto& s=model.state[ref.slot];
  u.id=observed.id;u.hp=observed.hp;u.maxhp=observed.maxhp;u.speed=observed.speed;u.radius=observed.radius;u.range=observed.range;u.damage=observed.dmg;u.velocity=u.smoothVelocity={observed.vx,observed.vy};u.cooldown=0;s.cooldownMax=observed.cdMax;s.minRange=observed.minRange;s.prep=0;s.energy=1000;s.cost=0;s.timeRate=1;s.player=invalidSlot;s.ability=invalidSlot;
 }
 for(const auto& observed:input.units.units)if(refs.count(observed.target))model.units[refs.at(observed.id).slot].target=refs.at(observed.target);
 for(const auto& g:input.guns){auto i=refs.at(g.id).slot;auto& u=model.units[i];auto& s=model.state[i];u.target=refs.count(g.target)?refs.at(g.target):UnitRef{};s.windup=g.windup;s.lobSpeed=g.lob;s.launch=1;s.splash=g.splash;s.prep=g.eligible?g.windup:0;if(g.eligible){anchor=anchor+u.pos;++guns;}}
 model.packs[0].anchor=guns?anchor*(1.0/guns):Vec2{};
 for(const auto& p:input.shells){UnitRef source;for(auto i:model.teams[p.team])if(model.units[i].role==Role::Artillery){source=model.reference(i);break;}if(!source)continue;Shell sh;sh.source=source;sh.pos=p.point;sh.at=p.at;sh.splash=p.splash;sh.damage=p.damage;model.shells.push_back(sh);}
 return model;
}
std::vector<PlannedShot> plan(const PlannerInput& input){auto model=project(input);copiedPlanner(model,0);return model.packs[0].artilleryQueue;}
void geometry(World& w){auto* c=dynamic_cast<react_v1::Controller*>(w.controllers[0].get());if(!c||c->shape.arm!="V2")return;PlannerInput input;input.units=c->snapshot().units;
 for(auto i:w.active)if(w.units[i].team==0&&w.units[i].role==Role::Artillery){const auto& r=c->records().at(w.units[i].id);const auto* t=w.resolve(w.units[i].target);const auto& st=w.state[i];const auto* cmd=c->command(w.units[i].id);
  const bool legal=prepared(w,i)&&st.inReach&&t&&t->alive&&cmd->fire!=react_v1::FireIntent::Hold&&!r.active&&r.winner!="guard"&&r.winner!="body_ability"&&r.winner!="failure";
  input.guns.push_back({w.units[i].id,t?t->id:0,windup(w,i),(st.lobSpeed>0?st.lobSpeed:300)*st.launch,blastRadius(w,i),legal});}
 for(const auto& sh:w.shells){const auto* src=w.resolve(sh.source);if(src&&!sh.slow&&sh.at>w.time)input.shells.push_back({sh.pos,sh.at,sh.damage,sh.splash,src->team});}
 if(std::none_of(input.guns.begin(),input.guns.end(),[](const GunView& g){return g.eligible;}))return;
 auto model=project(input);copiedPlanner(model,0);
 for(const auto& q:model.packs[0].artilleryQueue){const auto id=model.units[q.gun.slot].id;for(auto i:w.active)if(w.units[i].id==id){auto cmd=*c->command(id);if(!legalAim(input.units,id,cmd.movement,q.point)){c->shape.audit.push_back(js::obj({{"plannerRejected",true},{"id",double(id)},{"t",w.time},{"reason","arena_or_post_move_range_fallback_to_base"}}));continue;}cmd.hasAim=true;cmd.aim=q.point;c->submit(id,cmd);react_v1::decide(w,i);
  c->shape.audit.push_back(js::obj({{"planner",true},{"id",double(id)},{"t",w.time},{"family",attackName(q.family)},{"aim",js::arr({q.point.x,q.point.y})},{"expectedDamage",q.prediction}}));}}
}
Config configuration(js::V req){auto clean=js::obj({});for(auto key:js::keys(req))if(js::str(key)!="labShapes")js::set(clean,key,js::get(req,key));auto ext=js::get(req,"labShapes");shape_lab::only(ext,{"arm"});auto arm=js::str(js::get(ext,"arm"));if(arm!="base"&&arm!="V2"&&arm!="E1"&&arm!="R1"&&arm!="E1+R1")throw std::invalid_argument("unknown v6 arm");return battery_v1::configuration(clean);}
World create(std::shared_ptr<const Config> config,js::V req){auto w=battery_v1::create(config,req);auto* c=dynamic_cast<react_v1::Controller*>(w.controllers[0].get());if(!c)throw std::invalid_argument("v6 requires base controller");c->shape.arm=js::str(js::get(js::get(req,"labShapes"),"arm"));return w;}
js::V audit(World& w){js::Args rows;if(auto* c=dynamic_cast<react_v1::Controller*>(w.controllers[0].get()))rows.swap(c->shape.audit);return js::arr(std::move(rows));}
void shot(World& w,uint32_t i,const Shot& sh){if(w.units[i].team!=0)return;if(auto* c=dynamic_cast<react_v1::Controller*>(w.controllers[0].get()))c->shape.shotEvents.push_back(js::arr({double(sh.ordinal),double(w.units[i].id),sh.born,sh.damage}));}
js::V shots(World& w){js::Args rows;if(auto* c=dynamic_cast<react_v1::Controller*>(w.controllers[0].get()))rows.swap(c->shape.shotEvents);return js::arr(std::move(rows));}
}
