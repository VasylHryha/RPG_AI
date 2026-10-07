#pragma once
#include "s4_v6_controller.h"
namespace astelia::control {
struct ProbeGun {UnitId id;double x,y,gx,gy,px,py;bool solved,staged,inReach,outside;};
struct ProbeEscort {UnitId id;double x,y,gx,gy;bool arrived;UnitId focus;};
struct ProbeTick {double t=0,firstSight=-1,waveTime=-1;bool wave=false;UnitId target=0;unsigned ready=0,living=0;std::string reason;std::vector<ProbeGun> guns;std::vector<ProbeEscort> escorts;std::vector<ObservedUnit> enemies;};
class CollectiveProbeV1 final:public S4V6Controller {
 int arm_;UnitId target_=0;double ux_=1,uy_=0,firstSight_=-1,waveTime_=-1;std::string reason_;ProbeTick probe_;
public:
 CollectiveProbeV1(double seed,uint8_t side,const ControllerParams& p,int arm);
 void prepare(const Observation&)override;
 std::unique_ptr<Controller> clone()const override{return std::make_unique<CollectiveProbeV1>(*this);}
 const ProbeTick& probe()const{return probe_;}
};
}
