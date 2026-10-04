#include "builtins.h"
#include <cassert>
#include <cstring>
using namespace js;
static void identical(V a,V b){
  assert(a.tag==b.tag);
  if(a.tag==V::Number){assert((std::isnan(a.n)&&std::isnan(b.n))||(a.n==b.n&&std::signbit(a.n)==std::signbit(b.n)));}
  else assert(stringify(a)==stringify(b));
}
int main(){
  Args values{V(),V(nullptr),V(false),V(true),V(-0.0),V(0),V(-2.5),V(2.5),V(4294967296.5),V(INFINITY),V(-INFINITY),V(NAN),V(""),V("1"),V("word")};
  for(V a:values)for(V b:values){
#define CHECK_OP(id,text) identical(binary<Binary::id>({a,b}),bin(text,{a,b}));
    CHECK_OP(StrictEq,"===") CHECK_OP(StrictNe,"!==") CHECK_OP(Add,"+") CHECK_OP(Sub,"-") CHECK_OP(Mul,"*")
    CHECK_OP(Div,"/") CHECK_OP(Mod,"%") CHECK_OP(Pow,"**") CHECK_OP(Eq,"==") CHECK_OP(Ne,"!=")
    CHECK_OP(Lt,"<") CHECK_OP(Gt,">") CHECK_OP(Le,"<=") CHECK_OP(Ge,">=")
    CHECK_OP(Or,"|") CHECK_OP(And,"&") CHECK_OP(Xor,"^") CHECK_OP(Ushr,">>>") CHECK_OP(Shr,">>") CHECK_OP(Shl,"<<")
#undef CHECK_OP
    identical(builtinKnown<Builtin::Math_min>({a,b}),builtin("Math.min",{a,b}));
    identical(builtinKnown<Builtin::Math_max>({a,b}),builtin("Math.max",{a,b}));
    identical(builtinKnown<Builtin::Math_hypot>({a,b}),builtin("Math.hypot",{a,b}));
    identical(V(lengthScaledXY(num(a),num(b))),builtin("Math.hypot",{a,b}));
    identical(V(minNumber(num(a),num(b))),builtin("Math.min",{a,b}));
    identical(V(maxNumber(num(a),num(b))),builtin("Math.max",{a,b}));
#define CHECK_NUM(id,text) identical(V(numericBinary<Binary::id>({num(a),num(b)})),bin(text,{a,b}));
    CHECK_NUM(Sub,"-") CHECK_NUM(Mul,"*") CHECK_NUM(Div,"/") CHECK_NUM(Mod,"%") CHECK_NUM(Pow,"**")
#undef CHECK_NUM
  }
  V origin=obj({{V("x"),V(0)},{V("y"),V(0)}}),point=obj({{V("x"),V(3)},{V("y"),V(4)}});
  auto distance=measureDistance(origin,point);assert(compareDistance<Binary::Le>(distance,V(5)));assert(!compareDistance<Binary::Lt>(distance,V(5)));
  assert(compareDistance<Binary::Gt>(distance,V(-1)));assert(!compareDistance<Binary::Le>(distance,V(-1)));assert(!compareDistance<Binary::Ge>(distance,V(NAN)));
  assert(lengthXY(3,4)==5);assert(std::isfinite(lengthXY(1e300,1e300)));assert(lengthXY(1e-300,0)==1e-300);assert(std::isinf(lengthXY(INFINITY,NAN)));
  V map=construct("Map",{}),one=obj(),two=obj();
  methodKnown<Method::M_set>(map,{V(NAN),V(1)});methodKnown<Method::M_set>(map,{V(NAN),V(2)});
  methodKnown<Method::M_set>(map,{V(-0.0),V(3)});methodKnown<Method::M_set>(map,{V(0),V(4)});
  methodKnown<Method::M_set>(map,{V(true),V(5)});methodKnown<Method::M_set>(map,{V(1),V(6)});
  methodKnown<Method::M_set>(map,{one,V(7)});methodKnown<Method::M_set>(map,{two,V(8)});
  assert(num(get(map,"size"))==6);assert(num(methodKnown<Method::M_get>(map,{one}))==7);
  assert(num(methodKnown<Method::M_get>(map,{two}))==8);assert(num(method(map,"get",{V(NAN)}))==2);
  assert(!std::signbit(num(get(methodKnown<Method::M_keys>(map,{}),1))));
  methodKnown<Method::M_delete>(map,{V(true)});methodKnown<Method::M_set>(map,{V(true),V(9)});
  assert(num(get(methodKnown<Method::M_values>(map,{}),5))==9);
  assert(num(methodKnown<Method::M_get>(map,{V(1)}))==6);
  V array=arr({V(1),V(2)});int count=0;
  for(V value:iterate(array)){++count;if(num(value)==1)methodKnown<Method::M_push>(array,{V(3)});}
  assert(count==3);
  V first=obj({{V("a"),V(1)},{V("b"),V(2)}}),second=obj({{V("b"),V(3)},{V("a"),V(4)}});
  identical(propKnown<999>(first,"a"),V(1));identical(propKnown<999>(second,"a"),V(4));
  set(first,"c",V(5));identical(propKnown<999>(first,"a"),V(1));
  identical(propKnown<999>(obj(),"a"),V());
  assert(stringify(arr(keys(second)))=="[\"b\",\"a\"]");
  V mutableObject=obj({{V("a"),V(1)}});Ref named(mutableObject,V("a"),999);
  set(mutableObject,"new",V(2));for(int i=0;i<100;++i)set(mutableObject,V("new"+std::to_string(i)),V(i));
  named.put(V(7));identical(named.val(),V(7));identical(get(mutableObject,"a"),V(7));
  Var lazyValue(V(1));size_t before=cells.size();Ref(lazyValue).put(V(2));assert(cells.size()==before);Var captured(lazyValue);assert(cells.size()==before+1);Ref(lazyValue).put(V(3));identical(captured.val(),V(3));
  Var self;Ref beforeCapture(self);V recursive=fn([=](const CallArgs&){return self.val();},{self});beforeCapture.put(recursive);assert(call(recursive,{}).p==recursive.p);
  int constructed=0;Var sum(V(0));V input=arr({V(3),V(1),V(2)});
  auto predicate=[&](const CallArgs& a){sum.set(V(num(sum.val())+num(a[0])));return V(num(a[0])>1);};
  auto lazy=[&](){++constructed;return fn(predicate,{sum});};
  V filtered=arrayCallbackKnown<Method::M_filter>({input},predicate,lazy);assert(stringify(filtered)=="[3,2]");assert(num(sum.val())==6&&constructed==0);
  V custom=arr({V(1)});set(custom,"some",fn([](const CallArgs& a){return call(a[0],{V(9)});}));
  identical(arrayCallbackKnown<Method::M_some>({custom},predicate,lazy),V(true));assert(constructed==1&&num(sum.val())==15);
  V fixed=objKnown<1000>({{V("x"),V(1)},{V("10"),V(10)},{V("2"),V(2)},{V("a"),V(3)}});
  V fixedAgain=objKnown<1000>({{V("x"),V(9)},{V("10"),V(8)},{V("2"),V(7)},{V("a"),V(6)}});
  assert(fixed.p->shape==fixedAgain.p->shape);identical(hotProp(fixedAgain,0),V(9));
  assert(stringify(arr(keys(fixedAgain)))=="[\"2\",\"10\",\"x\",\"a\"]");
  Var state(V(41));V kept=obj({{V("text"),V("retained value")}});
  V callback=fn([=](const CallArgs&){state.set(V(num(state.val())+1));return get(kept,"text");},{state});
  V rooted=fnValues([=](const CallArgs&){return kept;},{kept});
  set(map,"get",fn([](const CallArgs&){return V(123);}));identical(methodKnown<Method::M_get>(map,{V(1)}),V(123));
  for(int i=0;i<3;++i){for(int j=0;j<1000;++j)obj({{V("discard"),arr({V(j)})}});collect({callback,rooted,map},0);
    identical(call(callback,{}),V("retained value"));assert(num(state.val())==42+i);assert(call(rooted,{}).p==kept.p);
    identical(methodKnown<Method::M_get>(map,{V(1)}),V(123));
  }
  std::cout<<"runtime contracts identical\n";
}
