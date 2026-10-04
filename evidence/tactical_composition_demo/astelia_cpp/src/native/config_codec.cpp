// Dynamic JSON values stop at this boundary; combat reads typed configuration.
#include "config_codec.h"
#include "world.h"
#include "../js_value.h"
#include <set>

namespace astelia {
namespace {
using js::V;
bool present(V o,const char* key){return js::get(o,key).tag!=V::Undefined;}
void only(V value,std::initializer_list<const char*> allowed) {
  if(value.tag!=V::Heap||value.p->kind!=js::Object::Plain)throw std::invalid_argument("expected JSON object");
  std::set<std::string> names;for(auto name:allowed)names.insert(name);
  for(auto key:js::keys(value))if(!names.count(js::str(key)))throw std::invalid_argument("unsupported native combat field: "+js::str(key));
}
double number(V o,const char* key,double fallback) {
  const auto v=js::get(o,key);if(v.tag==V::Undefined)return fallback;
  if(v.tag!=V::Number||!std::isfinite(v.n))throw std::invalid_argument(std::string("invalid numeric field: ")+key);
  return v.n;
}
bool boolean(V o,const char* key,bool fallback) {
  const auto v=js::get(o,key);if(v.tag==V::Undefined)return fallback;
  if(v.tag!=V::Boolean)throw std::invalid_argument(std::string("invalid boolean field: ")+key);return bool(v.n);
}
std::string string(V o,const char* key,std::string fallback) {
  const auto v=js::get(o,key);if(v.tag==V::Undefined)return fallback;
  if(v.tag!=V::String)throw std::invalid_argument(std::string("invalid string field: ")+key);return js::str(v);
}
uint32_t count(V o,const char* key,uint32_t fallback) {
  const double n=number(o,key,fallback);if(n<0||n>1000000||n!=std::floor(n))throw std::invalid_argument(std::string("invalid count: ")+key);return uint32_t(n);
}
const js::Args& array(V v) {
  if(v.tag!=V::Heap||v.p->kind!=js::Object::Array)throw std::invalid_argument("expected JSON array");return v.p->items;
}
Role role(const std::string& name) {
  for(size_t r=0;r<6;++r)if(name==roleName(Role(r)))return Role(r);throw std::invalid_argument("unknown role: "+name);
}
Dodge dodge(V v) {
  if(v.tag==V::Null||v.tag==V::Undefined)return Dodge::None;
  const auto s=js::str(v);if(s=="kiter")return Dodge::Kiter;if(s=="storm")return Dodge::Storm;if(s=="skittish")return Dodge::Skittish;
  throw std::invalid_argument("unknown dodge profile: "+s);
}
uint32_t kindIndex(const Config& c,const std::string& name) {
  for(size_t i=0;i<c.kinds.size();++i)if(c.kinds[i].name==name)return uint32_t(i);
  throw std::invalid_argument("unknown unit kind: "+name);
}
void skills(CombatSkills& s,V v) {
  only(v,{"lead","abilities","kite","pursuit","dodgeShots","shotReact","dodgeShells","lobLead"});
  const auto lead=string(v,"lead",s.lead==Lead::None?"none":s.lead==Lead::Raw?"raw":"smooth");
  if(lead=="none")s.lead=Lead::None;else if(lead=="raw")s.lead=Lead::Raw;else if(lead=="smooth")s.lead=Lead::Smooth;else throw std::invalid_argument("unknown lead");
  const auto ability=string(v,"abilities",s.abilities==AbilityPolicy::Off?"off":"auto");
  if(ability=="off")s.abilities=AbilityPolicy::Off;else if(ability=="auto")s.abilities=AbilityPolicy::Auto;else throw std::invalid_argument("coordinated abilities pending formation migration");
  s.kite=number(v,"kite",s.kite);s.shotReact=number(v,"shotReact",s.shotReact);
  const auto pursuit=string(v,"pursuit",s.pursuitCut?"cut":"chase");
  if(pursuit!="cut"&&pursuit!="chase")throw std::invalid_argument("unknown pursuit");s.pursuitCut=pursuit=="cut";
  if(present(v,"dodgeShots")){auto x=js::get(v,"dodgeShots");if(x.tag==V::Boolean){s.dodgeShots=bool(x.n);s.dodgeSoft=false;}
    else if(js::str(x)=="soft"){s.dodgeShots=s.dodgeSoft=true;}else throw std::invalid_argument("unknown shot dodge");}
  if(present(v,"dodgeShells"))s.dodgeShells=boolean(v,"dodgeShells",false);
  if(present(v,"lobLead")){auto x=js::get(v,"lobLead");if(x.tag==V::Boolean){s.lobLead=bool(x.n);s.adaptiveLobLead=false;}
    else if(js::str(x)=="adaptive"){s.lobLead=false;s.adaptiveLobLead=true;}else throw std::invalid_argument("unknown lob lead");}
  if(s.kite<0||s.shotReact<0)throw std::invalid_argument("negative combat skill");
}
}
Config configuration(const js::V& request) {
  only(request,{"mode","options","trace"});
  const auto mode=string(request,"mode","alone");if(mode!="alone")throw std::invalid_argument("native combat checkpoint requires mode=alone");
  V o=js::get(request,"options");if(o.tag==V::Undefined)o=js::obj({});
  only(o,{"seed","dt","duration","width","height","army","scenario","swapSides","rules","abilities","sandboxAbilities","ai","shots","shotSpeed","windUp",
    "hunters","enemyArmy","ours","unitSet","skirmishSet","temporal","playerStyle","perception","attackerCap","abilOff",
    "enemy","shotDodge","shotReact","shellDodgeAll","smoothLead","pursuit","kiteRadius"});
  const auto rules=string(o,"rules","sandbox");if(rules!="sandbox"&&rules!="game")throw std::invalid_argument("unknown rules");
  auto c=rules=="game"?gameConfig():sandboxConfig();c.mode=mode;
  c.seed=number(o,"seed",c.seed);c.dt=number(o,"dt",c.dt);c.duration=number(o,"duration",c.duration);
  c.width=number(o,"width",c.width);c.height=number(o,"height",c.height);
  c.shotSpeed=rules=="game"?240:number(o,"shotSpeed",c.shotSpeed);
  c.windUp=rules=="game"||boolean(o,"windUp",false);
  c.abilities=boolean(o,rules=="game"?"sandboxAbilities":"abilities",false);
  c.swapSides=boolean(o,"swapSides",false);c.temporal=boolean(o,"temporal",true);c.perception=boolean(o,"perception",false);
  c.attackerCap=count(o,"attackerCap",0);
  const auto scenario=string(o,"scenario","hunters");c.mirror=scenario=="mirror";
  if(scenario=="mirror")c.scenario=Scenario::Mirror;else if(scenario=="hunters")c.scenario=Scenario::Hunters;else if(scenario=="skirmish")c.scenario=Scenario::Skirmish;else throw std::invalid_argument("unknown scenario");
  const auto shot=string(o,"shots","aimed");if(shot!="aimed"&&shot!="homing")throw std::invalid_argument("unknown shot mode");c.aimedShots=shot=="aimed";
  const auto style=string(o,"playerStyle","kite");if(style=="kite")c.playerStyle=PlayerStyle::Kite;else if(style=="orbit")c.playerStyle=PlayerStyle::Orbit;else if(style=="press")c.playerStyle=PlayerStyle::Press;else throw std::invalid_argument("unknown player style");
  const auto parseArmy=[&](V a,std::array<uint32_t,3>& counts){only(a,{"melee","ranged","artillery"});size_t i=0;for(auto name:{"melee","ranged","artillery"})counts[i++]=count(a,name,0);};
  if(present(o,"army"))parseArmy(js::get(o,"army"),c.army);
  if(present(o,"enemyArmy")){c.hasEnemyArmy=true;parseArmy(js::get(o,"enemyArmy"),c.enemyArmy);}
  if(present(o,"hunters")){auto h=js::get(o,"hunters");only(h,{"melee","archers","respawn"});c.hunterMelee=count(h,"melee",0);c.hunterArchers=count(h,"archers",0);c.respawn=number(h,"respawn",3);if(c.respawn<0)throw std::invalid_argument("negative respawn");}
  if(present(o,"unitSet")){
    if(c.rules!=Rules::Game)throw std::invalid_argument("unitSet requires game rules");
    const auto set=js::get(o,"unitSet");only(set,{"kinds","army"});const auto kinds=js::get(set,"kinds");
    if(kinds.tag!=V::Heap||kinds.p->kind!=js::Object::Plain)throw std::invalid_argument("expected kinds object");
    for(const auto key:js::keys(kinds)){
      const auto name=js::str(key);const auto v=js::get(kinds,key);
      only(v,{"role","kind","hp","speed","r","dmg","reach","windup","cd","ep","epRegen","cost","prot","dodge","shot","lob","radius","minRange","launch","acc","block"});
      Kind k;bool found=false;for(const auto& old:c.kinds)if(old.name==name){k=old;found=true;break;}
      k.name=name;k.role=role(string(v,"role",found?roleName(k.role):""));
      k.hp=number(v,"hp",k.hp);k.speed=number(v,"speed",k.speed);k.radius=number(v,"r",k.radius);k.damage=number(v,"dmg",k.damage);k.reach=number(v,"reach",k.reach);
      k.windup=number(v,"windup",k.windup);k.cooldown=number(v,"cd",k.cooldown);k.energy=number(v,"ep",k.energy);k.regen=number(v,"epRegen",k.regen);k.cost=number(v,"cost",k.cost);
      k.protection=number(v,"prot",k.protection);k.shot=number(v,"shot",k.shot);k.lob=number(v,"lob",k.lob);k.splash=number(v,"radius",k.splash);k.minRange=number(v,"minRange",k.minRange);
      k.launch=number(v,"launch",k.launch);k.acc=number(v,"acc",k.acc);if(present(v,"dodge"))k.dodge=dodge(js::get(v,"dodge"));
      if(present(v,"block")){const auto b=js::get(v,"block");if(b.tag==V::Null)k.block=false;else {
        only(b,{"cost","cd","dur","mult","halfArc"});k.block=true;k.blockCost=number(b,"cost",40);k.blockCooldown=number(b,"cd",2);k.blockDuration=number(b,"dur",1);
        k.blockMultiplier=number(b,"mult",.5);k.blockHalfArc=number(b,"halfArc",1.5707963267948966);
        if(k.blockCost<0||k.blockCooldown<0||k.blockDuration<0||k.blockMultiplier<0||k.blockMultiplier>1||k.blockHalfArc<0)throw std::invalid_argument("invalid block parameters");}}
      if(!(k.hp>0)||k.speed<0||k.radius<0||k.damage<0||k.reach<k.radius+12||k.windup<0||k.cooldown<0||k.energy<0||k.regen<0||k.cost<0||k.protection<0||k.protection>1||k.shot<0||k.lob<0||k.splash<0||k.minRange<0||k.launch<0||!(k.acc>0))throw std::invalid_argument("invalid custom kind stats");
      if(found)c.kinds[kindIndex(c,name)]=k;else c.kinds.push_back(k);
    }
    c.hasCustomArmy=true;
    for(const auto a:array(js::get(set,"army"))){const auto& pair=array(a);if(pair.size()!=2||pair[1].tag!=V::Number||pair[1].n<0||pair[1].n>1e6||pair[1].n!=std::floor(pair[1].n))throw std::invalid_argument("invalid kind/count pair");
      const auto k=kindIndex(c,js::str(pair[0]));c.customArmy.push_back({c.kinds[k].role,k,uint32_t(pair[1].n)});}
  }
  if(present(o,"ours")){c.hasCarried=true;for(const auto v:array(js::get(o,"ours"))){only(v,{"role","kind","hp"});
    CarriedUnit u;u.role=role(string(v,"role",""));u.hp=number(v,"hp",0);if(!(u.hp>0))throw std::invalid_argument("invalid carried health");
    if(present(v,"kind")&&js::get(v,"kind").tag!=V::Null)u.kind=kindIndex(c,string(v,"kind",""));c.carried.push_back(u);}}
  if(present(o,"skirmishSet")){const auto s=js::get(o,"skirmishSet");only(s,{"count","maxAlive","kinds"});c.skirmishCount=count(s,"count",18);c.skirmishMaxAlive=count(s,"maxAlive",8);
    if(present(s,"kinds")){c.skirmishKinds.clear();for(const auto k:array(js::get(s,"kinds")))c.skirmishKinds.push_back(kindIndex(c,js::str(k)));}}
  if(string(o,"enemy","alone")!="alone")throw std::invalid_argument("native combat checkpoint requires alone enemy");
  for(auto& s:c.skills){s.abilities=AbilityPolicy::Auto;s.kite=number(o,"kiteRadius",70);s.shotReact=number(o,"shotReact",.12);
    s.dodgeShots=c.rules==Rules::Sandbox&&boolean(o,"shotDodge",true);s.dodgeShells=c.rules==Rules::Sandbox&&boolean(o,"shellDodgeAll",true);
    s.lead=c.rules==Rules::Game?Lead::None:boolean(o,"smoothLead",true)?Lead::Smooth:Lead::Raw;s.pursuitCut=c.rules==Rules::Sandbox&&string(o,"pursuit","cut")=="cut";}
  if(present(o,"ai")){const auto& profiles=array(js::get(o,"ai"));if(profiles.size()>2)throw std::invalid_argument("expected at most two profiles");
    for(size_t t=0;t<profiles.size();++t){const auto p=profiles[t];if(p.tag==V::Null)continue;only(p,{"level","brain","skills","lookahead"});
      const auto level=string(p,"level","");if(!level.empty()&&level!="novice")throw std::invalid_argument("only novice level migrated in native combat checkpoint");
      if(string(p,"brain","alone")!="alone")throw std::invalid_argument("formation brains pending native migration");
      if(present(p,"lookahead")&&js::truth(js::get(p,"lookahead")))throw std::invalid_argument("lookahead pending native migration");
      if(level=="novice")c.skills[t]=CombatSkills{};
      if(present(p,"skills"))skills(c.skills[t],js::get(p,"skills"));
    }}
  if(present(o,"abilOff")){const auto& sides=array(js::get(o,"abilOff"));if(sides.size()>2)throw std::invalid_argument("invalid ability sides");
    const std::array<std::string,6> names{"charge","shield","aimed","disengage","barrage","slow"};
    for(size_t t=0;t<sides.size();++t){if(sides[t].tag==V::Null)continue;for(const auto value:array(sides[t])){const auto name=js::str(value);auto i=std::find(names.begin(),names.end(),name);if(i==names.end())throw std::invalid_argument("unknown ability");c.abilityOff[t][size_t(i-names.begin())]=true;}}}
  if(!(c.shotSpeed>0))throw std::invalid_argument("shot speed must be positive");return c;
}
} // namespace astelia
