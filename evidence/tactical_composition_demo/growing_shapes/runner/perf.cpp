#include "perf.h"
#include "../medium/medium.hpp"
#include <array>
#include <iomanip>
#include <limits>
#include <set>
#include <sstream>
namespace {
constexpr double pi=3.14159265358979323846, dt=.1;
using growing::require;
struct Row { double x,y,phase; std::vector<uint64_t> links; };
struct Frame { int index; std::map<uint64_t,Row> rows; std::map<uint64_t,gm_drive> sites; };
using Stats=std::pair<double,double>;
struct Engine {
    growing::Medium& m; int index;
    std::deque<Frame> frames;
    std::map<uint64_t,double> death;
    std::array<double,8> novelty{};
    std::ostringstream out;
    Engine(void* handle,const PerfFrame* input,int count,int k,const uint64_t* ids,
           const double* timers,int n,const double* nov):m(*static_cast<growing::Medium*>(handle)),index(k) {
        require(count>0 && count<=601 && input && ids && timers && nov,"invalid history input");
        require(n==int(m.elements.size()) && n<=64 && k>=0,"invalid live state");
        require(!m.automatic_samples && m.carried_sites && m.undirected_cost,"revision 5.1 options required");
        for(int i=0;i<n;++i){require(ids[i]==m.elements[i].v.id,"timer identity mismatch");growing::finite(timers[i]);death[ids[i]]=timers[i];}
        for(int s=0;s<8;++s){growing::finite(nov[s]);novelty[s]=nov[s];}
        for(int i=0;i<count;++i){
            const auto& f=input[i]; require(f.count>=0 && f.count<=64 && f.sites>=0 && f.sites<=8,"invalid frame size");
            require(f.index>=0 && (i==0 || f.index==input[i-1].index+1),"nonconsecutive history");
            Frame frame;frame.index=f.index;
            for(int j=0;j<f.count;++j){auto& r=f.rows[j];require(r.count>=0 && r.count<=64,"invalid links");
                for(double v:{r.x,r.y,r.phase})growing::finite(v);
                require(!frame.rows.count(r.id),"duplicate historical id");
                frame.rows[r.id]={r.x,r.y,r.phase,std::vector<uint64_t>(r.neighbors,r.neighbors+r.count)};}
            for(int j=0;j<f.sites;++j){auto d=f.drives[j];require(d.id<8 && !frame.sites.count(d.id),"invalid historical site");
                for(double v:{d.x,d.y,d.phase,d.strength})growing::finite(v);frame.sites[d.id]=d;}
            frames.push_back(std::move(frame));
        }
        require(frames.back().index==k,"history endpoint mismatch");
        out<<std::setprecision(17);
    }
    bool samples(uint64_t id,int count) const {
        if(int(frames.size())<count)return false;
        for(auto i=frames.end()-count;i!=frames.end();++i)if(!i->rows.count(id))return false;
        return true;
    }
    std::vector<double> offsets(uint64_t id,uint64_t partner,bool sensor) const {
        std::vector<double> v;if(!samples(id,100))return v;
        for(auto i=frames.end()-100;i!=frames.end();++i){auto& e=i->rows.at(id);
            if(sensor){auto s=i->sites.find(partner);if(s==i->sites.end() || s->second.strength<=0 || std::hypot(e.x-s->second.x,e.y-s->second.y)>=3)continue;v.push_back(e.phase-s->second.phase);}
            else if(std::find(e.links.begin(),e.links.end(),partner)!=e.links.end() && i->rows.count(partner))v.push_back(e.phase-i->rows.at(partner).phase);
        }
        if(v.size()<80)v.clear();return v;
    }
    static Stats sum(const std::vector<Stats>& v,size_t start,size_t count){
        // Match NumPy 2.0 complex reduction: 128 real/imag scalars per block,
        // four complex lanes, aligned recursive split, then left-to-right tail.
        // Arithmetic order matters at inclusive coverage thresholds.
        if(count>64){size_t left=(count/8)*4;auto a=sum(v,start,left),b=sum(v,start+left,count-left);return {a.first+b.first,a.second+b.second};}
        if(count<4){Stats r{-0.,-0.};for(size_t i=0;i<count;++i){r.first+=v[start+i].first;r.second+=v[start+i].second;}return r;}
        std::array<Stats,4> lanes;for(size_t j=0;j<4;++j)lanes[j]=v[start+j];
        size_t i=4;for(;i<count-count%4;i+=4)for(size_t j=0;j<4;++j){lanes[j].first+=v[start+i+j].first;lanes[j].second+=v[start+i+j].second;}
        Stats r{(lanes[0].first+lanes[1].first)+(lanes[2].first+lanes[3].first),
                (lanes[0].second+lanes[1].second)+(lanes[2].second+lanes[3].second)};
        for(;i<count;++i){r.first+=v[start+i].first;r.second+=v[start+i].second;}return r;
    }
    static Stats stats(const std::vector<double>& v){
        std::vector<Stats> z;for(double a:v)z.emplace_back(std::cos(a),std::sin(a));auto total=sum(z,0,z.size());
        double scale=1./v.size(),real=total.first*scale,imag=total.second*scale;
        return {std::min(1.,std::hypot(real,imag)),std::atan2(imag,real)};
    }
    double lock(uint64_t id) const {
        if(!samples(id,100))return -1;
        std::set<uint64_t> partners;for(auto i=frames.end()-100;i!=frames.end();++i){auto& links=i->rows.at(id).links;partners.insert(links.begin(),links.end());}
        double best=0;for(auto j:partners){auto v=offsets(id,j,false);if(!v.empty())best=std::max(best,stats(v).first);}
        for(int s=0;s<8;++s){auto v=offsets(id,s,true);if(!v.empty())best=std::max(best,stats(v).first);}return best;
    }
    double signal(uint64_t id) const {
        if(!samples(id,101))return -1;
        auto& f=frames.back();auto& e=f.rows.at(id);double best=-1;uint64_t site=0;
        for(auto& kv:f.sites){auto s=kv.second;if(s.strength<=0)continue;double distance=std::hypot(e.x-s.x,e.y-s.y);
            double weight=s.strength*(distance<3?std::exp(-distance*distance/2):0);
            if(weight>best){best=weight;site=kv.first;}}
        if(best<=0)return -1;auto v=offsets(id,site,true);return v.empty()?-1:stats(v).first;
    }
    bool covered(int site) const {
        auto& f=frames.back();auto s=f.sites.find(site);if(s==f.sites.end() || s->second.strength<=0)return false;
        for(auto& kv:f.rows){auto id=kv.first;auto e=kv.second;
            if(!samples(id,101) || std::hypot(e.x-s->second.x,e.y-s->second.y)>=3)continue;
            auto v=offsets(id,site,true);if(!v.empty()){auto z=stats(v);if(z.first>=.8 && std::abs(z.second)<=.5)return true;}}
        return false;
    }
    void record(const std::vector<gm_drive>& drives){
        Frame f;f.index=index;auto neighbors=m.neighbors(true);
        for(size_t i=0;i<m.elements.size();++i){auto e=m.elements[i].v;Row r{e.x,e.y,e.phase,{}};
            for(int j:neighbors[i])if(std::hypot(e.x-m.elements[j].v.x,e.y-m.elements[j].v.y)<m.p.radius)r.links.push_back(m.elements[j].v.id);
            f.rows[e.id]=std::move(r);}
        for(auto d:drives)f.sites[d.id]=d;frames.push_back(std::move(f));if(frames.size()>601)frames.pop_front();
    }
    void drives_json(const std::vector<gm_drive>& ds){out<<'[';bool first=true;for(auto d:ds){if(!first)out<<',';first=false;out<<'['<<d.id<<','<<d.x<<','<<d.y<<','<<d.phase<<','<<d.rate<<','<<d.strength<<','<<d.width<<','<<d.reach<<']';}out<<']';}
    void frame_json(){auto& f=frames.back();out<<"{\"index\":"<<index<<",\"time\":"<<index*dt<<",\"elements\":{";
        bool first=true;for(auto kv:f.rows){if(!first)out<<',';first=false;auto r=kv.second;out<<'"'<<kv.first<<"\":["<<r.x<<','<<r.y<<','<<r.phase<<']';}
        out<<"},\"sites\":{";first=true;for(auto kv:f.sites){if(!first)out<<',';first=false;auto d=kv.second;out<<'"'<<kv.first<<"\":["<<d.x<<','<<d.y<<','<<d.phase<<','<<d.strength<<']';}
        out<<"},\"neighbors\":{";first=true;for(auto kv:f.rows){if(!first)out<<',';first=false;out<<'"'<<kv.first<<"\":[";bool one=true;for(auto id:kv.second.links){if(!one)out<<',';one=false;out<<id;}out<<']';}out<<"}}";
    }
    void endpoint(std::vector<gm_drive> ds,bool plastic,double coverage_start){
        out<<"{\"step\":"<<index<<",\"drives\":";drives_json(ds);
        m.set_drives(ds.data(),int(ds.size()));for(int j=0;j<5;++j)m.step(.02);
        ++index;for(auto& d:ds)d.phase+=dt*d.rate;
        m.observe();record(ds); // append first; rates/gains below do not alter frame
        out<<",\"frame\":";frame_json();
        std::map<uint64_t,double> signals;
        if(plastic){for(auto& element:m.elements){auto& e=element.v;
                if(samples(e.id,101)){double estimate=(frames.back().rows.at(e.id).phase-(frames.end()-101)->rows.at(e.id).phase)/10;
                    e.rate=std::clamp(e.rate+.005*(estimate-e.rate),.5*pi,1.5*pi);}
                double s=signal(e.id);if(s>=0){element.gain=std::clamp(element.gain+.005*(s-element.gain),0.,2.);signals[e.id]=s;}}
            out<<",\"event\":{\"time\":"<<index*dt<<",\"rule\":\"adaptation\",\"ids\":[],\"values\":{\"rates\":{";
            bool first=true;for(auto e:m.elements){if(!first)out<<',';first=false;out<<'"'<<e.v.id<<"\":"<<e.v.rate;}
            out<<"},\"gains\":{";first=true;for(auto e:m.elements){if(!first)out<<',';first=false;out<<'"'<<e.v.id<<"\":"<<e.gain;}
            out<<"},\"defined_signals\":{";first=true;for(auto kv:signals){if(!first)out<<',';first=false;out<<'"'<<kv.first<<"\":"<<kv.second;}
            out<<"}},\"cost\":"<<double(m.elements.size())+.1*m.couplings()<<'}';
            for(auto e:m.elements){double l=lock(e.v.id);death[e.v.id]=l>=0 && l<.5?death[e.v.id]+dt:0.;}
            std::array<bool,8> coverage{};for(int s=0;s<8;++s){coverage[s]=covered(s);auto found=frames.back().sites.find(s);
                novelty[s]=found!=frames.back().sites.end() && found->second.strength>0 && !coverage[s]?novelty[s]+dt:0.;}
            out<<",\"covered\":[";for(int s=0;s<8;++s){if(s)out<<',';out<<(coverage[s]?"true":"false");}out<<']';
            int active=0,covered_count=0;for(auto d:ds)if(d.strength>0){++active;covered_count+=coverage[d.id];}
            out<<",\"coverage\":";if(index>=coverage_start && active)out<<double(covered_count)/active;else out<<"null";
        }
        out<<",\"death\":{";bool first=true;for(auto kv:death){if(!first)out<<',';first=false;out<<'"'<<kv.first<<"\":"<<kv.second;}
        out<<"},\"novelty\":[";for(int s=0;s<8;++s){if(s)out<<',';out<<novelty[s];}out<<']';
    }
    std::vector<gm_drive> bindings(const GSObservation& o,const int32_t* assignment,const double* sites){
        std::vector<gm_drive> ds;for(int s=0;s<8;++s)ds.push_back({uint64_t(s),sites[2*s],sites[2*s+1],pi*(index*dt),pi,0.,1.,3.});
        if(o.task==GS_MOVE){double angle=o.target_angle+(o.target_distance<o.desired_range?pi:0.);auto& d=ds[assignment[0]];d.phase+=angle;d.strength=2*std::min(1.,std::abs(o.target_distance-o.desired_range)/2);}
        else{std::vector<GSEnemy> enemies(o.enemies,o.enemies+o.enemy_count);std::sort(enemies.begin(),enemies.end(),[](auto a,auto b){return a.id<b.id;});
            for(size_t j=0;j<enemies.size();++j){auto e=enemies[j];double k=e.visible?2*std::exp(-e.distance/10):0.;if(o.task==GS_CHOOSE)k*=(1+(1-e.hp/100))*(e.distance<=2.5?1.:.5);
                auto& d=ds[assignment[j]];d.phase+=e.angle;d.strength=k;}}
        return ds;
    }
    GSAction action(const GSObservation& o){auto read=m.readout(0,0,1,2);bool abstain=read[0]<.05;
        double a=read[1]-pi*(index*dt)+pi;double beta=std::fmod(a,2*pi);if(beta<0)beta+=2*pi;beta-=pi;
        GSAction result{0,0,-1};
        if(o.task==GS_CHOOSE){double best=std::numeric_limits<double>::infinity();int chosen=std::numeric_limits<int>::max();
            for(int j=0;j<o.enemy_count;++j){auto e=o.enemies[j];if(!e.visible || e.hp<=0)continue;double v=std::fmod(beta-e.angle+pi,2*pi);if(v<0)v+=2*pi;v=abstain?0:std::abs(v-pi);
                if(v<best || (v==best && e.id<chosen)){best=v;chosen=e.id;}}
            require(chosen!=std::numeric_limits<int>::max(),"no live choice");result.choice=chosen;
        }else if(!abstain){result.angle=beta;if(o.task==GS_PERCEIVE)result.magnitude=std::clamp(10*std::log(1/read[0]),0.,std::sqrt(800.));else if(o.task==GS_MOVE)result.magnitude=std::min(1.,read[0]/.8);}
        return result;
    }
};
thread_local std::string response;
template<class F>const char* guarded(F f){try{response=f();}catch(const std::exception& e){response=std::string("{\"error\":\"")+e.what()+"\"}";}return response.c_str();}
}
extern "C" const char* gp_batch(void* medium,GSWorld* world,const PerfFrame* frames,int count,int index,const uint64_t* ids,const double* death,int n,const double* novelty,const int32_t* assignment,const double* sites,int steps,double coverage_start){
    return guarded([&]{require(medium && world && assignment && sites && steps>0 && steps<=200,"invalid batch");
        std::set<int> slots;for(int s=0;s<8;++s){require(assignment[s]>=0 && assignment[s]<8,"invalid binding");slots.insert(assignment[s]);growing::finite(sites[2*s]);growing::finite(sites[2*s+1]);}require(slots.size()==8,"binding not permutation");
        require(steps<=200-index%200,"batch crosses growth boundary");
        Engine e(medium,frames,count,index,ids,death,n,novelty);e.out<<"{\"steps\":[";
        int ran=0;GSObservation obs{};
        for(;ran<steps;++ran){require(gs_observe(world,&obs)==GS_OK,"world observation failed");if(obs.done)break;
            require(obs.task==GS_PERCEIVE || obs.task==GS_MOVE || obs.task==GS_REMEMBER_STATIC || obs.task==GS_CHOOSE,"unsupported protocol task");
            auto ds=e.bindings(obs,assignment,sites);if(ran)e.out<<',';e.endpoint(ds,true,coverage_start);
            // At a growth/check/admission boundary Python must act BEFORE world.step.
            if(e.index%200==0){e.out<<",\"action\":null}";++ran;break;}
            auto a=e.action(obs);e.out<<",\"action\":["<<a.angle<<','<<a.magnitude<<','<<a.choice<<"]}";
            require(gs_step(world,&a)==GS_OK,"native world action rejected");
        }
        e.out<<"],\"boundary\":"<<(ran && e.index%200==0?"true":"false")<<'}';return e.out.str();});
}
extern "C" const char* gp_contract(void* medium,const PerfFrame* frames,int count,int index,const uint64_t* ids,const double* death,int n,const double* novelty,const gm_drive* drives,int nd,int adapt){
    return guarded([&]{require(medium && nd>=0 && nd<=8 && (nd==0 || drives) && (adapt==0 || adapt==1),"invalid contract");Engine e(medium,frames,count,index,ids,death,n,novelty);e.out<<"{\"steps\":[";
        std::vector<gm_drive> ds;if(nd)ds.assign(drives,drives+nd);
        e.endpoint(ds,adapt,0);e.out<<"}]}";return e.out.str();});
}
