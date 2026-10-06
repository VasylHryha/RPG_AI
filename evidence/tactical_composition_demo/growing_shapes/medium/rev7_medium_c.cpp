#include "rev7_medium.hpp"
#include <cstring>
#include <exception>
using rev7::Medium;
namespace {
Medium& obj(void* h) { rev7::require(h,"null handle");return *static_cast<Medium*>(h); }
const Medium& obj(const void* h) { rev7::require(h,"null handle");return *static_cast<const Medium*>(h); }
template<class F>int call(void* h,F f) noexcept {
    if(!h)return -1;auto& m=obj(h);try{m.error.clear();f(m);return 0;}catch(const std::exception& e){m.error=e.what();return -1;}catch(...){m.error="unknown native error";return -1;}
}
void buffer(const void* ptr,int capacity,size_t required){rev7::require(capacity>=0 && size_t(capacity)>=required && (required==0||ptr),"output buffer too small/null");}
}
extern "C" {
void* gm_create(uint64_t seed,const gm_params* p){try{rev7::require(p,"null parameters");return new Medium(seed,*p);}catch(...){return nullptr;}}
void gm_destroy(void* h){delete static_cast<Medium*>(h);}
void* gm_clone(const void* h){try{return new Medium(obj(h));}catch(...){return nullptr;}}
const char* gm_error(const void* h){return h?obj(h).error.c_str():"null handle";}
int gm_count(const void* h){return h?int(obj(h).elements.size()):-1;}
double gm_time(const void* h){return h?obj(h).time:-1;}
int gm_elements(void* h,gm_element* output,int cap){return call(h,[&](Medium& m){buffer(output,cap,m.elements.size());for(size_t i=0;i<m.elements.size();++i)output[i]=m.elements[i].v;});}
int gm_add(void* h,double x,double y,double phase,double rate,uint64_t* id){return call(h,[&](Medium& m){rev7::require(id,"null id output");*id=m.add(x,y,phase,rate);});}
int gm_set_element(void* h,uint64_t id,double x,double y,double phase,double rate){return call(h,[&](Medium& m){for(double v:{x,y,phase,rate})rev7::finite(v);auto& e=m.elements[m.index(id)].v;rev7::require(!m.elements[m.index(id)].output||(x==m.elements[m.index(id)].pin_x&&y==m.elements[m.index(id)].pin_y),"cannot move pinned output");e.x=x;e.y=y;e.phase=phase;e.rate=rate;});}
int gm_options(void* h,int samples,int carried,int undirected){return call(h,[&](Medium& m){for(int f:{samples,carried,undirected})rev7::require(f==0||f==1,"invalid option");m.automatic_samples=samples;m.carried_sites=carried;m.undirected_cost=undirected;});}
int gm_clock(void* h,double time){return call(h,[&](Medium& m){rev7::finite(time);rev7::require(time>=0 && m.elements.empty() && m.events.empty(),"clock requires pristine medium");m.time=time;m.last_growth=time;});}
int gm_first_id(void* h,uint64_t first){return call(h,[&](Medium& m){rev7::require(m.elements.empty() && m.time==0 && m.events.empty(),"first id requires pristine medium");m.next_id=first;});}
int gm_gain(void* h,uint64_t id,double gain){return call(h,[&](Medium& m){rev7::finite(gain);rev7::require(gain>=0 && gain<=2,"gain outside [0,2]");m.elements[m.index(id)].gain=gain;});}
int gm_get_gain(void* h,uint64_t id,double* gain){return call(h,[&](Medium& m){rev7::require(gain,"null gain output");*gain=m.elements[m.index(id)].gain;});}
int gm_remove(void* h,uint64_t id){return call(h,[&](Medium& m){m.remove(id);});}
int gm_split(void* h,uint64_t id,double a,double b,double offset,uint64_t* ids){return call(h,[&](Medium& m){rev7::require(ids,"null ids output");auto v=m.split(id,a,b,offset);ids[0]=v[0];ids[1]=v[1];});}
int gm_silence(void* h,uint64_t id,int silent){return call(h,[&](Medium& m){rev7::require(silent==0||silent==1,"invalid silence flag");m.elements[m.index(id)].v.silent=silent;});}
int gm_drives(void* h,const gm_drive* d,int n){return call(h,[&](Medium& m){m.set_drives(d,n);});}
int gm_rhs(void* h,double* output,int cap){return call(h,[&](Medium& m){buffer(output,cap,3*m.elements.size());std::vector<gm_element> s;for(auto e:m.elements)s.push_back(e.v);auto out=m.rhs(s,m.neighbors(),m.motion_neighbors());std::copy(out.begin(),out.end(),output);});}
int gm_neighbors(void* h,int32_t* indices,double* masks,double* inv,int cap){return call(h,[&](Medium& m){int k=std::min(m.p.k,std::max(0,int(m.elements.size())-1));size_t total=m.elements.size()*k;buffer(indices,cap,total);buffer(masks,cap,total);rev7::require(inv||m.elements.empty(),"null inverse counts");auto n=m.neighbors(true);for(size_t i=0;i<n.size();++i){int count=0;for(int j=0;j<k;++j){bool present=j<int(n[i].size());int ix=present?n[i][j]:-1;double mask=present && std::hypot(m.elements[ix].v.x-m.elements[i].v.x,m.elements[ix].v.y-m.elements[i].v.y)<m.p.radius?1:0;indices[i*k+j]=ix;masks[i*k+j]=mask;count+=int(mask);}inv[i]=1.0/std::max(1,count);}});}
int gm_step(void* h,double dt){return call(h,[&](Medium& m){m.step(dt);});}
int gm_observe(void* h){return call(h,[&](Medium& m){m.observe();});}
int gm_readout(void* h,double x,double y,double width,double reach,double* output){return call(h,[&](Medium& m){rev7::require(output,"null output");auto v=m.readout(x,y,width,reach);output[0]=v[0];output[1]=v[1];});}
int gm_plv(void* h,uint64_t a,uint64_t b,int input,double* output){return call(h,[&](Medium& m){rev7::require(output && (input==0||input==1),"invalid PLV arguments");m.index(a);if(input)rev7::require(std::any_of(m.drives.begin(),m.drives.end(),[&](const rev7::Drive& d){return d.v.id==b;}),"unknown drive id");else m.index(b);*output=m.plv(a,b,input);});}
int gm_measure_element(void* h,uint64_t id,gm_measure* output){return call(h,[&](Medium& m){rev7::require(output,"null output");*output=m.measure(id);});}
int gm_groups(void* h,double t,double f,int32_t* output,int cap){return call(h,[&](Medium& m){buffer(output,cap,m.elements.size());auto v=m.groups(t,f);std::copy(v.begin(),v.end(),output);});}
int gm_cost(void* h,double ce,double cc,double* output){return call(h,[&](Medium& m){rev7::finite(ce);rev7::finite(cc);rev7::require(ce>=0 && cc>=0 && output,"invalid cost arguments");output[0]=double(m.elements.size());output[1]=m.couplings();output[2]=ce*output[0]+cc*output[1];});}
int gm_configure_growth(void* h,const gm_growth* config){return call(h,[&](Medium& m){rev7::require(config,"null growth config");m.configure(*config);});}
int gm_utility(void* h,uint64_t id,double value){return call(h,[&](Medium& m){rev7::finite(value);auto& e=m.elements[m.index(id)];rev7::require(m.configured && m.time-e.v.born>m.growth.growth_period,"utility requires age greater than growth period");e.utility=value;e.has_utility=true;e.utility_known=true;});}
int gm_needs(void* h,const gm_need* n,int count){return call(h,[&](Medium& m){m.set_needs(n,count);});}
int gm_apply_growth(void* h){return call(h,[&](Medium& m){m.apply_growth();});}
size_t gm_save(void* h,void* output,size_t cap){size_t size=0;int ok=call(h,[&](Medium& m){auto bytes=m.save();size=bytes.size();if(output){rev7::require(cap>=size,"snapshot buffer too small");std::memcpy(output,bytes.data(),size);}});return ok==0?size:0;}
void* gm_load(const void* bytes,size_t size){try{return new Medium(Medium::load(bytes,size));}catch(...){return nullptr;}}
size_t gm_events(void* h,char* output,size_t cap){size_t size=0;int ok=call(h,[&](Medium& m){auto json=m.event_json();size=json.size()+1;if(output){rev7::require(cap>=size,"event buffer too small");std::memcpy(output,json.c_str(),size);}});return ok==0?size:0;}
}

extern "C" {
int gm_add_role(void* h,double x,double y,double phase,double rate,int output,uint64_t* id){return call(h,[&](Medium& m){rev7::require(id&&(output==0||output==1),"invalid role");rev7::require(!output||std::none_of(m.elements.begin(),m.elements.end(),[](const rev7::Element& e){return e.output;}),"singleton output cap");*id=m.add(x,y,phase,rate);m.elements.back().output=output;m.elements.back().pin_x=x;m.elements.back().pin_y=y;});}
int gm_role(void* h,uint64_t id,int* output){return call(h,[&](Medium& m){rev7::require(output,"null role");*output=m.elements[m.index(id)].output;});}
int gm_cut(void* h,uint64_t id,double* value,int set){return call(h,[&](Medium& m){rev7::require(value&&std::isfinite(*value)&&*value>=0,"invalid timer");auto& e=m.elements[m.index(id)];if(set)e.cut_off=*value;else *value=e.cut_off;});}
int gm_lesions(void* h,const uint64_t* ids,int n){return call(h,[&](Medium& m){rev7::require(n>=0&&(n==0||ids),"invalid lesions");std::set<uint64_t> next;for(int i=0;i<n;++i){m.index(ids[i]);next.insert(ids[i]);}m.lesions=next;});}
int gm_output(void* h,double* values){return call(h,[&](Medium& m){rev7::require(values,"null output");values[0]=values[1]=0;for(auto e:m.elements)if(e.output&&!e.v.silent){values[0]=1;values[1]=e.v.phase;}});}
int gm_stage_terms(void* h,double* values,int n){return call(h,[&](Medium& m){buffer(values,n,m.stage_terms.size());std::copy(m.stage_terms.begin(),m.stage_terms.end(),values);});}
}

// Evaluator-side ablations on fresh copies only. K is read by every RK4 RHS.
extern "C" int gm_comparator(void* h,int mode){return call(h,[&](Medium& m){
    rev7::require(mode==1||mode==2||mode==3,"unknown evaluator comparator");
    if(mode==1)m.p.K=0.;else if(mode==2)m.fixed_positions=true;else m.site_bodies=false;
});}

extern "C" {
int gm_phase_scale(void* h,double value){return call(h,[&](Medium& m){rev7::require(value==1||value==8||value==32,"only fixture lambda 1/8 or protocol lambda 32");m.phase_scale=value;});}
int gm_excursion(void* h,double* values,int n){return call(h,[&](Medium& m){buffer(values,n,m.excursion.size());std::copy(m.excursion.begin(),m.excursion.end(),values);});}
int gm_motion_neighbors(void* h,int32_t* indices,int32_t* counts,int n){return call(h,[&](Medium& m){buffer(indices,n,m.elements.size()*m.p.k);rev7::require(counts||m.elements.empty(),"null counts");auto held=m.motion_neighbors();for(size_t i=0;i<held.size();++i){counts[i]=int(held[i].size());for(int j=0;j<m.p.k;++j)indices[i*m.p.k+j]=j<counts[i]?held[i][j]:INT32_MIN;}});}
int gm_pin(void* h,uint64_t id,double* result){return call(h,[&](Medium& m){rev7::require(result,"null pin result");auto e=m.elements[m.index(id)];result[0]=e.output;result[1]=e.pin_x;result[2]=e.pin_y;});}
}
extern "C" {
int gm_policy(void* h,double* values){return call(h,[&](Medium& m){rev7::require(values,"null policy");values[0]=m.phase_scale;values[1]=m.fixed_positions;values[2]=m.site_bodies;});}
int gm_reference_drives(void* h,gm_drive* values,int n){return call(h,[&](Medium& m){buffer(values,n,m.drives.size());for(size_t j=0;j<m.drives.size();++j)values[j]=m.drives[j].v;});}
int gm_reference_drive_count(void* h){return h?int(obj(h).drives.size()):-1;}
int gm_reference_lesions(void* h,uint64_t* values,int n){return call(h,[&](Medium& m){buffer(values,n,m.lesions.size());std::copy(m.lesions.begin(),m.lesions.end(),values);});}
int gm_reference_lesion_count(void* h){return h?int(obj(h).lesions.size()):-1;}
int gm_reference_commit(void* h,const double* state,const double* excursion,const double* terms,int n,double dt){return call(h,[&](Medium& m){
    rev7::require(n==int(m.elements.size())&&dt>0,"invalid reference update");
    for(int i=0;i<n;++i){for(int j=0;j<3;++j)rev7::finite(state[3*i+j]);rev7::finite(excursion[i]);rev7::require(excursion[i]>=0,"negative excursion");
        if(m.elements[i].output)rev7::require(state[3*i]==m.elements[i].pin_x&&state[3*i+1]==m.elements[i].pin_y,"reference pin moved");}
    for(int i=0;i<n;++i){auto& e=m.elements[i].v;e.x=state[3*i];e.y=state[3*i+1];e.phase=state[3*i+2];}
    if(n){m.excursion.assign(excursion,excursion+n);m.stage_terms.assign(terms,terms+16*n);}else{m.excursion.clear();m.stage_terms.clear();}
    for(auto& d:m.drives)d.v.phase+=dt*d.v.rate;m.time+=dt;if(m.automatic_samples)m.observe();
});}
}
