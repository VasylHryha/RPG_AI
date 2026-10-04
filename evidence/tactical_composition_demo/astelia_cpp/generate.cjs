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
let serial=0, depth=0;
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
function ref(n){if(n.type==='Identifier')return `Ref(${lookup(n.name)})`;if(n.type==='MemberExpression'){if(!n.computed&&hotNames.includes(n.property.name))return `Ref(${expr(n.object)},${hotNames.indexOf(n.property.name)})`;return `([=](){Args r{${expr(n.object)},${key(n)}};return Ref(r[0],r[1]);}())`;}fail(n);}
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
function expr(n) {
  switch(n.type){
    case 'Literal':return n.value===null?'V(nullptr)':`V(${typeof n.value==='string'?q(n.value):typeof n.value==='boolean'?String(n.value):Number.isInteger(n.value)?String(n.value)+'.0':String(n.value)})`;
    case 'Identifier':if(n.name==='undefined')return 'V()';if(n.name==='Infinity')return 'V(INFINITY)';if(n.name==='NaN')return 'V(NAN)';if(['Boolean','Number','String'].includes(n.name))return `fn([](const CallArgs& a){return builtin(${q(n.name)},a);})`;return `${lookup(n.name)}.val()`;
    case 'ArrayExpression':return `arr(${argumentsExpr(n.elements)})`;
    case 'ObjectExpression':{
      const field=p=>{const k=p.computed?expr(p.key):`V(${q(p.key.name??p.key.value)})`;return `{${k},${p.method?functionExpr(p.value):expr(p.value)}}`;};
      if(!n.properties.some(p=>p.type==='SpreadElement'))return `obj({${n.properties.map(field).join(',')}})`;
      return `([=](){V o=obj();${n.properties.map(p=>p.type==='SpreadElement'?`assign(o,${expr(p.argument)});`:`{auto kv=std::pair<V,V>${field(p)};set(o,kv.first,kv.second);}`).join('')}return o;}())`;
    }
    case 'MemberExpression':if(n.object.type==='Identifier'&&n.object.name==='Math'&&n.property.name==='PI')return 'V(3.14159265358979323846)';if(!n.computed)return hotNames.includes(n.property.name)?`hotProp(${expr(n.object)},${hotNames.indexOf(n.property.name)})`:`prop(${expr(n.object)},${q(n.property.name)})`;return `get(Args{${expr(n.object)},${key(n)}})`;
    case 'FunctionExpression':case 'ArrowFunctionExpression':return functionExpr(n);
    case 'CallExpression':{
      const c=n.callee;
      if(c.type==='MemberExpression'&&!c.computed&&c.object.type==='Identifier'&&['Math','Object','Array','JSON'].includes(c.object.name))return `builtin(${q(c.object.name+'.'+c.property.name)},${argumentsExpr(n.arguments).replace(/^Args\{/,'CallArgs{')})`;
      if(c.type==='Identifier'&&['Boolean','Number','String'].includes(c.name))return `builtin(${q(c.name)},${argumentsExpr(n.arguments).replace(/^Args\{/,'CallArgs{')})`;
      if(c.type==='Identifier'&&natives.has(c.name)&&lookup(c.name)===globals.get(c.name))return `${c.name}(${argumentsExpr(n.arguments).replace(/^Args\{/,'CallArgs{')})`;
      if(c.type==='MemberExpression')return `method(${argumentsExpr([c.object,c.computed?c.property:{type:'Literal',value:c.property.name},...n.arguments]).replace(/^Args\{/,'CallArgs{')})`;
      return `call(${argumentsExpr([c,...n.arguments]).replace(/^Args\{/,'CallArgs{')})`;
    }
    case 'NewExpression':return `construct(${q(n.callee.name)},${argumentsExpr(n.arguments).replace(/^Args\{/,'CallArgs{')})`;
    case 'BinaryExpression':return `bin(${q(n.operator)},Args{${expr(n.left)},${expr(n.right)}})`;
    case 'LogicalExpression':return `([=](){V l=${expr(n.left)};return ${n.operator==='&&'?'truth(l)':n.operator==='||'?'!truth(l)':'nullish(l)'}?${expr(n.right)}:l;}())`;
    case 'UnaryExpression':return `unary(${q(n.operator)},${expr(n.argument)})`;
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
    let iterable=n.type==='ForOfStatement'?`iter(${expr(n.right)})`:`keys(${expr(n.right)})`;
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
for(const n of body){let name,fun;if(n.type==='FunctionDeclaration'){name=n.id.name;fun=n;}else if(n.type==='VariableDeclaration'){
  for(const d of n.declarations)if(d.id.type==='Identifier'&&natives.has(d.id.name)){output+=`// JS line ${d.loc.start.line}\nV ${d.id.name}(const CallArgs& a) ${functionContent(d.init)}\n`;}
}if(fun)output+=`// JS line ${n.loc.start.line}\nV ${name}(const CallArgs& a) ${functionContent(fun)}\n`;}
output+='void initialize(){\n';
for(const [name] of natives)output+=`${globals.get(name)}.set(fn(${name}));\n`;
for(const n of body){if(n.type==='FunctionDeclaration')continue;if(n.type==='VariableDeclaration')for(const d of n.declarations){if(d.init&&!natives.has(d.id.name))output+=`// JS line ${d.loc.start.line}\n`+rawAssign(d.id,expr(d.init))+'\n';}else output+=statement(n)+'\n';}
output+='}\nArgs roots(){return Args{'+[...globals.values()].map(v=>v+'.val()').join(',')+'};}\n} // namespace simulation\n';
output=output.replace(/get\(Args\{/g,'get({').replace(/bin\(("[^"\n]*"),Args\{/g,'bin($1,{');
output=output.replace(/\[=\]\(\)\{/g,'[&](){');
output=output.replace(/Args r\{/g,'CallArgs r{');
const globalBindings=new Set(globals.values());
output=output.replace(/Var (v_\w+_\d+);/g,(full,name)=>capturedBindings.has(name)||globalBindings.has(name)?full:`Local ${name};`);
fs.mkdirSync(path.join(__dirname,'src'),{recursive:true});fs.writeFileSync(path.join(__dirname,'src/formation_sim.cpp'),output);
fs.writeFileSync(path.join(__dirname,'src/formation_sim.h'),'#pragma once\n#include "js_value.h"\nnamespace simulation {\nvoid initialize();js::Args roots();\n'+[...natives.keys()].map(name=>`js::V ${name}(const js::CallArgs& a);`).join('\n')+'\n}\n');
console.log(`Generated ${natives.size} named C++ functions in original source order.`);
