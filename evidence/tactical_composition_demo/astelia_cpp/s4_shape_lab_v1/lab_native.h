#pragma once
// Development-only boundary and dummy bodies. Delivered engine/controller bytes are unchanged.
#include "world.h"
#include "geometry.h"
#include "config_codec.h"
#include "js_value.h"
#include <stdexcept>
#include <set>
namespace shape_lab {
using namespace astelia;
using js::V;
inline const js::Args& array(V v) {
 if(v.tag!=V::Heap||v.p->kind!=js::Object::Array)throw std::invalid_argument("lab expected array");
 return v.p->items;
}
inline void only(V v,std::initializer_list<const char*> names) {
 if(v.tag!=V::Heap||v.p->kind!=js::Object::Plain)throw std::invalid_argument("lab expected object");
 std::set<std::string> allowed;for(auto n:names)allowed.insert(n);
 for(auto k:js::keys(v))if(!allowed.count(js::str(k)))throw std::invalid_argument("unknown lab field: "+js::str(k));
}
inline double number(V v,const char* k) {
 auto n=js::get(v,k);if(n.tag!=V::Number||!std::isfinite(n.n))throw std::invalid_argument(std::string("lab finite number required: ")+k);return n.n;
}
class Dummy final:public Controller {
 int mode_; std::map<std::string,double> overrides_;
public:
 Dummy(const ControllerProfile& p,double seed,uint8_t side):Controller(seed,side),overrides_(p.params) {
  const std::vector<std::string> names={"dummy_static","dummy_static_fire","dummy_advance","dummy_advance_fire"};
  auto it=std::find(names.begin(),names.end(),p.name);if(it==names.end())throw std::invalid_argument("unknown dummy");mode_=int(it-names.begin());
  for(auto kv:overrides_)if((kv.first!="melee"&&kv.first!="ranged"&&kv.first!="artillery")||!std::isfinite(kv.second)||kv.second<0||kv.second>3||kv.second!=std::floor(kv.second))throw std::invalid_argument("invalid dummy role override");
 }
 int mode(ObservedRole r)const {const char* names[]={"melee","ranged","artillery"};auto it=overrides_.find(names[size_t(r)]);return it==overrides_.end()?mode_:int(it->second);}
 bool fixed(Role r)const{return mode(ObservedRole(uint8_t(r)))<2;}
 UnitDecision decide(const control::Observation& o,UnitId id)override {
  const ObservedUnit* self=nullptr;for(const auto& u:o.units)if(u.id==id)self=&u;
  if(!self)throw std::logic_error("dummy missing self");int m=mode(self->role);
  const ObservedUnit *gun=nullptr,*enemy=nullptr;double gd=INFINITY,ed=INFINITY;
  for(const auto& e:o.units)if(e.hp>0&&e.team!=side_) {
   double d=std::hypot(self->x-e.x,self->y-e.y);
   if(e.role==ObservedRole::Artillery&&(d<gd||(d==gd&&(!gun||e.id<gun->id)))){gd=d;gun=&e;}
   double gap=self->role==ObservedRole::Artillery?d:d-self->radius-e.radius;
   if(gap<=self->range&&(self->role!=ObservedRole::Artillery||d>=self->minRange)&&
      (d<ed||(d==ed&&(!enemy||e.id<enemy->id)))){ed=d;enemy=&e;}
  }
  // Advance toward the nearest gun; if no gun remains, hold (no undocumented pursuit).
  return {m>=2&&gun?gun->x:self->x,m>=2&&gun?gun->y:self->y,m>=2?1.0:0.0,0,(m%2&&enemy)?enemy->id:0};
 }
 std::unique_ptr<Controller> clone()const override{return std::make_unique<Dummy>(*this);}
};
inline Config configuration(V request) {
 V clean=js::obj({});for(auto k:js::keys(request))if(js::str(k)!="labScenario"&&js::str(k)!="labAbilities")js::set(clean,k,js::get(request,k));
 return astelia::configuration(clean);
}
inline World create(std::shared_ptr<const Config> c,V request) {
 auto scenario=js::get(request,"labScenario");
 if(scenario.tag!=V::Undefined){
  if(c->rules!=Rules::Game||c->scenario!=Scenario::Mirror||c->hasCustomArmy||c->hasCarried||c->hasEnemyArmy||c->army!=std::array<uint32_t,3>{10,30,10})throw std::invalid_argument("lab requires standard mirror slot template");
  only(scenario,{"sides"});if(array(js::get(scenario,"sides")).size()!=2)throw std::invalid_argument("lab requires two sides");
 }
 auto w=World::create(c);
 if(scenario.tag!=V::Undefined){
  const auto& sides=array(js::get(scenario,"sides"));std::vector<uint32_t> retained;
  for(uint8_t side=0;side<2;++side){std::array<std::vector<uint32_t>,3> slots;for(auto i:w.teams[side])slots[size_t(w.units[i].role)].push_back(i);std::array<size_t,3> used{};
   for(auto spec:array(sides[side])) {
    only(spec,{"role","kind","position","heading","hp_fraction"});const auto role=js::str(js::get(spec,"role"));size_t r=0;while(r<3&&role!=roleName(Role(r)))++r;
    if(r==3||used[r]>=slots[r].size())throw std::invalid_argument("lab role capacity exceeded");auto i=slots[r][used[r]++];
    auto name=js::get(spec,"kind");uint32_t kind=uint32_t(r);
    if(name.tag!=V::Undefined&&name.tag!=V::Null){if(name.tag!=V::String)throw std::invalid_argument("invalid lab kind");kind=invalidSlot;for(size_t k=0;k<c->kinds.size();++k)if(c->kinds[k].name==js::str(name))kind=uint32_t(k);if(kind==invalidSlot||c->kinds[kind].role!=Role(r))throw std::invalid_argument("lab kind role mismatch");}
    auto pos=js::get(spec,"position");only(pos,{"x","y"});Vec2 p{number(pos,"x"),number(pos,"y")};double hp=number(spec,"hp_fraction"),heading=number(spec,"heading");
    const auto& k=c->kinds[kind];if(hp<=0||hp>1||p.x<k.radius||p.y<k.radius||p.x>c->width-k.radius||p.y>c->height-k.radius)throw std::invalid_argument("invalid lab position/health");
    if(kind!=w.state[i].kind){
     // Use the delivered add path for kind-derived stats, then transplant into its standard role slot.
     auto tmp=w.add(side,Role(r),p,kind);auto oldid=w.units[i].id;auto oldgeneration=w.units[i].generation;auto strafe=w.state[i].strafe;
     w.units[i]=w.units[tmp.slot];w.state[i]=w.state[tmp.slot];w.units[i].id=oldid;w.units[i].generation=oldgeneration;w.state[i].strafe=strafe;
     w.units[tmp.slot].alive=w.units[tmp.slot].occupied=false;
    }
    auto& u=w.units[i];u.pos=p;u.hp=u.maxhp*hp;w.state[i].slot=p;w.state[i].guardDirection=heading;retained.push_back(i);
   }
  }
  for(auto i:w.active)if(std::find(retained.begin(),retained.end(),i)==retained.end())w.units[i].alive=w.units[i].occupied=false;
  w.active=std::move(retained);++w.membershipVersion;w.rebuildTeams();w.liveGrid.build(w.units,w.active,c->width,c->height,40);
 }
 auto ability=js::get(request,"labAbilities");if(ability.tag!=V::Undefined){if(js::str(ability)!="off")throw std::invalid_argument("labAbilities must be off");auto adjusted=std::make_shared<Config>(*w.config);adjusted->abilities=false;for(auto& sk:adjusted->skills)sk.abilities=AbilityPolicy::Off;for(auto& side:adjusted->abilityOff)side.fill(true);w.config=adjusted;}
 bool hasDummy=false;for(const auto& c:w.controllers)if(dynamic_cast<Dummy*>(c.get()))hasDummy=true;
 if(hasDummy){auto adjusted=std::make_shared<Config>(*w.config);for(uint8_t side=0;side<2;++side)if(dynamic_cast<Dummy*>(w.controllers[side].get())){adjusted->skills[side].abilities=AbilityPolicy::Off;adjusted->abilityOff[side].fill(true);}w.config=adjusted;}
 for(auto i:w.active)if(dynamic_cast<Dummy*>(w.controllers[w.units[i].team].get())){w.state[i].dodge=Dodge::None;w.state[i].block=false;}
 return w;
}
inline void separate(World& w) {
 astelia::separate(w.units,w.active,w.separationGrid,w.config->width,w.config->height,w.pushes);
 // Static dummy bodies stay fixed even when native collision resolution pushes them.
 for(auto i:w.active)if(auto* d=dynamic_cast<Dummy*>(w.controllers[w.units[i].team].get()))if(d->fixed(w.units[i].role))w.units[i].pos=w.state[i].slot;
}
}
