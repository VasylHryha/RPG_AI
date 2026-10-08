// Fixture-only RPC shares the deployed prepare/support/planner code. It neither
// calls collect nor coreStep; the planner rollout is disabled by public project.
namespace {
V fixture(V req){using namespace astelia;using namespace s1_script;
 reset(js::truth(js::get(req,"wrapper")));Host h(0,{},true);js::Args output;
 for(auto frame:js::get(req,"frames").p->items){h.tick=uint64_t(js::num(js::get(frame,"tick")));h.views=js::get(frame,"views").p->items;
  auto cs=js::get(frame,"casts");if(cs.tag!=V::Undefined){h.casts.clear();for(auto key:js::keys(cs)){auto v=js::get(cs,js::str(key));auto id=UnitId(std::stoul(js::str(key)));auto& c=h.casts[id];c.pending=true;c.lockedTarget=UnitId(js::num(js::get(v,"target")));auto a=js::get(v,"aim");c.lockedAim={js::num(a.p->items[0]),js::num(a.p->items[1])};c.aimLocked=js::truth(js::get(v,"aimLocked"));c.started=uint64_t(js::num(js::get(v,"started")));c.originDecision=uint64_t(js::num(js::get(v,"originDecision")));c.originVolley=uint64_t(js::num(js::get(v,"originVolley")));}}
  h.prepare({});js::Args actions,cmds;V projections=js::arr({});
  if(js::truth(js::get(frame,"native_projection"))&&!h.views.empty()){
   slice_teacher::PlannerInput in;auto s=h.views[0];in.units=publicView(s).units;
   for(auto wire:h.views){auto id=UnitId(js::num(js::get(wire,"self")));for(auto u:js::get(wire,"units").p->items)if(js::num(js::get(u,"id"))==id)in.guns.push_back({id,0,js::num(js::get(u,"windup")),js::num(js::get(u,"lob")),js::num(js::get(u,"splash")),false});}
   for(auto th:js::get(s,"threats").p->items){auto k=js::str(js::get(th,"kind"));if(k=="shell"||k=="own_shell")in.shells.push_back({{js::num(js::get(th,"x")),js::num(js::get(th,"y"))},js::num(js::get(th,"at")),js::num(js::get(th,"damage")),js::num(js::get(th,"radius")),uint8_t(k=="own_shell"?0:1)});}
   auto w=slice_teacher::project(in);w.observations[0]=in.units;w.dt=js::num(js::get(s,"dt"));
   for(auto u:js::get(s,"units").p->items)if(js::num(js::get(u,"team"))==0)for(auto i:w.active)if(w.units[i].id==js::num(js::get(u,"id"))){auto& st=w.state[i];st.prep=js::num(js::get(u,"prep"));st.guardUntil=js::num(js::get(u,"guard_until"));st.energy=js::num(js::get(u,"energy"));st.cost=js::num(js::get(u,"cost"));st.timeRate=js::num(js::get(u,"time_rate"));w.units[i].cooldown=js::num(js::get(u,"cooldown"));}
   auto deployed=std::make_unique<Host>(h);auto* pointer=deployed.get();pointer->collector.events.clear();w.controllers[0]=std::move(deployed);
   for(auto i:w.active)if(w.units[i].team==0&&pointer->cache.count(w.units[i].id))net_slice::decide(w,i);
   projections=pointer->collector.drain();h.casts=pointer->casts;
  }

  for(auto p:h.cache)actions.push_back(js::obj({{"id",double(p.first)},{"action",json(p.second)}}));
  for(auto p:commands)cmds.push_back(js::obj({{"id",double(p.first)},{"focus",double(p.second.focus)},{"absolute",js::arr({p.second.absolute.x,p.second.absolute.y})},{"shape",js::arr({p.second.shape.x,p.second.shape.y})},{"refreshed",p.second.refreshed},{"plan",double(p.second.plan)},{"expiry",p.second.expiry}}));
  output.push_back(js::obj({{"tick",double(h.tick)},{"actions",js::arr(std::move(actions))},{"commands",js::arr(std::move(cmds))},{"events",h.collector.drain()},{"native_projection",projections}}));
 }return js::arr(std::move(output));}
}
int main(int argc,char** argv){try{if(argc!=2)throw std::runtime_error("explicit --collect or --fixture required");bool run=std::string(argv[1])=="--collect";if(!run&&std::string(argv[1])!="--fixture")throw std::runtime_error("unknown mode");std::string line;while(std::getline(std::cin,line)){auto req=js::parse(line);if(run)collect(req);else std::cout<<js::stringify(fixture(req))<<'\n';js::collect({},0);}}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}
