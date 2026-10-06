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
bool finite(const Memory& m){return std::isfinite(m.state)&&std::isfinite(m.zOut)&&std::isfinite(m.zIn)&&std::isfinite(m.lastOut)&&std::isfinite(m.lastIn)&&std::isfinite(m.zInAnswered)&&std::isfinite(m.zInUnanswered);}
std::vector<ModelUnit> shifted(const std::vector<ModelUnit>& a,const std::vector<Derivative>& d,double h,bool positions){auto out=a;for(size_t i=0;i<a.size();++i){if(positions){out[i].x+=h*d[i].x;out[i].y+=h*d[i].y;}out[i].state+=h*d[i].state;}return out;}
}
Knobs controllerKnobs(Arm arm,const ControllerParams& params,const std::string& skeleton){
  Knobs k;if(arm==Arm::Morale)k.rateM=k.rateR=1;
  struct Bound {double* value;double lo,hi;};
  std::map<std::string,Bound> bounds{{"G",{&k.G,0,5}},{"f",{&k.f,.3,1.2}}};
  if(arm!=Arm::PushPull){bounds.insert({{"K",{&k.K,0,5}},{"K_t",{&k.Kt,0,5}},{"kappa",{&k.kappa,0,50}},{"beta",{&k.beta,0,3}},{"w",{&k.w,0,3}},{"gamma",{&k.gamma,0,2}}});
    if(arm==Arm::Resonator){bounds["omega_melee"]={&k.rateM,-2,2};bounds["omega_ranged"]={&k.rateR,-2,2};}
    else{bounds["lambda_melee"]={&k.rateM,0,2};bounds["lambda_ranged"]={&k.rateR,0,2};}}
  if(skeleton=="v2"||skeleton=="v3"||skeleton=="v5"||skeleton=="v4"||skeleton=="H"||skeleton=="F"||skeleton=="HF"){
    bounds.erase("f");bounds.erase("gamma");
    bounds["f_c"]={&k.fc,.3,1};bounds["m_k"]={&k.mk,.2,1};
    if(arm!=Arm::PushPull)bounds["lambda_th"]={&k.lambdaTh,0,3};else k.lambdaTh=0;
  }
  for(const auto& p:params){auto b=bounds.find(p.first);if(b==bounds.end()||!std::isfinite(p.second)||p.second<b->second.lo||p.second>b->second.hi)throw std::invalid_argument("invalid controller param: "+p.first);*b->second.value=p.second;}
  return k;
}
bool v2Legal(const ObservedUnit& source,const ObservedUnit& target){
  const double r=std::hypot(target.x-source.x,target.y-source.y);
  return source.role==ObservedRole::Artillery?r>=source.minRange&&r<=source.range:r<=source.range+source.radius+target.radius;
}
bool v2Threat(const ObservedUnit& self,const ObservedUnit& enemy,double zOut){return enemy.hp>0&&enemy.team!=self.team&&zOut>0&&v2Legal(enemy,self);}
double v2Preferred(const ObservedUnit& self,const ObservedUnit& enemy,const Knobs& k,double c){
  const double own=(self.range+(self.role==ObservedRole::Artillery?0:self.radius+enemy.radius))/100;
  const double opposing=(enemy.range+(enemy.role==ObservedRole::Artillery?0:self.radius+enemy.radius))/100;
  double committed=opposing<own?opposing+k.mk*(own-opposing):k.fc*own;
  // Q3 explicitly specifies this committed-distance override for own artillery.
  if(self.role==ObservedRole::Artillery)committed=std::max(k.fc*own,1.05*self.minRange/100);
  return opposing<own?committed+k.w*(own-opposing)*(1-c)/2:committed+(opposing+k.w*own-committed)*(1-c)/2;
}
double v3Preferred(const ObservedUnit& self,const ObservedUnit& enemy,const Knobs& k,double c,PairModes& modes){
  const double own=(self.range+(self.role==ObservedRole::Artillery?0:self.radius+enemy.radius))/100;
  const double opposing=(enemy.range+(enemy.role==ObservedRole::Artillery?0:self.radius+enemy.radius))/100;
  if(opposing<own)return v2Preferred(self,enemy,k,c); // unchanged kite band
  auto entry=modes.emplace(std::make_pair(self.id,enemy.id),c>=0).first;
  if(c>.2)entry->second=true;else if(c<-.2)entry->second=false;
  const double committed=self.role==ObservedRole::Artillery?std::max(k.fc*own,1.05*self.minRange/100):k.fc*own;
  return entry->second?committed:opposing+k.w*own;
}
Feasibility v4Feasibility(const DecisionDiagnostic& d,double mx,double my){
  const double rho=std::hypot(d.dx,d.dy),displacement=std::hypot(mx,my);
  if(!d.reference)return {0,"no_reference"};
  if(rho<1e-9)return {0,"coincident"};
  if(std::abs(rho-d.preferred)<=1e-6)return {0,"at_distance"};
  if(displacement<1e-9)return {0,"zero_displacement"};
  return {std::max(-1.0,std::min(1.0,(mx*d.dx+my*d.dy)/(displacement*rho)*(rho>d.preferred?1:-1))),""};
}
double v4Preferred(const ObservedUnit& self,const ObservedUnit& enemy,const Knobs& k,double c,PairModes& modes,PairHolds& holds,double now,std::vector<HoldEvent>& events){
  const double own=(self.range+(self.role==ObservedRole::Artillery?0:self.radius+enemy.radius))/100;
  const double opposing=(enemy.range+(enemy.role==ObservedRole::Artillery?0:self.radius+enemy.radius))/100;
  if(opposing<own)return v2Preferred(self,enemy,k,c);
  const double committed=self.role==ObservedRole::Artillery?std::max(k.fc*own,1.05*self.minRange/100):k.fc*own;
  const double escaped=opposing+k.w*own;
  const auto key=std::make_pair(self.id,enemy.id);
  auto inserted=modes.emplace(key,c>=0);auto& mode=inserted.first->second;
  if(inserted.second)return mode?committed:escaped; // first mode has no hold
  auto held=holds.find(key);
  if(held!=holds.end()){
    const double rho=std::hypot(enemy.x-self.x,enemy.y-self.y)/100;
    const bool early=std::abs(rho-(mode?committed:escaped))<=.1*own;
    if(self.speed>1&&now<held->second.until&&!early)return mode?committed:escaped;
    events.push_back({self.id,enemy.id,self.speed<=1?"immobile":early&&now<held->second.until?"target_band":"expired",now-held->second.started,held->second.until-held->second.started});
    holds.erase(held);
  }
  const bool next=c>.2?true:c<-.2?false:mode;
  if(next!=mode){mode=next;
    if(self.speed>1){const double duration=100*std::abs(escaped-committed)/self.speed;
      if(duration>0){holds[key]={now,now+duration};events.push_back({self.id,enemy.id,"started",0,duration});}}
  }
  return mode?committed:escaped;
}
std::vector<const ObservedUnit*> v2EnemySet(const ObservedUnit& self,const std::vector<const ObservedUnit*>& nearest,const std::map<UnitId,Memory>& memory){
  auto selected=nearest;if(selected.size()>8)selected.resize(8);
  std::vector<const ObservedUnit*> extra;
  for(auto u:nearest)if(v2Threat(self,*u,memory.at(u->id).zOut)&&std::find(selected.begin(),selected.end(),u)==selected.end())extra.push_back(u);
  std::sort(extra.begin(),extra.end(),[&](auto a,auto b){
    const double za=memory.at(a->id).zOut,zb=memory.at(b->id).zOut;
    if(za!=zb)return za>zb;
    const double ra=std::hypot(a->x-self.x,a->y-self.y),rb=std::hypot(b->x-self.x,b->y-self.y);
    return ra<rb||(ra==rb&&a->id<b->id);
  });
  for(auto u:extra){if(selected.size()==16)break;selected.push_back(u);}return selected;
}
std::array<double,2> v2EnemyMotion(const ObservedUnit& self,const std::vector<const ObservedUnit*>& enemies,const std::map<UnitId,Memory>& memory,const Knobs& k,double c){
  std::array<double,2> motion{};double total=0;
  for(auto u:enemies)total+=1+k.lambdaTh*std::tanh(memory.at(u->id).zOut*1.0); // fixed 1 s
  for(auto u:enemies){const double dx=(u->x-self.x)/100,dy=(u->y-self.y)/100,r=std::hypot(dx,dy);if(r==0)continue;
    const double weight=1+k.lambdaTh*std::tanh(memory.at(u->id).zOut*1.0);
    const double term=k.G*(1-v2Preferred(self,*u,k,c)/std::max(r,.01))*weight/total;
    motion[0]+=dx/r*term;motion[1]+=dy/r*term;
  }return motion;
}
std::array<double,2> v3EnemyMotion(const ObservedUnit& self,const std::vector<const ObservedUnit*>& enemies,const std::map<UnitId,Memory>& memory,const Knobs& k,double c,PairModes& modes){
  std::array<double,2> motion{};double total=0;
  for(auto u:enemies)total+=1+k.lambdaTh*std::tanh(memory.at(u->id).zOut*1.0);
  for(auto u:enemies){const double dx=(u->x-self.x)/100,dy=(u->y-self.y)/100,r=std::hypot(dx,dy);if(r==0)continue;
    const double weight=1+k.lambdaTh*std::tanh(memory.at(u->id).zOut*1.0);
    const double term=k.G*(1-v3Preferred(self,*u,k,c,modes)/std::max(r,.01))*weight/total;
    motion[0]+=dx/r*term;motion[1]+=dy/r*term;
  }return motion;
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

S3Controller::S3Controller(double seed,uint8_t side,Arm arm,const ControllerParams& params,const std::string& skeleton):Controller(seed,side),arm_(arm),knobs_(controllerKnobs(arm,params,skeleton)),v1_(skeleton!="v0"),v2_(skeleton=="v2"||skeleton=="v3"||skeleton=="v5"||skeleton=="v4"||skeleton=="H"||skeleton=="F"||skeleton=="HF"),v3_(v2_&&skeleton!="v2"),v4_(v3_&&skeleton!="v3"&&skeleton!="v5"),holdEnabled_(skeleton=="v4"||skeleton=="H"||skeleton=="HF"),focusEnabled_(skeleton=="v4"||skeleton=="F"||skeleton=="HF"){if(skeleton!="v0"&&skeleton!="v1"&&skeleton!="v2"&&skeleton!="v3"&&skeleton!="v5"&&skeleton!="v4"&&skeleton!="H"&&skeleton!="F"&&skeleton!="HF")throw std::invalid_argument("invalid skeleton");}
void S3Controller::prepare(const Observation& o){
  prepared_.clear();diagnostic_.clear();decisionDiagnostic_.clear();holdEvents_.clear();focus_.clear();std::vector<const ObservedUnit*> units;std::set<UnitId> live;
  for(const auto& u:o.units)if(u.hp>0){units.push_back(&u);live.insert(u.id);}
  std::sort(units.begin(),units.end(),[](auto a,auto b){return a->id<b->id;});
  for(auto it=memory_.begin();it!=memory_.end();)if(!live.count(it->first))it=memory_.erase(it);else ++it;
  for(auto it=pairModes_.begin();it!=pairModes_.end();)if(!live.count(it->first.first)||!live.count(it->first.second))it=pairModes_.erase(it);else ++it;
  for(auto it=pairHolds_.begin();it!=pairHolds_.end();)if(!live.count(it->first.first)||!live.count(it->first.second)){
    holdEvents_.push_back({it->first.first,it->first.second,"disappeared",o.t-it->second.started,it->second.until-it->second.started});it=pairHolds_.erase(it);
  }else ++it;
  const double q=std::exp(-o.dt/2);std::set<UnitId> bad;
  std::vector<ModelUnit> own;
  for(auto p:units){const auto& u=*p;auto found=memory_.find(u.id);if(found==memory_.end()){Memory m;m.lastOut=u.dealtToEnemy;m.lastIn=u.takenFromEnemy;if(u.team==side_&&arm_==Arm::Resonator)m.state=2*pi*random_();found=memory_.emplace(u.id,m).first;}
    auto& m=found->second;if(m.target&&!live.count(m.target))m.target=0;
    if(!(o.dt>0)||!std::isfinite(o.dt)||!(u.maxhp>0)||!std::isfinite(u.maxhp)||!finite(m)||!std::isfinite(u.dealtToEnemy)||!std::isfinite(u.takenFromEnemy)||u.dealtToEnemy<m.lastOut||u.takenFromEnemy<m.lastIn)bad.insert(u.id);
    else{m.zOut=q*m.zOut+(1-q)*(u.dealtToEnemy-m.lastOut)/o.dt/u.maxhp;m.zIn=q*m.zIn+(1-q)*(u.takenFromEnemy-m.lastIn)/o.dt/u.maxhp;// Consume tick k damage using legality retained at prepare(k), never current geometry.
      if(v1_&&arm_!=Arm::PushPull&&u.team==side_){
        const double incoming=(1-q)*(u.takenFromEnemy-m.lastIn)/o.dt/u.maxhp;
        const bool answered=v2_?!m.hadUnansweredThreat:m.hadLegalTarget;
        m.zInAnswered=q*m.zInAnswered+(answered?incoming:0);
        m.zInUnanswered=q*m.zInUnanswered+(answered?0:incoming);
      }
      m.lastOut=u.dealtToEnemy;m.lastIn=u.takenFromEnemy;if(!finite(m))bad.insert(u.id);}
    if(u.team==side_)own.push_back({u.x/100,u.y/100,m.state,u.role==ObservedRole::Melee?knobs_.rateM:knobs_.rateR,knobs_.kappa*(v1_&&arm_!=Arm::PushPull?m.zInAnswered-knobs_.beta*m.zOut-m.zInUnanswered:m.zIn-knobs_.beta*m.zOut),u.id,m.target});}
  model_=own;auto next=arm_==Arm::PushPull?own:frozenStep(own,arm_,knobs_,o.dt,substeps_);
  for(size_t i=0;i<next.size();++i){auto& m=memory_.at(next[i].id);if(!std::isfinite(next[i].state))bad.insert(next[i].id);else m.state=next[i].state;}
  const auto motion=allyRhs(next,0,.8,.01,arm_,true);
  // All group scores continue to use the previous assignments held in next.
  for(size_t i=0;i<next.size();++i){const auto id=next[i].id;const auto p=*std::find_if(units.begin(),units.end(),[&](auto u){return u->id==id;});const auto& self=*p;auto& m=memory_.at(id);
    UnitDecision d{self.x,self.y,0,0,0};double vx=0,vy=0;const double c=arm_==Arm::Resonator?std::cos(m.state):arm_==Arm::Morale?m.state:1;
    vx=motion[i].x;vy=motion[i].y;
    std::vector<const ObservedUnit*> enemies;for(auto u:units)if(u->team!=side_)enemies.push_back(u);
    std::sort(enemies.begin(),enemies.end(),[&](auto a,auto b){double ra=std::hypot(a->x-self.x,a->y-self.y),rb=std::hypot(b->x-self.x,b->y-self.y);return ra<rb||(ra==rb&&a->id<b->id);});
    if(v2_){auto selected=v2EnemySet(self,enemies,memory_);
      // Update all living pairs, even while excluded from the movement cap, so a threshold crossing is retained.
      if(v4_){
        DecisionDiagnostic diagnostic;diagnostic.id=id;diagnostic.x=self.x;diagnostic.y=self.y;diagnostic.c=c;
        std::map<UnitId,double> distances;
        const ObservedUnit* focus=nullptr;double focusWeight=-1;
        for(auto enemy:enemies){
          const double preferred=holdEnabled_?v4Preferred(self,*enemy,knobs_,c,pairModes_,pairHolds_,o.t,holdEvents_):v3Preferred(self,*enemy,knobs_,c,pairModes_);distances[enemy->id]=preferred;
          const auto key=std::make_pair(id,enemy->id);auto mode=pairModes_.find(key);
          if(mode!=pairModes_.end()&&self.range+(self.role==ObservedRole::Artillery?0:self.radius+enemy->radius)<=enemy->range+(enemy->role==ObservedRole::Artillery?0:self.radius+enemy->radius)){
            auto h=pairHolds_.find(key);diagnostic.pairs.push_back({enemy->id,mode->second,h==pairHolds_.end()?0:std::max(0.0,h->second.until-o.t),100*preferred});
            const double weight=1+knobs_.lambdaTh*std::tanh(memory_.at(enemy->id).zOut);
            if(focusEnabled_&&mode->second&&(weight>focusWeight||(weight==focusWeight&&(!focus||enemy->id<focus->id)))){focus=enemy;focusWeight=weight;}
          }
        }
        // Section 15 selects among all committed out-ranged pairs. The fallback uses E_i unchanged.
        if(focus){selected={focus};diagnostic.focus=focus->id;focus_[id]=focus->id;}
        const ObservedUnit* reference=focus;double mainWeight=-1,total=0;
        for(auto enemy:selected){const double weight=1+knobs_.lambdaTh*std::tanh(memory_.at(enemy->id).zOut);total+=weight;
          if(!focus&&(weight>mainWeight||(weight==mainWeight&&(!reference||enemy->id<reference->id)))){reference=enemy;mainWeight=weight;}}
        const bool inheritedSum=!focusEnabled_||(!holdEnabled_&&!focus);double enemyX=0,enemyY=0;
        for(auto enemy:selected){const double dx=(enemy->x-self.x)/100,dy=(enemy->y-self.y)/100,r=std::hypot(dx,dy);if(r==0)continue;
          const double weight=1+knobs_.lambdaTh*std::tanh(memory_.at(enemy->id).zOut);
          const double term=knobs_.G*(1-distances.at(enemy->id)/std::max(r,.01))*weight/total;if(inheritedSum){enemyX+=dx/r*term;enemyY+=dy/r*term;}else{vx+=dx/r*term;vy+=dy/r*term;}
        }
        if(inheritedSum){vx+=enemyX;vy+=enemyY;}
        if(reference){diagnostic.reference=reference->id;diagnostic.dx=reference->x-self.x;diagnostic.dy=reference->y-self.y;diagnostic.preferred=100*distances.at(reference->id);}
        decisionDiagnostic_.push_back(std::move(diagnostic));
      }else{
        if(v3_)for(auto enemy:enemies)v3Preferred(self,*enemy,knobs_,c,pairModes_);
        const auto enemyMotion=v3_?v3EnemyMotion(self,selected,memory_,knobs_,c,pairModes_):v2EnemyMotion(self,selected,memory_,knobs_,c);vx+=enemyMotion[0];vy+=enemyMotion[1];
        if(v3_&&attributionDiagnostics_){
          // Read-only diagnostics after the unchanged v3 policy. Never add a focus or hold.
          DecisionDiagnostic d;d.id=id;d.x=self.x;d.y=self.y;d.c=c;
          const ObservedUnit* reference=nullptr;double bestWeight=-1;
          for(auto enemy:selected){const double weight=1+knobs_.lambdaTh*std::tanh(memory_.at(enemy->id).zOut);
            if(weight>bestWeight||(weight==bestWeight&&(!reference||enemy->id<reference->id))){reference=enemy;bestWeight=weight;}}
          const auto preferred=[&](const ObservedUnit& enemy){
            const double own=(self.range+(self.role==ObservedRole::Artillery?0:self.radius+enemy.radius))/100;
            const double opposing=(enemy.range+(enemy.role==ObservedRole::Artillery?0:self.radius+enemy.radius))/100;
            if(opposing<own)return v2Preferred(self,enemy,knobs_,c);
            const double committed=self.role==ObservedRole::Artillery?std::max(knobs_.fc*own,1.05*self.minRange/100):knobs_.fc*own;
            return pairModes_.at({id,enemy.id})?committed:opposing+knobs_.w*own;
          };
          for(auto enemy:enemies){auto mode=pairModes_.find({id,enemy->id});if(mode!=pairModes_.end())d.pairs.push_back({enemy->id,mode->second,0,100*preferred(*enemy)});}
          if(reference){d.reference=reference->id;d.dx=reference->x-self.x;d.dy=reference->y-self.y;d.preferred=100*preferred(*reference);}
          decisionDiagnostic_.push_back(std::move(d));
        }
      }}
    else{const double preferred=knobs_.f*self.range/100*(1+(arm_==Arm::PushPull?0:knobs_.w)*(1-c)/2);
    for(size_t e=0;e<std::min(size_t(8),enemies.size());++e){auto u=enemies[e];double dx=(u->x-self.x)/100,dy=(u->y-self.y)/100,r=std::hypot(dx,dy);if(r==0)continue;
      double rho=r-(self.role==ObservedRole::Artillery?0:(self.radius+u->radius)/100);double term=knobs_.G*(1-preferred/std::max(rho,.01))/std::min(size_t(8),enemies.size());vx+=dx/r*term;vy+=dy/r*term;}}
    double best=-INFINITY,old=-INFINITY;UnitId target=0;bool hasLegalTarget=false;for(auto u:enemies){double r=std::hypot(u->x-self.x,u->y-self.y),gap=r-self.radius-u->radius;
      bool legal=v2_?v2Legal(self,*u):self.role==ObservedRole::Artillery?r>=self.minRange&&r<=self.range:gap<=self.range;if(!legal)continue;hasLegalTarget=true;
      double score;if(arm_==Arm::PushPull)score=-r/100;else{auto g=aggregate(next,i,u->id,arm_);double a=!g.valid?0:arm_==Arm::Resonator?std::cos(m.state-g.value):1-std::abs(m.state-g.value);auto& em=memory_.at(u->id);score=a+knobs_.gamma*std::tanh(knobs_.kappa*(v1_?em.zIn+em.zOut:em.zIn-knobs_.beta*em.zOut));if(bad.count(u->id))bad.insert(id);}
      if(!std::isfinite(score)){bad.insert(id);continue;}if(score>best||(score==best&&u->id<target)){best=score;target=u->id;}if(u->id==m.target)old=score;}
    if(v2_){m.hadUnansweredThreat=false;for(auto u:enemies)if(v2Threat(self,*u,memory_.at(u->id).zOut)&&!v2Legal(self,*u)){m.hadUnansweredThreat=true;break;}}
    m.hadLegalTarget=hasLegalTarget; // snapshot status for the next counter increment; clone-owned memory
    if(std::isfinite(old)&&best-old<.2)target=m.target;d.target=target;
    const double speed=std::hypot(vx,vy);if(!enemies.empty()&&speed>=1e-9){d.x=self.x+200*vx/speed;d.y=self.y+200*vy/speed;d.multiplier=std::min(1.0,speed);}
    if(!std::isfinite(speed)||!std::isfinite(d.x)||!std::isfinite(d.y)||!std::isfinite(d.multiplier)||!std::isfinite(c)||bad.count(id))d={self.x,self.y,0,0,0,true};
    prepared_[id]=d;diagnostic_.push_back({id,d.target,self.x,self.y,m.state,c,m.zOut,m.zIn});
  }
  for(const auto& entry:prepared_)memory_.at(entry.first).target=entry.second.target;
}
UnitDecision S3Controller::decide(const Observation&,UnitId id){auto it=prepared_.find(id);if(it==prepared_.end())throw std::invalid_argument("controller self absent from prepared snapshot");return it->second;}
} // namespace astelia::control
