#include "artillery.h"
#include <numeric>

namespace astelia {
namespace {
constexpr double pi=3.14159265358979323846;
struct Coming {UnitRef gun;double at;};
std::vector<PlannedShot> assign(const World& w,const std::vector<UnitRef>& ready,const std::vector<Coming>& coming,const std::vector<PlannedShot>& points){auto free=ready;auto soon=coming;std::vector<PlannedShot> out;const bool game=w.config->rules==Rules::Game;
  for(auto p:points){size_t best=SIZE_MAX;double bd=INFINITY;
    if(p.at>w.time+1e-9&&game){for(size_t i=0;i<soon.size();++i){const double d=std::abs(soon[i].at-p.at);if(d<.35&&d<bd&&gunReach(w,soon[i].gun.slot,p.point)){bd=d;best=i;}}
      if(best!=SIZE_MAX){p.gun=soon[best].gun;p.at=soon[best].at;soon.erase(soon.begin()+best);out.push_back(p);}continue;}
    for(size_t i=0;i<free.size();++i){const auto* gun=w.resolve(free[i]);const double d=distance(gun->pos,p.point);if(d<bd&&gunReach(w,free[i].slot,p.point)){bd=d;best=i;}}
    if(best!=SIZE_MAX){p.gun=free[best];free.erase(free.begin()+best);out.push_back(p);}}
  return out;
}
std::vector<PredictedShell> shells(const World& w,uint8_t team,const std::vector<PlannedShot>& shots,double flight){std::vector<PredictedShell> out;out.reserve(shots.size());for(const auto& q:shots)out.push_back(shellOf(w,team,q,flight));return out;}
PlannedShot point(Vec2 p,double at,bool fin=false){PlannedShot q;q.point=p;q.at=at;q.finisher=fin;return q;}
std::vector<PlannedShot> ring(Vec2 center,uint32_t n,double from,double span,double radius,double at){std::vector<PlannedShot> out;out.reserve(n);for(uint32_t i=0;i<n;++i){const double a=from+span*(i+.5)/n;out.push_back(point(center+Vec2{std::cos(a),std::sin(a)}*radius,at));}return out;}
double ltd(const World& w,uint8_t team,bool end){double score=0;for(auto i:w.teams[team])if(w.units[i].alive){const auto& u=w.units[i];double hp=u.hp;if(end)for(const auto& sh:w.shells){const auto* src=w.resolve(sh.source);if(src&&!sh.slow&&sh.source!=w.reference(i)&&(sh.lob||src->team!=team)&&distance(u.pos,sh.pos)<=sh.splash+u.radius)hp-=sh.damage;}
  score+=std::sqrt(std::max(0.0,hp))*u.damage/(w.state[i].cooldownMax>0?w.state[i].cooldownMax:.4);}return score;}
double hp(const World& w,uint8_t team){double sum=0;for(auto i:w.teams[team])if(w.units[i].alive)sum+=std::max(0.0,w.units[i].hp)+100;return sum;}
}
const char* attackName(AttackFamily f){constexpr const char* names[]={"singles","focus","net","wall","herd","split","trap","sweep","battery","dashnet","left","own"};if(size_t(f)>=size_t(AttackFamily::Count))throw std::invalid_argument("invalid artillery family");return names[size_t(f)];}
AttackFamily attackByName(const std::string& name){for(size_t i=0;i<size_t(AttackFamily::Count);++i)if(name==attackName(AttackFamily(i)))return AttackFamily(i);throw std::invalid_argument("unknown artillery family: "+name);}
bool fireGate(World& w,uint32_t i){const auto& u=w.units[i];const auto& skill=w.config->skills[u.team];const auto* target=w.resolve(u.target);if(!target||!target->alive)return true;auto& p=w.packs[u.team];
  if(skill.holdWave>0&&u.role==Role::Artillery&&w.state[u.target.slot].player!=invalidSlot){const auto& player=w.players[w.state[u.target.slot].player];if(player.dashReady<=w.time&&w.state[u.target.slot].energy>=10){double first=INFINITY;
      for(auto j:w.teams[u.team])if(j!=i&&w.units[j].role==Role::Artillery&&w.state[j].prep>0&&w.units[j].target==u.target&&w.state[j].castTime>=0)first=std::min(first,w.state[j].castTime);
      if(w.time<first+skill.holdWave&&std::isfinite(first))return false;}}
  if(skill.holdSync>0&&u.role==Role::Artillery&&p.enabled){if(p.gateTime!=w.time){p.gateTime=w.time;p.gateUntil=0;uint32_t now=1,soon=0;double wait=0;
      for(auto j:w.teams[u.team])if(j!=i){const auto& gun=w.units[j];const auto& state=w.state[j];const auto* t=w.resolve(gun.target);if(gun.role!=Role::Artillery||state.prep>0||!state.inReach||!t||!t->alive)continue;
        if(gun.cooldown<=0)++now;else if(gun.cooldown<skill.holdSync){++soon;wait=std::max(wait,gun.cooldown);}}
      if(soon){const double splash=blastRadius(w,i);const auto net=[&](uint32_t n,double delay){std::vector<PredictedShell> planned;const double landing=w.time+delay+windup(w,i)+distance(u.pos,target->pos)/lobSpeed(w,i);
        for(uint32_t j=0;j<n;++j){const double a=n>1?j*2*pi/(n-1):0;planned.push_back({j?target->pos+Vec2{std::cos(a),std::sin(a)}*(splash*1.5):target->pos,landing,u.damage,splash,u.team});}return planned;};
        const double apart=smartVolley(w,u.team,net(now,0))+smartVolley(w,u.team,net(soon,wait));if(smartVolley(w,u.team,net(now+soon,wait))>apart*1.2+1e-9)p.gateUntil=w.time+wait;}}
    if(w.time<p.gateUntil)return false;}
  return true;
}
void launch(World& w,uint8_t team,const Attack& attack){auto& p=w.packs[team];for(size_t i=0;i<attack.shots.size();++i){auto q=attack.shots[i];const auto* gun=w.resolve(q.gun);if(!gun||!gun->alive)continue;
    q.family=attack.family;q.variant=attack.variant;if(i<attack.per.size()){q.prediction=attack.per[i];q.hasPrediction=true;}
    if(q.at<=w.time+1e-9){released(w,q.gun.slot);fireShellAt(w,q.gun.slot,q.point,q.prediction,q.hasPrediction,q.family,q.finisher,q.variant);}
    else{w.tactical[q.gun.slot].reservedUntil=q.at+.3;p.artilleryQueue.push_back(q);}}
  if(!attack.shots.empty())++w.stats.attacks[team][size_t(attack.family)*2].used;
  if(attack.family!=AttackFamily::Left){p.artilleryLast=attack.family;p.artilleryVariant=attack.variant;}
}
double artilleryOutcome(World& w,uint8_t me,const Attack& attack,const ArtilleryRollout& rollout){++w.work->artilleryRollouts;auto lease=w.branches().fork(w);auto& c=lease.world();c.duration=w.time+rollout.horizon;if(rollout.dt>0)c.dt=rollout.dt;
  if(!std::isfinite(c.duration)||c.duration/c.dt>1e7)throw std::invalid_argument("invalid artillery branch horizon");launch(c,me,attack);
  if(rollout.ltd2){const double ours=ltd(c,me,false),theirs=ltd(c,1-me,false);while(!c.done())coreStep(c);return (theirs-ltd(c,1-me,true))-(ours-ltd(c,me,true));}
  const double ours=hp(c,me),theirs=hp(c,1-me);while(!c.done())coreStep(c);double fly=0;for(const auto& sh:c.shells)if(!sh.slow){const auto* source=c.resolve(sh.source);if(source)fly+=(source->team==me?1:-1)*(sh.hasPrediction?sh.prediction:sh.damage*.76);}
  return (theirs-hp(c,1-me))-(ours-hp(c,me))+fly;
}
void artilleryVolley(World& w,uint8_t me){if(!w.config->skills[me].artyPlan)return;auto& p=w.packs[me];const bool game=w.config->rules==Rules::Game;const auto& skill=w.config->skills[me];const auto& enemies=w.teams[1-me];
  for(auto& q:p.artilleryQueue){const auto* gun=w.resolve(q.gun);if(!gun||!gun->alive)continue;const bool due=game?prepared(w,q.gun.slot):q.at<=w.time+1e-9;
    if(due){w.tactical[q.gun.slot].reservedUntil=0;if(game){released(w,q.gun.slot);if(gunReach(w,q.gun.slot,q.point))fireShellAt(w,q.gun.slot,q.point,q.prediction,q.hasPrediction,q.family,q.finisher,q.variant);q.at=-INFINITY;}
      else if(!busyUnit(w,q.gun.slot)&&prepared(w,q.gun.slot)){released(w,q.gun.slot);fireShellAt(w,q.gun.slot,q.point,q.prediction,q.hasPrediction,q.family,q.finisher,q.variant);}}}
  p.artilleryQueue.erase(std::remove_if(p.artilleryQueue.begin(),p.artilleryQueue.end(),[&](const PlannedShot& q){const auto* u=w.resolve(q.gun);return !u||!u->alive||(game?w.time>=q.at+.3:q.at<=w.time+1e-9);}),p.artilleryQueue.end());
  if(p.cutOffUntil<=w.time)p.cutOff.clear();std::vector<UnitRef> ready;std::vector<Coming> coming;
  for(auto i:w.teams[me])if(w.units[i].alive&&w.units[i].role==Role::Artillery&&!(w.tactical[i].reservedUntil>w.time)){if(prepared(w,i)&&!busyUnit(w,i))ready.push_back(w.reference(i));
    else if(game&&w.state[i].prep>0&&!prepared(w,i))coming.push_back({w.reference(i),w.time+(windup(w,i)-w.state[i].prep)/w.state[i].timeRate});}
  if(ready.empty()||enemies.empty())return;
  if(!game&&ready.size()<=p.artilleryReady&&w.time<p.artilleryNext){p.artilleryReady=uint32_t(ready.size());return;}p.artilleryNext=w.time+skill.artyEvery;
  const bool light=w.branch&&!(w.thinkTeams&(1<<me));const uint32_t n=uint32_t(ready.size()+coming.size());double flight=0,splash=0;
  for(auto ref:ready){flight+=.8*w.units[ref.slot].range/lobSpeed(w,ref.slot);splash+=blastRadius(w,ref.slot);}flight=game?flight/ready.size():w.config->roles[2].flight;splash=game?splash/ready.size():w.config->roles[2].splash;
  const auto led=[&](uint32_t i){return w.units[i].pos+leadVelocity(w,w.reference(i),me)*flight;};
  const auto singles=[&](){std::vector<PlannedShot> shots;for(auto ref:ready){const auto& gun=w.units[ref.slot];if(game){const auto* target=w.resolve(gun.target);if(target&&target->alive&&gunReach(w,ref.slot,target->pos)){auto q=point(target->pos,w.time);q.gun=ref;shots.push_back(q);}}
      else{const auto target=artilleryTarget(w,ref.slot);if(target){auto q=point(led(target.slot),w.time);q.gun=ref;shots.push_back(q);}}}return shots;};
  struct Cluster {double score;Vec2 point;};std::vector<Cluster> clusters;const double reach=game?2*splash:76*flight+splash;
  for(auto i:enemies)if(w.units[i].alive){const auto center=led(i);uint32_t guns=0,count=0;for(auto gun:ready)if(gunReach(w,gun.slot,center))++guns;if(!guns)continue;
    for(auto j:enemies)if(w.units[j].alive&&distance(w.units[j].pos,center)<reach)++count;clusters.push_back({double(count)*guns,center});}
  std::stable_sort(clusters.begin(),clusters.end(),[](const Cluster& a,const Cluster& b){return a.score>b.score;});std::vector<Attack> attacks;attacks.push_back({AttackFamily::Singles,0,singles(),{},0});
  const auto add=[&](AttackFamily family,std::vector<PlannedShot> points,uint16_t variant=0){attacks.push_back({family,variant,std::move(points),{},0});};
  if(!light){for(size_t k=0;k<enemies.size();++k)if(w.state[enemies[k]].player!=invalidSlot){PredictedShell dummy{{-1e6,-1e6},w.time+flight,0,0,me};const auto prediction=predictVolley(w,me,{dummy},w.time+flight);
      const auto center=prediction.hasSnapshot?prediction.snapshot[k].point:led(enemies[k]);clusters.insert(clusters.begin(),{1e9,center});if(n>=2){auto points=ring(center,n-1,0,2*pi,112,w.time);points.insert(points.begin(),point(center,w.time));add(AttackFamily::Dashnet,std::move(points));}break;}}
  for(size_t k=0;k<std::min(clusters.size(),size_t(light?1:3));++k){const auto center=clusters[k].point;auto delta=p.anchor-center;const double d=length(delta);const auto toward=delta*(1/(d>0?d:1));const double angle=std::atan2(toward.y,toward.x);
    std::vector<PlannedShot> focus;for(uint32_t i=0;i<n;++i)focus.push_back(point(center+Vec2{std::cos(i*2.4),std::sin(i*2.4)}*(splash*.3),w.time));add(AttackFamily::Focus,std::move(focus));
    if(n>=3){auto points=ring(center,n-1,angle,2*pi,splash*1.5,w.time);points.insert(points.begin(),point(center,w.time));add(AttackFamily::Net,std::move(points));}if(light)continue;
    const auto line=[&](Vec2 origin,Vec2 direction,double spacing,double delay){std::vector<PlannedShot> points;for(uint32_t i=0;i<n;++i)points.push_back(point(origin+direction*((double(i)-(n-1)/2.0)*splash*spacing),w.time+i*delay));return points;};
    if(n>=3){const Vec2 perpendicular{-toward.y,toward.x};add(AttackFamily::Wall,line(center+toward*(splash*.8),perpendicular,1.4,0));add(AttackFamily::Herd,line(center-toward*(splash*1.2),perpendicular,1.4,0));add(AttackFamily::Split,line(center,toward,1.4,0));}
    if(n>=4){uint16_t variant=0;for(double direction:{0.0,pi/2,pi,-pi/2})for(double delay:{.4,.8})for(double width:{1.22,.7}){const double gapAngle=angle+direction;auto points=ring(center,n-1,gapAngle+width/2,2*pi-width,splash*1.5,w.time);
        auto finisher=point(center+Vec2{std::cos(gapAngle),std::sin(gapAngle)}*(splash*2.6),w.time+delay,true);const auto prediction=predictVolley(w,me,shells(w,me,points,flight),w.time+delay+flight);
        if(prediction.hasSnapshot){Vec2 centroid;uint32_t count=0;for(size_t i=0;i<prediction.snapshot.size();++i){const auto& q=prediction.snapshot[i];if(q.hp>0&&distance(w.units[enemies[i]].pos,center)<reach&&distance(q.point,center)>splash*1.2&&std::cos(std::atan2(q.point.y-center.y,q.point.x-center.x)-gapAngle)>.5){centroid=centroid+q.point;++count;}}if(count)finisher.point=centroid*(1.0/count);}
        points.push_back(finisher);add(AttackFamily::Trap,std::move(points),variant++);}}
    if(n>=3){add(AttackFamily::Sweep,line(center,toward,1.2,.3));add(AttackFamily::Sweep,line(center,{-toward.y,toward.x},1.2,.3));}}
  if(!light&&skill.artyBattery){std::vector<uint32_t> guns;for(auto i:enemies)if(w.units[i].alive&&w.units[i].role==Role::Artillery&&std::any_of(ready.begin(),ready.end(),[&](UnitRef r){return gunReach(w,r.slot,w.units[i].pos);}))guns.push_back(i);
    std::stable_sort(guns.begin(),guns.end(),[&](uint32_t a,uint32_t b){return distance(w.units[a].pos,p.anchor)<distance(w.units[b].pos,p.anchor);});for(size_t k=0;k<std::min(size_t(2),guns.size());++k){const auto center=led(guns[k]);std::vector<PlannedShot> points;for(uint32_t i=0;i<n;++i)points.push_back(point(center+Vec2{std::cos(i*2.4),std::sin(i*2.4)}*(splash*.4),w.time));add(AttackFamily::Battery,std::move(points));}}
  const double herd=light?0:skill.artyHerd;std::vector<Attack> scored;size_t best=SIZE_MAX;double bv=-1;
  for(auto& attack:attacks){if(attack.family!=AttackFamily::Singles)attack.shots=assign(w,ready,coming,attack.shots);if(attack.shots.empty())continue;++w.work->artilleryCandidates;const auto planned=shells(w,me,attack.shots,flight);double end=-1;if(herd)for(const auto& sh:planned)end=std::max(end,sh.at);
    auto prediction=predictVolley(w,me,planned,end,light?.25:.1);const double greedy=std::accumulate(prediction.value.begin(),prediction.value.end(),0.0)-prediction.own;double score=light?greedy:(1-skill.artyRobust)*greedy+skill.artyRobust*smartVolley(w,me,planned);
    if(herd&&prediction.hasSnapshot)for(size_t i=0;i<prediction.snapshot.size();++i){const auto& q=prediction.snapshot[i];if(q.hp<=0)continue;uint32_t friends=0,zone=0;for(size_t j=0;j<prediction.snapshot.size();++j)if(j!=i&&prediction.snapshot[j].hp>0&&distance(q.point,prediction.snapshot[j].point)<80)++friends;
      for(auto m:w.teams[me])if(w.units[m].alive&&w.units[m].role!=Role::Artillery&&distance(w.units[m].pos,q.point)<=w.units[m].range+(melee(w.units[m].role)?40:0))++zone;
      score+=herd*threatWorth(w,enemies[i])*(double(zone)-friends);}
    attack.score=score;attack.per=std::move(prediction.per);if(score>bv){bv=score;best=scored.size();}scored.push_back(std::move(attack));}
  if(best==SIZE_MAX)return;
  const auto& rollout=skill.rollout;if(!light&&rollout.enabled&&n>=2&&scored.size()>1&&w.time>=p.rolloutNext){p.rolloutNext=w.time+rollout.every;
    std::vector<size_t> order(scored.size());std::iota(order.begin(),order.end(),0);std::stable_sort(order.begin(),order.end(),[&](size_t a,size_t b){return scored[a].score>scored[b].score;});std::vector<size_t> shortlist(order.begin(),order.begin()+std::min(size_t(rollout.top),order.size()));
    for(auto family:rollout.shape){const auto found=std::find_if(order.begin(),order.end(),[&](size_t i){return scored[i].family==family;});if(found!=order.end()&&std::find(shortlist.begin(),shortlist.end(),*found)==shortlist.end())shortlist.push_back(*found);}
    double outcome=-INFINITY;for(auto i:shortlist){const double value=artilleryOutcome(w,me,scored[i],rollout);if(value>outcome){outcome=value;best=i;}}}
  launch(w,me,scored[best]);if(!light&&skill.artyFollow){const auto planned=shells(w,me,scored[best].shots,flight);double end=-1;for(const auto& sh:planned)end=std::max(end,sh.at);const auto prediction=predictVolley(w,me,planned,end);p.cutOff.clear();
    if(prediction.hasSnapshot)for(size_t i=0;i<prediction.snapshot.size();++i){const auto& q=prediction.snapshot[i];if(q.hp<=0)continue;uint32_t friends=0;for(size_t j=0;j<prediction.snapshot.size();++j)if(j!=i&&prediction.snapshot[j].hp>0&&distance(q.point,prediction.snapshot[j].point)<80)++friends;if(friends<=1)p.cutOff.push_back(w.reference(enemies[i]));}p.cutOffUntil=end+2;}
  Attack left;left.family=AttackFamily::Left;for(auto q:singles())if(std::none_of(scored[best].shots.begin(),scored[best].shots.end(),[&](const PlannedShot& used){return used.gun==q.gun;}))left.shots.push_back(q);launch(w,me,left);
  p.artilleryReady=0;for(auto i:w.teams[me])if(w.units[i].alive&&w.units[i].role==Role::Artillery&&prepared(w,i)&&!busyUnit(w,i)&&!(w.tactical[i].reservedUntil>w.time))++p.artilleryReady;
}
} // namespace astelia
