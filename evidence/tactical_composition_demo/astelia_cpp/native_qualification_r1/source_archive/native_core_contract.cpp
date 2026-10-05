#include "native/world.h"
#include <iostream>
#include <sstream>
#include <string>

using namespace astelia;
namespace {
void require(bool b,const char* message) { if (!b) throw std::runtime_error(message); }
UnitHot body(UnitId id,Vec2 p,double r) {UnitHot u;u.id=id;u.pos=p;u.radius=r;u.alive=u.occupied=true;return u;}
UnitRef scanBlocker(const std::vector<UnitHot>& units,Vec2 a,Vec2 b,double targetRadius,UnitRef shooter,UnitRef target) {
  // Independent scalar/long-double oracle, without production geometry helpers.
  const long double dx=b.x-a.x,dy=b.y-a.y,l=std::hypot(dx,dy);
  if (l<1) return {};
  const long double nx=dx/l,ny=dy/l;long double best=l-targetRadius;UnitRef found;
  for (uint32_t i=0;i<units.size();++i) {
    const auto& u=units[i];UnitRef ref{i,u.generation};
    if (!u.alive || ref==shooter || ref==target) continue;
    const long double px=u.pos.x-a.x,py=u.pos.y-a.y,t=px*nx+py*ny;
    if (t<=0 || t>best || std::abs(px*ny-py*nx)>=u.radius+1.5L) continue;
    if (t<best || (found && t==best && u.id<units[found.slot].id)) {found=ref;best=t;}
  }
  return found;
}
std::vector<Vec2> scanSeparate(const std::vector<UnitHot>& units,double width,double height) {
  std::vector<Vec2> out(units.size()),push(units.size());
  for (size_t i=0;i<units.size();++i) if (units[i].alive) {
    for (size_t j=i+1;j<units.size();++j) if (units[j].alive) {
      const double dx=units[j].pos.x-units[i].pos.x,dy=units[j].pos.y-units[i].pos.y;
      const double l=std::hypot(dx,dy),r=units[i].radius+units[j].radius;
      if (l>=r || l==0) continue;
      const double x=dx/l*(r-l)/2,y=dy/l*(r-l)/2;
      push[i].x-=x;push[i].y-=y;push[j].x+=x;push[j].y+=y;
    }
    out[i]=units[i].pos;
  }
  for (size_t i=0;i<units.size();++i) if (units[i].alive) {
    out[i].x=std::max(units[i].radius,std::min(width-units[i].radius,units[i].pos.x+push[i].x));
    out[i].y=std::max(units[i].radius,std::min(height-units[i].radius,units[i].pos.y+push[i].y));
  }
  return out;
}
std::string snapshot(const World& w) {
  std::ostringstream s;s.precision(17);s<<w.time<<' '<<w.random.state<<' '<<w.nextId;
  for (const auto& u:w.units) if (u.occupied) s<<' '<<u.id<<' '<<u.pos.x<<' '<<u.pos.y<<' '<<u.hp<<' '<<u.cooldown<<' '<<u.target.slot<<' '<<u.target.generation;
  for (const auto& p:w.shots) s<<' '<<p.pos.x<<' '<<p.pos.y<<' '<<p.left;
  s<<' '<<w.stats.melee<<' '<<w.stats.ranged<<' '<<w.stats.artillery;return s.str();
}
void geometry() {
  std::vector<UnitHot> units{body(1,{20,53},8),body(2,{200,53},6),body(3,{100,39},16)};
  std::vector<uint32_t> active{0,1,2};SpatialGrid grid;
  grid.build(units,active,400,200,40);
  require(lineBlocker(units,grid,{20,53},{200,53},6,{0,1},{1,1})==UnitRef{2,1},"radius-16 blocker omitted");
  units[2].pos={100,150};grid.moved(2,units[2].pos);
  require(!lineBlocker(units,grid,{20,53},{200,53},6,{0,1},{1,1}),"moved blocker remained in lane");
  units[2].pos={100,39};grid.moved(2,units[2].pos);units[2].alive=false;
  require(!lineBlocker(units,grid,{20,53},{200,53},6,{0,1},{1,1}),"dead blocker remained in lane");
  units={body(1,{23,100},16),body(2,{48,100},16)};active={0,1};std::vector<Vec2> pushes;
  separate(units,active,grid,400,200,pushes);
  require(std::abs(units[0].pos.x-19.5)<1e-12 && std::abs(units[1].pos.x-51.5)<1e-12,"radius-16 separation pair omitted");
  units={body(1,{100,100},16),body(2,{100,100},16)};
  separate(units,active,grid,400,200,pushes);require(units[0].pos.x==100 && units[1].pos.x==100,"coincident-center policy changed");
  // Overflow/sparse cells must not alias (0,4096) and (1,0).
  units={body(1,{0,163840},1),body(2,{40,0},1)};
  grid.build(units,active,1e9,1e9,40);std::vector<uint32_t> got;
  grid.query({-1,163839},{1,163841},[&](auto i){got.push_back(i);});
  require(got==std::vector<uint32_t>{0},"cell-coordinate alias");
  Rng random(20261004);
  for (int trial=0;trial<64;++trial) {
    units.clear();active.clear();
    for (uint32_t i=0;i<80;++i) {units.push_back(body(i+1,{random()*600-100,random()*600-100},random()*40+.25));active.push_back(i);}
    grid.build(units,active,400,400,40);
    for (int q=0;q<24;++q) {
      const Vec2 a{random()*400,random()*400},b{random()*400,random()*400};
      require(lineBlocker(units,grid,a,b,0,{},{})==scanBlocker(units,a,b,0,{},{}),"blocker differs from independent scan");
    }
    const auto expected=scanSeparate(units,400,400);separate(units,active,grid,400,400,pushes);
    for (size_t i=0;i<units.size();++i) require(std::hypot(units[i].pos.x-expected[i].x,units[i].pos.y-expected[i].y)<1e-9,"separation differs from all-pair oracle");
  }
  require(length({1e300,1e300})>1e300 && std::isfinite(length({1e300,1e300})),"length overflow");
  require(length({1e-300,1e-300})>1e-300,"length underflow");
}
void lifecycle() {
  auto c=std::make_shared<Config>(sandboxConfig());c->army={0,0,0};World w(c);
  auto a=w.add(0,Role::Melee,{100,100}),b=w.add(1,Role::Melee,{130,100});w.rebuildTeams();
  w.damage(a,b,1000);w.reclaim();require(!w.resolve(b),"unreferenced dead slot retained");
  auto replacement=w.add(1,Role::Ranged,{130,100});
  require(replacement.slot==b.slot && replacement.generation!=b.generation,"dead slot not safely reused");
  require(!w.resolve(b) && w.resolve(replacement),"stale handle resolved replacement");
  // A dead source remains available until its projectile is retired.
  Shot shot;shot.source=a;shot.target=replacement;w.shots.push_back(shot);w.units[a.slot].alive=false;w.reclaim();
  require(w.resolve(a),"projectile source reclaimed while referenced");w.shots.clear();w.reclaim();require(!w.resolve(a),"projectile source not reclaimed after retirement");
  for (int i=0;i<1000;++i) {auto u=w.add(0,Role::Melee,{100,100});w.units[u.slot].alive=false;w.reclaim();}
  require(w.units.size()<=3,"slot storage grows with historical spawns");

  // Exercise slot reuse through the live index, not only handle resolution.
  w.units[replacement.slot].alive=false;w.reclaim();
  auto target=w.add(1,Role::Melee,{200,100});
  auto shooter=w.add(0,Role::Ranged,{20,100});w.rebuildTeams();
  w.liveGrid.build(w.units,w.active,400,400,40);
  for (int i=0;i<1000;++i) {
    auto blocker=w.add(1,Role::Melee,{100,100});
    require(lineBlocker(w.units,w.liveGrid,{20,100},{200,100},8,shooter,target)==blocker,"spawn absent from live grid");
    w.move(blocker.slot,{100,180},1);
    require(!lineBlocker(w.units,w.liveGrid,{20,100},{200,100},8,shooter,target),"spawn move leaves stale blocker");
    w.units[blocker.slot].alive=false;w.reclaim();
    require(!w.liveGrid.contains(blocker.slot),"dead slot remains indexed");
  }
  require(w.units.size()<=4,"live grid stress grows historical slot storage");
}
void numericalLimits() {
  auto c=std::make_shared<Config>(sandboxConfig());c->army={1,1,0};c->dt=1e-310;c->duration=1e-309;
  auto tiny=World::create(c);coreStep(tiny);
  for (auto i:tiny.active) {
    const auto& u=tiny.units[i];const auto& s=tiny.state[i];
    require(std::isfinite(u.velocity.x) && std::isfinite(u.velocity.y) && std::isfinite(u.smoothVelocity.x) &&
      std::isfinite(u.smoothVelocity.y) && std::isfinite(s.longVelocity.x) && std::isfinite(s.longSpeed),"subnormal dt creates invalid motion state");
  }
  c=std::make_shared<Config>(sandboxConfig());c->army={1,1,0};c->dt=1e308;c->duration=1e308;
  auto huge=World::create(c);bool overflow=false;
  try {coreStep(huge);} catch (const std::overflow_error&) {overflow=true;}
  require(overflow,"aggregate overflow silently accepted");
  c=std::make_shared<Config>(sandboxConfig());c->army={1,1,0};
  auto fresh=World::create(c);fresh.move(fresh.active[0],{600,400},.1);
}
void effectForks() {
  auto c=std::make_shared<Config>(sandboxConfig());c->army={0,0,0};c->dt=.1;
  World w(c);auto source=w.add(0,Role::Ranged,{100,100}),target=w.add(1,Role::Melee,{500,100});w.rebuildTeams();
  Shot shot;shot.pos={100,100};shot.direction={1,0};shot.source=source;shot.target=target;
  shot.speed=100;shot.left=100;shot.damage=1;shot.hitSet={source};w.shots.push_back(shot);
  Shell shell;shell.source=source;shell.pos={500,100};shell.at=5;w.shells.push_back(shell);
  w.fields.push_back({{100,100},40,0,5,0});w.dots.push_back({source,target,1,5,.5});
  w.hitLog.push_back({0,3,0,1});w.state[source.slot].energy=17;
  const auto initial=snapshot(w);BranchPool pool;
  {
    auto a=pool.fork(w);coreStep(a.world());
    require(a.world().counters.branchSteps==1 && a.world().counters.projectileSteps>0,"effect fork executed no projectile work");
    const double accumulation=a.world().dots[0].accumulated;
    auto b=pool.fork(a.world());
    b.world().shots[0].hitSet.push_back(target);b.world().shells[0].damage=9;
    b.world().fields[0].until=99;b.world().dots[0].accumulated=12;
    b.world().hitLog[0].amount=7;b.world().state[source.slot].energy=2;
    require(a.world().shots[0].hitSet.size()==1 && a.world().shells[0].damage==0 && a.world().fields[0].until==5 &&
      a.world().dots[0].accumulated==accumulation && a.world().hitLog[0].amount==3 && a.world().state[source.slot].energy==17,
      "nested effect fork shares mutable authority");
    require(snapshot(w)==initial && w.shots[0].hitSet.size()==1 && w.fields[0].until==5 && w.dots[0].accumulated==.5,
      "effect branch changes parent");
  }
  auto reused=pool.fork(w);
  require(snapshot(reused.world())==initial && reused.world().shots[0].hitSet.size()==1 && reused.world().fields[0].until==5 &&
    reused.world().dots[0].accumulated==.5 && reused.world().state[source.slot].energy==17,"reused branch leaks effect state");
}
void projectileOracle() {
  auto c=std::make_shared<Config>(sandboxConfig());c->army={0,0,0};c->dt=.1;c->width=c->height=500;
  for (auto& role:c->roles) role.speed=0;
  Rng random(2026100410);
  for (int trial=0;trial<8;++trial) {
    World w(c);std::vector<double> expected;
    for (uint32_t i=0;i<80;++i) {
      auto u=w.add(i%2,Role::Ranged,{40+random()*420,40+random()*420});
      w.units[u.slot].radius=.25+random()*39.75;w.units[u.slot].cooldown=1e9;expected.push_back(w.units[u.slot].hp);
    }
    double expectedDamage=0,expectedWaste=0;
    for (int q=0;q<16;++q) {
      Shot shot;shot.source=w.reference(0);shot.pos={random()*500,random()*500};
      const double angle=random()*6.283185307179586;shot.direction={std::cos(angle),std::sin(angle)};
      shot.left=100+random()*300;shot.speed=shot.left/c->dt;shot.damage=1;
      const long double segment=std::min(shot.left,shot.speed*c->dt);long double nearest=INFINITY;
      uint32_t hit=invalidSlot;
      // Independent closest-point scan; no production geometry/grid helpers.
      for (uint32_t i=1;i<w.units.size();++i) {
        const auto& u=w.units[i];const long double x=u.pos.x-shot.pos.x,y=u.pos.y-shot.pos.y;
        const long double along=std::max(0.L,std::min(segment,x*shot.direction.x+y*shot.direction.y));
        if (std::hypot(x-along*shot.direction.x,y-along*shot.direction.y)<=u.radius &&
            (along<nearest || (along==nearest && i<hit))) {nearest=along;hit=i;}
      }
      if (hit!=invalidSlot && w.units[hit].team==1) {--expected[hit];++expectedDamage;}
      else if (hit!=invalidSlot || shot.left<=shot.speed*c->dt) ++expectedWaste;
      w.shots.push_back(shot);
    }
    w.rebuildTeams();coreStep(w);
    for (size_t i=0;i<expected.size();++i) require(w.units[i].hp==expected[i],"shot damage differs from independent body scan");
    require(w.stats.ranged==expectedDamage && w.stats.wasted==expectedWaste,"shot ownership/waste differs from oracle");
  }
  c->roles[size_t(Role::Melee)].radius=16;
  World w(c);auto source=w.add(0,Role::Ranged,{20,76}),target=w.add(1,Role::Ranged,{200,76}),blocker=w.add(1,Role::Melee,{100,60});
  for (auto i:w.active) w.units[i].cooldown=1e9;
  Shot shot;shot.source=source;shot.target=target;shot.pos={20,76};shot.direction={1,0};shot.speed=2000;shot.left=200;shot.damage=8;
  w.shots.push_back(shot);w.rebuildTeams();coreStep(w);
  require(w.units[blocker.slot].hp==292 && w.units[target.slot].hp==90,"radius-16 shot-cell boundary omitted");
}
void worlds() {
  auto c=std::make_shared<Config>(sandboxConfig());c->army={2,4,2};c->width=650;c->duration=2;
  auto w=World::create(c),repeat=World::create(c);BranchPool pool;
  const auto initial=snapshot(w);
  {
    auto a=pool.fork(w);coreStep(a.world());
    auto b=pool.fork(a.world());coreStep(b.world());
    require(a.world().time==c->dt && b.world().time==2*c->dt,"nested branch overwrote parent lease");
    require(snapshot(w)==initial,"branch mutated original world");
    require(a.world().config==w.config && &a.world().units[0]!=&w.units[0],"mutable fork state shared");
    a.world().random();require(w.random.state!=a.world().random.state,"branch RNG shared");
  }
  {
    auto a=pool.fork(w);require(snapshot(a.world())==initial,"reused branch retains previous state");
  }
  while (!w.done()) {coreStep(w);coreStep(repeat);}
  require(snapshot(w)==snapshot(repeat),"fresh replay differs");
  require(w.counters.outerSteps>0 && w.counters.unitActions>0,"core did no combat work");
  for (auto i:w.active) {require(std::isfinite(w.units[i].hp) && w.units[i].hp>0,"invalid live HP");validateBody(w.units[i]);}
  Rng r(1);require(r()==270369.0/4294967296.0,"xorshift seed conversion");
  require(toUint32(-1)==0xffffffffU && toUint32(4294967297.0)==1,"ToUint32 wrapping");
}
} // namespace
int main() {
  try {geometry();lifecycle();numericalLimits();effectForks();projectileOracle();worlds();std::cout<<"native core contracts passed\n";return 0;}
  catch (const std::exception& e) {std::cerr<<e.what()<<'\n';return 1;}
}
