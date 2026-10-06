#pragma once
#include "s3_controller.h"
#include "s4_v6_complex.h"
namespace astelia::control {
UnitId v6RetainedTarget(double best,double old,UnitId incumbent,UnitId selected);
struct V6Diagnostic {
  UnitId id=0,target=0;
  double real=0,imag=0,amplitude=0;
  bool argValid=false,rateValid=false;
  double arg=0,argRate=0;
  std::string rateReason="no_previous_valid_endpoint";
};
struct V6ArgMemory {double arg=0,time=0;bool valid=false;};
class S4V6Controller : public S3Controller {
protected:
  double mu_=0;
  std::map<UnitId,v6::Complex> complexStates_;
  std::map<UnitId,v6::Complex> lastFiniteStates_;
  std::map<UnitId,V6ArgMemory> argMemory_;
  std::vector<V6Diagnostic> complexDiagnostic_;
  std::vector<v6::Unit> complexModel_;
  v6::Tick lastTick_;
  uint64_t retryCount_=0,failureCount_=0;
  unsigned refinement_=1; // captured default-knob engineering refinement only
  virtual v6::Tick integrateTick(const std::vector<v6::Unit>& a,double dt){return v6::step(a,{mu_,knobs_.K,knobs_.Kt},dt);}
public:
  S4V6Controller(double seed,uint8_t side,const ControllerParams& params={});
  void prepare(const Observation&) override;
  std::unique_ptr<Controller> clone() const override {return std::make_unique<S4V6Controller>(*this);}
  const auto& complexStates()const{return complexStates_;}
  const auto& argMemory()const{return argMemory_;}
  const auto& complexDiagnostic()const{return complexDiagnostic_;}
  const auto& complexModel()const{return complexModel_;}
  const auto& lastTick()const{return lastTick_;}
  double mu()const{return mu_;}
  uint64_t retryCount()const{return retryCount_;}
  uint64_t failureCount()const{return failureCount_;}
};
}
