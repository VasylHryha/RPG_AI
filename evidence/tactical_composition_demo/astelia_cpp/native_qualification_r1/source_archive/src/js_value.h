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
  bool gcMarked=false;
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
struct ValueHash {size_t operator()(const V&)const;};
struct ValueEqual {bool operator()(const V&,const V&)const;};
using OrderedIndex=std::unordered_map<V,size_t,ValueHash,ValueEqual>;
inline const std::vector<std::string> hotNames={"x","y","hp","cd","target","alive","id","team","role","w","r","speed","range","dmg","cdMax","vx","vy","svx","svy","units","o","ai","skills","packs","t","dec","move","slotX","slotY","state","prep","formation"};
inline const std::unordered_map<std::string,int> hotLookup=[](){std::unordered_map<std::string,int> out;for(size_t i=0;i<hotNames.size();++i)out.emplace(hotNames[i],int(i));return out;}();
// Immutable property layouts are shared across objects with the same insertion
// history. Values and enumeration order remain owned by each object.
struct Shape {
  std::vector<std::string> keys;
  std::array<int,32> hot;
  Shape(){hot.fill(-1);}
  std::array<std::vector<int>,2> named;
  std::unordered_map<std::string,size_t> index;
  std::unordered_map<std::string,Shape*> next;
};
inline Shape emptyShape;
inline std::vector<std::unique_ptr<Shape>> shapes;
inline Shape* appendShape(Shape* parent,const std::string& key){
  auto hit=parent->next.find(key);if(hit!=parent->next.end())return hit->second;
  auto shape=std::make_unique<Shape>();shape->index=parent->index;shape->keys=parent->keys;shape->hot=parent->hot;
  shape->keys.push_back(key);auto hot=hotLookup.find(key);if(hot!=hotLookup.end())shape->hot[hot->second]=int(parent->keys.size());
  shape->index.emplace(key,parent->index.size());Shape* result=shape.get();
  shapes.push_back(std::move(shape));parent->next.emplace(key,result);return result;
}
struct FunctionData {Fn fn;std::vector<V*> captured;Args capturedValues;};
struct OrderedData {std::vector<std::pair<V,V>> entries;OrderedIndex entryIndex;};
// Compact value storage: keys and offsets belong to the shared Shape, while
// callable and ordered-collection payloads exist only for their respective kinds.
struct Object {
  enum Kind { Plain, Array, Map, Set, Function } kind;
  Args props;
  Shape* shape=&emptyShape;
  bool marked=false;
  Args items;
  std::unique_ptr<OrderedData> ordered;
  std::unique_ptr<FunctionData> function;
  explicit Object(Kind k):kind(k){if(k==Map||k==Set)ordered=std::make_unique<OrderedData>();if(k==Function)function=std::make_unique<FunctionData>();}
};
inline std::vector<std::unique_ptr<Object>> arena;
inline std::vector<std::unique_ptr<V>> cells;
inline std::array<std::vector<std::unique_ptr<Object>>,5> spareObjects;
inline std::vector<std::unique_ptr<V>> spareCells;
inline V heap(Object::Kind kind) {
  auto& spare=spareObjects[size_t(kind)];
  if(spare.empty())arena.emplace_back(new Object(kind));
  else {arena.push_back(std::move(spare.back()));spare.pop_back();}
  return V(arena.back().get());
}
inline V arr(Args a={}) { auto v=heap(Object::Array);v.p->items=std::move(a);return v; }
inline V fn(Fn f) { auto v=heap(Object::Function);v.p->function->fn=std::move(f);return v; }
inline V arg(const Args& a,size_t i) { return i<a.size()?a[i]:V(); }
inline V arg(std::initializer_list<V> a,size_t i) {return i<a.size()?*(a.begin()+i):V();}
inline V arg(const CallArgs& a,size_t i){return i<a.length?a.data[i]:V();}
struct Var {
  mutable V value;mutable V* p=nullptr;
  explicit Var(V v=V()):value(v){}
  // Only an escaping capture needs a shared cell. Immediate native callbacks
  // operate on the original stack value, with no allocation or pointer chain.
  void promote()const{if(p)return;if(spareCells.empty())cells.emplace_back(new V(value));else{cells.push_back(std::move(spareCells.back()));spareCells.pop_back();*cells.back()=value;}p=cells.back().get();}
  Var(const Var& other){other.promote();p=other.p;}
  V* address()const{return p?p:&value;}
  V val()const{return *address();}
  V set(V v)const{return *address()=v;}
};
inline V fn(Fn f,std::vector<Var> captures) {V v=fn(std::move(f));for(auto c:captures)v.p->function->captured.push_back(c.p);return v;}
inline V fnValues(Fn f,Args roots){V v=fn(std::move(f));v.p->function->capturedValues=std::move(roots);return v;}
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
[[gnu::noinline]] inline double numSlow(const V& v);
inline double num(const V& v){if(v.tag==V::Number||v.tag==V::Boolean)return v.n;return numSlow(v);}
[[gnu::noinline]] inline double numSlow(const V& v) {
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
inline bool ValueEqual::operator()(const V& a,const V& b)const{return same(a,b);}
inline size_t ValueHash::operator()(const V& v)const{
  size_t h=0;switch(v.tag){case V::Number:h=std::isnan(v.n)?0x7ff80000u:std::hash<double>{}(v.n==0?0.0:v.n);break;case V::Boolean:h=size_t(v.n);break;case V::String:h=std::hash<std::string>{}(v.string());break;case V::Heap:h=std::hash<void*>{}(v.p);break;default:break;}
  return h^(size_t(v.tag)*0x9e3779b97f4a7c15ULL);
}
inline bool indexKey(const std::string& s,uint32_t& n){if(s.empty()||s.size()>10||(s.size()>1&&s[0]=='0'))return false;uint64_t x=0;for(char c:s){if(c<'0'||c>'9')return false;x=x*10+c-'0';}if(x>=4294967295ULL)return false;n=x;return true;}
inline Args keys(V v){Args out;if(v.tag==V::String){for(size_t i=0;i<utf16(v.string()).size();++i)out.emplace_back(std::to_string(i));return out;}if(v.tag!=V::Heap)return out;
  if(v.p->kind==Object::Array)for(size_t i=0;i<v.p->items.size();++i)out.emplace_back(std::to_string(i));
  std::vector<std::pair<uint32_t,std::string>> ints;for(auto& key:v.p->shape->keys){uint32_t i;if(indexKey(key,i))ints.emplace_back(i,key);}
  std::sort(ints.begin(),ints.end());for(auto& kv:ints)out.emplace_back(kv.second);for(auto& key:v.p->shape->keys){uint32_t i;if(!indexKey(key,i))out.emplace_back(key);}return out;}
inline V prop(V v,const std::string& k){if(nullish(v))throw std::runtime_error("Cannot read properties of "+str(v)+" (reading '"+k+"')");
  if(v.tag==V::String){auto units=utf16(v.string());if(k=="length")return V(double(units.size()));uint32_t i;if(indexKey(k,i)){if(i>=units.size())return V();std::string out;utf8(out,units[i]);return V(out);}return V();}
  if(v.tag!=V::Heap)return V();uint32_t i;
  if(v.p->kind==Object::Array){if(k=="length")return V(double(v.p->items.size()));if(indexKey(k,i))return i<v.p->items.size()?v.p->items[i]:V();}
  if((v.p->kind==Object::Map||v.p->kind==Object::Set)&&k=="size")return V(double(v.p->ordered->entries.size()));
  auto it=v.p->shape->index.find(k);return it==v.p->shape->index.end()?V():v.p->props[it->second];}
inline int namedSlot(Shape* shape,size_t field,unsigned family,const std::string& key){
  auto& named=shape->named[family];if(named.size()<=field)named.resize(field+1,-2);
  int& slot=named[field];if(slot==-2){auto hit=shape->index.find(key);slot=hit==shape->index.end()?-1:int(hit->second);}return slot;
}
inline V propCached(V v,const std::string& key,size_t field,unsigned family=0){
  if(v.tag==V::Heap&&(v.p->kind==Object::Plain||v.p->kind==Object::Function)){int slot=namedSlot(v.p->shape,field,family,key);return slot<0?V():v.p->props[size_t(slot)];}
  return prop(v,key);
}
template<size_t Field,unsigned Family=0> inline V propKnown(V v,const std::string& key){return propCached(v,key,Field,Family);}
inline V get(V v,V key){if(v.tag==V::Heap&&v.p->kind==Object::Array&&key.tag==V::Number&&key.n>=0&&key.n<4294967295.0&&std::floor(key.n)==key.n){size_t i=size_t(key.n);return i<v.p->items.size()?v.p->items[i]:V();}return prop(v,str(key));}
inline V hotProp(V v,int index){if(v.tag==V::Heap){int slot=v.p->shape->hot[index];return slot<0?V():v.p->props[slot];}return prop(v,hotNames[index]);}
inline V get(std::initializer_list<V> a){return get(arg(a,0),arg(a,1));}
inline V set(V v,V key,V value){if(v.tag==V::Heap&&v.p->kind==Object::Array&&key.tag==V::Number&&key.n>=0&&key.n<4294967295.0&&std::floor(key.n)==key.n){size_t i=size_t(key.n);if(i>=v.p->items.size())v.p->items.resize(i+1);return v.p->items[i]=value;}std::string k=str(key);if(v.tag!=V::Heap)throw std::runtime_error("Cannot set properties of "+str(v));uint32_t i;
  if(v.p->kind==Object::Array){if(k=="length"){v.p->items.resize(u32(value));return value;}if(indexKey(k,i)){if(i>=v.p->items.size())v.p->items.resize(i+1);return v.p->items[i]=value;}}
  auto it=v.p->shape->index.find(k);if(it==v.p->shape->index.end()){v.p->shape=appendShape(v.p->shape,k);v.p->props.push_back(value);}else v.p->props[it->second]=value;return value;}
inline V hotSet(V v,int index,V value){if(v.tag==V::Heap){int slot=v.p->shape->hot[index];if(slot>=0)return v.p->props[slot]=value;}return set(v,V(hotNames[index]),value);}
inline V obj(std::vector<std::pair<V,V>> fields={}){V v=heap(Object::Plain);v.p->props.reserve(fields.size());for(auto& kv:fields)set(v,kv.first,kv.second);return v;}
template<size_t Site> inline V objKnown(std::initializer_list<std::pair<V,V>> fields){
  static Shape* layout=nullptr;
  if(!layout){V v=obj(std::vector<std::pair<V,V>>(fields));layout=v.p->shape;return v;}
  V v=heap(Object::Plain);v.p->shape=layout;v.p->props.reserve(fields.size());
  for(const auto& field:fields)v.p->props.push_back(field.second);
  return v;
}
inline Args iter(V v){if(v.tag==V::String){Args a;auto units=utf16(v.string());for(size_t i=0;i<units.size();++i){size_t end=i+1;if(units[i]>=0xd800&&units[i]<=0xdbff&&end<units.size()&&units[end]>=0xdc00&&units[end]<=0xdfff)++end;a.emplace_back(utf16String(units,i,end));i=end-1;}return a;}if(v.tag!=V::Heap)throw std::runtime_error(str(v)+" is not iterable");
  if(v.p->kind==Object::Array)return v.p->items;Args a;if(v.p->kind==Object::Map)for(auto& kv:v.p->ordered->entries)a.push_back(arr({kv.first,kv.second}));else if(v.p->kind==Object::Set)for(auto& kv:v.p->ordered->entries)a.push_back(kv.first);else throw std::runtime_error("object is not iterable");return a;}
struct Iteration {
  V value;Args fallback;
  explicit Iteration(V v):value(v){if(v.tag!=V::Heap||v.p->kind!=Object::Array)fallback=iter(v);}
  size_t size()const{return value.tag==V::Heap&&value.p->kind==Object::Array?value.p->items.size():fallback.size();}
  V at(size_t i)const{return value.tag==V::Heap&&value.p->kind==Object::Array?value.p->items[i]:fallback[i];}
  struct Iterator {const Iteration* range;size_t index;V operator*()const{return range->at(index);}Iterator& operator++(){++index;return *this;}bool operator!=(const Iterator&)const{return index<range->size();}};
  Iterator begin()const{return {this,0};}Iterator end()const{return {this,size()};}
};
inline Iteration iterate(V v){return Iteration(v);}
inline V call(V f,const CallArgs& a){if(f.tag!=V::Heap||f.p->kind!=Object::Function)throw std::runtime_error(str(f)+" is not a function");return f.p->function->fn(a);}
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
enum class Binary{StrictEq,StrictNe,Add,Sub,Mul,Div,Mod,Pow,Eq,Ne,Lt,Gt,Le,Ge,Or,And,Xor,Ushr,Shr,Shl};
enum class Unary{Not,Plus,Minus,BitNot,Void,Typeof};
// Ordered argument construction preserves JS left-to-right operand evaluation.
template<Binary Op> inline double numericBinary(std::initializer_list<double> a){
  double l=*a.begin(),r=*(a.begin()+1);
  if constexpr(Op==Binary::Add)return l+r;
  if constexpr(Op==Binary::Sub)return l-r;
  if constexpr(Op==Binary::Mul)return l*r;
  if constexpr(Op==Binary::Div)return l/r;
  if constexpr(Op==Binary::Mod)return std::fmod(l,r);
  if constexpr(Op==Binary::Pow)return std::pow(l,r);
}
inline double lengthScaledXY(double x,double y){
  double b=std::abs(y),c=std::abs(x);
  if(std::isinf(b)||std::isinf(c))return INFINITY;
  if(std::isnan(b)||std::isnan(c))return NAN;
  double m=std::max(b,c);if(m==0)return 0.0;
  return std::sqrt((c/m)*(c/m)+(b/m)*(b/m))*m;
}
// Native Euclidean geometry. Ordinary arena coordinates avoid the two
// divisions in V8's scaled hypot; extremes retain the overflow-safe fallback.
inline double lengthXY(double x,double y){
  double q=x*x+y*y;if(std::isfinite(q)&&q>=std::numeric_limits<double>::min())return std::sqrt(q);
  if(x==0&&y==0)return 0.0;return lengthScaledXY(x,y);
}
struct DistanceMeasure {double square,linear;bool ordinary;};
inline DistanceMeasure measureDistance(V a,V b){
  double dx=num(hotProp(a,0))-num(hotProp(b,0)),dy=num(hotProp(a,1))-num(hotProp(b,1)),q=dx*dx+dy*dy;
  bool ordinary=std::isfinite(q)&&(q>=std::numeric_limits<double>::min()||(dx==0&&dy==0));
  return {q,ordinary?0.0:lengthScaledXY(dx,dy),ordinary};
}
template<Binary Op> inline bool compareDistance(DistanceMeasure d,V threshold){
  double r=num(threshold);if(std::isnan(r)||(!d.ordinary&&std::isnan(d.linear)))return false;
  if(r<0)return Op==Binary::Gt||Op==Binary::Ge;
  double rr=r*r;
  bool ordinary=d.ordinary&&std::isfinite(rr)&&(rr>=std::numeric_limits<double>::min()||r==0);
  double lhs=ordinary?d.square:d.ordinary?std::sqrt(d.square):d.linear,rhs=ordinary?rr:r;
  if constexpr(Op==Binary::Lt)return lhs<rhs;
  if constexpr(Op==Binary::Le)return lhs<=rhs;
  if constexpr(Op==Binary::Gt)return lhs>rhs;
  if constexpr(Op==Binary::Ge)return lhs>=rhs;
}
inline double minNumber(double x,double y){if(std::isnan(x)||std::isnan(y))return NAN;if(x==0&&y==0)return std::signbit(x)||std::signbit(y)?-0.0:0.0;return std::min(x,y);}
inline double maxNumber(double x,double y){if(std::isnan(x)||std::isnan(y))return NAN;if(x==0&&y==0)return std::signbit(x)&&std::signbit(y)?-0.0:0.0;return std::max(x,y);}
inline double clampNumber(double v,double a,double b){return maxNumber(a,minNumber(b,v));}
inline double distanceXY(V a,V b){
  double dx=numericBinary<Binary::Sub>({num(hotProp(a,0)),num(hotProp(b,0))});
  double dy=numericBinary<Binary::Sub>({num(hotProp(a,1)),num(hotProp(b,1))});
  return lengthXY(dx,dy);
}

template<Binary Op> inline V binary(std::initializer_list<V> a){V x=arg(a,0),y=arg(a,1);
  if(Op==Binary::StrictEq)return V(eq(x,y));if(Op==Binary::StrictNe)return V(!eq(x,y));
  if(Op==Binary::Add&&(x.tag==V::String||y.tag==V::String))return V(str(x)+str(y));
  double l=num(x),r=num(y);
  if(Op==Binary::Add){if(x.tag==V::String||y.tag==V::String)return V(str(x)+str(y));return V(l+r);}if(Op==Binary::Sub)return V(l-r);if(Op==Binary::Mul)return V(l*r);if(Op==Binary::Div)return V(l/r);if(Op==Binary::Mod)return V(std::fmod(l,r));if(Op==Binary::Pow)return V(std::pow(l,r));
  if(Op==Binary::StrictEq)return V(eq(x,y));if(Op==Binary::StrictNe)return V(!eq(x,y));if(Op==Binary::Eq)return V(eq(x,y)||(nullish(x)&&nullish(y))||((x.tag!=V::Heap&&y.tag!=V::Heap)&&l==r));if(Op==Binary::Ne)return V(!truth(binary<Binary::Eq>(a)));
  if(Op==Binary::Lt)return V(x.tag==V::String&&y.tag==V::String?x.string()<y.string():l<r);if(Op==Binary::Gt)return V(x.tag==V::String&&y.tag==V::String?x.string()>y.string():l>r);if(Op==Binary::Le)return V(x.tag==V::String&&y.tag==V::String?x.string()<=y.string():l<=r);if(Op==Binary::Ge)return V(x.tag==V::String&&y.tag==V::String?x.string()>=y.string():l>=r);
  if(Op==Binary::Or)return V(double(i32(x)|i32(y)));if(Op==Binary::And)return V(double(i32(x)&i32(y)));if(Op==Binary::Xor)return V(double(i32(x)^i32(y)));
  if(Op==Binary::Ushr)return V(double(u32(x)>>(u32(y)&31)));if(Op==Binary::Shr)return V(double(i32(x)>>(u32(y)&31)));if(Op==Binary::Shl){uint32_t u=u32(x)<<(u32(y)&31);return V(double(i32(V(double(u)))));}
  throw std::runtime_error("unreachable binary operator");}
template<Unary Op> inline V unaryKnown(V v){if(Op==Unary::Not)return V(!truth(v));if(Op==Unary::Plus)return V(num(v));if(Op==Unary::Minus)return V(-num(v));if(Op==Unary::BitNot)return V(double(~i32(v)));if(Op==Unary::Void)return V();if(Op==Unary::Typeof){switch(v.tag){case V::Undefined:return V("undefined");case V::Boolean:return V("boolean");case V::Number:return V("number");case V::String:return V("string");case V::Heap:if(v.p->kind==Object::Function)return V("function");default:return V("object");}}throw std::runtime_error("unreachable unary operator");}
struct Local {mutable V v;V val()const{return v;}V set(V x)const{return v=x;}};
struct Ref {
  V* cell=nullptr;const Var* binding=nullptr;V base,key;int hot=-1,named=-1;
  Ref(const Var& x):binding(&x){}Ref(const Local& x):cell(&x.v){}
  Ref(V b,V k):base(b),key(k){}Ref(V b,V k,int field):base(b),key(k),named(field){}Ref(V b,int h):base(b),hot(h){}
  V val()const{return binding?binding->val():cell?*cell:hot>=0?hotProp(base,hot):named>=0?propCached(base,key.string(),size_t(named)):get(base,key);}
  V put(V x)const{
    if(binding)return binding->set(x);if(cell)return *cell=x;if(hot>=0)return hotSet(base,hot,x);
    if(named>=0&&base.tag==V::Heap&&(base.p->kind==Object::Plain||base.p->kind==Object::Function)){int slot=namedSlot(base.p->shape,size_t(named),0,key.string());if(slot>=0)return base.p->props[size_t(slot)]=x;}
    return set(base,key,x);
  }
};
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
    V key=arg(a,0);if(key.tag==V::Number&&key.n==0)key.n=0;auto find=[&](){auto it=p->ordered->entryIndex.find(key);return it==p->ordered->entryIndex.end()?p->ordered->entries.end():p->ordered->entries.begin()+it->second;};
    if(k=="get"){auto i=find();return i==p->ordered->entries.end()?V():i->second;}
    if(k=="has")return V(find()!=p->ordered->entries.end());
    if(k=="set"||k=="add"){V val=k=="add"?key:arg(a,1);auto i=find();if(i==p->ordered->entries.end()){p->ordered->entryIndex.emplace(key,p->ordered->entries.size());p->ordered->entries.emplace_back(key,val);}else i->second=val;return v;}
    if(k=="delete"){auto i=find();bool yes=i!=p->ordered->entries.end();if(yes){size_t slot=i-p->ordered->entries.begin();p->ordered->entryIndex.erase(key);p->ordered->entries.erase(i);for(size_t j=slot;j<p->ordered->entries.size();++j)p->ordered->entryIndex[p->ordered->entries[j].first]=j;}return V(yes);}
    if(k=="keys"||k=="values"){Args out;for(auto& kv:p->ordered->entries)out.push_back(k=="keys"?kv.first:kv.second);return arr(out);}
    if(k=="entries"){Args out;for(auto& kv:p->ordered->entries)out.push_back(arr({kv.first,kv.second}));return arr(out);}
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
enum class Method{M_toFixed,M_split,M_includes,M_indexOf,M_get,M_has,M_set,M_add,M_delete,M_keys,M_values,M_entries,M_push,M_unshift,M_shift,M_slice,M_splice,M_concat,M_join,M_sort,M_reduce,M_map,M_filter,M_some,M_every,M_find,M_findIndex,M_forEach,M_state,M_clone};
inline const std::array<std::string,30> methodNames{"toFixed","split","includes","indexOf","get","has","set","add","delete","keys","values","entries","push","unshift","shift","slice","splice","concat","join","sort","reduce","map","filter","some","every","find","findIndex","forEach","state","clone"};
template<Method M> inline V methodKnown(V v,const CallArgs& a){
  const std::string& k=methodNames[size_t(M)];V own=propKnown<size_t(M),1>(v,k);if(own.tag!=V::Undefined)return call(own,std::move(a));
  if(v.tag==V::Number&&M==Method::M_toFixed){double d=a.empty()?0:num(a[0]);if(std::isnan(d))d=0;if(!std::isfinite(d)||std::trunc(d)<0||std::trunc(d)>100)throw std::runtime_error("toFixed() digits argument must be between 0 and 100");return fixed(v.n,int(d));}
  if(v.tag==V::String&&(M==Method::M_split||M==Method::M_includes||M==Method::M_indexOf)){
    auto units=utf16(v.string()),separator=utf16(str(arg(a,0)));Args out;
    if(M==Method::M_split){
      uint32_t limit=a.size()<2||a[1].tag==V::Undefined?UINT32_MAX:u32(a[1]);if(!limit)return arr();
      if(a.empty()||a[0].tag==V::Undefined)return arr({v});
      if(separator.empty()){for(size_t i=0;i<units.size()&&out.size()<limit;++i)out.emplace_back(utf16String(units,i,i+1));return arr(out);}
      size_t start=0;while(out.size()<limit){auto hit=std::search(units.begin()+start,units.end(),separator.begin(),separator.end());if(hit==units.end())break;size_t pos=hit-units.begin();out.emplace_back(utf16String(units,start,pos));start=pos+separator.size();}
      if(out.size()<limit)out.emplace_back(utf16String(units,start,units.size()));return arr(out);
    }
    double raw=a.size()>1?num(a[1]):0;if(std::isnan(raw))raw=0;size_t start=size_t(std::max(0.0,std::min(double(units.size()),std::trunc(raw))));
    auto hit=std::search(units.begin()+start,units.end(),separator.begin(),separator.end());bool found=separator.empty()||hit!=units.end();
    return M==Method::M_includes?V(found):V(found?int(hit-units.begin()):-1);
  }
  if(v.tag!=V::Heap)throw std::runtime_error(k+" is not a function");
  auto p=v.p;
  if(p->kind==Object::Map||p->kind==Object::Set){
    V key=arg(a,0);if(key.tag==V::Number&&key.n==0)key.n=0;auto find=[&](){auto it=p->ordered->entryIndex.find(key);return it==p->ordered->entryIndex.end()?p->ordered->entries.end():p->ordered->entries.begin()+it->second;};
    if(M==Method::M_get){auto i=find();return i==p->ordered->entries.end()?V():i->second;}
    if(M==Method::M_has)return V(find()!=p->ordered->entries.end());
    if(M==Method::M_set||M==Method::M_add){V val=M==Method::M_add?key:arg(a,1);auto i=find();if(i==p->ordered->entries.end()){p->ordered->entryIndex.emplace(key,p->ordered->entries.size());p->ordered->entries.emplace_back(key,val);}else i->second=val;return v;}
    if(M==Method::M_delete){auto i=find();bool yes=i!=p->ordered->entries.end();if(yes){size_t slot=i-p->ordered->entries.begin();p->ordered->entryIndex.erase(key);p->ordered->entries.erase(i);for(size_t j=slot;j<p->ordered->entries.size();++j)p->ordered->entryIndex[p->ordered->entries[j].first]=j;}return V(yes);}
    if(M==Method::M_keys||M==Method::M_values){Args out;for(auto& kv:p->ordered->entries)out.push_back(M==Method::M_keys?kv.first:kv.second);return arr(out);}
    if(M==Method::M_entries){Args out;for(auto& kv:p->ordered->entries)out.push_back(arr({kv.first,kv.second}));return arr(out);}
  }
  if(p->kind==Object::Array){
    auto& xs=p->items;int n=xs.size();
    if(M==Method::M_push){xs.insert(xs.end(),a.begin(),a.end());return V(double(xs.size()));}
    if(M==Method::M_unshift){xs.insert(xs.begin(),a.begin(),a.end());return V(double(xs.size()));}
    if(M==Method::M_shift){if(xs.empty())return V();V r=xs.front();xs.erase(xs.begin());return r;}
    if(M==Method::M_slice){int start=relative(arg(a,0),n,0),end=relative(arg(a,1),n,n);return arr(Args(xs.begin()+start,xs.begin()+std::max(start,end)));}
    if(M==Method::M_splice){int start=relative(arg(a,0),n,0),count=a.size()<2?n-start:int(std::min(double(n-start),std::max(0.0,num(a[1]))));Args out(xs.begin()+start,xs.begin()+start+count);xs.erase(xs.begin()+start,xs.begin()+start+count);if(a.size()>2)xs.insert(xs.begin()+start,a.begin()+2,a.end());return arr(out);}
    if(M==Method::M_concat){Args out=xs;for(V x:a){if(x.tag==V::Heap&&x.p->kind==Object::Array)spread(out,x);else out.push_back(x);}return arr(out);}
    if(M==Method::M_includes||M==Method::M_indexOf){for(int i=0;i<n;++i)if(M==Method::M_includes?same(xs[i],arg(a,0)):eq(xs[i],arg(a,0)))return M==Method::M_includes?V(true):V(i);return M==Method::M_includes?V(false):V(-1);}
    if(M==Method::M_join){std::string sep=a.empty()?",":str(a[0]),out;for(int i=0;i<n;++i){if(i)out+=sep;if(!nullish(xs[i]))out+=str(xs[i]);}return V(out);}
    if(M==Method::M_sort){std::stable_sort(xs.begin(),xs.end(),[&](const V& x,const V& y){if(a.empty())return str(x)<str(y);return num(call(a[0],{x,y}))<0;});return v;}
    if(M==Method::M_reduce){V acc;int i=0;if(a.size()>1)acc=a[1];else{if(!n)throw std::runtime_error("Reduce of empty array with no initial value");acc=xs[i++];}for(;i<n;++i)acc=call(a[0],{acc,xs[i],V(i),v});return acc;}
    if(M==Method::M_map||M==Method::M_filter||M==Method::M_some||M==Method::M_every||M==Method::M_find||M==Method::M_findIndex||M==Method::M_forEach){
      Args out;for(int i=0;i<n;++i){V x=xs[i];V r=call(a[0],{x,V(i),v});bool ok=truth(r);if(M==Method::M_map)out.push_back(r);else if(M==Method::M_filter){if(ok)out.push_back(x);}else if(M==Method::M_some&&ok)return V(true);else if(M==Method::M_every&&!ok)return V(false);else if(M==Method::M_find&&ok)return x;else if(M==Method::M_findIndex&&ok)return V(i);}
      if(M==Method::M_some)return V(false);if(M==Method::M_every)return V(true);if(M==Method::M_findIndex)return V(-1);if(M==Method::M_find||M==Method::M_forEach)return V();return arr(out);
    }
  }throw std::runtime_error("unsupported method "+k);
}
// Immediate callbacks have a direct C++ call path. A source-defined method
// still receives a real rooted function through the lazy fallback factory.
template<Method M,class Callback,class Factory> inline V arrayCallbackKnown(const CallArgs& args,Callback&& callback,Factory&& factory){
  V v=arg(args,0);const CallArgs a(args.data+1,args.length-1);
  const std::string& key=methodNames[size_t(M)];V own=propKnown<size_t(M),1>(v,key);
  if(own.tag!=V::Undefined||v.tag!=V::Heap||v.p->kind!=Object::Array){Args passed{factory()};passed.insert(passed.end(),a.begin(),a.end());return methodKnown<M>(v,passed);}
  auto& xs=v.p->items;int n=int(xs.size());
  if constexpr(M==Method::M_sort){std::stable_sort(xs.begin(),xs.end(),[&](V x,V y){return num(callback(CallArgs{x,y}))<0;});return v;}
  if constexpr(M==Method::M_reduce){V acc;int i=0;if(!a.empty())acc=a[0];else{if(!n)throw std::runtime_error("Reduce of empty array with no initial value");acc=xs[i++];}for(;i<n;++i)acc=callback(CallArgs{acc,xs[i],V(i),v});return acc;}
  Args out;if constexpr(M==Method::M_map||M==Method::M_filter)out.reserve(size_t(n));
  for(int i=0;i<n;++i){V x=xs[i];V r=callback(CallArgs{x,V(i),v});bool ok=truth(r);
    if constexpr(M==Method::M_map)out.push_back(r);
    if constexpr(M==Method::M_filter){if(ok)out.push_back(x);}
    if constexpr(M==Method::M_some){if(ok)return V(true);}
    if constexpr(M==Method::M_every){if(!ok)return V(false);}
    if constexpr(M==Method::M_find){if(ok)return x;}
    if constexpr(M==Method::M_findIndex){if(ok)return V(i);}
  }
  if constexpr(M==Method::M_some)return V(false);
  if constexpr(M==Method::M_every)return V(true);
  if constexpr(M==Method::M_findIndex)return V(-1);
  if constexpr(M==Method::M_find||M==Method::M_forEach)return V();
  return arr(std::move(out));
}
template<Method M> inline V methodKnown(const CallArgs& a){return methodKnown<M>(a[0],CallArgs(a.data+1,a.length-1));}
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
  for(auto& p:arena)p->marked=false;
  for(auto& c:cells)c->gcMarked=false;
  std::unordered_set<const std::string*> liveStrings;
  for(size_t i=0;i<permanentCells;++i){cells[i]->gcMarked=true;roots.push_back(*cells[i]);}
  while(!roots.empty()){
    V v=std::move(roots.back());roots.pop_back();
    if(v.tag==V::String){liveStrings.insert(v.text);continue;}
    if(v.tag!=V::Heap||v.p->marked)continue;v.p->marked=true;
    for(V p:v.p->props)roots.push_back(p);
    for(auto& x:v.p->items)roots.push_back(x);
    if(v.p->ordered)for(auto& p:v.p->ordered->entries){roots.push_back(p.first);roots.push_back(p.second);}
    if(v.p->function)for(V x:v.p->function->capturedValues)roots.push_back(x);
    if(v.p->function)for(V* c:v.p->function->captured)if(!c->gcMarked){c->gcMarked=true;roots.push_back(*c);}
  }
  arena.erase(std::remove_if(arena.begin(),arena.end(),[&](auto& p){
    if(p->marked)return false;
    p->props.clear();p->items.clear();
    if(p->ordered){p->ordered->entries.clear();p->ordered->entryIndex.clear();}
    if(p->function){p->function->captured.clear();p->function->capturedValues.clear();p->function->fn=nullptr;}
    p->shape=&emptyShape;spareObjects[size_t(p->kind)].push_back(std::move(p));return true;
  }),arena.end());
  for(auto it=strings.begin();it!=strings.end();)if(!liveStrings.count(&*it))it=strings.erase(it);else ++it;
  auto first=cells.begin()+permanentCells;
  cells.erase(std::remove_if(first,cells.end(),[&](auto& p){if(p->gcMarked)return false;spareCells.push_back(std::move(p));return true;}),cells.end());
}
struct Finally {std::function<void()> f;~Finally(){f();}};
} // namespace js
