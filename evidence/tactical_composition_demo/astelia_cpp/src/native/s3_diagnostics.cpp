#include "s3_diagnostics.h"
#include <algorithm>
#include <cmath>
#include <map>
namespace astelia::control {
namespace {
std::vector<std::vector<size_t>> components(const std::vector<std::vector<bool>>& graph){
  std::vector<bool> visited(graph.size());std::vector<std::vector<size_t>> out;
  for(size_t i=0;i<graph.size();++i)if(!visited[i]){std::vector<size_t> stack{i},group;visited[i]=true;while(!stack.empty()){auto u=stack.back();stack.pop_back();group.push_back(u);for(size_t j=0;j<graph.size();++j)if(graph[u][j]&&!visited[j]){visited[j]=true;stack.push_back(j);}}out.push_back(group);}return out;
}
const DiagnosticUnit* find(const DiagnosticFrame& f,UnitId id){for(const auto& u:f.units)if(u.id==id)return &u;return nullptr;}
}
void DiagnosticHistory::append(double t,const std::vector<DiagnosticUnit>& u){frames_.push_back({t,u});while(!frames_.empty()&&frames_.front().t<t-3-1e-9)frames_.pop_front();}
GroupDiagnostics DiagnosticHistory::summarize(bool phases) const{
  GroupDiagnostics d;d.phases=phases;if(frames_.empty())return d;const auto& last=frames_.back();const auto& units=last.units;
  d.windowReady=last.t-frames_.front().t>=3-1e-9;
  std::map<UnitId,std::vector<const DiagnosticUnit*>> targets;for(const auto& u:units)if(u.target)targets[u.target].push_back(&u);
  for(const auto& g:targets)if(!units.empty())d.concentration=std::max(d.concentration,double(g.second.size())/units.size());
  if(!phases)return d;
  double x=0,y=0;bool finite=true;for(const auto& u:units){finite&=std::isfinite(u.state);x+=std::cos(u.state);y+=std::sin(u.state);}
  if(!units.empty()&&finite){d.coherence=std::hypot(x,y)/units.size();d.coherenceValid=true;}
  std::vector<double> means;for(const auto& g:targets){x=y=0;for(auto u:g.second){x+=std::cos(u->state);y+=std::sin(u->state);}if(std::isfinite(x)&&std::isfinite(y)&&std::hypot(x,y)>=.1*g.second.size())means.push_back(std::atan2(y,x));}
  std::vector<std::vector<bool>> graph(means.size(),std::vector<bool>(means.size()));for(size_t i=0;i<means.size();++i)for(size_t j=0;j<i;++j){double delta=means[i]-means[j];graph[i][j]=graph[j][i]=std::abs(std::atan2(std::sin(delta),std::cos(delta)))<=.3;}
  d.distinct=components(graph).size();if(!d.windowReady)return d;
  graph.assign(units.size(),std::vector<bool>(units.size()));for(size_t i=0;i<units.size();++i)for(size_t j=0;j<i;++j){if(std::hypot(units[i].x-units[j].x,units[i].y-units[j].y)>150)continue;x=y=0;bool present=true;
    for(const auto& frame:frames_){auto a=find(frame,units[i].id),b=find(frame,units[j].id);if(!a||!b||!std::isfinite(a->state)||!std::isfinite(b->state)){present=false;break;}double diff=a->state-b->state;x+=std::cos(diff);y+=std::sin(diff);}
    if(present){double resultant=std::min(1.0,std::hypot(x,y)/frames_.size());double stddev=std::sqrt(std::max(0.0,-2*std::log(std::max(resultant,1e-300))));graph[i][j]=graph[j][i]=stddev<=.2;}}
  for(const auto& c:components(graph))if(c.size()>=2){std::vector<UnitId> ids;for(auto i:c)ids.push_back(units[i].id);std::sort(ids.begin(),ids.end());d.candidates.push_back(ids);}std::sort(d.candidates.begin(),d.candidates.end());return d;
}
} // namespace astelia::control
