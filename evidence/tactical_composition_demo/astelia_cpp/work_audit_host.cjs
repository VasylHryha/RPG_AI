// Instrument a development-only in-memory copy. The pinned snapshot is untouched.
'use strict';
const fs=require('fs'), path=require('path'), Module=require('module'), crypto=require('crypto');
const filename=path.resolve(__dirname,'../astelia_snapshot/formation_sim.js');
const original=fs.readFileSync(filename,'utf8');
const expected='85b16e9b84b42b831dd2e64a7055474b6df902e4c1ffd635e6670fc6fb665733';
if(crypto.createHash('sha256').update(original).digest('hex')!==expected) throw Error('frozen source changed');
const parser=new Module('acorn');
parser._compile(process.binding('natives')['internal/deps/acorn/acorn/dist/acorn'],'acorn.js');
const ast=parser.exports.parse(original,{ecmaVersion:2022});
const body=ast.body[0].expression.callee.body.body;
const audit={executed_fights:0,executed_steps:0,branch_steps:0,forks:0,unit_actions:0,
             projectile_steps:0,search_calls:0,inference_calls:0,artillery_rollouts:0,candidate_models:0,
             fork_settings:{},cache_hits:0};
const patches=[];
function patch(name,edit) {
  const node=body.find(n=>n.type==='FunctionDeclaration'&&n.id.name===name);
  if(!node) throw Error('missing audit function '+name);
  patches.push({start:node.start,end:node.end,text:edit(original.slice(node.start,node.end))});
}
function once(text,needle,replacement) {
  if(text.split(needle).length!==2) throw Error('audit insertion is not unique: '+needle);
  return text.replace(needle,replacement);
}
patch('step',text=>{
  text=once(text,'function step(w) {','function step(w) { if(w.forked) __nativeAudit.branch_steps++;');
  text=once(text,'for (const u of order) {\n\t\tif (!u.alive) continue;',
    'for (const u of order) {\n\t\tif (!u.alive) continue; __nativeAudit.unit_actions++;');
  return once(text,'for (const s of w.shots) {','for (const s of w.shots) { __nativeAudit.projectile_steps++;');
});
patch('fork',text=>once(text,'function fork(w, extraOpts) {',
  'function fork(w, extraOpts) { __nativeAudit.forks++; const auditDt=(extraOpts&&extraOpts.dt)||w.o.dt; const auditH=((extraOpts&&extraOpts.duration)??w.o.duration)-w.t; const auditKey=auditDt+"/"+auditH; __nativeAudit.fork_settings[auditKey]=(__nativeAudit.fork_settings[auditKey]||0)+1;'));
patch('bcPredict',text=>text.replace('{','{ __nativeAudit.inference_calls++;'));
patch('artyOutcome',text=>text.replace('{','{ __nativeAudit.artillery_rollouts++;'));
patch('lookahead',text=>{
  text=once(text,'const hp = (list) =>','__nativeAudit.search_calls++; const hp = (list) =>');
  return once(text,'const playout = (plan, model) => {','const playout = (plan, model) => { __nativeAudit.candidate_models++;');
});
let instrumented=original;
for(const p of patches.sort((a,b)=>b.start-a.start)) instrumented=instrumented.slice(0,p.start)+p.text+instrumented.slice(p.end);
instrumented=once(instrumented,"'use strict';","'use strict'; const __nativeAudit=globalThis.__asteliaNativeAudit;");
globalThis.__asteliaNativeAudit=audit;
const copy=new Module(filename,module);copy.filename=filename;copy.paths=Module._nodeModulePaths(path.dirname(filename));
copy._compile(instrumented,filename);require.cache[filename]=copy;
const sim=copy.exports,create=sim.create,step=sim.step;
sim.create=(...args)=>{audit.executed_fights++;return create(...args);};
sim.step=(...args)=>{audit.executed_steps++;return step(...args);};
audit.source_sha256=expected;
audit.instrumented_sha256=crypto.createHash('sha256').update(instrumented).digest('hex');
audit.scope='development_work_audit';
require('./js_host.cjs');
process.on('exit',()=>process.stderr.write(JSON.stringify(audit)+'\n'));
