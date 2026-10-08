// No coreStep, fight loop, search, tuning or entropy allocation in these fixtures.
#include "react.h"
#include "geometry.h"
#include "formation.h"
#include "controller_bridge.h"
#include "observer_v1.h"
#include <iostream>
#include <iomanip>
#include <sstream>
#include <stdexcept>
using namespace astelia;
namespace {
unsigned checks=0;
void check(bool yes,const char* why){++checks;if(!yes)throw std::runtime_error(why);}
bool same(Vec2 a,Vec2 b){return a.x==b.x&&a.y==b.y;}
std::shared_ptr<Config> config(){auto c=std::make_shared<Config>(gameConfig());c->seed=73;c->scenario=Scenario::Mirror;c->mirror=true;c->army={0,0,0};c->abilities=false;c->duration=0;
 c->skills[0].smartShells=c->skills[0].castDodge=c->skills[0].dodgeShots=true;c->skills[0].shotReact=.12;return c;}
World fixture(){auto c=config();World w(c);w.time=1;w.dt=1./30;
 auto u=w.add(0,Role::Ranged,{400,400});auto other=w.add(0,Role::Ranged,{405,400});auto gun=w.add(1,Role::Artillery,{600,400});
 w.units[u.slot].target=gun;w.units[other.slot].target=gun;w.units[gun.slot].target=other;w.state[gun.slot].prep=.2;w.state[u.slot].standoff=0;w.state[other.slot].standoff=0;
 w.rebuildTeams();w.liveGrid.build(w.units,w.active,c->width,c->height,40);return w;}
void parity(World& w){
 auto o=react_v1::observe(w,0);
 for(auto i:w.active)if(w.units[i].team==0){auto copied=react_v1::react(o,w.units[i].id);World oracle(w.config);oracle.copyFrom(w);oracle.state[i].standoff=0;decideUnit(oracle,i);const auto& d=oracle.state[i].decision;
  const bool active=d.move&&d.release==Release::None&&oracle.state[i].guardUntil<=w.time;
  check(copied.active==active,"engine react activation mismatch");if(active)check(same(copied.goal,d.goal),"engine react goal mismatch");}
}
void observation(){auto w=fixture();Shell sh;sh.source=w.reference(2);sh.pos={400,400};sh.at=2;sh.splash=40;sh.born=.5;w.shells.push_back(sh);
 Shot shot;shot.source=w.reference(2);shot.pos={380,400};shot.direction={1,0};shot.born=.5;shot.speed=240;shot.left=100;w.shots.push_back(shot);
 w.fields.push_back({{405,400},45,.9,3,1});auto o=react_v1::observe(w,0);
 check(o.shells.size()==1&&same(o.shells[0].position,sh.pos)&&same(o.shells[0].landing,sh.pos)&&o.shells[0].at==sh.at&&o.shells[0].radius==sh.splash,"shell fields");
 check(o.shots.size()==1&&same(o.shots[0].position,shot.pos)&&same(o.shots[0].direction,shot.direction)&&o.shots[0].born==shot.born&&o.shots[0].left==shot.left&&o.shots[0].speed==shot.speed,"shot fields");
 check(o.fields.size()==1&&o.fields[0].from==.9&&o.fields[0].until==3&&o.fields[0].radius==45,"field fields");
 const auto& s=w.state[2];const auto& gun=w.units[2];double release=w.time+std::max(0.0,windup(w,2)-s.prep)/s.timeRate;
 check(o.casts.size()==1&&o.casts[0].target==w.units[1].id&&o.casts[0].gun==gun.id&&o.casts[0].releaseAt==release&&o.casts[0].landingAt==release+distance(w.units[1].pos,gun.pos)/((s.lobSpeed>0?s.lobSpeed:300)*s.launch),"cast fields");
 const auto frozen=o.shells[0].at;w.shells[0].at=9;check(o.shells[0].at==frozen,"immutable snapshot ownership");
 sh.source=w.reference(0);w.shells.push_back(sh);shot.source=w.reference(0);w.shots.push_back(shot);w.fields.push_back({{400,400},45,0,9,0});
 auto invalid=sh;invalid.source={999,1};w.shells.push_back(invalid);shot.aimed=false;shot.source=w.reference(2);w.shots.push_back(shot);
 o=react_v1::observe(w,0);check(o.shells.size()==1&&o.shots.size()==1&&o.fields.size()==1,"enemy-only resolved aimed boundary");
 w.units[2].alive=false;o=react_v1::observe(w,0);check(o.casts.empty()&&o.shells.size()==1,"retained dead projectile source, dead cast excluded");
}
void reactCases(){auto w=fixture();parity(w);w.units[2].target=w.reference(0);parity(w);w.state[2].prep=0;
 Shell sh;sh.source=w.reference(2);sh.pos={400,400};sh.at=1.6;sh.splash=40;w.shells.push_back(sh);parity(w);
 sh.pos={425,435};w.shells.push_back(sh);parity(w);w.shells.back().slow=true;parity(w);
 for(int x=0;x<20;++x)for(int y=0;y<8;++y){w.units[0].pos={10.+x*21,10.+y*65};w.shells[0].pos=w.units[0].pos;w.shells[0].at=1.01+x*.07;parity(w);}
 w.shells.clear();w.units[0].pos={400,400};w.fields.push_back({{400,400},45,0,2,1});parity(w);w.fields[0].until=1.49;parity(w);w.fields.clear();
 Shot shot;shot.source=w.reference(2);shot.pos={380,400};shot.direction={1,0};shot.speed=240;shot.left=100;
 for(double born:{.5,.879,.881,1.0}){shot.born=born;w.shots={shot};parity(w);}
 w.state[0].guardUntil=2;parity(w);w.state[0].guardUntil=0;
 auto meleeUnit=w.add(0,Role::Melee,{585,400});w.units[meleeUnit.slot].target=w.reference(2);w.state[meleeUnit.slot].standoff=0;w.rebuildTeams();parity(w);
 w.units[meleeUnit.slot].pos={400,400};parity(w);
}
control::ControllerParams theta(){auto v=js::parse(std::string(std::istreambuf_iterator<char>(std::cin),{}));control::ControllerParams p;
 for(auto k:js::keys(js::get(v,"selected_params")))p[js::str(k)]=js::num(js::get(js::get(v,"selected_params"),k));return p;}
void bind(World& w,const control::ControllerParams& p,bool shadow=false){w.controllers[0]=std::make_unique<react_v1::Controller>(73,0,p,control::V7Selector::Gate);dynamic_cast<react_v1::Controller*>(w.controllers[0].get())->shadow(shadow);}
void tick(World& w){react_v1::prepare(w);prepareControllers(w);react_v1::shadows(w);for(auto i:w.active)if(w.units[i].team==0)react_v1::decide(w,i);react_v1::constrainPrep(w);}
std::string bytes(const World& w){std::ostringstream s;s<<std::setprecision(17)<<w.time<<' '<<w.random.state<<' '<<w.spawnRandom.state<<' '<<w.nextShot;
 for(auto i:w.active){const auto& u=w.units[i];const auto& a=w.state[i];const auto& d=a.decision;
  s<<' '<<u.id<<' '<<u.pos.x<<' '<<u.pos.y<<' '<<u.hp<<' '<<u.cooldown<<' '<<u.target.slot<<' '<<u.target.generation<<' '<<a.prep<<' '<<a.energy<<' '<<a.inReach<<' '<<a.castOk<<' '<<d.goal.x<<' '<<d.goal.y<<' '<<d.multiplier<<' '<<d.stop<<' '<<int(d.release)<<' '<<d.move<<' '<<d.keep<<' '<<d.post<<' '<<d.bound;
  const auto& t=w.tactical[i];s<<' '<<a.castTime<<' '<<a.guardUntil<<' '<<a.slot.x<<' '<<a.slot.y<<' '<<a.damageDealt<<' '<<a.damageTaken<<' '<<t.assigned.slot<<' '<<t.assigned.generation<<' '<<int(t.order.kind)<<' '<<t.order.until<<' '<<t.reservedUntil<<' '<<t.fireHold<<' '<<t.waitFrom;}
 for(const auto& sh:w.shells)s<<' '<<sh.pos.x<<' '<<sh.pos.y<<' '<<sh.source.slot<<' '<<sh.source.generation<<' '<<sh.at<<' '<<sh.born<<' '<<sh.splash<<' '<<sh.damage<<' '<<sh.slow;
 for(const auto& sh:w.shots)s<<' '<<sh.pos.x<<' '<<sh.pos.y<<' '<<sh.direction.x<<' '<<sh.direction.y<<' '<<sh.born<<' '<<sh.left;
 for(const auto& f:w.fields)s<<' '<<f.pos.x<<' '<<f.pos.y<<' '<<f.radius<<' '<<f.from<<' '<<f.until;
 auto* c=dynamic_cast<const react_v1::Controller*>(w.controllers[0].get());s<<' '<<c->studentRandomState();for(const auto& kv:c->complexStates())s<<' '<<kv.first<<' '<<kv.second.real()<<' '<<kv.second.imag();
 for(const auto& kv:c->memory()){const auto& m=kv.second;s<<' '<<kv.first<<' '<<m.state<<' '<<m.zOut<<' '<<m.zIn<<' '<<m.lastOut<<' '<<m.lastIn<<' '<<m.target<<' '<<m.zInAnswered<<' '<<m.zInUnanswered<<' '<<m.hadLegalTarget<<' '<<m.hadUnansweredThreat;}
 for(const auto& kv:c->pairModes())s<<' '<<kv.first.first<<' '<<kv.first.second<<' '<<kv.second;
 for(const auto& kv:c->pairHolds())s<<' '<<kv.first.first<<' '<<kv.first.second<<' '<<kv.second.started<<' '<<kv.second.until;
 for(const auto& kv:c->modes())s<<' '<<kv.first<<' '<<kv.second;
 for(const auto& kv:c->argMemory())s<<' '<<kv.first<<' '<<kv.second.arg<<' '<<kv.second.time<<' '<<kv.second.valid;
 return s.str();}
void arbitration(const control::ControllerParams& p){auto w=fixture();bind(w,p);w.state[2].prep=0;Shell sh;sh.source=w.reference(2);sh.pos={400,400};sh.at=2.2;sh.splash=40;w.shells.push_back(sh);tick(w);
 auto* c=dynamic_cast<react_v1::Controller*>(w.controllers[0].get());const auto id=w.units[0].id;
 check(c->records().at(id).winner=="react"&&w.state[0].decision.release==Release::None&&!w.state[0].inReach&&!w.state[0].castOk,"reaction pauses release and preparation start");
 w.shells.clear();w.state[2].prep=0;w.time+=w.dt;tick(w);check(!c->records().at(id).active&&c->records().at(id).wasReacting&&w.state[0].decision.release==Release::Direct,"return after dodge");
 auto d=UnitDecision{0,400,1,0,w.units[2].id};auto corrected=react_v1::participate(c->snapshot().units,id,d);
 check(std::hypot(corrected.x-w.units[2].pos.x,corrected.y-w.units[2].pos.y)<=w.units[0].range+w.units[0].radius+w.units[2].radius+1e-10,"withdrawal stays in own reach");
 auto gun=w.add(0,Role::Artillery,{450,400});w.units[gun.slot].target=w.reference(2);w.state[gun.slot].prep=1;w.state[gun.slot].minRange=30;w.rebuildTeams();w.time+=w.dt;tick(w);
 react_v1::Command cmd;cmd.movement={450,400,0,0,w.units[2].id};cmd.hasAim=true;cmd.aim={610,420};cmd.fire=react_v1::FireIntent::Hold;cmd.volley=42;c->submit(w.units[gun.slot].id,cmd);react_v1::decide(w,gun.slot);react_v1::constrainPrep(w);
 check(w.state[gun.slot].decision.release==Release::None&&!c->records().at(w.units[gun.slot].id).ready&&c->command(w.units[gun.slot].id)->volley==42,"explicit hold and membership");
 cmd.fire=react_v1::FireIntent::Release;c->submit(w.units[gun.slot].id,cmd);react_v1::decide(w,gun.slot);check(w.state[gun.slot].decision.release==Release::Artillery&&c->records().at(w.units[gun.slot].id).ready,"explicit release recomputes readiness");
 auto point=react_v1::aimPoint(w,gun.slot,{0,0});check(same(point,cmd.aim),"explicit aim resolution");fireShellAt(w,gun.slot,point);check(same(w.shells.back().pos,cmd.aim),"shell explicit aim");
 auto bad=cmd;bad.aim.x=NAN;bool rejected=false;try{c->submit(w.units[gun.slot].id,bad);}catch(const std::invalid_argument&){rejected=true;}check(rejected,"nonfinite aim rejected");
 bad=cmd;bad.aim={w.config->width-w.units[gun.slot].radius,w.config->height-w.units[gun.slot].radius};check(distance(w.units[gun.slot].pos,bad.aim)>w.units[gun.slot].range,"far aim fixture is inside arena beyond gun range");rejected=false;try{c->submit(w.units[gun.slot].id,bad);}catch(const std::invalid_argument&){rejected=true;}check(rejected,"artillery aim beyond range rejected");
 bad=cmd;bad.aim={450,400};rejected=false;try{c->submit(w.units[gun.slot].id,bad);}catch(const std::invalid_argument&){rejected=true;}check(rejected,"artillery aim inside minRange rejected");
 bad=cmd;bad.movement.target=id;rejected=false;try{c->submit(w.units[gun.slot].id,bad);}catch(const std::invalid_argument&){rejected=true;}check(rejected,"friendly target rejected");
 bad=cmd;bad.movement.target=999;rejected=false;try{c->submit(w.units[gun.slot].id,bad);}catch(const std::invalid_argument&){rejected=true;}check(rejected,"missing target rejected");
 auto saved=w.units[gun.slot].pos;w.units[gun.slot].pos={100,100};check(!react_v1::aimReach(w,gun.slot),"artillery aim checked again after movement");w.units[gun.slot].pos=saved;
 cmd.volley=0;cmd.movement.target=w.units[2].id;c->submit(id,cmd);fireShot(w,0,w.reference(2));const auto direction=(cmd.aim-w.units[0].pos)*(1/distance(cmd.aim,w.units[0].pos));check(same(w.shots.back().direction,direction),"direct shot explicit aim");
 auto clone=c->clone();check(clone.get()!=c,"controller clone independent");
 w.units[2].alive=false;react_v1::decide(w,gun.slot);check(c->command(w.units[gun.slot].id)->movement.target==0&&!c->records().at(w.units[gun.slot].id).ready,"executed target and readiness reconciled after target dies");
}
void shadow(const control::ControllerParams& p){auto off=fixture();auto on=fixture();bind(off,p,false);bind(on,p,true);
 std::ostringstream trajectoryOff,trajectoryOn;bool sawReaction=false,sawReturn=false;
 for(int n=0;n<8;++n){for(auto* w:{&off,&on}){w->shells.clear();w->state[2].prep=0;if(n<4){Shell s;s.source=w->reference(2);s.pos={400,400};s.at=w->time+1.5;s.splash=40;w->shells.push_back(s);}
   tick(*w);for(auto i:w->active)if(w->units[i].team==0){const auto& d=w->state[i].decision;if(d.move)w->move(i,d.goal,w->dt*d.multiplier,d.stop);}w->time+=w->dt;}
  trajectoryOff<<bytes(off)<<'\n';trajectoryOn<<bytes(on)<<'\n';
  auto* c=dynamic_cast<react_v1::Controller*>(on.controllers[0].get());for(const auto& kv:c->records()){const auto& r=kv.second;sawReaction|=r.active;sawReturn|=r.wasReacting&&!r.active;check(r.active==r.teacher.active,"shadow activation parity");if(r.active)check(r.reactCandidate.movement.x==r.teacher.goal.x&&r.reactCandidate.movement.y==r.teacher.goal.y,"shadow goal parity");}
 }
 check(trajectoryOff.str()==trajectoryOn.str(),"byte-identical shadow on/off decision/movement trajectory");
 check(sawReaction&&sawReturn,"shadow fixture exercises active reaction and return");
 std::cout<<"{\"fixture\":\"shadow_identity\",\"ticks\":8,\"bytes\":"<<trajectoryOff.str().size()<<",\"identical\":true}\n";
}
}
int main(){try{auto p=theta();observation();reactCases();arbitration(p);shadow(p);std::cout<<"{\"status\":\"PASS\",\"assertions\":"<<checks<<",\"fights\":0}\n";return 0;}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}
