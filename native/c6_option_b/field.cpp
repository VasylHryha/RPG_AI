// Option B: unchanged scalar R4 evaluator plus exact typed trajectory cache.
#include <cstdint>
#include <algorithm>
#include <cmath>
#include <complex>
#include <vector>
#include <list>
#include <cstring>
#include <climits>
#include <limits>
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
 Workspace(int ns,int n,const int* adj):forcing(ns),phasors(n),saturated(ns),vx(n),vy(n),vt(n),neighbors(ns){
   for(int a=0;a<ns;a++)for(int b=0;b<ns;b++)if(adj[a*ns+b])neighbors[a].push_back(b);
 }
};
static void drive(int ns,double t,const double* psi,double amplitude,C* forcing){
 const double nu[8]={-.7,-.5,-.3,-.1,.1,.3,.5,.7};
 std::fill(forcing,forcing+ns,C(0.));
 for(int a=0;a<ns;a++)for(int m=0;m<8;m++)
   forcing[a]+=amplitude/8.*std::polar(1.,(.2+nu[m])*t+psi[a*8+m]);
}
struct DrivePath {
 int ns,steps;double start,dt,amplitude;
 std::vector<double> psi;std::vector<C> values;
};
static thread_local std::list<DrivePath> drive_cache;
static thread_local size_t drive_bytes=0;
static thread_local size_t drive_limit=32*1024*1024;
static bool same_bits(const double* a,const double* b,size_t n) {
 return std::memcmp(a,b,n*sizeof(double))==0;
}
static const C* drive_path(int ns,int steps,double start,double dt,const double* psi,double amplitude){
 auto& cache=drive_cache;
 const size_t size=size_t(3)*steps*ns*sizeof(C), bytes=size+size_t(ns)*8*sizeof(double);
 if(bytes>drive_limit||steps==0)return nullptr;
 for(auto it=cache.begin();it!=cache.end();++it)
   if(it->ns==ns&&it->steps==steps&&same_bits(&it->start,&start,1)&&same_bits(&it->dt,&dt,1)&&same_bits(&it->amplitude,&amplitude,1)&&
      same_bits(it->psi.data(),psi,size_t(ns)*8)){
     cache.splice(cache.begin(),cache,it);return cache.front().values.data();
   }
 while(!cache.empty()&&(drive_bytes+bytes>drive_limit||cache.size()>=4)) {
   drive_bytes-=cache.back().values.capacity()*sizeof(C)+cache.back().psi.capacity()*sizeof(double);cache.pop_back();
 }
 DrivePath path{ns,steps,start,dt,amplitude,std::vector<double>(psi,psi+ns*8),std::vector<C>(size_t(3)*steps*ns)};
 for(int step=0;step<steps;step++){
   double t=start+step*dt;
   drive(ns,t,psi,amplitude,path.values.data()+size_t(3*step)*ns);
   drive(ns,t+.5*dt,psi,amplitude,path.values.data()+size_t(3*step+1)*ns);
   drive(ns,t+dt,psi,amplitude,path.values.data()+size_t(3*step+2)*ns);
 }
 cache.push_front(std::move(path));drive_bytes+=bytes;
 return cache.front().values.data();
}
// params: mu,D,drive,output,incoming,eps,sigma,J,K; site drive has eight tones.
static int evaluate(int ns,int n,int nc,const double* y,const double* q,
 const double* omega,const double* rates,const double* masks,const int* modes,
 const double* origins,const double* p,double* out,Workspace& work,const C* forcing){
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
 medium(y,out);
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
   // Antisymmetric pair contributions use the same ascending neighbor order.
   for(int i=0;i<n;i++)for(int j=i+1;j<n;j++){
     double dx=x[2*j]-x[2*i],dy=x[2*j+1]-x[2*i+1];
     double s=std::sqrt(dx*dx+dy*dy+p[5]*p[5]);
     double phase=th[j]-th[i];double force=(1.+J*std::cos(phase))/s-1./(s*s);
     double fx=dx*force/(n-1),fy=dy*force/(n-1);vx[i]+=fx;vy[i]+=fy;vx[j]-=fx;vy[j]-=fy;
     double wx=weights[2*j]-weights[2*i],wy=weights[2*j+1]-weights[2*i+1];
     double coupling=K*std::exp(-wx*wx-wy*wy)*std::sin(phase)/(n-1);vt[i]+=coupling;vt[j]-=coupling;
   }
   for(int i=0;i<n;i++){
     C g=0.;double denom=0.;
     for(int a=0;a<ns;a++){
       double dx=q[2*a]-weights[2*i],dy=q[2*a+1]-weights[2*i+1];
       double w=std::exp(-(dx*dx+dy*dy)/(2*p[6]*p[6]));
       g+=w*saturated[a];denom+=w;
       // Use the fixed selected-member inventory for normalization, then mask.
       if(selected){double ax=q[2*a]-x[2*i],ay=q[2*a+1]-x[2*i+1];
         double ow=mode==2?std::exp(-(ax*ax+ay*ay)/(2*p[6]*p[6])):w;
         C emission=p[3]/selected*ow*phasors[i]*std::max(0.,masks[c*n+i]);
         put(out,a,get(out,a)+emission);
       }
     }
     if(!(denom>1e-12))return 2;
     dv[2*i]=vx[i];dv[2*i+1]=vy[i];dv[2*n+i]=rates[c*n+i]+vt[i]+p[4]*std::imag(g/denom*std::conj(phasors[i]));
   }
 }
 for(int i=0;i<count;i++)if(!std::isfinite(out[i]))return 1;
 return 0;
}
static bool valid_dimensions(int ns,int n,int nc) {
 if(ns<1||n<3||nc<0)return false;
 const uint64_t stride=3ULL*n+2ULL*ns;
 return stride<=INT_MAX && 2ULL*ns+uint64_t(nc)*stride<=INT_MAX &&
        8ULL*ns<=INT_MAX && uint64_t(ns)*ns<=INT_MAX && uint64_t(n)*nc<=INT_MAX;
}
extern "C" int field_rhs(int ns,int n,int nc,double t,const double* y,const double* q,
 const double* omega,const double* psi,const int* adj,const double* rates,
 const double* masks,const int* modes,const double* origins,const double* p,double* out){
 try {
   if(!valid_dimensions(ns,n,nc)||!std::isfinite(t)||!y||!q||!omega||!psi||!adj||!p||!out||
      (nc&&(!rates||!masks||!modes||!origins)))return 3;
   Workspace work(ns,n,adj);drive(ns,t,psi,p[2],work.forcing.data());
   return evaluate(ns,n,nc,y,q,omega,rates,masks,modes,origins,p,out,work,work.forcing.data());
 } catch(...) {return -1;}
}
static int field_run_uncached(int ns,int n,int nc,double start,double dt,int steps,int sample,
 const double* initial,const double* q,const double* omega,const double* psi,const int* adj,
 const double* rates,const double* masks,const int* modes,const double* origins,const double* p,double* frames){
 const int size=2*ns+nc*(3*n+2*ns);
 std::vector<double> y(initial,initial+size),tmp(size),a(size),b(size),c(size),d(size);
 std::copy(y.begin(),y.end(),frames);int frame=1;
 Workspace work(ns,n,adj);const C* cached=drive_path(ns,steps,start,dt,psi,p[2]);
 auto rhs=[&](int step,int stage,double t,const double* z,double* result){
   const C* forcing=cached?cached+size_t(3*step+stage)*ns:work.forcing.data();
   if(!cached)drive(ns,t,psi,p[2],work.forcing.data());
   return evaluate(ns,n,nc,z,q,omega,rates,masks,modes,origins,p,result,work,forcing);
 };
 for(int step=0;step<steps;step++){
   double t=start+step*dt;int err=rhs(step,0,t,y.data(),a.data());if(err)return err;
   for(int i=0;i<size;i++)tmp[i]=y[i]+.5*dt*a[i];
   err=rhs(step,1,t+.5*dt,tmp.data(),b.data());if(err)return err;
   for(int i=0;i<size;i++)tmp[i]=y[i]+.5*dt*b[i];
   err=rhs(step,1,t+.5*dt,tmp.data(),c.data());if(err)return err;
   for(int i=0;i<size;i++)tmp[i]=y[i]+dt*c[i];
   err=rhs(step,2,t+dt,tmp.data(),d.data());if(err)return err;
   for(int i=0;i<size;i++){y[i]+=dt/6.*(a[i]+2*b[i]+2*c[i]+d[i]);if(!std::isfinite(y[i]))return 1;}
   if((step+1)%sample==0){std::copy(y.begin(),y.end(),frames+size_t(frame)*size);frame++;}
 }
 return 0;
}

// Full-state memoization of independent OFF material/carrier components.
// Every input participates in a bitwise key; no digest collision is possible.
// Actual medium is recomputed live on a hit, using its unchanged all-OFF law.
namespace {
struct Trajectory {
 std::vector<unsigned char> key;
 std::vector<double> material;
 size_t bytes() const {return key.capacity()+material.capacity()*sizeof(double);}
};
struct Memo {
 std::list<Trajectory> retired, controls;
 std::list<std::vector<unsigned char>> probation;
 size_t retired_bytes=0, control_bytes=0, probation_bytes=0;
 uint64_t retired_hits=0, control_hits=0, misses=0, avoided_steps=0;
};
static thread_local Memo memo;
static thread_local size_t retired_limit=256*1024*1024, control_limit=32*1024*1024;
static thread_local size_t probation_limit=2*1024*1024;
template<class T> void append(std::vector<unsigned char>& key,const T* p,size_t n) {
 const auto* bytes=reinterpret_cast<const unsigned char*>(p);
 key.insert(key.end(),bytes,bytes+n*sizeof(T));
}
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
 // Recompute actual medium live; key only the independent material input.
 append(key,initial+2*ns,nc*(3*n+2*ns));append(key,q,2*ns);
 append(key,omega,ns);append(key,psi,ns*8);append(key,adj,size_t(ns)*ns);
 append(key,rates,n*nc);append(key,masks,n*nc);append(key,modes,nc);
 append(key,origins,2*n*nc);append(key,p,9);
 return key;
}
void store(std::list<Trajectory>& cache,size_t& bytes,size_t limit,Trajectory&& entry) {
 if(entry.bytes()>limit)return;
 cache.push_front(std::move(entry));bytes+=cache.front().bytes();
 while(bytes>limit||cache.size()>128){bytes-=cache.back().bytes();cache.pop_back();}
}
bool repeated(const std::vector<unsigned char>& key) {
 auto found=std::find(memo.probation.begin(),memo.probation.end(),key);
 if(found!=memo.probation.end()) {
   memo.probation.splice(memo.probation.begin(),memo.probation,found);return true;
 }
 if(key.size()>probation_limit)return false;
 memo.probation.push_front(key);memo.probation_bytes+=key.size();
 while(memo.probation.size()>128||memo.probation_bytes>probation_limit) {
   memo.probation_bytes-=memo.probation.back().size();memo.probation.pop_back();
 }
 return false;
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
   bool eligible=nc==1, retired=false;
   if(eligible)for(int i=0;i<n;i++) {
     if(masks[i]>0.)eligible=false;
     retired=retired||masks[i]<0.;
   }
   if(!eligible)return field_run_uncached(ns,n,nc,start,dt,steps,sample,initial,q,omega,psi,adj,rates,masks,modes,origins,p,frames);
   auto key=physical_key(ns,n,nc,start,dt,steps,sample,initial,q,omega,psi,adj,rates,masks,modes,origins,p);
   auto& cache=retired?memo.retired:memo.controls;
   auto found=std::find_if(cache.begin(),cache.end(),[&](const Trajectory& path){return path.key==key;});
   const int count=steps/sample+1, stride=3*n+2*ns, width=2*ns+stride;
   if(found!=cache.end()) {
     std::vector<double> actual(size_t(count)*2*ns);
     int code=field_run_uncached(ns,n,0,start,dt,steps,sample,initial,q,omega,psi,adj,rates,masks,modes,origins,p,actual.data());
     if(code)return code;
     for(int f=0;f<count;f++) {
       std::copy_n(actual.data()+size_t(f)*2*ns,2*ns,frames+size_t(f)*width);
       std::copy_n(found->material.data()+size_t(f)*stride,stride,frames+size_t(f)*width+2*ns);
     }
     cache.splice(cache.begin(),cache,found);
     if(retired)memo.retired_hits++;else memo.control_hits++;
     memo.avoided_steps+=steps;
     return 0;
   }
   memo.misses++;
   bool admit=retired||repeated(key);
   int code=field_run_uncached(ns,n,nc,start,dt,steps,sample,initial,q,omega,psi,adj,rates,masks,modes,origins,p,frames);
   const size_t entry_bytes=key.capacity()+size_t(count)*stride*sizeof(double);
   const size_t limit=retired?retired_limit:control_limit;
   if(code||!admit||entry_bytes>limit)return code;
   auto& bytes=retired?memo.retired_bytes:memo.control_bytes;
   // Evict before allocating the new retained payload, including entry overhead cap.
   while(!cache.empty()&&(bytes+entry_bytes>limit||cache.size()>=128)) {
     bytes-=cache.back().bytes();cache.pop_back();
   }
   Trajectory entry{std::move(key),std::vector<double>(size_t(count)*stride)};
   for(int f=0;f<count;f++)std::copy_n(frames+size_t(f)*width+2*ns,stride,entry.material.data()+size_t(f)*stride);
   if(retired)store(memo.retired,memo.retired_bytes,retired_limit,std::move(entry));
   else store(memo.controls,memo.control_bytes,control_limit,std::move(entry));
   return 0;
 } catch(...) {return -1;}
}
extern "C" void option_b_cache_clear() {memo=Memo{};drive_cache.clear();drive_bytes=0;}
// Per-thread engineering limits. Zero disables admission; no effect on arithmetic.
extern "C" void option_b_cache_limits(uint64_t retired,uint64_t control,uint64_t probation,uint64_t drive) {
 option_b_cache_clear();
 retired_limit=std::min<uint64_t>(retired,256*1024*1024);
 control_limit=std::min<uint64_t>(control,32*1024*1024);
 probation_limit=std::min<uint64_t>(probation,2*1024*1024);
 drive_limit=std::min<uint64_t>(drive,32*1024*1024);
}
extern "C" void option_b_cache_stats(uint64_t* out) {
 out[0]=memo.retired_hits;out[1]=memo.control_hits;out[2]=memo.misses;
 out[3]=memo.avoided_steps;out[4]=memo.retired_bytes;out[5]=memo.control_bytes;out[6]=memo.probation_bytes;out[7]=drive_bytes;
}
