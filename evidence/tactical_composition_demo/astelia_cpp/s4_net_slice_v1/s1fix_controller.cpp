// Script-only public reference oracle. Existing Host action/lifecycle gates stay intact.
#include "s1fix_script.h"
#include "public_mechanics.h"
#include <algorithm>
#include <tuple>
#include <cmath>
namespace s1_script {
using namespace astelia;using js::V;
std::map<UnitId,Provenance> plannerSources;Provenance selectedSource;
std::map<UnitId,Command> commands;bool wrapper=false;
void reset(bool b){wrapper=b;commands.clear();plannerSources.clear();selectedSource={};}
namespace {
double n(V v,const char* k){return js::num(js::get(v,k));}
V self(V s){for(auto u:js::get(s,"units").p->items)if(n(u,"id")==n(s,"self"))return u;throw std::logic_error("self");}
V target(V s,UnitId id){for(auto u:js::get(s,"units").p->items)if(n(u,"id")==id&&n(u,"team")!=n(s,"side")&&n(u,"hp")>0)return u;return {};}
Vec2 pos(V u){return {n(u,"x"),n(u,"y")};}
// The public snapshot helper is inserted by s1_build.py from the unchanged teacher.cpp.
PUBLIC_VIEW_HELPER
V retained(V s){auto me=self(s);auto th=js::get(s,"threats").p->items;
 auto urgency=[&](V q){auto k=js::str(js::get(q,"kind"));int kind=k=="shell"?0:k=="shot"?1:k=="field"?2:k=="cast"?3:4;
 double at=(kind==0||kind==4)?n(q,"at"):kind==3?n(q,"landing_at"):kind==2?std::max(n(s,"t"),n(q,"from")):n(s,"t")+std::max(0.,(n(me,"x")-n(q,"x"))*n(q,"dx")+(n(me,"y")-n(q,"y"))*n(q,"dy"))/std::max(n(q,"speed"),1e-6);
 return std::make_tuple(distance(pos(me),pos(q))>n(q,"radius")+n(me,"radius")+4,std::max(0.,at-n(s,"t")),kind,n(q,"ordinal"));};
 std::sort(th.begin(),th.end(),[&](V a,V b){return urgency(a)<urgency(b);});if(th.size()>8)th.resize(8);
 V out=js::obj({});for(auto key:js::keys(s))js::set(out,js::str(key),js::get(s,js::str(key)));js::set(out,"threats",js::arr(std::move(th)));return out;}
std::pair<Vec2,double> intercept(V me,V focus){double lob=n(me,"lob");if(!(lob>0)||!std::isfinite(lob))throw std::runtime_error("invalid lob");double tau=distance(pos(me),pos(focus))/lob;Vec2 velocity{n(focus,"vx"),n(focus,"vy")};for(int i=0;i<3;++i)tau=distance(pos(me),pos(focus)+velocity*tau)/lob;auto q=pos(focus)+velocity*tau;double residual=length(velocity)*std::abs(distance(pos(me),q)/lob-tau);if(!std::isfinite(q.x)||!std::isfinite(q.y)||!std::isfinite(residual))throw std::runtime_error("nonfinite intercept");return {q,residual};}
// Autonomous single-shot request is projected into physical support BEFORE
// categorical sampling. Retain raw lead/projection distance as diagnostics.
Vec2 legalLead(V s,V focus){auto me=self(s);auto q=intercept(me,focus).first;
 q.x=clamp(q.x,0,n(s,"width"));q.y=clamp(q.y,0,n(s,"height"));auto delta=q-pos(me);double d=length(delta);
 if(d>n(me,"range"))q=pos(me)+delta*((n(me,"range")-1e-7)/d);
 if(distance(q,pos(me))<n(me,"min_range"))q=pos(focus);
 return q;}
struct Support{Vec2 aim;bool legal=false,centerLegal=false;unsigned index=0,count=0;double error=0,residual=0,radius=0;};
// Prospective S1FIX support: exact desired centre plus local splash rings.
// No request-dependent polar grid about the enemy: that rotated group shapes.
Support support(V s,V focus,Vec2 requested,bool present){auto me=self(s);auto lead=intercept(me,focus);Support o;o.residual=lead.second;o.radius=n(me,"splash");if(!present)requested=legalLead(s,focus);
 if(!std::isfinite(requested.x)||!std::isfinite(requested.y))throw std::runtime_error("nonfinite command");
 double best=INFINITY;
 for(unsigned i=0;i<32;++i){Vec2 p=requested;if(i){double angle=((i-1)%16)*std::acos(-1)/8,f=i<=16?.5:1;p=p+Vec2{n(s,"side")?-std::cos(angle):std::cos(angle),std::sin(angle)}*(o.radius*f);}double d=distance(pos(me),p);bool legal=p.x>=0&&p.x<=n(s,"width")&&p.y>=0&&p.y<=n(s,"height")&&d>=n(me,"min_range")&&d<=n(me,"range");if(!i)o.centerLegal=legal;if(!legal)continue;++o.count;double error=distance(p,requested);if(error<best){o.legal=true;o.index=i;o.aim=p;o.error=error;best=error;}}
 // The last candidate is a living-focus fallback, ensuring a legal autonomous
 // action when lead leaves reach. Its original snap error is still measured.
 Vec2 p=pos(focus);double d=distance(pos(me),p);if(p.x>=0&&p.x<=n(s,"width")&&p.y>=0&&p.y<=n(s,"height")&&d>=n(me,"min_range")&&d<=n(me,"range")){++o.count;double error=distance(p,requested);if(error<best){o.legal=true;o.index=32;o.aim=p;o.error=error;}}
 return o;}
net_slice::Intent unit(V s,UnitId focus=0,Vec2 request={},bool present=false){using namespace net_slice;validate(s);auto me=self(s);auto enc=encode(s);UnitId id=UnitId(n(s,"self"));V enemy;
 if(focus)enemy=target(s,focus);else if(n(me,"prep")>0)enemy=target(s,UnitId(n(me,"target")));else if(!enc.enemies.empty())enemy=target(s,enc.enemies[0]);
 auto o=view(retained(s));auto reaction=net_public::react(o,id);Vec2 goal=pos(me);
 Intent c;c.target=focus;if(enemy.tag!=V::Undefined){c.target=UnitId(n(enemy,"id"));auto found=std::find(enc.enemies.begin(),enc.enemies.end(),c.target);if(found==enc.enemies.end())throw std::runtime_error("unsupported focus");c.targetIndex=unsigned(found-enc.enemies.begin()+1);auto a=support(s,enemy,request,present);c.hasAim=a.legal;c.aim=a.aim;c.aimIndex=a.index;auto delta=pos(enemy)-pos(me);double d=length(delta),wanted=std::clamp(d,n(me,"min_range")+1,n(me,"range")-1);if(d>0)goal=goal+delta*((d-wanted)/d);
 bool body=n(me,"guard_until")>n(s,"t")||js::truth(js::get(me,"busy")),reach=d>=n(me,"min_range")&&d<=n(me,"range");c.startOpportunity=!body&&reach&&a.legal&&n(me,"prep")<=0&&n(me,"cooldown")<=0&&n(me,"energy")>=n(me,"cost");c.releaseOpportunity=!body&&reach&&a.legal&&n(me,"prep")>0&&n(me,"prep")+n(s,"dt")*n(me,"time_rate")>=n(me,"windup")-1e-9;c.start=c.startOpportunity&&!reaction.active;c.release=c.releaseOpportunity&&!reaction.active;}
 if(reaction.active)goal=reaction.goal;auto p=net_public::participate(o.units,id,{goal.x,goal.y,1,0,c.target});goal={p.x,p.y};double best=INFINITY;
 for(unsigned i=0;i<33;++i){Vec2 q=pos(me);if(i){double angle=((i-1)%16)*std::acos(-1)/8,f=i<=16?.6:1;q=q+Vec2{n(s,"side")?-std::cos(angle):std::cos(angle),std::sin(angle)}*(n(me,"speed")*f);q.x=clamp(q.x,n(me,"radius"),n(s,"width")-n(me,"radius"));q.y=clamp(q.y,n(me,"radius"),n(s,"height")-n(me,"radius"));}double d=distance(q,goal);if(d<best){best=d;c.goal=q;c.moveIndex=i;}}
 c.multiplier=c.moveIndex!=0;return c;}
V vec(Vec2 p){return js::arr({p.x,p.y});}
}
}
namespace s1_script {
net_public::Snapshot publicView(V s){return view(s);}
net_slice::Intent autonomous(V s,UnitId locked){return unit(s,locked);}
bool reacting(V s){return net_public::react(view(retained(s)),UnitId(n(s,"self"))).active;}
}
namespace net_slice {
void Host::prepare(const astelia::control::Observation&){using namespace s1_script;using namespace astelia;
 const bool decision=(tick-1)%6==0||cache.empty();
 std::map<UnitId,js::V> wires;std::map<UnitId,Intent> base,next;std::vector<UnitId> ids;std::vector<Vec2> positions;std::vector<double> speeds;
 for(auto s:views){auto id=UnitId(n(s,"self"));wires[id]=s;ids.push_back(id);positions.push_back(pos(self(s)));speeds.push_back(n(self(s),"speed"));base[id]=unit(s,casts[id].pending?casts[id].lockedTarget:0);}
 for(auto it=commands.begin();it!=commands.end();)if(!wires.count(it->first)||(!casts[it->first].pending&&n(self(wires.at(it->first)),"prep")<=0))it=commands.erase(it);else ++it;
 if(decision){
  slice_teacher::PlannerInput input;if(!views.empty())input.units=view(views[0]).units;
  unsigned eligible=0;
  for(auto p:base){auto s=wires.at(p.first),me=self(s);bool startable=p.second.start&&!casts[p.first].pending;eligible+=startable;input.guns.push_back({p.first,p.second.target,n(me,"windup"),n(me,"lob"),n(me,"splash"),startable});}
  if(!views.empty())for(auto th:js::get(views[0],"threats").p->items){auto k=js::str(js::get(th,"kind"));if((k=="shell"||k=="own_shell")&&!js::truth(js::get(th,"slow"))&&n(th,"at")>n(views[0],"t"))input.shells.push_back({pos(th),n(th,"at"),n(th,"damage"),n(th,"radius"),uint8_t(k=="own_shell"?0:1)});}
  unsigned group=0,changedAssignments=0;std::map<UnitId,Command> proposed;plannerSources.clear();
  if(wrapper&&eligible>=2){auto model=slice_teacher::project(input);slice_teacher::copiedPlanner(model,0);
   for(auto q:model.packs[0].artilleryQueue){auto id=model.units[q.gun.slot].id;if(q.family==AttackFamily::Singles||q.family==AttackFamily::Left)continue;++group;
    if(q.at>model.time+1e-9)throw std::runtime_error("delayed candidate in immediate slate");
    if(!plannerSources.count(id)||!wires.count(id))throw std::runtime_error("missing focus provenance");
    auto provenance=plannerSources.at(id);auto s=wires.at(id);auto t=target(s,provenance.focus);
    if(t.tag==js::V::Undefined){collector.record(tick,id,"s1_rejection",js::obj({{"reason","invalid_focus"}}));continue;}
    // Preserve the copied planner's gun-bound point exactly at assignment.
    auto requested=q.point;auto c=unit(s,provenance.focus,requested,true);auto a=support(s,t,requested,true);
    if(!c.start||!a.centerLegal){collector.record(tick,id,"s1_rejection",js::obj({{"reason","focus_assignment_infeasible"}}));continue;}
    proposed[id]={provenance.focus,q.point-provenance.center,requested,n(s,"t")+3,false,tick};
    if(c.target!=base.at(id).target||distance(c.aim,base.at(id).aim)>n(self(s),"splash")/4)++changedAssignments;
    collector.record(tick,id,"s1_candidate",js::obj({{"focus",double(provenance.focus)},{"planner_point",vec(q.point)},{"requested",vec(requested)},{"planner_center",vec(provenance.center)},{"shape",vec(q.point-provenance.center)},{"family",double(uint8_t(q.family))},{"variant",double(q.variant)}}));
   }
  }
  bool accepted=group>=2&&proposed.size()==group;
  if(accepted)for(auto p:proposed)commands[p.first]=p.second;
  else if(group)collector.record(tick,ids[0],"s1_rejection",js::obj({{"reason","whole_plan_infeasible"}}));
  collector.record(tick,ids.empty()?0:ids[0],"s1_joint",js::obj({{"eligible",double(eligible)},{"feasible",double(accepted?group:0)},{"changed_assignment",accepted&&changedAssignments>0}}));
 }
 for(auto p:base){auto id=p.first;auto s=wires.at(id),me=self(s);auto& cast=casts[id];Intent c=p.second;bool applied=false;std::string reason="empty";
  auto it=commands.find(id);
  if(it!=commands.end()){
   auto& command=it->second;auto t=target(s,command.focus);
   if(n(s,"t")>command.expiry)reason="expired";
   else if(t.tag==js::V::Undefined)reason="dead_focus";
   else if(cast.pending&&cast.lockedTarget!=command.focus)reason="late_focus_lock";
   else if(cast.aimLocked)reason="already_aim_locked";
   else{
    applied=true;
    // Refresh at the first physical opportunity, before decide() locks aim,
    // even when reaction suppresses release. Never wait for six-tick readout.
    if(!command.refreshed&&cast.pending&&p.second.releaseOpportunity){auto lead=intercept(me,t);command.absolute=lead.first+command.shape;command.refreshed=true;
     collector.record(tick,id,"s1_refresh",js::obj({{"focus",double(command.focus)},{"requested",vec(command.absolute)},{"autonomous",vec(lead.first)},{"autonomous_snapped",vec(support(s,t,lead.first,false).aim)},{"self",vec(pos(me))},{"t",n(s,"t")},{"lob",n(me,"lob")},{"splash",n(me,"splash")},{"shape",vec(command.shape)},{"residual",lead.second},{"plan",double(command.plan)}}),command.plan,tick,cast.started);
    }
    auto a=support(s,t,command.absolute,true);
    if(!a.centerLegal){applied=false;reason="command_point_illegal";}
    else{c=unit(s,command.focus,command.absolute,true);c.volley=command.plan;}
   }
   if(!applied&&reason!="already_aim_locked"){collector.record(tick,id,"s1_rejection",js::obj({{"reason",reason}}));commands.erase(it);}
  }
  // Cast authority, including dead-focus identity, precedes raw logging.
  // Aim is frozen after the native lifecycle lock; no resnapping while held.
  if(cast.pending){c.target=cast.lockedTarget;if(cast.aimLocked){c.aim=cast.lockedAim;c.hasAim=true;c.volley=cast.originVolley;}}
  if(!decision&&cache.count(id)){auto held=cache.at(id);c.goal=held.goal;c.moveIndex=held.moveIndex;c.multiplier=held.multiplier;c.stop=held.stop;
   if(!cast.pending){c=held;}}
  auto t=target(s,c.target);
  if(t.tag!=js::V::Undefined&&c.releaseOpportunity&&!cast.aimLocked){auto lead=intercept(me,t);auto a=support(s,t,applied?commands.at(id).absolute:lead.first,applied);
   collector.record(tick,id,"s1_support",js::obj({{"forced",a.count<=1},{"legal_count",double(a.count)},{"center_illegal",!a.centerLegal},{"snap_error",a.error},{"raw_lead",vec(lead.first)},{"autonomous_bound",vec(legalLead(s,t))},{"autonomous_bound_error",distance(lead.first,legalLead(s,t))},{"residual",a.residual},{"splash",n(me,"splash")},{"requested",vec(applied?commands.at(id).absolute:legalLead(s,t))},{"snapped",vec(c.aim)},{"bounded",vec(applied?commands.at(id).absolute:legalLead(s,t))},{"commanded",applied}}));
  }
  if(decision)collector.record(tick,id,"s1_autonomous_shadow",json(p.second),0,tick,cast.started);
  next[id]=c;
 }
 if(decision){Law law;law.J=0;auto drift=motion(std::vector<double>(ids.size(),0),positions,ids,law,speeds,"intact");lastDrift=drift;
  for(size_t i=0;i<ids.size();++i){auto id=ids[i];auto& c=next.at(id);c.goal=c.goal+drift[i];if(length(drift[i])>1e-12)c.multiplier=1;auto delta=c.goal-positions[i];double d=length(delta);if(d>speeds[i]&&d>0)c.goal=positions[i]+delta*(speeds[i]/d);c.goal.x=clamp(c.goal.x,0,n(wires.at(id),"width"));c.goal.y=clamp(c.goal.y,0,n(wires.at(id),"height"));phases[id]=0;decisionTicks[id]=tick;assignments[id]=c.target;collector.record(tick,id,"snapshot",wires.at(id));collector.record(tick,id,"intent",json(c),c.volley,tick);}
 }
 for(auto p:next)raw[p.first]=cache[p.first]=p.second;
}
}
