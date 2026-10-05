#pragma once
#include "controller.h"
#include <array>
#include <set>
namespace astelia::control {
enum class Arm { Resonator, Morale, PushPull };
struct Knobs {
  double K=2.5,Kt=2.5,kappa=25,beta=1.5,rateM=0,rateR=0,G=2.5,w=1.5,f=.75,gamma=1;
};
Knobs controllerKnobs(Arm,const ControllerParams&);
struct Memory {double state=0,zOut=0,zIn=0,lastOut=0,lastIn=0;UnitId target=0;};
struct ModelUnit {double x=0,y=0,state=0,rate=0,pressure=0;UnitId id=0,target=0;};
struct Derivative {double x=0,y=0,state=0;};
// Production and reference algebra share the same protected ally kernel.
std::vector<Derivative> allyRhs(const std::vector<ModelUnit>&,double K,double J=.8,double eps=.01,Arm arm=Arm::Resonator,bool trueUnit=false);
std::vector<ModelUnit> coupledReferenceStep(std::vector<ModelUnit>,double dt,double K,double J,double eps);
std::vector<double> stateRhs(const std::vector<ModelUnit>&,Arm,const Knobs&);
std::vector<ModelUnit> frozenStep(std::vector<ModelUnit>,Arm,const Knobs&,double dt,unsigned substeps=1);
struct DiagnosticUnit {UnitId id=0,target=0;double x=0,y=0,state=0,commitment=1,zOut=0,zIn=0;};
class S3Controller : public Controller {
protected:
  Arm arm_;Knobs knobs_;
  std::map<UnitId,Memory> memory_;
  std::map<UnitId,UnitDecision> prepared_;
  std::vector<DiagnosticUnit> diagnostic_;
  std::vector<ModelUnit> model_;
  unsigned substeps_=1; // only the native refinement contract changes this
public:
  S3Controller(double seed,uint8_t side,Arm arm,const ControllerParams& params={});
  void prepare(const Observation&) override;
  UnitDecision decide(const Observation&,UnitId) override;
  std::unique_ptr<Controller> clone() const override {return std::make_unique<S3Controller>(*this);}
  const std::map<UnitId,Memory>& memory() const {return memory_;}
  const std::vector<DiagnosticUnit>& diagnostic() const {return diagnostic_;}
  const std::vector<ModelUnit>& model() const {return model_;}
  const Knobs& knobs() const {return knobs_;}
  Arm arm() const {return arm_;}
};
} // namespace astelia::control
