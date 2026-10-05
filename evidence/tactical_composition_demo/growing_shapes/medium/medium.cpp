#include "medium.hpp"
#include <cstring>
#include <iomanip>
#include <limits>
#include <numeric>
#include <set>
#include <sstream>
#include <stdexcept>
#include <type_traits>
namespace growing {
constexpr double pi=3.141592653589793238462643383279502884;
void require(bool b,const char* m) { if(!b) throw std::invalid_argument(m); }
void finite(double v) { require(std::isfinite(v),"non-finite parameter/state"); }
static double distance(const gm_element& a,const gm_element& b) { return std::hypot(b.x-a.x,b.y-a.y); }
static double kernel(double r,double width) { return std::exp(-0.5*(r/width)*(r/width)); }
Medium::Medium(uint64_t seed,gm_params params):p(params),rng(seed) {
    for(double v:{p.A,p.B,p.J,p.K,p.eps,p.radius,p.geometry_rate}) finite(v);
    require(p.eps>0 && p.radius>0 && p.geometry_rate>=0 && p.k>0,"invalid C4 parameters");
    require((p.distance_weighted==0 || p.distance_weighted==1) && p.window>=2 && p.min_samples>=2 && p.min_samples<=p.window,"invalid window/weight flag");
}
int Medium::index(uint64_t id) const {
    for(size_t i=0;i<elements.size();++i) if(elements[i].v.id==id) return int(i);
    throw std::invalid_argument("unknown element id");
}
double Medium::random_angle() { // SplitMix64: completely serialized, no global RNG.
    uint64_t z=(rng+=UINT64_C(0x9e3779b97f4a7c15));
    z=(z^(z>>30))*UINT64_C(0xbf58476d1ce4e5b9); z=(z^(z>>27))*UINT64_C(0x94d049bb133111eb);
    return double((z^(z>>31))>>11)*0x1.0p-53*(2*pi);
}
uint64_t Medium::add(double x,double y,double phase,double rate,const std::string& rule,std::map<std::string,double> why) {
    for(double v:{x,y,phase,rate}) finite(v);
    require(!configured || elements.size()<size_t(growth.N_max),"element cap reached");
    require(next_id<std::numeric_limits<uint64_t>::max(),"id exhausted");
    Element e; e.v={next_id++,x,y,phase,rate,time,0}; elements.push_back(e);
    events.push_back({time,rule,{e.v.id},std::move(why)}); return e.v.id;
}
void Medium::remove(uint64_t id,const std::string& rule,std::map<std::string,double> why) {
    int i=index(id); elements.erase(elements.begin()+i);
    events.push_back({time,rule,{id},std::move(why)});
}
std::vector<uint64_t> Medium::split(uint64_t id,double a,double b,double offset,const std::string& rule,std::map<std::string,double> why) {
    finite(a); finite(b); finite(offset); require(offset>0,"split offset must be positive");
    require(!configured || elements.size()<size_t(growth.N_max),"element cap reached");
    gm_element old=elements[index(id)].v; double angle=random_angle(), dx=0.5*offset*std::cos(angle),dy=0.5*offset*std::sin(angle);
    // One atomic structural event. Children have fresh identity/history/protection.
    require(next_id<std::numeric_limits<uint64_t>::max()-1,"id exhausted");
    elements.erase(elements.begin()+index(id));
    uint64_t first=next_id;
    Element e,f; e.v={next_id++,old.x-dx,old.y-dy,a,old.rate,time,0};
    f.v={next_id++,old.x+dx,old.y+dy,b,old.rate,time,0}; elements.push_back(e); elements.push_back(f);
    events.push_back({time,rule,{id,first,first+1},std::move(why)}); return {first,first+1};
}
Neighbors Medium::neighbors(bool padded) const {
    const int n=int(elements.size()), k=std::min(p.k,std::max(0,n-1)); Neighbors out(n);
    // Cell width is the radius: all r<radius candidates lie in the 3x3 stencil.
    using Cell=std::pair<int64_t,int64_t>; std::map<Cell,std::vector<int>> grid;
    auto cell=[&](const gm_element& e) {
        double x=std::floor(e.x/p.radius),y=std::floor(e.y/p.radius);
        require(std::abs(x)<double(INT64_MAX)/2 && std::abs(y)<double(INT64_MAX)/2,"position outside grid range");
        return Cell(int64_t(x),int64_t(y));
    };
    for(int i=0;i<n;++i) if(!elements[i].v.silent) grid[cell(elements[i].v)].push_back(i);
    for(int i=0;i<n;++i) {
        if(elements[i].v.silent) continue;
        auto c=cell(elements[i].v); std::vector<std::pair<double,int>> candidates;
        for(int dx=-1;dx<=1;++dx) for(int dy=-1;dy<=1;++dy) {
            auto it=grid.find({c.first+dx,c.second+dy}); if(it==grid.end()) continue;
            for(int j:it->second) if(j!=i) {
                double r=distance(elements[i].v,elements[j].v);
                if(r<p.radius) candidates.push_back({r,j});
            }
        }
        // Exact masked-padding indices are needed only by the diagnostic API.
        // If <k local candidates, complete the nearest list by scanning far points.
        if(padded && int(candidates.size())<k) for(int j=0;j<n;++j) if(j!=i && !elements[j].v.silent) {
            double r=distance(elements[i].v,elements[j].v); if(r>=p.radius) candidates.push_back({r,j});
        }
        int count=std::min(k,int(candidates.size()));
        std::partial_sort(candidates.begin(),candidates.begin()+count,candidates.end());
        for(int j=0;j<count;++j) out[i].push_back(candidates[j].second);
    }
    return out;
}
std::vector<double> Medium::rhs(const std::vector<gm_element>& s,const Neighbors& held) const {
    std::vector<double> out(3*s.size(),0);
    for(size_t i=0;i<s.size();++i) {
        if(s[i].silent) continue; double vx=0,vy=0,phase=0; const auto& e=s[i];
        for(int j:held[i]) {
            const auto& other=s[j]; double dx=other.x-e.x,dy=other.y-e.y;
            double r=std::hypot(dx,dy),rr=std::max(r,p.eps),d=other.phase-e.phase;
            double radial=(p.A*(1+p.J*std::cos(d))-p.B/rr)/rr;
            vx+=dx*radial; vy+=dy*radial;
            phase+=p.K*(p.distance_weighted?std::exp(-r*r):1)*std::sin(d);
        }
        double inv=1.0/std::max(size_t(1),held[i].size());
        out[3*i]=p.geometry_rate*vx*inv; out[3*i+1]=p.geometry_rate*vy*inv;
        out[3*i+2]=e.rate+phase*inv;
        for(const auto& d:drives) {
            double r=std::hypot(d.v.x-e.x,d.v.y-e.y);
            // Caller supplies phase at start of step; rate advances it at RK stages.
            if(r<d.v.reach) out[3*i+2]+=d.v.strength*kernel(r,d.v.width)*std::sin(d.v.phase-e.phase);
        }
    }
    return out;
}
void Medium::step(double dt) {
    finite(dt); require(dt>0,"dt must be positive"); auto held=neighbors();
    std::vector<gm_element> start; for(auto& e:elements) start.push_back(e.v);
    auto stage=[&](const std::vector<double>& v,double amount) {
        auto s=start; for(size_t i=0;i<s.size();++i) { s[i].x+=amount*v[3*i]; s[i].y+=amount*v[3*i+1]; s[i].phase+=amount*v[3*i+2]; } return s;
    };
    auto initial_drives=drives;
    auto at=[&](double amount) { for(size_t j=0;j<drives.size();++j) drives[j].v.phase=initial_drives[j].v.phase+amount*drives[j].v.rate; };
    auto k1=rhs(start,held); at(dt/2); auto k2=rhs(stage(k1,dt/2),held);
    auto k3=rhs(stage(k2,dt/2),held); at(dt); auto k4=rhs(stage(k3,dt),held);
    auto result=start;
    for(size_t i=0;i<result.size();++i) {
        result[i].x+=dt/6*(k1[3*i]+2*k2[3*i]+2*k3[3*i]+k4[3*i]);
        result[i].y+=dt/6*(k1[3*i+1]+2*k2[3*i+1]+2*k3[3*i+1]+k4[3*i+1]);
        result[i].phase+=dt/6*(k1[3*i+2]+2*k2[3*i+2]+2*k3[3*i+2]+k4[3*i+2]);
        if(!std::isfinite(result[i].x)||!std::isfinite(result[i].y)||!std::isfinite(result[i].phase)) { drives=initial_drives; throw std::runtime_error("non-finite RK4 result"); }
    }
    finite(time+dt); for(size_t i=0;i<elements.size();++i) elements[i].v=result[i]; time+=dt; observe();
}
void Medium::set_drives(const gm_drive* v,int count) {
    require(count>=0 && (count==0 || v),"invalid drives"); std::vector<Drive> next; std::set<uint64_t> ids, reset_history;
    for(int i=0;i<count;++i) {
        for(double z:{v[i].x,v[i].y,v[i].phase,v[i].rate,v[i].strength,v[i].width,v[i].reach}) finite(z);
        require(v[i].width>0 && v[i].reach>0 && v[i].strength>=0 && ids.insert(v[i].id).second,"invalid/duplicate drive");
        Drive d; d.v=v[i];bool same_identity=false;
        for(const auto& old:drives) if(old.v.id==v[i].id) {
            // A changed drive identity/band/geometry starts a new novelty episode.
            if(old.v.x==v[i].x && old.v.y==v[i].y && old.v.rate==v[i].rate && old.v.reach==v[i].reach && old.v.width==v[i].width && old.v.strength==v[i].strength) {d.novelty=old.novelty;same_identity=true;}
        }
        if(!same_identity)reset_history.insert(d.v.id);
        next.push_back(d);
    }
    for(const auto& old:drives)if(!ids.count(old.v.id))reset_history.insert(old.v.id);
    for(auto& frame:history)for(uint64_t id:reset_history)frame.drives.erase(id);
    drives=std::move(next);
}
void Medium::set_needs(const gm_need* v,int count) {
    require(count>=0 && (count==0 || v),"invalid needs"); std::vector<Need> next; std::set<uint64_t> ids;
    for(int i=0;i<count;++i) {
        for(double z:{v[i].x,v[i].y,v[i].phase,v[i].rate,v[i].error}) finite(z);
        require(v[i].error>=0 && ids.insert(v[i].id).second,"invalid/duplicate need"); Need d; d.v=v[i];
        for(const auto& old:needs) if(old.v.id==v[i].id && old.v.x==v[i].x && old.v.y==v[i].y) {d.need=old.need;d.last_birth=old.last_birth;}
        next.push_back(d);
    } needs=std::move(next);
}
double Medium::plv(uint64_t a,uint64_t b,bool input,int* samples) const {
    double x=0,y=0; int count=0;
    for(const auto& frame:history) {
        auto it=frame.elements.find(a); const auto& other=input?frame.drives:frame.elements;
        auto jt=other.find(b); if(it==frame.elements.end() || jt==other.end()) continue;
        double d=it->second-jt->second; x+=std::cos(d); y+=std::sin(d); ++count;
    }
    if(samples) *samples=count;
    if(count<p.min_samples)return 0;
    double value=std::min(1.0,std::hypot(x,y)/count);
    return 1-value<=8*std::numeric_limits<double>::epsilon()?1.0:value;
}
// Global optimum over contiguous two-cluster partitions on the circle, maximizing
// summed weighted resultant lengths. Deterministic first partition wins ties.
static gm_measure fit(std::vector<std::pair<double,double>> points) {
    gm_measure m{}; if(points.empty()) return m;
    // Common rescaling leaves the fit/strain invariant and avoids weight overflow.
    double maximum=0;for(auto p:points)maximum=std::max(maximum,p.second);
    if(maximum<=0)return m;
    for(auto& p:points)p.second/=maximum;
    points.erase(std::remove_if(points.begin(),points.end(),[](auto p){return p.second==0;}),points.end());
    for(auto& p:points) {p.first=std::fmod(p.first,2*pi); if(p.first<0)p.first+=2*pi;}
    std::stable_sort(points.begin(),points.end());
    double total=0,c=0,s=0; for(auto p:points){total+=p.second;c+=p.second*std::cos(p.first);s+=p.second*std::sin(p.first);}
    if(total<=0) return m; m.phase1=m.phase2=std::atan2(s,c);
    const int n=int(points.size()); double best=-1,bc1=0,bs1=0,bw1=0,bc2=0,bs2=0,bw2=0;
    std::vector<double> cx(2*n+1),sy(2*n+1),wt(2*n+1);
    for(int i=0;i<2*n;++i) {auto p=points[i%n];cx[i+1]=cx[i]+p.second*std::cos(p.first);sy[i+1]=sy[i]+p.second*std::sin(p.first);wt[i+1]=wt[i]+p.second;}
    for(int start=0;start<n;++start) for(int len=1;len<n;++len) {
        double c1=cx[start+len]-cx[start],s1=sy[start+len]-sy[start],w1=wt[start+len]-wt[start];
        double c2=c-c1,s2=s-s1,w2=total-w1,score=std::hypot(c1,s1)+std::hypot(c2,s2);
        if(w1<=0 || w2<=0)continue;
        if(score>best) {best=score;bc1=c1;bs1=s1;bw1=w1;bc2=c2;bs2=s2;bw2=w2;}
    }
    if(best<0) return m;
    m.phase1=std::atan2(bs1,bc1);m.phase2=std::atan2(bs2,bc2);
    double coherence=std::hypot(bc1,bs1)/bw1*std::hypot(bc2,bs2)/bw2;
    double balance=4*bw1*bw2/(total*total),opposition=(1-std::cos(m.phase1-m.phase2))/2;
    m.strain=std::clamp(balance*coherence*opposition,0.0,1.0);
    if(1-m.strain<=8*std::numeric_limits<double>::epsilon())m.strain=1;
    return m;
}
gm_measure Medium::instantaneous_strain(int i,const Neighbors& n) const {
    if(elements[i].v.silent) return {}; const auto& e=elements[i].v; std::vector<std::pair<double,double>> points;
    for(int j:n[i]) {
        double r=distance(e,elements[j].v),w=std::abs(p.K)*(p.distance_weighted?std::exp(-r*r):1)/std::max(size_t(1),n[i].size());
        if(w>0) points.push_back({elements[j].v.phase+(p.K<0?pi:0),w});
    }
    for(const auto& d:drives) {double r=std::hypot(e.x-d.v.x,e.y-d.v.y);double w=d.v.strength*kernel(r,d.v.width);if(r<d.v.reach && w>0) points.push_back({d.v.phase,w});}
    return fit(std::move(points));
}
void Medium::observe() {
    Sample sample; auto n=neighbors();
    for(size_t i=0;i<elements.size();++i) if(!elements[i].v.silent) {
        sample.elements[elements[i].v.id]=elements[i].v.phase;
        sample.strain[elements[i].v.id]=instantaneous_strain(int(i),n);
    }
    for(auto& d:drives) if(d.v.strength>0) sample.drives[d.v.id]=d.v.phase;
    history.push_back(std::move(sample)); while(history.size()>size_t(p.window)) history.pop_front();
    if(configured) update_timers();
}
gm_measure Medium::measure(uint64_t id) const {
    gm_measure m{}; int i=index(id); if(elements[i].v.silent) return m;
    auto n=neighbors();
    for(int j:n[i]) m.lock=std::max(m.lock,plv(id,elements[j].v.id));
    for(const auto& d:drives) if(d.v.strength>0 && std::hypot(elements[i].v.x-d.v.x,elements[i].v.y-d.v.y)<d.v.reach) m.lock=std::max(m.lock,plv(id,d.v.id,true));
    for(const auto& f:history) {auto it=f.strain.find(id); if(it!=f.strain.end()) {m.strain+=it->second.strain;++m.samples;m.phase1=it->second.phase1;m.phase2=it->second.phase2;}}
    if(m.samples) m.strain/=m.samples; if(m.samples<p.min_samples) m.strain=0;
    return m;
}
std::vector<int> Medium::groups(double threshold,double factor) const {
    finite(threshold);finite(factor);require(threshold>=0 && threshold<=1 && factor>0,"invalid group threshold");
    std::vector<int> active;for(size_t i=0;i<elements.size();++i)if(!elements[i].v.silent)active.push_back(int(i));
    std::vector<int> labels(elements.size(),-1);if(active.empty())return labels;
    std::vector<double> nearest(active.size(),std::numeric_limits<double>::infinity());
    for(size_t i=0;i<active.size();++i)for(size_t j=0;j<active.size();++j)if(i!=j)nearest[i]=std::min(nearest[i],distance(elements[active[i]].v,elements[active[j]].v));
    std::sort(nearest.begin(),nearest.end());size_t mid=nearest.size()/2;double median=nearest.size()%2?nearest[mid]:(nearest[mid-1]+nearest[mid])/2;
    int label=0;for(int i:active)if(labels[i]<0) {
        labels[i]=label;std::vector<int> stack{i};while(!stack.empty()) {int a=stack.back();stack.pop_back();
            for(int b:active)if(labels[b]<0 && distance(elements[a].v,elements[b].v)<factor*median) {
                int count=0;double lock=plv(elements[a].v.id,elements[b].v.id,false,&count);
                if(count>=p.min_samples && lock>=threshold) {labels[b]=label;stack.push_back(b);}
            }
        } ++label;
    }
    return labels;
}
std::vector<double> Medium::readout(double x,double y,double width,double reach) const {
    for(double v:{x,y,width,reach})finite(v);require(width>0 && reach>0,"invalid kernel");
    double c=0,s=0,w=0;for(const auto& e:elements)if(!e.v.silent) {double r=std::hypot(x-e.v.x,y-e.v.y);if(r<reach){double a=kernel(r,width);w+=a;c+=a*std::cos(e.v.phase);s+=a*std::sin(e.v.phase);}}
    return {w>0?std::clamp(std::hypot(c,s)/w,0.0,1.0):0,(w>0 && std::hypot(c,s)>1e-15*w)?std::atan2(s,c):0};
}
int Medium::couplings() const {auto n=neighbors();int count=0;for(auto row:n)count+=int(row.size());for(const auto& e:elements)if(!e.v.silent)for(const auto& d:drives)if(d.v.strength>0 && std::hypot(e.v.x-d.v.x,e.v.y-d.v.y)<d.v.reach)++count;return count;}
double Medium::cost() const {return growth.c_e*elements.size()+growth.c_c*couplings();}
void Medium::configure(gm_growth g) {
    for(double v:{g.L_on,g.L_off,g.S_split,g.T_nov,g.T_split,g.T_death,g.growth_period,g.T_protect,g.split_offset,g.c_e,g.c_c,g.C_max,g.E_need,g.T_need,g.epsilon_U})finite(v);
    require(g.L_off>=0 && g.L_on<=1 && g.L_on>g.L_off && g.S_split>=0 && g.S_split<=1,"invalid lock/strain thresholds");
    require(g.T_nov>=0 && g.T_split>=0 && g.T_death>=0 && g.growth_period>0 && g.T_protect>=0 && g.split_offset>0 && g.c_e>=0 && g.c_c>=0 && g.C_max>=0 && g.E_need>=0 && g.T_need>=0 && g.epsilon_U>=0 && g.utility_checks>0 && g.N_max>0 && (g.reward_arm==0||g.reward_arm==1),"invalid growth configuration");
    require(elements.size()<=size_t(g.N_max),"existing size exceeds cap");
    growth=g;configured=true;last_growth=time;
    for(auto& e:elements){e.split={};e.death={};e.useless=0;}for(auto& d:drives)d.novelty={};for(auto& n:needs)n.need={};
    update_timers();
}
void Medium::update_timers() {
    for(auto& e:elements) {
        if(e.v.silent) {e.split.update(false,time);e.death.update(false,time);continue;}
        auto m=measure(e.v.id);bool full=m.samples>=p.min_samples;
        e.split.update(full && m.strain>=growth.S_split && m.lock<growth.L_on,time);
        e.death.update(full && m.lock<growth.L_off,time);
    }
    for(auto& d:drives) {
        bool novel=d.v.strength>0;
        for(const auto& e:elements)if(!e.v.silent && std::hypot(e.v.x-d.v.x,e.v.y-d.v.y)<d.v.reach && plv(e.v.id,d.v.id,true)>=growth.L_on)novel=false;
        d.novelty.update(novel,time);
    }
    for(auto& n:needs)n.need.update(growth.reward_arm && n.v.error>growth.E_need,time);
}
void Medium::apply_growth() {
    require(configured,"growth not configured");
    require(std::none_of(elements.begin(),elements.end(),[](const Element& e){return e.v.silent!=0;}),"restore silenced evaluation elements before growth");
    if(time-last_growth<growth.growth_period)return;
    update_timers();last_growth=time;
    std::map<uint64_t,gm_measure> measured;for(const auto& e:elements)measured[e.v.id]=measure(e.v.id);
    std::vector<uint64_t> dead;
    for(auto& e:elements) {
        bool protected_now=time-e.v.born<growth.T_protect;
        if(growth.reward_arm && e.has_utility && time-e.v.born>growth.growth_period) e.useless=std::abs(e.utility)<growth.epsilon_U?e.useless+1:0;
        bool fresh_utility=e.has_utility;e.has_utility=false;
        if(protected_now)continue;
        if(e.death.ready(time,growth.T_death)) {dead.push_back(e.v.id);events.push_back({time,"D1",{e.v.id},{{"lock",measured[e.v.id].lock},{"duration",time-e.death.since},{"age",time-e.v.born}}});}
        else if(growth.reward_arm && fresh_utility && e.useless>=growth.utility_checks && time-e.v.born>growth.growth_period) {dead.push_back(e.v.id);events.push_back({time,"D2",{e.v.id},{{"utility",e.utility},{"checks",double(e.useless)},{"age",time-e.v.born}}});}
        // A utility result is consumed once, never counted repeatedly without evaluations.
        e.has_utility=false;
    }
    for(uint64_t id:dead)elements.erase(elements.begin()+index(id));
    while(cost()>growth.C_max) {
        int best=-1;double rank=0;
        for(size_t i=0;i<elements.size();++i) {
            auto& e=elements[i];if(time-e.v.born<growth.T_protect || (growth.reward_arm && !e.utility_known))continue;
            double score=growth.reward_arm?e.utility:measured[e.v.id].lock;
            if(best<0 || score<rank || (score==rank && e.v.id<elements[best].v.id)){best=int(i);rank=score;}
        }
        if(best<0)break;uint64_t id=elements[best].v.id;
        remove(id,"D3",{{"rank",rank},{"cost",cost()},{"budget",growth.C_max},{"lock",measured[id].lock},{"age",time-elements[best].v.born}});
    }
    // Stable snapshot order: input-site order, then pre-existing element order, then need-site order.
    for(auto& d:drives)if(d.novelty.ready(time,growth.T_nov) && elements.size()<size_t(growth.N_max)) {
        double max_lock=0;int in_range=0;
        for(const auto& e:elements)if(!e.v.silent && std::hypot(e.v.x-d.v.x,e.v.y-d.v.y)<d.v.reach){max_lock=std::max(max_lock,plv(e.v.id,d.v.id,true));++in_range;}
        add(d.v.x,d.v.y,d.v.phase,d.v.rate,"B1",{{"site",double(d.v.id)},{"duration",time-d.novelty.since},{"threshold",growth.L_on},{"max_input_lock",max_lock},{"in_range",double(in_range)}});d.novelty.since=-1;
    }
    std::vector<uint64_t> split_ids;for(auto& e:elements)if(measured.count(e.v.id) && e.split.ready(time,growth.T_split))split_ids.push_back(e.v.id);
    for(uint64_t id:split_ids)if(elements.size()<size_t(growth.N_max)) {auto m=measured[id];double duration=time-elements[index(id)].split.since;
        split(id,m.phase1,m.phase2,growth.split_offset,"B2",{{"strain",m.strain},{"lock",m.lock},{"duration",duration}});
    }
    if(growth.reward_arm)for(auto& n:needs)if(n.need.ready(time,growth.T_need) && (n.last_birth<0 || time-n.last_birth>=growth.T_need) && elements.size()<size_t(growth.N_max)) {
        add(n.v.x,n.v.y,n.v.phase,n.v.rate,"B3",{{"region",double(n.v.id)},{"error",n.v.error},{"duration",time-n.need.since}});n.last_birth=time;n.need.since=-1;
    }
    update_timers();
}
// Explicit field serialization avoids padding and preserves every operational field.
struct Writer {
    std::vector<char> b;
    template<class T> void pod(T v) {static_assert(std::is_arithmetic<T>::value,"scalar only");size_t n=b.size();b.resize(n+sizeof(v));std::memcpy(b.data()+n,&v,sizeof(v));}
    void str(const std::string& s){pod<uint64_t>(s.size());b.insert(b.end(),s.begin(),s.end());}
};
struct Reader {
    const char* b;size_t size,pos=0;
    template<class T>T pod(){require(pos<=size && sizeof(T)<=size-pos,"truncated snapshot");T v;std::memcpy(&v,b+pos,sizeof(v));pos+=sizeof(v);return v;}
    size_t count(){uint64_t n=pod<uint64_t>();require(n<=size-pos,"invalid snapshot count");return size_t(n);}
    std::string str(){size_t n=count();std::string s(b+pos,n);pos+=n;return s;}
};
#define PARAM_FIELDS(F) F(A) F(B) F(J) F(K) F(eps) F(radius) F(geometry_rate) F(k) F(distance_weighted) F(window) F(min_samples)
#define GROWTH_FIELDS(F) F(L_on) F(L_off) F(S_split) F(T_nov) F(T_split) F(T_death) F(growth_period) F(T_protect) F(split_offset) F(c_e) F(c_c) F(C_max) F(E_need) F(T_need) F(epsilon_U) F(N_max) F(reward_arm) F(utility_checks)
#define ELEMENT_FIELDS(F) F(id) F(x) F(y) F(phase) F(rate) F(born) F(silent)
#define DRIVE_FIELDS(F) F(id) F(x) F(y) F(phase) F(rate) F(strength) F(width) F(reach)
#define NEED_FIELDS(F) F(id) F(x) F(y) F(phase) F(rate) F(error)
#define MEASURE_FIELDS(F) F(lock) F(strain) F(phase1) F(phase2) F(samples)
std::vector<char> Medium::save() const {
    Writer w;w.str("growing-medium-v1");
#define WRITE_P(f) w.pod(p.f);
    PARAM_FIELDS(WRITE_P)
#undef WRITE_P
#define WRITE_G(f) w.pod(growth.f);
    GROWTH_FIELDS(WRITE_G)
#undef WRITE_G
    w.pod<int32_t>(configured);w.pod(time);w.pod(last_growth);w.pod(next_id);w.pod(rng);
    w.pod<uint64_t>(elements.size());for(const auto& e:elements){
#define WRITE_E(f) w.pod(e.v.f);
        ELEMENT_FIELDS(WRITE_E)
#undef WRITE_E
        w.pod(e.split.since);w.pod(e.death.since);w.pod(e.utility);w.pod<int32_t>(e.has_utility);w.pod<int32_t>(e.utility_known);w.pod(e.useless);
    }
    w.pod<uint64_t>(drives.size());for(const auto& d:drives){
#define WRITE_D(f) w.pod(d.v.f);
        DRIVE_FIELDS(WRITE_D)
#undef WRITE_D
        w.pod(d.novelty.since);
    }
    w.pod<uint64_t>(needs.size());for(const auto& d:needs){
#define WRITE_N(f) w.pod(d.v.f);
        NEED_FIELDS(WRITE_N)
#undef WRITE_N
        w.pod(d.need.since);w.pod(d.last_birth);
    }
    w.pod<uint64_t>(history.size());for(const auto& s:history){
        for(auto* map:{&s.elements,&s.drives}){w.pod<uint64_t>(map->size());for(auto kv:*map){w.pod(kv.first);w.pod(kv.second);}}
        w.pod<uint64_t>(s.strain.size());for(auto kv:s.strain){w.pod(kv.first);
#define WRITE_M(f) w.pod(kv.second.f);
            MEASURE_FIELDS(WRITE_M)
#undef WRITE_M
        }
    }
    w.pod<uint64_t>(events.size());for(const auto& e:events){w.pod(e.time);w.str(e.rule);w.pod<uint64_t>(e.ids.size());for(auto id:e.ids)w.pod(id);w.pod<uint64_t>(e.measurements.size());for(auto kv:e.measurements){w.str(kv.first);w.pod(kv.second);}}
    w.str(error);return w.b;
}
Medium Medium::load(const void* data,size_t size) {
    require(data && size>0,"empty snapshot");Reader r{static_cast<const char*>(data),size};require(r.str()=="growing-medium-v1","snapshot version mismatch");gm_params p{};
#define READ_P(f) p.f=r.pod<decltype(p.f)>();
    PARAM_FIELDS(READ_P)
#undef READ_P
    Medium m(0,p);
#define READ_G(f) m.growth.f=r.pod<decltype(m.growth.f)>();
    GROWTH_FIELDS(READ_G)
#undef READ_G
    int32_t conf=r.pod<int32_t>();require(conf==0||conf==1,"invalid configured flag");m.configured=conf;
    m.time=r.pod<double>();m.last_growth=r.pod<double>();m.next_id=r.pod<uint64_t>();m.rng=r.pod<uint64_t>();
    size_t n=r.count();for(size_t i=0;i<n;++i){Element e;
#define READ_E(f) e.v.f=r.pod<decltype(e.v.f)>();
        ELEMENT_FIELDS(READ_E)
#undef READ_E
        e.split.since=r.pod<double>();e.death.since=r.pod<double>();e.utility=r.pod<double>();e.has_utility=r.pod<int32_t>();e.utility_known=r.pod<int32_t>();e.useless=r.pod<int>();m.elements.push_back(e);
    }
    n=r.count();for(size_t i=0;i<n;++i){Drive d;
#define READ_D(f) d.v.f=r.pod<decltype(d.v.f)>();
        DRIVE_FIELDS(READ_D)
#undef READ_D
        d.novelty.since=r.pod<double>();m.drives.push_back(d);
    }
    n=r.count();for(size_t i=0;i<n;++i){Need d;
#define READ_N(f) d.v.f=r.pod<decltype(d.v.f)>();
        NEED_FIELDS(READ_N)
#undef READ_N
        d.need.since=r.pod<double>();d.last_birth=r.pod<double>();m.needs.push_back(d);
    }
    n=r.count();require(n<=size_t(p.window),"snapshot history exceeds window");for(size_t i=0;i<n;++i){Sample s;
        for(auto* map:{&s.elements,&s.drives}){size_t count=r.count();for(size_t j=0;j<count;++j){auto id=r.pod<uint64_t>();double value=r.pod<double>();finite(value);(*map)[id]=value;}}
        size_t count=r.count();for(size_t j=0;j<count;++j){auto id=r.pod<uint64_t>();gm_measure v{};
#define READ_M(f) v.f=r.pod<decltype(v.f)>();
            MEASURE_FIELDS(READ_M)
#undef READ_M
            s.strain[id]=v;
        }m.history.push_back(std::move(s));
    }
    n=r.count();for(size_t i=0;i<n;++i){Event e;e.time=r.pod<double>();e.rule=r.str();size_t count=r.count();for(size_t j=0;j<count;++j)e.ids.push_back(r.pod<uint64_t>());count=r.count();for(size_t j=0;j<count;++j){auto key=r.str();double value=r.pod<double>();e.measurements[key]=value;}m.events.push_back(std::move(e));}
    m.error=r.str();require(r.pos==size,"trailing snapshot data");
    finite(m.time);finite(m.last_growth);require(m.time>=0 && m.last_growth<=m.time && m.next_id>0,"invalid snapshot clock/id");
    std::set<uint64_t> ids;for(const auto& e:m.elements){for(double v:{e.v.x,e.v.y,e.v.phase,e.v.rate,e.v.born,e.utility,e.split.since,e.death.since})finite(v);require(e.v.id>0 && e.v.id<m.next_id && ids.insert(e.v.id).second && e.v.born<=m.time && (e.v.silent==0||e.v.silent==1),"invalid snapshot element");}
    // Reuse public validation without resetting saved timers/configuration.
    Medium check=m;check.set_drives(nullptr,0);std::vector<gm_drive> ds;for(auto d:m.drives)ds.push_back(d.v);check.set_drives(ds.data(),int(ds.size()));
    std::vector<gm_need> ns;for(auto d:m.needs)ns.push_back(d.v);check.set_needs(ns.data(),int(ns.size()));
    if(m.configured)check.configure(m.growth);
    for(const auto& d:m.drives)finite(d.novelty.since);
    for(const auto& d:m.needs){finite(d.need.since);finite(d.last_birth);}
    for(const auto& e:m.elements)require(e.useless>=0 && (!e.has_utility || e.utility_known),"invalid snapshot utility");
    for(const auto& f:m.history)for(const auto& kv:f.strain){const auto& v=kv.second;for(double z:{v.lock,v.strain,v.phase1,v.phase2})finite(z);require(v.strain>=0 && v.strain<=1,"invalid snapshot strain");}
    for(const auto& e:m.events){finite(e.time);for(const auto& kv:e.measurements)finite(kv.second);}
    return m;
}
static std::string escape(const std::string& s){std::string out="\"";for(unsigned char c:s){if(c=='"'||c=='\\'){out+='\\';out+=c;}else if(c<32){std::ostringstream v;v<<"\\u"<<std::hex<<std::setw(4)<<std::setfill('0')<<int(c);out+=v.str();}else out+=c;}return out+'"';}
std::string Medium::event_json() const {
    std::ostringstream s;s<<std::setprecision(17)<<'[';bool first=true;
    for(auto& e:events){if(!first)s<<',';first=false;s<<"{\"time\":"<<e.time<<",\"rule\":"<<escape(e.rule)<<",\"ids\":[";for(size_t i=0;i<e.ids.size();++i){if(i)s<<',';s<<e.ids[i];}s<<"],\"measurements\":{";bool k=true;for(auto v:e.measurements){if(!k)s<<',';k=false;s<<escape(v.first)<<':'<<v.second;}s<<"}}";}s<<']';return s.str();
}
}
