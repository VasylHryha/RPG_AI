// Development-only mechanical translation. Build/run use the committed C++ alone.
// Node's bundled Acorn parses the pinned input; no npm dependencies are installed.
'use strict';
const fs = require('fs'), path = require('path'), Module = require('module');
const parser = new Module('acorn');
parser._compile(process.binding('natives')['internal/deps/acorn/acorn/dist/acorn'], 'acorn.js');
const sourcePath = path.join(__dirname, '../astelia_snapshot/formation_sim.js');
const source = fs.readFileSync(sourcePath, 'utf8');
const ast = parser.exports.parse(source, {ecmaVersion:2022, locations:true});
const body = ast.body[0].expression.callee.body.body.filter(n => !(n.type==='ExpressionStatement' && n.directive));
// The module/browser export wrapper is host glue, not simulation behavior.
body.splice(body.findIndex(n => n.type==='IfStatement' && source.slice(n.start,n.end).includes('module.exports')));
let serial=0, depth=0, objectSite=0;
const literalPool=new Map();
function literal(value){if(!literalPool.has(value))literalPool.set(value,`literal_${literalPool.size}`);return literalPool.get(value);}
let scopes=[];
const globals=new Map(), natives=new Map();
const capturedBindings=new Set();
const hotNames=['x','y','hp','cd','target','alive','id','team','role','w','r','speed','range','dmg','cdMax','vx','vy','svx','svy','units','o','ai','skills','packs','t','dec','move','slotX','slotY','state','prep','formation'];
const q=JSON.stringify;
function fail(n) { throw Error(`${n.type} at line ${n.loc.start.line}: ${source.slice(n.start,n.end).slice(0,160)}`); }
function bindPattern(p,scope) {
  if(p.type==='Identifier'){if(!scope.has(p.name))scope.set(p.name,`v_${p.name}_${serial++}`);}
  else if(p.type==='ArrayPattern')p.elements.filter(Boolean).forEach(p=>bindPattern(p,scope));
  else if(p.type==='ObjectPattern')p.properties.forEach(p=>bindPattern(p.value,scope));
  else if(p.type==='AssignmentPattern')bindPattern(p.left,scope);
  else fail(p);
}
function lookup(name){for(let i=scopes.length-1;i>=0;--i)if(scopes[i].has(name))return scopes[i].get(name);throw Error('Unknown identifier '+name);}
function captures(){return [...new Set(scopes.flatMap(s=>[...s.values()]))];}
function visibleCells(n){
  const used=new Set();function visit(x){if(!x||typeof x!=='object')return;if(x.type==='Identifier')used.add(x.name);for(const [k,v] of Object.entries(x))if(k!=='loc')if(Array.isArray(v))v.forEach(visit);else if(v&&typeof v==='object')visit(v);}
  visit(n);
  const bindings=[...new Set(scopes.slice(1).flatMap(s=>[...s].filter(([name])=>used.has(name)).map(([,v])=>v)))];
  bindings.forEach(v=>capturedBindings.add(v));
  return `{${bindings.join(',')}}`;
}
function rawAssign(p,value) {
  if(p.type==='Identifier')return `${lookup(p.name)}.set(${value});`;
  if(p.type==='ArrayPattern'||p.type==='ObjectPattern'){
    const tmp=`p_${serial++}`;let out=`V ${tmp}=${value};\n`;
    if(p.type==='ArrayPattern')p.elements.forEach((e,i)=>{if(e)out+=rawAssign(e,`get(${tmp},V(${i}))`)+'\n';});
    else p.properties.forEach(e=>{out+=rawAssign(e.value,`get(${tmp},V(${q(e.key.name||e.key.value)}))`)+'\n';});
    return out;
  }
  if(p.type==='AssignmentPattern') {const tmp=`p_${serial++}`;return `V ${tmp}=${value};\n`+rawAssign(p.left,`(${tmp}.tag==V::Undefined?${expr(p.right)}:${tmp})`);}
  if(p.type==='MemberExpression')return `${ref(p)}.put(${value});`;
  fail(p);
}
function ref(n){if(n.type==='Identifier')return `Ref(${lookup(n.name)})`;if(n.type==='MemberExpression'){if(!n.computed&&hotNames.includes(n.property.name))return `Ref(${expr(n.object)},${hotNames.indexOf(n.property.name)})`;if(!n.computed)return `Ref(${expr(n.object)},${literal(n.property.name)},${literal(n.property.name).slice(8)})`;return `([=](){Args r{${expr(n.object)},${key(n)}};return Ref(r[0],r[1]);}())`;}fail(n);}
function key(n){return n.computed?expr(n.property):`V(${q(n.property.name)})`;}
function argumentsExpr(nodes){
  if(!nodes.some(n=>n&&n.type==='SpreadElement'))return `Args{${nodes.map(n=>n?expr(n):'V()').join(',')}}`;
  return `([=](){Args a;${nodes.map(n=>n.type==='SpreadElement'?`spread(a,${expr(n.argument)});`:`a.push_back(${expr(n)});`).join('')}return a;}())`;
}
function functionExpr(n){
  const capture=visibleCells(n);
  const content=functionContent(n);
  return `fn([=](const CallArgs& a)->V ${content},${capture})`;
}
function functionContent(n){
  const scope=new Map();n.params.forEach(p=>bindPattern(p,scope));scopes.push(scope);depth++;
  let intro=[...scope.values()].map(v=>`Var ${v};`).join('\n')+'\n';
  n.params.forEach((p,i)=>{intro+=rawAssign(p,`arg(a,${i})`)+'\n';});
  let out;
  if(n.body.type==='BlockStatement')out=block(n.body.body,intro);
  else out='{\n'+intro+'return '+expr(n.body)+';\n}';
  depth--;scopes.pop();return out;
}
const numberOps={'-':'Sub','*':'Mul','/':'Div','%':'Mod','**':'Pow','+':'Add'};
function isNumber(n){
  if(n.type==='Literal')return typeof n.value==='number';
  if(n.type==='UnaryExpression')return ['+','-','~'].includes(n.operator);
  if(n.type==='BinaryExpression')return n.operator==='+'?isNumber(n.left)&&isNumber(n.right):['-','*','/','%','**','|','&','^','>>>','>>','<<'].includes(n.operator);
  if(n.type==='Identifier')return ['Infinity','NaN'].includes(n.name);
  if(n.type==='CallExpression'){
    const c=n.callee;
    if(c.type==='Identifier')return ['len','dist','gap','clamp','Number'].includes(c.name)&&(!natives.has(c.name)||lookup(c.name)===globals.get(c.name));
    return c.type==='MemberExpression'&&!c.computed&&c.object.type==='Identifier'&&c.object.name==='Math';
  }
  return false;
}
function numberExpr(n){
  if(n.type==='Literal'&&typeof n.value==='number')return Number.isInteger(n.value)?String(n.value)+'.0':String(n.value);
  if(n.type==='BinaryExpression'&&numberOps[n.operator]&&(n.operator!=='+'||isNumber(n)))return `numericBinary<Binary::${numberOps[n.operator]}>({${numberExpr(n.left)},${numberExpr(n.right)}})`;
  if(n.type==='UnaryExpression'&&['+','-'].includes(n.operator))return `(${n.operator}${numberExpr(n.argument)})`;
  return `num(${expr(n)})`;
}
function expr(n) {
  switch(n.type){
    case 'Literal':return n.value===null?'V(nullptr)':`V(${typeof n.value==='string'?q(n.value):typeof n.value==='boolean'?String(n.value):Number.isInteger(n.value)?String(n.value)+'.0':String(n.value)})`;
    case 'Identifier':if(n.name==='undefined')return 'V()';if(n.name==='Infinity')return 'V(INFINITY)';if(n.name==='NaN')return 'V(NAN)';if(['Boolean','Number','String'].includes(n.name))return `fn([](const CallArgs& a){return builtin(${q(n.name)},a);})`;return `${lookup(n.name)}.val()`;
    case 'ArrayExpression':return `arr(${argumentsExpr(n.elements)})`;
    case 'ObjectExpression':{
      const field=p=>{const k=p.computed?expr(p.key):`V(${q(p.key.name??p.key.value)})`;return `{${k},${p.method?functionExpr(p.value):expr(p.value)}}`;};
      if(!n.properties.some(p=>p.type==='SpreadElement'))return `${n.properties.every(p=>!p.computed)&&new Set(n.properties.map(p=>p.key.name??p.key.value)).size===n.properties.length?'objKnown<'+(objectSite++)+'>':'obj'}({${n.properties.map(field).join(',')}})`;
      return `([=](){V o=obj();${n.properties.map(p=>p.type==='SpreadElement'?`assign(o,${expr(p.argument)});`:`{auto kv=std::pair<V,V>${field(p)};set(o,kv.first,kv.second);}`).join('')}return o;}())`;
    }
    case 'MemberExpression':if(n.object.type==='Identifier'&&n.object.name==='Math'&&n.property.name==='PI')return 'V(3.14159265358979323846)';if(!n.computed)return hotNames.includes(n.property.name)?`hotProp(${expr(n.object)},${hotNames.indexOf(n.property.name)})`:`propKnown<${literal(n.property.name).slice(8)}>(${expr(n.object)},${literal(n.property.name)}.string())`;return `get(Args{${expr(n.object)},${key(n)}})`;
    case 'FunctionExpression':case 'ArrowFunctionExpression':return functionExpr(n);
    case 'CallExpression':{
      const c=n.callee;
      if(c.type==='MemberExpression'&&!c.computed&&c.object.type==='Identifier'&&['Math','Object','Array','JSON'].includes(c.object.name))return `builtin(${q(c.object.name+'.'+c.property.name)},${argumentsExpr(n.arguments).replace(/^Args\{/,'CallArgs{')})`;
      if(c.type==='Identifier'&&['Boolean','Number','String'].includes(c.name))return `builtin(${q(c.name)},${argumentsExpr(n.arguments).replace(/^Args\{/,'CallArgs{')})`;
      if(c.type==='Identifier'&&natives.has(c.name)&&lookup(c.name)===globals.get(c.name))return `${c.name}(${argumentsExpr(n.arguments).replace(/^Args\{/,'CallArgs{')})`;
      if(c.type==='MemberExpression'&&!c.computed&&['map','filter','some','every','find','findIndex','forEach','reduce','sort'].includes(c.property.name)&&n.arguments[0]&&['ArrowFunctionExpression','FunctionExpression'].includes(n.arguments[0].type)){
        const callback=n.arguments[0],direct=functionContent(callback),fallback=functionExpr(callback);
        return `arrayCallbackKnown<Method::M_${c.property.name}>(${argumentsExpr([c.object,...n.arguments.slice(1)]).replace(/^Args\{/,'CallArgs{')},[&](const CallArgs& a)->V ${direct},[&](){return ${fallback};})`;
      }
      if(c.type==='MemberExpression'&&!c.computed&&["toFixed", "split", "includes", "indexOf", "get", "has", "set", "add", "delete", "keys", "values", "entries", "push", "unshift", "shift", "slice", "splice", "concat", "join", "sort", "reduce", "map", "filter", "some", "every", "find", "findIndex", "forEach", "state", "clone"].includes(c.property.name))return `methodKnown<Method::M_${c.property.name}>(${argumentsExpr([c.object,...n.arguments]).replace(/^Args\{/,'CallArgs{')})`;
      if(c.type==='MemberExpression')return `method(${argumentsExpr([c.object,c.computed?c.property:{type:'Literal',value:c.property.name},...n.arguments]).replace(/^Args\{/,'CallArgs{')})`;
      return `call(${argumentsExpr([c,...n.arguments]).replace(/^Args\{/,'CallArgs{')})`;
    }
    case 'NewExpression':return `construct(${q(n.callee.name)},${argumentsExpr(n.arguments).replace(/^Args\{/,'CallArgs{')})`;
    case 'BinaryExpression':if(['<','<=','>','>='].includes(n.operator)&&n.left.type==='CallExpression'&&n.left.callee.type==='Identifier'&&n.left.callee.name==='dist'&&lookup('dist')===globals.get('dist')&&n.left.arguments.length===2){const id={'<':'Lt','<=':'Le','>':'Gt','>=':'Ge'}[n.operator];return `([&](){CallArgs points{${n.left.arguments.map(expr).join(',')}};auto d=measureDistance(points[0],points[1]);V radius=${expr(n.right)};return V(compareDistance<Binary::${id}>(d,radius));}())`;}if(numberOps[n.operator]&&(n.operator!=='+'||isNumber(n)))return `V(${numberExpr(n)})`;return `bin(${q(n.operator)},Args{${expr(n.left)},${expr(n.right)}})`;
    case 'LogicalExpression':return `([=](){V l=${expr(n.left)};return ${n.operator==='&&'?'truth(l)':n.operator==='||'?'!truth(l)':'nullish(l)'}?${expr(n.right)}:l;}())`;
    case 'UnaryExpression':if(['+','-'].includes(n.operator))return `V(${numberExpr(n)})`;return `unary(${q(n.operator)},${expr(n.argument)})`;
    case 'UpdateExpression':return `update(${ref(n.argument)},${n.operator==='++'?1:-1},${n.prefix})`;
    case 'ConditionalExpression':return `(truth(${expr(n.test)})?${expr(n.consequent)}:${expr(n.alternate)})`;
    case 'AssignmentExpression':{
      if(n.left.type==='ArrayPattern'||n.left.type==='ObjectPattern')return `([=](){V rhs=${expr(n.right)};${rawAssign(n.left,'rhs')}return rhs;}())`;
      return `([=](){auto r=${ref(n.left)};${n.operator==='='?'':'V old=r.val();'}V rhs=${expr(n.right)};return r.put(${n.operator==='='?'rhs':`bin(${q(n.operator.slice(0,-1))},Args{old,rhs})`});}())`;
    }
    case 'SequenceExpression':return `([=](){${n.expressions.slice(0,-1).map(e=>expr(e)+';').join('')}return ${expr(n.expressions.at(-1))};}())`;
    case 'TemplateLiteral':return `V(${n.quasis.map((part,i)=>`std::string(${q(part.value.cooked)})`+(i<n.expressions.length?`+str(${expr(n.expressions[i])})`:'' )).join('+')})`;
    default:fail(n);
  }
}
function block(nodes,intro=''){
  const scope=new Map();for(const n of nodes){if(n.type==='VariableDeclaration')n.declarations.forEach(d=>bindPattern(d.id,scope));if(n.type==='FunctionDeclaration')bindPattern(n.id,scope);}
  scopes.push(scope);
  let out='{\n'+[...scope.values()].map(v=>`Var ${v};`).join('\n')+'\n'+intro;
  for(const n of nodes){if(n.type==='FunctionDeclaration')out+=`${lookup(n.id.name)}.set(${functionExpr(n)});\n`;}
  for(const n of nodes)if(n.type!=='FunctionDeclaration')out+=statement(n)+'\n';
  if(intro)out+='return V();\n';
  scopes.pop();return out+'}';
}
function statement(n){switch(n.type){
  case 'BlockStatement':return block(n.body);
  case 'EmptyStatement':return ';';
  case 'ExpressionStatement':return expr(n.expression)+';';
  case 'VariableDeclaration':return n.declarations.map(d=>d.init?rawAssign(d.id,expr(d.init)):'').join('\n');
  case 'ReturnStatement':return `return ${n.argument?expr(n.argument):'V()'};`;
  case 'IfStatement':return `if(truth(${expr(n.test)}))${wrapped(n.consequent)}`+(n.alternate?`else ${wrapped(n.alternate)}`:'');
  case 'WhileStatement':return `while(truth(${expr(n.test)}))${wrapped(n.body)}`;
  case 'DoWhileStatement':return `do ${wrapped(n.body)} while(truth(${expr(n.test)}));`;
  case 'ForStatement':{
    const scope=new Map();if(n.init&&n.init.type==='VariableDeclaration')n.init.declarations.forEach(d=>bindPattern(d.id,scope));scopes.push(scope);
    let out='{'+[...scope.values()].map(v=>`Var ${v};`).join('');
    out+='for('+ (n.init?(n.init.type==='VariableDeclaration'?statement(n.init).replace(/;\n/g,',').replace(/;$/,''):expr(n.init)):'')+';'+(n.test?'truth('+expr(n.test)+')':'true')+';'+(n.update?expr(n.update):'')+')'+wrapped(n.body)+'}';scopes.pop();return out;
  }
  case 'ForOfStatement':case 'ForInStatement':{
    const tmp=`it_${serial++}`,scope=new Map(),p=n.left.type==='VariableDeclaration'?n.left.declarations[0].id:n.left;
    if(n.left.type==='VariableDeclaration')bindPattern(p,scope);
    let iterable=n.type==='ForOfStatement'?`iterate(${expr(n.right)})`:`keys(${expr(n.right)})`;
    scopes.push(scope);const out=`for(V ${tmp}:${iterable}){${[...scope.values()].map(v=>`Var ${v};`).join('')}${rawAssign(p,tmp)}${statement(n.body)}}`;scopes.pop();return out;
  }
  case 'BreakStatement':return 'break;';case 'ContinueStatement':return 'continue;';
  case 'SwitchStatement':{
    const tmp=`sw_${serial++}`;return `{V ${tmp}=${expr(n.discriminant)};`+n.cases.map((c,i)=>(i?'else ':'')+(c.test?`if(eq(${tmp},${expr(c.test)}))`:'')+block(c.consequent.filter(s=>s.type!=='BreakStatement'))).join('')+'}';
  }
  case 'TryStatement':if(n.handler)fail(n);return `{Finally finally_${serial++}{[=]()${statement(n.finalizer)}};${statement(n.block)}}`;
  default:fail(n);
}}
function wrapped(n){return n.type==='BlockStatement'?statement(n):'{'+statement(n)+'}';}
for(const n of body){if(n.type==='VariableDeclaration')n.declarations.forEach(d=>{bindPattern(d.id,globals);if(d.id.type==='Identifier'&&d.init&&['ArrowFunctionExpression','FunctionExpression'].includes(d.init.type))natives.set(d.id.name,d.init);});if(n.type==='FunctionDeclaration'){bindPattern(n.id,globals);natives.set(n.id.name,n);}}
scopes=[globals];
let output='// Generated from the frozen JS by generate.cjs. Do not edit this file directly.\n#include "builtins.h"\nnamespace simulation {\nusing namespace js;\n';
output += [...globals.values()].map(v=>`Var ${v};`).join('\n')+'\n';
output += [...natives.keys()].map(name=>`V ${name}(const CallArgs& a);`).join('\n')+'\n';
function nativeContent(name,n){
  if(name==='assignSlots'){
    const fallback=functionContent(n).slice(1,-1);
    const field=(v,k)=>`propKnown<${literal(k).slice(8)}>(${v},${literal(k)}.string())`;
    return `{
      V w=arg(a,0),pack=arg(a,1),c=arg(a,2),f=${field('c','f')},ms=${field('c','ms')},A=${field('c','A')},melee=${field('c','melee')},ranged=${field('c','ranged')},art=${field('c','art')},shape=${field('c','shape')};
      V ax=${field('A','ax')},ay=${field('A','ay')},sync=${field('f','syncRadius')},sideMargin=${field('f','zoneSideMargin')},behind=${field('f','zoneBehind')},depth=${field('f','zoneDepth')};
      bool numeric=ax.tag==V::Number&&ay.tag==V::Number&&hotProp(A,0).tag==V::Number&&hotProp(A,1).tag==V::Number&&sync.tag==V::Number&&sideMargin.tag==V::Number&&behind.tag==V::Number&&depth.tag==V::Number;
      for(V list:{melee,ranged,art})for(V u:iterate(list))numeric=numeric&&hotProp(u,0).tag==V::Number&&hotProp(u,1).tag==V::Number;
      V sm=${field('shape','melee')},sr=${field('shape','ranged')},sa=${field('shape','artillery')};
      for(V slots:{sm,sr,sa})for(V slot:iterate(slots))numeric=numeric&&${field('slot','l')}.tag==V::Number&&${field('slot','d')}.tag==V::Number;
      if(numeric){
        double px=-ay.n,py=ax.n;
        auto lat=[A,px,py](V u){return (num(hotProp(u,0))-num(hotProp(A,0)))*px+(num(hotProp(u,1))-num(hotProp(A,1)))*py;};
        auto dep=[A](V u){return -((num(hotProp(u,0))-num(hotProp(A,0)))*num(${field('A','ax')})+(num(hotProp(u,1))-num(hotProp(A,1)))*num(${field('A','ay')}));};
        auto place=[&](V list,V slots){Args members=iter(list),order=iter(slots);
          std::stable_sort(members.begin(),members.end(),[&](V a,V b){double d=lat(a)-lat(b);if(d==0||std::isnan(d))d=dep(a)-dep(b);return d<0;});
          std::stable_sort(order.begin(),order.end(),[&](V a,V b){double d=num(${field('a','l')})-num(${field('b','l')});if(d==0||std::isnan(d))d=num(${field('a','d')})-num(${field('b','d')});return d<0;});
          for(size_t i=0;i<members.size();++i){V u=members[i],slot=i<order.size()?order[i]:V();double d=num(${field('slot','d')}),l=num(${field('slot','l')});
            hotSet(u,27,V(num(hotProp(A,0))-num(${field('A','ax')})*d+px*l));hotSet(u,28,V(num(hotProp(A,1))-num(${field('A','ay')})*d+py*l));set(u,${literal('hasSlot')},V(true));
          }
        };
        place(melee,sm);place(ranged,sr);place(art,sa);
        double off=0;for(V m:iterate(ms))off=maxNumber(off,lengthXY(num(hotProp(m,27))-num(hotProp(m,0)),num(hotProp(m,28))-num(hotProp(m,1))));
        set(pack,${literal('formed')},V(off<sync.n||(truth(${field('pack','formed')})&&off<sync.n*4)));
        double minL=INFINITY,maxL=-INFINITY,minD=INFINITY,backD=-INFINITY;
        for(V slots:{sm,sr,sa})for(V slot:iterate(slots)){double l=num(${field('slot','l')}),d=num(${field('slot','d')});minL=minNumber(minL,l);maxL=maxNumber(maxL,l);minD=minNumber(minD,d);backD=maxNumber(backD,d);}
        minL-=sideMargin.n;maxL+=sideMargin.n;backD+=behind.n;
        double rcx=num(hotProp(A,0)),rcy=num(hotProp(A,1));if(!ranged.p->items.empty()){rcx=0;rcy=0;for(V r:iterate(ranged)){rcx+=num(hotProp(r,0));rcy+=num(hotProp(r,1));}rcx/=ranged.p->items.size();rcy/=ranged.p->items.size();}
        V cover=obj({{${literal('x')},V(rcx)},{${literal('y')},V(rcy)},{${literal('r')},V(num(reachOf({w,hotProp(pack,7),${literal('ranged')}}))*num(${field('f','coverFraction')}))}});
        set(pack,${literal('zone')},obj({{${literal('front')},V(minD-depth.n)},{${literal('back')},V(backD)},{${literal('minL')},V(minL)},{${literal('maxL')},V(maxL)},{${literal('cover')},cover}}));
        auto zone=[=](V h){if(lengthXY(num(hotProp(h,0))-rcx,num(hotProp(h,1))-rcy)>num(reachOf({w,hotProp(pack,7),${literal('ranged')}}))*num(${field('f','coverFraction')}))return false;double d=dep(h),l=lat(h);return d>=minD-num(${field('f','zoneDepth')})&&d<=backD&&l>=minL&&l<=maxL;};
        V inZone=fnValues([=](const CallArgs& a){return V(zone(arg(a,0)));},{w,pack,f,A});set(pack,${literal('inZone')},inZone);
        Args soft;for(V m:iterate(ms))if(!truth(get(${globals.get('MELEE')}.val(),hotProp(m,8))))soft.push_back(m);V oursSoft=arr(std::move(soft));
        V threatens=fnValues([=](const CallArgs& a){V h=arg(a,0);if(dep(h)>minD)return V(true);
          V chargeT=${field('h','chargeT')};if(num(${field('h','chargeEnd')})>num(hotProp(w,24))&&truth(chargeT)&&!truth(get(${globals.get('MELEE')}.val(),hotProp(chargeT,8))))return V(true);
          V target=hotProp(h,4);if(truth(target)&&truth(hotProp(target,5))&&eq(hotProp(target,7),hotProp(pack,7))&&!truth(get(${globals.get('MELEE')}.val(),hotProp(target,8)))&&num(gap({h,target}))<40)return V(true);
          V isMelee=get(${globals.get('MELEE')}.val(),hotProp(h,8));if(!truth(isMelee))return isMelee;for(V m:iterate(oursSoft))if(distanceXY(m,h)<num(${field('f','peelRadius')}))return V(true);return V(false);
        },{A,w,pack,f,oursSoft});set(pack,${literal('threatens')},threatens);
        V latFn=fnValues([=](const CallArgs& a){return V(lat(arg(a,0)));},{A}),depFn=fnValues([=](const CallArgs& a){return V(dep(arg(a,0)));},{A});
        assign(c,obj({{${literal('px')},V(px)},{${literal('py')},V(py)},{${literal('lat')},latFn},{${literal('dep')},depFn},{${literal('minL')},V(minL)},{${literal('maxL')},V(maxL)},{${literal('minD')},V(minD)},{${literal('backD')},V(backD)},{${literal('inZone')},inZone}}));return V();
      }
      ${fallback}
    }`;
  }
  if(name==='separate'){
    const fallback=functionContent(n).slice(1,-1);
    return `{
      V w=arg(a,0),units=hotProp(w,19),o=hotProp(w,20),width=propKnown<${literal('width').slice(8)}>(o,${literal('width')}.string()),height=propKnown<${literal('height').slice(8)}>(o,${literal('height')}.string());
      struct Body{V unit;double x,y,r;};std::vector<Body> bodies;bool numeric=width.tag==V::Number&&height.tag==V::Number;
      for(V u:iterate(units))if(truth(hotProp(u,5))){V x=hotProp(u,0),y=hotProp(u,1),r=hotProp(u,10);numeric=numeric&&x.tag==V::Number&&y.tag==V::Number&&r.tag==V::Number;bodies.push_back({u,x.tag==V::Number?x.n:0,y.tag==V::Number?y.n:0,r.tag==V::Number?r.n:0});}
      if(numeric){
        double cell=num(${globals.get('SEP_CELL')}.val());size_t count=bodies.size();
        std::unordered_map<V,std::vector<size_t>,ValueHash,ValueEqual> grid;grid.reserve(count);
        std::vector<double> px(count,0),py(count,0);
        for(size_t i=0;i<count;++i){auto& u=bodies[i];set(u.unit,${literal('_si')},V(double(i)));grid[V(std::floor(u.x/cell)*4096+std::floor(u.y/cell))].push_back(i);}
        for(size_t i=0;i<count;++i){auto& a=bodies[i];double cx=std::floor(a.x/cell),cy=std::floor(a.y/cell);
          for(int ox=-1;ox<=1;++ox)for(int oy=-1;oy<=1;++oy){auto hit=grid.find(V((cx+ox)*4096+cy+oy));if(hit==grid.end())continue;
            for(size_t j:hit->second){if(j<=i)continue;auto& b=bodies[j];double dx=b.x-a.x,dy=b.y-a.y,d=lengthXY(dx,dy),m=a.r+b.r;if(d>=m||d==0)continue;
              double push=(m-d)/2,nx=dx/d*push,ny=dy/d*push;px[i]-=nx;py[i]-=ny;px[j]+=nx;py[j]+=ny;
            }
          }
        }
        for(size_t i=0;i<count;++i){auto& u=bodies[i];hotSet(u.unit,0,V(clampNumber(u.x+px[i],u.r,width.n-u.r)));hotSet(u.unit,1,V(clampNumber(u.y+py[i],u.r,height.n-u.r)));lgMoved({u.unit});}
        V moves=${globals.get('MOVES')}.val();set(moves,${literal('n')},V(num(propKnown<${literal('n').slice(8)}>(moves,${literal('n')}.string()))+1));return V();
      }
      ${fallback}
    }`;
  }
  if(name==='nearest')return `{
    V from=arg(a,0),list=arg(a,1),filter=arg(a,2),best(nullptr);double bestSquare=INFINITY,bestLinear=INFINITY;bool ordinary=true;
    for(V u:iterate(list)){
      if(eq(u,from)||(truth(filter)&&!truth(call(filter,{u}))))continue;
      DistanceMeasure d=measureDistance(u,from);bool closer;
      if(ordinary&&d.ordinary)closer=d.square<bestSquare;
      else closer=(d.ordinary?std::sqrt(d.square):d.linear)<(ordinary?std::sqrt(bestSquare):bestLinear);
      if(closer){ordinary=d.ordinary;bestSquare=d.square;bestLinear=d.linear;best=u;}
    }return best;
  }`;
  if(name==='lineBlocker')return `{
    V w=arg(a,0),b=arg(a,3),shooter=arg(a,4);double ax=num(arg(a,1)),ay=num(arg(a,2));
    double dx=num(hotProp(b,0))-ax,dy=num(hotProp(b,1))-ay,L=lengthXY(dx,dy);if(L<1)return V(nullptr);
    double nx=dx/L,ny=dy/L,bt=L-num(hotProp(b,10));V best(nullptr);
    V g=propKnown<${literal('_lg').slice(8)}>(w,${literal('_lg')}.string());if(!truth(g)){lgBuild({w});g=propKnown<${literal('_lg').slice(8)}>(w,${literal('_lg')}.string());}
    double bx=num(hotProp(b,0)),by=num(hotProp(b,1)),cell=num(${globals.get('LG')}.val());
    double x0=std::floor((minNumber(ax,bx)-12)/cell),x1=std::floor((maxNumber(ax,bx)+12)/cell);
    double y0=std::floor((minNumber(ay,by)-12)/cell),y1=std::floor((maxNumber(ay,by)+12)/cell);
    for(double cx=x0;cx<=x1;++cx)for(double cy=y0;cy<=y1;++cy){
      V c=methodKnown<Method::M_get>(g,{V(cx*4096+cy)});if(!truth(c))continue;
      for(V u:iterate(c)){
        if(!truth(hotProp(u,5))||eq(u,b)||eq(u,shooter))continue;
        double px=num(hotProp(u,0))-ax,py=num(hotProp(u,1))-ay,t=px*nx+py*ny;
        if(t<=0||t>bt||(t==bt&&!(truth(best)&&truth(binary<Binary::Lt>({hotProp(u,6),hotProp(best,6)})))))continue;
        if(std::abs(px*ny-py*nx)<num(hotProp(u,10))+1.5){bt=t;best=u;}
      }
    }return best;
  }`;
  if(name==='len')return '{return V(lengthXY(num(arg(a,0)),num(arg(a,1))));}';
  if(name==='dist')return '{return V(distanceXY(arg(a,0),arg(a,1)));}';
  if(name==='gap')return '{double d=distanceXY(arg(a,0),arg(a,1));d-=num(hotProp(arg(a,0),10));d-=num(hotProp(arg(a,1),10));return V(d);}';
  return functionContent(n);
}
for(const n of body){let name,fun;if(n.type==='FunctionDeclaration'){name=n.id.name;fun=n;}else if(n.type==='VariableDeclaration'){
  for(const d of n.declarations)if(d.id.type==='Identifier'&&natives.has(d.id.name)){output+=`// JS line ${d.loc.start.line}\nV ${d.id.name}(const CallArgs& a) ${nativeContent(d.id.name,d.init)}\n`;}
}if(fun)output+=`// JS line ${n.loc.start.line}\nV ${name}(const CallArgs& a) ${nativeContent(name,fun)}\n`;}
output+='void initialize(){\n';
for(const [name] of natives)output+=`${globals.get(name)}.set(fn(${name}));\n`;
for(const n of body){if(n.type==='FunctionDeclaration')continue;if(n.type==='VariableDeclaration')for(const d of n.declarations){if(d.init&&!natives.has(d.id.name))output+=`// JS line ${d.loc.start.line}\n`+rawAssign(d.id,expr(d.init))+'\n';}else output+=statement(n)+'\n';}
output+='}\nArgs roots(){return Args{'+[...globals.values()].map(v=>v+'.val()').join(',')+'};}\n} // namespace simulation\n';
output=output.replace(/get\(Args\{/g,'get({').replace(/bin\(("[^"\n]*"),Args\{/g,'bin($1,{');
output=output.replace(/\[=\]\(\)\{/g,'[&](){');
output=output.replace(/Args r\{/g,'CallArgs r{');
const globalBindings=new Set(globals.values());
output=output.replace(/Var (v_\w+_\d+);/g,(full,name)=>capturedBindings.has(name)||globalBindings.has(name)?full:`Local ${name};`);
const binaryIds={"===": "StrictEq", "!==": "StrictNe", "+": "Add", "-": "Sub", "*": "Mul", "/": "Div", "%": "Mod", "**": "Pow", "==": "Eq", "!=": "Ne", "<": "Lt", ">": "Gt", "<=": "Le", ">=": "Ge", "|": "Or", "&": "And", "^": "Xor", ">>>": "Ushr", ">>": "Shr", "<<": "Shl"};
const unaryIds={"!": "Not", "+": "Plus", "-": "Minus", "~": "BitNot", "void": "Void", "typeof": "Typeof"};
const builtinIds={"Math.PI": "Math_PI", "Math.sin": "Math_sin", "Math.cos": "Math_cos", "Math.atan2": "Math_atan2", "Math.sqrt": "Math_sqrt", "Math.abs": "Math_abs", "Math.floor": "Math_floor", "Math.ceil": "Math_ceil", "Math.round": "Math_round", "Math.min": "Math_min", "Math.max": "Math_max", "Math.hypot": "Math_hypot", "Boolean": "Boolean", "Number": "Number", "String": "String", "Object.assign": "Object_assign", "Object.keys": "Object_keys", "Object.values": "Object_values", "Object.entries": "Object_entries", "Object.fromEntries": "Object_fromEntries", "Array.isArray": "Array_isArray", "Array.from": "Array_from", "JSON.stringify": "JSON_stringify", "JSON.parse": "JSON_parse"};
output=output.replace(/bin\(("[^"\n]*"),/g,(_,op)=>`binary<Binary::${binaryIds[JSON.parse(op)]}>(`);
output=output.replace(/unary\(("[^"\n]*"),/g,(_,op)=>`unaryKnown<Unary::${unaryIds[JSON.parse(op)]}>(`);
output=output.replace(/builtin\(("[^"\n]*"),/g,(_,name)=>`builtinKnown<Builtin::${builtinIds[JSON.parse(name)]}>(`);
output=output.replace(/V\(("(?:[^"\\]|\\.)*")\)/g,(_,value)=>literal(JSON.parse(value)));
const literalDecls=[...literalPool].map(([value,name])=>`const V ${name}=V(${q(value)});`).join('\n')+'\n';
output=output.replace('using namespace js;\n','using namespace js;\n'+literalDecls);
output=output.replace('Args roots(){return Args{','Args roots(){return Args{'+[...literalPool.values()].join(',')+',');
output=output.replace(/[ \t]+$/gm,'');
fs.mkdirSync(path.join(__dirname,'src'),{recursive:true});fs.writeFileSync(path.join(__dirname,'src/formation_sim.cpp'),output);
fs.writeFileSync(path.join(__dirname,'src/formation_sim.h'),'#pragma once\n#include "js_value.h"\nnamespace simulation {\nvoid initialize();js::Args roots();\n'+[...natives.keys()].map(name=>`js::V ${name}(const js::CallArgs& a);`).join('\n')+'\n}\n');
console.log(`Generated ${natives.size} named C++ functions in original source order.`);
