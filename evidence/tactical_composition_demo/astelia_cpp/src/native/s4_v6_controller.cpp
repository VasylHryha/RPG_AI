#include "s4_v6_controller.h"
#include <algorithm>
#include <cmath>
#include <stdexcept>
namespace astelia::control {
namespace {
double admitMu(const ControllerParams& params){auto p=params.find("mu");const double mu=p==params.end()?0:p->second;
  if(!std::isfinite(mu)||mu< -2||mu>2)throw std::invalid_argument("invalid controller param: mu");return mu;}
ControllerParams legacyParams(ControllerParams params){admitMu(params);params.erase("mu");
  if(params.count("omega_melee"))throw std::invalid_argument("omega_melee is fixed at zero in v6");return params;}
bool finiteMemory(const Memory& m){return std::isfinite(m.zOut)&&std::isfinite(m.zIn)&&std::isfinite(m.lastOut)&&std::isfinite(m.lastIn)&&std::isfinite(m.zInAnswered)&&std::isfinite(m.zInUnanswered);}
void finite(double value){if(!std::isfinite(value))throw std::runtime_error("non_finite_consumer");}
}
S4V6Controller::S4V6Controller(double seed,uint8_t side,const ControllerParams& params):
  S3Controller(seed,side,Arm::Resonator,legacyParams(params),"v5"),mu_(admitMu(params)){}
UnitId v6RetainedTarget(double best,double old,UnitId incumbent,UnitId selected){return std::isfinite(old)&&best-old<.2?incumbent:selected;}
void S4V6Controller::prepare(const Observation& o){
  prepared_.clear();diagnostic_.clear();decisionDiagnostic_.clear();complexDiagnostic_.clear();complexModel_.clear();model_.clear();
  std::vector<const ObservedUnit*> units;std::set<UnitId> live;
  for(const auto& u:o.units)if(u.hp>0){units.push_back(&u);live.insert(u.id);}
  std::sort(units.begin(),units.end(),[](auto a,auto b){return a->id<b->id;});
  auto clean=[&](auto& map){for(auto it=map.begin();it!=map.end();)if(!live.count(it->first))it=map.erase(it);else ++it;};
  clean(memory_);clean(complexStates_);clean(lastFiniteStates_);clean(argMemory_);
  for(auto it=pairModes_.begin();it!=pairModes_.end();)if(!live.count(it->first.first)||!live.count(it->first.second))it=pairModes_.erase(it);else ++it;
  auto oldStates=lastFiniteStates_;const auto oldModes=pairModes_;bool bad=false;
  for(const auto& u:o.units)if(!std::isfinite(u.hp))bad=true;
  const bool validDt=o.dt>0&&std::isfinite(o.dt);const double q=validDt?std::exp(-o.dt/2):0;
  for(auto p:units){const auto& u=*p;
    auto found=memory_.find(u.id);if(found==memory_.end()){Memory m;m.lastOut=u.dealtToEnemy;m.lastIn=u.takenFromEnemy;found=memory_.emplace(u.id,m).first;}
    auto& m=found->second;if(m.target&&!live.count(m.target))m.target=0;
    bool valid=validDt&&std::isfinite(o.t)&&std::isfinite(u.x)&&std::isfinite(u.y)&&std::isfinite(u.range)&&std::isfinite(u.minRange)&&std::isfinite(u.radius)&&std::isfinite(u.speed)&&u.maxhp>0&&std::isfinite(u.maxhp)&&finiteMemory(m)&&std::isfinite(u.dealtToEnemy)&&std::isfinite(u.takenFromEnemy)&&u.dealtToEnemy>=m.lastOut&&u.takenFromEnemy>=m.lastIn;
    if(valid){auto next=m;
      const double outgoing=(1-q)*(u.dealtToEnemy-m.lastOut)/o.dt/u.maxhp;
      const double incoming=(1-q)*(u.takenFromEnemy-m.lastIn)/o.dt/u.maxhp;
      next.zOut=q*m.zOut+outgoing;next.zIn=q*m.zIn+incoming;
      if(u.team==side_){next.zInAnswered=q*m.zInAnswered+(!m.hadUnansweredThreat?incoming:0);next.zInUnanswered=q*m.zInUnanswered+(m.hadUnansweredThreat?incoming:0);}
      next.lastOut=u.dealtToEnemy;next.lastIn=u.takenFromEnemy;valid=finiteMemory(next);if(valid)m=next;
    }
    if(!valid)bad=true;
    if(u.team==side_){auto inserted=complexStates_.emplace(u.id,v6::Complex{});lastFiniteStates_.emplace(u.id,v6::Complex{});oldStates.emplace(u.id,lastFiniteStates_.at(u.id));
      complexModel_.push_back({u.id,m.target,u.x/100,u.y/100,u.role==ObservedRole::Melee?0:knobs_.rateR,
                              knobs_.kappa*(m.zInAnswered-knobs_.beta*m.zOut-m.zInUnanswered),inserted.first->second});}
  }
  // Counter consumption is outside integration and occurs exactly once.
  lastTick_=bad?v6::Tick{}:integrateTick(complexModel_,o.dt);
  if(bad){lastTick_.units=complexModel_;lastTick_.reason="observation_or_counter_non_finite";}
  retryCount_+=lastTick_.retries;
  try{
    if(!lastTick_.accepted)throw std::runtime_error(lastTick_.reason);
    auto next=lastTick_.units;
    if(refinement_>1){ // Engineering comparison: same tick, 4n policy substeps.
      next=complexModel_;const double h=o.dt/(lastTick_.n*refinement_);const auto edges=v6::topology(next);
      for(unsigned s=0;s<lastTick_.n*refinement_;++s){auto a=next;
        auto shift=[&](const std::vector<v6::Complex>& d,double dt){auto b=a;for(size_t i=0;i<b.size();++i)b[i].z+=dt*d[i];return b;};
        auto k1=v6::rhs(a,{mu_,knobs_.K,knobs_.Kt},edges),k2=v6::rhs(shift(k1,h/2),{mu_,knobs_.K,knobs_.Kt},edges),
             k3=v6::rhs(shift(k2,h/2),{mu_,knobs_.K,knobs_.Kt},edges),k4=v6::rhs(shift(k3,h),{mu_,knobs_.K,knobs_.Kt},edges);
        for(size_t i=0;i<a.size();++i)next[i].z+=h/6*(k1[i]+2.0*k2[i]+2.0*k3[i]+k4[i]);}
    }
    const auto edges=v6::topology(next);
    for(size_t i=0;i<next.size();++i){const auto id=next[i].id;const auto& self=**std::find_if(units.begin(),units.end(),[&](auto p){return p->id==id;});
      auto& m=memory_.at(id);double vx=0,vy=0;const double c=v6::commitment(next[i].z);UnitDecision d{self.x,self.y,0,0,0};
      for(auto edge:edges[i]){auto j=edge.first;const double dx=next[j].x-next[i].x,dy=next[j].y-next[i].y,r=std::hypot(dx,dy);finite(r);
        const double radial=(1+.8*v6::similarity(next[i].z,next[j].z)-1/std::max(r,.01))/(r>0?r:1);
        finite(radial);vx+=dx*radial/edges[i].size();vy+=dy*radial/edges[i].size();finite(vx);finite(vy);}
      std::vector<const ObservedUnit*> enemies;for(auto u:units)if(u->team!=side_)enemies.push_back(u);
      std::sort(enemies.begin(),enemies.end(),[&](auto a,auto b){const double ra=std::hypot(a->x-self.x,a->y-self.y),rb=std::hypot(b->x-self.x,b->y-self.y);return ra<rb||(ra==rb&&a->id<b->id);});
      auto selected=v2EnemySet(self,enemies,memory_);
      for(auto enemy:enemies)v3Preferred(self,*enemy,knobs_,c,pairModes_);
      const auto enemyMotion=v3EnemyMotion(self,selected,memory_,knobs_,c,pairModes_);finite(enemyMotion[0]);finite(enemyMotion[1]);vx+=enemyMotion[0];vy+=enemyMotion[1];
      double best=-INFINITY,old=-INFINITY;UnitId target=0;bool legal=false;
      for(auto enemy:enemies)if(v2Legal(self,*enemy)){legal=true;
        const auto group=v6::group(next,i,enemy->id);const auto& em=memory_.at(enemy->id);
        const double engagement=knobs_.kappa*(em.zIn+em.zOut);finite(engagement);
        const double score=v6::alignment(next[i].z,group)+std::tanh(engagement);finite(score);
        if(score>best||(score==best&&enemy->id<target)){best=score;target=enemy->id;}if(enemy->id==m.target)old=score;}
      m.hadUnansweredThreat=false;for(auto enemy:enemies)if(v2Threat(self,*enemy,memory_.at(enemy->id).zOut)&&!v2Legal(self,*enemy)){m.hadUnansweredThreat=true;break;}
      m.hadLegalTarget=legal;d.target=v6RetainedTarget(best,old,m.target,target);
      finite(vx);finite(vy);const double speed=std::hypot(vx,vy);finite(speed);
      if(!enemies.empty()&&speed>=1e-9){d.x=self.x+200*vx/speed;d.y=self.y+200*vy/speed;finite(d.x);finite(d.y);d.multiplier=std::min(1.0,speed);}
      finite(d.multiplier);prepared_[id]=d;
      diagnostic_.push_back({id,d.target,self.x,self.y,next[i].z.real(),c,m.zOut,m.zIn});
      if(attributionDiagnostics_){DecisionDiagnostic trace;trace.id=id;trace.x=self.x;trace.y=self.y;trace.c=c;
        for(auto enemy:enemies){auto mode=pairModes_.find({id,enemy->id});if(mode!=pairModes_.end())trace.pairs.push_back({enemy->id,mode->second,0,100*v3Preferred(self,*enemy,knobs_,c,pairModes_)});}decisionDiagnostic_.push_back(trace);}
    }
    // Publish only after every integration and downstream consumer succeeds.
    for(size_t i=0;i<next.size();++i){const auto id=next[i].id;complexStates_[id]=next[i].z;memory_.at(id).target=prepared_.at(id).target;
      const double r=v6::amplitude(next[i].z);V6Diagnostic d;d.id=id;d.target=prepared_.at(id).target;d.real=next[i].z.real();d.imag=next[i].z.imag();d.amplitude=r;d.argValid=r>=v6::delta;
      auto& history=argMemory_[id];if(d.argValid){d.arg=std::arg(next[i].z);
        if(history.valid&&o.t>history.time){d.argRate=std::remainder(d.arg-history.arg,2*3.14159265358979323846)/(o.t-history.time);finite(d.argRate);d.rateValid=true;d.rateReason="";}
        else d.rateReason=history.valid?"non_increasing_time":"no_previous_valid_endpoint";
      }else d.rateReason="amplitude_below_0.2";
      history={d.arg,o.t,d.argValid};complexDiagnostic_.push_back(d);}
    lastTick_.units=next;lastFiniteStates_=complexStates_;
  }catch(const std::exception& e){
    ++failureCount_;lastTick_.accepted=false;lastTick_.reason=e.what();lastTick_.units=complexModel_;complexStates_=oldStates;pairModes_=oldModes;
    prepared_.clear();diagnostic_.clear();complexDiagnostic_.clear();decisionDiagnostic_.clear();
    for(auto p:units)if(p->team==side_){prepared_[p->id]={p->x,p->y,0,0,0,true};memory_.at(p->id).target=0;argMemory_.erase(p->id);}
  }
}
}
