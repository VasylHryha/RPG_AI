#pragma once
#include "schema.h"
namespace net_slice {
struct Law {double A=.5,B=.5,J=.5,K=1,omega=0,share=.125;};
using Graph=std::vector<std::vector<size_t>>;
Graph graph(const std::vector<astelia::Vec2>&,const std::vector<astelia::UnitId>&);
std::vector<double> phaseStep(const std::vector<double>&,const std::vector<astelia::Vec2>&,const std::vector<astelia::UnitId>&,const Law&,const std::vector<double>&,double,const std::string&,const Graph* fixed=nullptr);
std::vector<astelia::Vec2> motion(const std::vector<double>&,const std::vector<astelia::Vec2>&,const std::vector<astelia::UnitId>&,const Law&,const std::vector<double>&,const std::string&);
struct Weights {std::string kind;std::map<std::string,std::vector<double>> values;explicit Weights(js::V);std::vector<double> linear(const std::string&,const std::vector<double>&)const;Law law()const;};
struct Forward {std::vector<double> logits,memory;};
Forward forward(const Weights&,const std::vector<double>&,const std::vector<double>& state={},const std::vector<double>& message={});
}
