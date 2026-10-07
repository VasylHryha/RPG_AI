#pragma once
#include "spacing.h"
namespace astelia::control {
struct EscortPoint {
 UnitId id=0,gun=0,threat=0,target=0;double x=0,y=0,gx=0,gy=0,rawX=0,rawY=0,clipX=0,clipY=0;
 int direction=0; // 0 unavailable, 1 ranged, 2 centroid, 3 nearest gun
};
std::vector<EscortPoint> escortPoints(const Observation&,uint8_t,double);
class EscortProbeV1 final:public Controller {
 SpacingProbeV1 base_;double dose_;std::map<UnitId,UnitDecision> actions_;
public:
 EscortProbeV1(double seed,uint8_t side,const ControllerParams& p,int arm):Controller(seed,side),base_(seed,side,p,11),dose_(arm==12?60:120){if(arm!=12&&arm!=13)throw std::invalid_argument("unknown escort arm");}
 void prepare(const Observation&)override;
 UnitDecision decide(const Observation&,UnitId)override;
 std::unique_ptr<Controller> clone()const override{return std::make_unique<EscortProbeV1>(*this);}
 SpacingProbeV1& base(){return base_;}
 double dose()const{return dose_;}
};
Controller* probeBase(Controller*);
}
