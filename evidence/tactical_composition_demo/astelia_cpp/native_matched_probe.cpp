#include "native/api.h"
#include "native/nearest_kernel.h"
#include <chrono>
#include <iomanip>
#include <iostream>
#include <tuple>
using namespace astelia;
// Complete hot authority, not a positions-only copy. Each member has its own
// typed column. Cold authority and grid rebuilding use production functions.
#define MEMBERS(X) X(Vec2,pos) X(Vec2,velocity) X(Vec2,smoothVelocity) X(double,hp) X(double,maxhp) X(double,radius) X(double,speed) X(double,range) X(double,damage) X(double,cooldown) X(UnitRef,target) X(UnitId,id) X(uint32_t,generation) X(uint8_t,team) X(Role,role) X(uint8_t,alive) X(uint8_t,occupied)
struct Columns {
#define DECL(T,n) std::vector<T> n;
  MEMBERS(DECL)
#undef DECL
  size_t size()const{return id.size();}
  explicit Columns(const std::vector<UnitHot>& src){for(const auto& u:src){
#define ADD(T,n) n.push_back(u.n);
    MEMBERS(ADD)
#undef ADD
  }}
  UnitHot operator[](size_t i)const{UnitHot u;
#define GET(T,n) u.n=n[i];
    MEMBERS(GET)
#undef GET
    return u;
  }
};
// Layout alternatives keep the same public query parameters and caller work.
// Runtime filters prevent the probe from specializing away production predicates.
template<class Storage> __attribute__((noinline)) UnitRef nearestLayout(const Storage& units,const World& w,uint32_t slot,bool outsideMinimum,bool meleeOnly,double maximum,double minimumHp){
  return nearestKernel(units,w.foes(w.units[slot].team),slot,w.state[slot].minRange,outsideMinimum,meleeOnly,maximum,minimumHp);
}
template<class T> bool same(T a,T b){return a==b;}
bool same(Vec2 a,Vec2 b){return a.x==b.x&&a.y==b.y;}
template<class F> void measure(const char* name,uint64_t operations,F fn){auto start=std::chrono::steady_clock::now();const double sum=fn();const auto seconds=std::chrono::duration<double>(std::chrono::steady_clock::now()-start).count();std::cout<<"{\"kind\":\""<<name<<"\",\"operations\":"<<operations<<",\"seconds\":"<<seconds<<",\"checksum\":"<<sum<<"}\n";}
World fixture(){auto c=gameConfig();c.seed=20261005;c.width=1200;c.height=800;c.dt=.03;c.duration=.3;auto w=create(c);
  for(size_t i=0;i<w.units.size();++i){auto& u=w.units[i];const size_t k=i%50;u.pos={460+(k%10)*28.0+u.team*25.0,90+(k/10)*75.0};w.state[i].previous=u.pos;u.velocity=u.smoothVelocity={};}
  w.liveGrid.build(w.units,w.active,1200,800,40);return w;
}
int main(){try{std::cout<<std::setprecision(17);auto w=fixture();const Columns source(w.units);volatile bool queryOutside=false,queryMelee=false;volatile double queryMaximum=INFINITY,queryMinimumHp=0;constexpr uint32_t geometryN=100000,networkN=20000,forkN=300,cloneN=20000;
  std::vector<double> x(46);for(size_t i=0;i<x.size();++i)x[i]=(int(i*17%101)-50)/50.0;const auto net=frozenNetwork();std::vector<double> hidden,scores;
  for(int cycle=0;cycle<2;++cycle)for(int layout:{0,1,2,2,1,0})measure(layout==0?"geometry_records":layout==1?"geometry_columns":"geometry_production",geometryN,[&](){double sum=0;for(uint32_t k=0;k<geometryN;++k){const uint32_t i=k%100;const bool outside=queryOutside,meleeOnly=queryMelee;const double maximum=queryMaximum,minimumHp=queryMinimumHp;const auto r=layout==0?nearestLayout(w.units,w,i,outside,meleeOnly,maximum,minimumHp):layout==1?nearestLayout(source,w,i,outside,meleeOnly,maximum,minimumHp):nearest(w,i,outside,meleeOnly,maximum,minimumHp);sum+=r?w.units[r.slot].id:0;}return sum;});
  measure("network",networkN,[&](){double sum=0;for(uint32_t k=0;k<networkN;++k){x[0]=(int(k%101)-50)/50.0;networkScores(*net,x,hidden,scores);sum+=scores[k%13];}return sum;});
  for(int j=0;j<30;++j){Shot shot;shot.pos={100,700};shot.source=w.reference(0);shot.target=w.reference(50);shot.direction={1,0};shot.speed=240;shot.left=.5;shot.ordinal=w.nextShot++;w.shots.push_back(shot);}
  measure("fork_playout",forkN,[&](){double sum=0;for(uint32_t k=0;k<forkN;++k){auto branch=fork(w);auto& c=branch.world();c.duration=.3;c.dt=.03;run(c);sum+=c.time+c.survivors(0)+c.survivors(1);}return sum;});
  std::cout<<"{\"kind\":\"fork_work\",\"forks\":"<<w.work->forks<<",\"steps\":"<<w.work->branchSteps<<",\"unit_actions\":"<<w.work->branchUnitActions<<",\"projectile_steps\":"<<w.work->branchProjectileSteps<<"}\n";
  // Populate every conditional-state family before the complete clone probe.
  const auto player=w.add(1,Role::Player,{1100,700});w.players[w.state[player.slot].player].manual=1;w.players[w.state[player.slot].player].manualTarget=w.reference(0);
  w.fields.push_back({{100,200},45,0,2,0});w.dots.push_back({w.reference(0),player,3,4,.1});w.spawnQueue.push_back({3,Role::Hunter});
  fireShot(w,10,w.reference(60));w.shots.back().hitSet.push_back(w.reference(61));fireShellAt(w,40,{700,200},12,true);w.packs[0].artilleryQueue.push_back({{700,300},w.reference(40),2,14,false,true});w.packs[0].cutOff.push_back(player);w.tactical[0].order={OrderKind::Attack,{},player,4,14};
  for(size_t i=0;i<w.state.size();++i)w.state[i].rolledShots.push_back(i+100);
  w.rebuildTeams();const Columns populated(w.units);World recordClone(w.config),columnAuthority(w.config);Columns columnClone(populated);
  for(int cycle=0;cycle<2;++cycle)for(bool records:{true,false,false,true})measure(records?"complete_clone_records":"complete_clone_columns",cloneN,[&](){double sum=0;for(uint32_t k=0;k<cloneN;++k){
    if(records){recordClone.copyFrom(w);sum+=recordClone.units[k%w.units.size()].hp+recordClone.players.size()+recordClone.packs[0].artilleryQueue.size();}
    else{columnAuthority.copyAuthorityFrom(w);columnClone=populated;for(auto& team:columnAuthority.teams)team.clear();for(auto i:columnAuthority.active)if(columnClone.alive[i])columnAuthority.teams[columnClone.team[i]].push_back(i);columnAuthority.liveGrid.buildStorage(columnClone,columnAuthority.active,1200,800,40);sum+=columnClone.hp[k%w.units.size()]+columnAuthority.players.size()+columnAuthority.packs[0].artilleryQueue.size();}}
    return sum;});
  for(size_t i=0;i<w.units.size();++i){const auto a=w.units[i],b=columnClone[i];
#define SAME(T,n) if(!same(a.n,b.n))throw std::runtime_error("column clone mismatch: " #n);
    MEMBERS(SAME)
#undef SAME
    if(a.pos.x!=b.pos.x||a.pos.y!=b.pos.y||a.velocity.x!=b.velocity.x||a.velocity.y!=b.velocity.y||a.smoothVelocity.x!=b.smoothVelocity.x||a.smoothVelocity.y!=b.smoothVelocity.y||a.target!=b.target)throw std::runtime_error("vector/ref clone mismatch");}
  columnAuthority.players[0].manualTarget={};columnAuthority.state[0].rolledShots.clear();columnAuthority.shots.back().hitSet.clear();columnAuthority.packs[0].artilleryQueue.clear();if(w.players[0].manualTarget!=w.reference(0)||w.state[0].rolledShots.empty()||w.shots.back().hitSet.empty()||w.packs[0].artilleryQueue.empty())throw std::runtime_error("column authority aliases parent");
  std::cout<<"{\"kind\":\"clone_equivalence\",\"passed\":true,\"hot_bytes\":"<<sizeof(UnitHot)<<",\"conditional_bytes\":"<<sizeof(UnitState)<<"}\n";
}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}
