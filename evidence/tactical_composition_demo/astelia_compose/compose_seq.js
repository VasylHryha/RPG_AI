// Bottom-up composition, the fast version (development tool; NOT a recorded run). Same pieces, start, fight and confirmation as compose.js; a different search:
// "one combination after another" (the owner, 2026-10-04) with quick checks.
//   * Racing: a candidate plays the selection battles in stages (STAGES, default 4, 8, 16, 32 fights, both sides of each battle). After every stage but the last
//     it is dropped unless its paired mean gain over the current assembly is above 0; at the last stage it is kept only if the gain is above
//     max(MIN_GAIN, 2 standard errors) (the compose.js acceptance rule). Most changes do nothing or harm and stop after 4 fights.
//   * First improvement: candidates are raced in chunks of CHUNK (to keep every core busy), promising ones first (positive first-stage gain in an earlier
//     round); the first chunk with an accepted candidate gives the next assembly (its best one). No full sweep of every change per round.
//   * When no single change is accepted: a two-step check. Every single change is tried as a first step, INCLUDING ones that hurt alone (run 3 showed the
//     parts of a useful group can each hurt alone), most promising first; on top of each, every second change is raced against the current assembly.
//     The first pair that passes is taken and logged as a synergy (neither part was accepted alone this round). Cap: FIRSTS first steps (default all).
//   * The brain may move to any value in one step (run 3: alone -> formation -> rules crossed a -7.8 valley).
//   * Opponents: ENEMY_LEVEL's skills without the skills in ENEMY_DROP (default: artyRollout, which simulates futures and makes a fight about 20x slower).
//
//   node compose_seq.js <out.json> [rounds_cap]      env: ENEMY_LEVEL, ENEMY_DROP, SEL_SEEDS, CONF_SEEDS, OPP_SEL, STAGES, CHUNK, FIRSTS, MIN_GAIN, SEARCH_SEED, CONF_ELITE, NO_CONFIRM
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
const ENEMY_LEVEL = env('ENEMY_LEVEL', 'elite');
const ENEMY_DROP = env('ENEMY_DROP', 'artyRollout').split(',').filter(Boolean);
const ENEMY = ENEMY_LEVEL ? { skills: Object.fromEntries(Object.entries(S.LEVELS[ENEMY_LEVEL].skills).filter(([k]) => !ENEMY_DROP.includes(k))) } : {};
const STAGES = env('STAGES', '4,8,16,32').split(',').map(Number);
const CHUNK = +env('CHUNK', os.cpus().length), FIRSTS = +env('FIRSTS', 1e9), MIN_GAIN = +env('MIN_GAIN', 1.0);

// ---------------------------------------------------------------- one fight (as compose.js)
function fight({ profile, opp, seed, swap }) {
	const o = Object.assign({ seed, scenario: 'mirror', duration: 150, abilities: true, swapSides: swap, rules: 'game' }, S.enemyOf(opp));
	o.ai = [profile, ENEMY];
	const r = S.run('reactive', o);
	return { m: r.survivors - r.enemySurvivors, win: r.enemySurvivors === 0 && r.survivors > 0 ? 1 : 0 };
}
if (process.env.COMPOSE_WORKER) { process.on('message', (t) => process.send(Object.assign(t, fight(t)))); return; }

// ---------------------------------------------------------------- the pieces (as compose.js)
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
function pieces(p) {
	const out = [];
	for (const k of Object.keys(S.SKILLS)) if (JSON.stringify(skillOf(p, k)) !== JSON.stringify(skillOf(NOVICE, k))) out.push(`${k}=${JSON.stringify(skillOf(p, k))}`);
	if (p.brain !== 'alone') out.push(`brain=${p.brain}`);
	if (p.formation) out.push(`formation=${p.formation}`);
	return out;
}
function moves(p) {
	const out = [];
	for (const k of Object.keys(S.SKILLS)) for (const v of VALUES[k]) if (JSON.stringify(v) !== JSON.stringify(skillOf(p, k))) out.push({ slot: k, label: `${k}=${JSON.stringify(v)}`, apply: (q) => { q.skills[k] = v; } });
	for (const b of BRAINS) if (b !== p.brain) out.push({ slot: 'brain', label: `brain=${b}`, apply: (q) => { q.brain = b; if (b === 'alone') q.formation = null; else if (!q.formation) q.formation = 'line'; } });
	if (p.brain !== 'alone') for (const f of PRESETS) if (f !== p.formation) out.push({ slot: 'formation', label: `formation=${f}`, apply: (q) => { q.formation = f; } });
	return out;
}
const applyAll = (p, ms) => { const q = { brain: p.brain, formation: p.formation, skills: Object.assign({}, p.skills) }; for (const m of ms) m.apply(q); return q; };

// ---------------------------------------------------------------- workers, cache, paired gain (as compose.js)
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
// selection battles in race order: seed by seed, opponents in a fixed shuffled order, both sides together, so every stage is a balanced paired subset
let rng = +env('SEARCH_SEED', 12345);
const rand = () => { rng ^= rng << 13; rng ^= rng >>> 17; rng ^= rng << 5; return ((rng >>> 0) % 1e9) / 1e9; };
const shuffle = (a) => { for (let i = a.length - 1; i > 0; i--) { const j = Math.floor(rand() * (i + 1)); [a[i], a[j]] = [a[j], a[i]]; } return a; };
const RACE = SEL_SEEDS.flatMap((seed) => shuffle(OPP_SEL.slice()).flatMap((opp) => [false, true].map((swap) => ({ opp, seed, swap }))));
if (STAGES[STAGES.length - 1] > RACE.length) throw new Error(`the last stage (${STAGES[STAGES.length - 1]}) needs more selection battles than ${RACE.length}`);
const LONG = RACE.slice(0, STAGES[STAGES.length - 1]);
const cache = new Map();
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
	const c = margins(cur, bs), d = margins(cand, bs).map((x, i) => x - c[i]);
	const m = mean(d), sd = Math.sqrt(d.reduce((a, x) => a + (x - m) ** 2, 0) / Math.max(1, d.length - 1));
	return { gain: m, se: sd / Math.sqrt(d.length), n: d.length };
}
const accepted = (g) => g.gain > Math.max(MIN_GAIN, 2 * g.se);

// ---------------------------------------------------------------- the race: every candidate in `cands` ({label, p}) through the stages, in parallel
async function race(cur, cands) {
	let alive = cands.slice();
	for (let s = 0; s < STAGES.length && alive.length; s++) {
		const bs = RACE.slice(0, STAGES[s]);
		await evaluate([cur, ...alive.map((c) => c.p)], bs);
		for (const c of alive) { c.g = pairedGain(c.p, cur, bs); c.stage = s; if (s === 0) c.first = c.g.gain; }
		alive = s < STAGES.length - 1 ? alive.filter((c) => c.g.gain > 0) : alive.filter((c) => accepted(c.g));
	}
	return alive.sort((a, b) => b.g.gain - a.g.gain);
}
// first improvement over chunks; returns {winner, tried}
async function firstImprovement(cur, cands) {
	const tried = [];
	for (let i = 0; i < cands.length; i += CHUNK) {
		const chunk = cands.slice(i, i + CHUNK), ok = await race(cur, chunk);
		tried.push(...chunk);
		if (ok.length) return { winner: ok[0], tried };
	}
	return { winner: null, tried };
}
const fmt = (c) => ({ move: c.label, first_stage_gain: +c.first.toFixed(2), dropped_after: STAGES[c.stage], gain: +c.g.gain.toFixed(2), se: +c.g.se.toFixed(2) });

async function main() {
	const OUT = process.argv[2], CAP = +(process.argv[3] || 40), t0 = Date.now();
	const log = { started: new Date().toISOString(), tool: 'compose_seq.js', settings: { ENEMY_LEVEL: ENEMY_LEVEL || 'pool defaults', ENEMY_DROP, SEL_SEEDS, CONF_SEEDS, OPP_SEL, STAGES, CHUNK, FIRSTS, MIN_GAIN,
		SEARCH_SEED: +env('SEARCH_SEED', 12345), rules: 'game', lookahead: 'excluded in this run' }, race_order: LONG.map(bkey), snapshot: 'astelia_snapshot/SOURCE.md', rounds: [], synergies: [] };
	const save = () => fs.writeFileSync(OUT, JSON.stringify(log, null, 1));
	let cur = NOVICE; const pathTaken = ['novice'], promise = new Map();   // label -> first-stage gain last time it was raced
	await evaluate([NOVICE], LONG);
	log.start_score = mean(margins(NOVICE, LONG));
	for (let round = 1; round <= CAP; round++) {
		const f0 = fights, rec = { round, from_pieces: pieces(cur).length, from_score: +mean(margins(cur, LONG)).toFixed(2) };
		const singles = shuffle(moves(cur)).map((m) => ({ ms: [m], label: m.label, p: applyAll(cur, [m]) }))
			.sort((a, b) => (promise.get(b.label) ?? 0) - (promise.get(a.label) ?? 0));
		let { winner, tried } = await firstImprovement(cur, singles);
		for (const c of tried) promise.set(c.label, c.first);
		rec.singles_tried = tried.length; rec.singles_total = singles.length;
		if (!winner) {   // stuck: two-step check, every first step (harmful ones too), most promising first
			const firsts = singles.slice().sort((a, b) => b.first - a.first).slice(0, FIRSTS);
			let pairsTried = 0, firstsTried = 0;
			for (const m1 of firsts) {
				firstsTried++;
				const p1 = m1.p, seconds = shuffle(moves(p1).filter((m) => m.slot !== m1.ms[0].slot))
					.map((m) => ({ ms: [m1.ms[0], m], parts: [m1, singles.find((c) => c.label === m.label)].filter(Boolean), label: `${m1.label} + ${m.label}`, p: applyAll(p1, [m]) }))
					.sort((a, b) => (promise.get(b.ms[1].label) ?? 0) - (promise.get(a.ms[1].label) ?? 0));
				const r = await firstImprovement(cur, seconds);
				pairsTried += r.tried.length;
				if (r.winner) {
					winner = r.winner; winner.how = '2 together';
					log.synergies.push({ round, combination: winner.label, gain: +winner.g.gain.toFixed(2), se: +winner.g.se.toFixed(2), parts_alone: winner.parts.map(fmt) });
					break;
				}
			}
			Object.assign(rec, { firsts_tried: firstsTried, firsts_total: firsts.length, pairs_tried: pairsTried });
		}
		rec.fights = fights - f0; rec.seconds = +((Date.now() - t0) / 1000).toFixed(0);
		if (!winner) { rec.stopped = 'no single change or two-step pair was accepted'; log.rounds.push(rec); save(); console.log(`round ${round}: stopped | fights ${fights}`); break; }
		cur = winner.p; pathTaken.push(winner.label);
		Object.assign(rec, { accepted: winner.label, how: winner.how || 'single', gain: +winner.g.gain.toFixed(2), se: +winner.g.se.toFixed(2), pieces: pieces(cur), score: +mean(margins(cur, LONG)).toFixed(2) });
		log.rounds.push(rec); save();
		console.log(`round ${round}: +${rec.gain} (se ${rec.se}) ${rec.how}: ${rec.accepted} -> ${rec.pieces.length} pieces, score ${rec.score} | tried ${rec.singles_tried}/${rec.singles_total} singles, ${rec.fights} fights, ${rec.seconds} s`);
	}
	log.final = { path: pathTaken, pieces: pieces(cur), n_pieces: pieces(cur).length, profile: toAi(cur), score_selection: mean(margins(cur, LONG)), search_fights: fights, search_seconds: (Date.now() - t0) / 1000 };
	save();
	if (!process.env.NO_CONFIRM) {   // fresh seeds, the whole opponent pool, both sides, same opponents' skills
		const CONF = battles(CONF_SEEDS, S.POOL);
		const ref = { novice: { level: 'novice' }, regular: { level: 'regular' }, veteran: { level: 'veteran' } };
		if (process.env.CONF_ELITE) ref['elite-fast'] = { level: 'elite-fast' };
		const tasks = [];
		for (const b of CONF) { tasks.push(Object.assign({ profile: toAi(cur), who: 'found' }, b)); for (const [n, a] of Object.entries(ref)) tasks.push(Object.assign({ profile: a, who: n }, b)); }
		const res = await runAll(tasks);
		const by = {}; for (const r of res) (by[r.who] = by[r.who] || []).push(r);
		log.confirmation = Object.fromEntries(Object.entries(by).map(([k, v]) => [k, { margin: +mean(v.map((x) => x.m)).toFixed(2), won: +mean(v.map((x) => x.win)).toFixed(3), n: v.length }]));
		const pk = (r) => `${r.opp}|${r.seed}|${r.swap}`, f = Object.fromEntries(by.found.map((r) => [pk(r), r.m]));
		for (const n of Object.keys(ref)) { const d = by[n].map((r) => f[pk(r)] - r.m); const m = mean(d), sd = Math.sqrt(d.reduce((a, x) => a + (x - m) ** 2, 0) / (d.length - 1)); log.confirmation[`found_minus_${n}`] = { mean: +m.toFixed(2), se: +(sd / Math.sqrt(d.length)).toFixed(2) }; }
	}
	log.fights = fights; log.finished = new Date().toISOString(); log.seconds = (Date.now() - t0) / 1000; save();
	console.log('final', log.final.n_pieces, 'pieces:', log.final.pieces.join(', '));
	if (log.confirmation) console.log('confirmation', JSON.stringify(log.confirmation));
	for (const ch of pool) ch.kill();
}
main().catch((e) => { console.error(e); for (const ch of pool) ch.kill(); process.exit(1); });
