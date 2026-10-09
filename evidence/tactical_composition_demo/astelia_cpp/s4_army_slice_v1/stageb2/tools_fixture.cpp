#include "candidates.h"
#include <iostream>
#include <iomanip>
#include <limits>
using namespace stageb2;
void point(std::optional<Point> p){if(p)std::cout<<"["<<p->x<<","<<p->y<<"]";else std::cout<<"null";}
int main(){std::cout<<std::setprecision(17);std::string op;while(std::cin>>op){try{if(op=="lead"){double x,y,vx,vy,t;std::cin>>x>>y>>vx>>vy>>t;point(lead({x,y},{vx,vy},t));}
else if(op=="range"){double x,y,ox,oy,lo,hi;Box b;std::cin>>x>>y>>ox>>oy>>lo>>hi>>b.x0>>b.y0>>b.x1>>b.y1;point(range_project({x,y},{ox,oy},lo,hi,b));}
else if(op=="flight"){double x,y,tx,ty,l,w;std::cin>>x>>y>>tx>>ty>>l>>w;std::cout<<flight_time({x,y},{tx,ty},l,w);}
else if(op=="dodge"){double x,y,tx,ty,vx,vy,t,c;int side;std::cin>>x>>y>>tx>>ty>>vx>>vy>>t>>c>>side;point(dodge_spot({x,y},{tx,ty},{vx,vy},t,c,side));}
else if(op=="friend"){double x,y,tx,ty,c,ox,oy,lo,hi;Box b;std::cin>>x>>y>>tx>>ty>>c>>ox>>oy>>lo>>hi>>b.x0>>b.y0>>b.x1>>b.y1;point(behind_friend({x,y},{tx,ty},c,{ox,oy},lo,hi,b));}
else if(op=="cluster"||op=="splash"||op=="best"){size_t n;double r;std::cin>>n>>r;std::vector<Point> es(n);for(auto& p:es)std::cin>>p.x>>p.y;if(op=="cluster"){auto cs=cluster_centres(es,r);std::cout<<"[";for(size_t i=0;i<cs.size();++i){if(i)std::cout<<",";point(cs[i]);}std::cout<<"]";}else if(op=="splash"){Point p;std::cin>>p.x>>p.y;std::cout<<splash_coverage(p,es,r);}else{Point o;double lo,hi;Box b;std::cin>>o.x>>o.y>>lo>>hi>>b.x0>>b.y0>>b.x1>>b.y1;point(best_splash(es,r,o,lo,hi,b));}}
else if(op=="threat"){size_t n;Point p;double t;std::cin>>n>>p.x>>p.y>>t;std::vector<EnemyThreat> es(n);for(auto& e:es)std::cin>>e.position.x>>e.position.y>>e.velocity.x>>e.velocity.y>>e.damage>>e.cycle>>e.reach;std::cout<<threat_estimate(p,es,t);}
else if(op=="invalid_flight")std::cout<<flight_time({0,0},{1,1},std::numeric_limits<double>::quiet_NaN(),0);
else if(op=="invalid_range")point(range_project({std::numeric_limits<double>::infinity(),0},{0,0},0,10,{0,0,20,20}));
else if(op=="overflow_lead")point(lead({1e308,0},{1e308,0},2));
else if(op=="bad_bank"){Frame f;f.width=500;f.height=300;for(int i=1;i<=65;++i){Row u(23);u[0]=i;u[2]=1;u[3]=40;u[4]=40;u[7]=100;u[8]=100;u[9]=8;u[10]=60;u[11]=100;u[12]=20;u[14]=1;f.units.push_back(u);f.own.push_back({double(i),0,0,1,1,100,10,0,3,.3});}candidates(f,1);}
else throw std::invalid_argument("unknown op");std::cout<<'\n';}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}}
