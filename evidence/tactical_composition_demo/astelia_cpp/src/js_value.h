// Narrow ECMAScript value semantics used by the frozen formation simulation.
// Native C++ execution: no JavaScript engine, subprocess, or external library.
#pragma once
#include <algorithm>
#include <array>
#include <charconv>
#include <cmath>
#include <cstdint>
#include <cstring>
#include <cstdlib>
#include <functional>
#include <iomanip>
#include <iostream>
#include <limits>
#include <memory>
#include <sstream>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <vector>

namespace js {
struct Object;
inline std::unordered_set<std::string> strings;
inline const std::string* intern(std::string s){return &*strings.insert(std::move(s)).first;}
struct V {
  enum Tag { Undefined, Null, Number, Boolean, String, Heap } tag = Undefined;
  union { double n=0; Object* p; const std::string* text; };
  const std::string& string() const {return *text;}
  V() = default;
  V(std::nullptr_t):tag(Null){}
  V(double x):tag(Number),n(x){}
  V(int x):V(double(x)){}
  V(bool x):tag(Boolean),n(x){}
  V(const char* x):tag(String),text(intern(x)){}
  V(std::string x):tag(String),text(intern(std::move(x))){}
  explicit V(Object* x):tag(Heap),p(x){}
};
using Args = std::vector<V>;
struct CallArgs {
  const V* data;size_t length;
  CallArgs(std::initializer_list<V> xs):data(xs.begin()),length(xs.size()){}
  CallArgs(const Args& xs):data(xs.data()),length(xs.size()){}
  CallArgs(const V* xs,size_t n):data(xs),length(n){}
  const V* begin()const{return data;}const V* end()const{return data+length;}
  size_t size()const{return length;}bool empty()const{return length==0;}
  const V& operator[](size_t i)const{return data[i];}
};
using Fn = std::function<V(const CallArgs&)>;
inline const std::vector<std::string> hotNames={"x","y","hp","cd","target","alive","id","team","role","w","r","speed","range","dmg","cdMax","vx","vy","svx","svy","units","o","ai","skills","packs","t","dec","move","slotX","slotY","state","prep","formation"};
inline const std::unordered_map<std::string,int> hotLookup=[](){std::unordered_map<std::string,int> out;for(size_t i=0;i<hotNames.size();++i)out.emplace(hotNames[i],int(i));return out;}();
struct Object {
  enum Kind { Plain, Array, Map, Set, Function } kind;
  std::vector<std::pair<std::string,V>> props;
  std::unordered_map<std::string,size_t> index;
  Args items;
  std::vector<std::pair<V,V>> entries;
  Fn fn;
  std::vector<V*> captured;
  std::array<int,32> hot;
  explicit Object(Kind k):kind(k){hot.fill(-1);}
};
inline std::vector<std::unique_ptr<Object>> arena;
inline std::vector<std::unique_ptr<V>> cells;
inline V heap(Object::Kind kind) { arena.emplace_back(new Object(kind)); return V(arena.back().get()); }
inline V arr(Args a={}) { auto v=heap(Object::Array);v.p->items=std::move(a);return v; }
inline V fn(Fn f) { auto v=heap(Object::Function);v.p->fn=std::move(f);return v; }
inline V arg(const Args& a,size_t i) { return i<a.size()?a[i]:V(); }
inline V arg(std::initializer_list<V> a,size_t i) {return i<a.size()?*(a.begin()+i):V();}
inline V arg(const CallArgs& a,size_t i){return i<a.length?a.data[i]:V();}
struct Var {
  V* p;
  explicit Var(V v=V()) { cells.emplace_back(new V(std::move(v)));p=cells.back().get(); }
  V val() const { return *p; }
  V set(V v) const { return *p=std::move(v); }
};
inline V fn(Fn f,std::vector<Var> captures) {V v=fn(std::move(f));for(auto c:captures)v.p->captured.push_back(c.p);return v;}
inline bool truth(const V& v) {
  switch(v.tag) { case V::Undefined:case V::Null:return false;case V::Boolean:return v.n;
    case V::Number:return v.n!=0&&!std::isnan(v.n);case V::String:return !v.string().empty();default:return true; }
}
inline bool nullish(const V& v) {return v.tag==V::Undefined||v.tag==V::Null;}
inline std::string str(const V& v);
inline void utf8(std::string& out,uint32_t cp){if(cp<128)out+=char(cp);else if(cp<2048){out+=char(192|(cp>>6));out+=char(128|(cp&63));}else if(cp<65536){out+=char(224|(cp>>12));out+=char(128|((cp>>6)&63));out+=char(128|(cp&63));}else{out+=char(240|(cp>>18));out+=char(128|((cp>>12)&63));out+=char(128|((cp>>6)&63));out+=char(128|(cp&63));}}
inline std::vector<uint16_t> utf16(const std::string& text){std::vector<uint16_t> out;for(size_t i=0;i<text.size();){uint32_t cp=static_cast<unsigned char>(text[i++]);int n=cp<128?0:cp<224?1:cp<240?2:3;if(n)cp&=(1u<<(6-n))-1;for(int j=0;j<n&&i<text.size();++j)cp=(cp<<6)|(static_cast<unsigned char>(text[i++])&63);if(cp>=65536){cp-=65536;out.push_back(uint16_t(0xd800+(cp>>10)));out.push_back(uint16_t(0xdc00+(cp&1023)));}else out.push_back(uint16_t(cp));}return out;}
inline std::string utf16String(const std::vector<uint16_t>& units,size_t first,size_t last){std::string out;for(size_t i=first;i<last;++i){uint32_t cp=units[i];if(cp>=0xd800&&cp<=0xdbff&&i+1<last&&units[i+1]>=0xdc00&&units[i+1]<=0xdfff){cp=0x10000+((cp-0xd800)<<10)+(units[++i]-0xdc00);}utf8(out,cp);}return out;}
inline bool space(uint16_t c){return (c>=9&&c<=13)||c==32||c==0xa0||c==0x1680||(c>=0x2000&&c<=0x200a)||c==0x2028||c==0x2029||c==0x202f||c==0x205f||c==0x3000||c==0xfeff;}
inline double stringNumber(const std::string& text){auto units=utf16(text);size_t first=0,last=units.size();while(first<last&&space(units[first]))++first;while(last>first&&space(units[last-1]))--last;if(first==last)return 0;std::string s;for(size_t i=first;i<last;++i){if(units[i]>127)return NAN;s+=char(units[i]);}
  if(s.size()>2&&s[0]=='0'&&(s[1]=='x'||s[1]=='X'||s[1]=='b'||s[1]=='B'||s[1]=='o'||s[1]=='O')){int base=s[1]=='x'||s[1]=='X'?16:s[1]=='b'||s[1]=='B'?2:8;double out=0;for(size_t i=2;i<s.size();++i){int d=s[i]>='0'&&s[i]<='9'?s[i]-'0':s[i]>='a'&&s[i]<='f'?s[i]-'a'+10:s[i]>='A'&&s[i]<='F'?s[i]-'A'+10:-1;if(d<0||d>=base)return NAN;out=out*base+d;}return out;}
  if(s=="Infinity"||s=="+Infinity")return INFINITY;if(s=="-Infinity")return -INFINITY;
  if(s.find_first_not_of("0123456789eE+-.")!=std::string::npos)return NAN;
  char* end;double d=std::strtod(s.c_str(),&end);return end==s.c_str()||*end?NAN:d;}
inline double num(const V& v) {
  switch(v.tag) {case V::Number:case V::Boolean:return v.n;case V::Null:return 0;case V::Undefined:return NAN;
    case V::String:return stringNumber(v.string());
    default:return num(V(str(v)));}
}
inline std::string numberString(double x) {
  if(std::isnan(x))return "NaN";if(std::isinf(x))return x<0?"-Infinity":"Infinity";if(x==0)return "0";
  char b[128];auto r=std::to_chars(b,b+128,x);std::string s(b,r.ptr);
  auto ep=s.find('e');
  if(ep!=std::string::npos) {
    int exp=std::stoi(s.substr(ep+1));std::string m=s.substr(0,ep);bool neg=m[0]=='-';if(neg)m.erase(0,1);
    auto dot=m.find('.');int pos=(dot==std::string::npos?int(m.size()):int(dot))+exp;if(dot!=std::string::npos)m.erase(dot,1);
    if(exp>=-6&&exp<21){if(pos<=0)m="0."+std::string(-pos,'0')+m;else if(pos>=int(m.size()))m+=std::string(pos-m.size(),'0');else m.insert(pos,".");return (neg?"-":"")+m;}
    return s.substr(0,ep)+"e"+(exp>=0?"+":"-")+std::to_string(std::abs(exp));
  }return s;
}
inline std::string str(const V& v) {
  switch(v.tag){case V::Undefined:return "undefined";case V::Null:return "null";case V::Boolean:return v.n?"true":"false";
    case V::Number:return numberString(v.n);case V::String:return v.string();default:
    if(v.p->kind==Object::Array){std::string s;for(size_t i=0;i<v.p->items.size();++i){if(i)s+=',';if(!nullish(v.p->items[i]))s+=str(v.p->items[i]);}return s;}
    return "[object Object]";}
}
inline uint32_t u32(const V& v){double x=num(v);if(!std::isfinite(x)||x==0)return 0;double y=std::fmod(std::trunc(x),4294967296.0);if(y<0)y+=4294967296.0;return uint32_t(y);}
inline int32_t i32(const V& v){uint32_t u=u32(v);return u<=INT32_MAX?int32_t(u):int32_t(int64_t(u)-4294967296LL);}
inline bool eq(const V& a,const V& b){if(a.tag!=b.tag)return false;switch(a.tag){case V::Undefined:case V::Null:return true;case V::String:return a.string()==b.string();case V::Heap:return a.p==b.p;default:return a.n==b.n;}}
inline bool same(const V& a,const V& b){return eq(a,b)||(a.tag==V::Number&&b.tag==V::Number&&std::isnan(a.n)&&std::isnan(b.n));}
inline bool indexKey(const std::string& s,uint32_t& n){if(s.empty()||s.size()>10||(s.size()>1&&s[0]=='0'))return false;uint64_t x=0;for(char c:s){if(c<'0'||c>'9')return false;x=x*10+c-'0';}if(x>=4294967295ULL)return false;n=x;return true;}
inline Args keys(V v){Args out;if(v.tag==V::String){for(size_t i=0;i<utf16(v.string()).size();++i)out.emplace_back(std::to_string(i));return out;}if(v.tag!=V::Heap)return out;
  if(v.p->kind==Object::Array)for(size_t i=0;i<v.p->items.size();++i)out.emplace_back(std::to_string(i));
  std::vector<std::pair<uint32_t,std::string>> ints;for(auto& kv:v.p->props){uint32_t i;if(indexKey(kv.first,i))ints.emplace_back(i,kv.first);}
  std::sort(ints.begin(),ints.end());for(auto& kv:ints)out.emplace_back(kv.second);for(auto& kv:v.p->props){uint32_t i;if(!indexKey(kv.first,i))out.emplace_back(kv.first);}return out;}
inline V prop(V v,const std::string& k){if(nullish(v))throw std::runtime_error("Cannot read properties of "+str(v)+" (reading '"+k+"')");
  if(v.tag==V::String){auto units=utf16(v.string());if(k=="length")return V(double(units.size()));uint32_t i;if(indexKey(k,i)){if(i>=units.size())return V();std::string out;utf8(out,units[i]);return V(out);}return V();}
  if(v.tag!=V::Heap)return V();uint32_t i;
  if(v.p->kind==Object::Array){if(k=="length")return V(double(v.p->items.size()));if(indexKey(k,i))return i<v.p->items.size()?v.p->items[i]:V();}
  if((v.p->kind==Object::Map||v.p->kind==Object::Set)&&k=="size")return V(double(v.p->entries.size()));
  auto it=v.p->index.find(k);return it==v.p->index.end()?V():v.p->props[it->second].second;}
inline V get(V v,V key){if(v.tag==V::Heap&&v.p->kind==Object::Array&&key.tag==V::Number&&key.n>=0&&key.n<4294967295.0&&std::floor(key.n)==key.n){size_t i=size_t(key.n);return i<v.p->items.size()?v.p->items[i]:V();}return prop(v,str(key));}
inline V hotProp(V v,int index){if(v.tag==V::Heap){int slot=v.p->hot[index];return slot<0?V():v.p->props[slot].second;}return prop(v,hotNames[index]);}
inline V get(std::initializer_list<V> a){return get(arg(a,0),arg(a,1));}
inline V set(V v,V key,V value){if(v.tag==V::Heap&&v.p->kind==Object::Array&&key.tag==V::Number&&key.n>=0&&key.n<4294967295.0&&std::floor(key.n)==key.n){size_t i=size_t(key.n);if(i>=v.p->items.size())v.p->items.resize(i+1);return v.p->items[i]=value;}std::string k=str(key);if(v.tag!=V::Heap)throw std::runtime_error("Cannot set properties of "+str(v));uint32_t i;
  if(v.p->kind==Object::Array){if(k=="length"){v.p->items.resize(u32(value));return value;}if(indexKey(k,i)){if(i>=v.p->items.size())v.p->items.resize(i+1);return v.p->items[i]=value;}}
  auto it=v.p->index.find(k);if(it==v.p->index.end()){v.p->index[k]=v.p->props.size();auto h=hotLookup.find(k);if(h!=hotLookup.end())v.p->hot[h->second]=v.p->props.size();v.p->props.emplace_back(k,value);}else v.p->props[it->second].second=value;return value;}
inline V hotSet(V v,int index,V value){if(v.tag==V::Heap){int slot=v.p->hot[index];if(slot>=0)return v.p->props[slot].second=value;}return set(v,V(hotNames[index]),value);}
inline V obj(std::vector<std::pair<V,V>> fields={}){V v=heap(Object::Plain);for(auto& kv:fields)set(v,kv.first,kv.second);return v;}
inline Args iter(V v){if(v.tag==V::String){Args a;auto units=utf16(v.string());for(size_t i=0;i<units.size();++i){size_t end=i+1;if(units[i]>=0xd800&&units[i]<=0xdbff&&end<units.size()&&units[end]>=0xdc00&&units[end]<=0xdfff)++end;a.emplace_back(utf16String(units,i,end));i=end-1;}return a;}if(v.tag!=V::Heap)throw std::runtime_error(str(v)+" is not iterable");
  if(v.p->kind==Object::Array)return v.p->items;Args a;if(v.p->kind==Object::Map)for(auto& kv:v.p->entries)a.push_back(arr({kv.first,kv.second}));else if(v.p->kind==Object::Set)for(auto& kv:v.p->entries)a.push_back(kv.first);else throw std::runtime_error("object is not iterable");return a;}
inline V call(V f,const CallArgs& a){if(f.tag!=V::Heap||f.p->kind!=Object::Function)throw std::runtime_error(str(f)+" is not a function");return f.p->fn(a);}
inline V call(const CallArgs& a){return call(arg(a,0),CallArgs(a.data+1,a.length-1));}
inline V bin(const std::string& op,std::initializer_list<V> a){V x=arg(a,0),y=arg(a,1);
  if(op=="===")return V(eq(x,y));if(op=="!==")return V(!eq(x,y));
  if(op=="+"&&(x.tag==V::String||y.tag==V::String))return V(str(x)+str(y));
  double l=num(x),r=num(y);
  if(op=="+"){if(x.tag==V::String||y.tag==V::String)return V(str(x)+str(y));return V(l+r);}if(op=="-")return V(l-r);if(op=="*")return V(l*r);if(op=="/")return V(l/r);if(op=="%")return V(std::fmod(l,r));if(op=="**")return V(std::pow(l,r));
  if(op=="===")return V(eq(x,y));if(op=="!==")return V(!eq(x,y));if(op=="==")return V(eq(x,y)||(nullish(x)&&nullish(y))||((x.tag!=V::Heap&&y.tag!=V::Heap)&&l==r));if(op=="!=")return V(!truth(bin("==",a)));
  if(op=="<")return V(x.tag==V::String&&y.tag==V::String?x.string()<y.string():l<r);if(op==">")return V(x.tag==V::String&&y.tag==V::String?x.string()>y.string():l>r);if(op=="<=")return V(x.tag==V::String&&y.tag==V::String?x.string()<=y.string():l<=r);if(op==">=")return V(x.tag==V::String&&y.tag==V::String?x.string()>=y.string():l>=r);
  if(op=="|")return V(double(i32(x)|i32(y)));if(op=="&")return V(double(i32(x)&i32(y)));if(op=="^")return V(double(i32(x)^i32(y)));
  if(op==">>>")return V(double(u32(x)>>(u32(y)&31)));if(op==">>")return V(double(i32(x)>>(u32(y)&31)));if(op=="<<"){uint32_t u=u32(x)<<(u32(y)&31);return V(double(i32(V(double(u)))));}
  throw std::runtime_error("unsupported operator "+op);}
inline V unary(const std::string& op,V v){if(op=="!")return V(!truth(v));if(op=="+")return V(num(v));if(op=="-")return V(-num(v));if(op=="~")return V(double(~i32(v)));if(op=="void")return V();if(op=="typeof"){switch(v.tag){case V::Undefined:return V("undefined");case V::Boolean:return V("boolean");case V::Number:return V("number");case V::String:return V("string");case V::Heap:if(v.p->kind==Object::Function)return V("function");default:return V("object");}}throw std::runtime_error("unsupported unary "+op);}
struct Local {mutable V v;V val()const{return v;}V set(V x)const{return v=x;}};
struct Ref {V* cell=nullptr;V base,key;int hot=-1;Ref(const Var& x):cell(x.p){}Ref(const Local& x):cell(&x.v){}Ref(V b,V k):base(b),key(k){}Ref(V b,int h):base(b),hot(h){}V val()const{return cell?*cell:hot>=0?hotProp(base,hot):get(base,key);}V put(V x)const{return cell?(*cell=x):hot>=0?hotSet(base,hot,x):set(base,key,x);}};
inline V update(Ref r,int delta,bool prefix){V old=V(num(r.val()));V v=r.put(V(old.n+delta));return prefix?v:old;}
inline void spread(Args& a,V v){Args b=iter(v);a.insert(a.end(),b.begin(),b.end());}
inline void assign(V target,V source){if(nullish(source))return;for(V k:keys(source))set(target,k,get(source,k));}
inline int relative(V v,int n,int fallback){if(v.tag==V::Undefined)return fallback;double x=num(v);if(std::isnan(x))x=0;if(x<0)return std::max(0,n+int(std::max(-double(n),std::trunc(x))));return int(std::min(double(n),std::trunc(x)));}
inline V fixed(double x,int digits){
  if(digits<0||digits>100)throw std::runtime_error("toFixed() digits argument must be between 0 and 100");
  if(!std::isfinite(x)||std::abs(x)>=1e21)return V(numberString(x));
  std::ostringstream out;out<<std::fixed<<std::setprecision(digits)<<(x==0?0.0:x);std::string text=out.str();
  // libc formats exact half ties to even. ECMAScript chooses the larger
  // magnitude. Detect a tie from the binary mantissa, without x*10^digits
  // (which would incorrectly turn values such as 2.675 into half ties).
  uint64_t bits;double magnitude=std::abs(x);std::memcpy(&bits,&magnitude,8);
  int exponent=int((bits>>52)&2047);uint64_t mantissa=bits&0xfffffffffffffULL;
  if(exponent)mantissa|=1ULL<<52;
  if(mantissa){int zeros=0;uint64_t odd=mantissa;while(!(odd&1)){++zeros;odd>>=1;}
    int binaryExponent=exponent?exponent-1023-52:-1074;
    if(binaryExponent+digits+zeros==-1&&(odd&3)==1){
      for(int i=int(text.size())-1;i>=0;--i){if(text[i]=='.'||text[i]=='-')continue;if(text[i]<'9'){++text[i];break;}text[i]='0';}
    }
  }return V(text);
}
inline V method(V v,const std::string& k,const CallArgs& a){
  V own=get(v,V(k));if(own.tag!=V::Undefined)return call(own,std::move(a));
  if(v.tag==V::Number&&k=="toFixed"){double d=a.empty()?0:num(a[0]);if(std::isnan(d))d=0;if(!std::isfinite(d)||std::trunc(d)<0||std::trunc(d)>100)throw std::runtime_error("toFixed() digits argument must be between 0 and 100");return fixed(v.n,int(d));}
  if(v.tag==V::String&&(k=="split"||k=="includes"||k=="indexOf")){
    auto units=utf16(v.string()),separator=utf16(str(arg(a,0)));Args out;
    if(k=="split"){
      uint32_t limit=a.size()<2||a[1].tag==V::Undefined?UINT32_MAX:u32(a[1]);if(!limit)return arr();
      if(a.empty()||a[0].tag==V::Undefined)return arr({v});
      if(separator.empty()){for(size_t i=0;i<units.size()&&out.size()<limit;++i)out.emplace_back(utf16String(units,i,i+1));return arr(out);}
      size_t start=0;while(out.size()<limit){auto hit=std::search(units.begin()+start,units.end(),separator.begin(),separator.end());if(hit==units.end())break;size_t pos=hit-units.begin();out.emplace_back(utf16String(units,start,pos));start=pos+separator.size();}
      if(out.size()<limit)out.emplace_back(utf16String(units,start,units.size()));return arr(out);
    }
    double raw=a.size()>1?num(a[1]):0;if(std::isnan(raw))raw=0;size_t start=size_t(std::max(0.0,std::min(double(units.size()),std::trunc(raw))));
    auto hit=std::search(units.begin()+start,units.end(),separator.begin(),separator.end());bool found=separator.empty()||hit!=units.end();
    return k=="includes"?V(found):V(found?int(hit-units.begin()):-1);
  }
  if(v.tag!=V::Heap)throw std::runtime_error(k+" is not a function");
  auto p=v.p;
  if(p->kind==Object::Map||p->kind==Object::Set){
    V key=arg(a,0);auto find=[&](){return std::find_if(p->entries.begin(),p->entries.end(),[&](auto& kv){return same(kv.first,key);});};
    if(k=="get"){auto i=find();return i==p->entries.end()?V():i->second;}
    if(k=="has")return V(find()!=p->entries.end());
    if(k=="set"||k=="add"){V val=k=="add"?key:arg(a,1);auto i=find();if(i==p->entries.end())p->entries.emplace_back(key,val);else i->second=val;return v;}
    if(k=="delete"){auto i=find();bool yes=i!=p->entries.end();if(yes)p->entries.erase(i);return V(yes);}
    if(k=="keys"||k=="values"){Args out;for(auto& kv:p->entries)out.push_back(k=="keys"?kv.first:kv.second);return arr(out);}
    if(k=="entries"){Args out;for(auto& kv:p->entries)out.push_back(arr({kv.first,kv.second}));return arr(out);}
  }
  if(p->kind==Object::Array){
    auto& xs=p->items;int n=xs.size();
    if(k=="push"){xs.insert(xs.end(),a.begin(),a.end());return V(double(xs.size()));}
    if(k=="unshift"){xs.insert(xs.begin(),a.begin(),a.end());return V(double(xs.size()));}
    if(k=="shift"){if(xs.empty())return V();V r=xs.front();xs.erase(xs.begin());return r;}
    if(k=="slice"){int start=relative(arg(a,0),n,0),end=relative(arg(a,1),n,n);return arr(Args(xs.begin()+start,xs.begin()+std::max(start,end)));}
    if(k=="splice"){int start=relative(arg(a,0),n,0),count=a.size()<2?n-start:int(std::min(double(n-start),std::max(0.0,num(a[1]))));Args out(xs.begin()+start,xs.begin()+start+count);xs.erase(xs.begin()+start,xs.begin()+start+count);if(a.size()>2)xs.insert(xs.begin()+start,a.begin()+2,a.end());return arr(out);}
    if(k=="concat"){Args out=xs;for(V x:a){if(x.tag==V::Heap&&x.p->kind==Object::Array)spread(out,x);else out.push_back(x);}return arr(out);}
    if(k=="includes"||k=="indexOf"){for(int i=0;i<n;++i)if(k=="includes"?same(xs[i],arg(a,0)):eq(xs[i],arg(a,0)))return k=="includes"?V(true):V(i);return k=="includes"?V(false):V(-1);}
    if(k=="join"){std::string sep=a.empty()?",":str(a[0]),out;for(int i=0;i<n;++i){if(i)out+=sep;if(!nullish(xs[i]))out+=str(xs[i]);}return V(out);}
    if(k=="sort"){std::stable_sort(xs.begin(),xs.end(),[&](const V& x,const V& y){if(a.empty())return str(x)<str(y);return num(call(a[0],{x,y}))<0;});return v;}
    if(k=="reduce"){V acc;int i=0;if(a.size()>1)acc=a[1];else{if(!n)throw std::runtime_error("Reduce of empty array with no initial value");acc=xs[i++];}for(;i<n;++i)acc=call(a[0],{acc,xs[i],V(i),v});return acc;}
    if(k=="map"||k=="filter"||k=="some"||k=="every"||k=="find"||k=="findIndex"||k=="forEach"){
      Args out;for(int i=0;i<n;++i){V x=xs[i];V r=call(a[0],{x,V(i),v});bool ok=truth(r);if(k=="map")out.push_back(r);else if(k=="filter"){if(ok)out.push_back(x);}else if(k=="some"&&ok)return V(true);else if(k=="every"&&!ok)return V(false);else if(k=="find"&&ok)return x;else if(k=="findIndex"&&ok)return V(i);}
      if(k=="some")return V(false);if(k=="every")return V(true);if(k=="findIndex")return V(-1);if(k=="find"||k=="forEach")return V();return arr(out);
    }
  }throw std::runtime_error("unsupported method "+k);
}
inline V method(const CallArgs& a){return method(a[0],str(a[1]),CallArgs(a.data+2,a.length-2));}
inline V construct(const std::string& name,const CallArgs& a){if(name=="Float64Array")return arr(Args(size_t(num(arg(a,0))),V(0.0)));if(name=="Map"||name=="Set"){V v=heap(name=="Map"?Object::Map:Object::Set);if(!a.empty()&&!nullish(a[0]))for(V x:iter(a[0])){if(name=="Map")method(v,"set",{get(x,0),get(x,1)});else method(v,"add",{x});}return v;}throw std::runtime_error("unsupported constructor "+name);}
inline std::string quote(const std::string& s){std::string out="\"";const char* hex="0123456789abcdef";for(size_t i=0;i<s.size();++i){unsigned char c=s[i];if(c==0xed&&i+2<s.size()&&(static_cast<unsigned char>(s[i+1])&0xe0)==0xa0){uint16_t cp=uint16_t(((c&15)<<12)|((static_cast<unsigned char>(s[i+1])&63)<<6)|(static_cast<unsigned char>(s[i+2])&63));out+="\\u";for(int k=12;k>=0;k-=4)out+=hex[(cp>>k)&15];i+=2;}
    else if(c=='"'||c=='\\'){out+='\\';out+=char(c);}else if(c=='\n')out+="\\n";else if(c=='\r')out+="\\r";else if(c=='\t')out+="\\t";else if(c<32){out+="\\u00";out+=hex[c>>4];out+=hex[c&15];}else out+=char(c);}return out+'"';}
inline std::string stringify(V v){switch(v.tag){case V::Undefined:return "undefined";case V::Null:return "null";case V::Boolean:return v.n?"true":"false";case V::Number:return std::isfinite(v.n)?numberString(v.n):"null";case V::String:return quote(v.string());default:
  if(v.p->kind==Object::Function)return "undefined";
  if(v.p->kind==Object::Array){std::string s="[";for(V x:v.p->items){if(s.size()>1)s+=',';std::string t=stringify(x);s+=t=="undefined"?"null":t;}return s+"]";}
  std::string s="{";for(V k:keys(v)){std::string t=stringify(get(v,k));if(t=="undefined")continue;if(s.size()>1)s+=',';s+=quote(str(k))+":"+t;}return s+"}";}}
struct Parser {
  const std::string& s;size_t i=0;
  void ws(){while(i<s.size()&&std::isspace(static_cast<unsigned char>(s[i])))++i;}
  char peek(){ws();return i<s.size()?s[i]:'\0';}
  void expect(char c){if(peek()!=c)throw std::runtime_error("invalid JSON");++i;}
  std::string string(){expect('"');std::string out;while(i<s.size()){char c=s[i++];if(c=='"')return out;if(c!='\\'){out+=c;continue;}if(i==s.size())break;c=s[i++];switch(c){case 'n':out+='\n';break;case 'r':out+='\r';break;case 't':out+='\t';break;case 'b':out+='\b';break;case 'f':out+='\f';break;case 'u':{if(i+4>s.size())throw std::runtime_error("invalid JSON escape");unsigned cp=std::stoul(s.substr(i,4),nullptr,16);i+=4;if(cp>=0xd800&&cp<=0xdbff&&i+6<=s.size()&&s.compare(i,2,"\\u")==0){unsigned low=std::stoul(s.substr(i+2,4),nullptr,16);if(low>=0xdc00&&low<=0xdfff){cp=0x10000+((cp-0xd800)<<10)+(low-0xdc00);i+=6;}}utf8(out,cp);break;}default:out+=c;}}
    throw std::runtime_error("unterminated JSON string");}
  V value(){char c=peek();if(c=='"')return V(string());if(c=='{'){++i;V v=obj();if(peek()=='}'){++i;return v;}do{V k=V(string());expect(':');set(v,k,value());if(peek()=='}'){++i;return v;}expect(',');}while(true);}
    if(c=='['){++i;Args a;if(peek()==']'){++i;return arr(a);}do{a.push_back(value());if(peek()==']'){++i;return arr(a);}expect(',');}while(true);}
    if(s.compare(i,4,"null")==0){i+=4;return V(nullptr);}if(s.compare(i,4,"true")==0){i+=4;return V(true);}if(s.compare(i,5,"false")==0){i+=5;return V(false);}
    char* end;double x=std::strtod(s.c_str()+i,&end);if(end==s.c_str()+i)throw std::runtime_error("invalid JSON number");i=end-s.c_str();return V(x);}
};
inline V parse(const std::string& s){Parser p{s};V v=p.value();if(p.peek())throw std::runtime_error("trailing JSON input");return v;}
// Collect only at host frame boundaries, where every live root is supplied.
inline void collect(Args roots,size_t permanentCells){
  std::unordered_set<Object*> objects;
  std::unordered_set<V*> liveCells;
  std::unordered_set<const std::string*> liveStrings;
  for(size_t i=0;i<permanentCells;++i){liveCells.insert(cells[i].get());roots.push_back(*cells[i]);}
  while(!roots.empty()){
    V v=std::move(roots.back());roots.pop_back();
    if(v.tag==V::String){liveStrings.insert(v.text);continue;}
    if(v.tag!=V::Heap||!objects.insert(v.p).second)continue;
    for(auto& p:v.p->props)roots.push_back(p.second);
    for(auto& x:v.p->items)roots.push_back(x);
    for(auto& p:v.p->entries){roots.push_back(p.first);roots.push_back(p.second);}
    for(V* c:v.p->captured)if(liveCells.insert(c).second)roots.push_back(*c);
  }
  arena.erase(std::remove_if(arena.begin(),arena.end(),[&](auto& p){return !objects.count(p.get());}),arena.end());
  for(auto it=strings.begin();it!=strings.end();)if(!liveStrings.count(&*it))it=strings.erase(it);else ++it;
  auto first=cells.begin()+permanentCells;
  cells.erase(std::remove_if(first,cells.end(),[&](auto& p){return !liveCells.count(p.get());}),cells.end());
}
struct Finally {std::function<void()> f;~Finally(){f();}};
} // namespace js
