#pragma once
#include "models.h"
#include "collector.h"
namespace net_slice {
class Host final:public astelia::control::Controller {
public:
 std::shared_ptr<const Weights> weights;bool teacher=false,shadow=false;uint64_t tick=0;std::string fight="fixture",ablation="intact";
 std::vector<js::V> views;std::map<UnitId,Intent> cache,raw;std::map<UnitId,uint64_t> decisionTicks;
 std::map<UnitId,Cast> casts;std::map<UnitId,CastOutput> projected;std::map<UnitId,double> phases,lastLaunch,heldForce;std::map<UnitId,std::vector<double>> memory,heldFeatures;std::map<UnitId,UnitId> assignments;std::set<UnitId> consumed;
 Graph fixed;std::vector<UnitId> fixedIds;Collector collector;std::map<UnitId,Intent> shadowLabels;
 Host(uint8_t,std::shared_ptr<const Weights>,bool teacher=false);
 void prepare(const astelia::control::Observation&)override;
 astelia::UnitDecision decide(const astelia::control::Observation&,UnitId)override;
 std::unique_ptr<astelia::control::Controller> clone()const override;
};
void builtinDecision(astelia::World&,uint32_t);void bind(astelia::World&);void decide(astelia::World&,uint32_t);void prePrep(astelia::World&);void postPrep(astelia::World&);void finishTick(astelia::World&);void consumedAck(astelia::World&,uint32_t);void launchedAck(astelia::World&,uint32_t,const astelia::Shell&);bool aimReach(const astelia::World&,uint32_t);astelia::Vec2 aimPoint(const astelia::World&,uint32_t,astelia::Vec2);
}
