#include "stagea.h"
#include <sys/resource.h>
#include "react.h"
#include "geometry.h"
#include <algorithm>
#include <cmath>
#include <iostream>
#include <set>
namespace stagea {
void memoryReport(uint64_t tick,size_t before,size_t after,bool final){
 if(!std::getenv("STAGEA_MEMORY_PROFILE")||(!final&&tick!=1&&tick%300))return;
 rusage usage{};if(getrusage(RUSAGE_SELF,&usage))throw std::runtime_error("getrusage failed");
 double peak=double(usage.ru_maxrss);
#ifndef __APPLE__
 peak*=1024; // macOS reports bytes; Linux reports KiB.
#endif
 std::cout<<"{\"stageAMemory\":true,\"tick\":"<<tick<<",\"final\":"<<(final?"true":"false")
  <<",\"arena_before\":"<<before<<",\"arena_after\":"<<after<<",\"shapes\":"<<js::shapes.size()
  <<",\"peak_rss_bytes\":"<<std::fixed<<std::setprecision(0)<<peak<<"}\n"<<std::defaultfloat<<std::setprecision(6);
}
void collectTick(astelia::World& w,js::Args roots,uint64_t tick){
 bool enabled=false;
 for(auto& cc:w.controllers)if(auto* c=dynamic_cast<react_v1::Controller*>(cc.get())){
  enabled=enabled||c->stage.collect||bool(c->stage.weights);
  // The input has been consumed by inference and serialized by record().
  // Numerical caches and learned memory own no js::V handles.
  c->stage.input=js::V();
  for(auto row:c->shape.audit)roots.push_back(row);
  for(auto row:c->shape.shotEvents)roots.push_back(row);
  for(auto row:c->battery.audit)roots.push_back(row);
 }
 if(!enabled)return;
 auto before=js::arena.size();js::collect(std::move(roots),0);
 // No live object refers to the consumed input layouts after the sweep.
 for(auto& cc:w.controllers)if(auto* c=dynamic_cast<react_v1::Controller*>(cc.get()))c->stage.layouts.clear();
 memoryReport(tick,before,js::arena.size());
}
namespace {
double sig(double x){return (1+std::tanh(x/2))/2;}
Vec nums(js::V a){if(a.tag!=js::V::Heap||a.p->kind!=js::Object::Array)throw std::invalid_argument("array required");Vec r;for(auto v:a.p->items){double x=js::num(v);if(!std::isfinite(x))throw std::invalid_argument("nonfinite array");r.push_back(x);}return r;}
Matrix mat(js::V a){Matrix m;for(auto v:a.p->items)m.push_back(nums(v));return m;}
js::V vectorJSON(const Vec& v){js::Args a;for(auto x:v)a.push_back(x);return js::arr(std::move(a));}
js::V matrixJSON(const Matrix& m){js::Args a;for(auto& v:m)a.push_back(vectorJSON(v));return js::arr(std::move(a));}
Vec tan(Vec a){for(auto& x:a)x=std::tanh(x);return a;}
void append(Vec& a,const Vec& b){a.insert(a.end(),b.begin(),b.end());}
double dot(const Vec& a,const Vec& b){if(a.size()!=b.size())throw std::invalid_argument("dot dimensions");double x=0;for(size_t i=0;i<a.size();++i)x+=a[i]*b[i];return x;}
const astelia::ObservedUnit& unit(react_v1::Controller& c,UnitId id){for(auto& u:c.snapshot().units.units)if(u.id==id)return u;throw std::invalid_argument("missing unit");}
js::V snapshot(react_v1::Controller& c){
 const auto& s=c.snapshot();const auto& o=s.units;js::Args units,own,shells,shots,fields,casts;std::vector<std::pair<std::string,js::V>> historyFields,pairFields;
 for(auto& u:o.units){units.push_back(js::arr({double(u.id),double(u.team),double(uint8_t(u.role)),u.x,u.y,u.vx,u.vy,u.hp,u.maxhp,u.radius,u.speed,u.range,u.dmg,u.cd,u.cdMax,double(u.target),u.damageDealt,u.damageTaken,u.minRange,u.dealtToEnemy,u.takenFromEnemy,u.friendlyDealt,u.friendlyTaken}));
  Vec h(16);auto m=c.memory().find(u.id);if(m!=c.memory().end()){const auto& v=m->second;h={v.zOut,v.zIn,v.lastOut/u.maxhp,v.lastIn/u.maxhp,double(v.target)/256,v.zInAnswered,v.zInUnanswered,double(v.hadLegalTarget),double(v.hadUnansweredThreat),0,0,0,0,0,0,0};}
  auto z=c.complexStates().find(u.id);if(z!=c.complexStates().end()){h[9]=z->second.real();h[10]=z->second.imag();}
  auto a=c.argMemory().find(u.id);if(a!=c.argMemory().end()){h[11]=a->second.arg;h[12]=a->second.time/150;h[13]=a->second.valid;}
  historyFields.push_back({std::to_string(u.id),vectorJSON(h)});
 }
 for(auto& p:c.pairModes())pairFields.push_back({std::to_string(p.first.first)+":"+std::to_string(p.first.second),p.second});
 auto history=c.stage.layouts.object(historyFields),pairs=c.stage.layouts.object(pairFields);
 for(auto& u:s.own)own.push_back(js::arr({double(u.id),u.guardUntil,u.prep,u.windup,u.timeRate,u.energy,u.cost,double(u.busy),s.stageGuns.at(u.id)[0]/100,s.stageGuns.at(u.id)[1]/100}));
 for(auto& x:s.stageShells)shells.push_back(js::arr({x[0]/o.width,x[1]/o.height,x[0]/o.width,x[1]/o.height,x[2]-o.t,x[3]/100,x[4],x[5],x[6]/100}));
 for(auto& x:s.shots)shots.push_back(js::arr({x.position.x/o.width,x.position.y/o.height,x.direction.x,x.direction.y,o.t-x.born,x.speed/100,x.left/100}));
 for(auto& x:s.fields)fields.push_back(js::arr({x.position.x/o.width,x.position.y/o.height,x.radius/100,x.from-o.t,x.until-o.t}));
 for(auto& x:s.casts)casts.push_back(js::arr({double(x.gun)/256,double(x.target)/256,x.landing.x/o.width,x.landing.y/o.height,x.releaseAt-o.t,x.landingAt-o.t,x.radius/100}));
 return js::obj({{"stageA",true},{"t",o.t},{"dt",o.dt},{"width",o.width},{"height",o.height},{"units",js::arr(std::move(units))},{"own",js::arr(std::move(own))},{"shells",js::arr(std::move(shells))},{"shots",js::arr(std::move(shots))},{"fields",js::arr(std::move(fields))},{"casts",js::arr(std::move(casts))},{"history",history},{"pairModes",pairs}});
}
struct Packed {Matrix tokens,query,pos;Vec speeds,assignments;std::vector<UnitId> ids,enemies,tokenIds;std::vector<size_t> enemy;};
Packed pack(js::V row,const std::string& kind){
 Packed p;auto units=mat(js::get(row,"units"));std::sort(units.begin(),units.end(),[](auto&a,auto&b){return a[0]<b[0];});double W=js::num(js::get(row,"width")),H=js::num(js::get(row,"height")),t=js::num(js::get(row,"t"));std::map<UnitId,Vec> own;for(auto v:mat(js::get(row,"own")))own[UnitId(v[0])]=Vec(v.begin()+1,v.end());
 for(auto& u:units){if(u.size()!=23||u[0]>=16777216||u[8]<=0)throw std::invalid_argument("unit envelope");Vec v(64);v[0]=1;v[1]=u[0]/256;v[2]=u[1];for(unsigned k=0;k<3;++k)v[3+k]=u[2]==k;v[6]=u[3]/W;v[7]=u[4]/H;v[8]=u[5]/100;v[9]=u[6]/100;v[10]=u[7]/u[8];v[11]=u[9]/100;v[12]=u[10]/100;v[13]=u[11]/100;v[14]=u[12]/u[8];v[15]=u[13]/std::max(u[14],.001);v[16]=u[15]/256;
 for(unsigned k=0;k<7;++k)v[17+k]=u[16+k]/u[8];
 if(own.count(UnitId(u[0]))){auto a=own.at(UnitId(u[0]));v[24]=a[0]-t;v[25]=a[1]/std::max(a[2],.001);v[26]=a[2];v[27]=a[3];v[28]=a[4]/100;v[29]=a[5]/100;v[30]=a[6];v[31]=a[7];v[41]=a[8];}
 v[19]=u[18]/100;v[40]=t/150;v[42]=js::num(js::get(row,"dt"));
 if(kind=="N1h"){auto h=nums(js::get(js::get(row,"history"),std::to_string(UnitId(u[0]))));if(h.size()!=16)throw std::invalid_argument("history width");std::copy(h.begin(),h.end(),v.begin()+48);}
 if(u[1]==0){p.ids.push_back(UnitId(u[0]));p.pos.push_back({u[3],u[4]});p.speeds.push_back(u[10]);p.assignments.push_back(u[15]);Vec q(128);std::copy(v.begin(),v.begin()+48,q.begin());if(kind=="N1h")std::copy(v.begin()+48,v.end(),q.begin()+48);p.query.push_back(q);}else{p.enemy.push_back(p.tokens.size());p.enemies.push_back(UnitId(u[0]));}
 p.tokenIds.push_back(UnitId(u[0]));p.tokens.push_back(v);
 }
 if(p.ids.size()>64||p.enemies.size()>64)throw std::invalid_argument("entity overflow");
 if(kind=="N1h")for(size_t i=0;i<p.ids.size();++i)for(size_t j=0;j<p.enemies.size();++j)p.query[i][64+j]=js::truth(js::get(js::get(row,"pairModes"),std::to_string(p.ids[i])+":"+std::to_string(p.enemies[j])));
 unsigned k=0;for(auto name:{"shells","shots","fields","casts"}){auto bank=mat(js::get(row,name));if(bank.size()>(k<2?64:32))throw std::invalid_argument("threat overflow");for(auto a:bank){Vec v(64);v[32+k]=1;if(a.size()>11)throw std::invalid_argument("threat width");std::copy(a.begin(),a.end(),v.begin()+36);p.tokens.push_back(v);}++k;}
 Vec w(64);w[47]=1;w[36]=t/150;w[37]=js::num(js::get(row,"dt"));w[38]=W/1000;w[39]=H/1000;p.tokens.push_back(w);return p;
}
Matrix infer(State& s,const Packed& p,double dt,bool refresh){
 const auto& w=*s.weights;if(!(dt>0&&dt<=.2))throw std::invalid_argument("dt envelope");
 if(refresh){s.cache.clear();for(auto& v:p.tokens)s.cache.push_back(tan(w.linear("enc2",tan(w.linear("enc1",v)))));s.cachedIds=p.tokenIds;}
 // Dead entities require a refreshed token bank. No index aliasing across removal.
 if(s.cachedIds!=p.tokenIds)throw std::invalid_argument("cached identity mismatch");
 size_t n=p.ids.size();Matrix q,ctx,mem;std::map<UnitId,Vec> next;for(size_t i=0;i<n;++i){q.push_back(tan(w.linear("query",p.query[i])));Vec scores;for(auto& z:s.cache)scores.push_back(dot(q.back(),z)/8);double mx=*std::max_element(scores.begin(),scores.end()),sum=0;for(auto& x:scores){x=std::exp(x-mx);sum+=x;}Vec c(64);for(size_t j=0;j<s.cache.size();++j)for(unsigned k=0;k<64;++k)c[k]+=scores[j]/sum*s.cache[j][k];ctx.push_back(c);Vec m(8);auto found=s.memory.find(p.ids[i]);if(found!=s.memory.end())m=found->second;else if(w.kind=="N2"||w.kind=="N2J0")m[0]=std::fmod(p.ids[i]*.6180339887498949,1.)*2*3.14159265358979323846;
 if(w.kind=="N1"||w.kind=="N1h")m.assign(8,0);mem.push_back(m);}
 if(w.kind=="N1r"){auto old=mem;for(size_t i=0;i<n;++i){std::vector<std::pair<double,size_t>> ns;for(size_t j=0;j<n;++j)if(i!=j)ns.push_back({std::hypot(p.pos[j][0]-p.pos[i][0],p.pos[j][1]-p.pos[i][1])/100,j});std::sort(ns.begin(),ns.end(),[&](auto a,auto b){return a.first<b.first||(a.first==b.first&&p.ids[a.second]<p.ids[b.second]);});Vec mean(8);size_t count=0;for(size_t k=0;k<std::min(size_t(8),ns.size());++k)if(ns[k].first<3){++count;for(unsigned z=0;z<8;++z)mean[z]+=old[ns[k].second][z];}for(auto& v:mean)v/=std::max(size_t(1),count);auto x=q[i];append(x,ctx[i]);append(x,old[i]);append(x,mean);mem[i]=tan(w.linear("recur",x));}}
 Matrix drift(n,Vec(2)),headmem=mem,align(n,Vec(p.enemies.size()));const auto& law=w.p.at("law");
 if(w.kind=="N2"||w.kind=="N2J0"){
  std::vector<std::vector<size_t>> graph(n);Matrix distances(n,Vec(n));for(size_t i=0;i<n;++i){std::vector<size_t> ns;for(size_t j=0;j<n;++j)if(i!=j){distances[i][j]=std::hypot(p.pos[j][0]-p.pos[i][0],p.pos[j][1]-p.pos[i][1])/100;ns.push_back(j);}std::sort(ns.begin(),ns.end(),[&](size_t a,size_t b){return distances[i][a]<distances[i][b]||(distances[i][a]==distances[i][b]&&p.ids[a]<p.ids[b]);});for(size_t k=0;k<std::min(size_t(8),ns.size());++k)if(distances[i][ns[k]]<3)graph[i].push_back(ns[k]);}
  Vec forcing(n),theta(n);for(size_t i=0;i<n;++i){auto x=q[i];append(x,ctx[i]);forcing[i]=std::tanh(w.linear("force",x)[0]);theta[i]=mem[i][0];}
  auto rhs=[&](const Vec& th){Vec rates(n);for(size_t i=0;i<n;++i){double sum=0;for(auto j:graph[i])sum+=std::exp(-distances[i][j]*distances[i][j])*std::sin(th[j]-th[i]);rates[i]=2*std::tanh(law[4])+forcing[i]+2*sig(law[3])*sum/std::max(size_t(1),graph[i].size());}return rates;};
  auto shift=[&](const Vec& k,double h){auto a=theta;for(size_t i=0;i<n;++i)a[i]+=h*k[i];return a;};auto k1=rhs(theta),k2=rhs(shift(k1,dt/2)),k3=rhs(shift(k2,dt/2)),k4=rhs(shift(k3,dt));for(size_t i=0;i<n;++i)theta[i]+=dt*(k1[i]+2*k2[i]+2*k3[i]+k4[i])/6;
  for(size_t i=0;i<n;++i){double sn=0,cs=0,vx=0,vy=0;for(auto j:graph[i]){sn+=std::sin(theta[j]);cs+=std::cos(theta[j]);double r=std::max(.1,distances[i][j]);double f=(sig(law[0])*(1+(w.kind=="N2J0"?0:sig(law[2]))*std::cos(theta[j]-theta[i]))-sig(law[1])/r)/r;vx+=(p.pos[j][0]-p.pos[i][0])/100*f;vy+=(p.pos[j][1]-p.pos[i][1])/100*f;}for(size_t e=0;e<p.enemies.size();++e){double snp=0,csp=0;size_t peers=0;for(auto j:graph[i])if(p.assignments[j]==p.enemies[e]){snp+=std::sin(theta[j]);csp+=std::cos(theta[j]);++peers;}if(peers){snp/=peers;csp/=peers;double length=std::hypot(snp,csp);if(length>=1e-6)align[i][e]=2*(std::sin(theta[i])*snp+std::cos(theta[i])*csp)/length;}}double count=std::max(size_t(1),graph[i].size());sn/=count;cs/=count;vx/=count;vy/=count;double scale=.25*sig(law[5])*p.speeds[i]/(1+std::hypot(vx,vy));drift[i]={vx*scale,vy*scale};mem[i]={theta[i],std::sin(theta[i]),std::cos(theta[i]),sn,cs,forcing[i],0,0};headmem[i]={mem[i][1],mem[i][2],sn,cs,forcing[i],0,0,0};}
 }
 Matrix out;for(size_t i=0;i<n;++i){auto x=q[i];append(x,ctx[i]);append(x,headmem[i]);auto h=tan(w.linear("head",x));auto y=w.linear("out",h);if(w.kind=="N2"||w.kind=="N2J0"){double phase=2*std::cos(mem[i][0]);y[3]+=phase;y[4]-=phase;y[5]+=phase;}Vec v={sig(y[0]),sig(y[1]),sig(y[2]),y[3],y[4],y[5],sig(y[6]),sig(y[7]),drift[i][0],drift[i][1],y[8]};auto key=w.linear("target",h);for(size_t e=0;e<p.enemy.size();++e)v.push_back(dot(key,s.cache.at(p.enemy[e]))/8+align[i][e]);out.push_back(v);next[p.ids[i]]=mem[i];}s.memory=std::move(next);return out;
}
js::V commandJSON(const react_v1::Command& c){auto d=c.movement;return js::obj({{"target",double(d.target)},{"goal",js::arr({d.x,d.y})},{"multiplier",d.multiplier},{"stop",d.stop},{"aim",c.hasAim?js::arr({c.aim.x,c.aim.y}):js::V(nullptr)},{"fire",c.fire==react_v1::FireIntent::Hold?"hold":c.fire==react_v1::FireIntent::Release?"release":"automatic"}});}
}
Weights::Weights(js::V v){if(js::str(js::get(v,"version"))!="ARMYA1"||js::str(js::get(v,"dtype"))!="float64")throw std::invalid_argument("weight schema");kind=js::str(js::get(v,"kind"));if(kind!="N1"&&kind!="N1h"&&kind!="N1r"&&kind!="N2"&&kind!="N2J0")throw std::invalid_argument("weight kind");auto ps=js::get(v,"parameters");std::map<std::string,std::vector<size_t>> shapes={{"law",{6}}};for(auto z:std::vector<std::tuple<std::string,size_t,size_t>>{{"enc1",64,64},{"enc2",64,64},{"query",64,128},{"head",64,136},{"out",9,64},{"target",64,64},{"recur",8,144},{"force",1,128}}){auto name=std::get<0>(z);shapes[name+".weight"]={std::get<1>(z),std::get<2>(z)};shapes[name+".bias"]={std::get<1>(z)};}
 if(js::keys(ps).size()!=shapes.size())throw std::invalid_argument("weight keys");for(auto& x:shapes){auto item=js::get(ps,x.first);auto shape=nums(js::get(item,"shape"));if(shape.size()!=x.second.size())throw std::invalid_argument("weight dimensions");size_t count=1;for(size_t i=0;i<shape.size();++i){if(shape[i]!=x.second[i])throw std::invalid_argument("weight dimensions");count*=x.second[i];}auto data=nums(js::get(item,"values"));if(data.size()!=count)throw std::invalid_argument("weight count");p[x.first]=data;}}
Vec Weights::linear(const std::string& name,const Vec& x)const{auto y=p.at(name+".bias");const auto& w=p.at(name+".weight");if(w.size()!=x.size()*y.size())throw std::invalid_argument("linear dimensions");for(size_t i=0;i<y.size();++i)for(size_t j=0;j<x.size();++j)y[i]+=w[i*x.size()+j]*x[j];for(auto v:y)if(!std::isfinite(v))throw std::runtime_error("nonfinite model output");return y;}
void configure(react_v1::Controller& c,js::V config){c.stage.collect=js::truth(js::get(config,"collect"));c.stage.parity=js::truth(js::get(config,"parity"));auto weights=js::get(config,"weights");if(weights.tag!=js::V::Undefined)c.stage.weights=std::make_shared<const Weights>(weights);}
void begin(react_v1::Controller& c){auto& s=c.stage;if(!s.collect&&!s.weights)return;s.input=snapshot(c);if(!s.weights)return;auto p=pack(s.input,s.weights->kind);double t=c.snapshot().units.t;bool refresh=t+1e-9>=s.nextFrame||s.cachedIds!=p.tokenIds;auto out=infer(s,p,c.snapshot().units.dt,refresh);if(refresh)s.nextFrame=t+.2;s.outputs.clear();for(size_t i=0;i<p.ids.size();++i)s.outputs[p.ids[i]]=out[i];++s.ticks;if(s.parity)std::cout<<js::stringify(js::obj({{"stageAParity",true},{"input",s.input},{"output",matrixJSON(out)},{"refresh",refresh}}))<<'\n';}
react_v1::Command command(react_v1::Controller& c,UnitId id){const auto& u=unit(c,id);auto y=c.stage.outputs.at(id);react_v1::Command cmd;auto& d=cmd.movement;auto& o=c.snapshot().units;d.x=std::clamp(y[0]*o.width+y[8],u.radius,o.width-u.radius);d.y=std::clamp(y[1]*o.height+y[9],u.radius,o.height-u.radius);d.multiplier=y[2];size_t target=std::max_element(y.begin()+10,y.end())-(y.begin()+10);std::vector<UnitId> enemies;for(auto& e:o.units)if(e.team!=u.team)enemies.push_back(e.id);std::sort(enemies.begin(),enemies.end());d.target=target?enemies.at(target-1):0;auto fire=std::max_element(y.begin()+3,y.begin()+6)-(y.begin()+3);cmd.fire=fire==0?react_v1::FireIntent::Automatic:fire==1?react_v1::FireIntent::Hold:react_v1::FireIntent::Release;
 if(u.role==astelia::ObservedRole::Artillery){astelia::Vec2 point{y[6]*o.width,y[7]*o.height};double dx=point.x-u.x,dy=point.y-u.y,r=std::hypot(dx,dy);if(r<1e-12){dx=1;dy=0;r=1;}double radius=std::clamp(r,u.minRange,u.range);point={std::clamp(u.x+dx/r*radius,0.,o.width),std::clamp(u.y+dy/r*radius,0.,o.height)};if(astelia::distance({u.x,u.y},point)+1e-9>=u.minRange&&astelia::distance({u.x,u.y},point)<=u.range+1e-9){cmd.hasAim=true;cmd.aim=point;}}
 return cmd;}
void record(react_v1::Controller& c){if(!c.stage.collect)return;auto row=c.stage.input;js::Args labels;std::set<UnitId> living;for(auto u:js::get(row,"units").p->items)if(js::num(u.p->items[1])==0)living.insert(UnitId(js::num(u.p->items[0])));for(auto& kv:c.records()){if(!living.count(kv.first))continue;const auto& r=kv.second;labels.push_back(js::obj({{"id",double(r.id)},{"role",r.role},{"raw",commandJSON(r.stageRaw)},{"participation",commandJSON(r.stageParticipation)},{"react",commandJSON(r.reactCandidate)},{"executed",commandJSON(r.executed)},{"ready",r.ready},{"active",r.active},{"winner",r.winner},{"engineRelease",double(r.engineRelease)}}));}js::set(row,"labels",js::arr(std::move(labels)));if(c.stage.weights){js::Args state;for(auto& m:c.stage.memory){auto v=m.second;Vec entry={double(m.first)};append(entry,v);auto y=c.stage.outputs.at(m.first);entry.push_back(y[8]);entry.push_back(y[9]);state.push_back(vectorJSON(entry));}js::set(row,"networkKind",c.stage.weights->kind);js::set(row,"networkState",js::arr(std::move(state)));}std::cout<<js::stringify(row)<<'\n';}
js::V replay(js::V request){static std::unique_ptr<State> persistent;auto weights=js::get(request,"weights");if(weights.tag!=js::V::Undefined){persistent=std::make_unique<State>();persistent->weights=std::make_shared<const Weights>(weights);}if(!persistent)throw std::invalid_argument("replay reset weights required");auto& s=*persistent;js::Args outputs;for(auto row:js::get(request,"frames").p->items){auto p=pack(row,s.weights->kind);double t=js::num(js::get(row,"t"));bool refresh=t+1e-9>=s.nextFrame||s.cachedIds!=p.tokenIds;outputs.push_back(matrixJSON(infer(s,p,js::num(js::get(row,"dt")),refresh)));if(refresh)s.nextFrame=t+.2;}return js::obj({{"stageAReplay",true},{"outputs",js::arr(std::move(outputs))},{"combat_steps",0}});}
}
