// Exercise the real Stage A collector, including GC's interned-string lifetime.
#include "stagea.h"
#include "react.h"
#include <stdexcept>
int main(){
 astelia::World w(std::make_shared<const astelia::Config>());
 auto owned=std::make_unique<react_v1::Controller>(1,0,astelia::ControllerParams{},astelia::control::V7Selector::P16);
 auto& c=*owned;c.stage.collect=true;w.controllers[0]=std::move(owned);
 auto batch=js::parse("[{\"sentinel\":\"current request\"},{\"sentinel\":\"next request\"}]");
 auto completed=js::parse("{\"sentinel\":\"previous fight result\"}");
 auto trace=js::parse("{\"sentinel\":\"trace history\"}");
 c.shape.audit.push_back(js::parse("{\"sentinel\":\"shape pending\"}"));
 c.shape.shotEvents.push_back(js::parse("{\"sentinel\":\"shot pending\"}"));
 c.battery.audit.push_back(js::parse("{\"sentinel\":\"battery pending\"}"));
 for(uint64_t tick=1;tick<=4501;++tick){
  c.stage.input=js::parse("{\"temporary\":\"input consumed by record\",\"numbers\":[1,2,3,4]}");
  std::vector<std::pair<std::string,js::V>> fields;
  for(unsigned key=0;key<2500;++key)if((key+tick)%7)fields.push_back({std::to_string(key)+":"+std::to_string(key+tick%5),true});
  auto dynamic=c.stage.layouts.object(fields);js::set(c.stage.input,"pairModes",dynamic);
  if(js::get(dynamic,fields.back().first).tag!=js::V::Boolean)return 5;
  if(js::stringify(dynamic).find(fields.front().first)==std::string::npos)return 6;
  auto transient=js::parse("{\"temporary\":\"serialized observer\"}");(void)js::stringify(transient);
  stagea::collectTick(w,{completed,batch,trace},tick);
  if(js::arena.size()>20||c.stage.input.tag!=js::V::Undefined||!c.stage.layouts.owned.empty()||js::shapes.size()>100)return 2;
  for(auto value:js::Args{js::get(batch,0),js::get(batch,1),completed,trace,c.shape.audit.at(0),c.shape.shotEvents.at(0),c.battery.audit.at(0)})
   if(js::str(js::get(value,"sentinel")).empty())return 3;
 }
 if(js::str(js::get(js::get(batch,1),"sentinel"))!="next request")return 4;
 std::cout<<"{\"gc_ticks\":4501,\"live_json_objects\":"<<js::arena.size()<<",\"roots_preserved\":true}\n";
}
