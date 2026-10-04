#include "search.h"

namespace astelia {
void Network::validate() const {
  if(!inputs||!hidden||!outputs||inputs>4096||hidden>4096||outputs>4096||w1.size()!=size_t(inputs)*hidden||b1.size()!=hidden||w2.size()!=size_t(hidden)*outputs||b2.size()!=outputs)
    throw std::invalid_argument("invalid network dimensions");
  for(const auto* weights:{&w1,&b1,&w2,&b2})for(double x:*weights)if(!std::isfinite(x))throw std::invalid_argument("nonfinite network coefficient");
}
void networkScores(const Network& net,const std::vector<double>& x,std::vector<double>& h,std::vector<double>& scores){
  if(x.size()!=net.inputs)throw std::invalid_argument("network feature count mismatch");for(double f:x)if(!std::isfinite(f))throw std::invalid_argument("nonfinite network feature");
  h.resize(net.hidden);scores.resize(net.outputs);
  for(uint32_t j=0;j<net.hidden;++j){double v=net.b1[j];const double* weights=net.w1.data()+size_t(j)*net.inputs;
    for(uint32_t i=0;i<net.inputs;++i)v+=weights[i]*x[i];h[j]=std::max(0.0,v);if(!std::isfinite(v))throw std::overflow_error("network hidden overflow");}
  for(uint32_t q=0;q<net.outputs;++q){double v=net.b2[q];const double* weights=net.w2.data()+size_t(q)*net.hidden;
    for(uint32_t j=0;j<net.hidden;++j)v+=weights[j]*h[j];scores[q]=v;if(!std::isfinite(v))throw std::overflow_error("network score overflow");}
}
uint32_t bcPredict(const Network& net,const std::vector<double>& x){std::vector<double> h,scores;networkScores(net,x,h,scores);uint32_t best=0;
  for(uint32_t i=1;i<scores.size();++i)if(scores[i]>scores[best])best=i;return best;}
std::vector<uint32_t> bcTop(const Network& net,const std::vector<double>& x,uint32_t k){std::vector<double> h,scores;networkScores(net,x,h,scores);
  std::vector<uint32_t> indices;indices.reserve(scores.size());for(uint32_t i=0;i<scores.size();++i)indices.push_back(i);
  std::stable_sort(indices.begin(),indices.end(),[&](uint32_t a,uint32_t b){return scores[a]>scores[b];});indices.resize(std::min(size_t(k),indices.size()));return indices;}
std::vector<double> bcFeatures(const World& w,uint8_t team,const std::vector<Plan>& plans){const auto& p=w.packs[team];const auto& ours=w.teams[team];const auto& es=w.foes(team);
  std::vector<double> f;f.reserve(33+plans.size());const auto matches=[](Role role,size_t r){return r==0?melee(role):r==1?role==Role::Ranged||role==Role::Archer:role==Role::Artillery;};
  for(const auto* list:{&ours,&es})for(size_t r=0;r<3;++r){uint32_t count=0;double hp=0;for(auto i:*list)if(w.units[i].alive&&matches(w.units[i].role,r)){++count;hp+=w.units[i].hp/w.units[i].maxhp;}
    f.push_back(count/30.0);f.push_back(count?hp/count:0);}
  const auto center=[&](const std::vector<uint32_t>& list){Vec2 c;uint32_t n=0;for(auto i:list)if(w.units[i].alive){c=c+w.units[i].pos;++n;}return n?c*(1.0/n):p.anchor;};
  const auto oc=center(ours),ec=center(es);const auto spread=[&](const std::vector<uint32_t>& list,Vec2 c){double sum=0;uint32_t n=0;for(auto i:list)if(w.units[i].alive){sum+=distance(w.units[i].pos,c);++n;}return n?sum/n:0;};
  double near=INFINITY;for(auto i:ours)if(w.units[i].alive)for(auto j:es)near=std::min(near,distance(w.units[i].pos,w.units[j].pos));
  Vec2 velocity;for(auto i:es)velocity=velocity+w.units[i].velocity;velocity=velocity*(1.0/std::max(size_t(1),es.size()));const double distanceCenters=distance(oc,ec),dd=distanceCenters>0?distanceCenters:1;
  f.push_back(std::min(near,1000.0)/1000);f.push_back(std::min(dd,1400.0)/1400);f.push_back(spread(es,ec)/300);f.push_back(spread(ours,oc)/300);f.push_back(dot(velocity,oc-ec)/dd/80);
  uint32_t ourRange=0,theirRange=0;for(auto i:ours)if(w.units[i].alive&&w.units[i].role!=Role::Melee){for(auto j:es)if(distance(w.units[i].pos,w.units[j].pos)<=w.units[i].range){++ourRange;break;}}
  for(auto i:es)if(!melee(w.units[i].role)){for(auto j:ours)if(w.units[j].alive&&distance(w.units[i].pos,w.units[j].pos)<=w.units[i].range){++theirRange;break;}}
  f.push_back(ourRange/30.0);f.push_back(theirRange/30.0);
  const auto ready=[&](const std::vector<uint32_t>& list,Role role,Ability ability,bool includeHunter){uint32_t count=0,n=0;for(auto i:list)if(w.units[i].alive&&(w.units[i].role==role||(includeHunter&&w.units[i].role==Role::Hunter))){++n;
      const auto a=w.state[i].ability;const double t=a==invalidSlot?0:w.abilities[a].ready[size_t(ability)];if(t<=w.time)++count;}return n?double(count)/n:0;};
  f.push_back(ready(es,Role::Melee,Ability::Charge,true));f.push_back(ready(ours,Role::Melee,Ability::Charge,false));f.push_back(ready(es,Role::Artillery,Ability::Barrage,false));f.push_back(ready(ours,Role::Artillery,Ability::Barrage,false));
  f.push_back(ready(es,Role::Artillery,Ability::Slow,false));f.push_back(ready(ours,Role::Artillery,Ability::Slow,false));
  const auto& r=p.read;f.push_back(r.meleeCharging/10.0);f.push_back(r.raiders/10.0);f.push_back(r.fastShooters/30.0);f.push_back(r.exposed?1:0);f.push_back(r.formedEnemy?1:0);f.push_back(std::min(r.quiet,10.0)/10);
  f.push_back(std::min(w.time,150.0)/150);f.push_back(clamp(r.room,0,1200)/1200);for(auto plan:plans)f.push_back(p.search.hasChoice&&p.search.choice.role[0]==plan?1:0);return f;
}
} // namespace astelia
