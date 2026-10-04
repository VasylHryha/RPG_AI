// Bounded stage-B experiment: identical operations, inputs and observable sums.
// This measures representation/copy costs, not full simulator qualification.
#include "native/world.h"
#include <chrono>
#include <iomanip>
#include <iostream>
#include <string>

using namespace astelia;
struct Columns {
  std::vector<double> x,y,hp,radius,speed,range;
  std::vector<uint8_t> team;
  explicit Columns(const std::vector<UnitHot>& units) {
    for (const auto& u:units) {x.push_back(u.pos.x);y.push_back(u.pos.y);hp.push_back(u.hp);radius.push_back(u.radius);speed.push_back(u.speed);range.push_back(u.range);team.push_back(u.team);}
  }
};
template<class F> double measured(F&& f) {
  auto a=std::chrono::steady_clock::now();f();return std::chrono::duration<double>(std::chrono::steady_clock::now()-a).count();
}
int main() {
  auto c=std::make_shared<Config>(sandboxConfig());auto w=World::create(c);Columns cols(w.units);
  constexpr size_t loops=40000;
  auto records=[&]() {
    double sum=0;
    for (size_t k=0;k<loops;++k) for (const auto& a:w.units) for (const auto& b:w.units) {
      if (a.team==b.team) continue;
      const double x=a.pos.x-b.pos.x,y=a.pos.y-b.pos.y;
      if (x*x+y*y<(a.range+a.radius+b.radius)*(a.range+a.radius+b.radius)) sum+=b.hp;
      else sum+=(x*x+y*y)*1e-12;
    }
    return sum;
  };
  auto columns=[&]() {
    double sum=0;
    for (size_t k=0;k<loops;++k) for (size_t i=0;i<cols.x.size();++i) for (size_t j=0;j<cols.x.size();++j) {
      if (cols.team[i]==cols.team[j]) continue;
      const double x=cols.x[i]-cols.x[j],y=cols.y[i]-cols.y[j];
      if (x*x+y*y<(cols.range[i]+cols.radius[i]+cols.radius[j])*(cols.range[i]+cols.radius[i]+cols.radius[j])) sum+=cols.hp[j];
      else sum+=(x*x+y*y)*1e-12;
    }
    return sum;
  };
  struct Sample {const char* kind;double seconds,sum;};
  std::vector<Sample> samples;
  double recordTime=0,columnTime=0,expected=0;
  // Predeclared balanced order; every measurement is retained, with equal
  // operation counts. Eight measurements per representation, no fastest-pick.
  for (size_t cycle=0;cycle<4;++cycle) for (bool record:{true,false,false,true}) {
    double sum=0;
    const double seconds=measured([&](){sum=record?records():columns();});
    if (samples.empty()) expected=sum;
    else if (sum!=expected) {std::cerr<<"layout comparison changed operations\n";return 1;}
    samples.push_back({record?"records":"columns",seconds,sum});
    (record?recordTime:columnTime)+=seconds;
  }
  World copy(c);double copySum=0;
  const double copyTime=measured([&](){for (size_t i=0;i<loops;++i) {copy.copyFrom(w);copySum+=copy.units[0].pos.x;}});
  std::cout<<std::setprecision(17)<<"{\"scope\":\"native_layout_checkpoint\",\"unit_count\":"<<w.units.size()
    <<",\"iterations\":"<<loops<<",\"unit_hot_bytes\":"<<sizeof(UnitHot)<<",\"unit_state_bytes\":"<<sizeof(UnitState)
    <<",\"records_seconds\":"<<recordTime<<",\"columns_seconds\":"<<columnTime<<",\"copy_seconds\":"<<copyTime
    <<",\"records_sum\":"<<expected<<",\"columns_sum\":"<<expected<<",\"copy_sum\":"<<copySum
    <<",\"order\":\"records,columns,columns,records\",\"cycles\":4,\"samples\":[";
  for (size_t i=0;i<samples.size();++i) {
    if (i) std::cout<<',';
    const auto& s=samples[i];std::cout<<"{\"kind\":\""<<s.kind<<"\",\"seconds\":"<<s.seconds<<",\"sum\":"<<s.sum<<'}';
  }
  std::cout<<"]}\n";
}
