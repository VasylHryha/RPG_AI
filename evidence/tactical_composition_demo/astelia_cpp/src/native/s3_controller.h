#pragma once
#include "controller.h"
#include <array>
#include <set>
namespace astelia::control {
enum class Arm { Resonator, Morale, PushPull };
struct Knobs {
  double K=2.5,Kt=2.5,kappa=25,beta=1.5,rateM=0,rateR=0,G=2.5,w=1.5,f=.75,gamma=1,fc=.65,mk=.6,lambdaTh=1.5;
};
Knobs controllerKnobs(Arm,const ControllerParams&,const std::string& skeleton="v1");
struct Memory {double state=0,zOut=0,zIn=0,lastOut=0,lastIn=0;UnitId target=0;double zInAnswered=0,zInUnanswered=0;bool hadLegalTarget=true,hadUnansweredThreat=false;};
// v2 geometry is centre-distance in model units (100 pixels per unit).
bool v2Legal(const ObservedUnit& source,const ObservedUnit& target);
bool v2Threat(const ObservedUnit& self,const ObservedUnit& enemy,double zOut);
double v2Preferred(const ObservedUnit& self,const ObservedUnit& enemy,const Knobs&,double commitment);
std::vector<const ObservedUnit*> v2EnemySet(const ObservedUnit& self,const std::vector<const ObservedUnit*>& nearest,const std::map<UnitId,Memory>&);
std::array<double,2> v2EnemyMotion(const ObservedUnit& self,const std::vector<const ObservedUnit*>& selected,const std::map<UnitId,Memory>&,const Knobs&,double commitment);
using PairModes = std::map<std::pair<UnitId,UnitId>,bool>; // true: commit, false: escape
double v3Preferred(const ObservedUnit& self,const ObservedUnit& enemy,const Knobs&,double commitment,PairModes&);
std::array<double,2> v3EnemyMotion(const ObservedUnit& self,const std::vector<const ObservedUnit*>& selected,const std::map<UnitId,Memory>&,const Knobs&,double commitment,PairModes&);
struct PairHold { double started=0,until=0; };
using PairHolds = std::map<std::pair<UnitId,UnitId>,PairHold>;
struct HoldEvent {UnitId id=0,enemy=0;std::string reason;double duration=0,planned=0;};
struct DecisionPair {UnitId enemy=0;bool commit=false;double remaining=0,preferred=0;};
struct DecisionDiagnostic {UnitId id=0,focus=0,reference=0;double x=0,y=0,c=1,dx=0,dy=0,preferred=0;std::vector<DecisionPair> pairs;};
struct Feasibility {double cosine=0;std::string reason;};
Feasibility v4Feasibility(const DecisionDiagnostic&,double,double);
double v4Preferred(const ObservedUnit&,const ObservedUnit&,const Knobs&,double,PairModes&,PairHolds&,double,std::vector<HoldEvent>&);
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
  Arm arm_;Knobs knobs_;bool v1_,v2_,v3_,v4_;
  PairModes pairModes_;
  PairHolds pairHolds_;
  std::map<UnitId,UnitId> focus_;
  std::vector<DecisionDiagnostic> decisionDiagnostic_;
  std::vector<HoldEvent> holdEvents_;
  std::map<UnitId,Memory> memory_;
  std::map<UnitId,UnitDecision> prepared_;
  std::vector<DiagnosticUnit> diagnostic_;
  std::vector<ModelUnit> model_;
  unsigned substeps_=1; // only the native refinement contract changes this
public:
  S3Controller(double seed,uint8_t side,Arm arm,const ControllerParams& params={},const std::string& skeleton="v1");
  void prepare(const Observation&) override;
  UnitDecision decide(const Observation&,UnitId) override;
  std::unique_ptr<Controller> clone() const override {return std::make_unique<S3Controller>(*this);}
  const std::map<UnitId,Memory>& memory() const {return memory_;}
  const PairHolds& pairHolds() const {return pairHolds_;}
  const std::map<UnitId,UnitId>& focus() const {return focus_;}
  const std::vector<DecisionDiagnostic>& decisionDiagnostic() const {return decisionDiagnostic_;}
  const std::vector<HoldEvent>& holdEvents() const {return holdEvents_;}
  const PairModes& pairModes() const {return pairModes_;}
  const std::vector<DiagnosticUnit>& diagnostic() const {return diagnostic_;}
  const std::vector<ModelUnit>& model() const {return model_;}
  const Knobs& knobs() const {return knobs_;}
  Arm arm() const {return arm_;}
};
} // namespace astelia::control
