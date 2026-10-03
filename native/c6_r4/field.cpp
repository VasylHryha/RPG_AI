#include <algorithm>
#include <cmath>
#include <complex>
#include <vector>
using C=std::complex<double>;
static C get(const double* a,int i){return C(a[2*i],a[2*i+1]);}
static void put(double* a,int i,C v){a[2*i]=v.real();a[2*i+1]=v.imag();}
// params: mu,D,drive,output,incoming,eps,sigma,J,K; site drive has eight tones.
extern "C" int field_rhs(int ns,int n,int nc,double t,const double* y,const double* q,
 const double* omega,const double* psi,const int* adj,const double* rates,
 const double* masks,const int* modes,const double* origins,const double* p,double* out){
 const int stride=3*n+2*ns, count=2*ns+nc*stride;
 std::fill(out,out+count,0.);
 auto medium=[&](const double* z,double* dz){
   const double nu[8]={-.7,-.5,-.3,-.1,.1,.3,.5,.7};
   for(int a=0;a<ns;a++){
     C v=get(z,a);double s=std::norm(v);C r=C(p[0]+s-s*s,omega[a])*v;
     for(int b=0;b<ns;b++) if(adj[a*ns+b]) r+=p[1]/4.*(get(z,b)-v);
     for(int m=0;m<8;m++)r+=p[2]/8.*std::polar(1.,(.2+nu[m])*t+psi[a*8+m]);
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
   for(int i=0;i<n;i++){
     double vx=0.,vy=0.,vt=0.;
     const double* weights=mode==2?origins+2*n*c:x;
     for(int j=0;j<n;j++)if(j!=i){
       double dx=x[2*j]-x[2*i],dy=x[2*j+1]-x[2*i+1];
       double s=std::sqrt(dx*dx+dy*dy+p[5]*p[5]);
       double phase=th[j]-th[i];double force=(1.+J*std::cos(phase))/s-1./(s*s);
       vx+=dx*force/(n-1);vy+=dy*force/(n-1);
       double wx=weights[2*j]-weights[2*i],wy=weights[2*j+1]-weights[2*i+1];
       vt+=K*std::exp(-wx*wx-wy*wy)*std::sin(phase)/(n-1);
     }
     C g=0.;double denom=0.;
     for(int a=0;a<ns;a++){
       double dx=q[2*a]-weights[2*i],dy=q[2*a+1]-weights[2*i+1];
       double w=std::exp(-(dx*dx+dy*dy)/(2*p[6]*p[6]));C za=get(z,a);
       g+=w*za/std::sqrt(1.+std::norm(za));denom+=w;
       // Use the fixed selected-member inventory for normalization, then mask.
       if(selected){double ax=q[2*a]-x[2*i],ay=q[2*a+1]-x[2*i+1];
         double ow=std::exp(-(ax*ax+ay*ay)/(2*p[6]*p[6]));
         C emission=p[3]/selected*ow*std::polar(1.,th[i])*std::max(0.,masks[c*n+i]);
         put(out,a,get(out,a)+emission);
       }
     }
     if(!(denom>1e-12))return 2;
     dv[2*i]=vx;dv[2*i+1]=vy;dv[2*n+i]=rates[c*n+i]+p[4]*std::imag(g/denom*std::polar(1.,-th[i]));
   }
 }
 for(int i=0;i<count;i++)if(!std::isfinite(out[i]))return 1;
 return 0;
}
extern "C" int field_run(int ns,int n,int nc,double start,double dt,int steps,int sample,
 const double* initial,const double* q,const double* omega,const double* psi,const int* adj,
 const double* rates,const double* masks,const int* modes,const double* origins,const double* p,double* frames){
 const int size=2*ns+nc*(3*n+2*ns);
 std::vector<double> y(initial,initial+size),tmp(size),a(size),b(size),c(size),d(size);
 std::copy(y.begin(),y.end(),frames);int frame=1;
 auto rhs=[&](double t,const double* z,double* result){return field_rhs(ns,n,nc,t,z,q,omega,psi,adj,rates,masks,modes,origins,p,result);};
 for(int step=0;step<steps;step++){
   double t=start+step*dt;int err=rhs(t,y.data(),a.data());if(err)return err;
   for(int i=0;i<size;i++)tmp[i]=y[i]+.5*dt*a[i];
   err=rhs(t+.5*dt,tmp.data(),b.data());if(err)return err;
   for(int i=0;i<size;i++)tmp[i]=y[i]+.5*dt*b[i];
   err=rhs(t+.5*dt,tmp.data(),c.data());if(err)return err;
   for(int i=0;i<size;i++)tmp[i]=y[i]+dt*c[i];
   err=rhs(t+dt,tmp.data(),d.data());if(err)return err;
   for(int i=0;i<size;i++){y[i]+=dt/6.*(a[i]+2*b[i]+2*c[i]+d[i]);if(!std::isfinite(y[i]))return 1;}
   if((step+1)%sample==0){std::copy(y.begin(),y.end(),frames+frame*size);frame++;}
 }
 return 0;
}
