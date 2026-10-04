#include "formation.h"

namespace astelia {
namespace {
template<class Goal> const Goal* live(const World& w,const Goal& external,const Goal& internal){return external.until>w.time?&external:internal.until>w.time?&internal:nullptr;}
bool clump(const World& w,uint8_t team){const auto& ours=w.teams[team];const auto& es=w.foes(team);std::vector<uint32_t> guns;
  for(auto i:ours)if(w.units[i].alive&&w.units[i].role==Role::Artillery)guns.push_back(i);if(guns.size()<3)return false;
  const double sp=w.state[guns[0]].splash>0?w.state[guns[0]].splash:w.config->roles[2].splash;
  for(auto e:es){uint32_t count=0;for(auto h:es)if(distance(w.units[e].pos,w.units[h].pos)<sp)++count;if(count<4)continue;
    bool own=false,reach=false;for(auto i:ours)if(w.units[i].alive&&distance(w.units[i].pos,w.units[e].pos)<sp+50)own=true;
    for(auto i:guns){const double d=distance(w.units[i].pos,w.units[e].pos);if(d<=w.units[i].range&&d>=w.state[i].minRange)reach=true;}
    if(!own&&reach)return true;}return false;
}
double headDistance(const World& w,uint8_t team){double d=INFINITY;for(auto i:w.foes(team))if(melee(w.units[i].role))d=std::min(d,distance(w.units[i].pos,w.packs[team].anchor));return d;}
void goals(World& w,uint8_t team){auto& p=w.packs[team];auto& d=p.director;d.goals=PackGoals{};const double until=w.time+.7;
  const auto place=[&](Vec2 point){d.goals.place={point,d.observation.theirsCenter,until,true};};
  if(d.combo==ComboKind::Tchain){if(d.phase==0)place({clamp(p.anchor.x+d.away.x*200,100,w.config->width-100),clamp(p.anchor.y+d.away.y*200,100,w.config->height-100)});
    else if(d.phase==1){place(p.anchor);d.goals.plan.until=until;d.goals.plan.tactics.role.fill(Plan::Widehold);}
    else{d.goals.release.until=d.goals.engage.until=until;for(const auto& role:d.roles)if(role.role==0){const auto* u=w.resolve(role.unit);if(u&&u->alive)d.goals.release.ids.push_back(u->id);}
      std::vector<uint32_t> es;for(auto i:w.foes(team))if(melee(w.units[i].role))es.push_back(i);
      std::stable_sort(es.begin(),es.end(),[&](uint32_t a,uint32_t b){return distance(w.units[a].pos,p.anchor)<distance(w.units[b].pos,p.anchor);});
      for(size_t j=0;j<std::min(size_t(8),es.size());++j)d.goals.engage.ids.push_back(w.units[es[j]].id);}}
  else{if(d.phase==0){const auto delta=d.observation.oursCenter-d.observation.theirsCenter;const double l=length(delta);const auto point=p.anchor+delta*(50/(l>0?l:1));
      place({clamp(point.x,100,w.config->width-100),clamp(point.y,100,w.config->height-100)});}else place(p.anchor);}
}
}
const GoalPlace* placeGoal(const World& w,uint8_t team){const auto& p=w.packs[team];return live(w,p.commands.place,p.director.goals.place);}
const GoalPlan* planGoal(const World& w,uint8_t team){const auto& p=w.packs[team];return live(w,p.commands.plan,p.director.goals.plan);}
const GoalIds* engageGoal(const World& w,uint8_t team){const auto& p=w.packs[team];return live(w,p.commands.engage,p.director.goals.engage);}
const GoalIds* releaseGoal(const World& w,uint8_t team){const auto& p=w.packs[team];return live(w,p.commands.release,p.director.goals.release);}
bool containsId(const GoalIds* goal,UnitId id){return goal&&std::find(goal->ids.begin(),goal->ids.end(),id)!=goal->ids.end();}
Observation observe(const World& w,uint8_t team){Observation o;const auto& ours=w.teams[team];const auto& es=w.foes(team);Vec2 velocity;double sxx=0,syy=0,sxy=0;uint32_t meleeCount=0,chasing=0;
  for(auto i:ours){const auto& u=w.units[i];if(!u.alive)continue;++o.ours;o.hpOurs+=u.hp;o.oursCenter=o.oursCenter+u.pos;if(size_t(u.role)<3)++o.oursByRole[size_t(u.role)];}
  for(auto i:es){const auto& u=w.units[i];++o.theirs;o.hpTheirs+=u.hp;o.theirsCenter=o.theirsCenter+u.pos;if(size_t(u.role)<3)++o.theirsByRole[size_t(u.role)];}
  o.oursCenter=o.oursCenter*(1.0/std::max(1u,o.ours));o.theirsCenter=o.theirsCenter*(1.0/std::max(1u,o.theirs));
  for(auto i:ours)if(w.units[i].alive)for(auto j:es)o.gapNear=std::min(o.gapNear,distance(w.units[i].pos,w.units[j].pos));
  for(auto i:es){const auto& e=w.units[i];const auto delta=e.pos-o.theirsCenter;sxx+=delta.x*delta.x;syy+=delta.y*delta.y;sxy+=delta.x*delta.y;velocity=velocity+e.velocity;o.spread+=length(delta);
    if(melee(e.role)){++meleeCount;const auto toward=o.oursCenter-e.pos;const double l=length(toward);if(dot(e.velocity,toward)/(l>0?l:1)>20)++chasing;}}
  const double n=std::max(1u,o.theirs),th=.5*std::atan2(2*sxy,sxx-syy),tr=(sxx+syy)/n,det=(sxx*syy-sxy*sxy)/(n*n),v=std::sqrt(std::max(0.0,tr*tr/4-det));
  o.axis={std::cos(th),std::sin(th)};o.columnRatio=std::sqrt((tr/2+v)/std::max(1.0,tr/2-v));o.speedAlong=dot(velocity*(1/n),o.axis);o.spread/=n;
  o.centers=length(o.oursCenter-o.theirsCenter);if(!(o.centers>0))o.centers=1;o.approach=dot(velocity*(1/n),o.oursCenter-o.theirsCenter)/o.centers;
  o.chaseShare=meleeCount?double(chasing)/meleeCount:0;o.wallDist=std::min({o.oursCenter.x,w.config->width-o.oursCenter.x,o.oursCenter.y,w.config->height-o.oursCenter.y});
  o.finishing=o.theirs>0&&(o.theirs<=2||o.ours>=4*o.theirs);return o;
}
void directorStep(World& w,uint8_t team){if(!w.config->skills[team].combosEnabled||w.branch)return;auto& p=w.packs[team];auto& d=p.director;
  if(w.time-d.last<.5-1e-9)return;d.last=w.time;d.observation=observe(w,team);const auto& o=d.observation;
  const auto stop=[&](bool success){d.cool[size_t(d.combo)]=w.time+(d.combo==ComboKind::Tchain?8:6);d.active=false;d.goals={};if(success)++d.successes;else ++d.aborts;d.log.push_back({w.time,d.combo,d.phase,uint8_t(success?2:3)});};
  if(d.active){d.roles.erase(std::remove_if(d.roles.begin(),d.roles.end(),[&](const ComboRole& r){const auto* u=w.resolve(r.unit);return !u||!u->alive;}),d.roles.end());
    const double dwell=w.time-d.phaseStart,min=d.combo==ComboKind::Tchain?(d.phase==0?1.5:d.phase==1?1:2):(d.phase==0?1:2),max=d.combo==ComboKind::Tchain?(d.phase==1?6:8):5;
    if(d.roles.empty()||(d.combo==ComboKind::Tchain&&d.phase==0&&dwell>=min&&(o.wallDist<110||o.theirs<3))||dwell>max){stop(false);return;}
    const bool done=d.combo==ComboKind::Tchain?(d.phase==0?headDistance(w,team)<300||o.columnRatio>1.25*d.ratio0:d.phase==1?headDistance(w,team)<130||dwell>4:o.theirsByRole[0]==0||dwell>6):(d.phase==0?clump(w,team):dwell>3);
    if(dwell>=min&&done){if(d.phase==(d.combo==ComboKind::Tchain?2:1)){stop(d.combo==ComboKind::Tchain?o.theirsByRole[0]<=.5*d.startEnemies:int64_t(o.theirs)<=int64_t(d.startEnemies)-3);return;}
      ++d.phase;d.phaseStart=w.time;++d.switches;d.log.push_back({w.time,d.combo,d.phase,1});}goals(w,team);return;}
  if(w.time-d.selected<2-1e-9)return;d.selected=w.time;
  for(auto combo:w.config->skills[team].combos){if(d.cool[size_t(combo)]>w.time||o.finishing)continue;bool eligible=false;
    if(combo==ComboKind::Tchain){const auto delta=o.oursCenter-o.theirsCenter;const double l=length(delta);const auto away=delta*(1/(l>0?l:1)),end=o.oursCenter+away*300;
      eligible=o.theirsByRole[0]>=6&&o.oursByRole[1]>=10&&o.columnRatio>=2.2&&o.approach>=15&&o.chaseShare>=.5&&o.gapNear>=250&&o.gapNear<=700&&end.x>=100&&end.x<=w.config->width-100&&end.y>=100&&end.y<=w.config->height-100;
      if(eligible){d.away=away;d.ratio0=o.columnRatio;d.startEnemies=o.theirsByRole[0];}}
    else if(o.oursByRole[0]>=6&&o.theirsByRole[0]>=6){uint32_t contact=0;for(auto e:w.foes(team))if(melee(w.units[e].role)){bool near=false;for(auto i:w.teams[team])if(w.units[i].role==Role::Melee&&gap(w.units[i],w.units[e])<30)near=true;contact+=near;}
      eligible=contact>=5&&clump(w,team);if(eligible)d.startEnemies=o.theirs;}
    if(!eligible)continue;d.combo=combo;d.phase=0;d.start=d.phaseStart=w.time;d.active=true;d.roles.clear();
    if(combo==ComboKind::Tchain){std::vector<uint32_t> shooters;for(auto i:w.teams[team])if(w.units[i].role==Role::Ranged)shooters.push_back(i);
      const auto lateral=[&](uint32_t i){const auto delta=w.units[i].pos-o.theirsCenter;return std::abs(-delta.x*o.axis.y+delta.y*o.axis.x);};
      std::stable_sort(shooters.begin(),shooters.end(),[&](uint32_t a,uint32_t b){return lateral(a)>lateral(b);});for(size_t j=0;j<shooters.size();++j)d.roles.push_back({w.reference(shooters[j]),uint8_t(j<shooters.size()/2?0:1)});
      for(auto i:w.teams[team])if(w.units[i].role==Role::Melee)d.roles.push_back({w.reference(i),2});}
    else for(auto i:w.teams[team])if(w.units[i].role==Role::Melee||w.units[i].role==Role::Artillery)d.roles.push_back({w.reference(i),uint8_t(w.units[i].role==Role::Artillery?3:4)});
    ++d.starts;d.log.push_back({w.time,combo,0,0});goals(w,team);break;}
}
void issueOrder(World& w,UnitRef unit,const UnitOrder& order){auto* u=w.resolve(unit);if(!u||!u->alive)throw std::invalid_argument("order unit is unavailable");
  if(!std::isfinite(order.until)||!std::isfinite(order.point.x)||!std::isfinite(order.point.y)||!(order.radius>0)||!std::isfinite(order.radius))throw std::invalid_argument("invalid unit order");
  if(order.kind==OrderKind::Attack){const auto* target=w.resolve(order.target);if(!target||!target->alive||target->team==u->team)throw std::invalid_argument("invalid attack target");}
  w.tactical[unit.slot].order=order;
}
} // namespace astelia
