#include "formation.h"

namespace astelia {
namespace {
bool finishing(uint32_t ours,uint32_t theirs){return theirs>0&&(theirs<=2||ours>=4*theirs);}
struct Read {
  uint32_t ours=0,theirs=0,ourMelee=0,ourShoot=0,ourArt=0,theirMelee=0,theirShoot=0,theirArt=0,soft=0,raiders=0;
  double approach=0,recentTaken=0;
  bool exposed=false,canReach=false;
};
Read read(const World& w,uint8_t team){Read r;const auto& p=w.packs[team];const auto& ms=w.teams[team];const auto& es=w.foes(team);Vec2 center,velocity;bool allPinned=true;
  for(auto i:ms){const auto& m=w.units[i];if(!m.alive)continue;++r.ours;if(m.role==Role::Melee)++r.ourMelee;if(m.role==Role::Ranged)++r.ourShoot;if(m.role==Role::Artillery)++r.ourArt;}
  for(auto i:es){const auto& e=w.units[i];++r.theirs;center=center+e.pos;velocity=velocity+e.velocity;
    if(melee(e.role)){++r.theirMelee;if(!pinned(w,i))allPinned=false;
      bool raiding=false,held=false;
      for(auto j:ms){const auto& m=w.units[j];if(!m.alive)continue;const double d=distance(e.pos,m.pos);
        if(!melee(m.role)&&d<260&&(dot(e.velocity,m.pos-e.pos)/(d>0?d:1)>25||d<120))raiding=true;
        if(m.role==Role::Melee&&gap(m,e)<24)held=true;}
      if(raiding&&!held)++r.raiders;
    }else ++r.soft;
    if(e.role==Role::Ranged||e.role==Role::Archer)++r.theirShoot;if(e.role==Role::Artillery)++r.theirArt;
    for(auto j:ms)if(w.units[j].alive&&w.units[j].role!=Role::Melee&&distance(e.pos,w.units[j].pos)<=w.units[j].range)r.canReach=true;
  }
  const double n=std::max(1u,r.theirs);center=center*(1/n);velocity=velocity*(1/n);const auto delta=p.anchor-center;const double d=length(delta);
  r.approach=dot(velocity,delta)/(d>0?d:1);r.exposed=r.soft>=4&&allPinned;
  for(const auto& hit:w.hitLog)if(hit.to==team)r.recentTaken+=hit.amount;return r;
}
Plan gamePack(World& w,uint8_t team,const Read& r){
  auto& p=w.packs[team];if(!p.startCount)p.startCount=r.ours;const bool severe=r.ours*2<p.startCount;
  bool backline=false;for(auto j:w.teams[team])if(w.units[j].alive&&!melee(w.units[j].role))for(auto i:w.foes(team))if(distance(w.units[j].pos,w.units[i].pos)<=96)backline=true;
  Plan mode=severe?Plan::Withdraw:r.theirs&&!backline&&r.ours>=std::max(1u,r.theirs)?Plan::Pressure:Plan::Defend;
  std::array<std::vector<uint8_t>,3> hit;for(auto& x:hit)x.resize(w.units.size());
  for(auto i:w.foes(team))if(melee(w.units[i].role)){const auto& e=w.units[i];uint32_t best=invalidSlot;double bd=INFINITY;
    for(auto j:w.teams[team])if(w.units[j].alive){const double d=distance(e.pos,w.units[j].pos);if(d<bd){bd=d;best=j;}}
    if(best!=invalidSlot&&bd<e.speed+e.range+w.units[best].radius&&dot(e.velocity,w.units[best].pos-e.pos)>0)hit[0][best]=1;}
  for(const auto& shot:w.shots){const auto* src=w.resolve(shot.source);if(!src||src->team==team||!shot.aimed)continue;
    for(auto j:w.teams[team])if(w.units[j].alive){const auto delta=w.units[j].pos-shot.pos;const double along=dot(delta,shot.direction);
      if(along>0&&along<shot.speed&&std::abs(delta.x*shot.direction.y-delta.y*shot.direction.x)<=w.units[j].radius)hit[1][j]=1;}}
  for(const auto& sh:w.shells){const auto* src=w.resolve(sh.source);if(!src||src->team==team||sh.at-w.time>=1)continue;
    for(auto j:w.teams[team])if(w.units[j].alive&&distance(w.units[j].pos,sh.pos)<=sh.splash+w.units[j].radius)hit[2][j]=1;}
  std::array<uint32_t,3> counts{};for(size_t k=0;k<3;++k)for(auto h:hit[k])counts[k]+=h;const int families=int(counts[0]>0)+int(counts[1]>0)+int(counts[2]>0);
  Plan response=Plan::None;const double own=std::max(1u,r.ours);
  if(families>1||counts[0])response=Plan::Defend;else if(counts[1])response=counts[1]/own>=.6?Plan::Defend:Plan::Loose;
  else if(counts[2])response=counts[2]/own>=.6?Plan::Defend:counts[2]/own>=.25?Plan::Dispersed:Plan::Loose;
  p.responseCount=response==p.responseSeen?p.responseCount+1:1;p.responseSeen=response;
  if(response!=Plan::None&&p.responseCount>=2)p.response=response;else if(response==Plan::None&&p.responseCount>=3)p.response=Plan::None;
  if(!severe&&p.response!=Plan::None)mode=p.response;
  p.wantCount=mode==p.wantMode?p.wantCount+1:1;p.wantMode=mode;
  const bool go=p.plan==Plan::None||(mode==Plan::Withdraw&&p.plan!=Plan::Withdraw)||
    (p.plan==Plan::Withdraw?p.wantCount>=3:w.time-p.planSince>=1&&p.wantCount>=2);
  return go?mode:p.plan;
}
} // namespace
void commander(World& w,uint8_t team){
  auto& p=w.packs[team];const auto brain=w.brains[team];if(!p.enabled||brain==Brain::Formation||brain==Brain::Alone)return;
  if(w.time-p.lastThink<(w.config->rules==Rules::Game?.2:.5))return;p.lastThink=w.time;
  const auto r=read(w,team);if(brain==Brain::Gamepack){const auto plan=gamePack(w,team,r);if(plan!=p.plan){Tactics combo;combo.role.fill(plan);setPlan(w,team,combo);}return;}
  auto& features=p.read;features.present=true;features.raiders=r.raiders;features.exposed=r.exposed;
  Vec2 center,softCenter,velocity;uint32_t soft=0;const auto& es=w.foes(team);
  for(auto i:es){const auto& e=w.units[i];center=center+e.pos;velocity=velocity+e.velocity;if(!melee(e.role)){softCenter=softCenter+e.pos;++soft;}}
  const double n=std::max(size_t(1),es.size());center=center*(1/n);velocity=velocity*(1/n);softCenter=soft?softCenter*(1.0/soft):center;
  double spread=0;features.meleeCharging=features.fastShooters=0;for(auto i:es){const auto& e=w.units[i];spread+=distance(e.pos,center);
    const auto delta=p.anchor-e.pos;const double d=length(delta),closing=dot(e.velocity,delta)/(d>0?d:1);
    const auto toward=p.anchor-softCenter;const double td=length(toward),ahead=dot(e.pos-softCenter,toward)/(td>0?td:1);
    if(melee(e.role)&&!pinned(w,i)&&ahead>100&&d<450&&closing>20)++features.meleeCharging;
    if((e.role==Role::Ranged||e.role==Role::Archer)&&d<450&&closing>50)++features.fastShooters;}
  const auto delta=p.anchor-center;const double d=length(delta),approach=dot(velocity,delta)/(d>0?d:1);
  features.formedEnemy=spread/n<170&&std::abs(approach)<35;features.quiet=w.time-std::max(0.0,w.lastHit);features.room=p.facing.x>=0?p.anchor.x-140:w.config->width-140-p.anchor.x;
  Plan plan=Plan::Hold;
  if(p.caught)p.fastSeen=w.time;if(p.wings.empty()&&p.flankStarted)p.raidSpent=true;

  const auto enabled=[&](Plan candidate){const auto& off=w.config->disabledPlans[team];return std::find(off.begin(),off.end(),candidate)==off.end();};
  if(brain==Brain::Storm){
    plan=((r.recentTaken>60&&!r.canReach)&&enabled(Plan::Rush))||
      (r.ours>=r.theirs*1.25&&enabled(Plan::Rush))||(r.theirMelee<3&&r.ourMelee>=3&&enabled(Plan::Rush))?Plan::Rush:Plan::Advance;
  }else if(brain==Brain::Wolfpack)plan=r.ourMelee>=3&&!p.raidSpent&&enabled(Plan::Raid)?Plan::Raid:Plan::Skirmish;
  else if(w.config->rules==Rules::Game&&finishing(r.ours,r.theirs)&&enabled(w.config->fewPlan[team]))plan=w.config->fewPlan[team];
  else if(r.raiders>=2&&enabled(Plan::Intercept))plan=Plan::Intercept;
  else if(r.theirShoot==0&&r.theirArt>0&&enabled(Plan::Hunt))plan=Plan::Hunt;
  else if(w.time-p.fastSeen<4&&enabled(Plan::Counter))plan=Plan::Counter;
  else if(w.time-std::max(0.0,w.lastHit)>8&&p.plan==Plan::Siege&&p.phase!=PackPhase::Creeping&&r.approach<10&&enabled(Plan::Push))plan=Plan::Push;
  else if(r.ourArt>=p.base.siegeMinArt&&r.theirShoot+r.theirArt>0&&enabled(Plan::Siege))plan=Plan::Siege;
  else if(r.exposed&&r.ourShoot>=r.theirShoot&&enabled(Plan::Push))plan=Plan::Push;
  else if(r.exposed&&r.ourMelee>=4&&enabled(Plan::Flank))plan=Plan::Flank;
  Tactics combo;combo.role.fill(plan);
  if(const auto* goal=planGoal(w,team))combo=goal->tactics;
  else if(w.hasForced&&team==w.forcedTeam)combo=w.forced;
  else if(w.config->lookahead[team].enabled&&p.search.hasChoice)combo=p.search.choice;
  const bool differs=combo.role!=p.combo.role;
  if(differs&&(combo.role[0]==Plan::Hold||w.time-p.planSince>=(w.config->lookahead[team].enabled?0:2)))setPlan(w,team,combo);
}
} // namespace astelia
