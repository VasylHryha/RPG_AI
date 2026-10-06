#pragma once
#include "medium_c.h"
#include <set>
#include <algorithm>
#include <cmath>
#include <cstdint>
#include <deque>
#include <map>
#include <string>
#include <vector>
namespace rev7 {
struct Track { double since=-1; void update(bool yes,double t) { if(!yes) since=-1; else if(since<0) since=t; } bool ready(double t,double duration) const { return since>=0 && t-since>=duration; } };
struct Element { gm_element v{}; Track split, death; int output=0; double pin_x=0, pin_y=0; double cut_off=0; double gain=1; double utility=0; bool has_utility=false, utility_known=false; int useless=0; };
struct Drive { gm_drive v{}; Track novelty; };
struct Need { gm_need v{}; Track need; double last_birth=-1; };
struct Sample { std::map<uint64_t,double> elements, drives; std::map<uint64_t,gm_measure> strain; };
struct Event { double time; std::string rule; std::vector<uint64_t> ids; std::map<std::string,double> measurements; };
using Neighbors=std::vector<std::vector<int>>;
class Medium {
public:
    mutable std::vector<double> stage_terms; std::set<uint64_t> lesions;
    gm_params p; gm_growth growth{}; bool configured=false;
    bool automatic_samples=true, carried_sites=false, undirected_cost=false;
    double phase_scale=32; bool site_bodies=true; std::vector<double> excursion;
    bool fixed_positions=false; // Disposable evaluator copies only; never a growth rule.
    double time=0, last_growth=0; uint64_t next_id=1, rng;
    std::vector<Element> elements; std::vector<Drive> drives; std::vector<Need> needs;
    std::deque<Sample> history; std::vector<Event> events; std::string error;
    Medium(uint64_t seed,gm_params params);
    int index(uint64_t id) const;
    uint64_t add(double x,double y,double phase,double rate,const std::string& rule="ADD",std::map<std::string,double> why={});
    void remove(uint64_t id,const std::string& rule="REMOVE",std::map<std::string,double> why={});
    std::vector<uint64_t> split(uint64_t id,double a,double b,double offset,const std::string& rule="SPLIT",std::map<std::string,double> why={});
    Neighbors neighbors(bool padded=false) const;
    Neighbors strong_neighbors() const; // Transmission graph only; RHS/D4 keep neighbors().
    Neighbors motion_neighbors() const;
    std::vector<double> rhs(const std::vector<gm_element>& state,const Neighbors& held, const Neighbors& motion) const;
    void step(double dt); void observe();
    void set_drives(const gm_drive* values,int count); void set_needs(const gm_need* values,int count);
    double plv(uint64_t a,uint64_t b,bool input=false,int* samples=nullptr) const;
    gm_measure instantaneous_strain(int i,const Neighbors& n) const;
    gm_measure measure(uint64_t id) const;
    std::vector<int> groups(double threshold,double link_factor) const;
    std::vector<double> readout(double x,double y,double width,double reach) const;
    int couplings() const; double cost() const;
    void configure(gm_growth config); void update_timers(); void apply_growth();
    std::vector<char> save() const; static Medium load(const void* data,size_t size);
    std::string event_json() const;
private:
    double random_angle();
};
void require(bool condition,const char* message);
void finite(double value);
}
