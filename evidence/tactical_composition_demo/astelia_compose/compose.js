// Bottom-up composition on the pinned Astelia formation sandbox (../astelia_snapshot), game rules. Development tool; NOT a recorded run.
// Pieces: the 32 SKILLS (each with its documented values), the brain (alone -> formation -> rules) and the formation shape.
// Start: the hand-built 'novice' level. Search: beam (width BEAM) over single changes, racing (all candidates on the short battle
// set, the best RACE_TOP also on the long one), acceptance only if the paired mean gain over the current assembly is above
// max(MIN_GAIN, 2 standard errors). When no single change is accepted for any beam member: random pairs, then triples, of the best
// single changes (the "atoms that only bond with a third" case); each accepted combination whose single parts were all rejected is
// logged as a synergy. Stop when nothing is accepted. Confirmation of the final assembly and of the hand-built levels on fresh seeds.
//
//   node compose.js <out.json> [rounds_cap]          env: SEL_SEEDS, CONF_SEEDS, OPP_SEL, BEAM, RACE_TOP, PAIRS, TRIPLES, MIN_GAIN, NO_CONFIRM
'use strict';
const os = require('os'), fs = require('fs'), path = require('path');
const { fork } = require('child_process');
const SNAP = path.join(__dirname, '..', 'astelia_snapshot');
const S = require(path.join(SNAP, 'formation_sim.js'));
S.setNet(JSON.parse(fs.readFileSync(path.join(SNAP, 'bc_net.json'))));

const env = (k, d) => (process.env[k] !== undefined ? process.env[k] : d);
const SEL_SEEDS = env('SEL_SEEDS', '101,102').split(',').map(Number);
const CONF_SEEDS = env('CONF_SEEDS', '301,302,303').split(',').map(Number);
const OPP_SEL = env('OPP_SEL', 'wolfpack,storm,line,swarm,loose skirmish,box,crescent,alone').split(',');
const BEAM = +env('BEAM', 2), RACE_TOP = +env('RACE_TOP', 8), PAIRS = +env('PAIRS', 30), TRIPLES = +env('TRIPLES', 20), MIN_GAIN = +env('MIN_GAIN', 1.0);

// ---------------------------------------------------------------- one fight (as ai_lab.js, game rules)
function fight({ profile, opp, seed, swap }) {
	const o = Object.assign({ seed, scenario: 'mirror', duration: 150, abilities: true, swapSides: swap, rules: 'game' }, S.enemyOf(opp));
	o.ai = [profile, {}];
	const r = S.run('reactive', o);
	return { m: r.survivors - r.enemySurvivors, win: r.enemySurvivors === 0 && r.survivors > 0 ? 1 : 0 };
}
if (process.env.COMPOSE_WORKER) { process.on('message', (t) => process.send(Object.assign(t, fight(t)))); return; }

// ---------------------------------------------------------------- the pieces
const BRAINS = ['alone', 'formation', 'rules'];
const PRESETS = Object.keys(S.PRESETS);
const VALUES = {};
for (const [k, v] of Object.entries(S.SKILLS)) VALUES[k] = [v.def, v.alt];
for (const lv of Object.values(S.LEVELS)) for (const [k, v] of Object.entries(lv.skills || {})) VALUES[k].push(v);
for (const k of Object.keys(VALUES)) { const seen = new Set(); VALUES[k] = VALUES[k].filter((x) => { const s = JSON.stringify(x); if (seen.has(s)) return false; seen.add(s); return true; }); }
const NOVICE = { brain: 'alone', formation: null, skills: Object.assign({}, S.LEVELS.novice.skills) };
const skillOf = (p, k) => (k in p.skills ? p.skills[k] : S.SKILLS[k].def);
const keyOf = (p) => JSON.stringify([p.brain, p.formation, Object.keys(S.SKILLS).map((k) => skillOf(p, k))]);
const toAi = (p) => Object.assign({ brain: p.brain, lookahead: null, skills: p.skills }, p.formation ? { formation: { preset: p.formation } } : {});
function pieces(p) {   // what differs from novice: the assembly's connected pieces
	const out = [];
	for (const k of Object.keys(S.SKILLS)) if (JSON.stringify(skillOf(p, k)) !== JSON.stringify(skillOf(NOVICE, k))) out.push(`${k}=${JSON.stringify(skillOf(p, k))}`);
	if (p.brain !== 'alone') out.push(`brain=${p.brain}`);
	if (p.formation) out.push(`formation=${p.formation}`);
	return out;
}
function moves(p) {   // every single change
	const out = [];
	for (const k of Object.keys(S.SKILLS)) for (const v of VALUES[k]) if (JSON.stringify(v) !== JSON.stringify(skillOf(p, k))) out.push({ label: `${k}=${JSON.stringify(v)}`, apply: (q) => { q.skills[k] = v; } });
	const bi = BRAINS.indexOf(p.brain);
	for (const b of BRAINS) if (b !== p.brain && Math.abs(BRAINS.indexOf(b) - bi) === 1) out.push({ label: `brain=${b}`, apply: (q) => { q.brain = b; if (b === 'alone') q.formation = null; else if (!q.formation) q.formation = 'line'; } });
	if (p.brain !== 'alone') for (const f of PRESETS) if (f !== p.formation) out.push({ label: `formation=${f}`, apply: (q) => { q.formation = f; } });
	return out;
}
const applyAll = (p, ms) => { const q = { brain: p.brain, formation: p.formation, skills: Object.assign({}, p.skills) }; for (const m of ms) m.apply(q); return q; };

// ---------------------------------------------------------------- the worker pool and paired evaluation with a cache
const pool = []; for (let i = 0; i < os.cpus().length; i++) pool.push(fork(__filename, process.argv.slice(2), { env: Object.assign({}, process.env, { COMPOSE_WORKER: '1' }) }));
function runAll(tasks) {
	return new Promise((resolve) => {
		if (!tasks.length) return resolve([]);
		const out = [], queue = tasks.slice(); let live = pool.length;
		const finish = () => { for (const c of pool) c.removeAllListeners('message'); resolve(out); };
		for (const ch of pool) {
			const next = () => { if (queue.length) ch.send(queue.shift()); else if (--live === 0) finish(); };
			ch.on('message', (m) => { out.push(m); next(); }); next();
		}
	});
}
const battles = (seeds, opps) => opps.flatMap((opp) => seeds.flatMap((seed) => [false, true].map((swap) => ({ opp, seed, swap }))));
const SHORT = battles([SEL_SEEDS[0]], OPP_SEL), LONG = battles(SEL_SEEDS, OPP_SEL);
const cache = new Map();   // keyOf(profile) + battle -> margin
const bkey = (b) => `${b.opp}|${b.seed}|${b.swap}`;
let fights = 0;
async function evaluate(profiles, bs) {
	const tasks = [];
	for (const p of profiles) { const k = keyOf(p); for (const b of bs) if (!cache.has(k + '#' + bkey(b))) { cache.set(k + '#' + bkey(b), null); tasks.push(Object.assign({ profile: toAi(p), pkey: k }, b)); } }
	fights += tasks.length;
	for (const r of await runAll(tasks)) cache.set(r.pkey + '#' + bkey(r), r.m);
}
const margins = (p, bs) => bs.map((b) => cache.get(keyOf(p) + '#' + bkey(b)));
const mean = (a) => a.reduce((x, y) => x + y, 0) / a.length;
function pairedGain(cand, cur, bs) {
	const d = margins(cand, bs).map((x, i) => x - margins(cur, bs)[i]);
	const m = mean(d), sd = Math.sqrt(d.reduce((a, x) => a + (x - m) ** 2, 0) / Math.max(1, d.length - 1));
	return { gain: m, se: sd / Math.sqrt(d.length), n: d.length };
}
const accepted = (g) => g.gain > Math.max(MIN_GAIN, 2 * g.se);

// ---------------------------------------------------------------- search
let rng = 12345;
const rand = () => { rng ^= rng << 13; rng ^= rng >>> 17; rng ^= rng << 5; return ((rng >>> 0) % 1e9) / 1e9; };
async function bestSingles(cur) {
	const ms = moves(cur), cands = ms.map((m) => ({ m, p: applyAll(cur, [m]) }));
	await evaluate([cur, ...cands.map((c) => c.p)], SHORT);
	for (const c of cands) c.short = pairedGain(c.p, cur, SHORT);
	cands.sort((a, b) => b.short.gain - a.short.gain);
	const top = cands.slice(0, RACE_TOP);
	await evaluate([cur, ...top.map((c) => c.p)], LONG);
	for (const c of top) c.long = pairedGain(c.p, cur, LONG);
	return { cands, top };
}
async function combos(cur, singles, k, n) {
	const pool_ = singles.slice(0, 15), tried = new Set(), out = [];
	for (let t = 0; t < n * 5 && out.length < n; t++) {
		const idx = new Set(); while (idx.size < k) idx.add(Math.floor(rand() * pool_.length));
		const ms = [...idx].sort().map((i) => pool_[i].m), lab = ms.map((m) => m.label).join(' + ');
		const labels = ms.map((m) => m.label.split('=')[0]);
		if (tried.has(lab) || new Set(labels).size < labels.length) continue;
		tried.add(lab); out.push({ ms, label: lab, p: applyAll(cur, ms) });
	}
	await evaluate([cur, ...out.map((c) => c.p)], LONG);
	for (const c of out) c.long = pairedGain(c.p, cur, LONG);
	return out.sort((a, b) => b.long.gain - a.long.gain);
}

async function main() {
	const OUT = process.argv[2], CAP = +(process.argv[3] || 40);
	const log = { started: new Date().toISOString(), settings: { SEL_SEEDS, CONF_SEEDS, OPP_SEL, BEAM, RACE_TOP, PAIRS, TRIPLES, MIN_GAIN, rules: 'game', lookahead: 'excluded in this run' },
		snapshot: 'astelia_snapshot/SOURCE.md', rounds: [], synergies: [] };
	const save = () => fs.writeFileSync(OUT, JSON.stringify(log, null, 1));
	let beam = [{ p: NOVICE, path: ['novice'] }];
	await evaluate([NOVICE], LONG);
	for (let round = 1; round <= CAP; round++) {
		const next = [], rec = { round, members: [] };
		for (const b of beam) {
			const { cands, top } = await bestSingles(b.p);
			const acc = top.filter((c) => accepted(c.long)).map((c) => ({ p: c.p, path: b.path.concat(c.m.label), gain: c.long, how: 'single' }));
			const memberRec = { from: b.path[b.path.length - 1], pieces: pieces(b.p).length, score: mean(margins(b.p, LONG)),
				top_singles: top.map((c) => ({ move: c.m.label, gain: +c.long.gain.toFixed(2), se: +c.long.se.toFixed(2) })) };
			if (!acc.length) {   // stuck on single changes: try pairs, then triples (synergy search)
				for (const k of [2, 3]) {
					const cs = await combos(b.p, cands, k, k === 2 ? PAIRS : TRIPLES);
					const ok = cs.filter((c) => accepted(c.long));
					memberRec[`top_${k}`] = cs.slice(0, 5).map((c) => ({ moves: c.label, gain: +c.long.gain.toFixed(2), se: +c.long.se.toFixed(2) }));
					if (ok.length) {
						for (const c of ok.slice(0, BEAM)) {
							acc.push({ p: c.p, path: b.path.concat(c.label), gain: c.long, how: `${k} together` });
							log.synergies.push({ round, from: b.path[b.path.length - 1], combination: c.label, gain: +c.long.gain.toFixed(2), se: +c.long.se.toFixed(2),
								singles: c.ms.map((m) => { const s = cands.find((x) => x.m.label === m.label); return { move: m.label, short_gain: +s.short.gain.toFixed(2) }; }) });
						}
						break;
					}
				}
			}
			rec.members.push(memberRec);
			next.push(...acc);
		}
		if (!next.length) { rec.stopped = 'no single change, pair or triple was accepted for any beam member'; log.rounds.push(rec); save(); break; }
		const seen = new Set();
		beam = next.sort((a, b) => b.gain.gain - a.gain.gain).filter((x) => { const k = keyOf(x.p); if (seen.has(k)) return false; seen.add(k); return true; }).slice(0, BEAM);
		await evaluate(beam.map((x) => x.p), LONG);
		rec.beam = beam.map((x) => ({ path: x.path, pieces: pieces(x.p), n_pieces: pieces(x.p).length, score_long: +mean(margins(x.p, LONG)).toFixed(2), how: x.how }));
		rec.fights_so_far = fights;
		log.rounds.push(rec); save();
		console.log(`round ${round}: best ${rec.beam[0].score_long} with ${rec.beam[0].n_pieces} pieces via ${rec.beam[0].how}: ${rec.beam[0].path.slice(-1)[0]} | fights ${fights}`);
	}
	const final = beam.reduce((a, b) => (mean(margins(a.p, LONG)) >= mean(margins(b.p, LONG)) ? a : b));
	log.final = { path: final.path, pieces: pieces(final.p), n_pieces: pieces(final.p).length, profile: toAi(final.p), score_selection: mean(margins(final.p, LONG)) };
	if (!process.env.NO_CONFIRM) {   // fresh seeds, the whole opponent pool, both sides
		const CONF = battles(CONF_SEEDS, S.POOL);
		const ref = { novice: { level: 'novice' }, regular: { level: 'regular' }, veteran: { level: 'veteran' } };
		const tasks = [];
		for (const b of CONF) { tasks.push(Object.assign({ profile: toAi(final.p), who: 'found' }, b)); for (const [n, a] of Object.entries(ref)) tasks.push(Object.assign({ profile: a, who: n }, b)); }
		const res = await runAll(tasks);
		const by = {}; for (const r of res) (by[r.who] = by[r.who] || []).push(r);
		log.confirmation = Object.fromEntries(Object.entries(by).map(([k, v]) => [k, { margin: +mean(v.map((x) => x.m)).toFixed(2), won: +mean(v.map((x) => x.win)).toFixed(3), n: v.length }]));
		const pk = (r) => `${r.opp}|${r.seed}|${r.swap}`, f = Object.fromEntries(by.found.map((r) => [pk(r), r.m]));
		for (const n of Object.keys(ref)) { const d = by[n].map((r) => f[pk(r)] - r.m); const m = mean(d), sd = Math.sqrt(d.reduce((a, x) => a + (x - m) ** 2, 0) / (d.length - 1)); log.confirmation[`found_minus_${n}`] = { mean: +m.toFixed(2), se: +(sd / Math.sqrt(d.length)).toFixed(2) }; }
	}
	log.fights = fights; log.finished = new Date().toISOString(); save();
	console.log('final', log.final.n_pieces, 'pieces:', log.final.pieces.join(', '));
	if (log.confirmation) console.log('confirmation', JSON.stringify(log.confirmation));
	for (const ch of pool) ch.kill();
}
main().catch((e) => { console.error(e); for (const ch of pool) ch.kill(); process.exit(1); });
