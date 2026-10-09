// Lossless cached-bank decoding only: never enumerate or prune candidates.
#include <cmath>
#include <cstdint>
#include <cstring>
#include <algorithm>
struct P {double x,y;};
static P add(P a,P b){return {a.x+b.x,a.y+b.y};}
static P mul(P a,double b){return {a.x*b,a.y*b};}
static P sub(P a,P b){return {a.x-b.x,a.y-b.y};}
static P direction(P a){double r=std::hypot(a.x,a.y);return r>0?mul(a,1/r):P{1,0};}
static uint32_t bits(float x){uint32_t v;std::memcpy(&v,&x,4);return v;}
static float floating(uint32_t v){float x;std::memcpy(&x,&v,4);return x;}
static uint64_t bits64(double x){uint64_t v;std::memcpy(&v,&x,8);return v;}
static double floating64(uint64_t v){double x;std::memcpy(&x,&v,8);return x;}
static P position(const double* u){return {u[3],u[4]};}
static bool image(int t,int previous){return t==23&&(previous==24||previous==21||previous==19||previous==20||previous==18||previous==22);}
struct Geometry {
 const double *own,*units,*near,*shift,*gun,*artcentre,*velocity;int nu;double w,h;
 P clip(P p,const double* u,bool body=false)const {double r=body?u[9]:0;return {std::min(w-r,std::max(r,p.x)),std::min(h-r,std::max(r,p.y))};}
 P raw(int t,int i,int source,int ordinal)const {
  const double* u=own+i*23;const double* e=units+std::clamp(source,0,nu-1)*23;P p=position(u),ep=position(e);
  if(t==24)return add(p,{shift[i*2],shift[i*2+1]});
  if(t==21)return add(p,mul(direction(sub(ep,p)),200));
  if(t==19||t==20){auto a=add(ep,mul(direction(sub(p,ep)),std::max(u[18],u[11]-12)));return t==19?a:add(a,{shift[i*2],shift[i*2+1]});}
  if(t==22){const double* v=velocity+i*4+(ordinal%4/2)*2;P d{v[0],v[1]};return add(p,ordinal%2?d:std::hypot(d.x,d.y)>0?mul(direction(d),200):P{0,0});}
  if(t==18){P g=position(gun+i*23),destination=e[1]==1?ep:P{artcentre[0],artcentre[1]};return clip(add(g,mul(direction(sub(destination,g)),60)),u);}
  return {0,0};
 }
 P predict(int head,int t,int i,int source,int ordinal)const {
  const double* u=own+i*23;const double* e=units+std::clamp(source,0,nu-1)*23;P p=position(u),ep=position(e),delta=sub(p,ep);
  if(head==0){if(t!=0&&t!=1)return {0,0};if(source<0)return clip(add(p,{u[18],0}),u);double r=std::hypot(delta.x,delta.y);return clip(add(p,mul(direction(sub(ep,p)),std::min(u[11],std::max(u[18],r)))),u);}
  if(t==24||t==21||t==19||t==20||t==18||t==22)return clip(raw(t,i,source,ordinal),u);
  if(t==25){const double* ne=near+i*23;double lo=u[2]==2?u[18]:0,hi=u[2]==2?u[11]:u[11]+u[9]+ne[9];double r=ordinal<64?200:ordinal<128?hi:lo;P anchor=ordinal<64?p:position(ne);double a=(ordinal%64)*3.14159265358979323846/32;return clip(add(anchor,mul({std::cos(a),std::sin(a)},r)),u);}
  if(t==4)return p;
  if(t==5||t==7||t==23){double lo=t==23?(u[2]==2?u[18]:0):u[18];double hi=t==23?(u[2]==2?u[11]:u[11]+u[9]+e[9]):u[11];double r=t==7?u[18]:std::min(hi,std::max(lo,std::hypot(delta.x,delta.y)));return clip(add(ep,mul(direction(delta),r)),u,true);}
  if(t==6){P centre{};/* caller supplies enemy centre in a separate entry */return {0,0};}
  if(t==8){P d=direction(delta),side{-d.y,d.x};double a=3.14159265358979323846/4;return clip(add(ep,mul(add(mul(d,std::cos(a)),mul(side,(ordinal%2?1.:-1.)*std::sin(a))),(u[18]+u[11])/2)),u,true);}
  if(t==9)return clip(add(p,mul(direction(delta),std::max(60.,u[10]*.5))),u,true);
  return {0,0};
 }
 P predict_image(int t,int i,int source,int ordinal,P prior)const {
  const double* u=own+i*23;const double* ne=near+i*23;P origin=position(ne);
  if(t!=18)prior=raw(t,i,source,ordinal);
  auto delta=sub(prior,origin);double r=std::hypot(delta.x,delta.y);auto d=direction(r>0?delta:sub(position(u),origin));
  double lo=u[2]==2?u[18]:0,hi=u[2]==2?u[11]:u[11]+u[9]+ne[9];return clip(add(origin,mul(d,std::min(hi,std::max(lo,r)))),u,true);
 }
};
extern "C" void codec_bank(int expand,int head,int n,int cap,int nu,double w,double h,
 const double* own,const double* units,const double* near,const double* shift,const double* gun,const double* artcentre,const double* centre,const double* velocity,const double* threat,
 const int8_t* types,const int16_t* sources,const uint8_t* valid,const double* actual,const uint64_t* point_bits,const uint32_t* numeric_bits,
 double* points,float* numeric){
 Geometry g{own,units,near,shift,gun,artcentre,velocity,nu,w,h};
 int ne=0;for(int j=0;j<nu;++j)ne+=units[j*23+1]==1;
 for(int i=0;i<n;++i){int ordinal[1280]={},r22=0,r25=0,r8=0;
  for(int j=0;j<cap;++j){int at=i*cap+j,t=types[at];if(t==8)ordinal[j]=r8++;if(t==22)ordinal[j]=r22++;if(t==25)ordinal[j]=r25++;
   if(head==1&&image(t,j?types[at-1]:-1))continue;
   P p=valid[at]?g.predict(head,t,i,sources[at],ordinal[j]):P{0,0};
   if(valid[at]&&head==1&&t==6){const double* u=own+i*23;const double* e=units+std::clamp(int(sources[at]),0,nu-1)*23;P ep=position(e);p=g.clip(add(ep,mul(direction(sub(ep,{centre[0],centre[1]})),e[9]+u[9]+12)),u,true);}
   points[at*2]=expand?floating64(bits64(p.x)+point_bits[at*2]):p.x;points[at*2+1]=expand?floating64(bits64(p.y)+point_bits[at*2+1]):p.y;
  }
  for(int j=1;j<cap;++j){int at=i*cap+j;if(head!=1||!image(types[at],types[at-1]))continue;
   const double* reference=expand?points:actual;P prior{reference[(at-1)*2],reference[(at-1)*2+1]};
   P p=valid[at]?g.predict_image(types[at-1],i,sources[at-1],ordinal[j-1],prior):P{0,0};
   points[at*2]=expand?floating64(bits64(p.x)+point_bits[at*2]):p.x;points[at*2+1]=expand?floating64(bits64(p.y)+point_bits[at*2+1]):p.y;
  }
  for(int j=0;j<cap;++j){int at=i*cap+j;const double* reference=expand?points:actual;double dx=reference[at*2]-own[i*23+3],dy=reference[at*2+1]-own[i*23+4];
   float prediction[7]={valid[at]?float(dx/100):0,valid[at]?float(dy/100):0,valid[at]?float(std::hypot(dx,dy)/100):0,0,0,0,0};
   
   for(int k=0;k<7;++k)numeric[at*7+k]=expand?floating(bits(prediction[k])+numeric_bits[at*7+k]):prediction[k];
  }
  // Four independent candidate points; SIMD changes no reduction order.
  using V=double __attribute__((vector_size(32)));
  const double* reference=expand?points:actual;
  for(int j=0;j<cap;j+=4){bool any=false;V x{},y{},field{};
   for(int k=0;k<4;++k)if(j+k<cap){int at=i*cap+j+k;any=any||valid[at];x[k]=reference[at*2];y[k]=reference[at*2+1];}
   if(any)for(int e=0;e<ne;++e){const double* a=threat+e*4;V dx=x-a[0],dy=y-a[1];field+=a[2]/(1+(dx*dx+dy*dy)*a[3]);}
   for(int k=0;k<4&&j+k<cap;++k){int at=i*cap+j+k;float f=valid[at]?float(field[k]):0;numeric[at*7+4]=expand?floating(bits(f)+numeric_bits[at*7+4]):f;}
  }
 }
}
template<class U> static void decode(const unsigned char* input,U* output,const U* previous,const U* older,int64_t n,int mode){
 for(int64_t i=0;i<n;++i){U v=0;for(unsigned b=0;b<sizeof(U);++b)v|=U(input[b*n+i])<<(b*8);
  if(mode){U d=(v>>1)^U(0-U(v&1));v=mode==1?U(d+previous[i]):U(d+U(2*previous[i])-older[i]);}output[i]=v;
 }
}
extern "C" void codec_plane(const unsigned char* input,void* output,const void* previous,const void* older,int64_t n,int width,int mode){
 if(width==1)decode(input,(uint8_t*)output,(const uint8_t*)previous,(const uint8_t*)older,n,mode);
 if(width==2)decode(input,(uint16_t*)output,(const uint16_t*)previous,(const uint16_t*)older,n,mode);
 if(width==4)decode(input,(uint32_t*)output,(const uint32_t*)previous,(const uint32_t*)older,n,mode);
 if(width==8)decode(input,(uint64_t*)output,(const uint64_t*)previous,(const uint64_t*)older,n,mode);
}

extern "C" int codec_mapping(const int16_t* members,int16_t* mapping,int n,int cap,int families){
 std::fill(mapping,mapping+int64_t(n)*cap*2,int16_t(-1));
 for(int i=0;i<n;++i)for(int f=0;f<families;++f)for(int m=0;m<64;++m){int j=members[(i*families+f)*64+m];if(j>=cap)return 1;if(j>=0){int at=(i*cap+j)*2;mapping[at]=f;mapping[at+1]=m;}}
 return 0;
}
