#include <cmath>
#include <chrono>
#include <cstdio>
#include <vector>
#include <math.h>
int main(){
  std::vector<double> a(600),b(600),s(300),c(300);
  for(int i=0;i<600;i++)a[i]=-(i%97)*0.013;
  for(int i=0;i<300;i++)s[i]=(i%91)*0.07-3;
  volatile double sink=0;
  auto t0=std::chrono::steady_clock::now();
  for(int r=0;r<100000;r++){for(int i=0;i<600;i++)b[i]=std::exp(a[i]+r*1e-12);sink=sink+b[r%600];}
  auto t1=std::chrono::steady_clock::now();
  for(int r=0;r<100000;r++){for(int i=0;i<300;i++)__sincos(s[i]+r*1e-12,&c[i],&b[i]);sink=sink+b[r%300];}
  auto t2=std::chrono::steady_clock::now();
  for(int r=0;r<100000;r++){for(int i=0;i<300;i++)b[i]=std::sqrt(s[i]*s[i]+r*1e-12)/ (s[i]+4.);sink=sink+b[r%300];}
  auto t3=std::chrono::steady_clock::now();
  printf("exp %.2f ns  sincos %.2f ns  sqrt+div %.2f ns\n",std::chrono::duration<double,std::nano>(t1-t0).count()/6e7,
    std::chrono::duration<double,std::nano>(t2-t1).count()/3e7,std::chrono::duration<double,std::nano>(t3-t2).count()/3e7);
}
