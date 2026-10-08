#include "a0_oracle.h"
#include "shapes.h"
#include "geometry.h"
#include "controller_bridge.h"
namespace army_a0 {
UnitDecision base(const control::Observation& o,uint8_t side,UnitId id){
 const control::ObservedUnit* self=nullptr;for(const auto& u:o.units)if(u.id==id)self=&u;
 if(!self)throw std::invalid_argument("A0 missing unit");
 UnitDecision d{self->x,self->y,0,0,0};const control::ObservedUnit* best=nullptr;double bd=INFINITY;bool legal=false;
 for(const auto& t:o.units)if(t.team!=side&&t.hp>0){double gap=std::hypot(t.x-self->x,t.y-self->y);bool in=shapes_v6::reach(*self,t);
  if(!best||(in&&!legal)||(in==legal&&(gap<bd||(gap==bd&&t.id<best->id)))){best=&t;bd=gap;legal=in;}}
 if(!best)return d;d.target=best->id;
 const double preferred=self->role==ObservedRole::Melee?self->radius+best->radius:
  self->role==ObservedRole::Artillery?std::max(self->minRange,self->range-20):self->range+self->radius+best->radius-1;
 const double dx=self->x-best->x,dy=self->y-best->y,n=std::hypot(dx,dy);
 d.x=best->x+preferred*(n>0?dx/n:1);d.y=best->y+preferred*(n>0?dy/n:0);d.multiplier=std::abs(n-preferred)>1?1:0;return d;
}
// oracle() is generated from the P16 overlay block, with baseline calls replaced
// by base(). It contains no v6 dynamics or target memory.
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
 if(c->shape.arm=="T"){
  const auto begin=c->shape.audit.size();c->shape.arm="V2";shapes_v6::geometry(w);c->shape.arm="T";
  unsigned applied=0,rejected=0;for(size_t i=begin;i<c->shape.audit.size();++i){const auto row=c->shape.audit[i];
   applied+=js::truth(js::get(row,"planner"));rejected+=js::truth(js::get(row,"plannerRejected"));}
  c->shape.audit.push_back(js::obj({{"a0Event",true},{"eligible",double(eligible)},{"joint",eligible>=2},{"applied",double(applied)},{"rejected",double(rejected)},{"changed",0},{"t",w.time}}));return;
 }
 const bool joint=c->shape.arm=="O+G"&&eligible>=2;
 std::vector<std::pair<UnitId,PlannedShot>> plan;
 if(joint){auto model=shapes_v6::project(input);shapes_v6::copiedPlanner(model,0);
  for(const auto& q:model.packs[0].artilleryQueue)plan.push_back({model.units[q.gun.slot].id,q});
 }else{for(const auto& gun:input.guns)if(gun.eligible){auto single=input;
   for(auto& g:single.guns)g.eligible=g.id==gun.id;
   auto model=shapes_v6::project(single);shapes_v6::copiedPlanner(model,0);
   for(const auto& q:model.packs[0].artilleryQueue)if(model.units[q.gun.slot].id==gun.id)plan.push_back({gun.id,q});
 }}
 unsigned applied=0,rejected=0,changed=0;
 for(const auto& entry:plan){const auto id=entry.first;const auto& q=entry.second;
  for(auto i:w.active)if(w.units[i].id==id){auto cmd=*c->command(id);
   if(!applyAim(w,*c,id,q.point)){++rejected;continue;}
   ++applied;changed+=!cmd.hasAim||distance(cmd.aim,q.point)>1e-9;
  }
 }
 c->shape.audit.push_back(js::obj({{"a0Event",true},{"eligible",double(eligible)},{"joint",joint},{"applied",double(applied)},{"rejected",double(rejected)},{"changed",double(changed)},{"t",w.time}}));
}
}
