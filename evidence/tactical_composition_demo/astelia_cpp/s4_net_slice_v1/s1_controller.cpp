// Script-only public reference oracle. Existing Host action/lifecycle gates stay intact.
#include "s1_script.h"
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
struct Support{Vec2 aim;bool legal=false,centerLegal=false;unsigned index=0,count=0;double error=0,residual=0,radius=0;};
Support support(V s,V focus,Vec2 requested,bool present){auto me=self(s);auto lead=intercept(me,focus);Support o;o.residual=lead.second;o.radius=std::min(std::hypot(n(s,"width"),n(s,"height")),std::max({n(me,"splash"),distance(lead.first,pos(focus)),present?distance(requested,pos(focus)):0.}));if(!present)requested=lead.first;double best=INFINITY;
 for(unsigned i=0;i<33;++i){Vec2 p=pos(focus);if(i){double angle=((i-1)%16)*std::acos(-1)/8,f=i<=16?.5:1;p=p+Vec2{n(s,"side")?-std::cos(angle):std::cos(angle),std::sin(angle)}*(o.radius*f);}double d=distance(pos(me),p);bool legal=p.x>=0&&p.x<=n(s,"width")&&p.y>=0&&p.y<=n(s,"height")&&d>=n(me,"min_range")&&d<=n(me,"range");if(!i)o.centerLegal=legal;if(!legal)continue;++o.count;double error=distance(p,requested);if(error<best){o.legal=true;o.index=i;o.aim=p;o.error=error;best=error;}}
 return o;}
net_slice::Intent unit(V s,UnitId focus=0,Vec2 request={},bool present=false){using namespace net_slice;validate(s);auto me=self(s);auto enc=encode(s);UnitId id=UnitId(n(s,"self"));V enemy;
 if(focus)enemy=target(s,focus);else if(n(me,"prep")>0)enemy=target(s,UnitId(n(me,"target")));else if(!enc.enemies.empty())enemy=target(s,enc.enemies[0]);
 auto o=view(retained(s));auto reaction=net_public::react(o,id);Vec2 goal=pos(me);
 Intent c;if(enemy.tag!=V::Undefined){c.target=UnitId(n(enemy,"id"));auto found=std::find(enc.enemies.begin(),enc.enemies.end(),c.target);if(found==enc.enemies.end())throw std::runtime_error("unsupported focus");c.targetIndex=unsigned(found-enc.enemies.begin()+1);auto a=support(s,enemy,request,present);c.hasAim=a.legal;c.aim=a.aim;c.aimIndex=a.index;auto delta=pos(enemy)-pos(me);double d=length(delta),wanted=std::clamp(d,n(me,"min_range")+1,n(me,"range")-1);if(d>0)goal=goal+delta*((d-wanted)/d);
 bool body=n(me,"guard_until")>n(s,"t")||js::truth(js::get(me,"busy")),reach=d>=n(me,"min_range")&&d<=n(me,"range");c.startOpportunity=!body&&reach&&a.legal&&n(me,"prep")<=0&&n(me,"cooldown")<=0&&n(me,"energy")>=n(me,"cost");c.releaseOpportunity=!body&&reach&&a.legal&&n(me,"prep")>0&&n(me,"prep")+n(s,"dt")*n(me,"time_rate")>=n(me,"windup")-1e-9;c.start=c.startOpportunity&&!reaction.active;c.release=c.releaseOpportunity&&!reaction.active;}
 if(reaction.active)goal=reaction.goal;auto p=net_public::participate(o.units,id,{goal.x,goal.y,1,0,c.target});goal={p.x,p.y};double best=INFINITY;
 for(unsigned i=0;i<33;++i){Vec2 q=pos(me);if(i){double angle=((i-1)%16)*std::acos(-1)/8,f=i<=16?.6:1;q=q+Vec2{n(s,"side")?-std::cos(angle):std::cos(angle),std::sin(angle)}*(n(me,"speed")*f);q.x=clamp(q.x,n(me,"radius"),n(s,"width")-n(me,"radius"));q.y=clamp(q.y,n(me,"radius"),n(s,"height")-n(me,"radius"));}double d=distance(q,goal);if(d<best){best=d;c.goal=q;c.moveIndex=i;}}
 c.multiplier=c.moveIndex!=0;return c;}
V vec(Vec2 p){return js::arr({p.x,p.y});}
}
}
namespace net_slice {
void Host::prepare(const astelia::control::Observation&){using namespace s1_script;using namespace astelia;
 if((tick-1)%6!=0)return;
 std::map<UnitId,js::V> wires;std::map<UnitId,Intent> base,next;std::vector<UnitId> ids;std::vector<Vec2> positions;std::vector<double> speeds;
 for(auto s:views){auto id=UnitId(n(s,"self"));wires[id]=s;ids.push_back(id);positions.push_back(pos(self(s)));speeds.push_back(n(self(s),"speed"));base[id]=unit(s);}
 for(auto it=commands.begin();it!=commands.end();)if(!wires.count(it->first)||(!casts[it->first].pending&&n(self(wires.at(it->first)),"prep")<=0))it=commands.erase(it);else ++it;
 slice_teacher::PlannerInput input;
 if(!views.empty())input.units=view(views[0]).units;
 unsigned eligible=0;
 for(auto p:base){auto s=wires.at(p.first),me=self(s);bool startable=p.second.start&&!casts[p.first].pending;eligible+=startable;input.guns.push_back({p.first,p.second.target,n(me,"windup"),n(me,"lob"),n(me,"splash"),startable});}
 if(!views.empty())for(auto th:js::get(views[0],"threats").p->items){auto k=js::str(js::get(th,"kind"));if((k=="shell"||k=="own_shell")&&!js::truth(js::get(th,"slow"))&&n(th,"at")>n(views[0],"t"))input.shells.push_back({pos(th),n(th,"at"),n(th,"damage"),n(th,"radius"),uint8_t(k=="own_shell"?0:1)});}
 unsigned feasible=0,changedAssignments=0;std::map<UnitId,Command> proposed;plannerSources.clear();
 if(wrapper&&eligible>=2){auto model=slice_teacher::project(input);slice_teacher::copiedPlanner(model,0);for(auto q:model.packs[0].artilleryQueue){auto id=model.units[q.gun.slot].id;if(q.family==AttackFamily::Singles||q.family==AttackFamily::Left)continue;if(q.at>model.time+1e-9){collector.record(tick,id,"s1_rejection",js::obj({{"reason","delayed_planner_entry"}}));continue;}if(!plannerSources.count(id)||!wires.count(id))throw std::runtime_error("missing focus provenance");auto provenance=plannerSources.at(id);auto s=wires.at(id);auto t=target(s,provenance.focus);if(t.tag==js::V::Undefined){collector.record(tick,id,"s1_rejection",js::obj({{"reason","invalid_focus"}}));continue;}
  auto requested=intercept(self(s),t).first+(q.point-provenance.center);auto c=unit(s,provenance.focus,requested,true);if(!c.start){collector.record(tick,id,"s1_rejection",js::obj({{"reason","focus_assignment_infeasible"}}));continue;}proposed[id]={provenance.focus,q.point-provenance.center,requested,n(s,"t")+3,false,tick};++feasible;if(c.target!=base.at(id).target||distance(c.aim,base.at(id).aim)>n(self(s),"splash")/4)++changedAssignments;
  collector.record(tick,id,"s1_candidate",js::obj({{"focus",double(provenance.focus)},{"planner_point",vec(q.point)},{"planner_center",vec(provenance.center)},{"shape",vec(q.point-provenance.center)},{"family",double(uint8_t(q.family))},{"variant",double(q.variant)}}));}}
 if(feasible>=2)for(auto p:proposed)commands[p.first]=p.second;
 collector.record(tick,ids.empty()?0:ids[0],"s1_joint",js::obj({{"eligible",double(eligible)},{"feasible",double(feasible>=2?feasible:0)},{"changed_assignment",feasible>=2&&changedAssignments>0}}));
 for(auto p:base){auto id=p.first;auto s=wires.at(id),me=self(s);Intent c=p.second;bool applied=false;std::string reason="empty";auto it=commands.find(id);
  if(it!=commands.end()){auto& command=it->second;auto t=target(s,command.focus);reason="present";
   if(n(s,"t")>command.expiry)reason="expired";
   else if(t.tag==js::V::Undefined)reason="dead_focus";
   else if(casts[id].pending&&casts[id].lockedTarget!=command.focus)reason="late_focus_lock";
   else {applied=true;if(!command.refreshed){auto provisional=unit(s,command.focus,command.absolute,true);if(provisional.releaseOpportunity){if(casts[id].aimLocked){applied=false;reason="already_aim_locked";}else{auto lead=intercept(me,t);command.absolute=lead.first+command.shape;command.refreshed=true;collector.record(tick,id,"s1_refresh",js::obj({{"focus",double(command.focus)},{"requested",vec(command.absolute)},{"autonomous",vec(lead.first)},{"autonomous_snapped",vec(support(s,t,lead.first,false).aim)},{"self",vec(pos(me))},{"t",n(s,"t")},{"lob",n(me,"lob")},{"splash",n(me,"splash")},{"shape",vec(command.shape)},{"residual",lead.second},{"plan",double(command.plan)}}),command.plan,tick,casts[id].started);}}}
    if(applied){c=unit(s,command.focus,command.absolute,true);c.volley=command.plan;}}
   if(!applied)collector.record(tick,id,"s1_rejection",js::obj({{"reason",reason}}));}
  auto t=target(s,c.target);if(t.tag!=js::V::Undefined&&c.releaseOpportunity&&!casts[id].aimLocked){auto lead=intercept(me,t);auto a=support(s,t,applied?commands.at(id).absolute:lead.first,applied);collector.record(tick,id,"s1_support",js::obj({{"forced",a.count<=1},{"legal_count",double(a.count)},{"center_illegal",!a.centerLegal},{"snap_error",a.error},{"residual",a.residual},{"splash",n(me,"splash")},{"requested",vec(applied?commands.at(id).absolute:lead.first)},{"snapped",vec(c.aim)},{"bounded",vec(applied?commands.at(id).absolute:lead.first)}}));}
  next[id]=c;
 }
 // Shared J=0, A=B=.5, share=.125 movement; single categorical decision.
 Law law;law.J=0;auto drift=motion(std::vector<double>(ids.size(),0),positions,ids,law,speeds,"intact");lastDrift=drift;
 for(size_t i=0;i<ids.size();++i){auto id=ids[i];auto& c=next.at(id);c.goal=c.goal+drift[i];if(length(drift[i])>1e-12)c.multiplier=1;auto delta=c.goal-positions[i];double d=length(delta);if(d>speeds[i]&&d>0)c.goal=positions[i]+delta*(speeds[i]/d);c.goal.x=clamp(c.goal.x,0,n(wires.at(id),"width"));c.goal.y=clamp(c.goal.y,0,n(wires.at(id),"height"));phases[id]=0;raw[id]=cache[id]=c;decisionTicks[id]=tick;assignments[id]=c.target;collector.record(tick,id,"snapshot",wires.at(id));collector.record(tick,id,"intent",json(c),c.volley,tick);}
}
}
