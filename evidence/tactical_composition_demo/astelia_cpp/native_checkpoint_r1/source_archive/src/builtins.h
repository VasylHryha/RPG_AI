#pragma once
#include "js_value.h"
namespace v8 {namespace base {namespace ieee754 {
double sin(double);double cos(double);double atan2(double,double);
}}}
namespace js {
inline V builtin(const std::string& name,const CallArgs& a){
  V x=arg(a,0);double n=num(x);
  if(name=="Math.PI")return V(3.14159265358979323846);
  if(name=="Math.sin")return V(v8::base::ieee754::sin(n));
  if(name=="Math.cos")return V(v8::base::ieee754::cos(n));
  if(name=="Math.atan2")return V(v8::base::ieee754::atan2(n,num(arg(a,1))));
  if(name=="Math.sqrt")return V(std::sqrt(n));
  if(name=="Math.abs")return V(std::abs(n));
  if(name=="Math.floor")return V(std::floor(n));
  if(name=="Math.ceil")return V(std::ceil(n));
  if(name=="Math.round"){if(!std::isfinite(n)||n==0)return x;double f=std::floor(n);double r=(n-f<0.5)?f:f+1;return V(r==0?std::copysign(0.0,n):r);}
  if(name=="Math.min"||name=="Math.max"){double r=name=="Math.min"?INFINITY:-INFINITY;for(V v:a){double y=num(v);if(std::isnan(y))return V(NAN);if(name=="Math.min"){if(y<r||(y==0&&r==0&&std::signbit(y)))r=y;}else if(y>r||(y==0&&r==0&&!std::signbit(y)))r=y;}return V(r);}
  if(name=="Math.hypot"){if(a.size()!=2)throw std::runtime_error("hypot expects two arguments in this simulation");double b=std::abs(num(a[1])),c=std::abs(n);if(std::isinf(b)||std::isinf(c))return V(INFINITY);if(std::isnan(b)||std::isnan(c))return V(NAN);double m=std::max(b,c);if(m==0)return V(0);return V(std::sqrt((c/m)*(c/m)+(b/m)*(b/m))*m);}
  if(name=="Boolean")return V(truth(x));if(name=="Number")return V(n);if(name=="String")return V(str(x));
  if(name=="Object.assign"){for(size_t i=1;i<a.size();++i)assign(x,a[i]);return x;}
  if(name=="Object.keys")return arr(keys(x));
  if(name=="Object.values"){Args out;for(V k:keys(x))out.push_back(get(x,k));return arr(out);}
  if(name=="Object.entries"){Args out;for(V k:keys(x))out.push_back(arr({k,get(x,k)}));return arr(out);}
  if(name=="Object.fromEntries"){V out=obj();for(V entry:iter(x))set(out,get(entry,0),get(entry,1));return out;}
  if(name=="Array.isArray")return V(x.tag==V::Heap&&x.p->kind==Object::Array);
  if(name=="Array.from"){Args out;if(x.tag==V::Heap&&x.p->kind==Object::Plain){int len=int(num(get(x,"length")));for(int i=0;i<len;++i)out.push_back(V());}else out=iter(x);if(a.size()>1)for(size_t i=0;i<out.size();++i)out[i]=call(a[1],{out[i],V(double(i))});return arr(out);}
  if(name=="JSON.stringify")return V(stringify(x));if(name=="JSON.parse")return parse(str(x));
  throw std::runtime_error("unsupported builtin "+name);
}
enum class Builtin{Math_PI,Math_sin,Math_cos,Math_atan2,Math_sqrt,Math_abs,Math_floor,Math_ceil,Math_round,Math_min,Math_max,Math_hypot,Boolean,Number,String,Object_assign,Object_keys,Object_values,Object_entries,Object_fromEntries,Array_isArray,Array_from,JSON_stringify,JSON_parse};
template<Builtin B> inline V builtinKnown(const CallArgs& a){
  V x=arg(a,0);double n=0;if constexpr (B==Builtin::Math_sin||B==Builtin::Math_cos||B==Builtin::Math_atan2||B==Builtin::Math_sqrt||B==Builtin::Math_abs||B==Builtin::Math_floor||B==Builtin::Math_ceil||B==Builtin::Math_round||B==Builtin::Math_min||B==Builtin::Math_max||B==Builtin::Math_hypot||B==Builtin::Number)n=num(x);
  if(B==Builtin::Math_PI)return V(3.14159265358979323846);
  if(B==Builtin::Math_sin)return V(v8::base::ieee754::sin(n));
  if(B==Builtin::Math_cos)return V(v8::base::ieee754::cos(n));
  if(B==Builtin::Math_atan2)return V(v8::base::ieee754::atan2(n,num(arg(a,1))));
  if(B==Builtin::Math_sqrt)return V(std::sqrt(n));
  if(B==Builtin::Math_abs)return V(std::abs(n));
  if(B==Builtin::Math_floor)return V(std::floor(n));
  if(B==Builtin::Math_ceil)return V(std::ceil(n));
  if(B==Builtin::Math_round){if(!std::isfinite(n)||n==0)return x;double f=std::floor(n);double r=(n-f<0.5)?f:f+1;return V(r==0?std::copysign(0.0,n):r);}
  if(B==Builtin::Math_min||B==Builtin::Math_max){double r=B==Builtin::Math_min?INFINITY:-INFINITY;for(V v:a){double y=num(v);if(std::isnan(y))return V(NAN);if(B==Builtin::Math_min){if(y<r||(y==0&&r==0&&std::signbit(y)))r=y;}else if(y>r||(y==0&&r==0&&!std::signbit(y)))r=y;}return V(r);}
  if(B==Builtin::Math_hypot){if(a.size()!=2)throw std::runtime_error("hypot expects two arguments in this simulation");double b=std::abs(num(a[1])),c=std::abs(n);if(std::isinf(b)||std::isinf(c))return V(INFINITY);if(std::isnan(b)||std::isnan(c))return V(NAN);double m=std::max(b,c);if(m==0)return V(0);return V(std::sqrt((c/m)*(c/m)+(b/m)*(b/m))*m);}
  if(B==Builtin::Boolean)return V(truth(x));if(B==Builtin::Number)return V(n);if(B==Builtin::String)return V(str(x));
  if(B==Builtin::Object_assign){for(size_t i=1;i<a.size();++i)assign(x,a[i]);return x;}
  if(B==Builtin::Object_keys)return arr(keys(x));
  if(B==Builtin::Object_values){Args out;for(V k:keys(x))out.push_back(get(x,k));return arr(out);}
  if(B==Builtin::Object_entries){Args out;for(V k:keys(x))out.push_back(arr({k,get(x,k)}));return arr(out);}
  if(B==Builtin::Object_fromEntries){V out=obj();for(V entry:iter(x))set(out,get(entry,0),get(entry,1));return out;}
  if(B==Builtin::Array_isArray)return V(x.tag==V::Heap&&x.p->kind==Object::Array);
  if(B==Builtin::Array_from){Args out;if(x.tag==V::Heap&&x.p->kind==Object::Plain){int len=int(num(get(x,"length")));for(int i=0;i<len;++i)out.push_back(V());}else out=iter(x);if(a.size()>1)for(size_t i=0;i<out.size();++i)out[i]=call(a[1],{out[i],V(double(i))});return arr(out);}
  if(B==Builtin::JSON_stringify)return V(stringify(x));if(B==Builtin::JSON_parse)return parse(str(x));
  throw std::runtime_error("unreachable builtin");
}
}
