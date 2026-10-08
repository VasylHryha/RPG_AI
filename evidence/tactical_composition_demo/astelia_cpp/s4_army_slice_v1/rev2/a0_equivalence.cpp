// Same public states/history, separate controllers and Worlds. No combat advancement.
#include "a0_oracle.h"
#include "shapes.h"
#include "controller_bridge.h"
#include "geometry.h"
#include <fstream>
#include <iostream>
using namespace astelia;
struct Count {unsigned rows=0,mismatches=0;};
std::map<std::string,std::map<std::string,Count>> counts;
std::map<std::string,unsigned> coverage;
bool close(double a,double b){return std::isfinite(a)&&std::isfinite(b)&&std::abs(a-b)<1e-9;}
void compare(const std::string& role,const std::string& type,bool same){auto& c=counts[role][type];++c.rows;c.mismatches+=!same;}
bool movement(const UnitDecision& a,const UnitDecision& b){return close(a.x,b.x)&&close(a.y,b.y)&&close(a.multiplier,b.multiplier)&&close(a.stop,b.stop)&&a.controllerFailure==b.controllerFailure;}
bool command(const react_v1::Command& a,const react_v1::Command& b){return movement(a.movement,b.movement)&&a.movement.target==b.movement.target&&a.fire==b.fire&&a.hasAim==b.hasAim&&(!a.hasAim||(close(a.aim.x,b.aim.x)&&close(a.aim.y,b.aim.y)))&&a.volley==b.volley;}
double number(js::V o,const char* k){auto v=js::get(o,k);if(v.tag!=js::V::Number||!std::isfinite(v.n))throw std::invalid_argument(std::string("missing finite fixture field ")+k);return v.n;}
react_v1::Snapshot parse(js::V row){react_v1::Snapshot s;auto& o=s.units;o.t=number(row,"t");o.dt=number(row,"dt");o.width=1400;o.height=800;
 for(auto v:js::get(row,"units").p->items){const auto& a=v.p->items;control::ObservedUnit u;
  u.id=UnitId(a[0].n);u.team=uint8_t(a[1].n);u.role=ObservedRole(int(a[2].n));u.x=a[3].n;u.y=a[4].n;u.hp=a[5].n;u.radius=a[6].n;u.range=a[7].n;u.minRange=a[8].n;u.target=UnitId(a[9].n);
  u.vx=a[10].n;u.vy=a[11].n;u.maxhp=a[12].n;u.speed=a[13].n;u.dmg=a[14].n;u.cdMax=a[15].n;u.cd=a[16].n;u.dealtToEnemy=a[17].n;u.takenFromEnemy=a[18].n;o.units.push_back(u);
  if(u.team==0)s.own.push_back({u.id,a[19].n,a[20].n,a[21].n,1,a[22].n,a[23].n,js::truth(a[24])});
 }
 for(auto v:js::get(row,"shells").p->items){const auto& a=v.p->items;s.shells.push_back({{a[0].n,a[1].n},{a[0].n,a[1].n},a[2].n,a[3].n,false});}
 return s;
}
control::ControllerParams params(js::V row){control::ControllerParams out;auto p=js::get(row,"params");for(auto key:js::keys(p))out[js::str(key)]=js::num(js::get(p,js::str(key)));return out;}
struct Fixture {
 std::shared_ptr<Config> config;
 World t,g;
 react_v1::Controller *tc,*gc;
 unsigned previousSize=0;
 Fixture(control::ControllerParams p):config(std::make_shared<Config>(gameConfig())),t(config),g(config){
  config->width=1400;config->height=800;config->abilities=false;
  auto a=std::make_unique<react_v1::Controller>(1,0,p,control::V7Selector::P16),b=std::make_unique<react_v1::Controller>(1,0,p,control::V7Selector::P16);
  tc=a.get();gc=b.get();tc->shape.arm="T";gc->shape.arm="O+G";t.controllers[0]=std::move(a);g.controllers[0]=std::move(b);
 }
 void bind(World& w,const react_v1::Snapshot& s){
  // Rebuild physical value fixtures, preserving independently held controller history.
  World fresh(config);fresh.controllers[0]=std::move(w.controllers[0]);w=std::move(fresh);
  // World ID authority need not match stable public IDs; manual remap immediately.
  for(const auto& u:s.units.units){auto ref=w.add(u.team,Role(u.role),{u.x,u.y});auto& a=w.units[ref.slot];auto& st=w.state[ref.slot];a.id=u.id;a.hp=u.hp;a.maxhp=u.maxhp;a.radius=u.radius;a.speed=u.speed;a.range=u.range;a.damage=u.dmg;a.cooldown=u.cd;a.velocity={u.vx,u.vy};st.minRange=u.minRange;st.cooldownMax=u.cdMax;
   for(const auto& v:s.own)if(v.id==u.id){st.guardUntil=v.guardUntil;st.prep=v.prep;st.windup=v.windup;st.timeRate=v.timeRate;st.energy=v.energy;st.cost=v.cost;st.lobSpeed=300;st.launch=1;st.splash=40;}
  }
  w.time=s.units.t;w.dt=s.units.dt;w.observations[0]=s.units;
  // Keep planner's existing public in-flight shells in both fixture Worlds.
  for(const auto& sh:s.shells){UnitRef source;for(auto i:w.teams[1])if(w.units[i].role==Role::Artillery){source=w.reference(i);break;}if(!source)continue;Shell p;p.source=source;p.pos=sh.landing;p.at=sh.at;p.damage=40;p.splash=sh.radius;w.shells.push_back(p);}
 }
 void frame(const react_v1::Snapshot& s){if(previousSize>s.units.units.size())++coverage["target_removal_frames"];previousSize=s.units.units.size();bind(t,s);bind(g,s);tc->snapshot(s);gc->snapshot(s);tc->prepare(s.units);gc->prepare(s.units);
  for(const auto& u:s.units.units)if(u.team==0&&u.hp>0){const auto& a=tc->records().at(u.id);const auto& b=gc->records().at(u.id);const std::string role=roleName(Role(u.role));
   if(a.candidate.movement.controllerFailure||b.candidate.movement.controllerFailure)throw std::runtime_error("equivalence fixture policy failed closed; cannot count healthy parity");
   ++coverage["healthy_unit_rows"];coverage["react_rows"]+=a.active;coverage["guard_rows"]+=a.winner=="guard";coverage["body_rows"]+=a.winner=="body_ability";
   compare(role,"base_movement",movement(a.candidate.movement,b.candidate.movement));compare(role,"base_target",a.candidate.movement.target==b.candidate.movement.target);
   compare(role,"participation_react_body",command(a.executed,b.executed)&&a.winner==b.winner&&a.active==b.active);
  }
  for(auto i:t.active)if(t.units[i].team==0)react_v1::decide(t,i);
  for(auto i:g.active)if(g.units[i].team==0)react_v1::decide(g,i);
  for(auto i:t.active)if(t.units[i].team==0){auto id=t.units[i].id;auto j=std::find_if(g.active.begin(),g.active.end(),[&](auto k){return g.units[k].id==id;});auto& a=t.state[i].decision;auto& b=g.state[*j].decision;
   compare(roleName(t.units[i].role),"bridge_move_target_release",close(a.goal.x,b.goal.x)&&close(a.goal.y,b.goal.y)&&close(a.multiplier,b.multiplier)&&close(a.stop,b.stop)&&a.move==b.move&&a.post==b.post&&a.release==b.release&&tc->command(id)->movement.target==gc->command(id)->movement.target&&t.state[i].inReach==g.state[*j].inReach);
  }
  unsigned ready=0;for(auto i:t.active)if(t.units[i].team==0&&t.units[i].role==Role::Artillery){const auto id=t.units[i].id;const auto& record=tc->records().at(id);const auto* target=t.resolve(t.units[i].target);const auto* cmd=tc->command(id);
   ready+=prepared(t,i)&&t.state[i].inReach&&target&&target->alive&&cmd->fire!=react_v1::FireIntent::Hold&&!record.active&&record.winner!="guard"&&record.winner!="body_ability"&&record.winner!="failure";
  }
  army_a0::geometry(t);army_a0::geometry(g);
  for(const auto& event:tc->shape.audit)if(js::truth(js::get(event,"a0Event"))){const auto eligible=js::num(js::get(event,"eligible"));coverage[eligible==1?"single_applied":"multi_applied"]+=unsigned(js::num(js::get(event,"applied")));}
  const std::string type=ready==0?"aim_no_ready":ready==1?"aim_single_ready":"aim_multi_ready";
  for(const auto& u:s.units.units)if(u.team==0&&u.hp>0){const auto* a=tc->command(u.id);const auto* b=gc->command(u.id);compare(roleName(Role(u.role)),"executed_command",command(*a,*b));if(u.role==ObservedRole::Artillery)compare("artillery",type,command(*a,*b));}
  tc->shape.audit.clear();gc->shape.audit.clear();
 }
};
int main(int argc,char** argv){try{
 if(argc!=2)throw std::invalid_argument("fixture JSONL path required");
 std::ifstream f(argv[1]);std::string line;std::unique_ptr<Fixture> fixture;unsigned frames=0;
 while(std::getline(f,line)){auto row=js::parse(line);if(js::truth(js::get(row,"reset")))fixture=std::make_unique<Fixture>(params(row));if(!fixture)throw std::runtime_error("missing reset");fixture->frame(parse(row));++frames;}
 if(!frames)throw std::runtime_error("empty equivalence fixture");
 // Prove the comparator is sensitive to every output channel.
 react_v1::Command a,b;b.movement.target=3;if(command(a,b))throw std::runtime_error("target comparator blind");b=a;b.movement.multiplier=.5;if(command(a,b))throw std::runtime_error("movement comparator blind");b=a;b.fire=react_v1::FireIntent::Hold;if(command(a,b))throw std::runtime_error("fire comparator blind");b=a;b.hasAim=true;b.aim={12,13};if(command(a,b))throw std::runtime_error("aim comparator blind");
 js::V roles=js::obj({}),covered=js::obj({});for(auto c:coverage)js::set(covered,c.first,double(c.second));unsigned total=0;
 for(const auto& r:counts){js::V types=js::obj({});for(const auto& k:r.second){total+=k.second.mismatches;js::set(types,k.first,js::obj({{"rows",double(k.second.rows)},{"mismatches",double(k.second.mismatches)},{"rate",double(k.second.mismatches)/k.second.rows}}));}js::set(roles,r.first,types);}
 std::cout<<js::stringify(js::obj({{"status",total?"FAIL":"PASS"},{"frames",double(frames)},{"total_mismatches",double(total)},{"by_role_and_decision",roles},{"coverage",covered},{"combat_steps",0}}))<<'\n';return total?1:0;
 }catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}
