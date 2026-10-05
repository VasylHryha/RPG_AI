#include "api.h"
namespace astelia {
const std::vector<std::string>& opponentPool(){static const std::vector<std::string> names={"line","wide line","wedge","box","column","loose","screen","crescent","ring","wedge hold","line anvil","wedge flank","loose free","swarm","loose skirmish","loose berserk","storm","wolfpack","alone"};return names;}
Opponent enemyOf(const std::string& name,const Formation* overrideFormation){
  Brain brain=Brain::Formation;Formation f;
  if(name=="alone")brain=Brain::Alone;else if(name=="storm")brain=Brain::Storm;else if(name=="wolfpack")brain=Brain::Wolfpack;else if(name=="gamepack")brain=Brain::Gamepack;
  else f=overrideFormation?*overrideFormation:presetFormation(name);return {brain,f};
}
std::vector<std::string> drawOpponents(double seed,uint32_t rounds,bool pool){
  if(!std::isfinite(seed))throw std::invalid_argument("invalid opponent seed");Rng rng(toUint32(seed*2654435761.0));auto left=opponentPool();std::vector<std::string> out;out.reserve(pool?std::min(size_t(rounds),left.size()):rounds);
  for(uint32_t i=0;i<rounds;++i){const auto& from=pool?left:opponentPool();if(from.empty())break;const auto k=size_t(rng()*from.size());out.push_back(from[k]);if(pool)left.erase(left.begin()+k);}return out;
}
void setNet(Config& config,std::shared_ptr<const Network> net){
  if(net)net->validate();for(auto& la:config.lookahead){if(net&&(net->inputs!=33+la.plans.size()||net->outputs!=la.plans.size()))throw std::invalid_argument("network plans/features mismatch");}
  for(auto& la:config.lookahead){la.network=net;if(!net)la.netPrune=0;}
}
Summary summary(const World& w){const auto& s=w.stats;return {w.config->mode,s.melee,s.ranged,s.artillery,s.melee+s.ranged+s.artillery,s.wasted,s.aliveSeconds,s.enemyDamage,w.time,s.monsterDeaths,s.hunterKills,w.survivors(0),w.survivors(1)};}
Summary run(World& w){while(!w.done())coreStep(w);return summary(w);}
} // namespace astelia
