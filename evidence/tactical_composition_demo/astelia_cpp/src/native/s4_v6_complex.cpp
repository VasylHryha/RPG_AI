#include "s4_v6_complex.h"
#include <algorithm>
#include <cmath>
#include <stdexcept>
namespace astelia::control::v6 {
namespace {
void requireFinite(double x){if(!std::isfinite(x))throw std::runtime_error("non_finite");}
void requireFinite(Complex z){if(!finite(z))throw std::runtime_error("non_finite");}
void check(const std::vector<Unit>& a,const Rates& k,double dt){
  requireFinite(dt);requireFinite(k.mu);requireFinite(k.K);requireFinite(k.Kt);
  if(dt<=0||k.mu< -2||k.mu>2||k.K<0||k.K>5||k.Kt<0||k.Kt>5)throw std::runtime_error("invalid_envelope");
  for(const auto& u:a){requireFinite(u.x);requireFinite(u.y);requireFinite(u.omega);requireFinite(u.pressure);amplitude(u.z);
    if(std::abs(u.omega)>2)throw std::runtime_error("invalid_envelope");
    if(std::abs(u.pressure)>pressureLimit)throw std::runtime_error("pressure_envelope");}
}
struct BoundExceeded {};
void monitor(const std::vector<Unit>& a,double Z,double& maximum){
  for(const auto& u:a){const double r=amplitude(u.z);maximum=std::max(maximum,r);if(r>Z)throw BoundExceeded{};}
}
std::vector<Unit> shift(const std::vector<Unit>& a,const std::vector<Complex>& d,double h){
  auto b=a;for(size_t i=0;i<a.size();++i){b[i].z+=h*d[i];requireFinite(b[i].z);}return b;
}
}
bool finite(Complex z){return std::isfinite(z.real())&&std::isfinite(z.imag());}
double amplitude(Complex z){requireFinite(z);const double r=std::abs(z);requireFinite(r);return r;}
double similarity(Complex a,Complex b){
  const double product=amplitude(a)*amplitude(b);requireFinite(product);
  const Complex cross=a*std::conj(b);requireFinite(cross);
  const double s=cross.real()/std::max(product,delta*delta);requireFinite(s);return s;
}
double commitment(Complex z){requireFinite(z);return std::max(-1.0,std::min(1.0,z.real()));}
double alignment(Complex z,const Group& g){
  requireFinite(z);if(!g.valid)return 0;
  const double a=1-amplitude(z-g.mean);requireFinite(a);return std::max(-1.0,a);
}
Group group(const std::vector<Unit>& a,size_t i,uint32_t target){
  if(!target)return {};Complex sum{};size_t count=0;
  for(size_t j=0;j<a.size();++j)if(j!=i&&a[j].target==target){requireFinite(a[j].z);sum+=a[j].z;requireFinite(sum);++count;}
  if(!count)return {};const Complex mean=sum/double(count);requireFinite(mean);return {mean,true};
}
Edges topology(const std::vector<Unit>& a){
  Edges edges(a.size());
  for(size_t i=0;i<a.size();++i){std::vector<std::pair<double,size_t>> ns;
    for(size_t j=0;j<a.size();++j)if(j!=i){const double r=std::hypot(a[j].x-a[i].x,a[j].y-a[i].y);requireFinite(r);if(r<3)ns.push_back({r,j});}
    std::sort(ns.begin(),ns.end(),[&](auto p,auto q){return p.first<q.first||(p.first==q.first&&a[p.second].id<a[q.second].id);});
    if(ns.size()>8)ns.resize(8);
    for(auto p:ns)edges[i].push_back({p.second,std::exp(-p.first*p.first)});
  }return edges;
}
std::vector<Complex> rhs(const std::vector<Unit>& a,const Rates& k,const Edges& edges){
  if(edges.size()!=a.size())throw std::runtime_error("invalid_topology");
  std::vector<Complex> d(a.size());
  for(size_t i=0;i<a.size();++i){const auto& u=a[i];const double r=amplitude(u.z),square=r*r;requireFinite(square);
    const Complex cubic=nu*square*u.z;requireFinite(cubic);
    d[i]=Complex(k.mu,u.omega)*u.z-cubic-u.pressure;requireFinite(d[i]);
    auto g=group(a,i,u.target);if(g.valid){d[i]+=k.Kt*(g.mean-u.z);requireFinite(d[i]);}
    for(auto edge:edges[i]){if(edge.first>=a.size())throw std::runtime_error("invalid_topology");requireFinite(edge.second);
      const Complex term=k.K*edge.second*(a[edge.first].z-u.z)/double(edges[i].size());requireFinite(term);d[i]+=term;requireFinite(d[i]);}
  }return d;
}
double tickBound(const std::vector<Unit>& a,const Rates& k){
  double r=0,p=0;for(const auto& u:a){r=std::max(r,amplitude(u.z));requireFinite(u.pressure);p=std::max(p,std::abs(u.pressure));}
  const double Z=std::max(r,std::cbrt(p/nu)+std::sqrt(std::max(k.mu,0.0)/nu))+1;requireFinite(Z);return Z;
}
double lipschitz(const std::vector<Unit>& a,const Rates& k,double Z){
  double omega=0;for(const auto& u:a){requireFinite(u.omega);omega=std::max(omega,std::abs(u.omega));}
  const double L=std::abs(k.mu)+omega+3*nu*Z*Z+k.K+k.Kt;requireFinite(L);return L;
}
Tick trials(const std::vector<Unit>& start,const Rates& k,double dt,double Z){
  Tick result;result.units=start;result.Z=Z;
  try{
    check(start,k,dt);requireFinite(Z);if(Z<=0)throw std::runtime_error("invalid_bound");
    const auto edges=topology(start);
    for(unsigned attempt=0;attempt<2;++attempt){
      result.Z=Z;const double n=std::max(1.0,std::ceil(dt*lipschitz(start,k,Z)));
      // Check before converting to an integer; huge finite states cannot wrap n.
      if(n>64){result.reason="substep_cap";return result;}result.n=unsigned(n);
      auto a=start;const double h=dt/result.n;
      try{
        for(unsigned s=0;s<result.n;++s){
          monitor(a,Z,result.maxStageAmplitude);auto k1=rhs(a,k,edges);
          auto b=shift(a,k1,h/2);monitor(b,Z,result.maxStageAmplitude);auto k2=rhs(b,k,edges);
          b=shift(a,k2,h/2);monitor(b,Z,result.maxStageAmplitude);auto k3=rhs(b,k,edges);
          b=shift(a,k3,h);monitor(b,Z,result.maxStageAmplitude);auto k4=rhs(b,k,edges);
          for(size_t i=0;i<a.size();++i){a[i].z+=h/6*(k1[i]+2.0*k2[i]+2.0*k3[i]+k4[i]);requireFinite(a[i].z);}
          monitor(a,Z,result.maxStageAmplitude);
        }
        result.units=std::move(a);result.accepted=true;result.reason="accepted";return result;
      }catch(const BoundExceeded&){
        if(attempt==1){result.reason="retry_exhausted";return result;}
        ++result.retries;Z*=2;requireFinite(Z);
      }
    }
  }catch(const std::exception& e){result.reason=e.what();}
  return result;
}
Tick step(const std::vector<Unit>& a,const Rates& k,double dt){
  try{check(a,k,dt);return trials(a,k,dt,tickBound(a,k));}
  catch(const std::exception& e){Tick r;r.units=a;r.reason=e.what();return r;}
}
}
