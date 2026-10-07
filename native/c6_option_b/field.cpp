// Option B: decision 0032 vector kernel (default), selectable scalar exact kernel.
// C6_OPTION_B_INEXACT=0 retains the pre-adoption evaluator. Caches remain exact
// within a selected kernel; libraries and caches are isolated by build identity.
//
// Performance revision (evidence/c6_option_b/PERFORMANCE_DEEPDIVE_REPORT.md):
// - the evaluator forms independent arguments first, calls the same libm
//   entries back to back, then accumulates in the original order; every
//   floating-point operation keeps its operands, order and function in the
//   exact build; decision 0032 changes the vector functions/site factorization;
// - the material, actual-medium and drive caches are process-wide (shared by
//   all worker threads), single-flight and indexed by a hash of the complete
//   byte key. Equality is always a full byte comparison of the key, so no
//   digest collision can return a wrong value.
#include <cstdint>
#include <algorithm>
#include <cmath>
#include <complex>
#include <vector>
#include <list>
#include <cstring>
#include <climits>
#include <limits>
#include <memory>
#include <new>
#include <mutex>
#include <condition_variable>
#include <unordered_map>
#include <math.h>
#ifndef C6_OPTION_B_INEXACT
#define C6_OPTION_B_INEXACT 1
#endif
#if C6_OPTION_B_INEXACT
#include <Accelerate/Accelerate.h>
#endif
extern "C" int option_b_inexact_kernel(){return C6_OPTION_B_INEXACT;}
using C=std::complex<double>;
static C get(const double* a,int i){return C(a[2*i],a[2*i+1]);}
static void put(double* a,int i,C v){a[2*i]=v.real();a[2*i+1]=v.imag();}
// Workspace belongs to one integration, not each RK4 substage. Neighbor order
// and all law arithmetic are retained; cached drive values use the original
// absolute stage-time expression and never depend on state or cohort identity.
struct Workspace {
 std::vector<C> forcing,phasors,saturated;
 std::vector<double> vx,vy,vt;
 std::vector<std::vector<int>> neighbors;
 // Evaluator scratch: pair and site arguments/transcendentals, plus mode-2
 // origin Gaussians, which depend only on the fixed origins and sites.
 std::vector<double> ps,pf,pdx,pdy,psin,pcos,parg,pexp,sarg,sw,ow,fixed_w;
 std::vector<unsigned char> fixed_ready;
 Workspace(int ns,int n,const int* adj,int nc):forcing(ns),phasors(n),saturated(ns),vx(n),vy(n),vt(n),neighbors(ns),
   ps(size_t(n)*(n-1)/2),pf(ps.size()),pdx(ps.size()),pdy(ps.size()),psin(ps.size()),pcos(ps.size()),
   parg(ps.size()),pexp(ps.size()),sarg(size_t(n)*ns),sw(sarg.size()),ow(sarg.size()),
   fixed_w(size_t(nc)*n*ns),fixed_ready(size_t(nc),0){
   for(int a=0;a<ns;a++)for(int b=0;b<ns;b++)if(adj[a*ns+b])neighbors[a].push_back(b);
 }
};
static void drive(int ns,double t,const double* psi,double amplitude,C* forcing){
 const double nu[8]={-.7,-.5,-.3,-.1,.1,.3,.5,.7};
 std::fill(forcing,forcing+ns,C(0.));
 for(int a=0;a<ns;a++)for(int m=0;m<8;m++)
   forcing[a]+=amplitude/8.*std::polar(1.,(.2+nu[m])*t+psi[a*8+m]);
}

// ---------------------------------------------------------------------------
// Process-wide exact store: LRU by bytes, single flight per complete key.
namespace {
template<class T> void append(std::vector<unsigned char>& key,const T* p,size_t n) {
 const auto* bytes=reinterpret_cast<const unsigned char*>(p);
 key.insert(key.end(),bytes,bytes+n*sizeof(T));
}
uint64_t key_hash(const std::vector<unsigned char>& key) {
 uint64_t h=1469598103934665603ULL;  // FNV-1a: an index only, never equality.
 for(unsigned char b:key){h^=b;h*=1099511628211ULL;}
 return h;
}
template<class T> struct Value {
 std::vector<unsigned char> key;
 std::vector<T> data;
 bool retired=false;
 size_t bytes() const {return key.capacity()+data.capacity()*sizeof(T)+sizeof(*this);}
};
// Bytes a value with this key and payload would account for (Value::bytes()).
template<class T> size_t value_bytes(size_t key_bytes,size_t elements){
 return key_bytes+elements*sizeof(T)+sizeof(Value<T>);
}
template<class T> class Store {
public:
 using Ptr=std::shared_ptr<const Value<T>>;
 // A flight owns a copy of its key: callers may move their key afterwards.
 struct Flight {std::vector<unsigned char> key;std::mutex m;std::condition_variable cv;bool done=false;Ptr value;};
 // A leader lease always publishes (value or failure) exactly once.
 class Lease {
 public:
  Lease()=default;Lease(const Lease&)=delete;Lease& operator=(const Lease&)=delete;
  ~Lease(){if(store)store->finish(*this,nullptr);}
  void publish(Ptr value){if(store)store->finish(*this,std::move(value));}
 private:
  friend class Store;
  Store* store=nullptr;std::shared_ptr<Flight> flight;uint64_t hash=0;
 };
 // Returns a cached value, or nullptr with `lease` leading the computation.
 Ptr acquire(const std::vector<unsigned char>& key,uint64_t hash,Lease& lease) {
  std::unique_lock<std::mutex> lock(mutex);
  for(;;){
   auto range=index.equal_range(hash);
   for(auto it=range.first;it!=range.second;++it)
     if(it->second->value->key==key){
       lru.splice(lru.begin(),lru,it->second);hits++;return lru.front().value;
     }
   std::shared_ptr<Flight> flight;
   auto pending=inflight.equal_range(hash);
   for(auto it=pending.first;it!=pending.second;++it)
     if(it->second->key==key){flight=it->second;break;}
   if(!flight){
     auto lead=std::make_shared<Flight>();lead->key=key;
     inflight.emplace(hash,lead);misses++;
     lease.store=this;lease.flight=std::move(lead);lease.hash=hash;
     return nullptr;
   }
   lock.unlock();
   Ptr value;
   {std::unique_lock<std::mutex> wait(flight->m);flight->cv.wait(wait,[&]{return flight->done;});value=flight->value;}
   lock.lock();
   if(value){hits++;waits++;return value;}
   // The leader failed; retry so that exactly one thread leads again.
  }
 }
 void configure(size_t new_limit){std::lock_guard<std::mutex> lock(mutex);limit=new_limit;drop();}
 // Whether a value of this many bytes may be allocated for retention at all.
 // Callers bypass the store (no lease, no optional allocation) otherwise.
 bool admits(size_t value_bytes){std::lock_guard<std::mutex> lock(mutex);return value_bytes<=limit;}
 void clear(){std::lock_guard<std::mutex> lock(mutex);drop();hits=misses=waits=0;}
 struct Stats {uint64_t hits,misses,waits,bytes,entries,retired_bytes;};
 Stats stats(){
  std::lock_guard<std::mutex> lock(mutex);
  uint64_t retired_bytes=0;for(const auto& slot:lru)if(slot.value->retired)retired_bytes+=slot.value->bytes();
  return {hits,misses,waits,bytes,lru.size(),retired_bytes};
 }
private:
 struct Slot {Ptr value;uint64_t hash;};
 void finish(Lease& lease,Ptr value){
  lease.store=nullptr;
  {
   // Publication and deregistration are one step under the store lock: the
   // flight is complete before any later requester can miss its entry. Lock
   // order is store -> flight; followers never hold the flight lock while
   // taking the store lock.
   std::lock_guard<std::mutex> lock(mutex);
   {std::lock_guard<std::mutex> wait(lease.flight->m);lease.flight->done=true;lease.flight->value=value;}
   auto pending=inflight.equal_range(lease.hash);
   for(auto it=pending.first;it!=pending.second;++it)
     if(it->second==lease.flight){inflight.erase(it);break;}
   if(value&&value->bytes()<=limit){
     try {
       auto entry=lru.insert(lru.begin(),Slot{value,lease.hash});
       try {index.emplace(lease.hash,entry);}
       catch(...){lru.erase(entry);throw;}
       bytes+=value->bytes();
       while(bytes>limit)erase(std::prev(lru.end()));
     } catch(...) {}  // Admission is optional; the value is still returned.
   }
  }
  lease.flight->cv.notify_all();
 }
 void erase(typename std::list<Slot>::iterator entry){
  auto range=index.equal_range(entry->hash);
  for(auto it=range.first;it!=range.second;++it)if(it->second==entry){index.erase(it);break;}
  bytes-=entry->value->bytes();lru.erase(entry);
 }
 void drop(){lru.clear();index.clear();bytes=0;}
 std::mutex mutex;
 std::list<Slot> lru;
 std::unordered_multimap<uint64_t,typename std::list<Slot>::iterator> index;
 std::unordered_multimap<uint64_t,std::shared_ptr<Flight>> inflight;
 size_t limit=0,bytes=0;uint64_t hits=0,misses=0,waits=0;
};
// Engineering limits (bytes of retained keys plus payloads). Arithmetic is
// unaffected by any limit, including zero, which disables admission.
const uint64_t MATERIAL_MAX=1024ULL*1024*1024, MEDIUM_MAX=256ULL*1024*1024, DRIVE_MAX=256ULL*1024*1024;
Store<double>& material_store(){static Store<double>* s=[]{auto* p=new Store<double>;p->configure(MATERIAL_MAX);return p;}();return *s;}
Store<double>& medium_store(){static Store<double>* s=[]{auto* p=new Store<double>;p->configure(64ULL*1024*1024);return p;}();return *s;}
Store<C>& drive_store(){static Store<C>* s=[]{auto* p=new Store<C>;p->configure(128ULL*1024*1024);return p;}();return *s;}
std::mutex counter_mutex;
uint64_t avoided_material_steps=0,avoided_medium_steps=0,retired_hits=0,control_hits=0,eligible_misses=0;
// Integrated RK steps actually computed, by path (cost accounting only).
uint64_t computed_material_steps=0,computed_medium_steps=0,computed_uncached_steps=0,computed_drive_steps=0;
}

// The drive depends only on (sites, clock, horizon, amplitude, tone phases).
static std::shared_ptr<const Value<C>> drive_path(int ns,int steps,double start,double dt,const double* psi,double amplitude){
 if(steps==0)return nullptr;
 auto& store=drive_store();
 const size_t key_bytes=2*sizeof(int)+3*sizeof(double)+size_t(ns)*8*sizeof(double);
 // Disabled or oversized: no precomputed path is allocated; the integrator
 // streams the identical per-stage drive expression instead.
 if(!store.admits(value_bytes<C>(key_bytes,size_t(3)*steps*ns)))return nullptr;
 std::vector<unsigned char> key;
 key.reserve(key_bytes);
 const int dimensions[]={ns,steps};const double clock[]={start,dt,amplitude};
 append(key,dimensions,2);append(key,clock,3);append(key,psi,size_t(ns)*8);
 Store<C>::Lease lease;
 if(auto found=store.acquire(key,key_hash(key),lease))return found;
 std::shared_ptr<Value<C>> path;
 try {
   path=std::make_shared<Value<C>>();
   path->key=key;path->data.resize(size_t(3)*steps*ns);
 } catch(const std::bad_alloc&) {return nullptr;}  // Lease publishes failure; stream instead.
 for(int step=0;step<steps;step++){
   double t=start+step*dt;
   drive(ns,t,psi,amplitude,path->data.data()+size_t(3*step)*ns);
   drive(ns,t+.5*dt,psi,amplitude,path->data.data()+size_t(3*step+1)*ns);
   drive(ns,t+dt,psi,amplitude,path->data.data()+size_t(3*step+2)*ns);
 }
 lease.publish(path);
 {std::lock_guard<std::mutex> lock(counter_mutex);computed_drive_steps+=steps;}
 return path;
}

// params: mu,D,drive,output,incoming,eps,sigma,J,K; site drive has eight tones.
// Exact restructuring of the original scalar evaluator: independent arguments
// are formed first, transcendental calls run back to back, and every
// accumulation then runs in the original ascending order with the original
// operands. The original build merged each sin/cos pair into __sincos_stret;
// this file calls that entry explicitly for the same values.
// material_only: the actual-medium derivative (out[0,2ns)) is left zero and
// not evaluated. Valid only for cohorts without emission (every mask <= 0 and
// a finite output scale); otherwise the call returns 4 and callers fall back.
static int evaluate(int ns,int n,int nc,const double* y,const double* q,
 const double* omega,const double* rates,const double* masks,const int* modes,
 const double* origins,const double* p,double* out,Workspace& work,const C* forcing,bool material_only=false){
 const int stride=3*n+2*ns, count=2*ns+nc*stride;
 std::fill(out,out+count,0.);
 auto medium=[&](const double* z,double* dz){
   for(int a=0;a<ns;a++){
     C v=get(z,a);double s=std::norm(v);C r=C(p[0]+s-s*s,omega[a])*v;
     for(int b:work.neighbors[a]) r+=p[1]/4.*(get(z,b)-v);
     r+=forcing[a];
     put(dz,a,r);
   }
 };
 if(!material_only)medium(y,out);
 const int pairs=int(size_t(n)*(n-1)/2), sites=n*ns;
 double* const ps=work.ps.data();double* const pf=work.pf.data();
 double* const pdx=work.pdx.data();double* const pdy=work.pdy.data();
 double* const psin=work.psin.data();double* const pcos=work.pcos.data();
 double* const parg=work.parg.data();double* const pexp=work.pexp.data();
 double* const sarg=work.sarg.data();double* const sw=work.sw.data();double* const ow=work.ow.data();
 for(int c=0;c<nc;c++){
   const double* v=y+2*ns+c*stride;double* dv=out+2*ns+c*stride;
   const double* x=v;const double* th=v+2*n;const double* z=v+3*n;
   medium(z,dv+3*n);
   int mode=modes[c];double J=(mode==1||mode==3)?0.:p[7],K=mode==1?0.:p[8];
   int selected=0;for(int i=0;i<n;i++)if(masks[c*n+i]!=0.)selected++;
   const double* weights=mode==2?origins+2*n*c:x;
   auto& phasors=work.phasors;auto& saturated=work.saturated;
   auto& vx=work.vx;auto& vy=work.vy;auto& vt=work.vt;
   std::fill(vx.begin(),vx.end(),0.);std::fill(vy.begin(),vy.end(),0.);std::fill(vt.begin(),vt.end(),0.);
   for(int i=0;i<n;i++)phasors[i]=std::polar(1.,th[i]);
   for(int a=0;a<ns;a++){C za=get(z,a);saturated[a]=za/std::sqrt(1.+std::norm(za));}
   // Pair arguments, in the original (i ascending, j>i ascending) order.
   for(int i=0,k=0;i<n;i++)for(int j=i+1;j<n;j++,k++){
     double dx=x[2*j]-x[2*i],dy=x[2*j+1]-x[2*i+1];
     pdx[k]=dx;pdy[k]=dy;ps[k]=std::sqrt(dx*dx+dy*dy+p[5]*p[5]);
     pf[k]=th[j]-th[i];
     double wx=weights[2*j]-weights[2*i],wy=weights[2*j+1]-weights[2*i+1];
     parg[k]=-wx*wx-wy*wy;
   }
   // J==0 (modes 1, 3) or K==0 (mode 1): the original product J*cos or
   // K*exp*sin is then an exact signed zero whenever its operands are finite,
   // and adding it changes nothing (1.+(+-0.)==1.; vt stays +0.). Nonfinite
   // operands keep the original evaluation, so every error decision is kept.
   const bool need_cos=J!=0., need_coupling=K!=0.;
#if C6_OPTION_B_INEXACT
   if(need_cos||need_coupling){int count=pairs;vvsincos(psin,pcos,pf,&count);}
   if(need_coupling){int count=pairs;vvexp(pexp,parg,&count);}
#else
   if(need_cos||need_coupling)for(int k=0;k<pairs;k++)__sincos(pf[k],psin+k,pcos+k);
   if(need_coupling)for(int k=0;k<pairs;k++)pexp[k]=std::exp(parg[k]);
#endif
   for(int i=0,k=0;i<n;i++)for(int j=i+1;j<n;j++,k++){
     const double s=ps[k],phase=pf[k],dx=pdx[k],dy=pdy[k];
     double cosine=0.;
     if(need_cos)cosine=pcos[k];
     else if(!std::isfinite(phase)){double sine;__sincos(phase,&sine,&cosine);}
     double force=(1.+J*cosine)/s-1./(s*s);
     double fx=dx*force/(n-1),fy=dy*force/(n-1);vx[i]+=fx;vy[i]+=fy;vx[j]-=fx;vy[j]-=fy;
     if(need_coupling){
       double coupling=K*pexp[k]*psin[k]/(n-1);vt[i]+=coupling;vt[j]-=coupling;
     } else if(!std::isfinite(phase)||!std::isfinite(parg[k])){
       double sine,unused;__sincos(phase,&sine,&unused);
       double coupling=K*std::exp(parg[k])*sine/(n-1);vt[i]+=coupling;vt[j]-=coupling;
     }
   }
   // Site Gaussians: arguments, exponentials, then ordered accumulation.
   // Mode 2 weights use fixed origins: identical values for the whole run.
   const bool fixed=mode==2;
   double* const weight=fixed?work.fixed_w.data()+size_t(c)*sites:sw;
   if(!fixed||!work.fixed_ready[c]){
#if C6_OPTION_B_INEXACT
     // The study used fixed 64-site/64-element buffers without a guard.
     // Larger valid inputs take the scalar Gaussian path before any fixed
     // buffer access; this preserves the exact kernel's input domain.
     if(n<=64 && ns<=64){
       double ux[64],uy[64];int ix[64],iy[64],nux=0,nuy=0;
       for(int a=0;a<ns;a++){
         int u=0;while(u<nux&&ux[u]!=q[2*a])u++;
         if(u==nux)ux[nux++]=q[2*a];ix[a]=u;
         int v=0;while(v<nuy&&uy[v]!=q[2*a+1])v++;
         if(v==nuy)uy[nuy++]=q[2*a+1];iy[a]=v;
       }
       static thread_local double tx[64*64],ty[64*64],ex[64*64],ey[64*64];
       for(int i=0;i<n;i++){
         for(int u=0;u<nux;u++){double d=ux[u]-weights[2*i];tx[i*nux+u]=-(d*d)/(2*p[6]*p[6]);}
         for(int v=0;v<nuy;v++){double d=uy[v]-weights[2*i+1];ty[i*nuy+v]=-(d*d)/(2*p[6]*p[6]);}
       }
       int nx=n*nux,ny=n*nuy;vvexp(ex,tx,&nx);vvexp(ey,ty,&ny);
       for(int i=0;i<n;i++)for(int a=0;a<ns;a++)weight[i*ns+a]=ex[i*nux+ix[a]]*ey[i*nuy+iy[a]];
     }else
#endif
     {
     for(int i=0;i<n;i++)for(int a=0;a<ns;a++){
       double dx=q[2*a]-weights[2*i],dy=q[2*a+1]-weights[2*i+1];
       sarg[i*ns+a]=-(dx*dx+dy*dy)/(2*p[6]*p[6]);
     }
     for(int k=0;k<sites;k++)weight[k]=std::exp(sarg[k]);
     }
     if(fixed)work.fixed_ready[c]=1;
   }
   const double* own=weight;
   if(selected&&fixed){
     for(int i=0;i<n;i++)for(int a=0;a<ns;a++){
       double ax=q[2*a]-x[2*i],ay=q[2*a+1]-x[2*i+1];
       sarg[i*ns+a]=-(ax*ax+ay*ay)/(2*p[6]*p[6]);
     }
     for(int k=0;k<sites;k++)ow[k]=std::exp(sarg[k]);
     own=ow;
   }
   // When no member has a positive mask, every masked factor is +0., so each
   // emission term is an exact signed zero (finite output scale; weights are
   // in [0,1] and a nonfinite position or phase also makes dv nonfinite,
   // keeping error code 1). Adding a signed
   // zero leaves an accumulator unchanged unless it holds -0.; such entries
   // are replayed below with the original terms, in the original order. (The
   // medium derivative adds the forcing last and is never -0., so this guard
   // is not expected to trigger.)
   bool silent=std::isfinite(p[3]);for(int i=0;i<n;i++)if(masks[c*n+i]>0.)silent=false;
   const bool emit=selected&&!silent;
   if(material_only&&emit)return 4;
   for(int i=0;i<n;i++){
     C g=0.;double denom=0.;
     const double* wi=weight+size_t(i)*ns;const double* oi=own+size_t(i)*ns;
     for(int a=0;a<ns;a++){
       double w=wi[a];
       g+=w*saturated[a];denom+=w;
       // Use the fixed selected-member inventory for normalization, then mask.
       if(emit){
         C emission=p[3]/selected*oi[a]*phasors[i]*std::max(0.,masks[c*n+i]);
         put(out,a,get(out,a)+emission);
       }
     }
     if(!(denom>1e-12))return 2;
     dv[2*i]=vx[i];dv[2*i+1]=vy[i];dv[2*n+i]=rates[c*n+i]+vt[i]+p[4]*std::imag(g/denom*std::conj(phasors[i]));
   }
   if(selected&&silent&&!material_only)for(int a=0;a<ns;a++){
     const bool re=out[2*a]==0.&&std::signbit(out[2*a]),im=out[2*a+1]==0.&&std::signbit(out[2*a+1]);
     if(!re&&!im)continue;
     C value=get(out,a);
     for(int i=0;i<n;i++){
       C emission=p[3]/selected*own[size_t(i)*ns+a]*phasors[i]*std::max(0.,masks[c*n+i]);
       value=value+emission;
     }
     if(re)out[2*a]=value.real();
     if(im)out[2*a+1]=value.imag();
   }
 }
 for(int i=0;i<count;i++)if(!std::isfinite(out[i]))return 1;
 return 0;
}
static bool valid_dimensions(int ns,int n,int nc) {
 if(ns<1||n<3||nc<0)return false;
 const uint64_t stride=3ULL*n+2ULL*ns;
 return stride<=INT_MAX && 2ULL*ns+uint64_t(nc)*stride<=INT_MAX &&
        8ULL*ns<=INT_MAX && uint64_t(ns)*ns<=INT_MAX && uint64_t(n)*nc<=INT_MAX &&
        uint64_t(n)*(n-1)/2<=INT_MAX && uint64_t(n)*ns<=INT_MAX;
}
extern "C" int field_rhs(int ns,int n,int nc,double t,const double* y,const double* q,
 const double* omega,const double* psi,const int* adj,const double* rates,
 const double* masks,const int* modes,const double* origins,const double* p,double* out){
 try {
   if(!valid_dimensions(ns,n,nc)||!std::isfinite(t)||!y||!q||!omega||!psi||!adj||!p||!out||
      (nc&&(!rates||!masks||!modes||!origins)))return 3;
   Workspace work(ns,n,adj,nc);drive(ns,t,psi,p[2],work.forcing.data());
   return evaluate(ns,n,nc,y,q,omega,rates,masks,modes,origins,p,out,work,work.forcing.data());
 } catch(...) {return -1;}
}
// material_only integrates the cohort components only; the actual-medium
// columns of every frame keep their initial values (callers overwrite them).
static int field_run_uncached(int ns,int n,int nc,double start,double dt,int steps,int sample,
 const double* initial,const double* q,const double* omega,const double* psi,const int* adj,
 const double* rates,const double* masks,const int* modes,const double* origins,const double* p,double* frames,
 bool material_only=false,size_t out_stride=0){
 const int size=2*ns+nc*(3*n+2*ns), begin=material_only?2*ns:0;
 if(!out_stride)out_stride=size;  // Frame f starts at frames+f*out_stride.
 std::vector<double> y(initial,initial+size),tmp(size),a(size),b(size),c(size),d(size);
 std::copy(y.begin(),y.end(),frames);int frame=1;
 Workspace work(ns,n,adj,nc);
 const auto path=drive_path(ns,steps,start,dt,psi,p[2]);
 const C* cached=path?path->data.data():nullptr;
 auto rhs=[&](int step,int stage,double t,const double* z,double* result){
   const C* forcing=cached?cached+size_t(3*step+stage)*ns:work.forcing.data();
   if(!cached)drive(ns,t,psi,p[2],work.forcing.data());
   return evaluate(ns,n,nc,z,q,omega,rates,masks,modes,origins,p,result,work,forcing,material_only);
 };
 if(material_only)std::copy(y.begin(),y.begin()+begin,tmp.begin());
 for(int step=0;step<steps;step++){
   double t=start+step*dt;int err=rhs(step,0,t,y.data(),a.data());if(err)return err;
   for(int i=begin;i<size;i++)tmp[i]=y[i]+.5*dt*a[i];
   err=rhs(step,1,t+.5*dt,tmp.data(),b.data());if(err)return err;
   for(int i=begin;i<size;i++)tmp[i]=y[i]+.5*dt*b[i];
   err=rhs(step,1,t+.5*dt,tmp.data(),c.data());if(err)return err;
   for(int i=begin;i<size;i++)tmp[i]=y[i]+dt*c[i];
   err=rhs(step,2,t+dt,tmp.data(),d.data());if(err)return err;
   for(int i=begin;i<size;i++){y[i]+=dt/6.*(a[i]+2*b[i]+2*c[i]+d[i]);if(!std::isfinite(y[i]))return 1;}
   if((step+1)%sample==0){std::copy(y.begin(),y.end(),frames+size_t(frame)*out_stride);frame++;}
 }
 return 0;
}

// Full-state memoization of independent OFF material/carrier components and
// of no-cohort actual-medium runs. Every input participates in a byte key.
namespace {
std::vector<unsigned char> physical_key(int ns,int n,int nc,double start,double dt,int steps,int sample,
 const double* initial,const double* q,const double* omega,const double* psi,const int* adj,
 const double* rates,const double* masks,const int* modes,const double* origins,const double* p) {
 std::vector<unsigned char> key;
 // Reserve the complete key once; repeated vector growth copies are avoidable.
 const size_t doubles=2+size_t(nc)*(3*n+2*ns)+2*size_t(ns)+ns+8*size_t(ns)+4*size_t(n)*nc+9;
 key.reserve((5+size_t(ns)*ns+nc)*sizeof(int)+doubles*sizeof(double));
 const int dimensions[]={ns,n,nc,steps,sample};const double clock[]={start,dt};
 append(key,dimensions,5);append(key,clock,2);
 // In the OFF-only case, actual medium cannot feed material or carrier.
 // Recompute actual medium separately; key only the independent material input.
 append(key,initial+2*ns,size_t(nc)*(3*n+2*ns));append(key,q,2*size_t(ns));
 append(key,omega,ns);append(key,psi,size_t(ns)*8);append(key,adj,size_t(ns)*ns);
 append(key,rates,size_t(n)*nc);append(key,masks,size_t(n)*nc);append(key,modes,nc);
 append(key,origins,2*size_t(n)*nc);append(key,p,9);
 return key;
}
// No-cohort run: all inputs of the actual-medium law (q/n kept conservatively).
std::vector<unsigned char> medium_key(int ns,int n,double start,double dt,int steps,int sample,
 const double* initial,const double* q,const double* omega,const double* psi,const int* adj,const double* p) {
 std::vector<unsigned char> key;
 key.reserve((5+size_t(ns)*ns)*sizeof(int)+(2+2*size_t(ns)+2*size_t(ns)+ns+8*size_t(ns)+9)*sizeof(double));
 const int dimensions[]={ns,n,0,steps,sample};const double clock[]={start,dt};
 append(key,dimensions,5);append(key,clock,2);append(key,initial,2*size_t(ns));
 append(key,q,2*size_t(ns));append(key,omega,ns);append(key,psi,size_t(ns)*8);
 append(key,adj,size_t(ns)*ns);append(key,p,9);
 return key;
}
// Actual medium only (nc=0), exactly as computed by an uncached no-cohort run.
int medium_run(int ns,int n,double start,double dt,int steps,int sample,const double* initial,const double* q,
 const double* omega,const double* psi,const int* adj,const double* p,double* frames,size_t frame_stride) {
 const int count=steps/sample+1;
 auto& store=medium_store();
 const size_t key_bytes=(5+size_t(ns)*ns)*sizeof(int)+(2+2*size_t(ns)+2*size_t(ns)+ns+8*size_t(ns)+9)*sizeof(double);
 auto direct=[&]{
   // No optional trajectory: integrate straight into the caller's layout.
   int code=field_run_uncached(ns,n,0,start,dt,steps,sample,initial,q,omega,psi,adj,nullptr,nullptr,nullptr,nullptr,p,frames,false,frame_stride);
   if(!code){std::lock_guard<std::mutex> lock(counter_mutex);computed_medium_steps+=steps;}
   return code;
 };
 if(!store.admits(value_bytes<double>(key_bytes,size_t(count)*2*ns)))return direct();
 auto key=medium_key(ns,n,start,dt,steps,sample,initial,q,omega,psi,adj,p);
 std::shared_ptr<const Value<double>> found;
 {
   Store<double>::Lease lease;
   found=store.acquire(key,key_hash(key),lease);
   if(!found){
     std::shared_ptr<Value<double>> value;
     try {value=std::make_shared<Value<double>>();value->data.resize(size_t(count)*2*ns);}
     catch(const std::bad_alloc&) {value=nullptr;}
     if(!value){lease.publish(nullptr);return direct();}
     int code=field_run_uncached(ns,n,0,start,dt,steps,sample,initial,q,omega,psi,adj,nullptr,nullptr,nullptr,nullptr,p,value->data.data());
     if(code)return code;  // Lease destructor publishes failure.
     {std::lock_guard<std::mutex> lock(counter_mutex);computed_medium_steps+=steps;}
     value->key=std::move(key);
     lease.publish(value);found=value;
   } else {
     std::lock_guard<std::mutex> lock(counter_mutex);avoided_medium_steps+=steps;
   }
 }
 for(int f=0;f<count;f++)std::copy_n(found->data.data()+size_t(f)*2*ns,2*ns,frames+size_t(f)*frame_stride);
 return 0;
}
}
extern "C" int field_run(int ns,int n,int nc,double start,double dt,int steps,int sample,
 const double* initial,const double* q,const double* omega,const double* psi,const int* adj,
 const double* rates,const double* masks,const int* modes,const double* origins,const double* p,double* frames) {
 try {
   if(!valid_dimensions(ns,n,nc)||steps<0||sample<1||steps%sample||
      !std::isfinite(start)||!std::isfinite(dt)||dt<=0||!initial||!q||!omega||!psi||!adj||!p||!frames||
      (nc&&(!rates||!masks||!modes||!origins)))return 3;
   const uint64_t width64=2ULL*ns+uint64_t(nc)*(3ULL*n+2ULL*ns);
   if(uint64_t(steps/sample)+1>uint64_t(INT_MAX)||
      (uint64_t(steps/sample)+1)*width64>std::numeric_limits<size_t>::max()/sizeof(double)||
      3ULL*steps*ns>std::numeric_limits<size_t>::max()/sizeof(C))return 3;
   if(nc==0)return medium_run(ns,n,start,dt,steps,sample,initial,q,omega,psi,adj,p,frames,2*size_t(ns));
   bool eligible=nc==1, retired=false;
   if(eligible)for(int i=0;i<n;i++) {
     if(masks[i]>0.)eligible=false;
     retired=retired||masks[i]<0.;
   }
   if(!eligible){
     {std::lock_guard<std::mutex> lock(counter_mutex);computed_uncached_steps+=steps;}
     return field_run_uncached(ns,n,nc,start,dt,steps,sample,initial,q,omega,psi,adj,rates,masks,modes,origins,p,frames);
   }
   auto key=physical_key(ns,n,nc,start,dt,steps,sample,initial,q,omega,psi,adj,rates,masks,modes,origins,p);
   const int count=steps/sample+1, stride=3*n+2*ns, width=2*ns+stride;
   auto& store=material_store();Store<double>::Lease lease;
   // Disabled or oversized retention: no lookup, lease or payload copy.
   const bool cacheable=store.admits(value_bytes<double>(key.size(),size_t(count)*stride));
   std::shared_ptr<const Value<double>> found=cacheable?store.acquire(key,key_hash(key),lease):nullptr;
   if(found) {
     // The actual medium is never read from the material cache: it is the
     // separate no-cohort run (itself exactly memoized), as before.
     int code=medium_run(ns,n,start,dt,steps,sample,initial,q,omega,psi,adj,p,frames,size_t(width));
     if(code)return code;
     for(int f=0;f<count;f++)
       std::copy_n(found->data.data()+size_t(f)*stride,stride,frames+size_t(f)*width+2*ns);
     std::lock_guard<std::mutex> lock(counter_mutex);
     if(retired)retired_hits++;else control_hits++;
     avoided_material_steps+=steps;
     return 0;
   }
   {std::lock_guard<std::mutex> lock(counter_mutex);eligible_misses++;computed_material_steps+=steps;}
   // The OFF material never reads the actual medium, whose derivative here
   // receives only exact signed-zero emissions and so equals the no-cohort
   // law (as on a cache hit). Integrate the material alone and take the actual
   // medium from the shared no-cohort run. If the material fails, the original
   // inline integration decides the error code, exactly as before.
   int code;
   if(std::isfinite(p[3])&&field_run_uncached(ns,n,nc,start,dt,steps,sample,initial,q,omega,psi,adj,rates,masks,modes,origins,p,frames,true)==0)
     code=medium_run(ns,n,start,dt,steps,sample,initial,q,omega,psi,adj,p,frames,size_t(width));
   else
     code=field_run_uncached(ns,n,nc,start,dt,steps,sample,initial,q,omega,psi,adj,rates,masks,modes,origins,p,frames);
   if(code)return code;  // Lease destructor publishes failure; nothing stored.
   if(cacheable)try {
     auto value=std::make_shared<Value<double>>();
     value->data.resize(size_t(count)*stride);value->retired=retired;
     for(int f=0;f<count;f++)std::copy_n(frames+size_t(f)*width+2*ns,stride,value->data.data()+size_t(f)*stride);
     value->key=std::move(key);
     lease.publish(value);
   } catch(...) {}  // Optional admission only; frames are already complete.
   return 0;
 } catch(...) {return -1;}
}
// Clears retained values and counters (in-flight computations still publish).
extern "C" void option_b_cache_clear() {
 material_store().clear();medium_store().clear();drive_store().clear();
 std::lock_guard<std::mutex> lock(counter_mutex);
 avoided_material_steps=avoided_medium_steps=retired_hits=control_hits=eligible_misses=0;
 computed_material_steps=computed_medium_steps=computed_uncached_steps=computed_drive_steps=0;
}
// Process-wide engineering limits in bytes. Zero disables admission; no
// effect on arithmetic. Clears retained values.
extern "C" void option_b_cache_limits(uint64_t material,uint64_t medium,uint64_t drive) {
 material_store().configure(std::min<uint64_t>(material,MATERIAL_MAX));
 medium_store().configure(std::min<uint64_t>(medium,MEDIUM_MAX));
 drive_store().configure(std::min<uint64_t>(drive,DRIVE_MAX));
 option_b_cache_clear();
}
extern "C" void option_b_cache_stats(uint64_t* out) {
 auto m=material_store().stats();auto a=medium_store().stats();auto d=drive_store().stats();
 std::lock_guard<std::mutex> lock(counter_mutex);
 const uint64_t values[]={retired_hits,control_hits,eligible_misses,avoided_material_steps,
   m.retired_bytes,m.bytes-m.retired_bytes,m.entries,m.waits,
   a.hits,a.misses,avoided_medium_steps,a.bytes,a.waits,
   d.hits,d.misses,d.bytes,d.waits,
   computed_material_steps,computed_medium_steps,computed_uncached_steps,computed_drive_steps};
 std::copy(std::begin(values),std::end(values),out);
}
