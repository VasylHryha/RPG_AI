// JSON-allocation-only probe using the unchanged value implementation: no fight.
#include "js_value.h"
#include "bounded_json.h"
#include <sys/resource.h>
size_t peakRSS(){rusage r{};if(getrusage(RUSAGE_SELF,&r))throw std::runtime_error("getrusage failed");
 size_t peak=r.ru_maxrss;
#ifndef __APPLE__
 peak*=1024;
#endif
 return peak;
}
int main(int argc,char** argv){
 if(argc!=2)return 2;std::string mode=argv[1],line;
 bool dynamic=mode=="dynamic-cached"||mode=="dynamic-flat",gc=mode=="gc"||dynamic;
 auto request=js::parse("[{\"sentinel\":\"outer batch retained\"},{}]");
 size_t before=0,after=0,frameBytes=0;unsigned ticks=0;bool stopped=false;
 stagea::FrameLayouts layouts;
 if(!dynamic)std::getline(std::cin,line);
 while(dynamic?bool(std::getline(std::cin,line)):ticks<128){
  js::V row;
  if(dynamic){auto keys=js::parse(line);std::vector<std::pair<std::string,js::V>> fields;
   for(auto key:keys.p->items)fields.push_back({js::str(key),true});
   if(mode=="dynamic-flat")row=layouts.object(fields);
   else{row=js::obj({});for(const auto& field:fields)js::set(row,field.first,field.second);}
  }else row=js::parse(line);
  auto bytes=js::stringify(row);if(bytes.empty())return 3;frameBytes=line.size();
  before=js::arena.size();if(gc)js::collect({request},0);after=js::arena.size();layouts.clear();++ticks;
  if(peakRSS()>256*1024*1024){stopped=true;break;}
 }
 if(js::str(js::get(js::get(request,0),"sentinel"))!="outer batch retained")return 4;
 std::cout<<"{\"mode\":\""<<mode<<"\",\"gc\":"<<(gc?"true":"false")<<",\"ticks\":"<<ticks<<",\"frame_bytes\":"<<frameBytes
 <<",\"arena_before\":"<<before<<",\"arena_after\":"<<after<<",\"cached_shapes\":"<<js::shapes.size()
 <<",\"stopped_at_256MiB\":"<<(stopped?"true":"false")<<",\"peak_rss_bytes\":"<<peakRSS()<<"}\n";
}
