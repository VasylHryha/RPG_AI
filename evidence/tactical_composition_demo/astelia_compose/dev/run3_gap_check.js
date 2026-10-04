// Where does elite's advantage come from? Each profile on the run-3 selection battles (32), vs elite opponents without artyRollout.
const path=require('path'),fs=require('fs'),os=require('os');const {fork}=require('child_process');
const SNAP=''+path.join(__dirname,"..","..","astelia_snapshot")+'';
const S=require(path.join(SNAP,'formation_sim.js'));S.setNet(JSON.parse(fs.readFileSync(path.join(SNAP,'bc_net.json'))));
const ENEMY={skills:Object.fromEntries(Object.entries(S.LEVELS.elite.skills).filter(([k])=>k!=='artyRollout'))};
if(process.env.W){process.on('message',t=>{const o=Object.assign({seed:t.seed,scenario:'mirror',duration:150,abilities:true,swapSides:t.swap,rules:'game'},S.enemyOf(t.opp));o.ai=[t.profile,ENEMY];const t0=Date.now();const r=S.run('reactive',o);process.send(Object.assign(t,{m:r.survivors-r.enemySurvivors,ms:Date.now()-t0}));});return;}
const run=require('./run3_seq.json');
const B=run.race_order.map(s=>{const [opp,seed,swap]=s.split('|');return {opp,seed:+seed,swap:swap==='true'};});
const E=S.LEVELS.elite, noRoll=Object.fromEntries(Object.entries(E.skills).filter(([k])=>k!=='artyRollout'));
const found=run.final.profile;
const P={
 found: found,
 'elite skills (no rollout), alone': {brain:'alone',lookahead:null,skills:Object.assign({},S.LEVELS.novice.skills,noRoll)},
 'elite skills (no rollout), rules+wide line': {brain:'rules',lookahead:null,formation:{preset:'wide line'},skills:Object.assign({},S.LEVELS.novice.skills,noRoll)},
 'elite no lookahead, no rollout (oblique)': {brain:'rules',lookahead:null,formation:E.formation,skills:noRoll},
 'elite no lookahead (with rollout)': {brain:'rules',lookahead:null,formation:E.formation,skills:E.skills},
 'found + rules + wide line': Object.assign({},found,{brain:'rules',formation:{preset:'wide line'}}),
 'found + formation + wide line': Object.assign({},found,{brain:'formation',formation:{preset:'wide line'}}),
 'elite-fast (full, with lookahead)': {level:'elite-fast'},
};
const tasks=[];for(const [name,profile] of Object.entries(P))for(const b of B)tasks.push(Object.assign({name,profile},b));
const pool=[];for(let i=0;i<os.cpus().length;i++)pool.push(fork(__filename,[],{env:Object.assign({},process.env,{W:'1'})}));
const out=[],q=tasks.slice();let live=pool.length;
for(const ch of pool){const nx=()=>{if(q.length)ch.send(q.shift());else if(--live===0)done();};ch.on('message',m=>{out.push(m);nx();});nx();}
function done(){const by={};for(const r of out)(by[r.name]=by[r.name]||[]).push(r);
const f=Object.fromEntries(by.found.map(r=>[r.opp+r.seed+r.swap,r.m]));
for(const [n,v] of Object.entries(by)){const m=v.reduce((a,x)=>a+x.m,0)/v.length;const d=v.map(r=>r.m-f[r.opp+r.seed+r.swap]);const dm=d.reduce((a,x)=>a+x,0)/d.length;const sd=Math.sqrt(d.reduce((a,x)=>a+(x-dm)**2,0)/(d.length-1));
console.log(n.padEnd(46),'margin',m.toFixed(2).padStart(7),' vs found',dm.toFixed(2).padStart(7),'se',(sd/Math.sqrt(d.length)).toFixed(2),' s/fight',(v.reduce((a,x)=>a+x.ms,0)/v.length/1000).toFixed(1));}
for(const c of pool)c.kill();}
