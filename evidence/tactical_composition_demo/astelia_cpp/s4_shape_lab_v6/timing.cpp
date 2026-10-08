#include "timing.h"
#include "react.h"
#include "geometry.h"
#include "artillery.h"
#include "../s4_shape_lab_v1/lab_native.h"
#include <set>
namespace battery_v1 {
struct DummySnapshot {react_v1::Snapshot snapshot;};
void prepareDummies(World& w){for(uint8_t side=0;side<2;++side)if(auto* d=dynamic_cast<DodgingDummy*>(w.controllers[side].get()))d->view=std::make_shared<DummySnapshot>(DummySnapshot{react_v1::observe(w,side)});}
UnitDecision DodgingDummy::decide(const control::Observation& o,UnitId id){
 const control::ObservedUnit* self=nullptr;for(const auto& u:o.units)if(u.id==id)self=&u;if(!self||!view)throw std::logic_error("dummy snapshot absent");
 auto r=react_v1::react(view->snapshot,id);return {r.active?r.goal.x:self->x,r.active?r.goal.y:self->y,r.active?1.0:0.0,0,0};
}

std::map<UnitId,bool> Battery::step(const std::vector<Gun>& guns,double t,double dt){
 if(!(dt>0)||!std::isfinite(dt)||!std::isfinite(t)||!std::isfinite(k)||k<=0||!(radius>0))throw std::invalid_argument("invalid oscillator step");
 std::set<UnitId> live;for(const auto& g:guns){if(!(g.T>0)||!std::isfinite(g.T)||!live.insert(g.id).second)throw std::invalid_argument("invalid gun cycle/id");
  if(!states.count(g.id)){State s;s.phi=tau*(double((uint64_t(g.id)*2654435761ULL)%4294967296ULL)/4294967296.0);states[g.id]=s;}}
 for(auto it=states.begin();it!=states.end();)if(!live.count(it->first))it=states.erase(it);else ++it;
 std::map<UnitId,bool> crossed,release;
 const unsigned steps=unsigned(std::ceil(dt*120));const double h=dt/steps;
 for(unsigned iter=0;iter<steps;++iter){std::map<UnitId,double> next;
  for(const auto& g:guns){auto& s=states.at(g.id);double sum=0;unsigned n=0;
   for(const auto& j:guns)if(j.id!=g.id&&distance(g.pos,j.pos)<=radius){sum+=std::sin(states.at(j.id).phi-s.phi);++n;}
   s.neighbours=n;double p=s.phi+h*(tau/g.T+(n?k/g.T*sum/n:0));
   if(std::floor(p/tau)>std::floor(s.phi/tau))crossed[g.id]=true;
   next[g.id]=std::fmod(p,tau);if(next[g.id]<0)next[g.id]+=tau;
  }for(const auto& v:next)states.at(v.first).phi=v.second;
 }
 for(const auto& g:guns){auto& s=states.at(g.id);
  if(g.ready){if(s.waiting<0)s.waiting=t-dt;}else s.waiting=-1;
  const bool bound=g.ready&&s.waiting>=0&&t-s.waiting>=g.T-1e-9;
  release[g.id]=g.ready&&g.legal&&(crossed[g.id]||bound);
  s.hold=g.ready&&g.legal&&!release[g.id];if(s.hold)s.idle+=dt;
  s.reason=release[g.id]?(bound?"one_cycle_bound":"phase_crossing"):g.ready?(g.legal?"wait_phase":"illegal_or_reacting"):"not_ready";
  if(release[g.id])s.volley=uint64_t(std::floor(t*30+.5))+1;
 }
 return release;
}
namespace {
react_v1::Controller* controller(World& w,uint8_t side){return dynamic_cast<react_v1::Controller*>(w.controllers[side].get());}
const react_v1::Controller* controller(const World& w,uint8_t side){return dynamic_cast<const react_v1::Controller*>(w.controllers[side].get());}
react_v1::Command command(const World& w,uint32_t i,react_v1::Controller& c){auto cmd=*c.command(w.units[i].id);
 // Exact P16 fallback from actNovice; no V2 aim, offsets or target changes.
 const auto* target=w.resolve(w.units[i].target);if(target){const auto& sk=w.config->skills[w.units[i].team];const auto& ts=w.state[w.units[i].target.slot];
  const bool steady=ts.longSpeed>30&&length(ts.longVelocity)/ts.longSpeed>.8;
  const auto& s=w.state[i];const double fl=distance(w.units[i].pos,target->pos)/((s.lobSpeed>0?s.lobSpeed:300)*s.launch);
  const auto aim=target->pos+(sk.lobLead||(sk.adaptiveLobLead&&steady)?ts.longVelocity*fl:Vec2{});
  if(distance(w.units[i].pos,aim)>=s.minRange&&distance(w.units[i].pos,aim)<=w.units[i].range){cmd.hasAim=true;cmd.aim=aim;}}
 return cmd;
}
bool legal(const World& w,uint32_t i,const react_v1::Controller& c){const auto& r=c.records().at(w.units[i].id);const auto* t=w.resolve(w.units[i].target);
 return t&&t->alive&&t->team!=w.units[i].team&&w.state[i].inReach&&!r.active&&r.winner!="guard"&&r.winner!="body_ability"&&r.winner!="failure";}
void submit(World& w,uint32_t i,react_v1::Controller& c,react_v1::Command cmd,bool release){cmd.fire=release?react_v1::FireIntent::Release:react_v1::FireIntent::Hold;c.submit(w.units[i].id,cmd);react_v1::decide(w,i);}
}
Config configuration(js::V req){auto clean=js::obj({});for(auto key:js::keys(req))if(js::str(key)!="labBattery")js::set(clean,key,js::get(req,key));
 auto ext=js::get(req,"labBattery");shape_lab::only(ext,{"mode","k","radius"});auto mode=js::str(js::get(ext,"mode"));
 if(mode!="base"&&mode!="central_sync"&&mode!="battery_oscillator")throw std::invalid_argument("invalid battery mode");
 const double k=shape_lab::number(ext,"k"),r=shape_lab::number(ext,"radius");if((k!=.5&&k!=1&&k!=2)||(r!=200&&r!=400&&r!=-1))throw std::invalid_argument("undeclared oscillator grid");
 return react_v1::configuration(clean);
}
World create(std::shared_ptr<const Config> config,js::V req){auto w=react_v1::create(config,req);auto ext=js::get(req,"labBattery");
 auto* c=controller(w,0);if(!c)throw std::invalid_argument("battery requires forcedP16+react");auto& b=c->battery;
 const auto mode=js::str(js::get(ext,"mode"));b.mode=mode=="base"?0:mode=="central_sync"?1:2;b.k=shape_lab::number(ext,"k");b.radius=shape_lab::number(ext,"radius");if(b.radius==-1)b.radius=INFINITY;
 return w;
}
// Verbatim waves predicate/body from combat.cpp::coreStep, restricted to our guns.
bool copiedWaves(World& w,uint32_t i,unsigned waves){auto& s=w.state[i];const auto* t=w.resolve(w.units[i].target);
 if(waves>0&&!(s.prep>0)&&w.units[i].cooldown<=0&&s.inReach&&t&&t->alive&&s.energy>=s.cost&&windup(w,i)>0){
  uint32_t n=0;for(auto j:w.teams[w.units[i].team])if(w.units[j].alive&&w.state[j].inReach&&w.units[j].cooldown<=0&&!(w.state[j].prep>0)&&w.state[j].windup>0)++n;
  auto& ts=w.tactical[i];if(ts.waitFrom<0)ts.waitFrom=w.time;if(n<waves&&w.time-ts.waitFrom<1)return false;else ts.waitFrom=-1;}
 return true;
}
void central(World& w){for(uint8_t side=0;side<2;++side)if(auto* c=controller(w,side))if(c->battery.mode==1){
 // All engine targets/reach have already been applied, before preparation.
 std::vector<std::pair<uint32_t,bool>> releases;
 for(auto i:w.order)if(w.units[i].team==side&&w.units[i].role==Role::Artillery){auto& s=w.state[i];bool pass=true;
  if(!(s.prep>0)&&w.units[i].cooldown<=0&&s.inReach&&w.resolve(w.units[i].target)&&s.energy>=s.cost&&windup(w,i)>0){pass=copiedFireGate(w,i);if(pass)pass=copiedWaves(w,i);}
  releases.push_back({i,pass});}
 for(auto [i,pass]:releases){auto& st=c->battery.states[w.units[i].id];st.hold=!pass;st.reason=pass?"engine_sync_release":"engine_sync_hold";
  if(st.hold)st.idle+=w.dt;if(pass&&w.state[i].prep<=0&&w.units[i].cooldown<=0&&legal(w,i,*c))st.volley=uint64_t(std::floor(w.time*30+.5))+1;
  auto cmd=command(w,i,*c);cmd.volley=st.volley;submit(w,i,*c,cmd,pass);}
}}
void oscillator(World& w){for(uint8_t side=0;side<2;++side)if(auto* c=controller(w,side)){
 auto& b=c->battery;std::vector<Gun> guns;
 for(auto i:w.active)if(w.units[i].team==side&&w.units[i].role==Role::Artillery)guns.push_back({w.units[i].id,w.units[i].pos,w.state[i].cooldownMax+w.state[i].windup,prepared(w,i),legal(w,i,*c)});
 if(b.mode!=2){for(const auto& g:guns)b.states.try_emplace(g.id);continue;}
 const auto release=b.step(guns,w.time,w.dt);
 for(auto i:w.active)if(w.units[i].team==side&&w.units[i].role==Role::Artillery){auto cmd=command(w,i,*c);cmd.volley=b.states.at(w.units[i].id).volley;submit(w,i,*c,cmd,release.at(w.units[i].id));}
}}
void fired(World& w,uint32_t i){if(auto* c=controller(w,w.units[i].team)){auto& b=c->battery;if(b.mode==2)b.fired(w.units[i].id);}}
js::V rows(const World& w){js::Args out;for(uint8_t side=0;side<2;++side)if(auto* c=controller(w,side))for(auto i:w.active)if(w.units[i].team==side&&w.units[i].role==Role::Artillery){
 const auto& b=c->battery;const auto it=b.states.find(w.units[i].id);if(it==b.states.end())continue;const auto& s=it->second;
 out.push_back(js::arr({double(w.units[i].id),double(side),w.state[i].cooldownMax+w.state[i].windup,s.phi,s.idle,double(s.volley),s.hold,double(s.neighbours),s.reason}));}
 return js::arr(std::move(out));}
}

namespace battery_v1 {
void launch(World& w,uint32_t i,const Shell& sh){if(sh.slow||w.units[i].team!=0)return;auto* c=controller(w,0);if(!c)return;auto& b=c->battery;
 auto& s=b.states[w.units[i].id];if(b.mode==0)s.volley=uint64_t(std::floor(w.time*30+.5))+1;
 Exposure e{w.units[i].id,sh.born,sh.at,s.volley,{}};js::Args ids;
 for(auto j:w.active)if(w.units[j].alive&&w.units[j].team==1&&distance(w.units[j].pos,sh.pos)<=sh.splash+w.units[j].radius){e.ids.push_back(w.units[j].id);ids.push_back(double(w.units[j].id));}
 b.exposures.push_back(e);b.audit.push_back(js::obj({{"type","launch"},{"source",double(e.source)},{"born",e.born},{"at",e.at},{"volley",double(e.volley)},{"exposed",js::arr(std::move(ids))}}));
}
void landing(World& w,const Shell& sh){const auto* src=w.resolve(sh.source);if(!src||src->team!=0||sh.slow)return;auto* c=controller(w,0);if(!c)return;auto& b=c->battery;
 auto it=std::find_if(b.exposures.begin(),b.exposures.end(),[&](const Exposure& e){return e.source==src->id&&e.born==sh.born&&e.at==sh.at;});if(it==b.exposures.end())throw std::logic_error("missing launch exposure");
 unsigned escaped=0,eligible=0,censored=0;
 for(auto id:it->ids){const UnitHot* target=nullptr;for(const auto& u:w.units)if(u.id==id&&u.occupied)target=&u;
  if(!target||!target->alive){++censored;continue;}++eligible;if(distance(target->pos,sh.pos)>sh.splash+target->radius)++escaped;}
 b.audit.push_back(js::obj({{"type","landing"},{"source",double(it->source)},{"born",it->born},{"at",it->at},{"eligible",double(eligible)},{"escaped",double(escaped)},{"censored",double(censored)}}));b.exposures.erase(it);
}
js::V audits(World& w){js::Args a;if(auto* c=controller(w,0))a.swap(c->battery.audit);return js::arr(std::move(a));}
}
