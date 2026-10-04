// Dynamic JSON values stop at this boundary; combat reads typed configuration.
#include "config_codec.h"
#include "world.h"
#include "formation.h"
#include "artillery.h"
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
  only(v,{"lead","abilities","kite","pursuit","dodgeShots","shotReact","dodgeShells","lobLead","leaderBracket","leaderFire","lockedDodge","reactAim",
    "fireControl","fireDepth","holdFire","jink","killSpeed","waves","artyFire","artyRobust","artyHerd","artyRollout","artyFollow","artyBattery","artyModel","artyOwn",
    "meleeFocus","saveWounded","weaponsFree","castDodge","combos","artyEvery"});
  const auto lead=string(v,"lead",s.lead==Lead::None?"none":s.lead==Lead::Raw?"raw":"smooth");
  if(lead=="none")s.lead=Lead::None;else if(lead=="raw")s.lead=Lead::Raw;else if(lead=="smooth")s.lead=Lead::Smooth;else throw std::invalid_argument("unknown lead");
  const auto ability=string(v,"abilities",s.abilities==AbilityPolicy::Off?"off":s.abilities==AbilityPolicy::Auto?"auto":"coordinated");
  if(ability=="off")s.abilities=AbilityPolicy::Off;else if(ability=="auto")s.abilities=AbilityPolicy::Auto;else if(ability=="coordinated")s.abilities=AbilityPolicy::Coordinated;else throw std::invalid_argument("unknown ability policy");
  s.kite=number(v,"kite",s.kite);s.shotReact=number(v,"shotReact",s.shotReact);
  const auto pursuit=string(v,"pursuit",s.pursuitCut?"cut":"chase");
  if(pursuit!="cut"&&pursuit!="chase")throw std::invalid_argument("unknown pursuit");s.pursuitCut=pursuit=="cut";
  if(present(v,"dodgeShots")){auto x=js::get(v,"dodgeShots");if(x.tag==V::Boolean){s.dodgeShots=bool(x.n);s.dodgeSoft=false;}
    else if(js::str(x)=="soft"){s.dodgeShots=s.dodgeSoft=true;}else throw std::invalid_argument("unknown shot dodge");}
  if(present(v,"dodgeShells")){const auto x=js::get(v,"dodgeShells");s.planShells=s.smartShells=s.dodgeShells=false;
    if(x.tag==V::Boolean)s.dodgeShells=bool(x.n);else if(js::str(x)=="plan")s.planShells=true;else if(js::str(x)=="smart")s.smartShells=true;else throw std::invalid_argument("unknown shell dodge");}
  if(present(v,"lobLead")){auto x=js::get(v,"lobLead");if(x.tag==V::Boolean){s.lobLead=bool(x.n);s.adaptiveLobLead=false;}
    else if(js::str(x)=="adaptive"){s.lobLead=false;s.adaptiveLobLead=true;}else throw std::invalid_argument("unknown lob lead");}
  if(s.kite<0||s.shotReact<0)throw std::invalid_argument("negative combat skill");
  #define B(key) s.key=boolean(v,#key,s.key)
  #define N(key) s.key=number(v,#key,s.key)
  B(leaderFire);B(lockedDodge);B(reactAim);B(fireControl);B(killSpeed);B(artyBattery);B(artyOwn);B(meleeFocus);B(weaponsFree);B(castDodge);
  N(leaderBracket);N(fireDepth);N(jink);N(saveWounded);N(artyRobust);N(artyHerd);N(artyEvery);s.waves=count(v,"waves",s.waves);
  #undef B
  #undef N
  if(present(v,"artyFire")){const auto name=string(v,"artyFire","");if(name!="single"&&name!="plan")throw std::invalid_argument("unknown artillery fire");s.artyPlan=name=="plan";}
  if(present(v,"artyModel")){const auto name=string(v,"artyModel","");if(name!="simple"&&name!="exact")throw std::invalid_argument("unknown artillery model");s.artyExact=name=="exact";}
  if(present(v,"artyFollow")){const auto x=js::get(v,"artyFollow");s.followShooters=x.tag==V::String&&js::str(x)=="shooters";
    if(x.tag!=V::Boolean&&!s.followShooters)throw std::invalid_argument("unknown artillery follow");s.artyFollow=s.followShooters||bool(x.n);}
  if(present(v,"combos")){const auto list=js::get(v,"combos");s.combosEnabled=list.tag!=V::Null;s.combos.clear();if(s.combosEnabled)for(auto entry:array(list)){const auto name=js::str(entry);if(name=="tchain")s.combos.push_back(ComboKind::Tchain);else if(name=="fixlob")s.combos.push_back(ComboKind::Fixlob);else throw std::invalid_argument("unknown combo: "+name);}}
  if(present(v,"holdFire")){s.holdWave=s.holdSync=0;const auto h=js::get(v,"holdFire");if(js::truth(h)){only(h,{"wave","sync"});s.holdWave=number(h,"wave",0);s.holdSync=number(h,"sync",0);if(s.holdWave<0||s.holdSync<0)throw std::invalid_argument("invalid fire gate");}}
  if(present(v,"artyRollout")){s.rollout={};const auto ro=js::get(v,"artyRollout");if(js::truth(ro)){only(ro,{"top","horizon","shape","score","dt","every"});s.rollout.enabled=true;s.rollout.top=count(ro,"top",5);s.rollout.horizon=number(ro,"horizon",2);s.rollout.dt=number(ro,"dt",0);s.rollout.every=number(ro,"every",0);
    const auto score=string(ro,"score","");if(score!=""&&score!="ltd2"&&score!="hp")throw std::invalid_argument("unknown rollout score");s.rollout.ltd2=score=="ltd2";
    if(present(ro,"shape"))for(auto name:array(js::get(ro,"shape")))s.rollout.shape.push_back(attackByName(js::str(name)));
    if(!s.rollout.top||s.rollout.top>100000||s.rollout.horizon<=0||s.rollout.dt<0||s.rollout.every<0)throw std::invalid_argument("invalid artillery rollout budget/horizon");}}
}
Brain brain(const std::string& name){if(name=="alone")return Brain::Alone;if(name=="formation")return Brain::Formation;if(name=="rules"||name=="reactive")return Brain::Rules;
  if(name=="storm")return Brain::Storm;if(name=="wolfpack")return Brain::Wolfpack;if(name=="gamepack")return Brain::Gamepack;throw std::invalid_argument("unknown brain: "+name);}
void formation(Formation& f,V v){
  only(v,{"preset","shape","frontSpacing","rankSpacing","rangedRanks","screenGap","rearGap","standoff","turnRate","syncRadius","syncGate","holdWhileClosing","closingSpeed",
    "zoneDepth","zoneBehind","zoneSideMargin","coverFraction","maxStrikersPerTarget","dive","diveMinTargets","diveRange","laneLeash","kiteLeash","engagedWeight","shooterFocus","squadSize",
    "meleeDoctrine","autoAttack","flankWidth","flankDepth","flankWait","artilleryDoctrine","anchorMode","siegeMargin","siegeArtMargin","meleeKeepAway","siegeOwnArtMargin","siegeMinArt","peelRadius",
    "dodge","fireDepth","fireControl","surroundRing","surroundArc","surroundDist","surroundLanes","oblique","surroundMelee","surroundCorner","jink","release","raidTarget","flankForce","flankTarget",
    "anchorSpeed","surround","coordAbilities","shotDodge","smoothLead","pursuit","holdFire"});
  #define N(key) f.key=number(v,#key,f.key)
  #define B(key) f.key=boolean(v,#key,f.key)
  N(frontSpacing);N(rankSpacing);N(rangedRanks);N(screenGap);N(rearGap);N(standoff);N(turnRate);N(syncRadius);N(closingSpeed);
  N(zoneDepth);N(zoneBehind);N(zoneSideMargin);N(coverFraction);N(maxStrikersPerTarget);N(diveMinTargets);N(diveRange);N(laneLeash);N(kiteLeash);N(engagedWeight);N(squadSize);
  N(flankWidth);N(flankDepth);N(flankWait);N(siegeMargin);N(siegeArtMargin);N(meleeKeepAway);N(siegeOwnArtMargin);N(siegeMinArt);N(peelRadius);N(fireDepth);
  N(surroundRing);N(surroundArc);N(surroundDist);N(jink);N(anchorSpeed);
  B(syncGate);B(holdWhileClosing);B(dive);B(dodge);B(fireControl);B(surroundLanes);B(oblique);B(surroundCorner);B(flankForce);B(surround);B(coordAbilities);
  #undef N
  #undef B
  const auto enumeration=[&](const char* key,std::initializer_list<const char*> names,int fallback){const auto name=string(v,key,"");if(name.empty())return fallback;int i=0;for(auto value:names){if(name==value)return i;++i;}throw std::invalid_argument(std::string("unknown formation ")+key);};
  f.shape=Shape(enumeration("shape",{"line","wedge","box","column","screen","crescent","ring"},int(f.shape)));
  f.meleeDoctrine=MeleeDoctrine(enumeration("meleeDoctrine",{"zone","screen","flank","anvil","auto"},int(f.meleeDoctrine)));
  f.autoAttack=MeleeDoctrine(enumeration("autoAttack",{"zone","screen","flank","anvil","auto"},int(f.autoAttack)));
  f.shooterFocus=ShooterFocus(enumeration("shooterFocus",{"spread","one","squads","nearest","protect","soft"},int(f.shooterFocus)));
  f.artilleryDoctrine=ArtilleryDoctrine(enumeration("artilleryDoctrine",{"cluster","pinned","counter","soft"},int(f.artilleryDoctrine)));
  f.anchorMode=AnchorMode(enumeration("anchorMode",{"standoff","siege"},int(f.anchorMode)));
  f.raidTarget=SoftTarget(enumeration("raidTarget",{"soft","artillery"},int(f.raidTarget)));f.flankTarget=SoftTarget(enumeration("flankTarget",{"soft","artillery"},int(f.flankTarget)));
  f.surroundScreen=enumeration("surroundMelee",{"ring","screen"},f.surroundScreen?1:0)==1;
  if(present(v,"release")){f.release=0;if(js::get(v,"release").tag!=V::Null)for(const auto r:array(js::get(v,"release"))){const auto type=role(js::str(r));if(size_t(type)>2)throw std::invalid_argument("invalid released role");f.release|=1<<size_t(type);}}
  if(f.rangedRanks<1||f.rangedRanks>1e6||f.squadSize<1||f.squadSize!=std::floor(f.squadSize)||f.turnRate<0||f.turnRate>1||f.frontSpacing<0||f.rankSpacing<0||f.syncRadius<0||f.laneLeash<0||f.kiteLeash<0||f.anchorSpeed<0)throw std::invalid_argument("invalid formation geometry/count");
}
Tactics tactics(V v){Tactics out;if(v.tag==V::String){out.role.fill(planByName(js::str(v)));return out;}only(v,{"position","melee","ranged","artillery"});size_t i=0;
  for(const auto key:{"position","melee","ranged","artillery"})out.role[i++]=planByName(string(v,key,""));return out;}
std::shared_ptr<const Network> network(V value){only(value,{"W1","b1","W2","b2"});auto net=std::make_shared<Network>();
  const auto vector=[&](V v,std::vector<double>& target){for(auto x:array(v)){if(x.tag!=V::Number||!std::isfinite(x.n))throw std::invalid_argument("invalid network coefficient");target.push_back(x.n);}};
  const auto& w1=array(js::get(value,"W1"));const auto& w2=array(js::get(value,"W2"));if(w1.empty()||w2.empty()||w1.size()>4096||w2.size()>4096)throw std::invalid_argument("invalid network layers");
  net->hidden=uint32_t(w1.size());net->outputs=uint32_t(w2.size());net->inputs=uint32_t(array(w1[0]).size());if(net->inputs>4096)throw std::invalid_argument("too many network inputs");
  for(auto row:w1){if(array(row).size()!=net->inputs)throw std::invalid_argument("ragged network W1");vector(row,net->w1);}for(auto row:w2){if(array(row).size()!=net->hidden)throw std::invalid_argument("ragged network W2");vector(row,net->w2);}
  vector(js::get(value,"b1"),net->b1);vector(js::get(value,"b2"),net->b2);net->validate();return net;
}
Lookahead look(V v){Lookahead la;if(!js::truth(v))return la;la.enabled=true;
  const auto named=[&](const std::string& name){if(name!="full"&&name!="fast"&&name!="mind")throw std::invalid_argument("unknown lookahead: "+name);
    if(name!="full"){la.network=frozenNetwork();la.netPrune=3;}if(name=="mind"){la.mind=true;la.models={EnemyModel::Continue,EnemyModel::Rush};la.blend=.7;}};
  if(v.tag==V::String){named(js::str(v));return la;}if(v.tag==V::Boolean)return la;
  only(v,{"extends","every","horizon","dt","k","inertia","models","contact","plans","net","netPrune","mind","budget","robustTop","blend","terminal","stall","objective","urgency","everyStable","extra","tweakMargin"});
  if(present(v,"extends"))named(string(v,"extends","full"));
  #define N(key) la.key=number(v,#key,la.key)
  N(every);N(horizon);N(dt);N(k);N(inertia);N(contact);N(blend);N(terminal);N(stall);N(everyStable);N(tweakMargin);
  #undef N
  la.mind=boolean(v,"mind",la.mind);la.netPrune=count(v,"netPrune",la.netPrune);la.budget=count(v,"budget",la.budget);la.robustTop=count(v,"robustTop",la.robustTop);
  const auto plans=[&](const char* key,std::vector<Plan>& dest){if(present(v,key)){dest.clear();for(auto name:array(js::get(v,key)))dest.push_back(planByName(js::str(name)));}};plans("plans",la.plans);plans("extra",la.extra);
  if(present(v,"net"))la.network=js::truth(js::get(v,"net"))?network(js::get(v,"net")):nullptr;
  if(present(v,"models")){la.models.clear();for(auto entry:array(js::get(v,"models"))){const auto name=js::str(entry);if(name=="oracle")la.models.push_back(EnemyModel::Oracle);else if(name=="continue")la.models.push_back(EnemyModel::Continue);else if(name=="rush")la.models.push_back(EnemyModel::Rush);else if(name=="rules")la.models.push_back(EnemyModel::Rules);else throw std::invalid_argument("unknown enemy model: "+name);}}
  if(present(v,"objective")){const auto name=string(v,"objective","");if(name!="hp"&&name!="deaths")throw std::invalid_argument("unknown lookahead objective");la.hasObjective=true;la.deaths=name=="deaths";}
  if(present(v,"urgency")&&js::truth(js::get(v,"urgency"))){auto u=js::get(v,"urgency");only(u,{"from","kMin"});la.urgency=true;la.urgencyFrom=number(u,"from",0);la.urgencyMin=number(u,"kMin",0);if(la.urgencyFrom<0||la.urgencyFrom>=1||la.urgencyMin<0||la.urgencyMin>1)throw std::invalid_argument("invalid urgency settings");}
  if(la.every<0||la.horizon<=0||la.dt<0||la.k<0||la.contact<0||la.terminal<0||la.stall<0||la.everyStable<0||la.budget==0||la.robustTop==0||la.blend<0||la.blend>1||la.plans.empty()||la.models.empty()||la.budget>100000||la.plans.size()>100000)throw std::invalid_argument("invalid lookahead budget/horizon");
  if(la.network&&(la.network->inputs!=33+la.plans.size()||la.network->outputs!=la.plans.size()))throw std::invalid_argument("network plans/features mismatch");return la;
}
void thresholds(AbilityThresholds& a,V v){only(v,{"chargeSync","shieldAimedAt","shieldShellWindow","aimedSafe","aimedWorth","disengageNear","barrageMin","barrageHeld","slowMin","slowMoving"});
  #define N(key) a.key=number(v,#key,a.key)
  N(chargeSync);N(shieldAimedAt);N(shieldShellWindow);N(aimedSafe);N(aimedWorth);N(disengageNear);N(barrageMin);N(barrageHeld);N(slowMin);N(slowMoving);
  #undef N
}
}
Config configuration(const js::V& request) {
  only(request,{"mode","options","trace","opponent","debug"});
  const auto mode=string(request,"mode","alone");brain(mode);
  V o=js::get(request,"options");if(o.tag==V::Undefined)o=js::obj({});
  only(o,{"seed","dt","duration","width","height","army","scenario","swapSides","rules","abilities","sandboxAbilities","ai","shots","shotSpeed","windUp",
    "hunters","enemyArmy","ours","unitSet","skirmishSet","temporal","playerStyle","perception","attackerCap","abilOff",
    "enemy","enemyF","f","reactiveBase","shotDodge","shotReact","shellDodgeAll","smoothLead","pursuit","kiteRadius",
    "forcePlan","forceTeam","disablePlans","lookahead","ab","coordAbilities","reactAim","reactiveDodge"});
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
      if(!found&&size_t(k.role)<3){constexpr double prot[]={.2033,.1524,.1547};k.protection=prot[size_t(k.role)];}
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
  std::string enemy=string(o,"enemy","alone");V enemyForm=present(o,"enemyF")?js::get(o,"enemyF"):js::obj({{"preset","wedge hold"}});
  if(present(request,"opponent")&&!present(o,"enemy")){const auto name=string(request,"opponent","");
    if(name=="alone"||name=="storm"||name=="wolfpack"||name=="gamepack")enemy=name;
    else{enemy="formation";if(!present(o,"enemyF"))enemyForm=js::obj({{"preset",name}});}}
  V oursForm=present(o,"f")?js::get(o,"f"):js::obj({});
  if(mode=="reactive"){
    V base=present(o,"reactiveBase")?js::get(o,"reactiveBase"):js::obj({{"preset","wide line"}});V merged=js::obj({});
    for(auto key:js::keys(base))js::set(merged,key,js::get(base,key));for(auto key:js::keys(oursForm))js::set(merged,key,js::get(oursForm,key));oursForm=merged;
  }
  for(auto& s:c.skills){s.abilities=AbilityPolicy::Auto;s.kite=number(o,"kiteRadius",70);s.shotReact=number(o,"shotReact",.12);
    s.dodgeShots=c.rules==Rules::Sandbox&&boolean(o,"shotDodge",true);s.dodgeShells=c.rules==Rules::Sandbox&&boolean(o,"shellDodgeAll",true);
    s.lead=c.rules==Rules::Game?Lead::None:boolean(o,"smoothLead",true)?Lead::Smooth:Lead::Raw;s.pursuitCut=c.rules==Rules::Sandbox&&string(o,"pursuit","cut")=="cut";}
  std::array<V,2> profiles{js::obj({}),js::obj({})};if(present(o,"ai")){const auto& list=array(js::get(o,"ai"));if(list.size()>2)throw std::invalid_argument("expected at most two profiles");
    for(size_t t=0;t<list.size();++t)if(list[t].tag!=V::Null)profiles[t]=list[t];}
  c.reactiveDodge=boolean(o,"reactiveDodge",true);
  for(size_t t=0;t<2;++t){const auto p=profiles[t];only(p,{"level","brain","skills","lookahead","formation","ab","disablePlans","fewPlan","objective"});
    const auto level=string(p,"level","");if(!level.empty()&&level!="novice"&&level!="regular"&&level!="veteran"&&level!="elite"&&level!="elite-fast")throw std::invalid_argument("unknown level");
    const auto oldBrain=t==0?mode:c.scenario==Scenario::Mirror?enemy:"alone";
    const auto defaultBrain=level=="novice"?"alone":level=="regular"?"formation":level.empty()?oldBrain:"rules";
    c.brains[t]=brain(string(p,"brain",defaultBrain));
    V baseForm=t==0?oursForm:enemyForm;
    // Profile skill defaults read the legacy formation before the level's
    // formation replacement, exactly as buildProfile does.
    auto& s=c.skills[t];s.abilities=c.brains[t]==Brain::Rules&&boolean(o,"coordAbilities",true)?AbilityPolicy::Coordinated:AbilityPolicy::Auto;
    if(present(baseForm,"holdFire"))skills(s,js::obj({{"holdFire",js::get(baseForm,"holdFire")}}));
    s.reactAim=boolean(o,"reactAim",true);s.fireControl=boolean(baseForm,"fireControl",false);s.fireDepth=number(baseForm,"fireDepth",0);s.jink=number(baseForm,"jink",0);
    s.planShells=c.rules==Rules::Sandbox&&!boolean(o,"shellDodgeAll",true);
    if(c.rules==Rules::Sandbox){
      if(present(baseForm,"shotDodge")){V value=js::obj({{"dodgeShots",js::get(baseForm,"shotDodge")}});skills(s,value);}
      if(present(baseForm,"smoothLead"))s.lead=boolean(baseForm,"smoothLead",true)?Lead::Smooth:Lead::Raw;
      if(present(baseForm,"pursuit"))s.pursuitCut=string(baseForm,"pursuit","cut")=="cut";
    }
    if(level=="novice"){s.dodgeShots=s.dodgeSoft=s.dodgeShells=s.planShells=s.smartShells=false;s.shotReact=.3;s.lead=Lead::None;s.pursuitCut=false;s.kite=0;s.abilities=AbilityPolicy::Off;s.reactAim=false;}
    if(level=="regular"){s.dodgeShots=s.dodgeSoft=false;s.shotReact=.2;s.dodgeShells=true;s.planShells=s.smartShells=false;s.lead=Lead::Raw;s.pursuitCut=false;s.abilities=AbilityPolicy::Auto;s.reactAim=false;baseForm=js::obj({{"preset","line"}});}
    if(level=="veteran"||level=="elite"||level=="elite-fast"){s.artyPlan=s.lockedDodge=true;baseForm=js::obj({{"preset","wide line"}});}
    if(level=="elite"||level=="elite-fast"){s.smartShells=true;s.dodgeShells=s.planShells=false;s.castDodge=s.weaponsFree=s.artyBattery=true;s.saveWounded=.3;s.rollout.enabled=s.rollout.ltd2=true;s.rollout.shape={AttackFamily::Battery,AttackFamily::Split,AttackFamily::Herd};if(level=="elite-fast"){s.rollout.dt=.1;s.rollout.every=.3;}js::set(baseForm,"oblique",true);}
    if(present(p,"formation"))baseForm=js::get(p,"formation");
    const auto preset=string(baseForm,"preset",c.brains[t]==Brain::Rules?"wide line":"");c.formations[t]=presetFormation(preset);formation(c.formations[t],baseForm);
    if(c.brains[t]==Brain::Storm)c.formations[t]=presetFormation("line anvil");
    if(c.brains[t]==Brain::Wolfpack){c.formations[t]=presetFormation("loose");c.formations[t].dodge=true;}
    if(c.brains[t]==Brain::Gamepack)c.formations[t]=presetFormation("line");
    if(present(p,"skills"))skills(s,js::get(p,"skills"));
    const V la=present(p,"lookahead")?js::get(p,"lookahead"):(level=="elite"||level=="elite-fast")?js::obj({{"extends","fast"},{"terminal",6},{"stall",10}}):!level.empty()?V(nullptr):t==0&&present(o,"lookahead")?js::get(o,"lookahead"):V(nullptr);
    c.lookahead[t]=look(la);if(c.lookahead[t].enabled&&present(p,"objective")){const auto objective=string(p,"objective","");if(objective!="hp"&&objective!="deaths")throw std::invalid_argument("unknown profile objective");c.lookahead[t].hasObjective=true;c.lookahead[t].deaths=objective=="deaths";}
    if(present(o,"ab"))thresholds(c.abilityThresholds[t],js::get(o,"ab"));if(present(p,"ab"))thresholds(c.abilityThresholds[t],js::get(p,"ab"));
    if(present(p,"disablePlans")||(t==0&&present(o,"disablePlans"))){const auto value=present(p,"disablePlans")?js::get(p,"disablePlans"):js::get(o,"disablePlans");
      for(auto name:array(value))c.disabledPlans[t].push_back(planByName(js::str(name)));}
    c.fewPlan[t]=planByName(string(p,"fewPlan","surround"));
  }
  if(present(o,"forcePlan")&&js::truth(js::get(o,"forcePlan"))){c.forcePlan=tactics(js::get(o,"forcePlan"));c.hasForcePlan=true;const auto team=count(o,"forceTeam",0);if(team>1)throw std::invalid_argument("invalid forced team");c.forceTeam=uint8_t(team);}
  if(present(o,"abilOff")){const auto& sides=array(js::get(o,"abilOff"));if(sides.size()>2)throw std::invalid_argument("invalid ability sides");
    const std::array<std::string,6> names{"charge","shield","aimed","disengage","barrage","slow"};
    for(size_t t=0;t<sides.size();++t){if(sides[t].tag==V::Null)continue;for(const auto value:array(sides[t])){const auto name=js::str(value);auto i=std::find(names.begin(),names.end(),name);if(i==names.end())throw std::invalid_argument("unknown ability");c.abilityOff[t][size_t(i-names.begin())]=true;}}}
  if(!(c.shotSpeed>0))throw std::invalid_argument("shot speed must be positive");return c;
}
} // namespace astelia
