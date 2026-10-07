#pragma once
#include "s4_v6_controller.h"
#include "../../s4_escort_probe_v3/escort.h"
namespace astelia::control {
enum class V7Selector { Gate, P16, V6 };
bool v7Mode(double c,bool previous,bool initialized);
struct V7Choice { UnitId id=0; bool mode=true,selectedP16=true,transition=false; UnitDecision baseline,p16,selected; };
class S4V7Controller : public S4V6Controller {
 V7Selector selector_;
 std::map<UnitId,bool> modes_;
 std::map<UnitId,UnitDecision> actions_;
 std::vector<V7Choice> choices_;
 std::vector<GunFocus> guns_;
public:
 S4V7Controller(double seed,uint8_t side,const ControllerParams& p,V7Selector s=V7Selector::Gate):S4V6Controller(seed,side,p),selector_(s){}
 void prepare(const Observation&)override;
 UnitDecision decide(const Observation&,UnitId)override;
 std::unique_ptr<Controller> clone()const override{return std::make_unique<S4V7Controller>(*this);}
 const auto& modes()const{return modes_;}
 const auto& choices()const{return choices_;}
 const auto& gunAudit()const{return guns_;}
 UnitDecision baseline(const Observation& o,UnitId id){return S4V6Controller::decide(o,id);}
};
}
