#include "formation.h"

namespace astelia {
bool canDodge(const World& w,UnitRef target,UnitRef shooter){
  if(!w.config->aimedShots)return false;const auto* h=w.resolve(target);if(!h||!h->alive)return false;
  const auto& sk=w.config->skills[h->team];if(!sk.dodgeShots||(sk.dodgeSoft&&melee(h->role)))return false;
  const auto* t=w.resolve(h->target);if(melee(h->role)&&t&&t->alive&&gap(*h,*t)<=h->range)return false;
  const auto* u=w.resolve(shooter);return !u||distance(u->pos,h->pos)/w.config->shotSpeed-sk.shotReact>(h->radius+3)/std::max(1.0,h->speed);
}
double hitProbability(const World& w,uint8_t team,UnitRef target,UnitRef shooter){return canDodge(w,target,shooter)?w.packs[team].hitRate:.9;}
double hitLineProbability(const World& w,uint8_t team,UnitRef target,UnitRef shooter){
  const double p=hitProbability(w,team,target,shooter);const auto* u=w.resolve(shooter);const auto* h=w.resolve(target);const double fd=w.config->skills[team].fireDepth;
  if(!u||!h||fd==0)return p;const auto delta=h->pos-u->pos;const double l=length(delta);const auto direction=delta*(1/(l>0?l:1));uint32_t n=0;
  for(auto i:w.teams[h->team]){const auto& e=w.units[i];if(!e.alive||w.reference(i)==target)continue;const auto pos=e.pos-u->pos;const double a=dot(pos,direction);
    if(a>l&&a<u->range*1.3&&std::abs(pos.x*direction.y-pos.y*direction.x)<e.radius+4)++n;}
  return p+(1-p)*std::min(.6,n*fd);
}
bool aimClear(const World& w,uint32_t i,UnitRef target){
  const auto& u=w.units[i];if(!w.packs[u.team].enabled||!w.config->skills[u.team].fireControl||!w.config->aimedShots)return laneClear(w,i,target);
  const auto* t=w.resolve(target);if(!t)return false;const auto point=interceptPoint(w,u.pos,target,w.config->shotSpeed,u.team);
  const auto b=lineBlocker(w.units,w.liveGrid,u.pos,point,t->radius,w.reference(i),{});
  return (!b||w.units[b.slot].team!=u.team)&&laneClear(w,i,target);
}
void addPending(World& w,UnitRef source,UnitRef target,double amount){const auto* u=w.resolve(source);const auto* t=w.resolve(target);if(!u||!t)return;
  auto& p=w.packs[u->team];if(p.enabled){p.pending.resize(w.units.size());p.pending[target.slot]+=amount;}}
UnitRef artilleryTarget(const World& w,uint32_t i){
  const auto& u=w.units[i];const auto& p=w.packs[u.team];if(!p.enabled){auto ref=nearest(w,i,true);return ref?ref:nearest(w,i);}
  const auto& f=p.formation;const auto& es=w.foes(u.team);const auto& sk=w.config->skills[u.team];UnitRef best;double score=0;
  const double splash=w.state[i].splash>0?w.state[i].splash:w.config->roles[2].splash;
  for(auto j:es){const auto& h=w.units[j];const double d=distance(u.pos,h.pos);if(d>u.range||d<w.state[i].minRange)continue;
    uint32_t n=0;for(auto k:es)if(squared(w.units[k].pos-h.pos)<splash*splash)++n;
    const double value=n*(f.artilleryDoctrine==ArtilleryDoctrine::Pinned&&pinned(w,j)?f.engagedWeight:1)*
      (f.artilleryDoctrine==ArtilleryDoctrine::Counter&&h.role==Role::Artillery?6:1)*(f.artilleryDoctrine==ArtilleryDoctrine::Soft&&!melee(h.role)?3:1)*
      (sk.killSpeed?h.damage/std::max(.3,w.state[j].cooldownMax)/std::max(1.0,h.hp)*100:1);
    if(value>score){score=value;best=w.reference(j);}
  }
  return best;
}
UnitRef shooterTarget(const World& w,uint32_t i,bool released){
  const auto& u=w.units[i];const auto& p=w.packs[u.team];const auto& f=p.formation;const auto& sk=w.config->skills[u.team];const auto& ts=w.tactical[i];
  const auto usable=[&](UnitRef r){const auto* t=w.resolve(r);return t&&t->alive&&gap(u,*t)<=u.range;};
  if(!released){if(usable(ts.fireOrder))return ts.fireOrder;if(f.shooterFocus==ShooterFocus::One&&usable(p.focus))return p.focus;
    if(f.shooterFocus==ShooterFocus::Squads&&usable(ts.squadFocus))return ts.squadFocus;if(f.shooterFocus==ShooterFocus::Nearest)return nearest(w,i);}
  struct Candidate{double key;UnitRef target;};std::vector<Candidate> candidates;
  for(auto j:w.foes(u.team)){const auto& h=w.units[j];if(gap(u,h)>u.range)continue;const double left=h.hp-p.pending[j];if(left<=0)continue;
    const bool threat=threatens(w,u.team,j);double tier=0;
    if(released)tier=f.shooterFocus==ShooterFocus::Soft&&melee(h.role)?1e6:0;
    else if(f.shooterFocus==ShooterFocus::Protect)tier=threat?0:1e6+distance(h.pos,u.pos)*1e3;
    else if(f.shooterFocus==ShooterFocus::Soft)tier=(melee(h.role)?1e6:0)+(threat?0:1e5);
    else tier=threat?0:pinned(w,j)?1e6:2e6;
    const double ks=sk.killSpeed?10/std::max(.1,h.damage/std::max(.3,w.state[j].cooldownMax)):1;
    candidates.push_back({tier+(sk.fireControl?left/hitLineProbability(w,u.team,w.reference(j),w.reference(i)):left)*ks,w.reference(j)});
  }
  if(candidates.empty())return nearest(w,i);size_t best=0;for(size_t k=1;k<candidates.size();++k)if(candidates[k].key<candidates[best].key)best=k;
  if(aimClear(w,i,candidates[best].target))return candidates[best].target;
  std::stable_sort(candidates.begin(),candidates.end(),[](const Candidate& a,const Candidate& b){return a.key<b.key;});
  for(const auto& c:candidates)if(aimClear(w,i,c.target))return c.target;return candidates[0].target;
}
void leaderFire(World& w,uint8_t team){
  auto& p=w.packs[team];const auto& sk=w.config->skills[team];const auto& shooters=p.members[1];const auto& es=w.foes(team);
  for(auto i:shooters){auto& t=w.tactical[i];t.fireOrder={};t.fireHold=false;t.aimOffset=0;}
  if((p.formation.release&2)||shooters.empty()||es.empty())return;
  struct Target{uint32_t slot;double left,key;std::vector<uint32_t> reach;};std::vector<Target> targets;
  for(auto j:es){const auto& h=w.units[j];const double left=h.hp-p.pending[j];if(left<=0)continue;Target t{j,left,(threatens(w,team,j)?0:1e6)-(h.damage/(w.state[j].cooldownMax>0?w.state[j].cooldownMax:1))/left*1e3,{}};
    for(auto i:shooters)if(gap(w.units[i],h)<=w.units[i].range)t.reach.push_back(i);if(!t.reach.empty())targets.push_back(std::move(t));}
  std::stable_sort(targets.begin(),targets.end(),[](const Target& a,const Target& b){return a.key<b.key;});std::vector<uint8_t> free(w.units.size(),0);for(auto i:shooters)free[i]=1;
  for(auto& target:targets){std::vector<uint32_t> group;double expected=0;const auto ref=w.reference(target.slot);const auto& h=w.units[target.slot];
    target.reach.erase(std::remove_if(target.reach.begin(),target.reach.end(),[&](uint32_t i){return !free[i];}),target.reach.end());
    std::stable_sort(target.reach.begin(),target.reach.end(),[&](uint32_t a,uint32_t b){return distance(w.units[a].pos,h.pos)<distance(w.units[b].pos,h.pos);});
    for(auto i:target.reach){group.push_back(i);free[i]=0;expected+=w.units[i].damage*hitProbability(w,team,ref,w.reference(i));if(expected>=target.left*1.1)break;}
    if(group.empty())continue;bool all=true,any=false,dodge=false;for(auto i:group){all&=prepared(w,i);any|=prepared(w,i);dodge|=canDodge(w,ref,w.reference(i));}
    auto& targetState=w.tactical[target.slot];double since=any?(targetState.holdSince>0&&targetState.holdTeam==team?targetState.holdSince:w.time):-1;
    targetState.holdSince=since;targetState.holdTeam=team;
    const bool hold=w.config->windUp&&!all&&dodge&&since>=0&&w.time-since<.5;constexpr int offsets[]={0,1,-1};
    for(size_t j=0;j<group.size();++j){const auto i=group[j];auto& t=w.tactical[i];t.fireOrder=ref;t.fireHold=hold;
      t.aimOffset=sk.leaderBracket&&group.size()>1&&canDodge(w,ref,w.reference(i))?offsets[j%3]*sk.leaderBracket:0;}
  }
}
} // namespace astelia
