#include "perf.h"
#include "../medium/rev6_medium.hpp"
#include <array>
#include <iomanip>
#include <limits>
#include <set>
#include <sstream>
#include <locale>
#include <tuple>
namespace {
constexpr double pi=3.14159265358979323846, dt=.1;
using rev6::require;
struct Row { double x,y,phase; std::vector<uint64_t> links; int slot=0; };
struct Frame { int index; std::map<uint64_t,Row> rows; std::map<uint64_t,gm_drive> sites; };
using Stats=std::pair<double,double>;
struct Engine {
    rev6::Medium& m; int index;
    std::deque<Frame> frames;
    std::map<uint64_t,double> death;
    std::array<double,8> novelty{};
    mutable std::array<std::array<Stats,8>,64> sensor_cache{};
    mutable std::array<uint8_t,64> sensor_valid{};
    std::ostringstream out;
    Engine(void* handle,const PerfFrame* input,int count,int k,const uint64_t* ids,
           const double* timers,int n,const double* nov):m(*static_cast<rev6::Medium*>(handle)),index(k) {
        require(count>0 && count<=601 && input && ids && timers && nov,"invalid history input");
        require(n==int(m.elements.size()) && n<=64 && k>=0,"invalid live state");
        require(!m.automatic_samples && m.carried_sites && m.undirected_cost,"revision 6 options required");
        for(int i=0;i<n;++i){require(ids[i]==m.elements[i].v.id,"timer identity mismatch");rev6::finite(timers[i]);death[ids[i]]=timers[i];}
        for(int s=0;s<8;++s){rev6::finite(nov[s]);novelty[s]=nov[s];}
        for(int i=0;i<count;++i){
            const auto& f=input[i]; require(f.count>=0 && f.count<=64 && f.sites>=0 && f.sites<=8,"invalid frame size");
            require(f.index>=0 && (i==0 || f.index==input[i-1].index+1),"nonconsecutive history");
            Frame frame;frame.index=f.index;
            for(int j=0;j<f.count;++j){auto& r=f.rows[j];require(r.count>=0 && r.count<=64,"invalid links");
                for(double v:{r.x,r.y,r.phase})rev6::finite(v);
                require(!frame.rows.count(r.id),"duplicate historical id");
                frame.rows[r.id]={r.x,r.y,r.phase,std::vector<uint64_t>(r.neighbors,r.neighbors+r.count),j};}
            for(int j=0;j<f.sites;++j){auto d=f.drives[j];require(d.id<8 && !frame.sites.count(d.id),"invalid historical site");
                for(double v:{d.x,d.y,d.phase,d.strength})rev6::finite(v);frame.sites[d.id]=d;}
            frames.push_back(std::move(frame));
        }
        require(frames.back().index==k,"history endpoint mismatch");
        out.imbue(std::locale::classic());out<<std::setprecision(17);
    }
    bool samples(uint64_t id,int count) const {
        if(int(frames.size())<count)return false;
        for(auto i=frames.end()-count;i!=frames.end();++i)if(!i->rows.count(id))return false;
        return true;
    }
    std::vector<double> offsets(uint64_t id,uint64_t partner,bool sensor) const {
        std::vector<double> v;if((sensor&&m.elements[m.index(id)].output)||!samples(id,100))return v;
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
    Stats statistic(uint64_t id,uint64_t partner,bool sensor) const {
        if(!sensor){auto v=offsets(id,partner,false);return v.empty()?Stats{-1,0}:stats(v);}
        auto slot=frames.back().rows.at(id).slot;uint8_t bit=uint8_t(1u<<partner);
        if(sensor_valid[slot]&bit)return sensor_cache[slot][partner];
        auto v=offsets(id,partner,sensor);auto result=v.empty()?Stats{-1,0}:stats(v);
        sensor_cache[slot][partner]=result;sensor_valid[slot]|=bit;return result;
    }
    double lock(uint64_t id) const {
        if(!samples(id,100))return -1;
        std::set<uint64_t> partners;for(auto i=frames.end()-100;i!=frames.end();++i){auto& links=i->rows.at(id).links;partners.insert(links.begin(),links.end());}
        double best=0;for(auto j:partners)best=std::max(best,statistic(id,j,false).first);
        for(int s=0;s<8;++s)best=std::max(best,statistic(id,s,true).first);return best;
    }
    double signal(uint64_t id) const {
        if(m.elements[m.index(id)].output||!samples(id,101))return -1;
        auto& f=frames.back();auto& e=f.rows.at(id);double best=-1;uint64_t site=0;
        for(auto& kv:f.sites){auto s=kv.second;if(s.strength<=0)continue;double distance=std::hypot(e.x-s.x,e.y-s.y);
            double weight=s.strength*(distance<3?std::exp(-distance*distance/2):0);
            if(weight>best){best=weight;site=kv.first;}}
        if(best<=0)return -1;return statistic(id,site,true).first;
    }
    bool covered(int site) const {
        auto& f=frames.back();auto s=f.sites.find(site);if(s==f.sites.end() || s->second.strength<=0)return false;
        for(auto& kv:f.rows){auto id=kv.first;auto e=kv.second;
            if(m.elements[m.index(id)].output || !samples(id,101) || std::hypot(e.x-s->second.x,e.y-s->second.y)>=3)continue;
            auto z=statistic(id,site,true);if(z.first>=.8 && std::abs(z.second)<=.5)return true;}
        return false;
    }
    void record(const std::vector<gm_drive>& drives){
        sensor_valid.fill(0); // one immutable endpoint window per cache lifetime
        Frame f;f.index=index;auto neighbors=m.neighbors(true);
        for(size_t i=0;i<m.elements.size();++i){auto e=m.elements[i].v;Row r{e.x,e.y,e.phase,{},int(i)};
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
        diagnostics(plastic);
        out<<",\"death\":{";bool first=true;for(auto kv:death){if(!first)out<<',';first=false;out<<'"'<<kv.first<<"\":"<<kv.second;}
        out<<"},\"novelty\":[";for(int s=0;s<8;++s){if(s)out<<',';out<<novelty[s];}out<<']';
    }
    std::set<uint64_t> reach(std::set<uint64_t> reached,const std::map<uint64_t,std::set<uint64_t>>& edges){
        std::vector<uint64_t> todo(reached.begin(),reached.end());while(!todo.empty()){auto a=todo.back();todo.pop_back();auto found=edges.find(a);if(found!=edges.end())for(auto b:found->second)if(reached.insert(b).second)todo.push_back(b);}return reached;
    }
    void diagnostics(bool timers){
        auto held=m.neighbors();std::map<uint64_t,std::set<uint64_t>> forward,backward;
        std::set<uint64_t> outputs,allroots;std::array<std::set<uint64_t>,8> roots;
        for(size_t i=0;i<m.elements.size();++i){auto e=m.elements[i];forward[e.v.id];backward[e.v.id];if(e.output)outputs.insert(e.v.id);
            for(int j:held[i]){forward[m.elements[j].v.id].insert(e.v.id);backward[e.v.id].insert(m.elements[j].v.id);}
            if(!e.output&&e.gain>0)for(auto d:m.drives)if(d.v.id<8&&d.v.strength>0&&std::hypot(e.v.x-d.v.x,e.v.y-d.v.y)<d.v.reach){roots[d.v.id].insert(e.v.id);allroots.insert(e.v.id);}}
        auto f=reach(allroots,forward),b=reach(outputs,backward);
        if(timers)for(auto& e:m.elements)e.cut_off=f.count(e.v.id)||b.count(e.v.id)?0:e.cut_off+dt;
        out<<",\"paths\":[";for(int s=0;s<8;++s){if(s)out<<',';auto reached=reach(roots[s],forward);bool yes=false;for(auto o:outputs)yes|=reached.count(o)>0;out<<(yes?"true":"false");}out<<"],\"cut_off\":{";
        bool first=true;for(auto e:m.elements){if(!first)out<<',';first=false;out<<'"'<<e.v.id<<"\":"<<e.cut_off;}out<<"},\"exposure\":{";
        first=true;for(auto e:m.elements){if(!first)out<<',';first=false;bool geometric=false,actual=false;for(auto d:m.drives)if(d.v.strength>0&&std::hypot(e.v.x-d.v.x,e.v.y-d.v.y)<d.v.reach){geometric=true;actual|=!e.output&&e.gain>0;}
            double radius=std::hypot(e.v.x,e.v.y);out<<'"'<<e.v.id<<"\":{\"radius\":"<<radius<<",\"wall\":"<<(radius>6?"true":"false")<<",\"geometric\":"<<(geometric?"true":"false")<<",\"drive\":"<<(actual?"true":"false")<<'}';}out<<'}';
    }
    std::vector<gm_drive> bindings(const GSObservation& o,const int32_t* assignment,const double* sites){
        require(o.enemy_count>=0 && o.enemy_count<=8,"invalid enemy count");
        std::vector<gm_drive> ds;for(int s=0;s<8;++s)ds.push_back({uint64_t(s),sites[2*s],sites[2*s+1],pi*(index*dt),pi,0.,1.,3.});
        if(o.task==GS_MOVE){double angle=o.target_angle+(o.target_distance<o.desired_range?pi:0.);auto& d=ds[assignment[0]];d.phase+=angle;d.strength=2*std::min(1.,std::abs(o.target_distance-o.desired_range)/2);}
        else{std::vector<GSEnemy> enemies(o.enemies,o.enemies+o.enemy_count);std::sort(enemies.begin(),enemies.end(),[](auto a,auto b){return a.id<b.id;});
            for(size_t j=0;j<enemies.size();++j){auto e=enemies[j];double k=e.visible?2*std::exp(-e.distance/10):0.;if(o.task==GS_CHOOSE)k*=(1+(1-e.hp/100))*(e.distance<=2.5?1.:.5);
                auto& d=ds[assignment[j]];d.phase+=e.angle;d.strength=k;}}
        return ds;
    }
    GSAction action(const GSObservation& o){std::vector<double> read{0,0};for(auto e:m.elements)if(e.output&&!e.v.silent){read={1,e.v.phase};}bool abstain=read[0]<.05;
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
std::string quote(const char* s){std::ostringstream out;out<<'"';for(const unsigned char* p=reinterpret_cast<const unsigned char*>(s);*p;++p){
    if(*p=='"' || *p=='\\')out<<'\\'<<*p;else if(*p<32)out<<"\\u"<<std::hex<<std::setw(4)<<std::setfill('0')<<int(*p);else out<<*p;}out<<'"';return out.str();}
template<class F>const char* guarded(F f){try{response=f();}catch(const std::exception& e){response="{\"error\":"+quote(e.what())+"}";}return response.c_str();}
void validate_drives(const gm_drive* ds,int n){require(n>=0 && n<=8 && (n==0 || ds),"invalid drive count");std::set<uint64_t> ids;
    for(int i=0;i<n;++i){auto d=ds[i];require(d.id<8 && ids.insert(d.id).second,"invalid protocol site");
        for(double v:{d.x,d.y,d.phase,d.rate,d.strength,d.width,d.reach})rev6::finite(v);
        require(d.strength>=0 && d.width>0 && d.reach>0,"invalid drive geometry");}}
void validate_binding(const int32_t* assignment,const double* sites){require(assignment && sites,"missing binding");std::set<int> slots;
    for(int s=0;s<8;++s){require(assignment[s]>=0 && assignment[s]<8,"invalid binding");slots.insert(assignment[s]);rev6::finite(sites[2*s]);rev6::finite(sites[2*s+1]);}
    require(slots.size()==8,"binding not permutation");}
}
extern "C" int gp_abi_version(){return 3;}
extern "C" int gp_struct_size(int which){return which==0?sizeof(PerfRow):which==1?sizeof(PerfFrame):which==2?sizeof(PerfDrives):0;}
extern "C" const char* gp_batch(void* medium,GSWorld* world,const PerfFrame* frames,int count,int index,const uint64_t* ids,const double* death,int n,const double* novelty,const int32_t* assignment,const double* sites,int steps,double coverage_start){
    return guarded([&]{require(medium && world && assignment && sites && steps>0 && steps<=200,"invalid batch");
        validate_binding(assignment,sites);rev6::finite(coverage_start);
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
    return guarded([&]{require(medium && (adapt==0 || adapt==1),"invalid contract");validate_drives(drives,nd);Engine e(medium,frames,count,index,ids,death,n,novelty);e.out<<"{\"steps\":[";
        std::vector<gm_drive> ds;if(nd)ds.assign(drives,drives+nd);
        e.endpoint(ds,adapt,0);e.out<<"}]}";return e.out.str();});
}
extern "C" const char* gp_replay(void* medium,const PerfFrame* frames,int count,int index,const uint64_t* ids,const double* death,int n,const double* novelty,const PerfDrives* schedule,int steps,int adapt){
    return guarded([&]{require(medium && schedule && steps>0 && steps<=600 && (adapt==0 || adapt==1),"invalid replay");
        // Validate the entire supplied future before touching the medium.
        for(int i=0;i<steps;++i)validate_drives(schedule[i].drives,schedule[i].count);
        Engine e(medium,frames,count,index,ids,death,n,novelty);e.out<<"{\"steps\":[";
        for(int i=0;i<steps;++i){if(i)e.out<<',';auto& s=schedule[i];e.endpoint(std::vector<gm_drive>(s.drives,s.drives+s.count),adapt,0);e.out<<'}';}
        e.out<<"]}";return e.out.str();});
}
extern "C" const char* gp_evaluate_episode(void* medium,GSWorld* world,const PerfFrame* frames,int count,int index,const uint64_t* ids,const double* death,int n,const double* novelty,const int32_t* assignment,const double* sites){
    return guarded([&]{require(medium && world,"invalid evaluation");validate_binding(assignment,sites);
        Engine e(medium,frames,count,index,ids,death,n,novelty);GSObservation obs{};std::vector<gm_drive> ds;
        // Fresh evaluation copy: no adaptation, growth, timers, reward or recovery.
        for(int steps=0;;++steps){require(gs_observe(world,&obs)==GS_OK,"world observation failed");if(obs.done)break;
            require(steps<160 && (obs.task==GS_PERCEIVE || obs.task==GS_MOVE || obs.task==GS_REMEMBER_STATIC || obs.task==GS_CHOOSE),"invalid evaluation task/horizon");
            ds=e.bindings(obs,assignment,sites);e.m.set_drives(ds.data(),int(ds.size()));for(int j=0;j<5;++j)e.m.step(.02);
            ++e.index;auto a=e.action(obs);require(gs_step(world,&a)==GS_OK,"native world action rejected");}
        e.out<<"{\"index\":"<<e.index<<'}';return e.out.str();});
}
extern "C" const char* gp_future(void* medium,const PerfDrives* schedule,int steps,double* trajectory,int scalars){
    return guarded([&]{require(medium && schedule && trajectory && steps>0 && steps<=600,"invalid future");
        auto& m=*static_cast<rev6::Medium*>(medium);int n=int(m.elements.size());
        require(n<=64 && scalars==steps*n*3 && !m.automatic_samples && m.carried_sites && m.undirected_cost,"invalid frozen future state/size");
        for(int i=0;i<steps;++i)validate_drives(schedule[i].drives,schedule[i].count);
        for(int k=0;k<steps;++k){auto& ds=schedule[k];m.set_drives(ds.drives,ds.count);
            for(int j=0;j<5;++j)m.step(.02);
            for(int i=0;i<n;++i){auto e=m.elements[i].v;auto p=trajectory+(k*n+i)*3;p[0]=e.x;p[1]=e.y;p[2]=e.phase;}}
        return std::string("{}");});
}

extern "C" const char* gp_assay(void* medium,GSWorld* world,const PerfFrame* frames,int count,int index,const uint64_t* ids,const double* death,int n,const double* novelty,const int32_t* assignment,const double* sites,const PerfDrives* schedule,int scheduled,int relay){
    return guarded([&]{require(medium&&world&&scheduled>=0&&scheduled<=160&&relay>=0&&relay<=2,"invalid assay");validate_binding(assignment,sites);
        for(int i=0;i<scheduled;++i)validate_drives(schedule[i].drives,schedule[i].count);
        Engine e(medium,frames,count,index,ids,death,n,novelty);e.out<<"{\"decisions\":[";GSObservation obs{};int steps=0;
        for(;steps<160;++steps){require(gs_observe(world,&obs)==GS_OK,"world observation failed");if(obs.done)break;
            auto ds=e.bindings(obs,assignment,sites);if(scheduled){require(steps<scheduled,"short donor schedule");auto& src=schedule[steps];ds.assign(src.drives,src.drives+src.count);}
            if(steps)e.out<<',';e.out<<"{\"drives\":";e.drives_json(ds);e.m.set_drives(ds.data(),int(ds.size()));for(int j=0;j<5;++j)e.m.step(.02);++e.index;
            auto a=e.action(obs);if(relay){const gm_drive* selected=nullptr;for(const auto& d:ds)if(d.strength>0&&((relay==1&&d.id==0)||(relay==2&&(!selected||d.strength>selected->strength||(d.strength==selected->strength&&d.id<selected->id)))))selected=&d;
                double beta=selected?selected->phase+dt*selected->rate-pi*(e.index*dt):0;beta=std::fmod(beta+pi,2*pi);if(beta<0)beta+=2*pi;beta-=pi;
                // Reuse the exact decoder by a virtual singleton phase (no medium mutation).
                if(obs.task==GS_CHOOSE){double best=std::numeric_limits<double>::infinity();int chosen=INT32_MAX;for(int j=0;j<obs.enemy_count;++j){auto v=obs.enemies[j];if(!v.visible||v.hp<=0)continue;double z=std::fmod(beta-v.angle+pi,2*pi);if(z<0)z+=2*pi;z=std::abs(z-pi);if(z<best||(z==best&&v.id<chosen)){best=z;chosen=v.id;}}a={0,0,chosen};}
                else a={beta,obs.task==GS_MOVE?1.:0.,-1};}
            e.out<<",\"angle\":"<<a.angle<<",\"has_output\":"<<(std::any_of(e.m.elements.begin(),e.m.elements.end(),[](auto z){return z.output!=0;})?"true":"false");
            // Site angles at the decision endpoint are advanced on the same carrier.
            e.diagnostics(false);e.out<<'}';require(gs_step(world,&a)==GS_OK,"assay action failed");}
        require(gs_observe(world,&obs)==GS_OK&&obs.done,"assay horizon mismatch");require(!scheduled||steps==scheduled,"donor horizon mismatch");e.out<<"],\"index\":"<<e.index<<'}';return e.out.str();});
}
