#pragma once
#include "tools.h"
#include <array>
#include <map>
namespace stageb2 {
constexpr size_t MAX_AIM=194,MAX_MOVE=896,FEATURES=18;
constexpr double AIM_OFFSET=12,MOVE_OFFSET=24;
using Row=std::vector<double>;
struct Frame {double width,height;std::vector<Row> units,own,shells,shots,casts,fields;std::map<unsigned,Point> longVelocity;};
struct Candidate {Point point;Row features;int type;int source=-1;};
struct Banks {std::vector<Candidate> aim,move;};
inline void validate(const Frame& f,unsigned id){
 for(auto& kv:f.longVelocity)finite(kv.second);
 finite(f.width);finite(f.height);if(f.width<=0||f.height<=0)throw std::invalid_argument("candidate arena");
 auto rows=[](const std::vector<Row>& vs,size_t width){for(auto& v:vs){if(v.size()!=width)throw std::invalid_argument("candidate schema");for(auto x:v)finite(x);}};
 rows(f.units,23);rows(f.own,10);rows(f.shells,9);rows(f.shots,7);rows(f.casts,7);rows(f.fields,5);
 std::vector<double> ids,owns,ownids;bool actor=false;
 for(auto& u:f.units){if(u[0]<=0||u[0]!=std::floor(u[0])||u[0]>=16777216||(u[1]!=0&&u[1]!=1)||(u[2]!=0&&u[2]!=1&&u[2]!=2)||u[7]<=0||u[8]<=0||u[9]<0||u[10]<0||u[12]<0||!(0<=u[18]&&u[18]<=u[11]))throw std::invalid_argument("candidate units envelope");ids.push_back(u[0]);if(u[1]==0)owns.push_back(u[0]);if(u[0]==id&&u[1]==0){actor=true;if(2*u[9]>std::min(f.width,f.height))throw std::invalid_argument("candidate body box");}}
 std::sort(ids.begin(),ids.end());if(std::adjacent_find(ids.begin(),ids.end())!=ids.end()||owns.size()>64||f.units.size()-owns.size()>64||!actor||f.shells.size()>64||f.shots.size()>64||f.casts.size()>32||f.fields.size()>32)throw std::invalid_argument("candidate entity/threat envelope");
 for(auto& s:f.own){ownids.push_back(s[0]);if(s[2]<0||s[3]<0||s[4]<=0||s[8]<=0||s[9]<0)throw std::invalid_argument("candidate own-state physics");}std::sort(owns.begin(),owns.end());std::sort(ownids.begin(),ownids.end());if(owns!=ownids)throw std::invalid_argument("candidate own-state coverage");
}
inline Banks candidates(const Frame& frame,unsigned id,bool allow_missing_aim=false){validate(frame,id);
 auto units=frame.units;std::sort(units.begin(),units.end(),[](auto& a,auto& b){return a[0]<b[0];});Row own,state;std::vector<Row> enemies,friends;
 for(auto& u:units){if(u.size()!=23)throw std::invalid_argument("candidate unit schema");if(u[0]==id&&u[1]==0)own=u;else if(u[1]==1)enemies.push_back(u);else if(u[1]==0)friends.push_back(u);}
 for(auto& s:frame.own)if(s[0]==id)state=s;
 if(own.empty()||state.size()!=10||enemies.size()>64||friends.size()>63||frame.shells.size()>64||frame.shots.size()>64||frame.casts.size()>32||frame.fields.size()>32)throw std::invalid_argument("candidate envelope");
 double W=frame.width,H=frame.height,lo=own[18],hi=own[11],windup=std::max(0.,state[3]-state[2])/std::max(1e-6,state[4]),lob=state[8]*100,splash=state[9]*100;
 Point pos{own[3],own[4]},centre{};Box box{own[9],own[9],W-own[9],H-own[9]},landing{0,0,W,H};std::vector<Point> enemypos,predictions;std::vector<EnemyThreat> threats;
 for(auto& u:enemies){Point p{u[3],u[4]},v=frame.longVelocity.count(unsigned(u[0]))?frame.longVelocity.at(unsigned(u[0])):Point{u[5],u[6]};enemypos.push_back(p);predictions.push_back(own[2]==2?lead(p,v,flight_time(pos,p,lob,windup)):p);threats.push_back({p,{u[5],u[6]},u[12],std::max(.001,u[14]),u[11]});centre=add(centre,p);}centre=enemies.empty()?pos:mul(centre,1./enemies.size());Banks out;
 std::map<unsigned,int> indices;for(size_t i=0;i<units.size();++i)indices[unsigned(units[i][0])]=int(i);
 std::map<std::string,int> starts;int at=int(units.size());starts["shells"]=at;at+=frame.shells.size();starts["shots"]=at;at+=frame.shots.size();starts["fields"]=at;at+=frame.fields.size();starts["casts"]=at;
 struct Blast{Point p;double t,r;};std::vector<Blast> blasts;
 for(auto& s:frame.shells)if(s[7]==1&&!s[6]&&s[4]>0)blasts.push_back({{s[2]*W,s[3]*H},s[4],s[5]*100+own[9]+4});
 for(auto& s:frame.casts)if(s[1]*256!=id)blasts.push_back({{s[2]*W,s[3]*H},s[5],s[6]*100+own[9]+4});
 auto append=[&](std::vector<Candidate>& bank,std::optional<Point> point,int type,int source=-1){if(!point)return;auto p=*point;Row f(FEATURES);f[type]=1;f[11]=(p.x-pos.x)/100;f[12]=(p.y-pos.y)/100;f[13]=norm(sub(p,pos))/100;f[14]=double(splash_coverage(p,predictions,splash))/std::max(size_t(1),enemies.size());f[15]=threat_estimate(p,threats,.5)/100;f[17]=-1;for(auto b:blasts)if(norm(sub(p,b.p))<=b.r){++f[16];double t=std::max(0.,b.t);if(f[17]<0||t<f[17])f[17]=t;}bank.push_back({p,f,type,source});};
 auto aim=[&](Point p,int type,int source=-1){append(out.aim,range_project(p,pos,lo,hi,landing),type,source);};
 auto move=[&](Point p,int type,int source=-1){append(out.move,Point{std::clamp(p.x,box.x0,box.x1),std::clamp(p.y,box.y0,box.y1)},type,source);};
 aim(add(pos,{lo,0}),0);for(size_t i=0;i<enemypos.size();++i){aim(enemypos[i],0,indices[unsigned(enemies[i][0])]);aim(predictions[i],1,indices[unsigned(enemies[i][0])]);}
 if(own[2]==2){for(auto p:cluster_centres(predictions,2*splash))aim(p,2);append(out.aim,best_splash(predictions,splash,pos,lo,hi,landing),3);}
 move(pos,4);
 for(auto& u:enemies){int source=indices[unsigned(u[0])];Point p{u[3],u[4]},d=direction(sub(pos,p)),n{-d.y,d.x};double mid=(lo+hi)/2;auto band=range_project(pos,p,lo,hi,box);append(out.move,band,5,source);auto approach=range_project(add(p,mul(d,lo)),p,lo,hi,box);if(approach&&(!band||norm(sub(*approach,*band))>1e-8))append(out.move,approach,7,source);for(int side:{-1,1})append(out.move,range_project(add(p,mul(add(mul(d,std::cos(3.14159265358979323846/4)),mul(n,side*std::sin(3.14159265358979323846/4))),mid)),p,lo,hi,box),8,source);move(add(pos,mul(d,std::max(60.,own[10]*.5))),9,source);}
 for(auto& u:friends){Point p{u[3],u[4]};move(add(p,mul(direction(sub(p,centre)),u[9]+own[9]+12)),6,indices[unsigned(u[0])]);}
 for(size_t i=0;i<frame.shots.size();++i){auto& s=frame.shots[i];for(int side:{-1,1})move(add(pos,mul({s[3],-s[2]},30*side)),10,starts["shots"]+int(i));}
 for(size_t i=0;i<frame.fields.size();++i){auto& s=frame.fields[i];auto delta=sub(pos,{s[0]*W,s[1]*H});double d=norm(delta);move(add(pos,d<.5?Point{30,0}:mul(delta,40/d)),10,starts["fields"]+int(i));}
 double first=INFINITY;for(auto b:blasts)if(norm(sub(pos,b.p))<=b.r)first=std::min(first,b.t);
 if(std::isfinite(first)){double extent=std::max(8.,own[10]*(first+.1));for(double fraction:{1.,.6})for(int j=0;j<16;++j){double angle=j*3.14159265358979323846/8;move(add(pos,mul({std::cos(angle),std::sin(angle)},extent*fraction)),10);}}
 if(own[2]==2&&out.aim.empty()&&!allow_missing_aim)throw std::invalid_argument("empty required artillery aim bank; inspect coverage");for(auto* bank:{&out.aim,&out.move})for(auto& c:*bank){finite(c.point);for(auto x:c.features)finite(x);}if(out.aim.size()>MAX_AIM||out.move.size()>MAX_MOVE||out.move.empty())throw std::invalid_argument("candidate overflow");return out;
}
}
