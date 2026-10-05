#include "artillery.h"

namespace astelia {
namespace {
constexpr double pi=3.14159265358979323846;
struct Unit {Vec2 point,velocity,goal,dash;double radius=0,speed=0,hp=0,worth=0,protection=0,dashReady=0,dashUntil=0,energy=0;bool locked=false,player=false,hasGoal=false;};
bool escape(Vec2 point,double radius,double speed,uint8_t team,const std::vector<PredictedShell>& shells,double now,Vec2& goal){const PredictedShell* best=nullptr;double bt=INFINITY,bd=0;
  for(const auto& sh:shells){if(sh.team==team)continue;const double d=distance(point,sh.point),need=sh.splash+radius+4-d,left=sh.at-now;
    if(need>0&&left>0&&speed>0&&need/speed<left+.1&&left<bt){bt=left;best=&sh;bd=d;}}
  if(!best)return false;goal=bd<.5?point+Vec2{30,0}:point+(point-best->point)*(40/bd);return true;}
void move(Unit& u,Vec2 target,double dt){const auto delta=target-u.point;const double d=length(delta),step=std::min(u.speed*dt,d);if(d>0)u.point=u.point+delta*(step/d);}
bool locked(const World& w,uint32_t i){const auto& u=w.units[i];const auto* target=w.resolve(u.target);return melee(u.role)&&target&&target->alive&&gap(u,*target)<=u.range;}
}
bool busyUnit(const World& w,uint32_t i){const auto a=w.state[i].ability;if(a==invalidSlot)return false;const auto& ab=w.abilities[a];return ab.chargeEnd>w.time||ab.aimUntil>w.time||ab.disengageEnd>w.time;}
bool gunReach(const World& w,uint32_t i,Vec2 point){const double d=distance(w.units[i].pos,point);return d<=w.units[i].range&&d>=w.state[i].minRange;}
double lobSpeed(const World& w,uint32_t i){const auto& s=w.state[i];return (s.lobSpeed>0?s.lobSpeed:300)*(s.launch>0?s.launch:1);}
double blastRadius(const World& w,uint32_t i){return w.state[i].splash>0?w.state[i].splash:w.config->roles[2].splash;}
double threatWorth(const World& w,uint32_t i){const auto& u=w.units[i];return u.damage/(w.state[i].cooldownMax>0?w.state[i].cooldownMax:.4)/u.maxhp;}
PredictedShell shellOf(const World& w,uint8_t team,const PlannedShot& q,double flight){const auto* gun=w.resolve(q.gun);const bool game=w.config->rules==Rules::Game;
  return {q.point,q.at+(game?(gun?distance(gun->pos,q.point)/lobSpeed(w,q.gun.slot):flight):w.config->roles[2].flight),gun?gun->damage:w.config->roles[2].damage,game&&gun?blastRadius(w,q.gun.slot):w.config->roles[2].splash,team};}
Prediction predictVolley(const World& w,uint8_t me,const std::vector<PredictedShell>& planned,double snapTime,double dt){++w.work->artilleryPredictions;Prediction result;result.per.resize(planned.size());result.value.resize(planned.size());if(planned.empty())return result;
  if(!(dt>0)||!std::isfinite(dt))throw std::invalid_argument("invalid prediction step");const uint8_t them=1-me;const auto& skills=w.config->skills[me];const bool exact=skills.artyExact,dodges=w.packs[them].enabled?shellDodge(w,them):w.config->skills[them].dodgeShells;
  const bool smart=exact&&dodges&&w.config->skills[them].smartShells,lockedDodge=exact&&w.config->skills[them].lockedDodge;std::vector<Unit> enemies;enemies.reserve(w.teams[them].size());
  for(auto i:w.teams[them])if(w.units[i].alive){const auto& u=w.units[i];const auto& s=w.state[i];Unit e;e.point=u.pos;e.velocity=u.smoothVelocity;e.radius=u.radius;e.speed=u.speed;e.hp=u.hp;e.worth=threatWorth(w,i);e.protection=exact&&w.config->rules==Rules::Game?s.protection:0;e.locked=!lockedDodge&&locked(w,i);e.player=s.player!=invalidSlot;e.energy=s.energy;
    if(e.player){const auto& p=w.players[s.player];e.dashReady=p.dashReady;e.dashUntil=p.dashUntil;e.dash=p.dashDirection;}enemies.push_back(e);}
  std::vector<PredictedShell> shells;for(const auto& sh:w.shells){const auto* src=w.resolve(sh.source);if(src&&src->team!=them&&!sh.slow&&sh.at>w.time)shells.push_back({sh.pos,sh.at,sh.damage,sh.splash,src->team});}shells.insert(shells.end(),planned.begin(),planned.end());
  if(smart)for(auto& e:enemies){const auto cover=[&](Vec2 point){uint32_t count=0;for(const auto& sh:shells)if(distance(point,sh.point)<=sh.splash+e.radius+4)++count;return count;};
    double first=INFINITY;for(const auto& sh:shells)if(distance(e.point,sh.point)<=sh.splash+e.radius+4)first=std::min(first,sh.at);if(!std::isfinite(first)||e.locked)continue;
    const double extent=std::max(8.0,e.speed*(first-w.time+.1));uint32_t best=cover(e.point);double bd=0;
    for(double factor:{1.0,.6})for(int i=0;i<16;++i){const double a=i*pi/8;const auto point=e.point+Vec2{std::cos(a),std::sin(a)}*(extent*factor);const auto k=cover(point);const double d=extent*factor;
      if(k<best||(k==best&&e.hasGoal&&d<bd)){best=k;bd=d;e.goal=point;e.hasGoal=true;}}}
  const auto& ownSkills=w.config->skills[me];const bool ownDodge=ownSkills.dodgeShells||ownSkills.smartShells||ownSkills.planShells;
  if(exact&&skills.artyOwn)for(const auto& sh:planned)for(auto i:w.teams[me])if(w.units[i].alive){const auto& u=w.units[i];const double need=sh.splash+u.radius+4-distance(u.pos,sh.point);
    if(need>0&&(!ownDodge||(!ownSkills.lockedDodge&&locked(w,i))||u.speed<=0||need/u.speed>=sh.at-w.time+.1))result.own+=std::min(sh.damage,u.hp)*threatWorth(w,i);}
  std::vector<uint32_t> order;for(uint32_t i=0;i<planned.size();++i)order.push_back(i);std::stable_sort(order.begin(),order.end(),[&](uint32_t a,uint32_t b){return planned[a].at<planned[b].at;});
  const double end=planned[order.back()].at;if(!std::isfinite(end)||(end-w.time)/dt>1e7)throw std::invalid_argument("invalid prediction horizon");size_t k=0;double time=w.time;
  while(k<order.size()){++w.work->predictionSteps;const double next=std::max(time,std::min(time+dt,end));if(next==time&&planned[order[k]].at>time+1e-9)throw std::overflow_error("prediction time cannot advance");
    for(auto& e:enemies){++w.work->predictionUnitSteps;if(e.hp<=0||e.locked)continue;if(e.player){if(time>=e.dashUntil&&time>=e.dashReady&&e.energy>=10){const PredictedShell* threat=nullptr;for(const auto& sh:shells)if(sh.at>time&&sh.at-time<.45&&distance(e.point,sh.point)<=sh.splash+e.radius)threat=&sh;
          if(threat){const auto delta=e.point-threat->point;const double d=length(delta);e.dash=delta*(1/(d>0?d:1));e.dashUntil=time+.45;e.dashReady=time+.3;e.energy-=10;}}
        if(time<e.dashUntil)e.point=e.point+e.dash*((112/.45)*(std::min(next,e.dashUntil)-time));else e.point=e.point+e.velocity*(next-time);continue;}
      if(smart){if(e.hasGoal)move(e,e.goal,next-time);else e.point=e.point+e.velocity*(next-time);continue;}Vec2 goal;if(dodges&&escape(e.point,e.radius,e.speed,them,shells,time,goal))move(e,goal,next-time);else e.point=e.point+e.velocity*(next-time);}
    time=next;if(snapTime>=0&&!result.hasSnapshot&&time>=snapTime-1e-9){result.hasSnapshot=true;for(const auto& e:enemies)result.snapshot.push_back({e.point,e.hp});}
    while(k<order.size()&&planned[order[k]].at<=time+1e-9){const auto i=order[k++];const auto& sh=planned[i];for(auto& e:enemies)if(e.hp>0&&distance(e.point,sh.point)<=sh.splash+e.radius){const double damage=std::min(e.protection>0?std::floor(sh.damage*(1-e.protection)):sh.damage,e.hp);result.per[i]+=damage;e.hp-=damage;result.value[i]+=damage*e.worth+(e.hp<=0?.3*e.worth*100:0);}}
    if(time>=end)break;}
  return result;
}
double smartVolley(const World& w,uint8_t me,const std::vector<PredictedShell>& planned){if(planned.empty())return 0;double score=0,first=INFINITY;for(const auto& sh:planned)first=std::min(first,sh.at);const double damage=planned[0].damage,splash=planned[0].splash;
  for(auto i:w.teams[1-me])if(w.units[i].alive){const auto& u=w.units[i];const double radius=(splash+u.radius)*(splash+u.radius);const auto cover=[&](Vec2 point){uint32_t k=0;for(const auto& sh:planned){const auto d=point-sh.point;if(dot(d,d)<=radius)++k;}return k;};
    uint32_t least=cover(u.pos);if(!least)continue;const double extent=locked(w,i)?0:u.speed*(first-w.time)*.9;for(int d=0;d<16&&least&&extent>0;++d){const double a=d*pi/8;least=std::min(least,cover(u.pos+Vec2{std::cos(a),std::sin(a)}*extent));}
    const double dealt=std::min(u.hp,least*damage);score+=dealt*threatWorth(w,i)+(dealt>=u.hp?.3*threatWorth(w,i)*100:0);}
  return score;
}
} // namespace astelia
