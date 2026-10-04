#include "formation.h"

namespace astelia {
namespace {
constexpr double pi=3.1415926535897932384626433832795;
template<class Predicate> UnitRef nearestTo(const World& w,Vec2 from,const std::vector<uint32_t>& list,Predicate accept) {
  UnitRef best;double bd=INFINITY;for(auto i:list){const auto& u=w.units[i];if(!u.alive||!accept(i))continue;
    const double d=distance(from,u.pos);if(d<bd){bd=d;best=w.reference(i);}}return best;
}
UnitRef nearestTo(const World& w,Vec2 from,const std::vector<uint32_t>& list) {
  return nearestTo(w,from,list,[](uint32_t){return true;});
}
double maxDepth(const std::vector<Vec2>& slots,double fallback){double d=-INFINITY;for(auto p:slots)d=std::max(d,p.x);return slots.empty()?fallback:d;}
std::vector<Vec2> row(uint32_t n,double spacing,double depth,double stagger=0){
  std::vector<Vec2> out;out.reserve(n);for(uint32_t i=0;i<n;++i)out.push_back({depth,(double(i)-(double(n)-1)/2)*spacing+stagger});return out;
}
std::vector<Vec2> ranks(uint32_t n,uint32_t per,double spacing,double depth,double rankSpacing){
  std::vector<Vec2> out;out.reserve(n);for(uint32_t r=0;out.size()<n;++r){const auto k=std::min(per,n-uint32_t(out.size()));
    const auto add=row(k,spacing,depth+r*rankSpacing,r%2?spacing/2:0);out.insert(out.end(),add.begin(),add.end());}return out;
}
void append(std::vector<Vec2>& a,const std::vector<Vec2>& b){a.insert(a.end(),b.begin(),b.end());}
ShapeSlots makeShape(const std::array<uint32_t,3>& n,const Formation& f){
  ShapeSlots out;auto& m=out.role[0];auto& r=out.role[1];auto& a=out.role[2];
  switch(f.shape){
    case Shape::Line:{const auto per=std::max(1u,uint32_t(std::ceil(n[1]/f.rangedRanks)));
      m=row(n[0],f.frontSpacing,0);r=ranks(n[1],per,f.rankSpacing,f.screenGap,f.rankSpacing);
      a=row(n[2],f.frontSpacing*1.4,f.screenGap+f.rankSpacing*f.rangedRanks+f.rearGap);break;}
    case Shape::Wedge:{if(n[0])m.push_back({0,0});for(uint32_t i=1;m.size()<n[0];++i){m.push_back({i*f.frontSpacing*.55,i*f.frontSpacing*.8});if(m.size()<n[0])m.push_back({i*f.frontSpacing*.55,-double(i)*f.frontSpacing*.8});}
      for(uint32_t i=0;r.size()<n[1];++i)append(r,row(std::min(3+i*2,n[1]-uint32_t(r.size())),f.rankSpacing,f.screenGap+i*f.rankSpacing*.8));
      a=row(n[2],f.frontSpacing*1.2,maxDepth(r,f.screenGap)+f.rearGap);break;}
    case Shape::Box:{const double half=3.5*f.rankSpacing+f.frontSpacing*.8;const uint32_t front=(n[0]+1)/2,side=n[0]-front;
      m=row(front,half*2/std::max(1.0,double(front)-1),0);for(uint32_t i=0;i<side;++i)m.push_back({f.screenGap+(std::floor(i/2.0)+.5)*f.rankSpacing*1.5,i%2?-half:half});
      r=ranks(n[1],8,f.rankSpacing,f.screenGap,f.rankSpacing);a=row(n[2],f.rankSpacing*1.3,f.screenGap+std::ceil(n[1]/8.0)*f.rankSpacing+f.rearGap*.6);break;}
    case Shape::Column:m=ranks(n[0],5,f.frontSpacing*.7,0,f.rankSpacing);r=ranks(n[1],5,f.rankSpacing,f.screenGap+f.rankSpacing,f.rankSpacing);
      a=ranks(n[2],5,f.rankSpacing*1.2,maxDepth(r,f.screenGap)+f.rearGap,f.rankSpacing);break;
    case Shape::Screen:{m=ranks(n[0],5,f.frontSpacing*.6,0,f.rankSpacing);const uint32_t half=(n[1]+1)/2;const double off=5*f.frontSpacing*.6/2+3*f.rankSpacing;
      r=ranks(half,5,f.rankSpacing,f.screenGap*.6,f.rankSpacing);for(auto& s:r)s.y-=off;
      auto right=ranks(n[1]-half,5,f.rankSpacing,f.screenGap*.6,f.rankSpacing);for(auto& s:right)s.y+=off;append(r,right);
      a=row(n[2],f.frontSpacing*1.2,maxDepth(r,f.screenGap)+f.rearGap);break;}
    case Shape::Crescent:{const double radius=std::max(80.0,f.frontSpacing*n[0]/2);
      const auto arc=[&](uint32_t count,double depth,double spread){std::vector<Vec2> out;out.reserve(count);for(uint32_t i=0;i<count;++i){const double angle=count==1?0:(double(i)/(count-1)-.5)*spread;
        out.push_back({depth-radius*(1-std::cos(angle)),radius*std::sin(angle)});}return out;};
      m=arc(n[0],0,1.8);r=arc((n[1]+1)/2,f.screenGap,1.6);append(r,arc(n[1]/2,f.screenGap+f.rankSpacing,1.5));
      a=row(n[2],f.frontSpacing*1.2,f.screenGap+f.rankSpacing*2+f.rearGap);break;}
    case Shape::Ring:{const double radius=std::max(90.0,10*f.frontSpacing/(pi*2)*1.6);
      const auto circle=[&](uint32_t count,double rad){std::vector<Vec2> out;out.reserve(count);for(uint32_t i=0;i<count;++i){const double angle=double(i)/std::max(1u,count)*pi*2;
        out.push_back({radius-std::cos(angle)*rad,std::sin(angle)*rad});}return out;};
      m=circle(n[0],radius);const uint32_t inner=uint32_t(std::ceil(n[1]*.6));r=circle(inner,radius-26);append(r,circle(n[1]-inner,radius-48));a=circle(n[2],26);break;}
  }
  for(auto& list:out.role)std::stable_sort(list.begin(),list.end(),[](Vec2 a,Vec2 b){return a.y!=b.y?a.y<b.y:a.x<b.x;});return out;
}
double lateral(const Pack& p,Vec2 pos){const auto d=pos-p.anchor;return -d.x*p.facing.y+d.y*p.facing.x;}
double depth(const Pack& p,Vec2 pos){return -dot(pos-p.anchor,p.facing);}
Vec2 centroid(const World& w,const std::vector<uint32_t>& list){Vec2 c;uint32_t n=0;for(auto i:list)if(w.units[i].alive){c=c+w.units[i].pos;++n;}return c*(1.0/std::max(1u,n));}
UnitRef meleeAnswer(const World& w,uint32_t i){const auto& s=w.state[i];const auto* a=w.resolve(s.meleeAttacker);
  return a&&a->alive&&w.time-s.meleeAt<1&&gap(*a,w.units[i])<24?s.meleeAttacker:UnitRef{};}
void positionAnchor(World& w,uint8_t team){
  auto& p=w.packs[team];const auto& f=p.formation;const auto& ms=w.teams[team];const auto& es=w.foes(team);
  const auto* place=placeGoal(w,team);if(place){auto near=nearestTo(w,p.anchor,es);const auto* enemy=w.resolve(near);const auto face=place->hasFace?place->face:enemy?enemy->pos:p.anchor;
    const auto delta=face-p.anchor;const double l=length(delta);p.facing=p.facing+(delta*(1/(l>0?l:1))-p.facing)*f.turnRate;
    const double fl=length(p.facing);p.facing=p.facing*(1/(fl>0?fl:1));const auto move=place->point-p.anchor;const double d=length(move);
    if(d>1)p.anchor=p.anchor+move*(std::min(d,paceOf(w,team)*.9*w.config->dt)/d);p.phase=PackPhase::Ordered;p.waiting=false;return;}
  const auto* engage=engageGoal(w,team);const auto center=centroid(w,ms);auto near=engage?nearestTo(w,center,es,[&](uint32_t i){return containsId(engage,w.units[i].id);}):UnitRef{};
  if(!near)near=nearestTo(w,center,es);const auto& shape=p.shape;
  const double rear=maxDepth(shape.role[1],0);p.waiting=false;
  if(f.oblique&&es.size()>2&&near&&!engage){auto lo=es[0],hi=es[0];for(auto i:es){if(lateral(p,w.units[i].pos)<lateral(p,w.units[lo].pos))lo=i;if(lateral(p,w.units[i].pos)>lateral(p,w.units[hi].pos))hi=i;}
    const auto crowd=[&](uint32_t i){uint32_t n=0;for(auto j:es)if(distance(w.units[j].pos,w.units[i].pos)<250)++n;return n;};near=w.reference(crowd(lo)<=crowd(hi)?lo:hi);}
  if(near){const auto& nearest=w.units[near.slot];Vec2 aim;double closing=0;uint32_t n=0;
    for(auto i:es)if(distance(w.units[i].pos,nearest.pos)<250){aim=aim+w.units[i].pos;closing-=dot(w.units[i].velocity,p.facing);++n;}
    aim=aim*(1.0/n);closing/=n;
    if(f.anchorMode==AnchorMode::Siege){Vec2 fire;uint32_t count=0;for(auto i:es)if(!melee(w.units[i].role)){fire=fire+w.units[i].pos;++count;}if(count)aim=fire*(1.0/count);}
    const auto delta=aim-p.anchor;const double l=length(delta);p.facing=p.facing+(delta*(1/(l>0?l:1))-p.facing)*f.turnRate;
    const double fac=length(p.facing);p.facing=p.facing*(1/(fac>0?fac:1));
    const double front=dot(nearest.pos-p.anchor,p.facing),maximum=(f.anchorSpeed>0?f.anchorSpeed:paceOf(w,team)*.9)*w.config->dt;
    double step=0;
    if(f.anchorMode==AnchorMode::Siege){const bool unscreened=p.members[0].size()<3;double danger=-INFINITY;Vec2 away;
      for(auto i:es){const auto& e=w.units[i];if(melee(e.role)&&!unscreened)continue;for(auto j:ms){const auto& m=w.units[j];if(!m.alive)continue;
        const double reach=melee(e.role)?f.meleeKeepAway:e.range+(e.role==Role::Artillery?(m.role==Role::Artillery?f.siegeOwnArtMargin:f.siegeArtMargin):f.siegeMargin);
        const double d=distance(e.pos,m.pos),v=reach-d;danger=std::max(danger,v);if(v>0)away=away+(m.pos-e.pos)*(v/(d>0?d:1));}}
      const double artReach=front+maxDepth(shape.role[2],rear)-(reachOf(w,team,Role::Artillery)-15);
      step=danger>0?-std::min(danger,maximum):artReach>0?std::min(artReach,maximum):0;
      p.phase=step<0?PackPhase::GivingGround:step>0?PackPhase::Creeping:PackPhase::Siege;
      if(step<0){if(p.retreatSince<0){p.retreatSince=w.time;p.retreatDanger=danger;}}else p.retreatSince=-1;
      p.caught=p.retreatSince>=0&&w.time-p.retreatSince>1.5&&danger>p.retreatDanger+5;
      const double al=length(away);p.hasAway=danger>0&&al>0;
      if(p.hasAway){p.away=away*(1/al);const double twice=length(p.away);p.away=p.away*(1/(twice>0?twice:1));}
    }else{const double err=front+rear-reachOf(w,team,Role::Ranged)*f.standoff;const bool gate=!f.syncGate||p.formed||front>w.config->roles[4].range+60;
      p.waiting=f.holdWhileClosing&&closing>f.closingSpeed&&front<reachOf(w,1-team,Role::Artillery)+60;
      step=err<=0||!gate||p.waiting?0:std::min(err,maximum);p.phase=!gate?PackPhase::Forming:p.waiting?PackPhase::Waiting:err>0?PackPhase::Advancing:PackPhase::Holding;}
    Vec2 motion=p.facing*step;if(step<0&&p.hasAway)motion=p.away*(-step);
    if(step<0){const auto far=p.anchor+motion*40;
      if(far.x<110||far.x>w.config->width-110||far.y<110||far.y>w.config->height-110){const auto unit=motion*(1/std::abs(step));const Vec2 tangent{-unit.y,unit.x};
        const double side=dot(Vec2{w.config->width/2,w.config->height/2}-p.anchor,tangent)>=0?1:-1;motion=tangent*(side*std::abs(step));}}
    p.anchor=p.anchor+motion;
  }else if(w.config->rules==Rules::Game&&w.config->perception&&w.survivors(1-team)){
    p.anchor=p.anchor+p.facing*((f.anchorSpeed>0?f.anchorSpeed:paceOf(w,team)*.9)*w.config->dt);p.phase=PackPhase::Searching;}
  p.anchor={clamp(p.anchor.x,60,w.config->width-60),clamp(p.anchor.y,60,w.config->height-60)};
}
void assignSlots(World& w,uint8_t team){
  auto& p=w.packs[team];const auto& f=p.formation;const Vec2 perpendicular{-p.facing.y,p.facing.x};
  for(size_t r=0;r<3;++r){auto members=p.members[r];std::stable_sort(members.begin(),members.end(),[&](uint32_t a,uint32_t b){
    const double la=lateral(p,w.units[a].pos),lb=lateral(p,w.units[b].pos);return la!=lb?la<lb:depth(p,w.units[a].pos)<depth(p,w.units[b].pos);});
    for(size_t j=0;j<members.size();++j){auto& s=w.state[members[j]];const auto slot=p.shape.role[r][j];s.slot=p.anchor-p.facing*slot.x+perpendicular*slot.y;s.hasSlot=true;}}
  double off=0,minD=INFINITY,maxD=-INFINITY,minL=INFINITY,maxL=-INFINITY;
  for(auto i:w.teams[team])if(w.units[i].alive)off=std::max(off,distance(w.state[i].slot,w.units[i].pos));
  p.formed=off<f.syncRadius||(p.formed&&off<f.syncRadius*4);
  for(const auto& list:p.shape.role)for(auto s:list){minD=std::min(minD,s.x);maxD=std::max(maxD,s.x);minL=std::min(minL,s.y);maxL=std::max(maxL,s.y);}
  p.zoneFront=minD-f.zoneDepth;p.zoneBack=maxD+f.zoneBehind;p.zoneMinL=minL-f.zoneSideMargin;p.zoneMaxL=maxL+f.zoneSideMargin;
  p.cover=p.members[1].empty()?p.anchor:centroid(w,p.members[1]);p.coverRadius=reachOf(w,team,Role::Ranged)*f.coverFraction;
}
void meleeOrders(World& w,uint8_t team){
  auto& p=w.packs[team];const auto& f=p.formation;const auto& es=w.foes(team);const auto& ms=p.members[0];
  bool enemyNear=false,coming=false,exposed=true;uint32_t softN=0;Vec2 soft;
  for(auto i:es){const auto& e=w.units[i];if(melee(e.role)){if(inZone(w,team,i)||distance(e.pos,p.anchor)<f.zoneDepth+60)enemyNear=true;
      if(distance(e.pos,p.anchor)<=f.diveRange+200&&!pinned(w,i))coming=true;if(!pinned(w,i)&&distance(e.pos,p.anchor)<=f.diveRange+200)exposed=false;}
    else{soft=soft+e.pos;++softN;}}
  uint32_t inReach=0;for(auto i:es)if(!melee(w.units[i].role)&&-depth(p,w.units[i].pos)>0&&-depth(p,w.units[i].pos)<=f.diveRange)++inReach;
  p.diving=f.dive&&f.meleeDoctrine!=MeleeDoctrine::Screen&&!enemyNear&&!ms.empty()&&inReach>=f.diveMinTargets;
  const auto doctrine=f.meleeDoctrine==MeleeDoctrine::Auto?(p.flank!=FlankPhase::None?f.autoAttack:coming?MeleeDoctrine::Screen:f.autoAttack):f.meleeDoctrine;
  if(softN)soft=soft*(1.0/softN);exposed=exposed&&softN>=f.diveMinTargets;
  p.wings.erase(std::remove_if(p.wings.begin(),p.wings.end(),[&](const Wing& a){const auto* u=w.resolve(a.unit);return !u||!u->alive;}),p.wings.end());
  if(p.flankStart&&p.wings.size()<p.flankStart/2.0){p.raidSpent=true;p.flank=FlankPhase::None;p.flankSince=w.time;p.wings.clear();p.flankStart=0;}
  if((doctrine==MeleeDoctrine::Flank||doctrine==MeleeDoctrine::Anvil)&&p.flank==FlankPhase::None&&!p.raidSpent&&(exposed||(f.flankForce&&softN))){
    auto sorted=ms;std::stable_sort(sorted.begin(),sorted.end(),[&](uint32_t a,uint32_t b){return lateral(p,w.units[a].pos)<lateral(p,w.units[b].pos);});
    const size_t k=sorted.size()/(doctrine==MeleeDoctrine::Flank?2:4);std::vector<Wing> wings;
    for(size_t j=0;j<sorted.size();++j)if(j<k)wings.push_back({w.reference(sorted[j]),-1});else if(j>=sorted.size()-k)wings.push_back({w.reference(sorted[j]),1});
    if(wings.size()>=2){p.wings=std::move(wings);p.flank=FlankPhase::Out;p.flankSince=w.time;p.flankStart=uint32_t(p.wings.size());p.flankStarted=true;}}
  if(p.flank!=FlankPhase::None&&(!softN||p.wings.empty()||(doctrine!=MeleeDoctrine::Flank&&doctrine!=MeleeDoctrine::Anvil))){p.flank=FlankPhase::None;p.flankSince=w.time;p.wings.clear();p.flankStart=0;}
  const Vec2 perpendicular{-p.facing.y,p.facing.x};
  const auto way=[&](int side){return p.flank==FlankPhase::Out?p.anchor+perpendicular*(side*((p.zoneMaxL-p.zoneMinL)/2+f.flankWidth*.5)):
    soft+perpendicular*(side*f.flankWidth)+p.facing*f.flankDepth;};
  if(!p.wings.empty()){bool arrived=true;for(const auto& wing:p.wings)if(distance(w.units[wing.unit.slot].pos,way(wing.side))>=50)arrived=false;
    if(p.flank==FlankPhase::Out&&(arrived||w.time-p.flankSince>f.flankWait)){p.flank=FlankPhase::Along;p.flankSince=w.time;}
    else if(p.flank==FlankPhase::Along&&(arrived||w.time-p.flankSince>f.flankWait)){p.flank=FlankPhase::Strike;p.flankSince=w.time;}
    for(const auto& wing:p.wings){const auto i=wing.unit.slot;auto& t=w.tactical[i];t.wing=wing.side;t.assignedSet=true;t.assigned=meleeAnswer(w,i);t.answering=bool(t.assigned);t.hasFlankGoal=false;
      if(t.assigned)continue;if(p.flank==FlankPhase::Strike){const auto* target=w.resolve(w.units[i].target);if(target&&target->alive)t.assigned=w.units[i].target;
        if(!t.assigned&&f.flankTarget==SoftTarget::Artillery)t.assigned=nearestTo(w,w.units[i].pos,es,[&](uint32_t e){return w.units[e].role==Role::Artillery;});
        if(!t.assigned)t.assigned=nearestTo(w,w.units[i].pos,es,[&](uint32_t e){return !melee(w.units[e].role);});if(!t.assigned)t.assigned=nearestTo(w,w.units[i].pos,es);
      }else{t.assigned={};t.flankGoal=way(wing.side);t.hasFlankGoal=true;}}}
  std::vector<uint32_t> claims(w.units.size(),0),centre;
  const auto eligible=[&](uint32_t e,uint32_t m){const auto& h=w.units[e];if(doctrine==MeleeDoctrine::Screen)return gap(h,w.units[m])<30||threatens(w,team,e);
    return inZone(w,team,e)||(p.diving&&-depth(p,h.pos)<=f.diveRange&&depth(p,h.pos)<p.zoneBack&&lateral(p,h.pos)>=p.zoneMinL-120&&lateral(p,h.pos)<=p.zoneMaxL+120);};
  for(auto i:ms){auto& t=w.tactical[i];if(std::any_of(p.wings.begin(),p.wings.end(),[&](const Wing& wing){return wing.unit==w.reference(i);}))continue;
    t.wing=0;t.hasFlankGoal=false;t.assigned=meleeAnswer(w,i);t.answering=bool(t.assigned);t.assignedSet=true;centre.push_back(i);
    const auto target=w.units[i].target;const auto* old=w.resolve(target);if(!t.assigned&&old&&old->alive&&eligible(target.slot,i))t.assigned=target;if(t.assigned)++claims[t.assigned.slot];}
  for(auto i:centre){auto& t=w.tactical[i];if(t.assigned)continue;double best=INFINITY;
    for(auto e:es){if(!eligible(e,i)||claims[e]>=f.maxStrikersPerTarget)continue;const double k=(threatens(w,team,e)?0:1e5)+distance(w.units[e].pos,w.units[i].pos);
      if(k<best){best=k;t.assigned=w.reference(e);}}if(t.assigned)++claims[t.assigned.slot];}
}
void focusOrders(World& w,uint8_t team){
  auto& p=w.packs[team];const auto& f=p.formation;const auto& es=w.foes(team);const auto& ranged=p.members[1];
  const auto pick=[&](const std::vector<uint32_t>& list){UnitRef best;double bk=INFINITY;
    for(auto e:es){uint32_t n=0;for(auto r:list)if(gap(w.units[r],w.units[e])<=w.units[r].range)++n;if(!n)continue;
      const double left=w.units[e].hp-p.pending[e],k=(threatens(w,team,e)?0:1e6)+(left<=0?5e5:0)+left/n;
      if(k<bk){bk=k;best=w.reference(e);}}return best;};
  p.focus=f.shooterFocus==ShooterFocus::One?pick(ranged):UnitRef{};
  for(auto i:ranged)w.tactical[i].squadFocus={};if(w.config->skills[team].leaderFire)leaderFire(w,team);
  if(f.shooterFocus==ShooterFocus::Squads){auto sorted=ranged;std::stable_sort(sorted.begin(),sorted.end(),[&](uint32_t a,uint32_t b){return lateral(p,w.units[a].pos)<lateral(p,w.units[b].pos);});
    const auto size=std::max(1u,uint32_t(f.squadSize));for(size_t i=0;i<sorted.size();i+=size){const std::vector<uint32_t> group(sorted.begin()+i,sorted.begin()+std::min(sorted.size(),i+size));
      const auto target=pick(group);for(auto r:group)w.tactical[r].squadFocus=target;}}
}
void surroundOrders(World& w,uint8_t team){
  auto& p=w.packs[team];const auto& f=p.formation;const auto& es=w.foes(team);
  for(auto i:w.teams[team])w.tactical[i].hasSurroundGoal=false;if(!f.surround||es.empty())return;
  const auto center=centroid(w,w.teams[team]);auto target=p.focus;const auto* prior=w.resolve(target);if(!prior||!prior->alive)target=nearestTo(w,center,es);
  p.surroundTarget=target;const auto& t=w.units[target.slot];const double speed=length(t.smoothVelocity);
  double escape=speed>10?std::atan2(t.smoothVelocity.y,t.smoothVelocity.x):std::atan2(t.pos.y-center.y,t.pos.x-center.x),home=std::atan2(center.y-t.pos.y,center.x-t.pos.x);
  if(f.surroundCorner){home=std::atan2(w.config->height/2-t.pos.y,w.config->width/2-t.pos.x);escape=home+pi;}
  const auto at=[&](double angle,double radius){const auto pos=t.pos+Vec2{std::cos(angle)*radius,std::sin(angle)*radius};return Vec2{clamp(pos.x,20,w.config->width-20),clamp(pos.y,20,w.config->height-20)};};
  const auto assign=[&](const std::vector<uint32_t>& list,std::vector<Vec2> points){auto sorted=list;std::stable_sort(sorted.begin(),sorted.end(),[&](uint32_t a,uint32_t b){return distance(w.units[a].pos,t.pos)<distance(w.units[b].pos,t.pos);});
    for(auto i:sorted){if(points.empty())break;size_t best=0;for(size_t j=1;j<points.size();++j)if(distance(w.units[i].pos,points[j])<distance(w.units[i].pos,points[best]))best=j;
      auto& ts=w.tactical[i];ts.surroundGoal=points[best];ts.hasSurroundGoal=ts.assignedSet=true;ts.assigned=target;points.erase(points.begin()+best);}};
  const auto& m=p.members[0];const auto& r=p.members[1];const auto& a=p.members[2];std::vector<double> meleeAngles;
  double ring=std::max(32.0,f.surroundRing*(w.config->rules==Rules::Game?reachOf(w,team,Role::Melee)+28:30));
  if(f.surroundScreen)ring=std::max(ring,.45*(w.config->rules==Rules::Game?reachOf(w,team,Role::Ranged):150));
  std::vector<Vec2> points;for(size_t i=0;i<m.size();++i){const double angle=f.surroundScreen?home+(m.size()>1?double(i)/(m.size()-1)-.5:0)*120*pi/180:escape+2*pi*i/m.size();
    meleeAngles.push_back(angle);points.push_back(at(angle,ring));}assign(m,std::move(points));
  const auto reach=[&](uint32_t i){const auto& u=w.units[i];return w.config->rules==Rules::Game?u.range+(u.role==Role::Artillery?0:u.radius+12):w.config->roles[size_t(u.role)].range+20;};
  const double arc=f.surroundArc*pi/180;points.clear();
  for(size_t i=0;i<r.size();++i){double angle=home+(r.size()>1?double(i)/(r.size()-1)-.5:0)*arc;
    if(f.surroundLanes&&!meleeAngles.empty()){double best=angle,bd=INFINITY;for(auto a:meleeAngles){const double g=a+pi/meleeAngles.size();const double d=std::abs(std::atan2(std::sin(g-angle),std::cos(g-angle)));
      if(d<bd&&std::abs(std::atan2(std::sin(g-home),std::cos(g-home)))<=arc/2+.3){bd=d;best=g;}}
      angle=best+std::atan2(std::sin(angle-best),std::cos(angle-best))*.25;}
    points.push_back(at(angle,f.surroundDist*reach(r[i])));}assign(r,std::move(points));
  points.clear();for(size_t i=0;i<a.size();++i)points.push_back(at(home+(a.size()>1?double(i)/(a.size()-1)-.5:0)*120*pi/180,.85*reach(a[i])));assign(a,std::move(points));
}
} // namespace
namespace {
void cacheRates(const World& w,uint8_t team){if(w.ratesTime[team]==w.time&&w.ratesVersion[team]==w.membershipVersion)return;
  std::array<std::vector<double>,4> values;for(auto i:w.teams[team])if(w.units[i].alive){const auto& u=w.units[i];if(size_t(u.role)<3)values[size_t(u.role)].push_back(u.range);values[3].push_back(u.speed);}
  for(size_t k=0;k<4;++k){auto& v=values[k];double rate=k==3?w.config->roles[2].speed:w.config->roles[k].range;
    if(!v.empty()){const auto mid=v.begin()+v.size()/2;std::nth_element(v.begin(),mid,v.end());rate=*mid;}w.rates[team][k]=rate;}
  w.ratesTime[team]=w.time;w.ratesVersion[team]=w.membershipVersion;
}
}
double reachOf(const World& w,uint8_t team,Role role){if(w.config->rules!=Rules::Game||size_t(role)>2)return w.config->roles[size_t(role)].range;cacheRates(w,team);return w.rates[team][size_t(role)];}
double paceOf(const World& w,uint8_t team){if(w.config->rules!=Rules::Game)return w.config->roles[2].speed;cacheRates(w,team);return w.rates[team][3];}
bool pinned(const World& w,uint32_t i){const auto& u=w.units[i];const auto* t=w.resolve(u.target);return t&&t->alive&&t->role==Role::Melee&&gap(u,*t)<24;}
bool inZone(const World& w,uint8_t team,uint32_t i){const auto& p=w.packs[team];const auto pos=w.units[i].pos;const double d=depth(p,pos),l=lateral(p,pos);
  return distance(pos,p.cover)<=p.coverRadius&&d>=p.zoneFront&&d<=p.zoneBack&&l>=p.zoneMinL&&l<=p.zoneMaxL;}
bool threatens(const World& w,uint8_t team,uint32_t i){const auto& p=w.packs[team];const auto& h=w.units[i];const auto* t=w.resolve(h.target);
  const double minD=p.zoneFront+p.formation.zoneDepth;
  if(depth(p,h.pos)>minD)return true;const auto a=w.state[i].ability;
  if(a!=invalidSlot){const auto& ab=w.abilities[a];const auto* charge=w.resolve(ab.chargeTarget);if(ab.chargeEnd>w.time&&charge&&!melee(charge->role))return true;}
  if(t&&t->alive&&t->team==team&&!melee(t->role)&&gap(h,*t)<40)return true;
  if(melee(h.role))for(auto j:w.teams[team])if(w.units[j].alive&&!melee(w.units[j].role)&&distance(w.units[j].pos,h.pos)<p.formation.peelRadius)return true;return false;
}
void setPlan(World& w,uint8_t team,const Tactics& combo){auto& p=w.packs[team];p.combo=combo;p.plan=combo.role[0];p.planSince=w.time;
  p.formation=composeFormation(p.base,w.config->brains[team],combo);if(w.config->brains[team]==Brain::Rules){p.formation.dodge=w.config->reactiveDodge;p.formation.coordAbilities=w.config->abilities&&w.config->skills[team].abilities==AbilityPolicy::Coordinated;}++p.version;}
void formationPlan(World& w,uint8_t team){auto& p=w.packs[team];if(!p.enabled||!w.survivors(team))return;
  for(auto& m:p.members)m.clear();for(auto i:w.teams[team])if(w.units[i].alive){if(size_t(w.units[i].role)<3)p.members[size_t(w.units[i].role)].push_back(i);w.tactical[i].assignedSet=false;}
  std::array<uint32_t,3> counts;for(size_t r=0;r<3;++r)counts[r]=uint32_t(p.members[r].size());
  if(p.shapeVersion!=p.version||counts!=p.shapeCounts){p.shape=makeShape(counts,p.formation);p.shapeVersion=p.version;p.shapeCounts=counts;}
  positionAnchor(w,team);assignSlots(w,team);meleeOrders(w,team);focusOrders(w,team);surroundOrders(w,team);if(p.diving)p.phase=PackPhase::Diving;
}
} // namespace astelia
