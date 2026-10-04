// Frozen JS reference host. Does not patch or instrument the snapshot.
'use strict';
const fs = require('fs');
const readline = require('readline');
const sim = require('../astelia_snapshot/formation_sim.js');
sim.setNet(JSON.parse(fs.readFileSync(__dirname + '/../astelia_snapshot/bc_net.json', 'utf8')));
const fields = ['id', 'team', 'role', 'kind', 'x', 'y', 'hp', 'cd', 'alive'];
function bits(x) {const b=Buffer.alloc(8);b.writeDoubleBE(x);return b.toString('hex');}
function sanitize(v) {
  if (typeof v === 'function') return '[function]';
  if (!v || typeof v !== 'object') return v;
  if (v.units && v.o) return '[world]';
  if (v.id !== undefined && v.alive !== undefined) return {unit:v.id};
  if (v instanceof Map) return {map:[...v].map(([k,x])=>[sanitize(k),sanitize(x)])};
  if (v instanceof Set) return {set:[...v].map(sanitize)};
  if (Array.isArray(v)) return v.map(sanitize);
  return Object.fromEntries(Object.entries(v).filter(([k])=>k!=='net').map(([k,x])=>[k,sanitize(x)]));
}
function state(w, known, debug) {
  for (const u of w.units) known.set(u.id, u);
  return {t:w.t, units:[...known.values()].map(u => {
    const v = Object.fromEntries(fields.filter(k => u[k] !== undefined).map(k => [k,u[k]]));
    v.target = u.target ? u.target.id : null;
    v.bits = Object.fromEntries(['x','y','hp','cd'].map(k=>[k,bits(u[k])]));
    if (debug) v.debug = Object.fromEntries(Object.entries(u).filter(([k])=>k!=='w').map(([k,x])=>[k,sanitize(x)]));
    return v;
  }),bits:bits(w.t), ...(debug ? {debug:{packs:sanitize(w.packs),shots:sanitize(w.shots),shells:sanitize(w.shells),
    fields:sanitize(w.fields),stats:sanitize(w.stats),hitLog:sanitize(w.hitLog),rand:w.rand.state()}} : {})};
}
function fight(req) {
  if (req.operation === 'fixed') return req.value.toFixed(req.digits);
  if (req.operation === 'echo') return req.value;
  if (req.operation === 'keys') return Object.keys(req.value);
  if (req.operation === 'string') return req.method === 'length' ? req.value.length : req.value[req.method](...(req.args || []));
  if (req.operation === 'math') {
    const value = Math[req.name](...req.args);
    return {value,bits:bits(value)};
  }
  if (req.operation === 'rng') {
    // rng is internal: drawOpponents exercises the seed conversions and RNG.
    return sim.drawOpponents(req.seed, req.rounds, req.drawMode || 'any');
  }
  const options = Object.assign({}, req.opponent ? sim.enemyOf(req.opponent) : {}, req.options || {});
  const mode = req.mode || 'alone';
  let tick = 0, w, known = new Map();
  try {
    w = sim.create(mode, options);
    if (req.trace) process.stdout.write(JSON.stringify({step:tick,state:state(w,known,req.debug)})+'\n');
    while (!sim.done(w)) {
      sim.step(w); ++tick;
      if (req.trace) process.stdout.write(JSON.stringify({step:tick,state:state(w,known,req.debug)})+'\n');
    }
    return sim.summary(w);
  } catch(e) { return {error:e.message}; }
}
if (process.argv.includes('--catalog')) {
  console.log(JSON.stringify({POOL:sim.POOL, LEVELS:sim.LEVELS, SKILLS:sim.SKILLS}));
} else {
  const input = readline.createInterface({input:process.stdin,crlfDelay:Infinity});
  input.on('line', line => {
    if (!line.trim()) return;
    try {
      const req = JSON.parse(line);
      console.log(JSON.stringify(Array.isArray(req) ? req.map(fight) : fight(req)));
    } catch(e) { console.log(JSON.stringify({error:e.message})); }
  });
}
