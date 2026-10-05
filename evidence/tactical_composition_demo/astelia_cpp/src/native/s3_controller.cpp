#include "s3_controller.h"
#include <algorithm>
#include <cmath>
#include <stdexcept>
namespace astelia::control {
namespace {
constexpr double pi=3.14159265358979323846;
std::vector<size_t> neighbors(const std::vector<ModelUnit>& a,size_t i){
  std::vector<size_t> n;for(size_t j=0;j<a.size();++j)if(j!=i&&std::hypot(a[j].x-a[i].x,a[j].y-a[i].y)<3)n.push_back(j);
  std::sort(n.begin(),n.end(),[&](size_t j,size_t k){const double rj=std::hypot(a[j].x-a[i].x,a[j].y-a[i].y),rk=std::hypot(a[k].x-a[i].x,a[k].y-a[i].y);return rj<rk||(rj==rk&&a[j].id<a[k].id);});
  if(n.size()>8)n.resize(8);return n;
}
struct Group {double value=0;bool valid=false;};
Group aggregate(const std::vector<ModelUnit>& a,size_t i,UnitId target,Arm arm){
  if(!target)return {};double x=0,y=0;size_t count=0;
  for(size_t j=0;j<a.size();++j)if(j!=i&&a[j].target==target){++count;if(arm==Arm::Resonator){x+=std::cos(a[j].state);y+=std::sin(a[j].state);}else x+=a[j].state;}
  if(!count)return {};if(arm==Arm::Resonator){if(std::hypot(x,y)<.1*count)return {};return {std::atan2(y,x),true};}return {x/count,true};
}
bool finite(const Memory& m){return std::isfinite(m.state)&&std::isfinite(m.zOut)&&std::isfinite(m.zIn)&&std::isfinite(m.lastOut)&&std::isfinite(m.lastIn);}
std::vector<ModelUnit> shifted(const std::vector<ModelUnit>& a,const std::vector<Derivative>& d,double h,bool positions){auto out=a;for(size_t i=0;i<a.size();++i){if(positions){out[i].x+=h*d[i].x;out[i].y+=h*d[i].y;}out[i].state+=h*d[i].state;}return out;}
}
Knobs controllerKnobs(Arm arm,const ControllerParams& params){
  Knobs k;if(arm==Arm::Morale)k.rateM=k.rateR=1;
  struct Bound {double* value;double lo,hi;};
  std::map<std::string,Bound> bounds{{"G",{&k.G,0,5}},{"f",{&k.f,.3,1.2}}};
  if(arm!=Arm::PushPull){bounds.insert({{"K",{&k.K,0,5}},{"K_t",{&k.Kt,0,5}},{"kappa",{&k.kappa,0,50}},{"beta",{&k.beta,0,3}},{"w",{&k.w,0,3}},{"gamma",{&k.gamma,0,2}}});
    if(arm==Arm::Resonator){bounds["omega_melee"]={&k.rateM,-2,2};bounds["omega_ranged"]={&k.rateR,-2,2};}
    else{bounds["lambda_melee"]={&k.rateM,0,2};bounds["lambda_ranged"]={&k.rateR,0,2};}}
  for(const auto& p:params){auto b=bounds.find(p.first);if(b==bounds.end()||!std::isfinite(p.second)||p.second<b->second.lo||p.second>b->second.hi)throw std::invalid_argument("invalid controller param: "+p.first);*b->second.value=p.second;}
  return k;
}
std::vector<Derivative> allyRhs(const std::vector<ModelUnit>& a,double K,double J,double eps,Arm arm,bool trueUnit){
  std::vector<Derivative> d(a.size());for(size_t i=0;i<a.size();++i){auto n=neighbors(a,i);d[i].state=a[i].rate;
    for(auto j:n){const double dx=a[j].x-a[i].x,dy=a[j].y-a[i].y,r=std::hypot(dx,dy),rr=std::max(r,eps),diff=a[j].state-a[i].state;
      const double sim=arm==Arm::Resonator?std::cos(diff):arm==Arm::Morale?1-std::abs(diff):1;
      const double radial=(1+J*sim-1/rr)/(trueUnit?(r>0?r:1):rr);d[i].x+=dx*radial/n.size();d[i].y+=dy*radial/n.size();d[i].state+=K*std::exp(-r*r)*std::sin(diff)/n.size();}}
  return d;
}
std::vector<ModelUnit> coupledReferenceStep(std::vector<ModelUnit> a,double dt,double K,double J,double eps){
  // The C4 contract holds the initial neighbor identities/mask through stages.
  std::vector<std::vector<size_t>> ns;for(size_t i=0;i<a.size();++i)ns.push_back(neighbors(a,i));
  auto rhs=[&](const std::vector<ModelUnit>& x){std::vector<Derivative> d(x.size());for(size_t i=0;i<x.size();++i){d[i].state=x[i].rate;for(auto j:ns[i]){double dx=x[j].x-x[i].x,dy=x[j].y-x[i].y,r=std::hypot(dx,dy),rr=std::max(r,eps),diff=x[j].state-x[i].state,radial=(1+J*std::cos(diff)-1/rr)/rr;
    d[i].x+=dx*radial/ns[i].size();d[i].y+=dy*radial/ns[i].size();d[i].state+=K*std::exp(-r*r)*std::sin(diff)/ns[i].size();}}return d;};
  auto k1=rhs(a),k2=rhs(shifted(a,k1,dt/2,true)),k3=rhs(shifted(a,k2,dt/2,true)),k4=rhs(shifted(a,k3,dt,true));
  for(size_t i=0;i<a.size();++i){a[i].x+=dt/6*(k1[i].x+2*k2[i].x+2*k3[i].x+k4[i].x);a[i].y+=dt/6*(k1[i].y+2*k2[i].y+2*k3[i].y+k4[i].y);a[i].state+=dt/6*(k1[i].state+2*k2[i].state+2*k3[i].state+k4[i].state);}return a;
}
namespace {
using Topology=std::vector<std::vector<std::pair<size_t,double>>>;
Topology topology(const std::vector<ModelUnit>& a){Topology edges(a.size());for(size_t i=0;i<a.size();++i){auto n=neighbors(a,i);for(auto j:n){double r=std::hypot(a[j].x-a[i].x,a[j].y-a[i].y);edges[i].push_back({j,std::exp(-r*r)});}}return edges;}
std::vector<double> stateWithTopology(const std::vector<ModelUnit>& a,Arm arm,const Knobs& k,const Topology& edges){
  std::vector<double> d(a.size());for(size_t i=0;i<a.size();++i){auto g=aggregate(a,i,a[i].target,arm);
    if(arm==Arm::Resonator)d[i]=a[i].rate+a[i].pressure*std::sin(a[i].state)+(g.valid?k.Kt*std::sin(g.value-a[i].state):0);
    else if(arm==Arm::Morale)d[i]=-a[i].rate*a[i].state-a[i].pressure+(g.valid?k.Kt*(g.value-a[i].state):0);else continue;
    for(auto edge:edges[i]){double diff=a[edge.first].state-a[i].state;d[i]+=k.K*edge.second*(arm==Arm::Resonator?std::sin(diff):diff)/edges[i].size();}}
  return d;
}
}
std::vector<double> stateRhs(const std::vector<ModelUnit>& a,Arm arm,const Knobs& k){return stateWithTopology(a,arm,k,topology(a));}
std::vector<ModelUnit> frozenStep(std::vector<ModelUnit> a,Arm arm,const Knobs& k,double dt,unsigned substeps){
  // Positions, identities and pressure are frozen for all stages/half steps.
  const auto edges=topology(a);const double h=dt/substeps;for(unsigned s=0;s<substeps;++s){auto shift=[&](const std::vector<double>& d,double step){auto b=a;for(size_t i=0;i<a.size();++i)b[i].state+=step*d[i];return b;};
    auto rhs=[&](const std::vector<ModelUnit>& b){return stateWithTopology(b,arm,k,edges);};
    auto k1=rhs(a),k2=rhs(shift(k1,h/2)),k3=rhs(shift(k2,h/2)),k4=rhs(shift(k3,h));
    for(size_t i=0;i<a.size();++i){a[i].state+=h/6*(k1[i]+2*k2[i]+2*k3[i]+k4[i]);}}
  // Clipping is the game-tick boundary map, not an extra half-step map.
  if(arm==Arm::Morale)for(auto& u:a)if(std::isfinite(u.state))u.state=std::max(-1.0,std::min(1.0,u.state));
  return a;
}

S3Controller::S3Controller(double seed,uint8_t side,Arm arm,const ControllerParams& params):Controller(seed,side),arm_(arm),knobs_(controllerKnobs(arm,params)){}
void S3Controller::prepare(const Observation& o){
  prepared_.clear();diagnostic_.clear();std::vector<const ObservedUnit*> units;std::set<UnitId> live;
  for(const auto& u:o.units)if(u.hp>0){units.push_back(&u);live.insert(u.id);}
  std::sort(units.begin(),units.end(),[](auto a,auto b){return a->id<b->id;});
  for(auto it=memory_.begin();it!=memory_.end();)if(!live.count(it->first))it=memory_.erase(it);else ++it;
  const double q=std::exp(-o.dt/2);std::set<UnitId> bad;
  std::vector<ModelUnit> own;
  for(auto p:units){const auto& u=*p;auto found=memory_.find(u.id);if(found==memory_.end()){Memory m;m.lastOut=u.dealtToEnemy;m.lastIn=u.takenFromEnemy;if(u.team==side_&&arm_==Arm::Resonator)m.state=2*pi*random_();found=memory_.emplace(u.id,m).first;}
    auto& m=found->second;if(m.target&&!live.count(m.target))m.target=0;
    if(!(o.dt>0)||!std::isfinite(o.dt)||!(u.maxhp>0)||!std::isfinite(u.maxhp)||!finite(m)||!std::isfinite(u.dealtToEnemy)||!std::isfinite(u.takenFromEnemy)||u.dealtToEnemy<m.lastOut||u.takenFromEnemy<m.lastIn)bad.insert(u.id);
    else{m.zOut=q*m.zOut+(1-q)*(u.dealtToEnemy-m.lastOut)/o.dt/u.maxhp;m.zIn=q*m.zIn+(1-q)*(u.takenFromEnemy-m.lastIn)/o.dt/u.maxhp;m.lastOut=u.dealtToEnemy;m.lastIn=u.takenFromEnemy;if(!finite(m))bad.insert(u.id);}
    if(u.team==side_)own.push_back({u.x/100,u.y/100,m.state,u.role==ObservedRole::Melee?knobs_.rateM:knobs_.rateR,knobs_.kappa*(m.zIn-knobs_.beta*m.zOut),u.id,m.target});}
  model_=own;auto next=arm_==Arm::PushPull?own:frozenStep(own,arm_,knobs_,o.dt,substeps_);
  for(size_t i=0;i<next.size();++i){auto& m=memory_.at(next[i].id);if(!std::isfinite(next[i].state))bad.insert(next[i].id);else m.state=next[i].state;}
  const auto motion=allyRhs(next,0,.8,.01,arm_,true);
  // All group scores continue to use the previous assignments held in next.
  for(size_t i=0;i<next.size();++i){const auto id=next[i].id;const auto p=*std::find_if(units.begin(),units.end(),[&](auto u){return u->id==id;});const auto& self=*p;auto& m=memory_.at(id);
    UnitDecision d{self.x,self.y,0,0,0};double vx=0,vy=0;const double c=arm_==Arm::Resonator?std::cos(m.state):arm_==Arm::Morale?m.state:1;
    vx=motion[i].x;vy=motion[i].y;
    std::vector<const ObservedUnit*> enemies;for(auto u:units)if(u->team!=side_)enemies.push_back(u);
    std::sort(enemies.begin(),enemies.end(),[&](auto a,auto b){double ra=std::hypot(a->x-self.x,a->y-self.y),rb=std::hypot(b->x-self.x,b->y-self.y);return ra<rb||(ra==rb&&a->id<b->id);});
    const double preferred=knobs_.f*self.range/100*(1+(arm_==Arm::PushPull?0:knobs_.w)*(1-c)/2);
    for(size_t e=0;e<std::min(size_t(8),enemies.size());++e){auto u=enemies[e];double dx=(u->x-self.x)/100,dy=(u->y-self.y)/100,r=std::hypot(dx,dy);if(r==0)continue;
      double rho=r-(self.role==ObservedRole::Artillery?0:(self.radius+u->radius)/100);double term=knobs_.G*(1-preferred/std::max(rho,.01))/std::min(size_t(8),enemies.size());vx+=dx/r*term;vy+=dy/r*term;}
    double best=-INFINITY,old=-INFINITY;UnitId target=0;for(auto u:enemies){double r=std::hypot(u->x-self.x,u->y-self.y),gap=r-self.radius-u->radius;
      bool legal=self.role==ObservedRole::Artillery?r>=self.minRange&&r<=self.range:gap<=self.range;if(!legal)continue;
      double score;if(arm_==Arm::PushPull)score=-r/100;else{auto g=aggregate(next,i,u->id,arm_);double a=!g.valid?0:arm_==Arm::Resonator?std::cos(m.state-g.value):1-std::abs(m.state-g.value);auto& em=memory_.at(u->id);score=a+knobs_.gamma*std::tanh(knobs_.kappa*(em.zIn-knobs_.beta*em.zOut));if(bad.count(u->id))bad.insert(id);}
      if(!std::isfinite(score)){bad.insert(id);continue;}if(score>best||(score==best&&u->id<target)){best=score;target=u->id;}if(u->id==m.target)old=score;}
    if(std::isfinite(old)&&best-old<.2)target=m.target;d.target=target;
    const double speed=std::hypot(vx,vy);if(!enemies.empty()&&speed>=1e-9){d.x=self.x+200*vx/speed;d.y=self.y+200*vy/speed;d.multiplier=std::min(1.0,speed);}
    if(!std::isfinite(speed)||!std::isfinite(d.x)||!std::isfinite(d.y)||!std::isfinite(d.multiplier)||!std::isfinite(c)||bad.count(id))d={self.x,self.y,0,0,0,true};
    prepared_[id]=d;diagnostic_.push_back({id,d.target,self.x,self.y,m.state,c,m.zOut,m.zIn});
  }
  for(const auto& entry:prepared_)memory_.at(entry.first).target=entry.second.target;
}
UnitDecision S3Controller::decide(const Observation&,UnitId id){auto it=prepared_.find(id);if(it==prepared_.end())throw std::invalid_argument("controller self absent from prepared snapshot");return it->second;}
} // namespace astelia::control
