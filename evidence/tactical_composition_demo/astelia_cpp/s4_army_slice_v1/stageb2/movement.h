#pragma once
#include "tools.h"
#include <map>
namespace stageb2 {
struct MovementPoint {Point point;int type,source;};
inline std::vector<MovementPoint> ordinary_points(const std::vector<std::vector<double>>& units,const std::map<unsigned,Point>& velocities,double W,double H,unsigned id){
 const std::vector<double>* own=nullptr,*nearest=nullptr;std::vector<const std::vector<double>*> enemies,friends,guns;std::map<unsigned,int> indices;
 for(size_t i=0;i<units.size();++i){auto& u=units[i];indices[unsigned(u[0])]=int(i);if(u[0]==id)own=&u;if(u[1]==1)enemies.push_back(&u);else {if(u[0]!=id)friends.push_back(&u);if(u[2]==2)guns.push_back(&u);}}
 if(!own)throw std::invalid_argument("missing movement actor");const auto& u=*own;Point pos{u[3],u[4]};double r=u[9];Box box{r,r,W-r,H-r};std::vector<MovementPoint> out;
 auto position=[](auto e){return Point{(*e)[3],(*e)[4]};};
 auto nearer=[&](auto a,auto b,Point origin){double da=norm(sub(position(a),origin)),db=norm(sub(position(b),origin));return da<db||(da==db&&(*a)[0]<(*b)[0]);};
 for(auto e:enemies)if(!nearest||nearer(e,nearest,pos))nearest=e;
 auto bounds=[&](auto e){return std::pair<double,double>{u[2]==2?u[18]:0.,u[2]==2?u[11]:u[11]+r+(*e)[9]};};
 auto clip=[&](Point p,bool body=false){double margin=body?r:0.;return Point{std::clamp(p.x,margin,W-margin),std::clamp(p.y,margin,H-margin)};};
 auto emit=[&](Point p,int type,int source=-1,bool image=true){out.push_back({clip(p),type,source});if(image&&nearest){Point e=position(nearest),delta=sub(p,e);double length=norm(delta);auto d=direction(length?delta:sub(pos,e));auto band=bounds(nearest);out.push_back({clip(add(e,mul(d,std::clamp(length,band.first,band.second))),true),23,source});}};
 Point shift{};for(auto f:friends){if(u[2]==2&&(*f)[2]!=2)continue;auto delta=sub(pos,position(f));double distance=norm(delta);Point d=distance?direction(delta):Point{u[0]<(*f)[0]?-1.:1.,0};shift=add(shift,mul(d,std::max(0.,60-distance)));}
 emit(add(pos,shift),24);
 for(auto e:enemies){auto band=bounds(e);int source=indices[unsigned((*e)[0])];auto p=position(e);auto q=range_project(pos,p,band.first,band.second,box);if(q)out.push_back({*q,23,source});emit(add(pos,mul(direction(sub(p,pos)),200)),21,source);if(u[2]==2){auto anchor=add(p,mul(direction(sub(pos,p)),std::max(u[18],u[11]-12)));emit(anchor,19,source);emit(add(anchor,shift),20,source);}}
 if(u[2]==1&&!guns.empty()){auto g=guns.front();for(auto f:guns)if(nearer(f,g,pos))g=f;auto p=position(g);Point centre{};size_t count=0;for(auto e:enemies){emit(clip(add(p,mul(direction(sub(position(e),p)),60))),18,indices[unsigned((*e)[0])]);if((*e)[2]==2){centre=add(centre,position(e));++count;}}if(count)emit(clip(add(p,mul(direction(sub(mul(centre,1./count),p)),60))),18,indices[unsigned((*g)[0])]);}
 for(auto v:std::vector<Point>{{u[5],u[6]},velocities.count(id)?velocities.at(id):Point{u[5],u[6]}}){emit(norm(v)?add(pos,mul(direction(v),200)):pos,22);emit(add(pos,v),22);}
 if(!enemies.empty()){for(int j=0;j<64;++j){double angle=j*3.14159265358979323846/32;emit(add(pos,mul({std::cos(angle),std::sin(angle)},200)),25,-1,false);}auto band=bounds(nearest);for(double radius:band.first>0?std::vector<double>{band.second,band.first}:std::vector<double>{band.second})for(int j=0;j<64;++j){double angle=j*3.14159265358979323846/32;emit(add(position(nearest),mul({std::cos(angle),std::sin(angle)},radius)),25,indices[unsigned((*nearest)[0])],false);}}
 return out;
}
}
