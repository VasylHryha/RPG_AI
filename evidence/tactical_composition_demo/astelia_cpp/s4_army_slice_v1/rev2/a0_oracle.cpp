#include "a0_oracle.h"
#include "shapes.h"
#include "geometry.h"
#include "controller_bridge.h"
namespace army_a0 {
// Unit behavior is the read-only S4V7 public-history policy inside each Controller.
// Only the ready-set aim allocation below differs between O and O+G/T.
bool applyAim(World& w,react_v1::Controller& c,UnitId id,Vec2 point){
 auto cmd=*c.command(id);
 if(!shapes_v6::legalAim(c.snapshot().units,id,cmd.movement,point))return false;
 for(auto i:w.active)if(w.units[i].id==id){cmd.hasAim=true;cmd.aim=point;c.submit(id,cmd);react_v1::decide(w,i);return true;}
 throw std::logic_error("A0 aim unit missing");
}
void geometry(World& w){
 auto* c=dynamic_cast<react_v1::Controller*>(w.controllers[0].get());if(!c)return;
 shapes_v6::PlannerInput input;input.units=c->snapshot().units;
 unsigned eligible=0;
 for(auto i:w.active)if(w.units[i].team==0&&w.units[i].role==Role::Artillery){
  const auto& r=c->records().at(w.units[i].id);const auto* t=w.resolve(w.units[i].target);const auto& st=w.state[i];const auto* cmd=c->command(w.units[i].id);
  bool ok=prepared(w,i)&&st.inReach&&t&&t->alive&&cmd->fire!=react_v1::FireIntent::Hold&&!r.active&&r.winner!="guard"&&r.winner!="body_ability"&&r.winner!="failure";
  eligible+=ok;input.guns.push_back({w.units[i].id,t?t->id:0,windup(w,i),(st.lobSpeed>0?st.lobSpeed:300)*st.launch,blastRadius(w,i),ok});
 }
 for(const auto& sh:w.shells){const auto* src=w.resolve(sh.source);if(src&&!sh.slow&&sh.at>w.time)input.shells.push_back({sh.pos,sh.at,sh.damage,sh.splash,src->team});}
 if(!eligible)return;
 if(c->shape.arm=="T"||c->shape.arm=="O+G"){
  const auto begin=c->shape.audit.size();const auto arm=c->shape.arm;c->shape.arm="V2";shapes_v6::geometry(w);c->shape.arm=arm;
  unsigned applied=0,rejected=0;for(size_t i=begin;i<c->shape.audit.size();++i){const auto row=c->shape.audit[i];
   applied+=js::truth(js::get(row,"planner"));rejected+=js::truth(js::get(row,"plannerRejected"));}
  c->shape.audit.push_back(js::obj({{"a0Event",true},{"eligible",double(eligible)},{"joint",eligible>=2},{"applied",double(applied)},{"rejected",double(rejected)},{"changed",0},{"t",w.time}}));return;
 }
 const bool joint=false;
 std::vector<std::pair<UnitId,PlannedShot>> plan;
 for(const auto& gun:input.guns)if(gun.eligible){auto single=input;
   for(auto& g:single.guns)g.eligible=g.id==gun.id;
   auto model=shapes_v6::project(single);shapes_v6::copiedPlanner(model,0);
   for(const auto& q:model.packs[0].artilleryQueue)if(model.units[q.gun.slot].id==gun.id)plan.push_back({gun.id,q});
 }
 unsigned applied=0,rejected=0,changed=0;
 for(const auto& entry:plan){const auto id=entry.first;const auto& q=entry.second;
  for(auto i:w.active)if(w.units[i].id==id){auto cmd=*c->command(id);
   if(!applyAim(w,*c,id,q.point)){++rejected;continue;}
   ++applied;changed+=!cmd.hasAim||distance(cmd.aim,q.point)>1e-9;
   c->shape.audit.push_back(js::obj({{"planner",true},{"id",double(id)},{"t",w.time},{"family",attackName(q.family)},{"aim",js::arr({q.point.x,q.point.y})},{"expectedDamage",q.prediction},{"autonomous",true}}));
  }
 }
 c->shape.audit.push_back(js::obj({{"a0Event",true},{"eligible",double(eligible)},{"joint",joint},{"applied",double(applied)},{"rejected",double(rejected)},{"changed",double(changed)},{"t",w.time}}));
}
}
