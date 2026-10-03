#include <algorithm>
#include <cmath>
#include <complex>
#include <vector>
#include <list>
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
static const C* drive_path(int ns,int steps,double start,double dt,const double* psi,double amplitude){
 static thread_local std::list<DrivePath> cache;
 const size_t limit=32*1024*1024, size=size_t(3)*steps*ns*sizeof(C);
 if(size+size_t(ns)*8*sizeof(double)>limit)return nullptr;
 for(auto it=cache.begin();it!=cache.end();++it)
   if(it->ns==ns&&it->steps==steps&&it->start==start&&it->dt==dt&&it->amplitude==amplitude&&
      std::equal(it->psi.begin(),it->psi.end(),psi)){
     cache.splice(cache.begin(),cache,it);return cache.front().values.data();
   }
 DrivePath path{ns,steps,start,dt,amplitude,std::vector<double>(psi,psi+ns*8),std::vector<C>(size_t(3)*steps*ns)};
 for(int step=0;step<steps;step++){
   double t=start+step*dt;
   drive(ns,t,psi,amplitude,path.values.data()+size_t(3*step)*ns);
   drive(ns,t+.5*dt,psi,amplitude,path.values.data()+size_t(3*step+1)*ns);
   drive(ns,t+dt,psi,amplitude,path.values.data()+size_t(3*step+2)*ns);
 }
 cache.push_front(std::move(path));size_t bytes=0;
 for(const auto& entry:cache)bytes+=entry.values.size()*sizeof(C)+entry.psi.size()*sizeof(double);
 while(cache.size()>1&&(bytes>limit||cache.size()>4)){
   bytes-=cache.back().values.size()*sizeof(C)+cache.back().psi.size()*sizeof(double);cache.pop_back();
 }
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
extern "C" int field_rhs(int ns,int n,int nc,double t,const double* y,const double* q,
 const double* omega,const double* psi,const int* adj,const double* rates,
 const double* masks,const int* modes,const double* origins,const double* p,double* out){
 Workspace work(ns,n,adj);drive(ns,t,psi,p[2],work.forcing.data());
 return evaluate(ns,n,nc,y,q,omega,rates,masks,modes,origins,p,out,work,work.forcing.data());
}
extern "C" int field_run(int ns,int n,int nc,double start,double dt,int steps,int sample,
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
   if((step+1)%sample==0){std::copy(y.begin(),y.end(),frames+frame*size);frame++;}
 }
 return 0;
}
