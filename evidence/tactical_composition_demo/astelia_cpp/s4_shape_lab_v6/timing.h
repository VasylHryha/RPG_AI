#pragma once
#include "world.h"
#include "controller.h"
#include "js_value.h"
#include <map>
namespace battery_v1 {
using namespace astelia;
constexpr double tau=6.2831853071795864769;
struct Gun {UnitId id;Vec2 pos;double T;bool ready,legal;};
struct State {double phi=0,waiting=-1,idle=0;uint64_t volley=0;bool hold=false;unsigned neighbours=0;std::string reason="none";};
struct Exposure {UnitId source;double born,at;uint64_t volley;std::vector<UnitId> ids;};
struct Battery {
 std::vector<Exposure> exposures;js::Args audit;
 int mode=0;double k=1,radius=400;std::map<UnitId,State> states;
 // Synchronous explicit Euler, with <= 1/120 s substeps; K_i = k/T_i.
 std::map<UnitId,bool> step(const std::vector<Gun>& guns,double t,double dt);
 void fired(UnitId id){auto& s=states.at(id);s.phi=0;s.waiting=-1;s.hold=false;s.reason="fired_reset";}
};
Config configuration(js::V);World create(std::shared_ptr<const Config>,js::V);
class DodgingDummy final:public control::Controller {
public:
 std::shared_ptr<const struct DummySnapshot> view;
 DodgingDummy(double seed,uint8_t side):Controller(seed,side){}
 UnitDecision decide(const control::Observation&,UnitId)override;
 std::unique_ptr<control::Controller> clone()const override{return std::make_unique<DodgingDummy>(*this);}
};
void prepareDummies(World&);
void central(World&);void oscillator(World&);void fired(World&,uint32_t);
js::V rows(const World&);js::V audits(World&);void launch(World&,uint32_t,const Shell&);void landing(World&,const Shell&);
bool copiedFireGate(World&,uint32_t);
bool copiedWaves(World&,uint32_t,unsigned waves=3);
}
