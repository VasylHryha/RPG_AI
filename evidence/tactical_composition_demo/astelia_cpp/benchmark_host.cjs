// Instrument the public host calls, while executing the unchanged frozen sim.
'use strict';
const sim = require('../astelia_snapshot/formation_sim.js');
let fights = 0, steps = 0;
const create = sim.create, step = sim.step;
sim.create = (...args) => { ++fights; return create(...args); };
sim.step = (...args) => { ++steps; return step(...args); };
require('./js_host.cjs');
process.on('exit', () => process.stderr.write(JSON.stringify({executed_fights:fights, executed_steps:steps, cache_hits:0})+'\n'));
