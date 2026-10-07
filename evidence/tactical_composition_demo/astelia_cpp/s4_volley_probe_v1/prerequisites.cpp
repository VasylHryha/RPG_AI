#include "native/world.h"
#include "native/config_codec.h"
#include "native/observer_v1.h"
#include "js_value.h"
#include <iostream>
using namespace astelia;
class Hold final:public Controller{public:bool acquire;Hold(double seed,uint8_t side,bool a):Controller(seed,side),acquire(a){} UnitDecision decide(const control::Observation&o,UnitId id)override{for(auto&u:o.units)if(u.id==id){UnitId t=0;if(acquire&&side_==0)for(auto&e:o.units)if(e.team!=side_){t=e.id;break;}return {u.x,u.y,0,0,t};}throw std::runtime_error("id");}std::unique_ptr<Controller>clone()const override{return std::make_unique<Hold>(*this);}};
int main(){std::string line;std::getline(std::cin,line);auto req=js::parse(line);auto base=configuration(req);for(int mode=0;mode<3;++mode){auto c=std::make_shared<Config>(base);c->army={0,0,1};c->hasEnemyArmy=true;c->enemyArmy={0,0,3};c->duration=2;c->controllers[1]={"nearest",{},"v1"};auto w=World::create(c);w.controllers[0]=std::make_unique<Hold>(c->seed,0,mode==1);w.controllers[1]=std::make_unique<Hold>(c->seed,1,false);
for(auto i:w.teams[0]){w.units[i].pos={300,350};w.units[i].cooldown=0;}int n=0;for(auto i:w.teams[1]){w.units[i].pos={500,350+double(20*n++)};w.units[i].cooldown=0;}w.liveGrid.build(w.units,w.active,c->width,c->height,40);
observer_v1::Sink sink;sink.world=&w;observer_v1::Scope scope(sink);unsigned first=0,total=0;double firstTime=-1;while(!w.done()){coreStep(w);for(auto&l:sink.launches)if(l.team==0){++total;if(firstTime<0)firstTime=w.time;}sink.launches.clear();if(mode==2&&w.time<.04){for(auto i:w.teams[0]){auto target=w.reference(w.teams[1][0]);bool b=triggerAbility(w,i,Ability::Barrage,target);bool s=triggerAbility(w,i,Ability::Slow,{},w.units[target.slot].pos);first=b||s;}}}
std::cout<<"{\"mode\":"<<mode<<",\"abilities\":"<<(w.config->abilities?"true":"false")<<",\"auto\":"<<(w.config->skills[0].abilities==AbilityPolicy::Auto?"true":"false")<<",\"own_launches\":"<<total<<",\"first_launch_time\":"<<firstTime<<",\"manual_ability_succeeded\":"<<first<<"}\n";}}
