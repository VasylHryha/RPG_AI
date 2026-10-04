// Compile frozen authored formation data to ordinary typed C++ assignments.
// No property dictionaries or callback dispatch remain in the simulation.
'use strict';
const fs=require('fs'),path=require('path'),crypto=require('crypto');
const source=path.join(__dirname,'../astelia_snapshot/formation_sim.js');
const hash=crypto.createHash('sha256').update(fs.readFileSync(source)).digest('hex');
if(hash!=='85b16e9b84b42b831dd2e64a7055474b6df902e4c1ffd635e6670fc6fb665733')throw Error('frozen source mismatch');
const sim=require(source);
const cap=s=>s[0].toUpperCase()+s.slice(1);
const enumFields={shape:'Shape',meleeDoctrine:'MeleeDoctrine',autoAttack:'MeleeDoctrine',shooterFocus:'ShooterFocus',artilleryDoctrine:'ArtilleryDoctrine',anchorMode:'AnchorMode',raidTarget:'SoftTarget',flankTarget:'SoftTarget'};
const knobRole={meleeDoctrine:1,autoAttack:1,dive:1,diveMinTargets:1,diveRange:1,maxStrikersPerTarget:1,peelRadius:1,flankForce:1,flankTarget:1,flankWidth:1,flankDepth:1,flankWait:1,raidTarget:1,shooterFocus:2,squadSize:2,laneLeash:2,kiteLeash:2,artilleryDoctrine:3,engagedWeight:3};
const roleNames=['position','melee','ranged','artillery'];
function assignments(data,role=null){let lines=[];
 for(const [k,v] of Object.entries(data)){
  if(k==='preset')continue;
  if(k==='release'){
   const bits=(v||[]).filter(r=>role===null||roleNames[role]===r).reduce((b,r)=>b|(1<<(['melee','ranged','artillery'].indexOf(r))),0);
   if(role===null)lines.push(`f.release=${bits};`);else if(bits)lines.push(`f.release|=${bits};`);
   continue;
  }
  if(role!==null&&(knobRole[k]||0)!==role)continue;
  if(enumFields[k])lines.push(`f.${k}=${enumFields[k]}::${cap(v)};`);
  else if(k==='surroundMelee')lines.push(`f.surroundScreen=${v==='screen'};`);
  else if(typeof v==='boolean'||typeof v==='number')lines.push(`f.${k}=${JSON.stringify(v)};`);
  else throw Error('unsupported authored formation field '+k);
 }
 return lines.join('');
}
const plans=[...new Set([...Object.keys(sim.PLANS),...Object.keys(sim.BRAINS.storm.plans),...Object.keys(sim.BRAINS.wolfpack.plans),...Object.keys(sim.BRAINS.gamepack.plans)])];
let out=`// Generated from frozen formation_sim.js SHA256 ${hash}\n#include "formation.h"\n\nnamespace astelia {\n`;
out+='Formation presetFormation(const std::string& name){Formation f;\n';
for(const [name,v] of Object.entries(sim.PRESETS))out+=`if(name==${JSON.stringify(name)}){${assignments(v)}return f;}\n`;
out+='if(name.empty())return f;throw std::invalid_argument("unknown formation preset: "+name);}\n';
out+='Plan planByName(const std::string& name){\n';
for(const name of plans)out+=`if(name==${JSON.stringify(name)})return Plan::${cap(name)};\n`;
out+='if(name.empty())return Plan::None;throw std::invalid_argument("unknown plan: "+name);}\n';
out+='const char* planName(Plan p){switch(p){\n';
for(const name of plans)out+=`case Plan::${cap(name)}:return ${JSON.stringify(name)};\n`;
out+='default:return "";}}\n';
for(const [table,v] of Object.entries({Main:sim.PLANS,Storm:sim.BRAINS.storm.plans,Wolfpack:sim.BRAINS.wolfpack.plans,Gamepack:sim.BRAINS.gamepack.plans})){
 out+=`static void apply${table}(Formation& f,Plan p,size_t role){switch(p){\n`;
 for(const [name,data] of Object.entries(v)){
  out+=`case Plan::${cap(name)}:switch(role){\n`;
  for(let r=0;r<4;r++)out+=`case ${r}:${assignments(data,r)}break;\n`;
  out+='}break;\n';
 }
 out+='default:break;}}\n';
}
out+='Formation composeFormation(const Formation& base,Brain brain,const Tactics& combo){Formation f=base;f.release=0;for(size_t r=0;r<4;++r){\n';
out+='switch(brain){case Brain::Storm:applyStorm(f,combo.role[r],r);break;case Brain::Wolfpack:applyWolfpack(f,combo.role[r],r);break;case Brain::Gamepack:applyGamepack(f,combo.role[r],r);break;default:applyMain(f,combo.role[r],r);break;}}return f;}\n}\n';
fs.writeFileSync(path.join(__dirname,'src/native/formation_tables.cpp'),out);
console.log(`generated ${Object.keys(sim.PRESETS).length} presets and ${plans.length} named plans`);
