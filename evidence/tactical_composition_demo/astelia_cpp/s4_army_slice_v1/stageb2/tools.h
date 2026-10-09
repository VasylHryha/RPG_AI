#pragma once
#include <algorithm>
#include <cmath>
#include <optional>
#include <stdexcept>
#include <tuple>
#include <vector>
namespace stageb2 {
constexpr double EPS=1e-8;
struct Point {double x=0,y=0;};
struct Box {double x0,y0,x1,y1;};
inline void finite(double x){if(!std::isfinite(x))throw std::invalid_argument("nonfinite tool input");}
inline void finite(Point p){finite(p.x);finite(p.y);}
inline void finite(Box b){finite(b.x0);finite(b.y0);finite(b.x1);finite(b.y1);}
inline void finite(const std::vector<Point>& ps){for(auto p:ps)finite(p);}
inline Point add(Point a,Point b){Point p{a.x+b.x,a.y+b.y};finite(p);return p;}
inline Point sub(Point a,Point b){Point p{a.x-b.x,a.y-b.y};finite(p);return p;}
inline Point mul(Point a,double s){Point p{a.x*s,a.y*s};finite(p);return p;}
inline double norm(Point a){double r=std::hypot(a.x,a.y);finite(r);return r;}
inline Point direction(Point a){double r=norm(a);return r<1e-12?Point{1,0}:mul(a,1/r);}
inline Point lead(Point p,Point v,double t){finite(p);finite(v);finite(t);if(t<0||!std::isfinite(t))throw std::invalid_argument("flight seconds");return add(p,mul(v,t));}
inline double flight_time(Point own,Point target,double lob,double windup=0){finite(own);finite(target);finite(lob);finite(windup);if(lob<=0||windup<0)throw std::invalid_argument("flight parameters");double t=windup+norm(sub(target,own))/lob;finite(t);return t;}
inline std::vector<Point> circle_intersections(Point a,double ra,Point b,double rb){finite(a);finite(ra);finite(b);finite(rb);if(ra<0||rb<0)throw std::invalid_argument("circle radii");double d=norm(sub(b,a));if(d<1e-12||d>ra+rb+EPS||d<std::abs(ra-rb)-EPS)return {};double x=(ra*ra-rb*rb+d*d)/(2*d),h=std::sqrt(std::max(0.,ra*ra-x*x));auto v=direction(sub(b,a)),c=add(a,mul(v,x));Point n{-v.y,v.x};return {add(c,mul(n,h)),sub(c,mul(n,h))};}
inline std::vector<Point> circle_edges(Point o,double r,Box b){finite(o);finite(r);finite(b);if(r<0)throw std::invalid_argument("circle radius");std::vector<Point> out;for(double x:{b.x0,b.x1}){double h=r*r-(x-o.x)*(x-o.x);if(h>=-EPS)for(double y:{o.y+std::sqrt(std::max(0.,h)),o.y-std::sqrt(std::max(0.,h))})if(b.y0-EPS<=y&&y<=b.y1+EPS)out.push_back({x,y});}for(double y:{b.y0,b.y1}){double h=r*r-(y-o.y)*(y-o.y);if(h>=-EPS)for(double x:{o.x+std::sqrt(std::max(0.,h)),o.x-std::sqrt(std::max(0.,h))})if(b.x0-EPS<=x&&x<=b.x1+EPS)out.push_back({x,y});}return out;}
inline bool legal(Point p,Point o,double lo,double hi,Box b){finite(p);finite(o);finite(lo);finite(hi);finite(b);double d=norm(sub(p,o));return b.x0-EPS<=p.x&&p.x<=b.x1+EPS&&b.y0-EPS<=p.y&&p.y<=b.y1+EPS&&lo-EPS<=d&&d<=hi+EPS;}
inline std::optional<Point> range_project(Point p,Point o,double lo,double hi,Box b){finite(p);finite(o);finite(lo);finite(hi);finite(b);if(!(0<=lo&&lo<=hi)||b.x0>b.x1||b.y0>b.y1)throw std::invalid_argument("range/box");std::vector<Point> pts{{std::clamp(p.x,b.x0,b.x1),std::clamp(p.y,b.y0,b.y1)}};auto v=direction(sub(p,o));for(double r:{lo,hi}){pts.push_back(add(o,mul(v,r)));auto a=circle_edges(o,r,b);pts.insert(pts.end(),a.begin(),a.end());}for(double x:{b.x0,b.x1})pts.push_back({x,std::clamp(p.y,b.y0,b.y1)});for(double y:{b.y0,b.y1})pts.push_back({std::clamp(p.x,b.x0,b.x1),y});for(double x:{b.x0,b.x1})for(double y:{b.y0,b.y1})pts.push_back({x,y});std::optional<Point> out;for(auto q:pts)if(legal(q,o,lo,hi,b)&&(!out||std::make_tuple(norm(sub(q,p)),q.x,q.y)<std::make_tuple(norm(sub(*out,p)),out->x,out->y)))out=q;return out;}
inline int splash_coverage(Point p,const std::vector<Point>& enemies,double r){finite(p);finite(enemies);finite(r);if(r<0)throw std::invalid_argument("splash radius");int n=0;for(auto e:enemies)n+=norm(sub(p,e))<=r+EPS;return n;}
inline std::optional<Point> best_splash(const std::vector<Point>& enemies,double r,Point o,double lo,double hi,Box b){finite(enemies);finite(r);finite(o);finite(lo);finite(hi);finite(b);if(r<0)throw std::invalid_argument("splash radius");std::vector<Point> pts;for(size_t i=0;i<enemies.size();++i){auto a=enemies[i];auto q=range_project(a,o,lo,hi,b);if(q)pts.push_back(*q);auto edge=circle_edges(a,r,b);pts.insert(pts.end(),edge.begin(),edge.end());for(double ring:{lo,hi}){auto v=circle_intersections(a,r,o,ring);pts.insert(pts.end(),v.begin(),v.end());}for(size_t j=i+1;j<enemies.size();++j){auto v=circle_intersections(a,r,enemies[j],r);pts.insert(pts.end(),v.begin(),v.end());}}std::optional<Point> out;for(auto p:pts)if(legal(p,o,lo,hi,b)&&(!out||std::make_tuple(-splash_coverage(p,enemies,r),norm(sub(p,o)),p.x,p.y)<std::make_tuple(-splash_coverage(*out,enemies,r),norm(sub(*out,o)),out->x,out->y)))out=p;return out?out:range_project(o,o,lo,hi,b);}
inline std::vector<Point> cluster_centres(const std::vector<Point>& points,double radius){finite(points);finite(radius);if(radius<0)throw std::invalid_argument("cluster radius");std::vector<bool> seen(points.size());std::vector<Point> out;for(size_t i=0;i<points.size();++i){if(seen[i])continue;std::vector<size_t> component{i};seen[i]=true;for(size_t at=0;at<component.size();++at)for(size_t j=0;j<points.size();++j)if(!seen[j]&&norm(sub(points[component[at]],points[j]))<=radius+EPS){seen[j]=true;component.push_back(j);}Point c{};for(auto j:component)c=add(c,points[j]);out.push_back(mul(c,1./component.size()));}return out;}
inline Point dodge_spot(Point own,Point p,Point v,double t,double clearance,int side){finite(own);finite(p);finite(v);finite(t);finite(clearance);if((side!=1&&side!=-1)||clearance<0)throw std::invalid_argument("dodge parameters");auto d=direction(sub(lead(p,v,t),own));return add(own,mul({-d.y,d.x},clearance*side));}
inline std::optional<Point> behind_friend(Point f,Point threat,double clearance,Point target,double lo,double hi,Box b){finite(f);finite(threat);finite(clearance);finite(target);finite(lo);finite(hi);finite(b);if(clearance<0)throw std::invalid_argument("friend clearance");return range_project(add(f,mul(direction(sub(f,threat)),clearance)),target,lo,hi,b);}
struct EnemyThreat {Point position,velocity;double damage,cycle,reach;};
inline double threat_estimate(Point p,const std::vector<EnemyThreat>& es,double t){finite(p);finite(t);if(t<0)throw std::invalid_argument("threat horizon");double result=0;for(auto e:es){finite(e.position);finite(e.velocity);finite(e.damage);finite(e.cycle);finite(e.reach);if(e.damage<0||e.cycle<=0||e.reach<0)throw std::invalid_argument("threat parameters");double d=norm(sub(p,lead(e.position,e.velocity,t)))/std::max(1.,e.reach);result+=e.damage/e.cycle/(1+d*d);}finite(result);return result;}
}
