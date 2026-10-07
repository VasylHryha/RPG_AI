#include "collective.h"
#include <algorithm>
#include <stdexcept>
namespace astelia::control {
namespace {
constexpr double pi=3.14159265358979323846;
bool reach(const ObservedUnit& a,const ObservedUnit& b){double d=std::hypot(a.x-b.x,a.y-b.y);return d>=a.minRange&&d<=a.range;}
bool direct(const ObservedUnit& a,const ObservedUnit& b){return std::hypot(a.x-b.x,a.y-b.y)-a.radius-b.radius<=a.range;}
bool weaker(const ObservedUnit* a,const ObservedUnit* b){return a->hp<b->hp||(a->hp==b->hp&&a->id<b->id);}
std::pair<double,double> direction(double x,double y){double d=std::hypot(x,y);return d>1e-9?std::make_pair(x/d,y/d):std::make_pair(1.,0.);}
std::pair<double,double> axis(const ObservedUnit& g,const std::vector<const ObservedUnit*>& enemies,const std::vector<const ObservedUnit*>& guns){
 double x=0,y=0;unsigned n=0;for(auto e:enemies)if(e->id!=g.id){x+=e->x;y+=e->y;++n;}
 if(n)return direction(g.x-x/n,g.y-y/n);
 for(auto a:guns){x+=a->x;y+=a->y;++n;}return n?direction(x/n-g.x,y/n-g.y):std::make_pair(1.,0.);
}
}
CollectiveProbeV1::CollectiveProbeV1(double seed,uint8_t side,const ControllerParams& p,int arm):S4V6Controller(seed,side,p),arm_(arm){if(arm<7||arm>9)throw std::invalid_argument("unknown collective arm");}
void CollectiveProbeV1::prepare(const Observation& o){
 S4V6Controller::prepare(o);probe_={};probe_.t=o.t;if(!lastTick_.accepted)return;
 std::vector<const ObservedUnit*> guns,enemies;for(const auto& u:o.units)if(u.hp>0&&u.role==ObservedRole::Artillery)(u.team==side_?guns:enemies).push_back(&u);
 std::sort(guns.begin(),guns.end(),[](auto a,auto b){return a->id<b->id;});std::sort(enemies.begin(),enemies.end(),weaker);
 probe_.firstSight=firstSight_;probe_.waveTime=waveTime_;probe_.wave=waveTime_>=0;probe_.reason=reason_;probe_.living=guns.size();
 if(enemies.empty()||guns.empty())return;
 if(firstSight_<0)firstSight_=o.t;probe_.firstSight=firstSight_;
 const ObservedUnit* anchor=nullptr;for(auto e:enemies)if(e->id==target_)anchor=e;
 if(!anchor){anchor=enemies.front();if(arm_==9){unsigned best=~0u;for(auto e:enemies){auto u=axis(*e,enemies,guns);double x=e->x+308*u.first,y=e->y+308*u.second;unsigned exposure=0;for(auto q:enemies){double d=std::hypot(q->x-x,q->y-y);exposure+=d>=q->minRange&&d<=q->range;}if(exposure<best){best=exposure;anchor=e;}}auto u=axis(*anchor,enemies,guns);ux_=u.first;uy_=u.second;}
 else for(auto e:enemies)if(std::any_of(guns.begin(),guns.end(),[&](auto g){return reach(*g,*e);})){anchor=e;break;}target_=anchor->id;}
 probe_.target=target_;for(auto e:enemies)probe_.enemies.push_back(*e);
 if(arm_==9)std::sort(guns.begin(),guns.end(),[&](auto a,auto b){auto angle=[&](auto g){double d=std::atan2(g->y-anchor->y,g->x-anchor->x)-std::atan2(uy_,ux_);while(d< -pi)d+=2*pi;while(d>=pi)d-=2*pi;return d;};double aa=angle(a),bb=angle(b);return aa<bb||(aa==bb&&a->id<b->id);});
 double radius=30;for(auto e:enemies)radius=std::max(radius,e->range+30);
 for(size_t i=0;i<guns.size();++i){auto g=guns[i];auto u=direction(g->x-anchor->x,g->y-anchor->y);double preferred=std::max(g->minRange,g->range-12);
 if(arm_==9){double a=guns.size()==1?0:-pi/3+(2*pi/3)*i/(guns.size()-1);u={ux_*std::cos(a)-uy_*std::sin(a),ux_*std::sin(a)+uy_*std::cos(a)};preferred=308;}
 double outer=-1;for(auto e:enemies){double dx=e->x-anchor->x,dy=e->y-anchor->y,b=dx*u.first+dy*u.second,disc=radius*radius-(dx*dx+dy*dy-b*b);if(disc>=0)outer=std::max(outer,b+std::sqrt(disc));}
 bool solved=outer>=0&&std::isfinite(outer);double sx=solved?anchor->x+outer*u.first:g->x,sy=solved?anchor->y+outer*u.second:g->y;
 bool staged=solved&&std::hypot(g->x-sx,g->y-sy)<=20;probe_.ready+=staged;
 probe_.guns.push_back({g->id,g->x,g->y,sx,sy,anchor->x+preferred*u.first,anchor->y+preferred*u.second,solved,staged,reach(*g,*anchor),sx<0||sx>o.width||sy<0||sy>o.height});
 }
 if(waveTime_<0&&(probe_.ready>=std::ceil(.8*guns.size())||o.t-firstSight_>=20)){waveTime_=o.t;reason_=probe_.ready>=std::ceil(.8*guns.size())?"ready":"fallback20s";}
 probe_.wave=waveTime_>=0;probe_.waveTime=waveTime_;probe_.reason=reason_;
 for(size_t i=0;i<guns.size();++i){auto g=guns[i];auto& p=probe_.guns[i];auto& d=prepared_.at(g->id);
 if(probe_.wave){d.x=p.px;d.y=p.py;if(reach(*g,*anchor))d.target=target_;}
 else {d.x=p.gx;d.y=p.gy;for(auto e:enemies)if(d.target==e->id){d.target=0;break;}}
 d.multiplier=std::hypot(g->x-d.x,g->y-d.y)>1e-9?1:0;d.stop=0;
 }
 if(probe_.wave&&arm_>=8){double x=0,y=0;for(auto g:guns){x+=g->x;y+=g->y;}x/=guns.size();y/=guns.size();auto u=direction(anchor->x-x,anchor->y-y);double ex=x+60*u.first,ey=y+60*u.second;
 for(const auto& a:o.units)if(a.hp>0&&a.team==side_&&a.role==ObservedRole::Ranged){auto& d=prepared_.at(a.id);d.x=ex;d.y=ey;d.multiplier=std::hypot(a.x-ex,a.y-ey)>1e-9?1:0;d.stop=0;const ObservedUnit* selected=nullptr;double best=INFINITY;for(const auto& e:o.units)if(e.hp>0&&e.team!=side_&&e.role==ObservedRole::Ranged&&direct(a,e)){double gap=std::hypot(a.x-e.x,a.y-e.y)-a.radius-e.radius;if(gap<best||(gap==best&&selected&&e.id<selected->id)){selected=&e;best=gap;}}if(selected)d.target=selected->id;probe_.escorts.push_back({a.id,a.x,a.y,ex,ey,std::hypot(a.x-ex,a.y-ey)<=20,selected?selected->id:0});}
 }
}
}
