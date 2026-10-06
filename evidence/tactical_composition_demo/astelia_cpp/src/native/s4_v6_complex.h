#pragma once
// Versioned section-18.2 numerical kernel. No dependency on the combat world.
#include <complex>
#include <cstdint>
#include <string>
#include <vector>
namespace astelia::control::v6 {
using Complex = std::complex<double>;
constexpr double nu = 1.0, delta = .2, pressureLimit = 6000;
struct Unit {
  uint32_t id=0, target=0;
  double x=0,y=0,omega=0,pressure=0;
  Complex z{};
};
struct Rates {double mu=0,K=0,Kt=0;};
using Edges = std::vector<std::vector<std::pair<size_t,double>>>;
struct Group {Complex mean{};bool valid=false;};
struct Tick {
  bool accepted=false;
  std::string reason;
  unsigned n=0,retries=0;
  double Z=0,maxStageAmplitude=0;
  // Failed trials always return the tick-start joint state, never a partial step.
  std::vector<Unit> units;
};
bool finite(Complex);
double amplitude(Complex);
double similarity(Complex,Complex);
double commitment(Complex);
double alignment(Complex,const Group&);
Group group(const std::vector<Unit>&,size_t,uint32_t);
Edges topology(const std::vector<Unit>&);
std::vector<Complex> rhs(const std::vector<Unit>&,const Rates&,const Edges&);
double tickBound(const std::vector<Unit>&,const Rates&);
double lipschitz(const std::vector<Unit>&,const Rates&,double Z);
// Shared trial engine; explicit bound allows synthetic retry boundary fixtures.
// Production callers must use step(), which always derives Z at tick start.
Tick trials(const std::vector<Unit>&,const Rates&,double dt,double Z);
Tick step(const std::vector<Unit>&,const Rates&,double dt);
}
