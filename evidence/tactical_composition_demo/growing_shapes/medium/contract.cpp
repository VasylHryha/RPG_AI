#include "medium_c.h"
#include <cmath>
#include <cstring>
#include <iostream>
#include <stdexcept>
#include <vector>
static void expect(bool condition,const char* message){if(!condition)throw std::runtime_error(message);}
int main(){try{
    gm_params p{1,1,.8,1,1e-6,3,1,8,1,16,2};
    void* h=gm_create(17,&p);expect(h,"create");uint64_t a=0,b=0;
    expect(gm_add(h,0,0,0,0,&a)==0 && gm_add(h,1,0,0,0,&b)==0,"add");
    expect(a==1 && b==2,"stable ids");
    int32_t idx[2];double mask[2],inv[2],rhs[6];
    expect(gm_neighbors(h,idx,mask,inv,2)==0 && idx[0]==1 && idx[1]==0 && mask[0]==1 && inv[0]==1,"neighbors");
    expect(gm_rhs(h,rhs,6)==0 && std::abs(rhs[0]-.8)<1e-15 && rhs[2]==0,"law");
    expect(gm_rhs(h,rhs,1)==-1 && std::strlen(gm_error(h))>0,"buffer error");
    expect(gm_rhs(h,rhs,6)==0,"error recovery");
    void* branch=gm_clone(h);expect(branch,"clone");
    expect(gm_remove(branch,a)==0 && gm_count(branch)==1 && gm_count(h)==2,"clone isolation");
    uint64_t c=0;expect(gm_add(branch,0,0,0,0,&c)==0 && c>b,"id not reused");
    expect(gm_silence(h,a,1)==0,"silence");
    expect(gm_rhs(h,rhs,6)==0 && rhs[0]==0 && rhs[2]==0 && rhs[3]==0,"silence drops both directions");
    expect(gm_silence(h,a,0)==0 && gm_step(h,.02)==0,"restore/step");
    size_t size=gm_save(h,nullptr,0);std::vector<char> bytes(size);
    expect(size>0 && gm_save(h,bytes.data(),size)==size,"save");
    void* restored=gm_load(bytes.data(),size);expect(restored,"load");
    expect(gm_load(bytes.data(),size-1)==nullptr,"truncated snapshot");
    expect(gm_step(restored,.02)==0 && gm_step(h,.02)==0,"continued step");
    size=gm_save(h,nullptr,0);std::vector<char> one(size),two(size);
    expect(gm_save(h,one.data(),size)==size && gm_save(restored,two.data(),size)==size && one==two,"exact continuation");
    gm_destroy(branch);gm_destroy(restored);gm_destroy(h);
    expect(gm_create(0,nullptr)==nullptr && gm_step(nullptr,.1)==-1,"null C boundary");
    p.eps=0;expect(gm_create(0,&p)==nullptr,"invalid params");
    std::cout<<"C++ C API contract: PASS\n";return 0;
}catch(const std::exception& e){std::cerr<<"C++ C API contract: FAIL: "<<e.what()<<'\n';return 1;}}
