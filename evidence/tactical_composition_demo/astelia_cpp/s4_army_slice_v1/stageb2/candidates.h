#pragma once
#include "tools.h"
#include <array>
namespace stageb2 {
constexpr size_t MAX_AIM=194,MAX_MOVE=996,FEATURES=16;
constexpr double AIM_OFFSET=12,MOVE_OFFSET=24;
using Row=std::vector<double>;
struct Frame {double width,height;std::vector<Row> units,own,shells,shots,casts,fields;};
struct Candidate {Point point;Row features;int type;};
struct Banks {std::vector<Candidate> aim,move;};
inline void validate(const Frame& f,unsigned id){
 finite(f.width);finite(f.height);if(f.width<=0||f.height<=0)throw std::invalid_argument("candidate arena");
 auto rows=[](const std::vector<Row>& vs,size_t width){for(auto& v:vs){if(v.size()!=width)throw std::invalid_argument("candidate schema");for(auto x:v)finite(x);}};
 rows(f.units,23);rows(f.own,10);rows(f.shells,9);rows(f.shots,7);rows(f.casts,7);rows(f.fields,5);
 std::vector<double> ids,owns,ownids;bool actor=false;
 for(auto& u:f.units){if(u[0]<=0||u[0]!=std::floor(u[0])||u[0]>=16777216||(u[1]!=0&&u[1]!=1)||(u[2]!=0&&u[2]!=1&&u[2]!=2)||u[7]<=0||u[8]<=0||u[9]<0||u[10]<0||u[12]<0||!(0<=u[18]&&u[18]<=u[11]))throw std::invalid_argument("candidate units envelope");ids.push_back(u[0]);if(u[1]==0)owns.push_back(u[0]);if(u[0]==id&&u[1]==0){actor=true;if(2*u[9]>std::min(f.width,f.height))throw std::invalid_argument("candidate body box");}}
 std::sort(ids.begin(),ids.end());if(std::adjacent_find(ids.begin(),ids.end())!=ids.end()||owns.size()>64||f.units.size()-owns.size()>64||!actor||f.shells.size()>64||f.shots.size()>64||f.casts.size()>32||f.fields.size()>32)throw std::invalid_argument("candidate entity/threat envelope");
 for(auto& s:f.own){ownids.push_back(s[0]);if(s[2]<0||s[3]<0||s[4]<=0||s[8]<=0||s[9]<0)throw std::invalid_argument("candidate own-state physics");}std::sort(owns.begin(),owns.end());std::sort(ownids.begin(),ownids.end());if(owns!=ownids)throw std::invalid_argument("candidate own-state coverage");
}
inline Banks candidates(const Frame& frame,unsigned id){validate(frame,id);
 auto units=frame.units;std::sort(units.begin(),units.end(),[](auto& a,auto& b){return a[0]<b[0];});Row own,state;std::vector<Row> enemies,friends;
 for(auto& u:units){if(u.size()!=23)throw std::invalid_argument("candidate unit schema");if(u[0]==id&&u[1]==0)own=u;else if(u[1]==1)enemies.push_back(u);else if(u[1]==0)friends.push_back(u);}
 for(auto& s:frame.own)if(s[0]==id)state=s;
 if(own.empty()||state.size()!=10||enemies.size()>64||friends.size()>63||frame.shells.size()>64||frame.shots.size()>64||frame.casts.size()>32||frame.fields.size()>32)throw std::invalid_argument("candidate envelope");
 double W=frame.width,H=frame.height,lo=own[18],hi=own[11],windup=std::max(0.,state[3]-state[2])/std::max(1e-6,state[4]),lob=state[8]*100,splash=state[9]*100;
 Point pos{own[3],own[4]},centre{};Box box{own[9],own[9],W-own[9],H-own[9]},landing{0,0,W,H};std::vector<Point> enemypos,predictions;std::vector<EnemyThreat> threats;
 for(auto& u:enemies){Point p{u[3],u[4]},v{u[5],u[6]};enemypos.push_back(p);predictions.push_back(own[2]==2?lead(p,v,flight_time(pos,p,lob,windup)):p);threats.push_back({p,v,u[12],std::max(.001,u[14]),u[11]});centre=add(centre,p);}centre=enemies.empty()?pos:mul(centre,1./enemies.size());Banks out;
 auto append=[&](std::vector<Candidate>& bank,std::optional<Point> point,int type){if(!point)return;auto p=*point;Row f(FEATURES);f[type]=1;f[11]=(p.x-pos.x)/100;f[12]=(p.y-pos.y)/100;f[13]=norm(sub(p,pos))/100;f[14]=double(splash_coverage(p,predictions,splash))/std::max(size_t(1),enemies.size());f[15]=threat_estimate(p,threats,.5)/100;bank.push_back({p,f,type});};
 auto aim=[&](Point p,int type){append(out.aim,range_project(p,pos,lo,hi,landing),type);};
 auto move=[&](Point p,int type){append(out.move,Point{std::clamp(p.x,box.x0,box.x1),std::clamp(p.y,box.y0,box.y1)},type);};
 aim(add(pos,{lo,0}),0);for(size_t i=0;i<enemypos.size();++i){aim(enemypos[i],0);aim(predictions[i],1);}
 if(own[2]==2){for(auto p:cluster_centres(predictions,2*splash))aim(p,2);append(out.aim,best_splash(predictions,splash,pos,lo,hi,landing),3);}
 move(pos,4);
 for(auto& u:enemies){Point p{u[3],u[4]},d=direction(sub(pos,p)),n{-d.y,d.x};double mid=(lo+hi)/2;append(out.move,range_project(pos,p,lo,hi,box),5);append(out.move,range_project(add(p,mul(d,hi)),p,lo,hi,box),7);for(int side:{-1,1})append(out.move,range_project(add(p,mul(add(mul(d,std::cos(3.14159265358979323846/4)),mul(n,side*std::sin(3.14159265358979323846/4))),mid)),p,lo,hi,box),8);move(add(pos,mul(d,std::max(60.,own[10]*.5))),9);}
 for(auto& u:friends)append(out.move,behind_friend({u[3],u[4]},centre,u[9]+own[9]+12,centre,lo,hi,box),6);
 for(auto& u:enemies)for(int side:{-1,1})move(dodge_spot(pos,{u[3],u[4]},{u[5],u[6]},.5,std::max(60.,own[10]*.5),side),10);
 struct Hazard {Point p,v;double t,clearance;};std::vector<Hazard> hazards;
 for(auto& s:frame.shells)hazards.push_back({{s.at(2)*W,s.at(3)*H},{0,0},std::max(0.,s.at(4)),s.at(5)*100+own[9]+12});
 for(auto& s:frame.shots)hazards.push_back({{s.at(0)*W,s.at(1)*H},{s.at(2)*s.at(5)*100,s.at(3)*s.at(5)*100},std::min(.5,s.at(6)/std::max(s.at(5),1e-6)),std::max(60.,own[10]*.5)});
 for(auto& s:frame.casts)hazards.push_back({{s.at(2)*W,s.at(3)*H},{0,0},std::max(0.,s.at(5)),s.at(6)*100+own[9]+12});
 for(auto& s:frame.fields)hazards.push_back({{s.at(0)*W,s.at(1)*H},{0,0},std::max(0.,s.at(3)),s.at(2)*100+own[9]+12});
 for(auto h:hazards)for(int side:{-1,1})move(dodge_spot(pos,h.p,h.v,h.t,h.clearance,side),10);
 if(own[2]==2&&out.aim.empty())throw std::invalid_argument("empty required artillery aim bank; inspect coverage");for(auto* bank:{&out.aim,&out.move})for(auto& c:*bank){finite(c.point);for(auto x:c.features)finite(x);}if(out.aim.size()>MAX_AIM||out.move.size()>MAX_MOVE||out.move.empty())throw std::invalid_argument("candidate overflow");return out;
}
}
