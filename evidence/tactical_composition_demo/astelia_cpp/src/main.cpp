#include "formation_sim.h"
#include "builtins.h"
#include <fstream>
#include <filesystem>
#include <map>

using namespace js;
static size_t permanentCells;
static V inputRoot, batchRoot;
static uint64_t executedFights=0, executedSteps=0;
static std::string bits(double d){uint64_t u;std::memcpy(&u,&d,8);std::ostringstream out;out<<std::hex<<std::setfill('0')<<std::setw(16)<<u;return out.str();}
static V sanitize(V v){
  if(v.tag!=V::Heap)return v;if(v.p->kind==Object::Function)return V("[function]");
  if(truth(get(v,"units"))&&truth(get(v,"o")))return V("[world]");
  if(get(v,"id").tag!=V::Undefined&&get(v,"alive").tag!=V::Undefined)return obj({{"unit",get(v,"id")}});
  if(v.p->kind==Object::Array){Args out;for(V x:v.p->items)out.push_back(sanitize(x));return arr(out);}
  if(v.p->kind==Object::Map||v.p->kind==Object::Set){Args out;for(auto& p:v.p->ordered->entries)out.push_back(v.p->kind==Object::Map?arr({sanitize(p.first),sanitize(p.second)}):sanitize(p.first));return obj({{v.p->kind==Object::Map?"map":"set",arr(out)}});}
  V out=obj();for(V k:keys(v))if(!eq(k,V("net")))set(out,k,sanitize(get(v,k)));return out;
}
static V state(V world,std::map<int,V>& known,bool debug){
  for(V u:iter(get(world,"units")))known[int(num(get(u,"id")))]=u;
  Args us;
  for(auto& entry:known){V u=entry.second,out=obj();for(const char* key:{"id","team","role","kind","x","y","hp","cd","alive"}){V value=get(u,key);if(value.tag!=V::Undefined)set(out,key,value);}
    V target=get(u,"target");set(out,"target",truth(target)?get(target,"id"):V(nullptr));V fp=obj();for(const char* k:{"x","y","hp","cd"})set(fp,k,V(bits(num(get(u,k)))));set(out,"bits",fp);
    if(debug){V d=obj();for(V k:keys(u))if(!eq(k,V("w")))set(d,k,sanitize(get(u,k)));set(out,"debug",d);}us.push_back(out);}
  V out=obj({{"t",get(world,"t")},{"units",arr(us)},{"bits",V(bits(num(get(world,"t"))))}});
  if(debug){V d=obj();for(const char* k:{"packs","shots","shells","fields","stats","hitLog"})set(d,k,sanitize(get(world,k)));set(d,"rand",method(get(world,"rand"),"state",{}));set(out,"debug",d);}return out;
}
static V fight(V req){
  V op=get(req,"operation");
  if(eq(op,V("fixed")))return method(get(req,"value"),"toFixed",{get(req,"digits")});
  if(eq(op,V("echo")))return get(req,"value");
  if(eq(op,V("keys")))return builtin("Object.keys",{get(req,"value")});
  if(eq(op,V("string"))){V methodName=get(req,"method");if(eq(methodName,V("length")))return get(get(req,"value"),"length");V a=get(req,"args");return method(get(req,"value"),str(methodName),truth(a)?iter(a):Args{});}
  if(eq(op,V("math"))){V value=builtin("Math."+str(get(req,"name")),iter(get(req,"args")));return obj({{"value",value},{"bits",V(bits(num(value)))}});}
  if(eq(op,V("rng"))){V mode=get(req,"drawMode");if(!truth(mode))mode="any";return simulation::drawOpponents({get(req,"seed"),get(req,"rounds"),mode});}
  V options=obj();V opponent=get(req,"opponent");if(truth(opponent))assign(options,simulation::enemyOf({opponent}));assign(options,get(req,"options"));
  V mode=get(req,"mode");if(!truth(mode))mode="alone";
  V w;int tick=0;std::map<int,V> known;
  bool trace=truth(get(req,"trace"));
  try{
    ++executedFights;
    w=simulation::create({mode,options});
    auto dump=[&](){std::cout<<stringify(obj({{"step",V(tick)},{"state",state(w,known,truth(get(req,"debug")))}}))<<'\n';};
    if(trace)dump();
    while(!truth(simulation::done({w}))){
      ++executedSteps;simulation::step({w});++tick;if(trace)dump();
      if(arena.size()>50000||cells.size()>100000){Args roots=simulation::roots();roots.push_back(w);roots.push_back(req);roots.push_back(inputRoot);roots.push_back(batchRoot);for(auto& p:known)roots.push_back(p.second);collect(std::move(roots),permanentCells);}
    }
    return simulation::summary({w});
  }catch(const std::exception& e){return obj({{"error",V(e.what())}});}
}
int main(int argc,char** argv){
  try{
    simulation::initialize();permanentCells=cells.size();
    bool metrics=false;std::string net;
    for(int i=1;i<argc;++i)if(std::string(argv[i])=="--metrics")metrics=true;else if(net.empty())net=argv[i];else throw std::runtime_error("unexpected argument");
    if(net.empty())net=(std::filesystem::absolute(argv[0]).parent_path().parent_path().parent_path()/"astelia_snapshot"/"bc_net.json").string();
    std::ifstream inputNet(net);if(!inputNet)throw std::runtime_error("cannot open bc_net.json: "+net);
    std::string contents((std::istreambuf_iterator<char>(inputNet)),{});simulation::setNet({parse(contents)});
    std::string line;while(std::getline(std::cin,line)){
      if(line.find_first_not_of(" \t\r\n")==std::string::npos)continue;
      try{V request=parse(line),output;inputRoot=request;batchRoot=arr();if(request.tag==V::Heap&&request.p->kind==Object::Array){for(V r:iter(request))batchRoot.p->items.push_back(fight(r));output=batchRoot;}else output=fight(request);
        std::cout<<stringify(output)<<std::endl;
      }catch(const std::exception& e){std::cout<<stringify(obj({{"error",V(e.what())}}))<<std::endl;}
      inputRoot=V();batchRoot=V();collect(simulation::roots(),permanentCells);
    }
    if(metrics)std::cerr<<"{\"executed_fights\":"<<executedFights<<",\"executed_steps\":"<<executedSteps<<",\"cache_hits\":0}\n";
    return 0;
  }catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}
}
