#include "formation.h"

namespace astelia {
namespace {
bool busy(const World& w,uint32_t i){const auto a=w.state[i].ability;if(a==invalidSlot)return false;const auto& s=w.abilities[a];return s.chargeEnd>w.time||s.aimUntil>w.time||s.disengageEnd>w.time;}
}
void coordAbilities(World& w,uint8_t team){
  auto& p=w.packs[team];const auto& P=w.config->abilityThresholds[team];const auto& es=w.teams[1-team];
  if(!w.survivors(1-team))return;
  std::array<std::vector<uint32_t>,3> roles;
  for(auto i:w.teams[team])if(w.units[i].alive&&size_t(w.units[i].role)<3)roles[size_t(w.units[i].role)].push_back(i);
  const auto& ms=roles[0];const auto& rs=roles[1];const auto& as=roles[2];
  if(w.config->skills[team].reactAim)for(auto i:es){const auto a=w.state[i].ability;if(a==invalidSlot||!w.units[i].alive)continue;const auto& ab=w.abilities[a];const auto* target=w.resolve(ab.aimTarget);
    if(ab.aimUntil<=w.time||!target||target->team!=team||busy(w,ab.aimTarget.slot))continue;
    if(target->role==Role::Melee)triggerAbility(w,ab.aimTarget.slot,Ability::Shield);
    else if(target->role==Role::Ranged)triggerAbility(w,ab.aimTarget.slot,Ability::Disengage,w.reference(i));}
  std::vector<uint32_t> band,urgent;
  for(auto i:ms){const auto& m=w.units[i];const auto* target=w.resolve(m.target);if(busy(w,i)||!target||!target->alive||!abilityReady(w,i,Ability::Charge)||gap(m,*target)<50||gap(m,*target)>200)continue;
    bool touching=false;for(auto j:es)if(w.units[j].alive&&gap(m,w.units[j])<=m.range){touching=true;break;}if(touching)continue;
    band.push_back(i);if(w.tactical[i].answering||threatens(w,team,m.target.slot))urgent.push_back(i);}
  for(auto j:es){const auto a=w.state[j].ability;if(a==invalidSlot||!w.units[j].alive)continue;const auto& ab=w.abilities[a];const auto* target=w.resolve(ab.chargeTarget);
    if(ab.chargeEnd<=w.time||!target||melee(target->role))continue;uint32_t best=invalidSlot;double bd=INFINITY;
    for(auto i:ms)if(!busy(w,i)&&abilityReady(w,i,Ability::Charge)){const double g=gap(w.units[i],w.units[j]),d=distance(w.units[i].pos,w.units[j].pos);
      if(g>=50&&g<=200&&d<bd){bd=d;best=i;}}
    if(best!=invalidSlot)triggerAbility(w,best,Ability::Charge,w.reference(j));}
  const auto& together=band.size()>=std::min(P.chargeSync,double(ms.size()))?band:urgent;
  for(auto i:together)triggerAbility(w,i,Ability::Charge,w.units[i].target);
  for(auto i:ms){const auto a=w.state[i].ability;if(a==invalidSlot||busy(w,i)||w.abilities[a].shieldUntil>w.time||!abilityReady(w,i,Ability::Shield))continue;
    bool close=false;for(auto j:es)if(w.units[j].alive&&melee(w.units[j].role)&&gap(w.units[i],w.units[j])<50){close=true;break;}if(close)continue;
    uint32_t aimed=0;for(auto j:es)if(w.units[j].alive&&!melee(w.units[j].role)&&w.units[j].target==w.reference(i)&&distance(w.units[i].pos,w.units[j].pos)<=w.units[j].range)++aimed;
    bool shell=false;for(const auto& sh:w.shells){const auto* src=w.resolve(sh.source);if(src&&src->team!=team&&!sh.slow&&sh.at-w.time<P.shieldShellWindow&&distance(w.units[i].pos,sh.pos)<sh.splash+w.units[i].radius){shell=true;break;}}
    if(aimed>=P.shieldAimedAt||shell)triggerAbility(w,i,Ability::Shield);}
  for(auto i:rs){if(busy(w,i)||(!abilityReady(w,i,Ability::Disengage)&&!abilityReady(w,i,Ability::Aimed)))continue;
    const auto near=nearest(w,i,false,true);const auto* meleeNear=w.resolve(near);UnitRef charger;
    for(auto j:es){const auto a=w.state[j].ability;if(a!=invalidSlot&&w.units[j].alive&&w.abilities[a].chargeEnd>w.time&&w.abilities[a].chargeTarget==w.reference(i)){charger=w.reference(j);break;}}
    bool alone=meleeNear&&distance(meleeNear->pos,w.units[i].pos)<P.disengageNear;
    if(alone)for(auto m:ms)if(distance(w.units[m].pos,meleeNear->pos)<60){alone=false;break;}
    if((charger||alone)&&triggerAbility(w,i,Ability::Disengage,charger?charger:near))continue;
    const auto target=w.units[i].target;const auto* t=w.resolve(target);
    if(t&&t->alive&&!(meleeNear&&distance(meleeNear->pos,w.units[i].pos)<P.aimedSafe)&&t->hp-p.pending[target.slot]>w.units[i].damage*P.aimedWorth&&laneClear(w,i,target))triggerAbility(w,i,Ability::Aimed,target);}
  std::vector<const Field*> fields;for(const auto& f:w.fields)if(f.team==team&&f.from<=w.time&&f.until>w.time+.8)fields.push_back(&f);
  bool slowPending=false;for(const auto& sh:w.shells){const auto* src=w.resolve(sh.source);if(sh.slow&&src&&src->team==team)slowPending=true;}
  for(auto i:as){if(busy(w,i))continue;const bool barrage=abilityReady(w,i,Ability::Barrage);if(!barrage&&!abilityReady(w,i,Ability::Slow))continue;bool done=false;
    if(barrage)for(const auto* f:fields){uint32_t count=0;UnitRef first;for(auto j:es)if(w.units[j].alive&&distance(w.units[j].pos,f->pos)<=f->radius){if(!first)first=w.reference(j);++count;}
      if(count>=2&&triggerAbility(w,i,Ability::Barrage,first)){done=true;break;}}
    if(done||slowPending||!fields.empty())continue;
    if(barrage){UnitRef best;uint32_t bv=0;for(auto j:es){if(!w.units[j].alive)continue;const double d=distance(w.units[i].pos,w.units[j].pos);
      if(d>w.units[i].range||d<w.config->roles[2].minRange)continue;uint32_t n=0,held=0;
      for(auto k:es)if(w.units[k].alive&&distance(w.units[k].pos,w.units[j].pos)<w.config->roles[2].splash){++n;if(pinned(w,k))++held;}
      if((n>=P.barrageMin||held>=P.barrageHeld)&&n+held>bv){bv=n+held;best=w.reference(j);}}
      if(best&&triggerAbility(w,i,Ability::Barrage,best))continue;}
    if(!abilityReady(w,i,Ability::Slow))continue;UnitRef best;uint32_t bn=0;
    for(auto j:es){if(!w.units[j].alive)continue;const double d=distance(w.units[i].pos,w.units[j].pos);if(d>w.units[i].range||d<w.config->roles[2].minRange||length(w.units[j].velocity)<P.slowMoving)continue;
      uint32_t n=0;for(auto k:es)if(w.units[k].alive&&distance(w.units[k].pos,w.units[j].pos)<45)++n;if(n>bn){bn=n;best=w.reference(j);}}
    if(best&&bn>=P.slowMin&&triggerAbility(w,i,Ability::Slow,{},w.units[best.slot].pos+leadVelocity(w,best,team)*w.config->roles[2].flight))break;
  }
}
} // namespace astelia
