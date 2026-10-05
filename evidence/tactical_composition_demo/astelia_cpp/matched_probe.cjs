'use strict';
const fs=require('fs'),Module=require('module'),path=require('path'),crypto=require('crypto');
let source=fs.readFileSync(__dirname+'/../astelia_snapshot/formation_sim.js','utf8');
if(crypto.createHash('sha256').update(source).digest('hex')!=='85b16e9b84b42b831dd2e64a7055474b6df902e4c1ffd635e6670fc6fb665733')throw Error('source mismatch');
source=source.replace('const api = { triggerAbility','const api = { nearest, bcTop, triggerAbility');
const filename=path.resolve(__dirname,'../astelia_snapshot/formation_sim.js'),copy=new Module(filename,module);copy.filename=filename;copy.paths=Module._nodeModulePaths(path.dirname(filename));copy._compile(source,filename);const sim=copy.exports;
const net=JSON.parse(fs.readFileSync(__dirname+'/../astelia_snapshot/bc_net.json'));sim.setNet(net);
const w=sim.create('alone',{seed:20261005,width:1200,height:800,dt:.03,duration:.3,rules:'game',scenario:'mirror',army:{melee:10,ranged:30,artillery:10},ai:[{level:'novice'},{level:'novice'}]});
w.units.forEach((u,i)=>{let k=i%50;u.x=460+k%10*28+u.team*25;u.y=90+Math.floor(k/10)*75;u.px=u.x;u.py=u.y;u.vx=u.vy=u.svx=u.svy=0;});
function measure(kind,operations,fn){const start=process.hrtime.bigint(),checksum=fn();console.log(JSON.stringify({kind,operations,seconds:Number(process.hrtime.bigint()-start)/1e9,checksum}));}
const sides=[sim.monsters(w),sim.hunters(w)];
measure('geometry',100000,()=>{let sum=0;for(let k=0;k<100000;k++){const u=w.units[k%100],e=sim.nearest(u,sides[1-u.team]);sum+=e?e.id:0;}return sum;});
// The frozen bcPredict dense loops, retaining each output score by a checked
// in-memory extraction rather than replacing inference with a new algorithm.
// Export bcTop's exact shared forward computation; fail on source shape drift.
const original=source.match(/function bcTop\(net, x, k\) \{[\s\S]*?\n\}/)[0];
const body=original.slice(original.indexOf('{')+1,original.indexOf('return sc.map'));
if(!body.includes('const sc = net.W2.map'))throw Error('network extraction mismatch');
const scores=new Function('net','x',body+'return sc;');const x=Array.from({length:46},(_,i)=>(i*17%101-50)/50);
measure('network',20000,()=>{let sum=0;for(let k=0;k<20000;k++){x[0]=(k%101-50)/50;sum+=scores(net,x)[k%13];}return sum;});
let steps=0,units=0,projectiles=0;
for(let j=0;j<30;j++)w.shots.push({x:100,y:700,src:w.units[0],target:w.units[50],dx:1,dy:0,speed:240,left:.5,born:0,aimed:true,dmg:0,pend:0,dodgeable:false});
measure('fork_playout',300,()=>{let sum=0;for(let k=0;k<300;k++){const c=sim.fork(w,{duration:.3,dt:.03});c.forked=true;while(!sim.done(c)){units+=c.units.filter(u=>u.alive).length;projectiles+=c.shots.length;sim.step(c);steps++;}sum+=c.t+sim.monsters(c).length+sim.hunters(c).length;}return sum;});
console.log(JSON.stringify({kind:'fork_work',forks:300,steps,unit_actions:units,projectile_steps:projectiles}));
