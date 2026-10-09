// One native call builds every own unit's ragged banks. No oracle inputs.
#include "candidates.h"
#include <string>
static thread_local std::vector<double> output;
static thread_local std::string error;
extern "C" const char* candidate_error(){return error.c_str();}
extern "C" long candidate_batch(const double* input,const int* counts,double width,double height,int allow_missing_aim,const double** result){
 try {
  stageb2::Frame f;f.width=width;f.height=height;
  std::vector<stageb2::Row>* banks[]={&f.units,&f.own,&f.shells,&f.shots,&f.fields,&f.casts};
  int widths[]={23,10,9,7,5,7};
  for(int b=0;b<6;++b){if(counts[b]<0||counts[b]>128)throw std::invalid_argument("batch size");for(int i=0;i<counts[b];++i){banks[b]->emplace_back(input,input+widths[b]);input+=widths[b];}}
  for(int i=0;i<counts[6];++i){f.longVelocity[unsigned(input[0])]={input[1],input[2]};input+=3;}
  auto units=f.units;std::sort(units.begin(),units.end(),[](auto& a,auto& b){return a[0]<b[0];});
  output.clear();
  for(auto& u:units)if(u[1]==0){auto bank=stageb2::candidates(f,unsigned(u[0]),allow_missing_aim!=0);output.insert(output.end(),{u[0],double(bank.aim.size()),double(bank.move.size())});
   for(auto* cs:{&bank.aim,&bank.move})for(auto& c:*cs){output.push_back(c.point.x);output.push_back(c.point.y);output.insert(output.end(),c.features.begin()+11,c.features.end());output.push_back(c.type);output.push_back(c.source);}
  }
  *result=output.data();return long(output.size());
 }catch(const std::exception& e){error=e.what();*result=nullptr;return -1;}
}
