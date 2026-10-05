'use strict';
const fs=require('fs'),crypto=require('crypto'),sim=require('../astelia_snapshot/formation_sim.js');
const source=fs.readFileSync(__dirname+'/../astelia_snapshot/formation_sim.js');
if(crypto.createHash('sha256').update(source).digest('hex')!=='85b16e9b84b42b831dd2e64a7055474b6df902e4c1ffd635e6670fc6fb665733')throw Error('source identity mismatch');
function encode(x,path){if(typeof x==='function')return {native_callback:path};if(Array.isArray(x))return x.map((v,i)=>encode(v,path+'.'+i));if(x&&typeof x==='object')return Object.fromEntries(Object.entries(x).map(([k,v])=>[k,encode(v,path+'.'+k)]));return x;}
const catalog={};for(const [k,v] of Object.entries(sim))if(typeof v!=='function')catalog[k]=encode(v,k);
const data=JSON.stringify(catalog);
fs.writeFileSync(__dirname+'/src/native/catalog_data.h','#pragma once\nnamespace astelia { inline constexpr const char* catalogJSON=R"astelia('+data+')astelia"; }\n');
