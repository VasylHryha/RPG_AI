// No combat, controller factory, World, RNG or engine linkage.
#include "native/s4_v6_complex.h"
#include "js_value.h"
#include <iostream>
#include <limits>
using namespace astelia::control::v6;
namespace {
void require(bool b,const char* why){if(!b)throw std::runtime_error(why);}
void close(double a,double b,double eps=1e-12){require(std::isfinite(a)&&std::abs(a-b)<=eps,"numeric fixture mismatch");}
js::V state(const std::vector<Unit>& units){js::Args rows;for(auto& u:units)rows.push_back(js::arr({u.z.real(),u.z.imag()}));return js::arr(std::move(rows));}
void contracts(){
  close(similarity({0,0},{0,0}),0);close(similarity({0,0},{1,1}),0);
  close(similarity({.1,0},{1,0}),1);close(similarity({.1,0},{.1,0}),.25);
  close(similarity({1,1},{1,1}),1);close(similarity({1,1},{-1,-1}),-1);
  close(similarity({1,0},{0,1}),0);close(similarity({.05,0},{-.1,0}),-.125);
  std::vector<Unit> a{{1,7,0,0,0,0,{.5,0}},{2,7,1,0,0,0,{1,0}},{3,7,2,0,0,0,{-1,0}}};
  auto g=group(a,0,7);require(g.valid&&g.mean==Complex{},"cancelling group must be valid");close(alignment(a[0].z,g),.5);
  require(!group(a,0,8).valid,"empty group");require(!group({a[0]},0,7).valid,"self-only group");
  g=group({a[0],a[1]},0,7);require(g.valid&&g.mean==a[1].z,"singleton group");
  close(alignment({0,0},{{0,0},true}),1);close(alignment({1,0},{{0,0},true}),0);
  close(alignment({2,0},{{0,0},true}),-1);close(alignment({10,10},{{0,0},true}),-1);
  close(commitment({20,7}),1);close(commitment({-20,-7}),-1);require(a[0].z==Complex(.5,0),"action clip changed state");
  for(double mu:{-2.0,2.0}){auto zeros=a;for(auto& u:zeros)u.z={};auto r=step(zeros,{mu,5,5},1.0/30);require(r.accepted,"zero tick");for(auto& u:r.units)require(u.z==Complex{},"zero invariance");}
  // Corrected free radial law (including mu=0), with signed phase rotation.
  for(double mu:{-2.0,0.0,2.0})for(double omega:{-2.0,0.0,2.0}){
    std::vector<Unit> freeUnits{{1,0,0,0,omega,0,{.3,.4}}};const double t=2,r0=.5;
    for(unsigned tick=0;tick<60;++tick){auto r=step(freeUnits,{mu,0,0},1.0/30);require(r.accepted,"free radial tick");freeUnits=r.units;}
    const double radius=mu==0?r0/std::sqrt(1+2*r0*r0*t):r0*std::exp(mu*t)/std::sqrt(1+r0*r0*std::expm1(2*mu*t)/mu);
    const Complex expected=radius*std::polar(1.0,std::arg(Complex(.3,.4))+omega*t);
    require(std::abs(freeUnits[0].z-expected)<1e-5,"analytic radial/rotation law");
  }
  for(double drive:{-1.0,1.0}){
    std::vector<Unit> driven{{1,0,0,0,0,drive,{}}};
    for(unsigned tick=0;tick<360;++tick){auto r=step(driven,{-1,0,0},1.0/30);require(r.accepted,"constant-drive tick");driven=r.units;}
    const double x=driven[0].z.real();require(x*drive<0&&driven[0].z.imag()==0&&std::abs(-x-x*x*x-drive)<1e-8,"unique driven real fixed point");
  }
  a[0].z={};a[0].pressure=1;auto onset=step({a[0]},{-1,0,0},1.0/30);require(onset.accepted&&onset.units[0].z.real()<0&&onset.units[0].z.imag()==0,"first pressure sign");
  a[0].pressure=0;auto excited=step({a[0],a[1]},{-1,5,0},1.0/30);require(excited.accepted&&excited.units[0].z.real()>0,"driven neighbour");
  auto birth=std::vector<Unit>{a[0],a[1]};birth[0].z=birth[1].z={};birth[1].pressure=-1;
  auto triggered=step(birth,{-1,5,0},1.0/30);require(triggered.accepted&&triggered.units[0].z.real()>0&&triggered.units[1].z.real()>0,"pressure-triggered neighbour from zero birth");
  a[0].target=7;a[1].target=7;a[1].x=10;excited=step({a[0],a[1]},{-1,0,5},1.0/30);require(excited.accepted&&excited.units[0].z.real()>0,"target-group excitation");
  auto equal=rhs({{1,0,0,0,0,0,{1,1}},{2,0,0,0,0,0,{-1,-1}}},{0,1,0},{{{1,1}},{{0,1}}});
  auto free=rhs({{1,0,0,0,0,0,{1,1}},{2,0,0,0,0,0,{-1,-1}}},{0,0,0},{{},{}});
  require(std::abs((equal[0]-free[0])-(equal[1]-free[1])+4.0*Complex(1,1))<1e-12,"diffusive-only contraction");
  Unit u{1,0,0,0,0,0,{0,0}};Rates k{};const double L=lipschitz({u},k,1);
  auto r=trials({u},k,63.5/L,1);require(r.accepted&&r.n==64,"n=64 must pass");
  r=trials({u},k,64.5/L,1);require(!r.accepted&&r.reason=="substep_cap"&&r.units[0].z==u.z,"n>64 must fail atomically");
  u.pressure=60;r=trials({u},k,1.0/30,1);require(r.accepted&&r.retries==1&&r.Z==2,"stage retry must succeed");
  auto fromStart=trials({u},k,1.0/30,2);require(r.units[0].z==fromStart.units[0].z,"retry must restart from tick-start");
  r=trials({u},k,1.0/30,.1);require(!r.accepted&&r.retries==1&&r.reason=="retry_exhausted"&&r.units[0].z==u.z,"retry exhaustion");
  u.pressure=0;u.z={7,0};r=trials({u},k,.2,6);require(!r.accepted&&r.retries==1&&r.reason=="substep_cap"&&r.units[0].z==u.z,"retry cap");
  u.z={};u.pressure=6000;r=step({u},k,1.0/30);require(r.accepted,"pressure edge admitted");
  u.pressure=6000.01;r=step({u},k,1.0/30);require(!r.accepted&&r.reason=="pressure_envelope"&&r.n==0,"pressure rejected before integration");
  for(auto z:{Complex(NAN,0),Complex(0,INFINITY),Complex(1e308,1e308)}){u.pressure=0;u.z=z;r=step({u},k,1.0/30);require(!r.accepted,"non-finite/cubic/cap fixture must fail");}
  u.z={};u.pressure=NAN;r=step({u},k,1.0/30);require(!r.accepted&&r.reason=="non_finite"&&r.units[0].z==u.z,"non-finite pressure atomicity");
  u.pressure=0;u.z={1e200,0};bool overflowRejected=false;try{rhs({u},k,{{}});}catch(...){overflowRejected=true;}require(overflowRejected,"cubic overflow rejected before clipping");
  bool rejected=false;try{similarity({NAN,0},{});}catch(...){rejected=true;}require(rejected,"similarity cannot hide NaN");
  rejected=false;try{alignment({NAN,0},{});}catch(...){rejected=true;}require(rejected,"alignment cannot hide NaN even if empty");
  a[1].z={NAN,0};rejected=false;try{group(a,0,7);}catch(...){rejected=true;}require(rejected,"non-finite group cannot be empty fallback");
  // Neighbour tie order uses id, with eight of nine equidistant neighbours.
  std::vector<Unit> ties{{1,0,0,0,0,0,{}}};for(uint32_t id=10;id>=2;--id)ties.push_back({id,0,1,0,0,0,{}});
  auto edges=topology(ties);require(edges[0].size()==8,"neighbour cap");for(size_t i=0;i<8;++i)require(ties[edges[0][i].first].id==i+2,"neighbour ties by id");
  std::cout<<"{\"status\":\"passed\",\"scope\":\"complex_kernel_only\",\"fights\":0}\n";
}
}
int main(int argc,char** argv){
  try{if(argc==2&&std::string(argv[1])=="--contracts"){contracts();return 0;}
    std::string line;while(std::getline(std::cin,line)){
      auto req=js::parse(line);std::vector<Unit> a;
      for(auto row:js::get(req,"units").p->items){auto at=[&](size_t i){return js::num(row.p->items.at(i));};
        a.push_back({uint32_t(at(0)),uint32_t(at(1)),at(2),at(3),at(4),at(5),{at(6),at(7)}});}
      Rates k{js::num(js::get(req,"mu")),js::num(js::get(req,"K")),js::num(js::get(req,"K_t"))};
      auto r=step(a,k,js::num(js::get(req,"dt")));
      std::cout<<js::stringify(js::obj({{"accepted",r.accepted},{"reason",r.reason},{"n",double(r.n)},
        {"retries",double(r.retries)},{"Z",r.Z},{"max_stage_amplitude",r.maxStageAmplitude},{"units",state(r.units)}}))<<'\n';
      js::collect({},0);
    }return 0;
  }catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}
}
