// R3-owned directed adapter. Frozen C4/C6 kernels are never modified.
#include <algorithm>
#include <cmath>
#include <vector>
#include <limits>
struct Link { int j; double d; };
static std::vector<int> nearest(const double* x,int i,const double* other,int m,bool self) {
    std::vector<Link> links;
    for(int j=0;j<m;++j) if(!self || i!=j)
        links.push_back({j,std::hypot(other[2*j]-x[2*i],other[2*j+1]-x[2*i+1])});
    std::stable_sort(links.begin(),links.end(),[](const Link&a,const Link&b){return a.d<b.d;});
    std::vector<int> out;
    for(int j=0;j<std::min(8,(int)links.size());++j) if(links[j].d<3.) out.push_back(links[j].j);
    return out;
}
static void channel(const double* x,const double* th,int i,const double* y,const double* phi,
                    const std::vector<int>& ids,const double* gate,double J,double K,bool weighted,
                    double* dx,double* dth,bool geometry,bool phase) {
    if(ids.empty()) return;
    double ax=0,ay=0,at=0;
    for(int j:ids) {
        double ux=y[2*j]-x[2*i],uy=y[2*j+1]-x[2*i+1],r=std::hypot(ux,uy),rr=std::max(r,1e-6);
        double p=phi[j]-th[i],g=gate?gate[j]:1.;
        double a=(1.+J*std::cos(p)-1./rr)/rr;
        if(geometry) {ax+=g*ux*a;ay+=g*uy*a;}
        if(phase) at+=g*K*(weighted?std::exp(-r*r):1.)*std::sin(p);
    }
    double count=(double)ids.size(); // Before masking: a zero gate does not remove a neighbor.
    dx[2*i]+=ax/count; dx[2*i+1]+=ay/count; dth[i]+=at/count;
}
extern "C" int c6r3_integrate(int nb,int ns,int nd,int steps,int every,double dt,int mode,double outbound,
    const double* initial_x,const double* initial_th,const double* omega,const double* phase_origin,
    const double* reference_x,const double* reference_th,const double* prior_x,const double* prior_th,
    double* frames_x,double* frames_th) {
    const int n=nb+ns;
    if(nb<1||ns<0||nd<0||steps<0||every<1||steps%every||dt<=0||mode<0||mode>3) return -1;
    std::vector<double>x(initial_x,initial_x+2*n),th(initial_th,initial_th+n);
    std::vector<std::vector<int>> frozen_in(ns),frozen_ex(ns);
    if(mode==2) for(int i=0;i<ns;++i) {
        frozen_in[i]=nearest(phase_origin+2*nb,i,phase_origin+2*nb,ns,true);
        frozen_ex[i]=nearest(phase_origin+2*nb,i,reference_x,nb,false);
    }
    auto rhs=[&](const std::vector<double>&xx,const std::vector<double>&tt,int input,
                 const std::vector<std::vector<int>>&own,const std::vector<std::vector<int>>&ext,
                 std::vector<double>&dx,std::vector<double>&dtv) {
        dx.assign(2*n,0.);dtv.assign(omega,omega+n);
        std::vector<double>exx(2*(ns+nd)),extt(ns+nd),gates(ns+nd,1.);
        for(int j=0;j<ns;++j) {exx[2*j]=xx[2*(nb+j)];exx[2*j+1]=xx[2*(nb+j)+1];extt[j]=tt[nb+j];gates[j]=outbound;}
        for(int j=0;j<nd;++j) {exx[2*(ns+j)]=prior_x[2*(input*nd+j)];exx[2*(ns+j)+1]=prior_x[2*(input*nd+j)+1];extt[ns+j]=prior_th[input*nd+j];}
        for(int i=0;i<nb;++i) {
            channel(xx.data(),tt.data(),i,xx.data(),tt.data(),own[i],nullptr,.8,1.,true,dx.data(),dtv.data(),true,true);
            channel(xx.data(),tt.data(),i,exx.data(),extt.data(),ext[i],gates.data(),.8,1.,true,dx.data(),dtv.data(),true,true);
        }
        for(int i=0;i<ns;++i) {
            double J=(mode==1||mode==3)?0.:.8, K=mode==1?0.:1.;
            auto sx=xx.data()+2*nb;auto st=tt.data()+nb;auto vx=dx.data()+2*nb;auto vt=dtv.data()+nb;
            channel(sx,st,i,sx,st,own[nb+i],nullptr,J,K,true,vx,vt,true,mode!=2);
            channel(sx,st,i,reference_x+2*input*nb,reference_th+input*nb,ext[nb+i],nullptr,
                    (mode==1||mode==3)?0.:.8,mode==1?0.:1.,true,vx,vt,true,mode!=2);
            if(mode==2) {
                channel(sx,st,i,sx,st,frozen_in[i],nullptr,J,K,false,vx,vt,false,true);
                channel(sx,st,i,reference_x+2*input*nb,reference_th+input*nb,frozen_ex[i],nullptr,.8,1.,false,vx,vt,false,true);
            }
        }
    };
    auto save=[&](int frame) {std::copy(x.begin(),x.end(),frames_x+2*n*frame);std::copy(th.begin(),th.end(),frames_th+n*frame);};
    save(0);
    for(int step=0;step<steps;++step) {
        std::vector<std::vector<int>>own(n),ext(n);
        std::vector<double>exx(2*(ns+nd));
        for(int j=0;j<ns;++j) {exx[2*j]=x[2*(nb+j)];exx[2*j+1]=x[2*(nb+j)+1];}
        for(int j=0;j<nd;++j) {exx[2*(ns+j)]=prior_x[2*(2*step*nd+j)];exx[2*(ns+j)+1]=prior_x[2*(2*step*nd+j)+1];}
        for(int i=0;i<nb;++i) {own[i]=nearest(x.data(),i,x.data(),nb,true);ext[i]=nearest(x.data(),i,exx.data(),ns+nd,false);}
        for(int i=0;i<ns;++i) {own[nb+i]=nearest(x.data()+2*nb,i,x.data()+2*nb,ns,true);ext[nb+i]=nearest(x.data()+2*nb,i,reference_x+4*step*nb,nb,false);}
        std::vector<double>kx[4],kt[4],xx(2*n),tt(n);
        rhs(x,th,2*step,own,ext,kx[0],kt[0]);
        for(int stage=1;stage<4;++stage) {
            double factor=stage==3?dt:dt/2.;int previous=stage-1;
            for(int i=0;i<2*n;++i)xx[i]=x[i]+factor*kx[previous][i];
            for(int i=0;i<n;++i)tt[i]=th[i]+factor*kt[previous][i];
            rhs(xx,tt,2*step+(stage==3?2:1),own,ext,kx[stage],kt[stage]);
        }
        for(int i=0;i<2*n;++i) {x[i]+=dt/6.*(kx[0][i]+2*kx[1][i]+2*kx[2][i]+kx[3][i]);if(!std::isfinite(x[i]))return step+1;}
        for(int i=0;i<n;++i) {th[i]+=dt/6.*(kt[0][i]+2*kt[1][i]+2*kt[2][i]+kt[3][i]);if(!std::isfinite(th[i]))return step+1;}
        if((step+1)%every==0)save((step+1)/every);
    }
    return 0;
}
