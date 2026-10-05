#pragma once
#include "formation.h"
#include "search_types.h"
namespace astelia {
std::vector<double> bcFeatures(const World& w,uint8_t team,const std::vector<Plan>& plans);
void networkScores(const Network& net,const std::vector<double>& features,std::vector<double>& hidden,std::vector<double>& scores);
uint32_t bcPredict(const Network& net,const std::vector<double>& features);
std::vector<uint32_t> bcTop(const Network& net,const std::vector<double>& features,uint32_t k);
std::vector<Plan> distinctTactics(Brain brain,uint8_t role);
double reachRate(const World& w,uint8_t team);
void lookahead(World& w,uint8_t team);
} // namespace astelia
