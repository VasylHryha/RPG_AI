// Formation sandbox: two identical armies (10 artillery, 30 direct fire, 10 melee each), or our
// army against a respawning hunter stream. Every unit shares the SAME individual skills (chase,
// kite, lane strafe, shell lead, min-range back-off, answering a melee attacker). A side's brain
// adds coordination on top:
//   alone      no coordination
//   formation  shape + role rules (a fixed preset: shape, tactics, knobs)
//   reactive   formation + a commander: a short ordered list of plain condition rules (RULES)
//              that reads the enemy every half second and picks a plan (PLANS).
// Pure JS: node (compare.js, shapes.js, doctrines.js, reactive.js) and formation_sandbox.html.
(function (root) {
'use strict';

const DEFAULT_F = {
	shape: 'line',
	frontSpacing: 34, rankSpacing: 22, rangedRanks: 2, screenGap: 32, rearGap: 40,
	standoff: 0.8,             // the rear shooter rank stands this fraction of direct-fire range from the enemy front
	turnRate: 0.1,
	syncRadius: 30,            // formed when every member is this close to its slot
	syncGate: true,            // no advance into enemy reach before the shape is formed
	holdWhileClosing: true,    // the anchor waits while the enemy front walks into our fire
	closingSpeed: 15,          // px/s of enemy approach that counts as closing
	zoneDepth: 200, zoneBehind: 50, zoneSideMargin: 40,
	coverFraction: 0.9,        // strike zone is bounded by the shooters' cover
	maxStrikersPerTarget: 1,
	dive: true,                // no enemy melee near: strikers charge the enemy shooters together
	diveMinTargets: 4,         // a dive needs a real soft line: at least this many enemy shooters in reach
	diveRange: 320,            // how far ahead of the front edge a dive may reach
	laneLeash: 26,             // how far a direct-fire member may strafe off its slot for a lane
	kiteLeash: 60,             // how far behind its slot a direct-fire member may step back
	engagedWeight: 2,          // artillery value of a target a melee member pins
	shooterFocus: 'spread',    // spread | one | squads | nearest | protect | soft
	squadSize: 5,
	meleeDoctrine: 'zone',     // zone | screen | flank | anvil | auto
	autoAttack: 'anvil',
	flankWidth: 240, flankDepth: 60, flankWait: 8,
	artilleryDoctrine: 'pinned', // cluster | pinned | counter | soft
	anchorMode: 'standoff',    // standoff | siege
	siegeMargin: 30,           // siege: keep every member this far outside enemy direct-fire reach
	siegeArtMargin: 10,        // siege: and this far outside enemy artillery reach
	meleeKeepAway: 160,        // siege without our own melee screen: keep enemy melee this far
	siegeOwnArtMargin: 60,     // ...and our own artillery this far, since it cannot dodge in time
	siegeMinArt: 1,            // siege needs at least this many of our artillery
	peelRadius: 120,           // an enemy melee this close to one of our soft members is a threat
	dodge: false,              // step out of predicted enemy shell splashes
	fireDepth: 0,              // fire control: chance a dodged shot still hits per enemy behind the target (0 = ignore)
	fireControl: false,        // shots count by their chance to hit; targets that cannot dodge first; aim lane kept clear
	surroundRing: 0.65,        // encircle: melee ring radius as a share of melee reach (min 2 r)
	surroundArc: 200,          // encircle: shooter arc width in degrees, facing us
	surroundDist: 0.8,         // encircle: shooters at this share of their reach
	surroundLanes: true,       // encircle: shooters take the angles between the melee positions (clear lanes)
	oblique: false,            // face the weaker end of the enemy line instead of its nearest unit (local superiority)
	surroundMelee: 'ring',     // encircle: melee on a ring around the target ('ring') or on an arc on our side, nearer than our casters ('screen')
	surroundCorner: false,     // encircle: stand between the target and the arena centre, so its way away from us is a wall
	jink: 0,                   // shooters in a slot step this far side to side across enemy fire (0 = off)
	release: null,             // roles that leave the shape and act at full speed: ['melee', 'ranged', 'artillery']
	raidTarget: 'soft',        // what released melee go for: soft | artillery
	flankForce: false,         // flank wings go out even before the enemy soft line is exposed
	flankTarget: 'soft',       // what flank wings strike: soft | artillery
	anchorSpeed: 0,            // pack anchor speed (0 = the artillery's pace)
};

const PRESETS = {
	line: {},
	'wide line': { rangedRanks: 1, frontSpacing: 38, rankSpacing: 22, screenGap: 21, rearGap: 59, standoff: 0.89,
		turnRate: 0.17, zoneDepth: 45, coverFraction: 0.84, maxStrikersPerTarget: 2, laneLeash: 22, kiteLeash: 71,
		engagedWeight: 1, closingSpeed: 26, dive: false, zoneBehind: 88, zoneSideMargin: 57 },
	wedge: { shape: 'wedge' },
	box: { shape: 'box' },
	column: { shape: 'column' },
	loose: { shape: 'line', frontSpacing: 55, rankSpacing: 36, screenGap: 45 },
	screen: { shape: 'screen' },
	crescent: { shape: 'crescent' },
	ring: { shape: 'ring' },
	'wedge hold': { shape: 'wedge', meleeDoctrine: 'screen' },
	'line anvil': { meleeDoctrine: 'anvil' },
	'wedge flank': { shape: 'wedge', meleeDoctrine: 'flank' },
	// Loose formations whose members break off and attack as they want (release), at full speed.
	'loose free': { shape: 'line', frontSpacing: 55, rankSpacing: 36, screenGap: 45, release: ['melee', 'ranged'] },
	'swarm': { shape: 'line', frontSpacing: 55, rankSpacing: 36, screenGap: 45, release: ['melee', 'ranged', 'artillery'] },
	'loose skirmish': { shape: 'line', frontSpacing: 55, rankSpacing: 36, screenGap: 45, release: ['ranged'], dodge: true, holdWhileClosing: false },
	'loose berserk': { shape: 'line', frontSpacing: 55, rankSpacing: 36, screenGap: 45, release: ['melee'], raidTarget: 'artillery', holdWhileClosing: false },
};

// Every opponent a random gauntlet can draw: fixed formations, loose free-attack ones, the two
// thinking commanders, and an army fighting alone.
const POOL = [...Object.keys(PRESETS), 'storm', 'wolfpack', 'alone'];
// The options that put one pool entry on the enemy side.
function enemyOf(name, extra) {
	if (name === 'alone') return { enemy: 'alone' };
	if (name === 'storm' || name === 'wolfpack' || name === 'gamepack') return { enemy: name };
	return { enemy: 'formation', enemyF: Object.assign({ preset: name }, extra || {}) };
}
// Draw `rounds` opponents. mode 'any': each round any entry; 'pool': each entry at most once.
function drawOpponents(seed, rounds, mode) {
	const r = rng(seed * 2654435761 >>> 0 || 1), left = POOL.slice(), out = [];
	for (let i = 0; i < rounds; i++) {
		const from = mode === 'pool' ? left : POOL;
		if (!from.length) break;
		const k = Math.floor(r() * from.length);
		out.push(from[k]);
		if (mode === 'pool') left.splice(k, 1);
	}
	return out;
}

// Commander plans: overrides on the reactive side's base preset.
const PLANS = {
	hold:  { meleeDoctrine: 'screen', anchorMode: 'standoff', holdWhileClosing: true },
	siege: { meleeDoctrine: 'screen', anchorMode: 'siege', rearGap: 6, artilleryDoctrine: 'soft' },
	// Faster skirmishers: move in as one block so they meet all our shooters a few at a time.
	counter: { meleeDoctrine: 'screen', anchorMode: 'standoff', holdWhileClosing: false, syncGate: false, standoff: 0.6, dive: false,
		shooterFocus: 'spread' },
	// Extra options for the look-ahead commander (it only picks one when its simulated trade is better).
	advance: { meleeDoctrine: 'screen', anchorMode: 'standoff', holdWhileClosing: false, syncGate: false, standoff: 0.6,
		anchorSpeed: 62, dive: false },                                   // close at shooter speed
	skirmish: { meleeDoctrine: 'screen', anchorMode: 'standoff', holdWhileClosing: true, release: ['ranged'],
		shooterFocus: 'spread' },                                         // our shooters fight freely
	spread: { meleeDoctrine: 'screen', anchorMode: 'standoff', holdWhileClosing: true, frontSpacing: 55, rankSpacing: 36,
		screenGap: 45 },                                                  // loose spacing vs splash
	widehold: { meleeDoctrine: 'screen', anchorMode: 'standoff', holdWhileClosing: true, rangedRanks: 1, frontSpacing: 38,
		screenGap: 21 },                                                  // one wide shooter rank
	meleehunt: { meleeDoctrine: 'screen', anchorMode: 'standoff', holdWhileClosing: true, release: ['melee'],
		raidTarget: 'soft' },                                             // melee hunt their shooters
	// Bait: our tanky melee step forward into enemy charge range while the shooters hang back, so enemy
	// charges are spent on melee; the look-ahead sees the spent cooldowns and turns to push by itself.
	bait: { meleeDoctrine: 'screen', anchorMode: 'standoff', holdWhileClosing: false, syncGate: false, standoff: 1.05,
		screenGap: 95, dive: false },
	// Raiders: melee peel to them while the pack keeps its siege distance from the enemy's fire.
	intercept: { meleeDoctrine: 'screen', peelRadius: 180, maxStrikersPerTarget: 2, dive: false,
		anchorMode: 'siege', rearGap: 6, shooterFocus: 'protect', artilleryDoctrine: 'pinned', engagedWeight: 3 },
	hunt:  { meleeDoctrine: 'zone', dive: true, diveMinTargets: 1, diveRange: 700, anchorMode: 'standoff', holdWhileClosing: false,
		syncGate: false, standoff: 0.7 },
	push:  { meleeDoctrine: 'anvil', anchorMode: 'standoff', holdWhileClosing: false, shooterFocus: 'soft' },
	flank: { meleeDoctrine: 'flank', anchorMode: 'standoff', holdWhileClosing: true },
	// Encircle a few targets (Phase B1): melee on a ring around the target weighted to its escape, shooters on a
	// wide arc for crossfire, artillery behind them (surroundOrders).
	surround: { anchorMode: 'standoff', holdWhileClosing: false, syncGate: false, meleeDoctrine: 'zone', dive: false, shooterFocus: 'one', surround: true },
	// Artillery raid: melee wings go out wide and strike the enemy artillery from the flanks; the rest holds.
	raidart: { meleeDoctrine: 'flank', flankForce: true, flankTarget: 'artillery', flankWidth: 300, flankWait: 4, anchorMode: 'standoff', holdWhileClosing: true },
	// Local superiority: the whole pack faces the weaker end of the enemy line (positionAnchor, f.oblique).
	oblique: { meleeDoctrine: 'screen', anchorMode: 'standoff', holdWhileClosing: false, syncGate: false, oblique: true },
	// Engage few targets at once: every role acts at full speed on the shared focus target.
	engage: { anchorMode: 'standoff', holdWhileClosing: false, syncGate: false, release: ['melee', 'ranged', 'artillery'], raidTarget: 'soft', shooterFocus: 'one' },
	// Focus fire: shooters in squads of 4, each squad on one target until it falls.
	focus: { meleeDoctrine: 'screen', anchorMode: 'standoff', holdWhileClosing: true, shooterFocus: 'squads', squadSize: 4 },
	pushfocus: { meleeDoctrine: 'anvil', anchorMode: 'standoff', holdWhileClosing: false, shooterFocus: 'squads', squadSize: 4 },
};

// Commander rules: first match wins. Each is one plain condition on what we can see.
const RULES = [
	// Game rules only (the sandbox rules keep their results): few enemies -> the profile's fewPlan (default surround).
	// Also when we outnumber them 4 to 1 (the last guns otherwise sit just outside every reach: a standoff).
	['few', (r) => r.game && finishingCounts(r.ourCount, r.theirCount), (r) => `only ${r.theirCount} enemy: ${r.fewPlan}`],
	['intercept', (r) => r.raiders >= 2, (r) => `main threat: ${r.raiders} enemy melee raiding our back line, intercept them`],
	['hunt',  (r) => r.theirShoot === 0 && r.theirArt > 0, (r) => `only ${r.theirArt} enemy artillery left: ${r.ourMelee >= 2 ? 'melee run inside its minimum range' : 'close in and shoot them'}`],
	['counter', (r) => r.shootRush, (r) => 'main threat: we give ground but their shooters still close in: move in as one block'],
	['push',  (r) => r.quiet > 8 && r.sieging && r.approach < 10, (r) => `standoff: they are not coming and nobody has hit anyone for ${r.quiet.toFixed(0)} s, go in`],
	['siege', (r) => r.ourArt >= r.siegeMinArt && r.theirShoot + r.theirArt > 0, (r) => `we have ${r.ourArt} artillery: stay outside their fire and shell them`],
	['push',  (r) => r.exposed && r.ourShoot >= r.theirShoot, (r) => `enemy shooters exposed (${r.esoft}), we outshoot them`],
	['flank', (r) => r.exposed && r.ourMelee >= 4, () => 'enemy shooters exposed, they outshoot us: hit them from behind'],
	['hold',  () => true, () => 'default: hold and let them come'],
];

// Opponent commanders: their own rules, free to break formation and run at full speed.
const STORM_RULES = [
	['rush', (r) => r.outranged, (r) => `hit for ${r.recentTaken | 0} in 3 s and cannot hit back: all-out rush`],
	['rush', (r) => r.ourCount >= r.theirCount * 1.25, (r) => `we outnumber them ${r.ourCount} to ${r.theirCount}: all-in`],
	['rush', (r) => r.theirMelee < 3 && r.ourMelee >= 3, () => 'their melee screen is gone: into their back line'],
	['advance', () => true, () => 'advance in formation'],
];
const STORM_PLANS = {
	advance: { anchorMode: 'standoff', holdWhileClosing: false, meleeDoctrine: 'zone', dive: true, anchorSpeed: 60, release: null },
	rush: { release: ['melee', 'ranged', 'artillery'], raidTarget: 'soft' },
};
const WOLF_RULES = [
	['raid', (r) => r.ourMelee >= 3 && !r.raidSpent, () => 'raid their artillery from both flanks at full speed'],
	['skirmish', () => true, () => 'shooters skirmish at max range, artillery hunts theirs'],
];
const WOLF_PLANS = {
	raid: { meleeDoctrine: 'flank', flankForce: true, flankTarget: 'artillery', flankWidth: 300, flankWait: 4, release: ['ranged'],
		anchorMode: 'standoff', holdWhileClosing: false, shooterFocus: 'soft', artilleryDoctrine: 'counter', dodge: true, anchorSpeed: 55 },
	skirmish: { meleeDoctrine: 'zone', release: ['ranged'], anchorMode: 'standoff', holdWhileClosing: false,
		artilleryDoctrine: 'counter', dodge: true, anchorSpeed: 55 },
};
// The game's pack AI (reduced port, brain 'gamepack'): PRESSURE / DEFEND / WITHDRAW doctrine from
// systems/ai_tactics/PACK_COMBAT_DOCTRINES.md:34-69 and native/encounter_core/src/ai/encounter_groups_decision.cpp
// (severe attrition = fewer than half the starting members; backline breached = a hostile within kMeleeBand 96 px
// of a rear member, encounter_groups_internal.h), pressure needs living >= known threats; 1 s hold + 2 matching
// decisions, withdrawal immediate, leaving it 3 confirmations; threat responses (melee rush -> defend, direct line
// -> loose pressure or defend when saturating, area -> loose / dispersed pressure or defend when saturating,
// mixed -> defend; broad 0.25, saturating 0.60 of members). Layouts: pressure = screen_and_focus (melee wall in
// front, shooters behind, shared focus target); defend = surround (ring: melee outside, ranged inside);
// withdraw = the ring moving away. Left out: learned utility, Sense uncertainty, region planner, excursion and
// morph machinery. The threat horizon (1 s) is this port's choice: the game's value is not read here.
const GAMEPACK_PLANS = {
	// Pressure: the station is set by the actions' ranges (no formed-gate), and a frontliner that cannot attack from
	// its slot runs a bounded intercept at the target (PACK_COMBAT_DOCTRINES.md:83-97) -> dive at any target in reach.
	pressure:  { shape: 'line', anchorMode: 'standoff', holdWhileClosing: false, syncGate: false, standoff: 0.85, meleeDoctrine: 'zone', dive: true, diveMinTargets: 1, diveRange: 400, shooterFocus: 'one', artilleryDoctrine: 'cluster' },
	loose:     { shape: 'line', anchorMode: 'standoff', holdWhileClosing: false, syncGate: false, standoff: 0.85, meleeDoctrine: 'zone', dive: true, diveMinTargets: 1, diveRange: 400, shooterFocus: 'one', artilleryDoctrine: 'cluster', frontSpacing: 55, rankSpacing: 36, screenGap: 45 },
	dispersed: { shape: 'line', anchorMode: 'standoff', holdWhileClosing: false, syncGate: false, standoff: 0.85, meleeDoctrine: 'zone', dive: true, diveMinTargets: 1, diveRange: 400, shooterFocus: 'one', artilleryDoctrine: 'cluster', frontSpacing: 70, rankSpacing: 48, screenGap: 55 },
	defend:    { shape: 'ring', anchorMode: 'standoff', holdWhileClosing: true, meleeDoctrine: 'screen', dive: false, shooterFocus: 'protect' },
	withdraw:  { shape: 'ring', anchorMode: 'siege', meleeDoctrine: 'screen', dive: false, shooterFocus: 'protect', siegeMargin: 60 },
};
const GAMEPACK = { meleeBand: 96, broad: 0.25, saturating: 0.6, hold: 1.0, confirm: 2, leaveWithdraw: 3, horizon: 1.0 };
function gamePackDecide(w, pack) {
	const me = pack.team, ms = team(w, me), es = foes(w, me);
	if (pack.startCount === undefined) pack.startCount = ms.length;
	const severe = ms.length * 2 < pack.startCount;
	const backline = ms.some((m) => !MELEE[m.role] && es.some((e) => dist(e, m) <= GAMEPACK.meleeBand));
	let mode = severe ? 'withdraw' : es.length && !backline && ms.length >= Math.max(1, es.length) ? 'pressure' : 'defend';
	// Threat projection: which members are threatened within the horizon, by which family.
	const hit = { rush: new Set(), line: new Set(), area: new Set() };
	for (const e of es) if (MELEE[e.role]) {
		const m = nearest(e, ms);
		if (m && dist(e, m) < e.speed * GAMEPACK.horizon + e.range + m.r && (e.vx * (m.x - e.x) + e.vy * (m.y - e.y)) > 0) hit.rush.add(m);
	}
	for (const s of w.shots) if (s.src.team !== me && s.aimed) for (const m of ms) {
		const px = m.x - s.x, py = m.y - s.y, along = px * s.dx + py * s.dy;
		if (along > 0 && along < s.speed * GAMEPACK.horizon && Math.abs(px * s.dy - py * s.dx) <= m.r) hit.line.add(m);
	}
	for (const s of w.shells) if (s.src.team !== me && s.t - w.t < GAMEPACK.horizon) for (const m of ms) if (len(m.x - s.x, m.y - s.y) <= s.splash + m.r) hit.area.add(m);
	const cov = (set) => set.size / Math.max(1, ms.length), fams = Object.keys(hit).filter((k) => hit[k].size);
	let response = null;
	if (fams.length > 1) response = 'defend';
	else if (fams[0] === 'rush') response = 'defend';
	else if (fams[0] === 'line') response = cov(hit.line) >= GAMEPACK.saturating ? 'defend' : 'loose';
	else if (fams[0] === 'area') response = cov(hit.area) >= GAMEPACK.saturating ? 'defend' : cov(hit.area) >= GAMEPACK.broad ? 'dispersed' : 'loose';
	// A threat response needs 2 confirmations to enter and 3 to clear.
	pack.respCount = response === pack.respSeen ? (pack.respCount || 0) + 1 : 1;
	pack.respSeen = response;
	if (response && pack.respCount >= GAMEPACK.confirm) pack.response = response;
	else if (!response && pack.respCount >= 3) pack.response = null;
	if (!severe && pack.response) mode = pack.response;
	// Hysteresis: withdrawal is immediate; leaving it takes 3 confirmations; other changes 1 s hold + 2 matches.
	pack.wantCount = mode === pack.wantMode ? (pack.wantCount || 0) + 1 : 1;
	pack.wantMode = mode;
	const cur = pack.plan, held = w.t - (pack.planSince ?? -99);
	const go = !cur || (mode === 'withdraw' && cur !== 'withdraw') ||
		(cur === 'withdraw' ? pack.wantCount >= GAMEPACK.leaveWithdraw : held >= GAMEPACK.hold && pack.wantCount >= GAMEPACK.confirm);
	if (mode !== cur && go) {
		setPlan(w, pack, GAMEPACK_PLANS, comboOf(mode), `game doctrine: ${mode}`, {}, `plan ${mode}`);
	}
}
const BRAINS = {
	reactive: { rules: RULES, plans: null, base: { preset: 'wide line' } },
	storm: { rules: STORM_RULES, plans: STORM_PLANS, base: { preset: 'line anvil' } },
	wolfpack: { rules: WOLF_RULES, plans: WOLF_PLANS, base: { preset: 'loose', dodge: true } },
	gamepack: { rules: null, plans: GAMEPACK_PLANS, base: { preset: 'line' } },
};

// The look-ahead commander settings measured best so far (README): 12 plans, 3 s ahead, coarse 0.1 s
// steps, enemy assumed to keep doing what it does now, loss weight 1.5.
const LOOKAHEAD = { every: 1, horizon: 3, dt: 0.1, k: 1.5, inertia: 30, models: ['continue'], contact: 450,
	plans: ['hold', 'siege', 'counter', 'intercept', 'push', 'hunt', 'flank', 'advance', 'skirmish', 'spread', 'widehold', 'meleehunt', 'bait'] };

// ---------------------------------------------------------------- AI profiles
// One AI profile per side: { brain, formation, lookahead, skills }. The world rules (shots, abilities, healing)
// are the same for both sides; everything a side *decides* lives in its profile.
//   brain:     'alone' (every unit for itself) | 'formation' (a fixed formation) | 'rules' (commander that reads
//              the fight and switches plans) | 'storm' | 'wolfpack' (the two thinking opponents)
//   formation: formation settings, { preset, ...overrides } (DEFAULT_F, PRESETS)
//   lookahead: off (null) | 'full' (LOOKAHEAD) | 'fast' (with the shortlist network, setNet) | settings object
//   ab:        coordinated-ability thresholds (AB_DEFAULT)
//   skills:    the unit-level decisions below; to add one, register it here (def = default, alt = the value
//              ai_lab.js tests it against) and read it with sk(w, team, name)
const SKILLS = {
	dodgeShots:  { def: true,          alt: false,  values: [false, 'soft', true], doc: 'sidestep enemy aimed shots it has seen (soft = not melee)' },
	shotReact:   { def: 0.12,          alt: 0.3,    doc: 'seconds a unit needs to see a shot before it can react' },
	dodgeShells: { def: true,          alt: false,  values: [false, 'plan', true, 'smart'], doc: 'step out of predicted shell splashes and enemy slow fields (plan = only when the plan says so; smart = to the reachable spot under the fewest blasts, counting every shell in the air)' },
	lead:        { def: 'smooth',      alt: 'none', values: ['none', 'raw', 'smooth'], doc: 'aim shots and shells where the target will be: no / from its last step / from its movement over 0.3 s' },
	pursuit:     { def: 'cut',         alt: 'chase', values: ['chase', 'cut'], doc: 'melee run to where the target is / will be' },
	kite:        { def: 70,            alt: 0,      doc: 'shooters step back from enemy melee closer than this (0 = never)' },
	abilities:   { def: 'coordinated', alt: 'off',  values: ['off', 'auto', 'coordinated'], doc: 'never use / each unit by its own trigger / side-wide rules (coordAbilities)' },
	leaderBracket: { def: 12,          alt: 0,      doc: 'leader fire: a group aims centre, left and right of a target that can dodge, this many px apart, so a sidestep walks into another shot' },
	leaderFire:  { def: false,         alt: true,   doc: 'the leader assigns shooters to targets (enough to kill each, most dangerous first) and, with wind-ups, holds each group until all are ready so the shots arrive together' },
	lockedDodge: { def: false,         alt: true,   doc: 'melee locked in a fight also break off to dodge shells' },
	reactAim:    { def: true,          alt: false,  doc: 'coordinated: a unit an enemy aims at shields or jumps back' },
	fireControl: { def: false,         alt: true,   doc: 'shots count by their chance to hit; targets that cannot dodge first; aim lane kept clear' },
	fireDepth:   { def: 0,             alt: 0.25,   doc: 'fire control: chance a dodged shot still hits, per enemy behind the target' },
	holdFire:    { def: null,          alt: { wave: 0.45, sync: 0.5 }, values: [null, { wave: 0.45 }, { sync: 0.5 }, { wave: 0.45, sync: 0.5 }],
		doc: 'fire control for every unit, game rules: at the moment a unit could start its cast the leader starts it or holds it, only when holding pays. wave (artillery vs the player): with its dash ready the first gun casting at it is the bait, the others start this many s later and aim at the end of the dash the bait forces (dash net); sync (area attacks): hold while ours come off cooldown within this many s, only when one volley of them all leaves the enemy no escape that two separate ones would' },
	jink:        { def: 0,             alt: 14,     doc: 'shooters in a slot step this far side to side across enemy fire' },
	killSpeed:   { def: false,         alt: true,   doc: 'shooters and artillery rank targets by health left per damage per second they deal (the cheapest firepower to remove first) instead of health left' },
	waves:       { def: 0,             alt: 3,      doc: 'game rules: hold a cast start until this many of ours with a target in reach are ready, then start together (0 = off; waits at most 1 s)' },
	lobLead:     { def: false,         alt: true,   values: [false, true, 'adaptive'], doc: 'game rules: a lob aims where the target will be when it lands (the game aims at its position at release); adaptive = only when the target has moved steadily for about a second' },
	artyFire:    { def: 'single',      alt: 'plan', values: ['single', 'plan'], doc: 'artillery: each gun on its own target / plan: volleys chosen by predicting how the enemy will dodge (trap, sweep, net, wall, focus or singles)' },
	artyRobust:  { def: 0.5,           alt: 0,      doc: 'plan: weight of the smart-dodger model (best reachable spot) against the exact dodge rule the enemy uses' },
	artyHerd:    { def: 0,             alt: 10,     doc: 'plan: worth of where the enemy ends up: per enemy, its threat x (our fighters that reach its predicted spot - its friends within 80 px) x this' },
	artyRollout: { def: null,          alt: { top: 5, horizon: 2 }, values: [null, { top: 3, horizon: 2 }, { top: 5, horizon: 2 }, { top: 5, horizon: 2, shape: ['battery', 'split', 'herd'] }, { top: 5, horizon: 2, shape: ['battery', 'split', 'herd'], score: 'ltd2' }, { top: 5, horizon: 2, shape: ['battery', 'split', 'herd'], score: 'ltd2', dt: 0.1, every: 0.3 }], doc: 'plan: the best `top` attacks by shell damage, plus the best of each family in `shape` (e.g. split, herd, wall), are each played forward `horizon` s on a copy of the battle (every unit acting); the attack with the best result (their health and kills lost minus ours) is fired' },
	artyFollow:  { def: false,         alt: true,   values: [false, true, 'shooters'], doc: 'plan: enemies an attack leaves cut off (at most one friend within 80 px of their predicted spot) are marked for 2 s: our shooters rank them right after threats to our back line, our free melee within 200 px go for them (\'shooters\': shooters only)' },
	artyBattery: { def: false,         alt: true,   doc: 'plan: also try every shell on one of their guns (the two nearest in reach)' },
	artyModel:   { def: 'simple',      alt: 'exact', values: ['simple', 'exact'], doc: "plan: how the planner predicts the enemy under its shells. exact: each by its own dodge rule and protection; simple: every dodger steps straight out, raw damage" },
	artyOwn:     { def: false,         alt: true,   doc: "plan, exact model: our own units a planned blast catches and that cannot step out count against the attack" },
	meleeFocus:  { def: false,         alt: true,   doc: 'game rules: a melee unit swings at the enemy in reach with the least health left after our swings already winding up at it' },
	saveWounded: { def: 0,             alt: 0.3,    doc: 'game rules: a unit below this health fraction backs away from the nearest enemy toward our side, except when finishing (their last 2, or 4 to 1) (0 = off); tried and dropped: only when no faster enemy threatens or targets it (it then rarely backs off and loses the gain)' },
	weaponsFree: { def: false,         alt: true,   doc: 'game rules: a melee unit whose target is out of reach fights an enemy that is within its reach instead of idling next to it' },
	castDodge:   { def: false,         alt: true,   doc: 'smart dodge, game rules: an enemy gun winding up is a blast to come at its target (it aims at the target at release): our units next to that target step out before the lob exists; the target itself stays (moving would only move the aim) and dodges after release' },
	combos:      { def: null,          alt: [],     doc: 'the combo director (observe -> combos): the names of the combos this side may start (COMBOS); null = the director is off; [] = on with no combo (observes and logs only, the AI is unchanged)' },
	artyEvery:   { def: 0.25,          alt: 0.5,    doc: 'plan: seconds between planning decisions' },
};
const SKILL_DEFAULTS = Object.fromEntries(Object.entries(SKILLS).map(([k, v]) => [k, v.def]));
// Ready-made AI levels; each fully defines brain, formation, look-ahead and skills. A side takes one with
// { level: name } (its own fields override); a gauntlet enemy keeps its opponent brain and takes only the skills.
const LEVELS = {
	novice:  { brain: 'alone', lookahead: null, skills: { dodgeShots: false, shotReact: 0.3, dodgeShells: false, lead: 'none', pursuit: 'chase', kite: 0, abilities: 'off', reactAim: false } },
	regular: { brain: 'formation', formation: { preset: 'line' }, lookahead: null, skills: { dodgeShots: false, shotReact: 0.2, dodgeShells: true, lead: 'raw', pursuit: 'chase', abilities: 'auto', reactAim: false } },
	veteran: { brain: 'rules', formation: { preset: 'wide line' }, lookahead: null, skills: { artyFire: 'plan', lockedDodge: true } },
	elite:   { brain: 'rules', formation: { preset: 'wide line', oblique: true }, lookahead: { extends: 'fast', terminal: 6, stall: 10 },
		skills: { artyFire: 'plan', lockedDodge: true, dodgeShells: 'smart', castDodge: true, weaponsFree: true, saveWounded: 0.3, artyBattery: true, artyRollout: { top: 5, horizon: 2, shape: ['battery', 'split', 'herd'], score: 'ltd2' } } },
	// elite with the artillery outcome check on a budget (copies at 0.1 s steps, at most one check per 0.3 s):
	// 4.7x less CPU (10.3 vs 48.9 ms per tick), about 1.5 more of ours lost per won fight (pool, 1.3 standard errors).
	'elite-fast': { brain: 'rules', formation: { preset: 'wide line', oblique: true }, lookahead: { extends: 'fast', terminal: 6, stall: 10 },
		skills: { artyFire: 'plan', lockedDodge: true, dodgeShells: 'smart', castDodge: true, weaponsFree: true, saveWounded: 0.3, artyBattery: true, artyRollout: { top: 5, horizon: 2, shape: ['battery', 'split', 'herd'], score: 'ltd2', dt: 0.1, every: 0.3 } } },
};
let NET = null;   // shortlist network for lookahead 'fast' (bc_net.json); without it 'fast' plays the full look-ahead
function setNet(net) { NET = net; }
function resolveLookahead(la) {
	if (!la) return null;
	if (la === 'full') return LOOKAHEAD;
	if (la === 'fast') return NET ? Object.assign({}, LOOKAHEAD, { net: NET, netPrune: 3 }) : LOOKAHEAD;
	// The mind: role-by-role search over tactic combinations (8 per decision), the best 2 also against a rush.
	if (la === 'mind') return Object.assign({}, LOOKAHEAD, NET ? { net: NET, netPrune: 3 } : {}, { mind: true, budget: 8, robustTop: 2, models: ['continue', 'rush'], blend: 0.7 });
	// A settings object extends LOOKAHEAD, or the named look-ahead in `extends` ({ extends: 'mind', budget: 4 }).
	return Object.assign({}, la.extends ? resolveLookahead(la.extends) : LOOKAHEAD, la);
}
// Side t's profile: what the older options say (mode, reactiveBase / f / enemyF, world skill switches), then its
// level from options.ai[t], then options.ai[t]'s own fields. Resolved once per battle; reads are plain lookups.
const BRAIN_OF = { reactive: 'rules', formation: 'formation', alone: 'alone', storm: 'storm', wolfpack: 'wolfpack', gamepack: 'gamepack' };
function buildProfile(mode, o, t) {
	const x = (o.ai && o.ai[t]) || {}, lv = (x.level && LEVELS[x.level]) || {};
	// The side's final brain (its own profile, then its level, then the older options) sets brain-dependent defaults.
	const brain = x.brain || lv.brain || (t === 0 ? BRAIN_OF[mode] : o.scenario === 'mirror' ? BRAIN_OF[o.enemy] : 'alone');
	const form = t === 0 ? (mode === 'reactive' ? Object.assign({}, o.reactiveBase, o.f) : o.f || {}) : o.enemyF || {};
	const pick = (k, dflt) => (form[k] !== undefined ? form[k] : dflt);
	const base = { brain, formation: form, lookahead: t === 0 ? o.lookahead || null : null, disablePlans: t === 0 ? o.disablePlans || [] : [], skills: Object.assign({}, SKILL_DEFAULTS, {
		dodgeShots: o.shotDodge === false ? false : pick('shotDodge', true), shotReact: o.shotReact,
		dodgeShells: o.shellDodgeAll ? true : 'plan', lead: pick('smoothLead', o.smoothLead) ? 'smooth' : 'raw',
		pursuit: pick('pursuit', o.pursuit), kite: o.kiteRadius, reactAim: o.reactAim !== false,
		abilities: brain === 'rules' && o.coordAbilities !== false ? 'coordinated' : 'auto',
		fireControl: pick('fireControl', false), fireDepth: pick('fireDepth', 0), holdFire: pick('holdFire', null), jink: pick('jink', 0) }) };
	// Game rules: a cast aims at the target's position at release; reflex dodges only by their kind's dash. Stepping
	// out of a blast is movement, a decision a profile may turn on (casts never root: COMBAT_DESIGN.md:348,373).
	if (o.rules === 'game') Object.assign(base.skills, { lead: 'none', dodgeShots: false, dodgeShells: false, pursuit: 'chase' });
	const prof = Object.assign({}, base, lv, x);
	prof.skills = Object.assign({}, base.skills, lv.skills, x.skills);
	prof.lookahead = resolveLookahead(prof.lookahead);
	if (prof.lookahead && prof.objective) prof.lookahead = Object.assign({}, prof.lookahead, { objective: prof.objective });   // 'hp' | 'deaths'
	prof.ab = Object.assign({}, AB_DEFAULT, o.ab, lv.ab, x.ab);   // coordinated-ability thresholds
	return prof;
}

// shots: 'aimed' = a shot flies straight at shotSpeed to where its target will be and hits the first body it
// crosses (it can miss, and units sidestep it: shotDodge); 'homing' = the old shot that always follows its target.
// pursuit: 'cut' = melee run to where the target will be; 'chase' = to where it is. Both are skills of every army.
const DEFAULTS = { seed: 7, dt: 1 / 30, duration: 90, shots: 'aimed', shotSpeed: 350, shotDodge: true, shotReact: 0.12,
	pursuit: 'cut', smoothLead: true,
	windUp: false,   // every shot and shell needs a wind-up before its instant release (WINDUP); a dodge ability breaks it
	shellDodgeAll: true,   // every army steps out of predicted shell splashes (false = only packs whose settings say so)
	width: 1400, height: 800, scenario: 'hunters',
	enemy: 'alone', enemyF: { preset: 'wedge hold' }, reactiveBase: { preset: 'wide line' },
	hunters: { melee: 10, archers: 4, respawn: 3.0 }, kiteRadius: 70, f: {} };

const ROLE = {
	melee:    { hp: 300, speed: 70, r: 8, range: 18, dmg: 30, cd: 0.8 },
	ranged:   { hp: 90,  speed: 62, r: 6, range: 190, dmg: 14, cd: 1.0, shot: 420 },
	artillery:{ hp: 70,  speed: 48, r: 7, range: 330, minRange: 90, dmg: 26, cd: 3.0, flight: 1.0, splash: 45 },
	hunter:   { hp: 420, speed: 76, r: 9, range: 20, dmg: 40, cd: 1.0 },
	archer:   { hp: 200, speed: 66, r: 7, range: 220, dmg: 20, cd: 1.2, shot: 420 },
};
const MELEE = { melee: true, hunter: true };

// Abilities (option `abilities: true`; both armies get them). Two per role; using one locks the
// unit's other ability for `lock` seconds.
const ABIL = {
	lock: 1.5,
	charge: { cd: 8, speed: 230, min: 50, max: 200, bonus: 1.5, time: 1.0 },          // melee
	shield: { cd: 10, dur: 3, block: 0.8, speedMul: 0.5 },                             // melee
	aimed: { cd: 8, aim: 1.0, mult: 3 },                                               // direct fire
	disengage: { cd: 10, dist: 120, speed: 240 },                                      // direct fire
	barrage: { cd: 20, shells: 2, spread: 40, gap: 0.25, dmgMul: 0.6 },               // artillery (balanced: about 20% of damage)
	slow: { cd: 12, dur: 3, radius: 45, mul: 0.5 },                                     // artillery
};
const ROLE_ABIL = { melee: ['charge', 'shield'], hunter: ['charge', 'shield'], ranged: ['aimed', 'disengage'],
	archer: ['aimed', 'disengage'], artillery: ['barrage', 'slow'] };

// ---------------------------------------------------------------- game rules (world option rules: 'game')
// The game's own combat numbers, nothing invented here. Our three roles are three monster kinds:
//   melee = brute (maul), shooters = spitter (ember_spit), artillery = shaman / Voltfang (arc_bolt).
// Sources: data/enemies/enemy_kinds.json (base_speed, radius, ep, ep_regen, avoidance), data/monster_abilities.json
// (base_damage, range, projectile_speed, path lob, radius, windup, cooldown, ep_cost),
// systems/enemy/enemy_mind_config_factory.gd::AVOIDANCE_PROFILES / DEFAULT_DASH_DIST (dash dodge),
// ENEMY_DESIGN.md:744-770 (a dash reacts to a straight bolt within 28 px and 0.6 s; areas and lobs cannot be
// dashed), data/monster_abilities.json astelia:arc_bolt (the shaman's lob targets a lawful actor, so its release re-checks
// the target; ENEMY_DESIGN.md:546's point locked at windup start is for point / area actions), COMBAT_DESIGN.md:207-217 (a
// committed cast is never interrupted, a dash does not cancel it), COMBAT_DEFENSE.md:35-60 (hits are geometric,
// no to-hit roll), COMBAT_DEFENSE.md:491-520 (projectiles hit any body, allies included, for full damage; an
// area spares only its source), balance.json native_encounter_timing (group decisions at 5 Hz).
// Ranges are authored centre to centre; the sandbox measures melee and shot reach edge to edge, so it uses the
// authored range minus the attacker's radius and a typical target radius (12 px).
// Health, energy and damage are what the game's build derives for each kind at common rarity and its lowest
// evolution (brute and spitter Evo0, shaman Evo1, its min_evo): native/encounter_core/src/build/
// actor_build_compiler.cpp::ActorBuildCompiler::resolve and ::pool_value with the kind's traits
// (data/traits/monsters.json), damage = base_damage x stat_factor (combat_content_store.cpp::stat_factor).
// Energy regeneration: modules/astelia_core/progression/ep_aura.gd::base_regen_per_s + ::stat_regen_per_s
// (FM_540) from the derived stats. Damage before mitigation (not modelled).
const GAME = {
	melee:     { kind: 'brute',   hp: 258, speed: 40, r: 16, dmg: 19.5, reach: 64,  windup: 0.45, cd: 1.8, ep: 0,     epRegen: 0,  cost: 0,  dodge: null },
	ranged:    { kind: 'spitter', hp: 92,  speed: 55, r: 9,  dmg: 10.4, reach: 280, windup: 0.55, cd: 1.4, ep: 168,   epRegen: 22.3, cost: 6,  dodge: 'kiter', shot: 240 },
	artillery: { kind: 'shaman',  hp: 181, speed: 55, r: 10, dmg: 18,   reach: 320, windup: 0.7,  cd: 1.2, ep: 324.8, epRegen: 34.0, cost: 10, dodge: 'storm', lob: 300, radius: 40 },
	dodge: { kiter: { cd: 0.9, p: 0.8, dist: 60 }, storm: { cd: 1.0, p: 0.9, dist: 110 } },
	dodgeReach: 28, dodgeTtc: 0.6, typicalR: 12, thinkEvery: 0.2,
	// Protection from the kinds' traits (data/traits/monsters.json: thick_hide +0.2, warded +0.15), applied as
	// damage x (1 - protection), floored to whole health (DEFENSE_MODEL_DISTILLED.md:30-33, FORMULAS.md FM_250).
	protection: { melee: 0.2033, ranged: 0.1524, artillery: 0.1547 },   // trait + natural (ActorBuildCompiler::resolve)
	// Kiter kinds keep a standoff: kite_max = max(150, 0.9 range), standoff = min(0.6 kite_max, 0.8 range)
	// (systems/enemy/enemy_mind_config_factory.gd::build), backing off at x0.5 (FM_640 backpedal for a kiter).
	kiterBackpedal: 0.5,
	// Melee approach a point on a ring around the target, radius max(2 r, 0.65 reach), phased by identity
	// (native/encounter_core/src/ai/encounter_ai.cpp, kAttackArcReachFraction).
	ringReach: 0.65,
};
// Every kind the game's Skirmish 60 preset fields (systems/dev/dev_presets.gd::SKIRMISH60_FIGHT), derived the same
// way (native build at common rarity, base evo, tolerance caps): role = the sandbox formation role it takes.
GAME.kinds = {
	brute:   Object.assign({ role: 'melee' }, GAME.melee, { prot: 0.2033 }),
	warden:  Object.assign({ role: 'melee' }, GAME.melee, { kind: 'warden', ep: 176.25, epRegen: 21.4, prot: 0.2033,
		block: { cost: 40, cd: 2.0, dur: 1.0, mult: 0.5, halfArc: Math.PI / 2 } }),   // encounter_ai.cpp block; prepared_block_multiplier
	hound:   { role: 'melee', kind: 'hound',  hp: 106, speed: 95,  r: 6, dmg: 7.5, reach: 56, windup: 0.2,  cd: 0.8, ep: 0, epRegen: 0, cost: 0, prot: 0.0017, dodge: null },
	runner:  { role: 'melee', kind: 'runner', hp: 53,  speed: 110, r: 6, dmg: 9,   reach: 60, windup: 0.25, cd: 1.0, ep: 0, epRegen: 0, cost: 0, prot: 0.0009, dodge: 'skittish' },
	spitter: Object.assign({ role: 'ranged', prot: 0.1524 }, GAME.ranged),
	shaman:  Object.assign({ role: 'artillery', prot: 0.1547 }, GAME.artillery),
};
GAME.dodge.skittish = { cd: 0.7, p: 1.0, dist: 60, chip: true };   // enemy_mind_config_factory.gd::AVOIDANCE_PROFILES
// Temporal speed (FORMULAS.md FM_520 ACC, FM_530 R_logic; modules/astelia_core/progression/acceleration.gd::breakdown):
// ACC from each kind's derived stats (comp_share 0.2, aura 1.3 from Evo1); the player is the frame of reference,
// every other actor runs at its ACC / the player's ACC (capped at 4); projectiles launch at
// x clamp(1 + 0.2 (ACC - 1), 1, 8) (FM_156/157). Without a player present nothing is re-timed.
GAME.acc = { brute: 2.62, warden: 2.62, hound: 3.31, runner: 3.31, spitter: 2.62, shaman: 4.48, player: 6.62 };
GAME.launch = (acc) => Math.min(8, Math.max(1, 1 + 0.2 * (acc - 1)));
GAME.lowHpSurvival = 0.35;   // at or below: dash propensity 1 and chip dodging forced (kiter, storm, skittish)
GAME.roleKind = { melee: 'brute', ranged: 'spitter', artillery: 'shaman' };
// The player in Skirmish 60: profile combat_ready (Evo1 combat build: systems/dev/dev_profiles.gd::combat_seed),
// pools and attacks derived from the native build (combat_content_store.cpp: fire scale 2.0, range x1.85, launch
// speed x2.12 from ACC 6.62); cast times in action seconds, ACC otherwise taken as 1 (temporal core not modelled).
// Four auto limbs (2 hands + 2 aura) each cycle fire_bolt -> fire_lance; aura limbs pay x1.1025 EP; auto limbs
// stop at a 10% EP reserve (balance.json reserve.floor_frac). Manual: ember_bolt, cinder_pulse, base_dash.
GAME.player = {
	hp: 763, ep: 689.5, epRegen: 42.1, speed: 120, r: 9, prot: 0.0122, reserve: 0.1,
	bolt:  { dmg: 24,  ep: 20,    cast: 0.40, speed: 765, range: 666 },
	lance: { dmg: 48,  ep: 40,    cast: 0.80, speed: 893, range: 778, pierce: 2 },
	ember: { dmg: 140, ep: 116.7, cast: 2.33, speed: 893, range: 666 },
	pulse: { dmg: 180, ep: 215.2, cast: 4.30, radius: 130 },
	dash:  { ep: 10, cd: 0.3, dist: 112, time: 0.45 },   // data/deliveries/core.json base_dash (ignores the surround slow)
	// Surround slow (FORMULAS.md FM_600, balance.json horde): n bodies within 40 px of the player, t = min(1, n / 8),
	// move x lerp(1, 0.6, t); at t >= 0.66 manual casts are interrupted.
	surround: { radius: 40, max: 8, floor: 0.6, interrupt: 0.66 },
	limbs: [1, 1, 1.1025, 1.1025],
	// Every fire attack applies a burn stack (data/magic/catalog.json on_hit astelia:burn; content/effects/burn.md:
	// duration 4 s, independent stacks, capacity 5): total damage seed_factor 0.2 x the landed hit over the duration
	// (FORMULAS.md FM_270; effect_application_policy.cpp: the seeded rate replaces the flat one), ticks unmitigated.
	burn: { seed: 0.2, dur: 4.0, cap: 5 },
};
const standoffOf = (g) => Math.min(0.6 * Math.max(150, 0.9 * g.reach), 0.8 * g.reach);
// The shared stat tables hold the sandbox values or the game's; every battle in a process uses the same rules,
// and create() switches the tables when a battle's rules differ from the last one's.
ROLE.player = { hp: 763, speed: 120, r: 9, range: 666, dmg: 24, cd: 0 };
const SANDBOX_ROLE = JSON.parse(JSON.stringify(ROLE));
let RULES_NOW = 'sandbox';
function applyRules(name) {
	if (name === RULES_NOW) return;
	for (const r of Object.keys(SANDBOX_ROLE)) Object.assign(ROLE[r], SANDBOX_ROLE[r]);
	if (name === 'game') for (const r of ['melee', 'ranged', 'artillery']) {
		const g = GAME[r];
		Object.assign(ROLE[r], { hp: g.hp, speed: g.speed, r: g.r, dmg: g.dmg, cd: g.cd,
			range: r === 'artillery' ? g.reach : g.reach - g.r - GAME.typicalR });
		if (r === 'artillery') Object.assign(ROLE.artillery, { minRange: 0, splash: g.radius, flight: 0.8 });   // flight: a planning estimate; a lob lands after distance / lob speed
		if (r === 'ranged') ROLE.ranged.shot = g.shot;
	}
	RULES_NOW = name;
}
const isGame = (w) => w.o.rules === 'game';
// Finishing (game rules), defined here only: they have 2 or fewer left, or we outnumber them 4 to 1. Standing off
// never ends such a fight (the last guns sit outside every reach) and every attacker counts: the commander closes in
// (rule 'few'; the look-ahead compares only closing plans) and the wounded keep fighting (saveWounded).
const finishingCounts = (ours, theirs) => theirs > 0 && (theirs <= 2 || ours >= 4 * theirs);
const finishing = (w, t) => isGame(w) && finishingCounts(team(w, t).length, foes(w, t).length);
// Game rules: a cast starts once the cooldown is over and a target is in reach, with the energy (paid at start) and,
// for a shot, a lane free of pack-mates; the cooldown runs from the cast start (ARCHITECTURE.md:2706-2708); a
// started cast always runs to its release, which re-checks the target. gamePrep is the rules only: whether the leader
// wants the cast to start now (fire control, waves) is the unit's decision, castPermit, made beforehand.
const couldStart = (w, u) => { const t = u.target; return !(u.prep > 0) && u.cd <= 0 && !!u._inReach && !!t && t.alive && !(u.cost && u.ep < u.cost); };
function gamePrep(w, u, dt) {
	if (!windUp(w, u)) return;
	if (!(u.prep > 0)) {
		if (!couldStart(w, u)) return;
		// Attack admission cap (an arena knob: Skirmish 60 uses 6): at most that many casts of a team at once.
		if (w.o.attackerCap && team(w, u.team).filter((x) => x.prep > 0).length >= w.o.attackerCap) return;
		if (!u.castOk) return;
		if (u.role === 'ranged' && !laneClear(w, u, u.target)) return;
		if (u.cost) u.ep -= u.cost;
		u.cd = u.cdMax;
		u.prep = 0;
		u.castT = w.t;
	}
	u.prep += dt;
}
// Fire control (our decision, the leader's), asked of every unit that could start a cast now, once all have decided:
// start, or hold. holdFire (see fireGate) and waves (start together once enough of ours are ready, or after 1 s of
// waiting).
function castPermit(w, u) {
	if (!isGame(w) || !windUp(w, u) || !couldStart(w, u)) return true;
	if (sk(w, u.team, 'holdFire') && !fireGate(w, u)) return false;
	const wv = sk(w, u.team, 'waves');
	if (wv > 0) {
		const readyN = team(w, u.team).filter((x) => x._inReach && x.cd <= 0 && !(x.prep > 0) && x.windup).length;
		if (u.waitFrom === undefined) u.waitFrom = w.t;
		if (readyN < wv && w.t - u.waitFrom < 1.0) return false;
		u.waitFrom = undefined;
	}
	return true;
}
// Game dash dodge (kinds with a dodge profile): a hostile straight shot whose line passes within dodgeReach of
// the unit and reaches it within dodgeTtc, with the profile's chance, when its dash is off cooldown: an instant
// dash of the profile's distance across the shot's line. It does not cancel a committed cast.
// The mind dodges only the player's shots (encounter_autonomy_cognition.cpp), and only a manual shot unless the
// profile dodges chip or the unit is at or below lowHpSurvival health (then propensity 1, chip forced); time to
// contact at least 0.05 s (kDashReactMinimum); one roll per shot; the dash goes across the shot, toward the
// target for a chaser and away for a keeper (encounter_ai.cpp). The profile cooldown is applied as authored.
function gameDash(w, u) {
	const P = u.dodgeProf;
	if ((u.dashReady ?? 0) > w.t) return;
	const low = u.hp <= GAME.lowHpSurvival * u.maxhp;
	for (const s of w.shots) {
		if (!s.aimed || s.src.team === u.team || !s.src.isPlayer || !(s.manual || P.chip || low)) continue;
		const px = u.x - s.x, py = u.y - s.y, along = px * s.dx + py * s.dy;
		if (along <= 0 || along > Math.min(s.left, s.speed * GAME.dodgeTtc) || along / s.speed < 0.05) continue;
		if (Math.abs(px * s.dy - py * s.dx) > GAME.dodgeReach) continue;
		u._rolled = u._rolled || new Set();
		if (u._rolled.has(s)) continue;
		u._rolled.add(s);
		const roll = rng(((w.o.seed * 9301) ^ (Math.round(w.t * 30) * 49297) ^ (u.id * 233280)) >>> 0 || 1)();
		if (roll >= (low ? 1 : P.p)) continue;
		u.dashReady = w.t + P.cd / (u.tr || 1);
		// Side: toward the target for a chaser (melee), away from the shooter for a keeper.
		const ref = MELEE[u.role] && u.target ? { x: u.target.x - u.x, y: u.target.y - u.y } : { x: u.x - s.src.x, y: u.y - s.src.y };
		const side = (s.dy * ref.x - s.dx * ref.y) >= 0 ? 1 : -1;
		u.x = clamp(u.x + s.dy * P.dist * side, u.r, w.o.width - u.r); u.y = clamp(u.y - s.dx * P.dist * side, u.r, w.o.height - u.r);
		MOVES.n++; lgMoved(u); u.state = 'dash'; w.stats.dashes = (w.stats.dashes || 0) + 1;
		return;
	}
}
// Warden block (encounter_ai.cpp): a manual player projectile reaching it in 0.05-0.6 s raises a guard when the
// block is off cooldown and it has the energy: pays cost, guards for dur s facing the threat, holds still and does
// not attack; hits from within halfArc of the guard direction take x mult (applied after protection).
function gameBlock(w, u) {
	const B = u.block;
	if (u.guardUntil > w.t || (u.blockReady ?? 0) > w.t || u.ep < B.cost) return;
	for (const s of w.shots) {
		if (!s.aimed || !s.src.isPlayer || !s.manual) continue;
		const px = u.x - s.x, py = u.y - s.y, along = px * s.dx + py * s.dy, ttc = along / s.speed;
		if (along <= 0 || ttc < 0.05 || ttc > GAME.dodgeTtc || Math.abs(px * s.dy - py * s.dx) > u.r + 4) continue;
		u.ep -= B.cost; u.blockReady = w.t + B.cd / (u.tr || 1); u.guardUntil = w.t + B.dur / (u.tr || 1);
		u.guardDir = Math.atan2(s.src.y - u.y, s.src.x - u.x);
		return;
	}
}
// A unit's game-only fields: energy pool, cost per cast, dash profile.
function gameUnit(u) {
	if (u.role === 'player') return gamePlayer(u);
	const K = (u.w && u.w.kinds) || GAME.kinds, g = K[u.kind || GAME.roleKind[u.role]];
	if (!g) return;
	u.kind = u.kind || GAME.roleKind[u.role];
	const kiter = g.kind === undefined ? !!g.dodge && g.role !== 'melee' : false;
	Object.assign(u, { hp: g.hp, maxhp: g.hp, speed: g.speed, baseSpeed: g.speed, r: g.r, dmg: g.dmg, cdMax: g.cd, windup: g.windup,
		range: g.role === 'artillery' ? g.reach : g.reach - g.r - GAME.typicalR,
		ep: g.ep, epMax: g.ep, epRegen: g.epRegen, cost: g.cost, dodgeProf: g.dodge && GAME.dodge[g.dodge], dashSide: (u.id & 1) ? -1 : 1,
		prot: g.prot ?? GAME.protection[u.role] ?? 0, minRange: g.role === 'artillery' ? (g.minRange ?? 0) : undefined, standoff: (u.role === 'ranged' || u.role === 'artillery') ? standoffOf(g) : 0, block: g.block || null,
		launch: g.launch ?? GAME.launch(GAME.acc[u.kind] || 1), tr: 1,
		// A unit set's kinds carry their own projectile numbers (unitSet); the game's kinds use the shared ones.
		lob: g.lob, splash: g.radius, shotSpeed: g.shot });
	retime(u);
	void kiter;
}
// Re-time a unit to the player's frame when a player is present (w.timeRef = the player's ACC).
function retime(u) {
	const ref = u.w && u.w.timeRef;
	u.tr = ref ? Math.min(4, (GAME.acc[u.kind] || ref) / ref) : 1;
	u.speed = u.baseSpeed * u.tr;
}
function gamePlayer(u) {
	const P = GAME.player;
	Object.assign(u, { hp: P.hp, maxhp: P.hp, speed: P.speed, baseSpeed: P.speed, r: P.r, ep: P.ep, epMax: P.ep, epRegen: P.epRegen,
		prot: P.prot, isPlayer: true, range: P.bolt.range, dmg: P.bolt.dmg, cdMax: 0,
		limbs: P.limbs.map((m) => ({ mult: m, seq: 0, prep: 0, target: null })), manual: null, dashReady: 0, dashUntil: 0 });
}

function rng(seed) {
	let s = seed >>> 0 || 1;
	const f = () => { s ^= s << 13; s >>>= 0; s ^= s >>> 17; s ^= s << 5; s >>>= 0; return s / 4294967296; };
	f.state = () => s;   // a copy of the world continues the same sequence (cloneRng)
	return f;
}
const cloneRng = (r) => rng(r.state());
const len = (x, y) => Math.hypot(x, y);
const clamp = (v, a, b) => Math.max(a, Math.min(b, v));
const dist = (a, b) => len(a.x - b.x, a.y - b.y);
const gap = (a, b) => dist(a, b) - a.r - b.r;

// ---------------------------------------------------------------- shapes
// Local slots {d, l} per role: d = depth behind the front edge, l = lateral offset.
const rowOf = (n, spacing, d, stagger) => Array.from({ length: n }, (_, i) => ({ d, l: (i - (n - 1) / 2) * spacing + (stagger || 0) }));
function ranks(n, perRank, spacing, d0, rankSpacing) {
	const out = [];
	for (let r = 0; out.length < n; r++) {
		const k = Math.min(perRank, n - out.length);
		out.push(...rowOf(k, spacing, d0 + r * rankSpacing, r % 2 ? spacing / 2 : 0));
	}
	return out;
}
const maxD = (slots, fallback) => slots.length ? Math.max(...slots.map((s) => s.d)) : fallback;
const SHAPES = {
	line(c, f) {
		const per = Math.max(1, Math.ceil(c.ranged / f.rangedRanks));
		const rear = f.screenGap + f.rankSpacing * f.rangedRanks + f.rearGap;
		return { melee: rowOf(c.melee, f.frontSpacing, 0),
			ranged: ranks(c.ranged, per, f.rankSpacing, f.screenGap, f.rankSpacing),
			artillery: rowOf(c.artillery, f.frontSpacing * 1.4, rear) };
	},
	wedge(c, f) {
		const melee = c.melee ? [{ d: 0, l: 0 }] : [];
		for (let i = 1; melee.length < c.melee; i++) {
			melee.push({ d: i * f.frontSpacing * 0.55, l: i * f.frontSpacing * 0.8 });
			if (melee.length < c.melee) melee.push({ d: i * f.frontSpacing * 0.55, l: -i * f.frontSpacing * 0.8 });
		}
		const ranged = [];
		for (let r = 0; ranged.length < c.ranged; r++) {
			const k = Math.min(3 + r * 2, c.ranged - ranged.length);
			ranged.push(...rowOf(k, f.rankSpacing, f.screenGap + r * f.rankSpacing * 0.8));
		}
		return { melee, ranged, artillery: rowOf(c.artillery, f.frontSpacing * 1.2, maxD(ranged, f.screenGap) + f.rearGap) };
	},
	box(c, f) {
		const cols = 8, depth = Math.ceil(c.ranged / cols);
		const ranged = ranks(c.ranged, cols, f.rankSpacing, f.screenGap, f.rankSpacing);
		const halfW = (cols - 1) / 2 * f.rankSpacing + f.frontSpacing * 0.8;
		const front = Math.ceil(c.melee / 2), side = c.melee - front;
		const melee = rowOf(front, (halfW * 2) / Math.max(1, front - 1), 0);
		for (let i = 0; i < side; i++) melee.push({ d: f.screenGap + (Math.floor(i / 2) + 0.5) * f.rankSpacing * 1.5, l: i % 2 ? -halfW : halfW });
		return { melee, ranged, artillery: rowOf(c.artillery, f.rankSpacing * 1.3, f.screenGap + depth * f.rankSpacing + f.rearGap * 0.6) };
	},
	column(c, f) {
		const ranged = ranks(c.ranged, 5, f.rankSpacing, f.screenGap + f.rankSpacing, f.rankSpacing);
		const melee = ranks(c.melee, 5, f.frontSpacing * 0.7, 0, f.rankSpacing);
		return { melee, ranged, artillery: ranks(c.artillery, 5, f.rankSpacing * 1.2, maxD(ranged, f.screenGap) + f.rearGap, f.rankSpacing) };
	},
	screen(c, f) {
		const melee = ranks(c.melee, 5, f.frontSpacing * 0.6, 0, f.rankSpacing);
		const half = Math.ceil(c.ranged / 2), off = 5 * f.frontSpacing * 0.6 / 2 + 3 * f.rankSpacing;
		const block = (n, side) => ranks(n, 5, f.rankSpacing, f.screenGap * 0.6, f.rankSpacing).map((s) => ({ d: s.d, l: s.l + side * off }));
		const ranged = [...block(half, -1), ...block(c.ranged - half, 1)];
		return { melee, ranged, artillery: rowOf(c.artillery, f.frontSpacing * 1.2, maxD(ranged, f.screenGap) + f.rearGap) };
	},
	crescent(c, f) {
		const arc = (n, radius, d0, spread) => Array.from({ length: n }, (_, i) => {
			const a = n === 1 ? 0 : (i / (n - 1) - 0.5) * spread;
			return { d: d0 - radius * (1 - Math.cos(a)), l: radius * Math.sin(a) };
		});
		const R = Math.max(80, f.frontSpacing * c.melee / 2);
		const ranged = [...arc(Math.ceil(c.ranged / 2), R, f.screenGap, 1.6), ...arc(Math.floor(c.ranged / 2), R, f.screenGap + f.rankSpacing, 1.5)];
		return { melee: arc(c.melee, R, 0, 1.8), ranged, artillery: rowOf(c.artillery, f.frontSpacing * 1.2, f.screenGap + f.rankSpacing * 2 + f.rearGap) };
	},
	ring(c, f) {
		const circ = (n, radius, cd) => Array.from({ length: n }, (_, i) => {
			const a = (i / Math.max(1, n)) * Math.PI * 2;
			return { d: cd - Math.cos(a) * radius, l: Math.sin(a) * radius };
		});
		const Rm = Math.max(90, 10 * f.frontSpacing / (Math.PI * 2) * 1.6);
		const inner = Math.ceil(c.ranged * 0.6);
		return { melee: circ(c.melee, Rm, Rm), ranged: [...circ(inner, Rm - 26, Rm), ...circ(c.ranged - inner, Rm - 48, Rm)],
			artillery: circ(c.artillery, 26, Rm) };
	},
};

function makeUnit(id, team, role, x, y) {
	const d = ROLE[role];
	return { id, team, role, x, y, hp: d.hp, maxhp: d.hp, speed: d.speed, r: d.r, range: d.range,
		dmg: d.dmg, cdMax: d.cd, cd: 0, target: null, alive: true, slotX: x, slotY: y, hasSlot: false,
		meleeAttacker: null, meleeAt: -1, dealt: 0, vx: 0, vy: 0, svx: 0, svy: 0, strafe: id % 2 ? 1 : -1, state: 'idle' };
}

function resolveF(opt) {
	const f = Object.assign({}, DEFAULT_F);
	opt = opt || {};
	if (opt.preset && PRESETS[opt.preset]) Object.assign(f, PRESETS[opt.preset]);
	return Object.assign(f, opt);
}

function newPack(w, team, brain, f) {
	const left = team === 0;
	return { team, brain, base: f, f: Object.assign({}, f),
		anchor: { x: left ? 240 : w.o.width - 240, y: w.o.height / 2, ax: left ? 1 : -1, ay: 0 },
		formed: false, diving: false, waiting: false, zone: null, phase: 'forming', pending: new Map(),
		flank: { phase: 'none', since: 0, wings: new Map() }, plan: null, planSince: -99, planWhy: '',
		packFocus: null, squadFocus: new Map(), inZone: () => false, threatens: () => false };
}

// mode = our brain: 'alone' | 'formation' | 'reactive'. options.enemy = the mirror army's brain.
function create(mode, options) {
	const o = Object.assign({}, DEFAULTS, options || {});
	applyRules(o.rules || 'sandbox');
	// Game rules: these kinds have none of the sandbox's invented abilities; shots fly at the authored speed.
	if (o.rules === 'game') Object.assign(o, { abilities: !!o.sandboxAbilities, shotSpeed: GAME.ranged.shot, windUp: true });   // sandboxAbilities: the old invented abilities on top of the game's numbers (hand.html); results with it on are a separate setting
	const rand = rng(o.seed);
	const w = { mode, o, rand, t: 0, units: [], shots: [], shells: [], nextId: 1, spawnQueue: [], events: [], meleeHits: [],
		stats: { melee: 0, ranged: 0, artillery: 0, wasted: 0, monsterDeaths: 0, hunterKills: 0, aliveSeconds: 0, enemyDamage: 0 },
		packs: {}, hitLog: [], unitVer: 0, _tv: -1 };
	w.ai = [buildProfile(mode, o, 0), buildProfile(mode, o, 1)];
	// Unit set (option unitSet { kinds: { name: { role, stats } }, army: [[name, count]] }, game rules): both sides
	// field the same kinds; a kind's role is how it attacks (contact / straight shot / lob).
	if (o.unitSet) w.kinds = Object.assign({}, GAME.kinds, o.unitSet.kinds);
	const add = (team, role, x, y, kind) => { const u = makeUnit(w.nextId++, team, role, x, y); u.w = w; if (kind) u.kind = kind; if (o.rules === 'game') gameUnit(u); w.units.push(u); w.unitVer++; return u; };
	// One layout drawn once; the mirror army gets its exact reflection.
	const layout = [], army = o.army || { melee: 10, ranged: 30, artillery: 10 };
	const zone = { melee: [240, 60, 120], ranged: [150, 90, 150], artillery: [80, 60, 120] };
	const place = (role, kind) => { const z = zone[role]; layout.push([role, z[0] + rand() * z[1], o.height / 2 - z[2] + rand() * 2 * z[2], kind]); };
	if (o.unitSet) { for (const [k, n] of o.unitSet.army) for (let i = 0; i < n; i++) place(o.unitSet.kinds[k].role, k); }
	else {
		for (let i = 0; i < army.melee; i++) place('melee');
		for (let i = 0; i < army.ranged; i++) place('ranged');
		for (let i = 0; i < army.artillery; i++) place('artillery');
	}
	// A carried army (gauntlet): only these survivors, at their current hp, take the field.
	if (o.ours) {
		const left = layout.slice(), ours = [];
		for (const c of o.ours) {
			const i = left.findIndex(([role, , , kind]) => role === c.role && (kind || null) === (c.kind || null));
			const spot = i >= 0 ? left.splice(i, 1)[0] : [c.role, 200, o.height / 2];
			ours.push(Object.assign(add(0, c.role, spot[1], spot[2], c.kind), { hp: c.hp }));
		}
	} else if (o.scenario === 'skirmish') {
		// Skirmish 60 (systems/dev/dev_presets.gd::SKIRMISH60_FIGHT): 18 monsters from the preset's kinds, 8 alive at
		// once, the rest arriving as others fall; the player opposite. Kinds are drawn from the list per spawn.
		const S = Object.assign({ count: 18, maxAlive: 8, kinds: ['spitter', 'hound', 'brute', 'shaman', 'runner', 'warden'] }, o.skirmishSet);
		w.skirmish = { left: S.count, maxAlive: S.maxAlive, kinds: S.kinds, spawnRand: rng((o.seed * 7919) >>> 0 || 1) };
		if (o.temporal !== false) w.timeRef = GAME.acc.player;   // the player is the frame of reference
		while (w.skirmish.left > 0 && team(w, 0).length < S.maxAlive) skirmishSpawn(w, add);
		add(1, 'player', o.width - 260, o.height / 2);
	} else for (const [role, x, y, kind] of layout) add(0, role, x, y, kind);
	// The mirror army is the exact reflection, including each unit's preferred strafe side.
	if (o.scenario === 'mirror' && o.enemyArmy) {
		// A differently sized enemy army (option enemyArmy {melee, ranged, artillery}): its own layout,
		// spread over a taller band so a bigger army fits.
		const ea = o.enemyArmy, k = Math.max(1, (ea.melee + ea.ranged + ea.artillery) / 50);
		const band = (h) => Math.min(o.height - 40, h * Math.sqrt(k));
		for (let i = 0; i < ea.melee; i++) add(1, 'melee', o.width - (240 + rand() * 60 * k), o.height / 2 - band(240) / 2 + rand() * band(240));
		for (let i = 0; i < ea.ranged; i++) add(1, 'ranged', o.width - (150 + rand() * 90 * k), o.height / 2 - band(300) / 2 + rand() * band(300));
		for (let i = 0; i < ea.artillery; i++) add(1, 'artillery', o.width - (80 + rand() * 60 * k), o.height / 2 - band(240) / 2 + rand() * band(240));
	} else if (o.scenario === 'skirmish') {
		// the player is placed above
	} else if (o.scenario === 'mirror') layout.forEach(([role, x, y, kind], i) => { add(1, role, o.width - x, y, kind).strafe = -((w.units[i] && w.units[i].team === 0) ? w.units[i].strafe : 1); });
	else {
		for (let i = 0; i < o.hunters.melee; i++) spawnHunter(w, 'hunter');
		for (let i = 0; i < o.hunters.archers; i++) spawnHunter(w, 'archer');
	}
	// Each side's brain from its profile: a pack for every brain except 'alone'.
	for (const t of [0, 1]) {
		const b = w.ai[t].brain;
		if (b === 'alone' || (t === 1 && o.scenario !== 'mirror')) continue;
		const f = b === 'storm' || b === 'wolfpack' || b === 'gamepack' ? BRAINS[b].base : b === 'rules' && !w.ai[t].formation.preset ? Object.assign({ preset: 'wide line' }, w.ai[t].formation) : w.ai[t].formation;
		w.packs[t] = newPack(w, t, b === 'rules' ? 'reactive' : b, resolveF(f));
	}
	if (o.swapSides) {
		for (const u of w.units) { u.x = o.width - u.x; u.slotX = u.x; u.strafe = -u.strafe; }
		for (const k of [0, 1]) if (w.packs[k]) { const A = w.packs[k].anchor; A.x = o.width - A.x; A.ax = -A.ax; }
	}
	w.anchor = w.packs[0] ? w.packs[0].anchor : null;
	return w;
}

// A Skirmish 60 arrival: a kind drawn from the preset's list, entering on our side's edge.
function skirmishSpawn(w, add) {
	const S = w.skirmish, kind = S.kinds[Math.floor(S.spawnRand() * S.kinds.length)], g = GAME.kinds[kind];
	const u = (add || ((t, r, x, y) => { const v = makeUnit(w.nextId++, t, r, x, y); v.w = w; w.units.push(v); w.unitVer++; if (w._lg) lgPut(w, v); return v; }))
		(0, g.role, 90 + S.spawnRand() * 160, 120 + S.spawnRand() * (w.o.height - 240));
	u.kind = kind; gameUnit(u);
	S.left--;
	return u;
}
function spawnHunter(w, role) {
	const u = makeUnit(w.nextId++, 1, role, w.o.width - 60 - w.rand() * 80, 80 + w.rand() * (w.o.height - 160));
	u.w = w; w.units.push(u); w.unitVer++;
	if (w._lg) lgPut(w, u);
}

// Alive units per team, cached until membership changes (a death or a new unit bumps w.unitVer).
// Callers must not mutate the returned arrays.
function team(w, t) {
	if (w._tv !== w.unitVer) {
		w._tc = [[], []];
		for (const u of w.units) if (u.alive) w._tc[u.team].push(u);
		w._tv = w.unitVer;
	}
	return w._tc[t];
}
// Alive melee per team, in team order, cached with team().
function teamMelee(w, t) {
	const all = team(w, t);
	if (w._tmv !== w._tv || !w._tm) { w._tm = [null, null]; w._tmv = w._tv; }
	return w._tm[t] || (w._tm[t] = all.filter((u) => MELEE[u.role]));
}
// What a side knows (option perception: true, off by default: the arena is small, everyone sees everyone): the enemies within PERCEPTION_PX of any of its
// own units, shared by the pack. The game's Evo0 monster sight reach: balance.json sense.sight reach_by_evo_m[0]
// 40 m x monster_scale 0.6 = 24 m = 768 px; one radius for every monster (the full Sense law is not ported). The
// player sees everything (a human sees the screen). Decisions read foes(); physics always uses every unit.
const PERCEPTION_PX = 768;
function foes(w, t) {
	const all = team(w, 1 - t);
	if (!isGame(w) || w.o.perception !== true || team(w, t).some((u) => u.isPlayer)) return all;
	if (w._foeT === w.t && w._foeV === w.unitVer && w._foe && w._foe[t]) return w._foe[t];
	if (w._foeT !== w.t || w._foeV !== w.unitVer) { w._foe = [null, null]; w._foeT = w.t; w._foeV = w.unitVer; }
	const ours = team(w, t), r2 = PERCEPTION_PX * PERCEPTION_PX;
	return (w._foe[t] = all.filter((e) => ours.some((u) => (u.x - e.x) ** 2 + (u.y - e.y) ** 2 <= r2)));
}
const monsters = (w) => team(w, 0);
const hunters = (w) => team(w, 1);

function nearest(from, list, filter) {
	let best = null, bd = Infinity;
	for (const u of list) {
		if (u === from || (filter && !filter(u))) continue;
		const d = dist(u, from);
		if (d < bd) { bd = d; best = u; }
	}
	return best;
}

function moveToward(u, x, y, dt, stopAt) {
	const dx = x - u.x, dy = y - u.y, d = len(dx, dy), s = stopAt || 0;
	if (d <= s + 0.5) return;
	const step = Math.min(u.speed * dt, d - s);
	u.x += dx / d * step; u.y += dy / d * step;
	MOVES.n++; lgMoved(u);
}
// Counts unit moves, so a remembered lane check knows when any blocker may have moved.
const MOVES = { n: 0 };

// The first unit (nearest along the line) whose body the line from (ax, ay) to b crosses. Candidates come from
// the live grid (cells around the segment); equal distances go to the unit earliest in w.units (lowest id), so
// the result is what a scan of every unit in order finds.
function lineBlocker(w, ax, ay, b, shooter) {
	const dx = b.x - ax, dy = b.y - ay, L = len(dx, dy);
	if (L < 1) return null;
	const nx = dx / L, ny = dy / L;
	let best = null, bt = L - b.r;
	if (!w._lg) lgBuild(w);
	const x0 = Math.floor((Math.min(ax, b.x) - 12) / LG), x1 = Math.floor((Math.max(ax, b.x) + 12) / LG);
	const y0 = Math.floor((Math.min(ay, b.y) - 12) / LG), y1 = Math.floor((Math.max(ay, b.y) + 12) / LG);
	for (let cx = x0; cx <= x1; cx++) for (let cy = y0; cy <= y1; cy++) {
		const c = w._lg.get(cx * 4096 + cy);
		if (c) for (const u of c) {
			if (!u.alive || u === b || u === shooter) continue;
			const px = u.x - ax, py = u.y - ay, t = px * nx + py * ny;
			if (t <= 0 || t > bt || (t === bt && !(best && u.id < best.id))) continue;
			if (Math.abs(px * ny - py * nx) < u.r + 1.5) { bt = t; best = u; }
		}
	}
	return best;
}
// Live grid of alive units (cell LG px), kept current as units move (lgMoved), die (lgRemove) or are added.
const LG = 40;
const lgKey = (x, y) => Math.floor(x / LG) * 4096 + Math.floor(y / LG);
function lgBuild(w) { w._lg = new Map(); for (const u of w.units) if (u.alive) lgPut(w, u); }
function lgPut(w, u) { const k = lgKey(u.x, u.y); u._ck = k; let c = w._lg.get(k); if (!c) { c = []; w._lg.set(k, c); } c.push(u); }
function lgRemove(w, u) { if (!w._lg) return; const c = w._lg.get(u._ck); if (c) { const i = c.indexOf(u); if (i >= 0) c.splice(i, 1); } }
function lgMoved(u) {
	const w = u.w;
	if (!w || !w._lg) return;
	const k = lgKey(u.x, u.y);
	if (k !== u._ck) { lgRemove(w, u); lgPut(w, u); }
}
// Spatial grid of alive units for the shot phase (positions do not move while shots resolve). Candidates
// are visited in w.units order, so the first blocker found is exactly what a full scan would find.
const GRID = 64;
function buildGrid(w) {
	const g = new Map();
	w.units.forEach((u, i) => {
		if (!u.alive) return;
		u._i = i;
		const k = Math.floor(u.x / GRID) * 4096 + Math.floor(u.y / GRID);
		let c = g.get(k); if (!c) { c = []; g.set(k, c); } c.push(u);
	});
	return g;
}
function lineBlockerGrid(w, g, ax, ay, b, shooter) {
	const pad = 12;   // largest body radius + 1.5, rounded up
	const x0 = Math.floor((Math.min(ax, b.x) - pad) / GRID), x1 = Math.floor((Math.max(ax, b.x) + pad) / GRID);
	const y0 = Math.floor((Math.min(ay, b.y) - pad) / GRID), y1 = Math.floor((Math.max(ay, b.y) + pad) / GRID);
	if ((x1 - x0 + 1) * (y1 - y0 + 1) > 24) return lineBlocker(w, ax, ay, b, shooter);
	const cand = [];
	for (let cx = x0; cx <= x1; cx++) for (let cy = y0; cy <= y1; cy++) { const c = g.get(cx * 4096 + cy); if (c) for (const u of c) cand.push(u); }
	cand.sort((p, q) => p._i - q._i);
	const dx = b.x - ax, dy = b.y - ay, L = len(dx, dy);
	if (L < 1) return null;
	const nx = dx / L, ny = dy / L;
	let best = null, bt = L - b.r;
	for (const u of cand) {
		if (!u.alive || u === b || u === shooter) continue;
		const px = u.x - ax, py = u.y - ay, t = px * nx + py * ny;
		if (t <= 0 || t >= bt) continue;
		if (Math.abs(px * ny - py * nx) < u.r + 1.5) { bt = t; best = u; }
	}
	return best;
}
// Is the line from u to t free of our own units? Remembered for the same unit, target, positions and tick (a
// shooter asks up to three times per turn); any move of u or t, or a new tick, asks again.
const laneClear = (w, u, t) => {
	const m = u._lane;
	if (m && m.t === t && m.at === w.t && m.ux === u.x && m.uy === u.y && m.tx === t.x && m.ty === t.y && m.ver === MOVES.n) return m.ok;
	const b = lineBlocker(w, u.x, u.y, t, u), ok = !b || b.team !== u.team;
	u._lane = { t, at: w.t, ux: u.x, uy: u.y, tx: t.x, ty: t.y, ver: MOVES.n, ok };
	return ok;
};

function note(w, text, teamId) {
	if (w.rec) w.rec.events.push({ t: w.t, team: teamId || 0, text });
	w.events.push({ t: w.t, text: (teamId === 1 ? 'enemy: ' : '') + text });
	if (w.events.length > 80) w.events.shift();
}

function damage(w, src, dst, amount) {
	if (!dst.alive) return 0;
	if (isGame(w)) {
		let a = amount * (1 - (dst.prot || 0));   // protection
		if (dst.guardUntil > w.t && dst.block) {
			const d = Math.atan2(src.y - dst.y, src.x - dst.x) - dst.guardDir, wrap = Math.abs(Math.atan2(Math.sin(d), Math.cos(d)));
			if (wrap <= dst.block.halfArc) a *= dst.block.mult;
		}
		amount = Math.floor(a);   // whole health points
	}
	if (!MELEE[src.role]) {
		dst.lastShotHitT = w.t;
		if (dst.shieldUntil > w.t) { abStat(w, dst.team, 'shield', 'blocked', amount * ABIL.shield.block); amount *= 1 - ABIL.shield.block; }
	}
	const dealt = Math.min(amount, dst.hp);
	{
		const kind = MELEE[src.role] ? (amount > src.dmg * 1.2 ? 'charge hit' : 'melee hit')
			: src.role === 'artillery' ? (w._barrage ? 'barrage shell' : 'shell') : (amount > src.dmg * 1.2 ? 'aimed shot' : 'shot');
		if (dst.team === 0 && src.team === 1) { const tk = (w.stats.takenBy = w.stats.takenBy || {}); tk[kind] = (tk[kind] || 0) + dealt; }
		const ak = kind === 'charge hit' ? 'charge' : kind === 'aimed shot' ? 'aimed' : kind === 'barrage shell' ? 'barrage' : null;
		if (ak) abStat(w, src.team, ak, 'dmg', dealt);
		const bs = (w.stats.bySource = w.stats.bySource || {}); bs[kind] = (bs[kind] || 0) + dealt;
	}
	w.lastHitT = w.t;
	w.hitLog.push({ t: w.t, from: src.team, to: dst.team, amt: Math.min(amount, Math.max(0, dst.hp)) });
	dst.hp -= amount;
	if (MELEE[src.role]) { dst.meleeAttacker = src; dst.meleeAt = w.t; }
	if (src.team === 0) { w.stats[src.role] += dealt; src.dealt += dealt; } else w.stats.enemyDamage += dealt;
	// The player's fire attacks seed a burn from the landed hit (GAME.player.burn).
	if (src.isPlayer && dealt > 0 && !w._burnTick) {
		const B = GAME.player.burn, mine = (w.dots = w.dots || []).filter((d) => d.target === dst && d.until > w.t);
		if (mine.length < B.cap) w.dots.push({ target: dst, src, dps: B.seed * dealt / B.dur, until: w.t + B.dur, acc: 0 });
	}
	if (dst.hp <= 0) {
		// Fight recording (aar.js): who died, to what, doing what.
		if (w.rec) w.rec.deaths.push({ t: w.t, id: dst.id, team: dst.team, role: dst.role, state: dst.state, x: dst.x, y: dst.y, by: src.id, byRole: src.role, byTeam: src.team, atk: src.role === 'artillery' ? w._atk : undefined, flight: src.role === 'artillery' ? +w._shellAge.toFixed(2) : undefined });
		dst.alive = false; lgRemove(w, dst);
		w.unitVer++;
		if (dst.team === 1) {
			w.stats.hunterKills++;
			if (w.o.scenario === 'hunters') w.spawnQueue.push({ at: w.t + w.o.hunters.respawn, role: dst.role });
		} else { w.stats.monsterDeaths++; note(w, `lost ${dst.role} #${dst.id} to ${src.role}`); }
	}
	return dealt;
}

function addPending(w, shooter, t, amount) {
	const pack = w.packs[shooter.team];
	if (pack) pack.pending.set(t, (pack.pending.get(t) || 0) + amount);
}
// The movement a shooter leads with: smoothed over ~0.3 s (smoothLead), so side-to-side jinking fools it less.
// A side's skill (its AI profile).
const sk = (w, team, k) => w.ai[team].skills[k];
const vel = (w, h, team) => { const l = sk(w, team, 'lead'); return l === 'smooth' ? [h.svx, h.svy] : l === 'raw' ? [h.vx, h.vy] : [0, 0]; };
// Where a straight shot from (x, y) at `speed` meets h if h keeps its movement (time capped at 1.5 s).
function interceptPoint(w, x, y, h, speed, team) {
	const [vx, vy] = vel(w, h, team);
	let tau = dist({ x, y }, h) / speed;
	for (let i = 0; i < 3; i++) tau = Math.min(1.5, len(h.x + vx * tau - x, h.y + vy * tau - y) / speed);
	return { x: h.x + vx * tau, y: h.y + vy * tau, tau };
}
// Wind-up (world option windUp): once reloaded, an attack needs WINDUP[role] s of preparation; the release is
// instant and a unit may hold a prepared attack. Moving and dodging steps keep it; a dodge ability (disengage)
// breaks it (progress lost). The reload
// after a release is shortened by the wind-up, so the rate of fire is the same as without it.
const WINDUP = { ranged: 0.5, archer: 0.5, artillery: 1.0 };
const windUp = (w, u) => (isGame(w) ? u.windup || 0 : (w.o.windUp && WINDUP[u.role]) || 0);
const prepared = (w, u) => (isGame(w) ? u.prep > 0 : u.cd <= 0) && (u.prep || 0) >= windUp(w, u) - 1e-9;
// Release. Game rules: the cooldown already runs from the cast start; sandbox wind-ups shorten the reload so the
// rate of fire is unchanged.
function released(w, u) { u.prep = 0; if (!isGame(w)) u.cd = u.cdMax - windUp(w, u); }
// Can h sidestep an aimed shot from u? Not when its side does not dodge, nor a melee unit locked in a fight,
// nor when the shot arrives before h, at its current speed (a slow field halves it), can react and step
// its body width aside.
function canDodge(w, h, u) {
	if (w.o.shots !== 'aimed') return false;
	const sd = sk(w, h.team, 'dodgeShots');
	if (sd === false || (sd === 'soft' && MELEE[h.role])) return false;
	if (MELEE[h.role] && h.target && h.target.alive && gap(h, h.target) <= h.range) return false;
	return !u || dist(u, h) / w.o.shotSpeed - sk(w, h.team, 'shotReact') > (h.r + 3) / Math.max(1, h.speed);
}
// Fire control (skill fireControl): a shot counts toward its target's pending damage by its chance to hit
// (the side's measured hit rate on dodging targets, 0.9 on targets that cannot dodge), so just enough shooters
// stay on a target and the rest switch; targets are ranked by health left divided by that chance.
const pHit = (w, pack, h, u) => (canDodge(w, h, u) ? pack.hitRate ?? 0.3 : 0.9);
// A dodged shot flies on: enemies near its line beyond the target (up to 1.3x range) may still be hit.
function pHitLine(w, pack, h, u) {
	const p = pHit(w, pack, h, u);
	const fd = sk(w, pack.team, 'fireDepth');
	if (!u || !fd) return p;
	const dx = h.x - u.x, dy = h.y - u.y, L = len(dx, dy) || 1, nx = dx / L, ny = dy / L, far = u.range * 1.3;
	let n = 0;
	for (const e of team(w, h.team)) {
		if (e === h) continue;
		const px = e.x - u.x, py = e.y - u.y, a = px * nx + py * ny;
		if (a > L && a < far && Math.abs(px * ny - py * nx) < e.r + 4) n++;
	}
	return p + (1 - p) * Math.min(0.6, n * fd);
}
const fc = (w, u) => { const p = w.packs[u.team]; return p && sk(w, u.team, 'fireControl') && w.o.shots === 'aimed' ? p : null; };
function fireShot(w, u, target, dmg) {
	const d = dmg || u.dmg, speed = (isGame(w) && u.shotSpeed ? u.shotSpeed : w.o.shotSpeed) * (isGame(w) ? u.launch || 1 : 1);
	if (w.o.shots === 'aimed') {
		// Pending damage counts a shot by its chance to hit under fire control or leader fire control.
		const pk = fc(w, u) || (sk(w, u.team, 'leaderFire') && w.packs[u.team]) || null;
		const p = interceptPoint(w, u.x, u.y, target, speed, u.team);
		// Leader bracket: aim this many px to the side of the target's predicted spot (across the line of fire).
		if (u.aimOffset && u.fireOrder === target) { const ex = p.x - u.x, ey = p.y - u.y, l0 = len(ex, ey) || 1; p.x -= ey / l0 * u.aimOffset; p.y += ex / l0 * u.aimOffset; }
		const L = len(p.x - u.x, p.y - u.y) || 1;
		const dodgeable = canDodge(w, target, u), pend = pk ? d * pHit(w, pk, target, u) : d;
		w.shots.push({ x: u.x, y: u.y, dx: (p.x - u.x) / L, dy: (p.y - u.y) / L, left: u.range * 1.3, born: w.t,
			aimed: true, target, src: u, speed, dmg: d, pend, dodgeable });
		addPending(w, u, target, pend);
		return;
	}
	w.shots.push({ x: u.x, y: u.y, target, src: u, speed: ROLE[u.role].shot, dmg: d });
	addPending(w, u, target, d);
}
// Fire control: the path to where the shot is aimed is free of our own units.
function aimClear(w, u, t) {
	if (!fc(w, u)) return laneClear(w, u, t);
	const p = interceptPoint(w, u.x, u.y, t, w.o.shotSpeed, u.team);
	const b = lineBlocker(w, u.x, u.y, { x: p.x, y: p.y, r: t.r }, u);
	return (!b || b.team !== u.team) && laneClear(w, u, t);
}
function fireShell(w, u, h) {
	const lead = ROLE.artillery.flight, [vx, vy] = vel(w, h, u.team);
	fireShellAt(w, u, h.x + vx * lead, h.y + vy * lead);
}
// Unit features the AI reads, each from the unit's own stats (no per-role constants under game rules):
//   minR      a gun's minimum range (game rules: none unless its kind has one; sandbox: the role table's)
//   reachOf   our army's median reach for a role (formation distances), the sandbox role table outside game rules
//   paceOf    our army's median speed (formation pace; the slowest unit's pace cost lives under lobs)
const minR = (u) => (u.minRange !== undefined ? u.minRange : ROLE.artillery.minRange);
function reachOf(w, t, role) {
	if (!isGame(w)) return ROLE[role].range;
	const c = (w._reachC && w._reachC.t === w.t && w._reachC.v === w.unitVer) ? w._reachC : (w._reachC = { t: w.t, v: w.unitVer });
	const key = t + role;
	if (c[key] !== undefined) return c[key];
	const r = team(w, t).filter((u) => u.role === role).map((u) => u.range).sort((a, b) => a - b);
	return (c[key] = r.length ? r[r.length >> 1] : ROLE[role].range);
}
const paceOf = (w, t) => { if (!isGame(w)) return ROLE.artillery.speed; const v = team(w, t).map((u) => u.speed).sort((a, b) => a - b); return v.length ? v[v.length >> 1] : ROLE.artillery.speed; };
// A gun's lob speed (px/s, launch factor included) and blast radius: its own (unit sets) or the game's shaman.
const lobV = (u) => (u.lob || GAME.artillery.lob) * (u.launch || 1);
const blastR = (u) => u.splash || ROLE.artillery.splash;
function fireShellAt(w, u, x, y, pred, atk) {
	const fl = isGame(w) ? len(x - u.x, y - u.y) / lobV(u) : ROLE.artillery.flight;
	w.shells.push({ x, y, t: w.t + fl, born: w.t, src: u, dmg: u.dmg, splash: blastR(u), pred, lob: isGame(w), atk: atk || 'own' });
	const so = ((w.stats.shellOut = w.stats.shellOut || [{}, {}])[u.team]); so.shells = (so.shells || 0) + 1;
}

// ---------------------------------------------------------------- artillery planner (skill artyFire 'plan')
// Every army dodges a shell by the same rule (shellEscape). The planner plays that rule forward for the enemy,
// with every shell already in the air, and so knows where each enemy will be when each planned shell lands.
// It compares attacks on the densest clusters in reach and fires the one with the most expected damage:
//   singles  each gun at its own target (what 'single' does)        focus  every shell on one spot
//   net      centre + ring: every way out runs into another blast   wall   a line across their way to us
//   trap     a ring with one gap (4 directions) + a finisher fired 0.4 or 0.8 s later at where the escapers will be
//   sweep    shells landing 0.3 s apart along a line: they run from the earliest, so the sweep drives them on
// Each attack is also scored against a smart dodger (best spot it can reach); artyRobust blends the two.

// Shared shell dodge rule: the earliest-landing enemy shell (x, y) stands inside and can still step out of
// (need / speed < time left + 0.1); returns the point 40 px straight out of it, or null.
function shellEscape(x, y, r, speed, team, shells, now) {
	let best = null, bt = Infinity, bd = 0;
	for (const s of shells) {
		if (s.src.team === team) continue;
		const d = len(x - s.x, y - s.y), need = s.splash + r + 4 - d, left = s.t - now;
		if (need > 0 && left > 0 && need / speed < left + 0.1 && left < bt) { bt = left; best = s; bd = d; }
	}
	if (!best) return null;
	return bd < 0.5 ? { x: x + 30, y } : { x: x + (x - best.x) / bd * 40, y: y + (y - best.y) / bd * 40 };
}
// Predict planned shells (each { x, y, t: landing time, dmg, splash, src }) against the enemy of side `me`:
// every enemy dodges by the shared rule if its side dodges shells and it is not locked in melee, else keeps its
// smoothed movement; 0.1 s steps until the last landing. Returns damage per planned shell (capped at health)
// and, if snapT is given, every enemy's position at that time.
function predictVolley(w, me, planned, snapT, step) {
	const them = 1 - me, ep = w.packs[them], dodges = ep ? shellDodge(w, ep) : sk(w, them, 'dodgeShells') === true;
	// artyModel 'exact': each enemy by its own dodge rule (smart dodgers, locked melee that still dodge) and its
	// protection; 'simple': every dodger steps straight out, raw damage (the model before 2026-10-03).
	const exact = sk(w, me, 'artyModel') === 'exact';
	const lockedDodge = exact && sk(w, them, 'lockedDodge'), smart = exact && dodges && sk(w, them, 'dodgeShells') === 'smart';
	const es = team(w, them).map((h) => ({ x: h.x, y: h.y, r: h.r, speed: h.speed, vx: h.svx, vy: h.svy, hp: h.hp, worth: threatWorth(h), prot: exact && isGame(w) ? h.prot || 0 : 0,
		lock: !lockedDodge && MELEE[h.role] && h.target && h.target.alive && gap(h, h.target) <= h.range,
		pl: !!h.isPlayer, dashReady: h.dashReady ?? 0, dashUntil: h.dashUntil ?? 0, dashDir: h.dashDir, ep: h.ep }));
	const PD = GAME.player.dash, dashV = PD.dist / PD.time;
	const shells = w.shells.filter((x) => x.src.team !== them && !x.slow && x.t > w.t).concat(planned);
	// A smart dodger (smartEscape) goes to the reachable spot under the fewest blasts, or keeps its course when
	// none is better; planned shells included, decided once (no new shells appear during the prediction).
	if (smart) for (const u of es) {
		const cover = (x, y) => { let k = 0; for (const s of shells) if (len(x - s.x, y - s.y) <= s.splash + u.r + 4) k++; return k; };
		let first = Infinity; for (const s of shells) if (len(u.x - s.x, u.y - s.y) <= s.splash + u.r + 4 && s.t < first) first = s.t;
		if (first === Infinity || u.lock) continue;
		const E = Math.max(8, u.speed * (first - w.t + 0.1));
		let bk = cover(u.x, u.y), bd = 0;
		for (const f of [1, 0.6]) for (let i = 0; i < 16; i++) {
			const a = i * Math.PI / 8, x = u.x + Math.cos(a) * E * f, y = u.y + Math.sin(a) * E * f, k = cover(x, y), d = E * f;
			if (k < bk || (k === bk && u.goal && d < bd)) { bk = k; bd = d; u.goal = { x, y }; }
		}
	}
	// Our own units the blasts catch (a lob hits everyone but its caster): those that cannot step out in time.
	let own = 0;
	const ourDodge = sk(w, me, 'dodgeShells'), ourLocked = sk(w, me, 'lockedDodge');
	if (exact && sk(w, me, 'artyOwn')) for (const p of planned) for (const o of team(w, me)) {
		const d = len(o.x - p.x, o.y - p.y), need = p.splash + o.r + 4 - d;
		if (need <= 0) continue;
		const stuck = !ourDodge || (!ourLocked && MELEE[o.role] && o.target && o.target.alive && gap(o, o.target) <= o.range) || need / o.speed >= p.t - w.t + 0.1;
		if (stuck) own += Math.min(p.dmg, o.hp) * threatWorth(o);
	}
	const order = planned.map((p, i) => i).sort((a, b) => planned[a].t - planned[b].t), per = planned.map(() => 0), val = planned.map(() => 0);
	const end = planned[order[order.length - 1]].t, dt = step || 0.1;
	let k = 0, snap = null;
	for (let t = w.t; k < order.length; ) {
		const nt = Math.min(t + dt, end);
		for (const u of es) {
			if (u.hp <= 0 || u.lock) continue;
			if (u.pl) {
				// The player's dash rule (playerBrain): a shell landing on it within 0.45 s, dash ready -> 112 px in
				// 0.45 s straight away from the last such shell; ready again 0.3 s after the start.
				if (t >= u.dashUntil && t >= u.dashReady && u.ep >= PD.ep) {
					let thr = null;
					for (const s of shells) if (s.t > t && s.t - t < 0.45 && len(u.x - s.x, u.y - s.y) <= s.splash + u.r) thr = s;
					if (thr) { const dx = u.x - thr.x, dy = u.y - thr.y, l = len(dx, dy) || 1; u.dashDir = { x: dx / l, y: dy / l }; u.dashUntil = t + PD.time; u.dashReady = t + PD.cd; u.ep -= PD.ep; }
				}
				if (t < u.dashUntil && u.dashDir) { const st = dashV * Math.min(nt, u.dashUntil) - dashV * t; u.x += u.dashDir.x * st; u.y += u.dashDir.y * st; }
				else { u.x += u.vx * (nt - t); u.y += u.vy * (nt - t); }
				continue;
			}
			if (smart) {
				if (u.goal) { const dx = u.goal.x - u.x, dy = u.goal.y - u.y, d = len(dx, dy), st = Math.min(u.speed * (nt - t), d); if (d > 0) { u.x += dx / d * st; u.y += dy / d * st; } }
				else { u.x += u.vx * (nt - t); u.y += u.vy * (nt - t); }
				continue;
			}
			const v = dodges && shellEscape(u.x, u.y, u.r, u.speed, them, shells, t);
			if (v) { const dx = v.x - u.x, dy = v.y - u.y, d = len(dx, dy), st = Math.min(u.speed * (nt - t), d); if (d > 0) { u.x += dx / d * st; u.y += dy / d * st; } }
			else { u.x += u.vx * (nt - t); u.y += u.vy * (nt - t); }
		}
		t = nt;
		if (snapT !== undefined && !snap && t >= snapT - 1e-9) snap = es.map((u) => ({ x: u.x, y: u.y, hp: u.hp }));
		while (k < order.length && planned[order[k]].t <= t + 1e-9) {
			const i = order[k++], p = planned[i];
			for (const u of es) if (u.hp > 0 && len(u.x - p.x, u.y - p.y) <= p.splash + u.r) {
				const d = Math.min(u.prot ? Math.floor(p.dmg * (1 - u.prot)) : p.dmg, u.hp); per[i] += d; u.hp -= d; val[i] += d * u.worth + (u.hp <= 0 ? KILL_WORTH * u.worth * 100 : 0);
			}
		}
		if (t >= end) break;
	}
	return { per, val, snap, own };
}
// Threat a hit removes: the target's damage per second per point of health (melee, shooters and artillery are
// close: 0.125 / 0.156 / 0.124), so hits on a 90-health shooter are worth more than on a 300-health melee.
// A kill removes the rest of its threat: KILL_WORTH x 100 health points' worth on top.
const KILL_WORTH = 0.3;
const threatWorth = (h) => h.dmg / (h.cdMax || GAME.player.bolt.cast) / h.maxhp;   // its own damage rate per health (the player, cd 0: its bolt cast)
// Smart dodger: hit only if every spot it can reach before a shell lands is covered; takes its best spot's hits.
function smartVolley(w, me, planned) {
	const A = ROLE.artillery, dmg = planned.length ? planned[0].dmg : 0;
	let v = 0;
	for (const h of team(w, 1 - me)) {
		const sp = planned.length ? planned[0].splash : A.splash, r2 = (sp + h.r) ** 2, cover = (x, y) => { let k = 0; for (const p of planned) { const dx = x - p.x, dy = y - p.y; if (dx * dx + dy * dy <= r2) k++; } return k; };
		let least = cover(h.x, h.y);
		if (!least) continue;
		const lock = MELEE[h.role] && h.target && h.target.alive && gap(h, h.target) <= h.range;
		const E = lock ? 0 : h.speed * (Math.min(...planned.map((p) => p.t)) - w.t) * 0.9;
		for (let d = 0; d < 16 && least && E > 0; d++) least = Math.min(least, cover(h.x + Math.cos(d * Math.PI / 8) * E, h.y + Math.sin(d * Math.PI / 8) * E));
		const d = Math.min(h.hp, least * dmg);
		v += d * threatWorth(h) + (d >= h.hp ? KILL_WORTH * threatWorth(h) * 100 : 0);
	}
	return v;
}
// Fire control (game rules, skill holdFire), the same for every unit: asked by gamePrep at the moment a unit could
// start its cast: start now, or hold. A finished cast cannot be held, so the leader times attacks here. It holds
// only when holding pays: wave (artillery vs the player: a bait lob forces the dash, the rest aim at its end) and
// sync (area attacks: one volley that leaves no escape).
function fireGate(w, u) {
	const H = sk(w, u.team, 'holdFire'), t = u.target, pack = w.packs[u.team];
	const others = team(w, u.team).filter((x) => x !== u);
	if (H.wave && t.isPlayer && u.role === 'artillery') {
		// Bait, then the wave: with the player's dash ready, the first gun casting at it is the bait; the other
		// guns start H.wave s after it, so at their release the bait is in the air, the dash it forces is known
		// (predictVolley) and they aim at its end point (the planner's dash net).
		const dashReady = (t.dashReady ?? 0) <= w.t && t.ep >= GAME.player.dash.ep;
		const bait = others.filter((x) => x.role === 'artillery' && x.prep > 0 && x.target === t && x.castT !== undefined);
		if (dashReady && bait.length && w.t < Math.min(...bait.map((x) => x.castT)) + H.wave) return false;
	}
	if (H.sync && u.role === 'artillery' && pack) {
		// Both options scored against the best reachable spot (smartVolley): guns ready now and those ready within
		// H.sync s firing apart, or all of them together after the wait; hold only for a clear gain (20%).
		if (pack._gateT !== w.t) {
			pack._gateT = w.t; pack._gate = null;
			const able = (x) => x.role === 'artillery' && !(x.prep > 0) && x._inReach && x.target && x.target.alive;
			const now = [u, ...others.filter((x) => able(x) && x.cd <= 0)], soon = others.filter((x) => able(x) && x.cd > 0 && x.cd < H.sync);
			if (soon.length) {
				const sp = blastR(u), wait = Math.max(...soon.map((x) => x.cd));
				const land = (dly) => w.t + dly + windUp(w, u) + len(t.x - u.x, t.y - u.y) / lobV(u);
				const net = (k, dly) => Array.from({ length: k }, (_, i) => ({ x: i ? t.x + Math.cos(i * 2 * Math.PI / (k - 1)) * sp * 1.5 : t.x, y: i ? t.y + Math.sin(i * 2 * Math.PI / (k - 1)) * sp * 1.5 : t.y,
					t: land(dly), dmg: u.dmg, splash: sp, src: { team: u.team } }));
				const apart = smartVolley(w, u.team, net(now.length, 0)) + smartVolley(w, u.team, net(soon.length, wait));
				if (smartVolley(w, u.team, net(now.length + soon.length, wait)) > apart * 1.2 + 1e-9) pack._gate = { until: w.t + wait };
			}
		}
		if (pack._gate && w.t < pack._gate.until) return false;
	}
	return true;
}
function artilleryVolley(w, pack) {
	if (sk(w, pack.team, 'artyFire') !== 'plan') return;
	const A = ROLE.artillery, me = pack.team, es = team(w, 1 - me), G = isGame(w);
	// Delayed shots of an attack already chosen (finishers, sweep shells). Under game rules a gun cannot hold a
	// finished cast, so a delayed shot is a gun already mid-cast, fired at the planned point at its own release.
	if (pack.artyQueue && pack.artyQueue.length) {
		if (G) {
			for (const q of pack.artyQueue) if (q.u.alive && prepared(w, q.u)) { q.u.reservedUntil = 0; q.done = true; released(w, q.u); if (inReachOf(q.u, q)) fireShellAt(w, q.u, q.x, q.y, q.pred, q.atk); }
			pack.artyQueue = pack.artyQueue.filter((q) => !q.done && q.u.alive && w.t < q.at + 0.3);
		} else {
			for (const q of pack.artyQueue) if (q.at <= w.t + 1e-9 && q.u.alive) { q.u.reservedUntil = 0; if (!busy(w, q.u) && prepared(w, q.u)) { released(w, q.u); fireShellAt(w, q.u, q.x, q.y, q.pred, q.atk); } }
			pack.artyQueue = pack.artyQueue.filter((q) => q.at > w.t + 1e-9 && q.u.alive);
		}
	}
	// Enemies the last attack cut off (pack.cutOff, marked for 2 s): our shooters rank them (shooterTarget), our free
	// melee near them go for them (decide).
	if (pack.cutOff && pack.cutOff.until <= w.t) pack.cutOff = null;
	const ready = team(w, me).filter((u) => u.role === 'artillery' && prepared(w, u) && !busy(w, u) && !(u.reservedUntil > w.t));
	if (!ready.length || !es.length) return;
	const inRange = inReachOf;
	// Game rules: guns mid-cast and when each releases (its wind-up left, on its own clock).
	const coming = G ? team(w, me).filter((u) => u.role === 'artillery' && u.prep > 0 && !prepared(w, u) && !(u.reservedUntil > w.t))
		.map((u) => ({ u, rt: w.t + (windUp(w, u) - u.prep) / (u.tr || 1) })) : null;
	const FL = G ? ready.reduce((a, u) => a + 0.8 * u.range / lobV(u), 0) / ready.length : A.flight;
	const leadOf = (h) => { const [vx, vy] = vel(w, h, me); return { x: h.x + vx * FL, y: h.y + vy * FL }; };
	// Singles: each gun at its own target; under game rules exactly what a gun does alone (its target's position now).
	const singles = () => ready.map((u) => {
		if (G) { const t = u.target; return t && t.alive && inRange(u, t) ? { u, at: w.t, x: t.x, y: t.y } : null; }
		const h = artilleryTarget(w, u, es, pack.f); return h ? Object.assign({ u, at: w.t }, leadOf(h)) : null; }).filter(Boolean);
	// Copies of the battle used by the look-ahead fire singles: cheap, and the real planner decides for real.
	// Copies of the battle used by the look-ahead plan light: the densest cluster, singles / focus / net only.
	const light = !!w.forked && !(w.thinkTeams && w.thinkTeams.includes(pack.team));
	// Decide when another gun is ready, or every artyEvery s while guns stay ready.
	if (!G && ready.length <= (pack.artyReady || 0) && w.t < (pack.artyNext || 0)) { pack.artyReady = ready.length; return; }
	pack.artyNext = w.t + sk(w, me, 'artyEvery');
	const n = ready.length + coming.length, sp = G ? ready.reduce((a, u) => a + blastR(u), 0) / ready.length : A.splash, rho = sk(w, me, 'artyRobust');
	const toUs = (c) => { const x = pack.anchor.x - c.x, y = pack.anchor.y - c.y, l = len(x, y) || 1; return { x: x / l, y: y / l }; };
	// Clusters: led enemy positions by enemies within escape reach x guns that reach them.
	// Cluster radius for choosing where to aim: twice the blast under game rules (scales with any gun; today's 80 px
	// matches the 78 px the old 76 px/s x flight + blast gave); the sandbox keeps its escape-reach form.
	const reach = G ? 2 * sp : 76 * FL + sp, cand = [];
	for (const h of es) {
		const c = leadOf(h), g = ready.filter((u) => inRange(u, c)).length;
		if (!g) continue;
		let k = 0; for (const o of es) if (dist(o, c) < reach) k++;
		cand.push([k * g, c]);
	}
	cand.sort((a, b) => b[0] - a[0]);
	const attacks = [['singles', singles()]];
	const ring = (c, m, from, span, r) => Array.from({ length: m }, (_, i) => ({ x: c.x + Math.cos(from + span * (i + 0.5) / m) * r, y: c.y + Math.sin(from + span * (i + 0.5) / m) * r }));
	const pl = es.find((h) => h.isPlayer);
	if (pl && !light) {
		// The player: where the dash rule puts it when our shells land (shells already in the air included: a bait
		// lob makes it dash, so its end point is known). Dash net: a shell there and a ring at dash length around
		// it, so a second dash also ends in a blast.
		const i = es.indexOf(pl), snap = predictVolley(w, me, [{ x: -1e6, y: -1e6, t: w.t + FL, dmg: 0, splash: 0, src: { team: me } }], w.t + FL).snap;
		const E = snap ? { x: snap[i].x, y: snap[i].y } : leadOf(pl);
		cand.unshift([1e9, E]);
		if (n >= 2) attacks.push(['dashnet', [{ at: w.t, x: E.x, y: E.y }, ...ring(E, n - 1, 0, 2 * Math.PI, GAME.player.dash.dist).map((p) => Object.assign({ at: w.t }, p))]]);
	}
	for (const [, c] of cand.slice(0, light ? 1 : 3)) {
		const u = toUs(c), ua = Math.atan2(u.y, u.x), at = (p) => Object.assign({ at: w.t }, p);
		attacks.push(['focus', Array.from({ length: n }, (_, i) => at({ x: c.x + Math.cos(i * 2.4) * sp * 0.3, y: c.y + Math.sin(i * 2.4) * sp * 0.3 }))]);
		if (n >= 3) attacks.push(['net', [at(c), ...ring(c, n - 1, ua, 2 * Math.PI, sp * 1.5).map(at)]]);
		if (light) continue;
		if (n >= 3) attacks.push(['wall', Array.from({ length: n }, (_, i) => at({ x: c.x + u.x * sp * 0.8 - u.y * (i - (n - 1) / 2) * sp * 1.4, y: c.y + u.y * sp * 0.8 + u.x * (i - (n - 1) / 2) * sp * 1.4 }))]);
		if (n >= 3) {
			// Herd: a line on their far side, so they step toward us. Split: a line through them toward us, so
			// they step apart to both sides.
			const line = (o, d) => Array.from({ length: n }, (_, i) => at({ x: o.x + d.x * (i - (n - 1) / 2) * sp * 1.4, y: o.y + d.y * (i - (n - 1) / 2) * sp * 1.4 }));
			attacks.push(['herd', line({ x: c.x - u.x * sp * 1.2, y: c.y - u.y * sp * 1.2 }, { x: -u.y, y: u.x })]);
			attacks.push(['split', line(c, u)]);
		}
		if (n >= 4) for (const g of [0, Math.PI / 2, Math.PI, -Math.PI / 2]) for (const d of [0.4, 0.8]) for (const gw of [1.22, 0.7]) {
			// The ring leaves a gap (70 or 40 degrees) toward bearing ua + g; the finisher waits d s, then fires at
			// the predicted centre of the escapers when it lands (or at the gap's mouth if nobody is predicted out).
			const gapA = ua + g, rp = ring(c, n - 1, gapA + gw / 2, 2 * Math.PI - gw, sp * 1.5).map(at);
			const fin = { x: c.x + Math.cos(gapA) * sp * 2.6, y: c.y + Math.sin(gapA) * sp * 2.6, at: w.t + d, fin: true };
			const pr = predictVolley(w, me, rp.map((p) => shellOf(w, pack, p, FL)), w.t + d + FL);
			if (pr.snap) {
				let x = 0, y = 0, k = 0;
				pr.snap.forEach((q, i) => { const h = es[i]; if (q.hp > 0 && dist(h, c) < reach && dist(q, c) > sp * 1.2 && Math.cos(Math.atan2(q.y - c.y, q.x - c.x) - gapA) > 0.5) { x += q.x; y += q.y; k++; } });
				if (k) { fin.x = x / k; fin.y = y / k; }
			}
			attacks.push([`trap ${Math.round(g * 180 / Math.PI)} ${d} ${Math.round(gw * 180 / Math.PI)}`, [...rp, fin]]);
		}
		if (n >= 3) for (const dir of [u, { x: -u.y, y: u.x }]) {
			// Sweep: from the far side toward us (or across), each shell 0.3 s after the one before.
			attacks.push(['sweep', Array.from({ length: n }, (_, i) => ({ x: c.x + dir.x * (i - (n - 1) / 2) * sp * 1.2, y: c.y + dir.y * (i - (n - 1) / 2) * sp * 1.2, at: w.t + i * 0.3 }))]);
		}
	}
	// Counter-battery (skill artyBattery): every shell on one of their guns, the two nearest our guns reach.
	if (!light && sk(w, me, 'artyBattery')) {
		const theirs = es.filter((h) => h.role === 'artillery' && ready.some((u) => inRange(u, h))).sort((a, b) => dist(a, pack.anchor) - dist(b, pack.anchor));
		for (const h of theirs.slice(0, 2)) { const c = leadOf(h); attacks.push(['battery', Array.from({ length: n }, (_, i) => ({ at: w.t, x: c.x + Math.cos(i * 2.4) * sp * 0.4, y: c.y + Math.sin(i * 2.4) * sp * 0.4 }))]); }
	}
	// Score: guns assigned to points, then greedy-rule prediction blended with the smart dodger, plus (artyHerd)
	// where the survivors end up: inside the reach of our fighters is worth more.
	const herd = light ? 0 : sk(w, me, 'artyHerd'), fighters = herd ? team(w, me).filter((x) => x.role !== 'artillery') : [];
	const zone = (q) => { let k = 0; for (const f of fighters) if (len(f.x - q.x, f.y - q.y) <= f.range + (MELEE[f.role] ? 40 : 0)) k++; return k; };
	let best = null, bv = -1;
	const RO = !light && sk(w, me, 'artyRollout'), scored = [];
	for (const [name, pts] of attacks) {
		const shots = name === 'singles' ? pts : assignGuns(ready, pts, inRange, coming, w.t);
		if (!shots.length) continue;
		const planned = shots.map((q) => shellOf(w, pack, q, FL));
		const endT = herd ? Math.max(...planned.map((p) => p.t)) : undefined;
		const pr = predictVolley(w, me, planned, endT, light ? 0.25 : 0.1), greedy = pr.val.reduce((a, b) => a + b, 0) - pr.own;
		let v = light ? greedy : (1 - rho) * greedy + rho * smartVolley(w, me, planned);
		// Isolation: our fighters reaching its spot minus its own friends within 80 px of it then.
		if (herd && pr.snap) pr.snap.forEach((q, i) => { if (q.hp <= 0) return; let f = 0; for (const o of pr.snap) if (o !== q && o.hp > 0 && len(o.x - q.x, o.y - q.y) < 80) f++; v += herd * threatWorth(es[i]) * (zone(q) - f); });
		if (v > bv) { bv = v; best = { name, shots, per: pr.per }; }
		if (RO && n >= 2) scored.push({ v, name, shots, per: pr.per });
	}
	if (!best) return;
	// Budget: at most one outcome check every RO.every s; a gun firing in between takes the shortlist's best.
	if (RO && scored.length > 1 && w.t >= (pack.roNext ?? -1)) {
		pack.roNext = w.t + (RO.every || 0);
		// Judge by outcome: play the best few forward on copies of the battle; the shells' own damage is only the
		// shortlist. An attack that cuts them apart or holds them off our shooters wins here.
		scored.sort((a, b) => b.v - a.v);
		// Shaping attacks (split them, cut their rear off, wall their way to us) deal little shell damage, so the
		// best of each always goes forward too: only the outcome shows what moving them is worth.
		const list = scored.slice(0, RO.top);
		for (const fam of RO.shape || []) { const c = scored.find((x) => x.name.split(' ')[0] === fam); if (c && !list.includes(c)) list.push(c); }
		let bo = -Infinity;
		for (const cand of list) {
			const o = artyOutcome(w, pack, cand, RO.horizon);
			if (o > bo) { bo = o; best = cand; }
		}
	}
	launch(w, pack, best.shots, best.per, best.name);
	if (!light && sk(w, me, 'artyFollow')) {
		const planned = best.shots.map((q) => shellOf(w, pack, q, FL)), endT = Math.max(...planned.map((p) => p.t));
		const snap = predictVolley(w, me, planned, endT).snap, set = new Set();
		if (snap) snap.forEach((q, i) => { if (q.hp <= 0) return; let f = 0; for (const o of snap) if (o !== q && o.hp > 0 && len(o.x - q.x, o.y - q.y) < 80) f++; if (f <= 1) set.add(es[i]); });
		pack.cutOff = set.size ? { set, until: endT + 2 } : null;
	}
	// Guns the attack did not use fire at their own targets.
	const used = new Set(best.shots.map((q) => q.u));
	launch(w, pack, singles().filter((q) => !used.has(q.u)), null, 'left');
	pack.artyReady = team(w, me).filter((u) => u.role === 'artillery' && prepared(w, u) && !busy(w, u) && !(u.reservedUntil > w.t)).length;
}
const inReachOf = (u, p) => { const d = dist(u, p); return d <= u.range && d >= minR(u); };
// One attack played forward horizon s on a copy of the battle: their health lost (a kill counts 100 more) and
// shells still in the air at their predicted damage, minus the same for us.
function artyOutcome(w, pack, cand, horizon) {
	const RO = sk(w, pack.team, 'artyRollout'), me = pack.team, c = fork(w, Object.assign({ duration: w.t + horizon }, RO.dt ? { dt: RO.dt } : {}));
	c.forked = true;
	const byId = new Map(c.units.map((u) => [u.id, u]));
	launch(c, c.packs[me], cand.shots.map((q) => Object.assign({}, q, { u: byId.get(q.u.id) })), cand.per, cand.name);
	if (sk(w, me, 'artyRollout').score === 'ltd2') {
		// LTD2 (Kovarsky & Buro): sum of sqrt(health) x damage rate per side, so a finished kill outscores the same
		// damage spread; shells still in the air hit whoever stands in them at the end.
		const ltd = (t, end) => team(c, t).reduce((a, u) => {
			let h = u.hp;
			if (end) for (const s of c.shells) if (!s.slow && s.src !== u && (s.lob || s.src.team !== t) && len(u.x - s.x, u.y - s.y) <= s.splash + u.r) h -= s.dmg;
			return a + Math.sqrt(Math.max(0, h)) * u.dmg / (u.cdMax || GAME.player.bolt.cast);
		}, 0);
		const our0 = ltd(me), their0 = ltd(1 - me);
		while (!done(c)) step(c);
		return (their0 - ltd(1 - me, true)) - (our0 - ltd(me, true));
	}
	const hp = (t) => team(c, t).reduce((a, u) => a + Math.max(0, u.hp), 0) + 100 * team(c, t).length;
	const our0 = hp(me), their0 = hp(1 - me);
	while (!done(c)) step(c);
	let fly = 0; for (const s of c.shells) if (!s.slow) fly += (s.src.team === me ? 1 : -1) * (s.pred ?? s.dmg * 0.76);
	return (their0 - hp(1 - me)) - (our0 - hp(me)) + fly;
}
// A planned shot as the shell it will become (landing time = fire time + flight; under game rules the flight is
// the gun's distance over its lob speed, fl when the gun is not chosen yet).
const shellOf = (w, pack, q, fl) => {
	const f = !isGame(w) ? ROLE.artillery.flight : q.u ? len(q.x - q.u.x, q.y - q.u.y) / lobV(q.u) : fl;
	return { x: q.x, y: q.y, t: q.at + f, dmg: q.u ? q.u.dmg : ROLE.artillery.dmg, splash: q.u && isGame(w) ? blastR(q.u) : ROLE.artillery.splash, src: { team: pack.team } };
};
// Each point to the nearest free gun that reaches it. A delayed point under game rules goes to the gun mid-cast
// whose release is nearest its time (within 0.35 s), and takes that release time; with none it is dropped (a
// ready gun cannot hold its release). coming is null outside game rules.
function assignGuns(ready, pts, inRange, coming, now) {
	const free = ready.slice(), soon = coming ? coming.slice() : [], out = [];
	for (const p of pts) {
		let g = null, gd = Infinity;
		if (p.at > now + 1e-9 && coming) {   // a delayed point (game rules): only a gun already mid-cast
			for (const c of soon) { const e = Math.abs(c.rt - p.at); if (e < 0.35 && inRange(c.u, p) && e < gd) { gd = e; g = c; } }
			if (g) { soon.splice(soon.indexOf(g), 1); out.push(Object.assign({}, p, { u: g.u, at: g.rt })); }
			continue;
		}
		for (const u of free) if (inRange(u, p) && dist(u, p) < gd) { gd = dist(u, p); g = u; }
		if (g) { free.splice(free.indexOf(g), 1); out.push(Object.assign({ u: g }, p)); }
	}
	return out;
}
// Fire now what is due now; the rest waits in the pack's queue with its gun reserved.
function launch(w, pack, shots, per, name) {
	const base = name.split(' ')[0];
	shots.forEach((q, i) => {
		const pred = per ? per[i] : undefined, atk = q.fin ? base + '-finisher' : base;
		if (q.at <= w.t + 1e-9) { released(w, q.u); fireShellAt(w, q.u, q.x, q.y, pred, atk); }
		else { q.u.reservedUntil = q.at + 0.3; (pack.artyQueue = pack.artyQueue || []).push({ u: q.u, x: q.x, y: q.y, at: q.at, pred, atk }); }
	});
	if (w.rec && shots.length && name !== 'left') w.rec.arty.push({ t: w.t, team: pack.team, name, shots: shots.map((q) => ({ x: Math.round(q.x), y: Math.round(q.y), at: q.at, gun: q.u.id })) });
	if (shots.length) { const A = ((w.stats.atk = w.stats.atk || [{}, {}])[pack.team][base] = w.stats.atk[pack.team][base] || { used: 0, shells: 0, dmg: 0, kills: 0 }); A.used++; }
	if (name !== 'left' && name !== pack.artyLast) { pack.artyLast = name; note(w, `artillery: ${name}`, pack.team); }
}

// Shot dodge: an enemy aimed shot, seen for at least shotReact s, whose straight path passes through this unit
// within the next 0.4 s. Returns the sidestep point, or null.
function shotDodgeVector(w, u) {
	let best = null, bt = Infinity;
	for (const s of w.shots) {
		if (!s.aimed || s.src.team === u.team || w.t - s.born < sk(w, u.team, 'shotReact')) continue;
		const px = u.x - s.x, py = u.y - s.y, along = px * s.dx + py * s.dy;
		if (along <= 0 || along > Math.min(s.left, s.speed * 0.4)) continue;
		const side = px * s.dy - py * s.dx;
		if (Math.abs(side) <= u.r + 3 && along < bt) { bt = along; best = { s, side }; }
	}
	if (!best) return null;
	const k = best.side >= 0 ? 1 : -1;
	return { x: u.x + best.s.dy * 30 * k, y: u.y - best.s.dx * 30 * k };
}

// ---------------------------------------------------------------- shared individual skills
function meleeAnswer(w, u) {
	const a = u.meleeAttacker;
	return a && a.alive && w.t - u.meleeAt < 1.0 && gap(a, u) < 24 ? a : null;
}

// ---------------------------------------------------------------- the unit layer: decide, then act
// A unit's tick has two halves. decide() chooses what the unit wants and is the only code that writes u.target,
// u.state and u.dec: its one movement goal and how it may release a cast. act() carries that out (walk, then release
// or strike). The pack's code (formationPlan) only proposes: slots, goals, u.assigned. The rules (cast starts, hits)
// never choose.
//   dec.move  { x, y, stop, mul }  where the unit walks this tick (mul scales its step)
//   dec.keep  true: a later choice of the tick may not replace the goal (backing off a melee threat)
//   dec.rel   what act may release: null | 'melee' | 'direct' | 'art' | 'dodgeFire' | 'player'
//   dec.post  true: the reach check comes after the walk (shooters, a gun walking to its slot, a melee already on
//             its way to a goal); false: before it (a melee swings on where it stood, a free gun on where it was)
const goTo = (D, x, y, stop, mul) => { if (!D.keep) D.move = { x, y, stop: stop || 0, mul: mul === undefined ? 1 : mul }; };

function decMelee(w, u, t, D) {
	// Engage goal (a commander's order, pack.cmd): the nearest enemy of the engaged set.
	const pk = w.packs[u.team], eng = pk && cmdOf(w, pk, 'engage');
	if (eng && !(u.prep > 0) && !(t && eng.has(t.id) && t.alive)) {
		let e = null, ed = Infinity;
		for (const h of foes(w, u.team)) if (eng.has(h.id)) { const g = gap(u, h); if (g < ed) { ed = g; e = h; } }
		if (e) t = e;
	}
	// Weapons free (skill weaponsFree, game rules): with its own target out of reach and another enemy within reach,
	// a melee unit fights that one (a swing re-checks its target at release, COMBAT_DESIGN.md:78-80) instead of
	// standing next to an enemy while it walks to its assigned one.
	if (t && isGame(w) && sk(w, u.team, 'weaponsFree') && gap(u, t) > u.range) {
		let e = null, ed = u.range;
		for (const h of foes(w, u.team)) { const g = gap(u, h); if (g <= ed) { ed = g; e = h; } }
		if (e) t = e;
	}
	// Melee focus (skill meleeFocus, game rules): among the enemies within reach, swing at the one with the least
	// health left after the swings of ours already winding up at it (kills sooner, no overkill); nearby melee so
	// gang up on the weakest. A swing already winding up keeps its target.
	if (isGame(w) && sk(w, u.team, 'meleeFocus') && !(u.prep > 0)) {
		let e = null, el = Infinity;
		for (const h of foes(w, u.team)) {
			if (gap(u, h) > u.range) continue;
			let left = h.hp;
			for (const m of team(w, u.team)) if (m !== u && m.prep > 0 && m.target === h && MELEE[m.role]) left -= m.dmg * (1 - (h.prot || 0));
			const k = left > 0 ? left : 1e6 + h.hp;   // already dead to the swings in flight: last choice
			if (k < el) { el = k; e = h; }
		}
		if (e) t = e;
	}
	u.target = t;
	if (!t) return;
	D.rel = 'melee';
	const d = gap(u, t);
	u._inReach = d <= u.range;
	if (isGame(w)) {
		// Approach a point on a ring around the target, phased by identity, so attackers spread around it.
		if (d > u.range) {
			const rr = Math.max(2 * u.r, GAME.ringReach * (u.range + u.r + GAME.typicalR)), a = u.id * 2.399963;   // its own reach
			goTo(D, t.x + Math.cos(a) * rr, t.y + Math.sin(a) * rr);
		}
	} else if (d > u.range * 0.9) {
		if (sk(w, u.team, 'pursuit') === 'cut' && d > 30) { const p = interceptPoint(w, u.x, u.y, t, u.speed, u.team); goTo(D, p.x, p.y, u.range * 0.8 + t.r + u.r); }
		else goTo(D, t.x, t.y, u.range * 0.8 + t.r + u.r);
	}
}

function decDirect(w, u, t, D, gx, gy, leash, enemies) {
	u.target = t;
	D.rel = 'direct'; D.post = true;
	const free = leash === Infinity;
	let mx = gx, my = gy, stop = 0;
	u.state = free ? 'chase' : 'slot';
	const threat = nearest(u, isGame(w) && w.o.perception === true ? enemies.filter((e) => MELEE[e.role]) : teamMelee(w, 1 - u.team));   // perceived melee only
	if (threat && dist(threat, u) < sk(w, u.team, 'kite')) {
		const d = dist(threat, u) || 1;
		mx = u.x + (u.x - threat.x) / d * 40; my = u.y + (u.y - threat.y) / d * 40; u.state = 'kite';
	} else if (t && free && gap(u, t) > u.range) {
		mx = t.x; my = t.y; stop = u.range * 0.85 + t.r + u.r;
	} else if (t && gap(u, t) <= u.range && !laneClear(w, u, t)) {
		const dx = t.x - u.x, dy = t.y - u.y, d = len(dx, dy) || 1;
		mx = u.x - dy / d * 20 * u.strafe; my = u.y + dx / d * 20 * u.strafe; u.state = 'strafe';
		if (!free && len(mx - gx, my - gy) > leash) u.strafe = -u.strafe;
	} else if (free) { mx = u.x; my = u.y; }
	// Jink: while enemy shooters can reach us, step side to side across their line of fire, switching at
	// irregular moments, so shots aimed where we were heading miss.
	const pk = w.packs[u.team];
	const jk = pk ? sk(w, u.team, 'jink') : 0;
	if (jk && u.state === 'slot' && t) {
		if (!(u.jinkUntil > w.t)) { u.jinkUntil = w.t + 0.3 + ((u.id * 7919 + Math.round(w.t * 10) * 104729) % 1000) / 2500; u.jinkSide = -(u.jinkSide || 1); }
		const dx = t.x - u.x, dy = t.y - u.y, d = len(dx, dy) || 1;
		mx = gx - dy / d * jk * u.jinkSide; my = gy + dx / d * jk * u.jinkSide; u.state = 'jink';
	}
	if (!free && len(mx - gx, my - gy) > leash) {
		const d = len(mx - gx, my - gy); mx = gx + (mx - gx) / d * leash; my = gy + (my - gy) / d * leash;
	}
	goTo(D, mx, my, stop);
	u._inReach = !!t && gap(u, t) <= u.range;
}

function decArtillery(w, u, t, D, gx, gy, bound) {
	u.target = t;
	u.state = bound ? 'slot' : 'chase';
	D.rel = 'art'; D.bound = bound; D.post = bound;
	if (bound) goTo(D, gx, gy);
	if (!t) return;
	const d = dist(u, t);
	if (!bound) {
		if (d > u.range) goTo(D, t.x, t.y, u.range * 0.9);
		else if (d < minR(u) + 20) { goTo(D, 2 * u.x - t.x, 2 * u.y - t.y); u.state = 'kite'; }
	}
	u._inReach = d <= u.range && d >= minR(u);
}

// The player bot (Skirmish 60). The game cannot define a human, so this behaviour is the sandbox's design; every
// number it uses is the player's real kit (GAME.player). Four auto limbs fire at the nearest monster in reach;
// manual casts: cinder_pulse when 3+ monsters are inside its circle, ember_bolt at a target with 100+ health;
// it keeps 100 energy for dashes; dashes away from a swing about to land (0.25 s left), a lob about to land on it
// or a shot about to hit it; kites away from melee inside 160 px and steers off the walls.
function playerShot(w, u, t, spec, manual) {
	const ex = t.x - u.x, ey = t.y - u.y, L = len(ex, ey) || 1;
	w.shots.push({ x: u.x, y: u.y, dx: ex / L, dy: ey / L, left: spec.range, born: w.t, aimed: true, target: t, src: u,
		speed: spec.speed, dmg: spec.dmg, pend: spec.dmg, dodgeable: true, manual: !!manual, pierce: spec.pierce || 0 });
}
function playerBrain(w, u, dt) {
	const P = GAME.player, es = team(w, 1 - u.team);
	if (!es.length) return;
	if (u.dashUntil > w.t) { moveToward(Object.assign(u, { speed: P.dash.dist / P.dash.time }), u.x + u.dashDir.x * 50, u.y + u.dashDir.y * 50, dt); u.speed = P.speed; return; }
	const SR = P.surround, mob = Math.min(1, es.filter((e) => dist(e, u) <= SR.radius).length / SR.max);
	u.speed = P.speed * (1 - (1 - SR.floor) * mob);
	if (mob >= SR.interrupt && u.manual) { u.manual = null; w.stats.playerInterrupts = (w.stats.playerInterrupts || 0) + 1; }
	// Threats: a melee swing on us with 0.25 s or less left, a lob landing on us within 0.45 s, a shot hitting us within 0.3 s.
	let threat = null;
	for (const e of es) if (MELEE[e.role] && e.prep > 0 && e.target === u && e.windup - e.prep <= 0.25 && gap(e, u) <= e.range + 12) threat = { x: u.x - e.x, y: u.y - e.y };
	for (const sh of w.shells) if (sh.src.team !== u.team && sh.t - w.t < 0.45 && len(u.x - sh.x, u.y - sh.y) <= sh.splash + u.r) threat = { x: u.x - sh.x, y: u.y - sh.y };
	for (const sh of w.shots) if (sh.src.team !== u.team) {
		const px = u.x - sh.x, py = u.y - sh.y, along = px * sh.dx + py * sh.dy;
		if (along > 0 && along < sh.speed * 0.3 && Math.abs(px * sh.dy - py * sh.dx) <= u.r + 2) threat = { x: sh.dy * (px * sh.dy - py * sh.dx >= 0 ? 1 : -1), y: -sh.dx * (px * sh.dy - py * sh.dx >= 0 ? 1 : -1) };
	}
	if (threat && w.t >= u.dashReady && u.ep >= P.dash.ep) {
		const l = len(threat.x, threat.y) || 1;
		u.dashDir = { x: threat.x / l, y: threat.y / l }; u.ep -= P.dash.ep; u.dashReady = w.t + P.dash.cd; u.dashUntil = w.t + P.dash.time;
		u.state = 'dash'; w.stats.playerDashes = (w.stats.playerDashes || 0) + 1;
		return;
	}
	// Kite away from melee within 160 px, steer off the walls; otherwise close in to 450 px.
	let mx = 0, my = 0;
	for (const e of es) { const d = dist(e, u); if (MELEE[e.role] && d < 160) { mx += (u.x - e.x) / (d || 1) * (160 - d); my += (u.y - e.y) / (d || 1) * (160 - d); } }
	const m = 120;
	if (u.x < m) mx += (m - u.x) * 2; if (u.x > w.o.width - m) mx -= (u.x - w.o.width + m) * 2;
	if (u.y < m) my += (m - u.y) * 2; if (u.y > w.o.height - m) my -= (u.y - w.o.height + m) * 2;
	const near = nearest(u, es), style = w.o.playerStyle || 'kite';
	// Held-out styles (never used for tuning): 'orbit' keeps circling the pack at about 400 px; 'press' pushes in
	// to about 250 px. 'kite' (default) holds still unless melee come within 160 px, closing in beyond 450 px.
	if (style === 'orbit' && near) {
		const d = dist(near, u), tx = -(near.y - u.y) / (d || 1), ty = (near.x - u.x) / (d || 1);
		mx += tx * 60 + (near.x - u.x) / (d || 1) * (d - 400) * 0.5; my += ty * 60 + (near.y - u.y) / (d || 1) * (d - 400) * 0.5;
	} else if (style === 'press' && near && dist(near, u) > 250 && !mx && !my) { mx = near.x - u.x; my = near.y - u.y; }
	else if (!mx && !my && near && dist(near, u) > 450) { mx = near.x - u.x; my = near.y - u.y; }
	if (mx || my) { const l = len(mx, my); moveToward(u, u.x + mx / l * 40, u.y + my / l * 40, dt); u.state = 'kite'; }
	// Auto limbs: fire_bolt -> fire_lance; each commits on the nearest monster in reach above the 10% reserve.
	for (const L of u.limbs) {
		const spec = L.seq === 0 ? P.bolt : P.lance, cost = spec.ep * L.mult;
		if (L.prep > 0) {
			L.prep += dt;
			if (L.prep >= spec.cast) {
				const t = L.target && L.target.alive && dist(L.target, u) <= spec.range ? L.target : nearest(u, es, (e) => dist(e, u) <= spec.range);
				if (t) playerShot(w, u, t, spec, false);
				L.prep = 0; L.seq = 1 - L.seq;
			}
			continue;
		}
		const t = nearest(u, es, (e) => dist(e, u) <= spec.range);
		if (t && u.ep - cost >= P.reserve * u.epMax) { u.ep -= cost; L.prep = dt; L.target = t; }
	}
	// Manual (body source): cinder_pulse or ember_bolt, keeping 100 energy for dashes.
	if (u.manual) {
		u.manual.prep += dt;
		const M = u.manual, spec = P[M.kind];
		if (M.prep >= spec.cast) {
			if (M.kind === 'pulse') { for (const e of es.slice()) if (len(e.x - u.x, e.y - u.y) <= spec.radius + e.r) damage(w, u, e, spec.dmg); }
			else { const t = M.target && M.target.alive && dist(M.target, u) <= spec.range ? M.target : nearest(u, es, (e) => dist(e, u) <= spec.range); if (t) playerShot(w, u, t, spec, true); }
			u.manual = null;
		}
	} else {
		const inPulse = es.filter((e) => len(e.x - u.x, e.y - u.y) <= P.pulse.radius + e.r).length;
		const big = es.filter((e) => e.hp >= 100 && dist(e, u) <= P.ember.range).sort((a, b) => dist(a, u) - dist(b, u))[0];
		if (inPulse >= 3 && u.ep - P.pulse.ep >= 100) { u.ep -= P.pulse.ep; u.manual = { kind: 'pulse', prep: dt }; }
		else if (big && u.ep - P.ember.ep >= 100) { u.ep -= P.ember.ep; u.manual = { kind: 'ember', prep: dt, target: big }; }
	}
}
// A unit with no pack: every unit for itself (brain 'alone', the player bot).
function decideAlone(w, u, D) {
	if (u.role === 'player') { D.rel = 'player'; return; }   // an outside agent (the sandbox's player bot): it acts on its own rules
	const es = foes(w, u.team);
	kiterRetreat(w, u, es, D);
	if ((sk(w, u.team, 'dodgeShells') === true || sk(w, u.team, 'dodgeShells') === 'smart') && !(MELEE[u.role] && u.target && u.target.alive && gap(u, u.target) <= u.range)) {
		const v = dodgeVector(w, u);
		if (v) { goTo(D, v.x, v.y); u.state = 'dodge'; return; }
	}
	if (u.role === 'artillery') return decArtillery(w, u, artilleryTarget(w, u, es, null), D, 0, 0, false);
	if (MELEE[u.role]) {
		let t = meleeAnswer(w, u);
		if (!t && u.role === 'hunter') {
			const near = nearest(u, es), soft = nearest(u, es, (m) => !MELEE[m.role]);
			t = near;
			if (soft && near && dist(soft, u) < dist(near, u) + 60) t = soft;
			const block = nearest(u, es, (m) => MELEE[m.role] && gap(m, u) < 6);
			if (block) t = block;
		}
		u.state = 'chase';
		return decMelee(w, u, t || nearest(u, es), D);
	}
	decDirect(w, u, nearest(u, es), D, u.x, u.y, Infinity, es);
}

// ---------------------------------------------------------------- the reactive commander
const pinned = (h) => h.target && h.target.alive && h.target.role === 'melee' && gap(h, h.target) < 24;

// Threats, from the pack's own point of view: raiders on our back line, shooters closing faster than
// we can give ground, and whether we are being hit without being able to hit back.
function threatRead(w, pack, ours, es, em, A) {
	const soft = ours.filter((m) => !MELEE[m.role]);
	const raiders = em.filter((h) => soft.some((m) => dist(h, m) < 260 &&
		((h.vx * (m.x - h.x) + h.vy * (m.y - h.y)) / (dist(h, m) || 1) > 25 || dist(h, m) < 120)) &&
		!ours.some((m) => m.role === 'melee' && gap(m, h) < 24)).length;
	const eshoot = es.filter((h) => h.role === 'ranged' || h.role === 'archer');
	let shootSpeed = 0, nClose = 0;
	for (const h of eshoot) if (dist(h, A) < 420) { shootSpeed += (h.vx * (A.x - h.x) + h.vy * (A.y - h.y)) / (dist(h, A) || 1); nClose++; }
	shootSpeed = nClose ? shootSpeed / nClose : 0;
	// Shooters that move faster than our pack can give ground: siege cannot keep them out.
	// Closing speed toward us, not sidesteps: a fixed formation advances at 43 px/s, a released skirmisher at 62.
	const fastShooters = eshoot.filter((h) => dist(h, A) < 450 && (h.vx * (A.x - h.x) + h.vy * (A.y - h.y)) / (dist(h, A) || 1) > 50).length;
	if (pack.caught) {
		pack.fastSeen = w.t;   // giving ground is not working: they are faster than our pack
	}
	const recentTaken = w.hitLog.filter((x) => x.to === pack.team).reduce((a, x) => a + x.amt, 0);
	const recentDealt = w.hitLog.filter((x) => x.from === pack.team).reduce((a, x) => a + x.amt, 0);
	const canReach = ours.some((m) => m.role !== 'melee' && es.some((h) => dist(h, m) <= m.range));
	if (pack.flank.wings.size === 0 && pack.flankStarted) pack.raidSpent = true;
	return { raiders, shootSpeed, fastShooters, shootRush: w.t - (pack.fastSeen ?? -99) < 4, recentTaken, recentDealt,
		outranged: recentTaken > 60 && !canReach, ourCount: ours.length, theirCount: es.length,
		theirMelee: em.length, raidSpent: !!pack.raidSpent };
}

// What the commander can see, reduced to a few plain numbers and flags.
function readEnemy(w, pack) {
	const ours = team(w, pack.team), es = foes(w, pack.team), A = pack.anchor;
	const em = es.filter((h) => MELEE[h.role]), esoft = es.filter((h) => !MELEE[h.role]);
	let cx = 0, cy = 0, vx = 0, vy = 0; for (const h of es) { cx += h.x; cy += h.y; vx += h.vx; vy += h.vy; }
	const n = Math.max(1, es.length); cx /= n; cy /= n; vx /= n; vy /= n;
	let spread = 0; for (const h of es) spread += dist(h, { x: cx, y: cy }); spread /= n;
	const d = len(A.x - cx, A.y - cy) || 1;
	const approach = (vx * (A.x - cx) + vy * (A.y - cy)) / d;
	// A melee is charging only when it has run ahead of its own shooters toward us, not when it
	// just walks forward with its formation.
	let scx = cx, scy = cy;
	if (esoft.length) { scx = 0; scy = 0; for (const h of esoft) { scx += h.x; scy += h.y; } scx /= esoft.length; scy /= esoft.length; }
	const ahead = (h) => { const dd = len(A.x - scx, A.y - scy) || 1; return ((h.x - scx) * (A.x - scx) + (h.y - scy) * (A.y - scy)) / dd; };
	const meleeCharging = em.filter((h) => !pinned(h) && ahead(h) > 100 && dist(h, A) < 450 &&
		((h.vx * (A.x - h.x) + h.vy * (A.y - h.y)) / (dist(h, A) || 1)) > 20).length;
	return {
		em: em.length, esoft: esoft.length, meleeCharging, approach, spread,
		exposed: esoft.length >= 4 && em.every((h) => pinned(h)),   // their melee is dead or tied up by ours
		formedEnemy: spread < 170 && Math.abs(approach) < 35,
		room: A.ax >= 0 ? A.x - 140 : w.o.width - 140 - A.x,   // space behind us: we face +x, so our back is the left edge (and vice versa)
		ourMelee: ours.filter((m) => m.role === 'melee').length, ourArt: ours.filter((m) => m.role === 'artillery').length,
		ourShoot: ours.filter((m) => m.role === 'ranged').length,
		theirArt: es.filter((h) => h.role === 'artillery').length, siegeMinArt: pack.base.siegeMinArt,
		quiet: w.t - (w.lastHitT ?? 0),   // seconds since anyone hit anyone
		...threatRead(w, pack, ours, es, em, A),
		sieging: pack.plan === 'siege' && pack.phase !== 'creeping',   // standing off, not still closing in
		theirShoot: es.filter((h) => h.role === 'ranged' || h.role === 'archer').length,
	};
}

// ---------------------------------------------------------------- role tactics
// A plan is a combination of four role tactics, { position, melee, ranged, artillery }. Each plan table
// (PLANS, STORM_PLANS, WOLF_PLANS) is split into role tactics by the role each setting belongs to (KNOB_ROLE,
// anything else is group position; `release` goes to the role it releases), so the plan named X is the
// combination of the four tactics named X, and any mix of tactics is a valid combination too.
const TACTIC_ROLES = ['position', 'melee', 'ranged', 'artillery'];
const KNOB_ROLE = {
	meleeDoctrine: 'melee', autoAttack: 'melee', dive: 'melee', diveMinTargets: 'melee', diveRange: 'melee',
	maxStrikersPerTarget: 'melee', peelRadius: 'melee', flankForce: 'melee', flankTarget: 'melee', flankWidth: 'melee',
	flankDepth: 'melee', flankWait: 'melee', raidTarget: 'melee',
	shooterFocus: 'ranged', squadSize: 'ranged', laneLeash: 'ranged', kiteLeash: 'ranged',
	artilleryDoctrine: 'artillery', engagedWeight: 'artillery',
};
const tacticCache = new Map();
function tacticsOf(plans) {
	let t = tacticCache.get(plans);
	if (t) return t;
	t = Object.fromEntries(TACTIC_ROLES.map((r) => [r, {}]));
	for (const [name, p] of Object.entries(plans)) {
		for (const r of TACTIC_ROLES) t[r][name] = {};
		for (const [k, v] of Object.entries(p)) {
			if (k === 'release') { for (const r of ['melee', 'ranged', 'artillery']) if (v && v.includes(r)) t[r][name].release = [r]; }
			else t[KNOB_ROLE[k] || 'position'][name][k] = v;
		}
	}
	tacticCache.set(plans, t);
	return t;
}
// A plan name or a combination object -> the combination.
const comboOf = (plan) => (typeof plan === 'string' ? Object.fromEntries(TACTIC_ROLES.map((r) => [r, plan])) : plan);
// Its name: the plan name when all four tactics share it, else 'position/melee/ranged/artillery'.
const comboName = (c) => (TACTIC_ROLES.every((r) => c[r] === c.position) ? c.position : TACTIC_ROLES.map((r) => c[r]).join('/'));
// The pack's settings for a combination: base, then each role tactic (releases joined), then extra.
function composeF(base, plans, combo, extra) {
	const T = tacticsOf(plans), f = Object.assign({}, base, { release: null }), rel = [];
	for (const r of TACTIC_ROLES) for (const [k, v] of Object.entries(T[r][combo[r]] || {})) { if (k === 'release') rel.push(...v); else f[k] = v; }
	if (rel.length) f.release = rel;
	return Object.assign(f, extra);
}

// The pack's plan has one writer (setPlan) and one switching rule (planSwitchable). Sources, ranked, first with an
// opinion wins: a commander's order (pack.cmd.plan), a forced plan (headroom tests), the look-ahead's choice, the
// brain's rules. The look-ahead has its own interval and inertia, so a side with one switches at once; otherwise a
// new plan needs 2 s on the old one. 'hold', the answer to a charge, never waits.
function planFrom(w, pack, r, rules) {
	const off = w.ai[pack.team].disablePlans || [];
	r.game = isGame(w); r.fewPlan = w.ai[pack.team].fewPlan || 'surround';
	const cp = cmdOf(w, pack, 'plan');
	if (cp) return { plan: cp, why: () => 'commander order' };
	if (w.o.forcePlan && pack.team === (w.o.forceTeam || 0)) return { plan: w.o.forcePlan, why: () => 'forced for a headroom test' };
	// When finishing, the look-ahead chooses only among the closing plans (lookahead: FINISH_PLANS).
	if (w.ai[pack.team].lookahead && pack.lookPlan) return { plan: pack.lookPlan, why: () => 'look-ahead: best simulated trade' };
	let [plan, , why] = rules.find(([name, when], i) => i === rules.length - 1 || (!off.includes(name) && when(r)));
	if (plan === 'few') plan = r.fewPlan;
	return { plan, why };
}
const planDwell = (w, pack) => (w.ai[pack.team].lookahead ? 0 : 2);
const planSwitchable = (w, pack, name) => name !== pack.plan && (name === 'hold' || w.t - pack.planSince >= planDwell(w, pack));
function setPlan(w, pack, plans, combo, why, extra, text) {
	pack.plan = comboName(combo); pack.combo = combo; pack.planSince = w.t; pack.planWhy = why;
	pack.f = composeF(pack.base, plans, combo, extra);
	note(w, text ?? `plan ${pack.plan}: ${why}`, pack.team);
}
function commander(w, pack) {
	const brain = BRAINS[pack.brain];
	if (!brain || w.t - (pack.lastThink ?? -1) < (isGame(w) ? GAME.thinkEvery : 0.5)) return;
	pack.lastThink = w.t;
	if (pack.brain === 'gamepack') return gamePackDecide(w, pack);
	const r = readEnemy(w, pack);
	pack.read = r;
	const { plan, why } = planFrom(w, pack, r, brain.rules), combo = comboOf(plan);
	if (planSwitchable(w, pack, comboName(combo)))
		setPlan(w, pack, brain.plans || PLANS, combo, why(r),
			pack.brain === 'reactive' ? { dodge: w.o.reactiveDodge !== false, coordAbilities: !!w.o.abilities && sk(w, pack.team, 'abilities') === 'coordinated' } : {});
}

// ---------------------------------------------------------------- FORMATION
// One pack tick, in order: the group's position (anchor), slots and the zone, melee orders, shooter focus.
// The steps share one per-tick context `c`; each later step reads what the earlier ones put there.
function formationPlan(w, pack) {
	const f = pack.f, ms = team(w, pack.team), es = foes(w, pack.team), A = pack.anchor;
	if (!ms.length) return;
	const melee = ms.filter((m) => m.role === 'melee');
	const ranged = ms.filter((m) => m.role === 'ranged');
	const art = ms.filter((m) => m.role === 'artillery');
	for (const m of ms) m.assigned = undefined;   // this tick's target proposals, below; the unit's decide() makes the final choice
	// The shape depends only on the counts and the settings: built again only when either changes.
	const sc = pack._shape;
	const shape = sc && sc.f === f && sc.m === melee.length && sc.r === ranged.length && sc.a === art.length ? sc.shape
		: (pack._shape = { f, m: melee.length, r: ranged.length, a: art.length, shape: (SHAPES[f.shape] || SHAPES.line)({ melee: melee.length, ranged: ranged.length, artillery: art.length }, f) }).shape;
	const c = { f, ms, es, A, melee, ranged, art, shape, rearRank: maxD(shape.ranged, 0) };
	const prevPhase = pack.phase;
	positionAnchor(w, pack, c);
	assignSlots(w, pack, c);
	const { wasDiving, softInReach } = meleeOrders(w, pack, c);
	shooterFocusOrders(w, pack, c);
	surroundOrders(w, pack, c);
	if (pack.diving && !wasDiving) note(w, `dive: ${softInReach} enemy shooters in reach`, pack.team);
	if (pack.diving) pack.phase = 'diving';
	if (prevPhase !== pack.phase && pack.phase !== 'diving' && pack.brain !== 'reactive') note(w, `pack ${pack.phase}`, pack.team);
}

// Group position: turn toward the enemy and move the anchor (siege: stay outside their reach; standoff: hold
// our shooters' range, wait while they walk into our fire).
// Commander goals (pack.cmd, set from outside while paused: command.js), each until its time runs out:
//   place {x, y, face}  the anchor walks there at the formation's pace and faces `face` (or the nearest enemy)
//   engage (Set of enemy ids)  the formation closes on them by its plan; shooters rank them first, melee go for them
//   release (Set of our ids)   those units act freely (decideReleased)
//   plan (a plan name)         the commander's plan
// The units keep their own handling (slots, lanes, kiting, dodging): goals, not unit moves.
// A goal is live from the outside commander (pack.cmd) or, failing that, the combo director (pack.dir.goals).
const cmdOf = (w, pack, k) => {
	const c = pack.cmd && pack.cmd[k];
	if (c && c.until > w.t) return c.v;
	const d = pack.dir && pack.dir.goals[k];
	return d && d.until > w.t ? d.v : null;
};

// ---------------------------------------------------------------- the combo director
// Layers (PLAN_TACTICAL_COMBOS.md): observe (features, every director tick) -> director (the active combo, its phase,
// its role assignment, its goals) -> the formation commander (plan, anchor, slots) -> units (decide). The director
// speaks only through goals (place / engage / release / plan, the channel command.js uses), never through unit orders,
// and only every 0.5 s; selection every 2 s, only between combos.
// A combo is data, registered in COMBOS:
//   { name, priority, cooldown, enter(ctx) -> choices | null,                 entry precondition; the choices it returns are fixed
//     roles(ctx) -> { roleName: [units] },                                      role assignment, once, at start (and per phase if `reassign`)
//     phases: [{ name, goals(ctx) -> { place, engage, release, plan },          goals this phase hands down (refreshed every tick)
//                done(ctx) -> bool, abort(ctx) -> bool, min, max }],             success / abort predicates, dwell bounds in s
//     success(ctx) -> bool }                                                    the success signal logged at the end
// ctx = { w, pack, obs, choices, roles, phase, t0 (combo start), tp (phase start), units: { ours, theirs }, ids }
const COMBOS = {};
const DIRECTOR_EVERY = 0.5, SELECT_EVERY = 2;
// Features of the situation, plain numbers, from the side's own point of view (no unit names).
function observe(w, pack) {
	const me = pack.team, ours = team(w, me), es = foes(w, me);
	const by = (l, r) => l.filter((u) => u.role === r).length;
	const cen = (l) => { let x = 0, y = 0; for (const u of l) { x += u.x; y += u.y; } const n = Math.max(1, l.length); return { x: x / n, y: y / n }; };
	const oc = cen(ours), ec = cen(es);
	let near = Infinity; for (const m of ours) for (const e of es) near = Math.min(near, dist(m, e));
	// Their shape: principal axis of their positions, how elongated, and how fast they move along it.
	let sxx = 0, syy = 0, sxy = 0, vx = 0, vy = 0;
	for (const e of es) { const dx = e.x - ec.x, dy = e.y - ec.y; sxx += dx * dx; syy += dy * dy; sxy += dx * dy; vx += e.vx; vy += e.vy; }
	const n = Math.max(1, es.length), th = 0.5 * Math.atan2(2 * sxy, sxx - syy), tr = (sxx + syy) / n, det = (sxx * syy - sxy * sxy) / (n * n);
	const l1 = tr / 2 + Math.sqrt(Math.max(0, tr * tr / 4 - det)), l2 = tr / 2 - Math.sqrt(Math.max(0, tr * tr / 4 - det));
	const axis = { x: Math.cos(th), y: Math.sin(th) };
	const along = (vx / n) * axis.x + (vy / n) * axis.y;
	const toUs = len(oc.x - ec.x, oc.y - ec.y) || 1;
	const chasing = es.filter((e) => MELEE[e.role]).length ? es.filter((e) => MELEE[e.role] && (e.vx * (oc.x - e.x) + e.vy * (oc.y - e.y)) / (dist(e, oc) || 1) > 20).length / es.filter((e) => MELEE[e.role]).length : 0;
	const W = w.o.width, H = w.o.height;
	return {
		t: w.t, hpOurs: ours.reduce((a, u) => a + u.hp, 0), hpTheirs: es.reduce((a, u) => a + u.hp, 0), ours: ours.length, theirs: es.length, oursByRole: [by(ours, 'melee'), by(ours, 'ranged'), by(ours, 'artillery')], theirsByRole: [by(es, 'melee'), by(es, 'ranged'), by(es, 'artillery')],
		oc, ec, gapNear: near, dCentres: toUs, spreadTheirs: es.reduce((a, e) => a + dist(e, ec), 0) / n,
		column: { axis, ratio: Math.sqrt(l1 / Math.max(1, l2)), speedAlong: along }, approach: ((vx / n) * (oc.x - ec.x) + (vy / n) * (oc.y - ec.y)) / toUs,
		chaseShare: chasing, wallDist: Math.min(oc.x, W - oc.x, oc.y, H - oc.y), finishing: finishing(w, me),
	};
}
const briefing = (o) => `hp ${Math.round(o.hpOurs)}/${Math.round(o.hpTheirs)} ours ${o.oursByRole.join('/')} theirs ${o.theirsByRole.join('/')} gap ${o.gapNear.toFixed(0)} column ${o.column.ratio.toFixed(1)} along ${o.column.speedAlong.toFixed(0)} chasing ${(100 * o.chaseShare).toFixed(0)}%`;
function directorStep(w, pack) {
	const list = sk(w, pack.team, 'combos');
	if (!Array.isArray(list) || (w.forked && !(w.thinkTeams && w.thinkTeams.includes(pack.team)))) return;
	const D = pack.dir = pack.dir || { goals: {}, active: null, last: -99, selected: -99, cool: {}, stats: { starts: 0, aborts: 0, successes: 0, switches: 0 }, log: [] };
	if (w.t - D.last < DIRECTOR_EVERY - 1e-9) return;
	D.last = w.t;
	const obs = pack.obs = observe(w, pack);
	const say = (what, why) => { D.log.push({ t: +w.t.toFixed(2), what, why }); note(w, `combo ${what}${why ? ': ' + why : ''}`, pack.team); };
	const ctxOf = (A) => ({ w, pack, obs, choices: A.choices, roles: A.roles, phase: A.phase, t0: A.t0, tp: A.tp, units: { ours: team(w, pack.team), theirs: foes(w, pack.team) },
		ids: (l) => new Set(l.map((u) => u.id)) });
	const release = (why, kind) => {
		const A = D.active; D.active = null; D.goals = {};
		D.cool[A.combo.name] = w.t + (A.combo.cooldown ?? 5);
		D.stats[kind === 'success' ? 'successes' : 'aborts']++;
		say(`${kind} ${A.combo.name} after ${(w.t - A.t0).toFixed(1)} s, units released`, why + ' | ' + briefing(pack.obs));
	};
	if (D.active) {
		const A = D.active, ph = A.combo.phases[A.i], ctx = ctxOf(A);
		for (const u of [...A.roles.keys()]) if (!u.alive) A.roles.delete(u);
		const dwell = w.t - A.tp;
		if (!A.roles.size || ph.abort && dwell >= (ph.min ?? 0) && ph.abort(ctx)) return release(!A.roles.size ? 'no units left' : `${ph.name} aborted`, 'abort');
		if (ph.max && dwell > ph.max) return release(`${ph.name} timed out`, 'abort');
		if (dwell >= (ph.min ?? 0) && ph.done(ctx)) {
			if (A.i + 1 >= A.combo.phases.length) return release(A.combo.success && A.combo.success(ctx) ? 'success signal seen' : 'finished without the success signal', A.combo.success && A.combo.success(ctx) ? 'success' : 'abort');
			A.i++; A.tp = w.t; A.phase = A.combo.phases[A.i].name; D.stats.switches++;
			say(`${A.combo.name} -> ${A.phase}`, briefing(obs));
		}
		const g = A.combo.phases[A.i].goals(ctxOf(A)) || {};
		D.goals = {};
		for (const [k, v] of Object.entries(g)) if (v !== undefined && v !== null) D.goals[k] = { v, until: w.t + DIRECTOR_EVERY + 0.2 };
		return;
	}
	if (w.t - D.selected < SELECT_EVERY - 1e-9) return;
	D.selected = w.t;
	let best = null;
	for (const name of list) {
		const combo = COMBOS[name];
		if (!combo || (D.cool[name] ?? -1) > w.t) continue;
		const ctx = ctxOf({ choices: null, roles: new Map(), phase: null, t0: w.t, tp: w.t });
		const choices = combo.enter(ctx);
		if (choices && (!best || (combo.priority ?? 0) > (best.combo.priority ?? 0))) best = { combo, choices };
	}
	if (!best) return;
	const A = { combo: best.combo, choices: best.choices, roles: new Map(), i: 0, phase: best.combo.phases[0].name, t0: w.t, tp: w.t };
	const rl = best.combo.roles(ctxOf(A));
	for (const [r, l] of Object.entries(rl)) for (const u of l) A.roles.set(u, r);
	D.active = A; D.stats.starts++;
	say(`start ${A.combo.name} (${[...new Set(A.roles.values())].map((r) => r + ' ' + [...A.roles.values()].filter((x) => x === r).length).join(', ')})`, briefing(obs));
	const g = A.combo.phases[0].goals(ctxOf(A)) || {};
	for (const [k, v] of Object.entries(g)) if (v !== undefined && v !== null) D.goals[k] = { v, until: w.t + DIRECTOR_EVERY + 0.2 };
}
function positionAnchor(w, pack, c) {
	const { f, ms, es, A, melee, ranged, art, shape, rearRank } = c;
	const place = cmdOf(w, pack, 'place');
	if (place) {
		const fx = place.face ? place.face[0] : (nearest(A, es) || A).x, fy = place.face ? place.face[1] : (nearest(A, es) || A).y;
		const dx = fx - A.x, dy = fy - A.y, d = len(dx, dy) || 1;
		A.ax += (dx / d - A.ax) * f.turnRate; A.ay += (dy / d - A.ay) * f.turnRate;
		const an = len(A.ax, A.ay) || 1; A.ax /= an; A.ay /= an;
		const gx = place.x - A.x, gy = place.y - A.y, gd = len(gx, gy), st = Math.min(gd, paceOf(w, pack.team) * 0.9 * w.o.dt);
		if (gd > 1) { A.x += gx / gd * st; A.y += gy / gd * st; }
		pack.phase = 'ordered'; pack.waiting = false;
		return;
	}
	let cx = 0, cy = 0; for (const m of ms) { cx += m.x; cy += m.y; } cx /= ms.length; cy /= ms.length;
	const eng = cmdOf(w, pack, 'engage');
	let near = nearest({ x: cx, y: cy }, eng ? es.filter((h) => eng.has(h.id)).concat([]) : es) || nearest({ x: cx, y: cy }, es);
	if (f.oblique && es.length > 2 && near && !eng) {
		// Oblique (local superiority): face the end of the enemy line with fewer enemies near it, so our whole
		// pack engages part of theirs and the rest arrives piecemeal. Ends = the extremes across our facing.
		const lx = -A.ay, ly = A.ax, side = (h) => (h.x - A.x) * lx + (h.y - A.y) * ly;
		let lo = es[0], hi = es[0]; for (const h of es) { if (side(h) < side(lo)) lo = h; if (side(h) > side(hi)) hi = h; }
		const crowd = (e) => es.filter((h) => dist(h, e) < 250).length;
		near = crowd(lo) <= crowd(hi) ? lo : hi;
	}
	pack.waiting = false;
	if (near) {
		let hx = 0, hy = 0, n = 0, closing = 0;
		for (const h of es) if (dist(h, near) < 250) { hx += h.x; hy += h.y; n++; closing += -(h.vx * A.ax + h.vy * A.ay); }
		hx /= n; hy /= n; closing /= n;
		// Siege faces the enemy's fire (shooters and artillery), not whichever melee is nearest.
		const fire = es.filter((h) => !MELEE[h.role]);
		if (f.anchorMode === 'siege' && fire.length) { hx = 0; hy = 0; for (const h of fire) { hx += h.x; hy += h.y; } hx /= fire.length; hy /= fire.length; }
		const dx = hx - A.x, dy = hy - A.y, d = len(dx, dy) || 1;
		A.ax += (dx / d - A.ax) * f.turnRate; A.ay += (dy / d - A.ay) * f.turnRate;
		const an = len(A.ax, A.ay) || 1; A.ax /= an; A.ay /= an;
		const frontDist = (near.x - A.x) * A.ax + (near.y - A.y) * A.ay;
		const maxStep = (f.anchorSpeed || paceOf(w, pack.team) * 0.9) * w.o.dt;
		let step = 0;
		if (f.anchorMode === 'siege') {
			// Keep every member outside enemy direct-fire reach; creep in until our artillery reaches.
			// Stay outside their direct fire and, where our forward artillery allows, their artillery too.
			// With almost no melee of our own to screen, enemy melee are kept at arm's length too.
			const unscreened = melee.length < 3;
			let danger = -Infinity, awayX = 0, awayY = 0;
			for (const e of es) if (!MELEE[e.role] || unscreened)
				for (const m of ms) {
					// Our artillery is too slow to dodge a shell, so it keeps a wider berth from enemy artillery.
					const artMargin = m.role === 'artillery' ? f.siegeOwnArtMargin : f.siegeArtMargin;
					const reach = MELEE[e.role] ? f.meleeKeepAway : e.range + (e.role === 'artillery' ? artMargin : f.siegeMargin);
					const v = reach - dist(e, m);
					if (v > danger) danger = v;
					if (v > 0) { const dd = dist(e, m) || 1; awayX += (m.x - e.x) / dd * v; awayY += (m.y - e.y) / dd * v; }
				}
			const artReach = frontDist + maxD(shape.artillery, rearRank) - (reachOf(w, pack.team, 'artillery') - 15);
			step = danger > 0 ? -Math.min(danger, maxStep) : artReach > 0 ? Math.min(artReach, maxStep) : 0;
			pack.phase = step < 0 ? 'giving ground' : step > 0 ? 'creeping' : 'siege';
			// Caught: we have been giving ground for 1.5 s and they are still closer than when we started.
			if (step < 0) { if (pack.retreatFrom === undefined) pack.retreatFrom = { t: w.t, danger }; }
			else pack.retreatFrom = undefined;
			pack.caught = pack.retreatFrom !== undefined && w.t - pack.retreatFrom.t > 1.5 && danger > pack.retreatFrom.danger + 5;
			// Give ground straight away from what threatens us.
			const al = len(awayX, awayY);
			if (danger > 0 && al > 0) {
				const ux = awayX / al, uy = awayY / al, ul = len(ux, uy) || 1;   // normalised twice, as the tuned runs were
				pack.away = { x: ux / ul, y: uy / ul };
			} else pack.away = null;
		} else {
			const err = frontDist + rearRank - reachOf(w, pack.team, 'ranged') * f.standoff;
			const outside = frontDist > ROLE.archer.range + 60;
			const gate = !f.syncGate || pack.formed || outside;
			pack.waiting = f.holdWhileClosing && closing > f.closingSpeed && frontDist < reachOf(w, 1 - pack.team, 'artillery') + 60;
			step = err <= 0 || !gate || pack.waiting ? 0 : Math.min(err, maxStep);
			pack.phase = !gate ? 'forming' : pack.waiting ? 'waiting' : err > 0 ? 'advancing' : 'holding';
		}
		let mx = A.ax * step, my = A.ay * step;
		if (step < 0 && pack.away) { mx = pack.away.x * -step; my = pack.away.y * -step; }
		if (step < 0) {
			// Giving ground: slide along the wall toward open space instead of backing into it.
			const bx = A.x + mx * 40, by = A.y + my * 40, W = w.o.width, H = w.o.height, m = 110;
			if (bx < m || bx > W - m || by < m || by > H - m) {
				const sl = Math.abs(step), ux = mx / sl, uy = my / sl, tx = -uy, ty = ux, side = ((W / 2 - A.x) * tx + (H / 2 - A.y) * ty) >= 0 ? 1 : -1;
				mx = tx * side * Math.abs(step); my = ty * side * Math.abs(step);
			}
		}
		A.x += mx; A.y += my;
	}
	// No enemy known (perception): search by advancing along the facing at the anchor pace.
	if (!near && isGame(w) && w.o.perception === true && team(w, 1 - pack.team).length) {
		const st = (f.anchorSpeed || paceOf(w, pack.team) * 0.9) * w.o.dt; A.x += A.ax * st; A.y += A.ay * st; pack.phase = 'searching';
	}
	A.x = clamp(A.x, 60, w.o.width - 60); A.y = clamp(A.y, 60, w.o.height - 60);
}

// Slots for every member around the anchor, whether the shape is formed, the strike zone and the threat test.
function assignSlots(w, pack, c) {
	const { f, ms, es, A, melee, ranged, art, shape, rearRank } = c;
	const px = -A.ay, py = A.ax;
	const lat = (u) => (u.x - A.x) * px + (u.y - A.y) * py;
	const dep = (u) => -((u.x - A.x) * A.ax + (u.y - A.y) * A.ay);
	const place = (list, slots) => {
		const members = list.slice().sort((a, b) => lat(a) - lat(b) || dep(a) - dep(b));
		const order = slots.slice().sort((a, b) => a.l - b.l || a.d - b.d);
		members.forEach((u, i) => {
			const s = order[i];
			u.slotX = A.x - A.ax * s.d + px * s.l; u.slotY = A.y - A.ay * s.d + py * s.l; u.hasSlot = true;
		});
	};
	place(melee, shape.melee); place(ranged, shape.ranged); place(art, shape.artillery);
	let off = 0; for (const m of ms) off = Math.max(off, len(m.slotX - m.x, m.slotY - m.y));
	pack.formed = off < f.syncRadius || (pack.formed && off < f.syncRadius * 4);
	const all = [...shape.melee, ...shape.ranged, ...shape.artillery];
	const minL = Math.min(...all.map((s) => s.l)) - f.zoneSideMargin, maxL = Math.max(...all.map((s) => s.l)) + f.zoneSideMargin;
	const minD = Math.min(...all.map((s) => s.d)), backD = Math.max(...all.map((s) => s.d)) + f.zoneBehind;
	let rcx = A.x, rcy = A.y;
	if (ranged.length) { rcx = 0; rcy = 0; for (const r of ranged) { rcx += r.x; rcy += r.y; } rcx /= ranged.length; rcy /= ranged.length; }
	pack.zone = { front: minD - f.zoneDepth, back: backD, minL, maxL, cover: { x: rcx, y: rcy, r: reachOf(w, pack.team, 'ranged') * f.coverFraction } };
	const inZone = (h) => {
		if (len(h.x - rcx, h.y - rcy) > reachOf(w, pack.team, 'ranged') * f.coverFraction) return false;
		const d = dep(h), l = lat(h);
		return d >= minD - f.zoneDepth && d <= backD && l >= minL && l <= maxL;
	};
	pack.inZone = inZone;
	// Threat to the back line: inside the shape, on a soft member, or an enemy melee near one (peel early).
	const oursSoft = ms.filter((m) => !MELEE[m.role]);
	pack.threatens = (h) => dep(h) > minD || (h.chargeEnd > w.t && h.chargeT && !MELEE[h.chargeT.role]) ||
		(h.target && h.target.alive && h.target.team === pack.team && !MELEE[h.target.role] && gap(h, h.target) < 40) ||
		(MELEE[h.role] && oursSoft.some((m) => dist(m, h) < f.peelRadius));
	Object.assign(c, { px, py, lat, dep, minL, maxL, minD, backD, inZone });
}

// Melee orders: dive, the melee doctrine (screen / zone / flank / anvil / auto), flank wings, target claims.
function meleeOrders(w, pack, c) {
	const { f, ms, es, A, melee, ranged, art, shape, rearRank } = c;
	const { px, py, lat, dep, minL, maxL, minD, backD, inZone } = c;
	const enemyMeleeNear = es.some((h) => MELEE[h.role] && (inZone(h) || dist(h, A) < f.zoneDepth + 60));
	const softInReach = es.filter((h) => !MELEE[h.role] && -dep(h) > 0 && -dep(h) <= f.diveRange).length;
	const wasDiving = pack.diving;
	pack.diving = f.dive && f.meleeDoctrine !== 'screen' && !enemyMeleeNear && melee.length > 0 && softInReach >= f.diveMinTargets;
	const diveTarget = (h) => -dep(h) <= f.diveRange && dep(h) < backD && lat(h) >= minL - 120 && lat(h) <= maxL + 120;
	const eligible = (h) => inZone(h) || (pack.diving && diveTarget(h));
	const enemyMeleeComing = es.some((h) => MELEE[h.role] && dist(h, A) <= f.diveRange + 200 && !pinned(h));
	const doctrine = f.meleeDoctrine === 'auto' ? (pack.flank.phase !== 'none' ? f.autoAttack
		: enemyMeleeComing ? 'screen' : f.autoAttack) : f.meleeDoctrine;
	const soft = es.filter((h) => !MELEE[h.role]);
	let sx = 0, sy = 0; for (const h of soft) { sx += h.x; sy += h.y; }
	const softC = soft.length ? { x: sx / soft.length, y: sy / soft.length } : null;
	// Flank wings (flank / anvil): fixed once; out sideways, along their flank, strike from behind.
	for (const [m] of pack.flank.wings) if (!m.alive) pack.flank.wings.delete(m);
	if (pack.flank.start && pack.flank.wings.size < pack.flank.start / 2) { pack.raidSpent = true; pack.flank = { phase: 'none', since: w.t, wings: new Map() }; note(w, 'raid broken: wings fall back', pack.team); }
	const exposed = softC && soft.length >= f.diveMinTargets && es.filter((h) => MELEE[h.role]).every((h) => pinned(h) || dist(h, A) > f.diveRange + 200);
	if ((doctrine === 'flank' || doctrine === 'anvil') && pack.flank.phase === 'none' && !pack.raidSpent && (exposed || (f.flankForce && softC))) {
		const byLat = melee.slice().sort((a, b) => lat(a) - lat(b));
		const k = doctrine === 'flank' ? Math.floor(byLat.length / 2) : Math.floor(byLat.length / 4);
		const wings = new Map();
		byLat.forEach((m, i) => { if (i < k) wings.set(m, -1); else if (i >= byLat.length - k) wings.set(m, 1); });
		if (wings.size >= 2) { pack.flank = { phase: 'out', since: w.t, wings, start: wings.size }; pack.flankStarted = true; note(w, `flank: ${wings.size} melee leave the line`, pack.team); }
	}
	if (pack.flank.phase !== 'none' && (!softC || !pack.flank.wings.size || (doctrine !== 'flank' && doctrine !== 'anvil')))
		pack.flank = { phase: 'none', since: w.t, wings: new Map() };
	const wingOf = pack.flank.wings;
	if (wingOf.size) {
		const halfW = (maxL - minL) / 2;
		const way = (side) => pack.flank.phase === 'out'
			? { x: A.x + px * side * (halfW + f.flankWidth * 0.5), y: A.y + py * side * (halfW + f.flankWidth * 0.5) }
			: { x: softC.x + px * side * f.flankWidth + A.ax * f.flankDepth, y: softC.y + py * side * f.flankWidth + A.ay * f.flankDepth };
		const wings = [...wingOf.entries()];
		const arrived = wings.every(([m, side]) => dist(m, way(side)) < 50);
		if (pack.flank.phase === 'out' && (arrived || w.t - pack.flank.since > f.flankWait)) { pack.flank.phase = 'along'; pack.flank.since = w.t; }
		else if (pack.flank.phase === 'along' && (arrived || w.t - pack.flank.since > f.flankWait)) { pack.flank.phase = 'strike'; pack.flank.since = w.t; note(w, 'flank: wings strike from behind', pack.team); }
		for (const [m, side] of wings) {
			m.wing = side;
			const answer = meleeAnswer(w, m);
			m.answering = !!answer;
			if (answer) { m.assigned = answer; m.flankGoal = null; continue; }
			if (pack.flank.phase === 'strike') { m.assigned = m.target && m.target.alive ? m.target : (f.flankTarget === 'artillery' && nearest(m, es, (h) => h.role === 'artillery')) || nearest(m, soft) || nearest(m, es); m.flankGoal = null; }
			else { m.assigned = null; m.flankGoal = way(side); }
		}
	}
	for (const m of melee) if (!wingOf.has(m)) { m.wing = 0; m.flankGoal = null; }
	const screenOnly = (h, m) => gap(h, m) < 30 || pack.threatens(h);
	const claims = new Map();
	const centre = melee.filter((m) => !wingOf.has(m));
	for (const m of centre) {
		const answer = meleeAnswer(w, m);
		// It keeps its last target while that stays eligible (stickiness); its last target is its own final choice.
		m.assigned = answer || (m.target && m.target.alive && (doctrine === 'screen' ? screenOnly(m.target, m) : eligible(m.target)) ? m.target : null);
		m.answering = !!answer;
		if (m.assigned) claims.set(m.assigned, (claims.get(m.assigned) || 0) + 1);
		}
		for (const m of centre) {
		if (m.assigned) continue;
		let t = null, best = Infinity;
		for (const h of es) {
			if (!(doctrine === 'screen' ? screenOnly(h, m) : eligible(h)) || (claims.get(h) || 0) >= f.maxStrikersPerTarget) continue;
			const k = (pack.threatens(h) ? 0 : 1e5) + dist(h, m);
			if (k < best) { best = k; t = h; }
		}
		if (t) { m.assigned = t; claims.set(t, (claims.get(t) || 0) + 1); }
		}
		for (const m of melee)
		m.state = m.flankGoal ? 'flank' : !m.assigned ? 'slot' :
		m.answering ? 'answer' : m.wing ? 'behind' : pack.threatens(m.assigned) ? 'peel' : inZone(m.assigned) ? 'strike' : 'dive';
	return { wasDiving, softInReach };
}

// Encircle (f.surround): the focus target; melee spread evenly on a ring around it, the first angle on its
// escape (its movement, or away from us); shooters on a 200-degree arc facing us at 0.8 of their reach;
// artillery behind them at 0.85 of theirs. Each member gets a goal point (u.surroundGoal).
function surroundOrders(w, pack, c) {
	const { es, ms, melee, ranged, art } = c;
	for (const u of ms) u.surroundGoal = null;
	if (!pack.f.surround || !es.length) return;
	let cx = 0, cy = 0; for (const m of ms) { cx += m.x; cy += m.y; } cx /= ms.length; cy /= ms.length;
	const T = pack.packFocus && pack.packFocus.alive ? pack.packFocus : nearest({ x: cx, y: cy }, es);
	pack.surroundTarget = T;
	const sp = len(T.svx, T.svy);
	let esc = sp > 10 ? Math.atan2(T.svy, T.svx) : Math.atan2(T.y - cy, T.x - cx), home = Math.atan2(cy - T.y, cx - T.x);
	if (pack.f.surroundCorner) {
		// Cornering: our side faces the arena centre from the target, so moving away from us runs into a wall;
		// the melee ring's first angle sits on the wall side, cutting the slide along it.
		home = Math.atan2(w.o.height / 2 - T.y, w.o.width / 2 - T.x);
		esc = home + Math.PI;
	}
	const at = (a, r) => ({ x: clamp(T.x + Math.cos(a) * r, 20, w.o.width - 20), y: clamp(T.y + Math.sin(a) * r, 20, w.o.height - 20) });
	const assign = (list, pts) => {
		const free = pts.slice();
		for (const u of list.slice().sort((a, b) => dist(a, T) - dist(b, T))) {
			let bi = 0; for (let i = 1; i < free.length; i++) if (dist(u, free[i]) < dist(u, free[bi])) bi = i;
			if (free.length) { u.surroundGoal = free.splice(bi, 1)[0]; u.assigned = T; }
		}
	};
	const f = pack.f, ringR = Math.max(2 * 16, f.surroundRing * (isGame(w) ? reachOf(w, pack.team, 'melee') + 16 + GAME.typicalR : 30));
	let meleeAngles = melee.map((_, i) => esc + (2 * Math.PI * i) / melee.length);
	if (f.surroundMelee === 'screen') {
		// Screen: melee on a 120-degree arc facing us, closer than our casters, so they are the bodies nearest the
		// target (its auto attacks pick the nearest) and our casters behind them stay out of its fire.
		meleeAngles = melee.map((_, i) => home + (melee.length > 1 ? (i / (melee.length - 1) - 0.5) : 0) * (120 * Math.PI / 180));
		assign(melee, meleeAngles.map((a) => at(a, Math.max(ringR, 0.45 * (isGame(w) ? reachOf(w, pack.team, 'ranged') : 150)))));
	} else assign(melee, meleeAngles.map((a) => at(a, ringR)));
	const reachR = (u) => (isGame(w) ? u.range + (u.role === 'artillery' ? 0 : u.r + GAME.typicalR) : ROLE[u.role].range + 20);   // its own reach
	const arc = f.surroundArc * Math.PI / 180;
	let shotAngles = ranged.map((u, i) => home + (ranged.length > 1 ? (i / (ranged.length - 1) - 0.5) : 0) * arc);
	if (f.surroundLanes && meleeAngles.length) {
		// Move each shooter angle to the nearest gap between melee angles (inside the arc), so its line to the
		// target passes between our melee rather than through them.
		const gaps = meleeAngles.map((a, i) => a + Math.PI / Math.max(1, meleeAngles.length));
		const wrap = (x) => Math.atan2(Math.sin(x), Math.cos(x));
		shotAngles = shotAngles.map((a) => {
			let best = a, bd = Infinity;
			for (const g of gaps) { const d = Math.abs(wrap(g - a)); if (d < bd && Math.abs(wrap(g - home)) <= arc / 2 + 0.3) { bd = d; best = g; } }
			return best + wrap(a - best) * 0.25;   // stay near the gap, keep a little spread
		});
	}
	assign(ranged, ranged.map((u, i) => at(shotAngles[i], f.surroundDist * reachR(u))));
	assign(art, art.map((u, i) => at(home + (art.length > 1 ? (i / (art.length - 1) - 0.5) : 0) * (120 * Math.PI / 180), 0.85 * reachR(u))));
}
// Shooter focus: one target for all, or one per squad (shooterFocus 'one' / 'squads').
function shooterFocusOrders(w, pack, c) {
	const { f, ms, es, A, melee, ranged, art, shape, rearRank } = c;
	const { lat } = c;
	const inReachOf = (h, list) => list.filter((r) => gap(r, h) <= r.range).length;
	const pickFocus = (list) => {
		let best = null, bk = Infinity;
		for (const h of es) {
			const n = inReachOf(h, list);
			if (!n) continue;
			const left = h.hp - (pack.pending.get(h) || 0);
			const k = (pack.threatens(h) ? 0 : 1e6) + (left <= 0 ? 5e5 : 0) + left / n;
			if (k < bk) { bk = k; best = h; }
		}
		return best;
	};
	pack.packFocus = f.shooterFocus === 'one' ? pickFocus(ranged) : null;
	pack.squadFocus = new Map();
	if (sk(w, pack.team, 'leaderFire')) leaderFire(w, pack, c);
	if (f.shooterFocus === 'squads') {
		const order = ranged.slice().sort((a, b) => lat(a) - lat(b));
		for (let i = 0; i < order.length; i += f.squadSize) {
			const squad = order.slice(i, i + f.squadSize), t = pickFocus(squad);
			for (const r of squad) pack.squadFocus.set(r, t);
		}
	}
}

// Leader fire control (skill leaderFire). Each tick: targets in reach of our shooters, threats to our back line
// first, then by damage per second removed per health left; each gets the nearest free shooters until their
// expected damage (chance to hit: the side's hit rate on dodging targets, 0.9 on targets that cannot dodge) is 1.1x
// its health left. With wind-ups a group is held until every member is prepared (at most 0.5 s after the first),
// so the shots arrive together; a target that cannot dodge is fired at at once. Shooters without orders act alone.
function leaderFire(w, pack, c) {
	const rel = pack.f.release && pack.f.release.includes('ranged');
	const shooters = rel ? [] : c.ranged, es = c.es;
	for (const u of c.ranged) { u.fireOrder = null; u.fireHold = false; u.aimOffset = 0; }
	if (!shooters.length || !es.length) return;
	const T = [];
	for (const h of es) {
		const left = h.hp - (pack.pending.get(h) || 0);
		if (left <= 0) continue;
		const reach = shooters.filter((u) => gap(u, h) <= u.range);
		if (reach.length) T.push({ h, left, reach, k: (pack.threatens(h) ? 0 : 1e6) - (h.dmg / (h.cdMax || 1)) / left * 1e3 });
	}
	T.sort((a, b) => a.k - b.k);
	const free = new Set(shooters);
	for (const t of T) {
		const group = [], cand = t.reach.filter((u) => free.has(u)).sort((a, b) => dist(a, t.h) - dist(b, t.h));
		let exp = 0;
		for (const u of cand) { group.push(u); free.delete(u); exp += u.dmg * (canDodge(w, t.h, u) ? pack.hitRate ?? 0.3 : 0.9); if (exp >= t.left * 1.1) break; }
		if (!group.length) continue;
		const allReady = group.every((u) => prepared(w, u)), anyReady = group.some((u) => prepared(w, u));
		const since = anyReady ? (t.h._holdSince && t.h._holdTeam === pack.team ? t.h._holdSince : w.t) : null;
		t.h._holdSince = since; t.h._holdTeam = pack.team;
		const hold = w.o.windUp && !allReady && group.some((u) => canDodge(w, t.h, u)) && since !== null && w.t - since < 0.5;
		// Bracket: a target that can dodge gets shots at it and a step to either side (centre, left, right, ...).
		const br = sk(w, pack.team, 'leaderBracket');
		group.forEach((u, i) => { u.fireOrder = t.h; u.fireHold = hold; u.aimOffset = br && group.length > 1 && canDodge(w, t.h, u) ? [0, 1, -1][i % 3] * br : 0; });
	}
}

// Does this side step out of shells? Skill dodgeShells; 'plan' = only when its current plan says so (f.dodge).
const shellDodge = (w, pack) => { const d = sk(w, pack.team, 'dodgeShells'); return d === true || d === 'smart' || (d === 'plan' && !!pack.f.dodge); };
// Predicted shell landings: a unit inside a splash that has not landed yet steps straight out.
function dodgeVector(w, u) {
	if (w.fields) for (const f of w.fields) {
		if (f.team === u.team || f.from > w.t || f.until < w.t + 0.5) continue;
		const d = len(u.x - f.x, u.y - f.y);
		if (d <= f.r + u.r) return d < 0.5 ? { x: u.x + 30, y: u.y } : { x: u.x + (u.x - f.x) / d * 40, y: u.y + (u.y - f.y) / d * 40 };
	}
	return sk(w, u.team, 'dodgeShells') === 'smart' ? smartEscape(w, u) : shellEscape(u.x, u.y, u.r, u.speed, u.team, w.shells, w.t);
}
// Smart dodge: only when standing inside an enemy shell's future blast. Candidate spots: staying, and 16
// directions at the distance it can cover before that earliest shell lands; each spot counts the enemy shells
// whose blast covers it (a shell that lands after the unit could arrive counts too). Goes to the spot under the
// fewest blasts, then the shortest move; returns null if staying is already best.
// Blasts to come (skill castDodge): every enemy gun mid-cast lobs at its target's position at its release.
function castBlasts(w, team) {
	if (w._cbT === w.t && w._cb && w._cb[team]) return w._cb[team];
	if (w._cbT !== w.t) { w._cb = [null, null]; w._cbT = w.t; }
	const out = [];
	for (const g of w.units) {
		if (!g.alive || g.team === team || g.role !== 'artillery' || !(g.prep > 0)) continue;
		const T = g.target;
		if (!T || !T.alive || T.team !== team) continue;
		const rel = w.t + Math.max(0, windUp(w, g) - g.prep) / (g.tr || 1);
		out.push({ x: T.x, y: T.y, t: rel + len(T.x - g.x, T.y - g.y) / lobV(g), splash: blastR(g), src: g, tgt: T });
	}
	return (w._cb[team] = out);
}
function smartEscape(w, u) {
	let sh = w.shells.filter((s) => s.src.team !== u.team && s.t > w.t && !s.slow);
	if (isGame(w) && sk(w, u.team, 'castDodge')) sh = sh.concat(castBlasts(w, u.team).filter((b) => b.tgt !== u));
	let first = Infinity;
	for (const s of sh) if (len(u.x - s.x, u.y - s.y) <= s.splash + u.r + 4 && s.t < first) first = s.t;
	if (first === Infinity) return null;
	const cover = (x, y) => { let k = 0; for (const s of sh) if (len(x - s.x, y - s.y) <= s.splash + u.r + 4) k++; return k; };
	const E = Math.max(8, u.speed * (first - w.t + 0.1));
	let best = null, bk = cover(u.x, u.y), bd = 0;
	for (const f of [1, 0.6]) for (let i = 0; i < 16; i++) {
		const a = i * Math.PI / 8, x = clamp(u.x + Math.cos(a) * E * f, u.r, w.o.width - u.r), y = clamp(u.y + Math.sin(a) * E * f, u.r, w.o.height - u.r);
		const k = cover(x, y), d = len(x - u.x, y - u.y);
		if (k < bk || (k === bk && best && d < bd)) { bk = k; bd = d; best = { x, y }; }
	}
	return best;
}

// A released unit leaves its slot and acts at its own full speed, still on the pack's target priorities.
function decideReleased(w, u, D, pack, es) {
	const f = pack.f;
	u.state = 'rush';
	if (u.role === 'melee') {
		let t = meleeAnswer(w, u);
		if (!t && u.target && u.target.alive && !MELEE[u.target.role]) t = u.target;
		if (!t) {
			const want = f.raidTarget === 'artillery' ? es.filter((h) => h.role === 'artillery') : es.filter((h) => !MELEE[h.role]);
			const claimed = (h) => w.units.filter((x) => x.alive && x.team === u.team && x.target === h && x.role === 'melee').length;
			t = nearest(u, want, (h) => claimed(h) < 2) || nearest(u, es);
		}
		return decMelee(w, u, t, D);
	}
	if (u.role === 'artillery') return decArtillery(w, u, artilleryTarget(w, u, es, null), D, 0, 0, false);
	decDirect(w, u, shooterTarget(w, pack, u, es, true), D, u.x, u.y, Infinity, es);
	u.state = 'rush';
}

// Game rules kiter standoff: a hostile closer than the standoff -> move to the standoff point on the ray from it
// through the unit, at the backpedal speed (ENEMY_DESIGN / encounter_ai.cpp MOVE_TO standoff). Casting goes on, and
// nothing else walks this tick.
function kiterRetreat(w, u, es, D) {
	if (!isGame(w) || !u.standoff) return false;
	const h = nearest(u, es);
	if (!h) return false;
	const d = dist(u, h);
	if (d >= u.standoff) return false;
	const k = u.standoff / (d || 1);
	goTo(D, h.x + (u.x - h.x) * k, h.y + (u.y - h.y) * k, 0, GAME.kiterBackpedal);
	D.keep = true; u.state = 'kite';
	return true;
}
// Save the wounded (skill saveWounded = health fraction, game rules): a unit below it backs away from the nearest
// enemy toward our side; it lives, and in a gauntlet it is healed for the next fight.
function saveWounded(w, u, es, D) {
	const fr = sk(w, u.team, 'saveWounded');
	if (!isGame(w) || !fr || u.hp > fr * u.maxhp || !es.length) return false;
	// Finishing: every attacker counts and the fight is about to end, so the wounded keep fighting (against a lone
	// player this is always so).
	if (finishing(w, u.team)) return false;
	// Only while healthy units hold the line: with half of us or more wounded, backing off is a rout (all retreat
	// into a corner, nobody shoots back, all die: hand-commanded game vs swarm, 26 -> 0 in 12 s).
	const ours = team(w, u.team);
	if (ours.filter((m) => m.hp <= fr * m.maxhp).length * 2 >= ours.length) return false;
	const e = nearest(u, es);
	if (!e || dist(u, e) > (e.range || 0) + e.speed * 1.5 + 60) return false;   // nothing close enough to finish it

	const home = u.team === 0 ? 40 : w.o.width - 40, ax = u.x - e.x, ay = u.y - e.y, l = len(ax, ay) || 1;
	goTo(D, u.x + ax / l * 60 + (home - u.x) * 0.2, u.y + ay / l * 60); u.state = 'retreat';
	return true;
}
// A commander's order (command.js: a person or an outside planner gives them while the battle is paused), until
// order.until, in place of the unit's own AI:
//   move {x, y}      walk there, hitting whatever is in reach on the way; done on arrival
//   attack {target}  go for that enemy (its id) and hit it; done when it is dead
//   hold             stay, hit whatever is in reach; done when `until` passes
//   retreat {x, y}   walk there without attacking; done on arrival
// A finished order (or one whose `until` passed) is logged in w.orderEvents and the unit is under its own AI again.
// Guns still fire through the pack's artillery planner when it runs.
function decideOrder(w, u, D) {
	const o = u.order, es = foes(w, u.team);
	// An order ends when it is done (arrived, target dead) and the unit goes back under its own AI at once.
	const arrived = (o.do === 'move' || o.do === 'retreat') && len(o.x - u.x, o.y - u.y) <= (o.radius || 14);
	if (arrived || (o.do === 'attack' && !w.units.some((h) => h.id === o.target && h.alive))) {
		(w.orderEvents = w.orderEvents || []).push({ t: w.t, id: u.id, do: o.do, why: arrived ? 'arrived' : 'target dead' });
		u.order = null; return decideOwn(w, u, D);
	}
	// In reach, nearest first; a shooter takes the nearest with a clear lane (a shot hits the first body).
	const inReach = () => {
		const c = es.map((h) => [u.role === 'artillery' ? dist(u, h) : gap(u, h), h]).filter(([g]) => g <= u.range).sort((x, y) => x[0] - y[0]);
		if (u.role !== 'ranged') return c.length ? c[0][1] : null;
		for (const [, h] of c) if (laneClear(w, u, h)) return h;
		return c.length ? c[0][1] : null;
	};
	// Hitting on the way or in place: the order's own walk (if any) is already set, nothing else walks.
	const hit = (t) => {
		if (!t) return;
		D.keep = true;
		if (MELEE[u.role]) decMelee(w, u, t, D); else if (u.role === 'artillery') decArtillery(w, u, t, D, u.x, u.y, true); else decDirect(w, u, t, D, u.x, u.y, 0, es);
	};
	if (o.do === 'attack') {
		const T = w.units.find((h) => h.id === o.target && h.alive);
		if (!T) { u.order = null; return decideOwn(w, u, D); }
		if (MELEE[u.role]) decMelee(w, u, T, D);
		else if (u.role === 'artillery') decArtillery(w, u, T, D, u.x, u.y, false);
		else decDirect(w, u, T, D, T.x, T.y, Infinity, es);
		u.state = 'order';
		return;
	}
	if (o.do === 'move' || o.do === 'retreat') {
		if (len(o.x - u.x, o.y - u.y) > 4) goTo(D, o.x, o.y);
		u.state = o.do;
		if (o.do === 'move') hit(inReach());
		return;
	}
	u.state = 'hold';   // hold
	hit(inReach());
}
// The unit's own AI: the pack's, or none (every unit for itself).
function decideOwn(w, u, D) {
	if (w.packs[u.team]) decideFormation(w, u, D); else decideAlone(w, u, D);
}
function decideFormation(w, u, D) {
	const pack = w.packs[u.team], f = pack.f, es = foes(w, u.team);
	if (saveWounded(w, u, es, D)) return;
	kiterRetreat(w, u, es, D);   // backing off is the move this tick; the rest of the decision still runs
	if (f.surround && u.surroundGoal && u.target && u.target.alive) {
		// Encircle: move to the goal point, then attack from there (no other movement this tick).
		const T = u.target;
		if (!(MELEE[u.role] && gap(u, T) <= u.range)) goTo(D, u.surroundGoal.x, u.surroundGoal.y);
		D.keep = true;
		if (MELEE[u.role]) { D.post = true; return decMelee(w, u, T, D); }
		if (u.role === 'artillery') return decArtillery(w, u, T, D, u.x, u.y, true);
		return decDirect(w, u, T, D, u.x, u.y, 0, es);
	}
	const rel = cmdOf(w, pack, 'release');
	if ((rel && rel.has(u.id)) || (f.release && f.release.includes(u.role) && !(u.role === 'melee' && pack.flank.wings.has(u)))) {
		if (shellDodge(w, pack)) { const v = dodgeVector(w, u); if (v) { goTo(D, v.x, v.y); u.state = 'dodge'; return; } }
		return decideReleased(w, u, D, pack, es);
	}
	if (shellDodge(w, pack) && (sk(w, u.team, 'lockedDodge') || !(u.role === 'melee' && u.target && gap(u, u.target) <= u.range))) {
		const v = dodgeVector(w, u);
		if (v) {
			goTo(D, v.x, v.y); u.state = 'dodge';
			if (u.role === 'ranged') D.rel = 'dodgeFire';
			return;
		}
	}
	if (u.role === 'melee') {
		if (u.flankGoal && !u.answering) goTo(D, u.flankGoal.x, u.flankGoal.y);
		else if (u.target) decMelee(w, u, u.target, D); else goTo(D, u.slotX, u.slotY);
		return;
	}
	if (u.role === 'artillery') {
		// Scored only when ready to fire (3 s reload); while reloading it keeps its last target.
		if (u.cd > 0) return decArtillery(w, u, u.target && u.target.alive ? u.target : null, D, u.slotX, u.slotY, true);
		return decArtillery(w, u, artilleryTarget(w, u, es, f), D, u.slotX, u.slotY, true);
	}
	decDirect(w, u, shooterTarget(w, pack, u, es, false), D, u.slotX, u.slotY, f.laneLeash + f.kiteLeash, es);
}

// One unit's decision for this tick (see the unit layer above). Reflexes (dash, block) have already happened.
function decide(w, u) {
	const D = u.dec = { move: null, keep: false, rel: null, post: false, bound: false };
	u._inReach = false;
	// The pack's proposal for this tick (melee targets, the surround target).
	if (u.assigned !== undefined) u.target = u.assigned;
	const pack = w.packs[u.team];
	// Enemies an artillery attack left cut off (the planner marks them): free melee near them go for them.
	if (pack && MELEE[u.role] && pack.cutOff && pack.cutOff.until > w.t && sk(w, u.team, 'artyFollow') !== 'shooters' &&
		!(u.target && u.target.alive && gap(u, u.target) <= u.range)) {
		let b = null, bd = 200; for (const h of pack.cutOff.set) if (h.alive && dist(u, h) < bd) { bd = dist(u, h); b = h; }
		if (b) u.target = b;
	}
	if (u.guardUntil > w.t) { u.state = 'guard'; return; }   // guarding: holds still, does not attack
	if (w.shots.length && !(MELEE[u.role] && u.target && u.target.alive && gap(u, u.target) <= u.range)) {
		const sd = sk(w, u.team, 'dodgeShots');
		const v = sd !== false && !(sd === 'soft' && MELEE[u.role]) && shotDodgeVector(w, u);
		if (v) { goTo(D, v.x, v.y); u.state = 'dodge'; return; }
	}
	if (u.order && u.order.until <= w.t) { (w.orderEvents = w.orderEvents || []).push({ t: w.t, id: u.id, do: u.order.do, why: 'time is up' }); u.order = null; }
	if (u.order) return decideOrder(w, u, D);
	decideOwn(w, u, D);
}

// Act: carry out the decision. Walk to the goal; a prepared cast is released on the target (the release re-checks
// the target's reach, ARCHITECTURE.md:2709-2716), a melee swing lands only if the target is still in reach.
function walk(u, dt) { const m = u.dec.move; if (m) moveToward(u, m.x, m.y, dt * m.mul, m.stop); }
function act(w, u, dt) {
	const D = u.dec, t = u.target;
	switch (D.rel) {
		case 'melee': {
			if (D.post) walk(u, dt);
			const d = gap(u, t);
			if (!D.post) walk(u, dt);
			if (isGame(w)) {
				// A committed swing releases when its windup is done; it lands only if the target is still in reach.
				if (prepared(w, u) && u.prep > 0) { released(w, u); if (d <= u.range) { w.meleeHits.push([u, t, u.chargeBonus ? ABIL.charge.bonus : 1]); u.chargeBonus = false; } }
			} else if (d <= u.range && u.cd <= 0 && !(u.shieldUntil > w.t)) {
				u.cd = u.cdMax;
				w.meleeHits.push([u, t, u.chargeBonus ? ABIL.charge.bonus : 1]);
				u.chargeBonus = false;
			}
			return;
		}
		case 'direct': {
			walk(u, dt);
			const pk = w.packs[u.team];
			if (t && prepared(w, u) && (!isGame(w) || u.prep > 0) && gap(u, t) <= u.range && !(pk && u.fireHold) && aimClear(w, u, t)) { released(w, u); fireShot(w, u, t); }
			return;
		}
		case 'dodgeFire': {
			walk(u, dt);
			if (t && t.alive && prepared(w, u) && !u.fireHold && gap(u, t) <= u.range && aimClear(w, u, t)) { released(w, u); fireShot(w, u, t); }
			return;
		}
		case 'art': {
			if (D.post) walk(u, dt);
			if (!t) return;
			const d = dist(u, t);
			if (!D.post) walk(u, dt);
			// The pack fires volleys (artilleryVolley); under game rules a gun the planner did not use releases on its own.
			if (!isGame(w)) {
				if (w.packs[u.team] && sk(w, u.team, 'artyFire') !== 'single') return;
				if (prepared(w, u) && d <= u.range && d >= ROLE.artillery.minRange) { released(w, u); fireShell(w, u, t); }
				return;
			}
			if (u.reservedUntil > w.t) return;   // the planner fires it at its release
			// Release re-checks the target (ARCHITECTURE.md:2709-2716): its current position, or a fizzle (no refund).
			if (prepared(w, u)) {
				released(w, u);
				if (d <= u.range && d >= minR(u)) {
					// Our decision (skill lobLead): aim where the target will be when the lob lands.
					const fl = len(t.x - u.x, t.y - u.y) / lobV(u), mode = sk(w, u.team, 'lobLead');
					// Steadiness: the second-long average velocity's length over the average speed (1 = one direction).
					const steady = (t.lsp || 0) > 30 && len(t.lvx || 0, t.lvy || 0) / t.lsp > 0.8;
					const L = mode === true || (mode === 'adaptive' && steady);
					fireShellAt(w, u, t.x + (L ? t.lvx * fl : 0), t.y + (L ? t.lvy * fl : 0));
				}
			}
			return;
		}
		case 'player': return playerBrain(w, u, dt);
		default: walk(u, dt);
	}
}

// ---------------------------------------------------------------- target rules (shared by every brain)
// Shooter target by the pack's focus rule (f.shooterFocus): 'one' / 'squads' (the focus orders), 'nearest', or
// ranked: 'protect' (threats to our back line, then nearest), 'soft' (shooters first), default (threats, then
// targets our melee pin, then the rest), each tier by health left. A released shooter (acting at full speed off
// the shape) ranks only 'soft'-first. Ranked by priority first, firing lines checked only until a clear one is
// found: a blocked lane costs more than any priority gap, so this picks what checking every lane would.
function shooterTarget(w, pack, u, es, released) {
	const f = pack.f, sf = f.shooterFocus;
	if (!released) {
		const usable = (h) => h && h.alive && gap(u, h) <= u.range;
		if (u.fireOrder && usable(u.fireOrder)) return u.fireOrder;
		if (sf === 'one' && usable(pack.packFocus)) return pack.packFocus;
		if (sf === 'squads' && usable(pack.squadFocus.get(u))) return pack.squadFocus.get(u);
		if (sf === 'nearest') return nearest(u, es);
	}
	const fcOn = sk(w, pack.team, 'fireControl'), cand = [];
	for (const h of es) {
		if (gap(u, h) > u.range) continue;
		const left = h.hp - (pack.pending.get(h) || 0);
		if (left <= 0) continue;
		const eng = cmdOf(w, pack, 'engage'), off = eng && !eng.has(h.id) ? 3e6 : 0;   // a commander's engage goal first
		const tier = off + (released ? (sf === 'soft' && MELEE[h.role] ? 1e6 : 0)
			: sf === 'protect' ? (pack.threatens(h) ? 0 : 1e6 + dist(h, u) * 1e3)
			: sf === 'soft' ? (MELEE[h.role] ? 1e6 : 0) + (pack.threatens(h) ? 0 : 1e5)
			: (pack.threatens(h) ? 0 : pack.cutOff && pack.cutOff.set.has(h) ? 5e5 : pinned(h) ? 1e6 : 2e6));
		const ks = sk(w, pack.team, 'killSpeed') ? 10 / Math.max(0.1, h.dmg / Math.max(0.3, h.cdMax)) : 1;   // health left per damage per second
		cand.push([tier + (fcOn ? left / pHitLine(w, pack, h, u) : left) * ks, h]);
	}
	if (!cand.length) return nearest(u, es);
	// The first lowest key (what a stable sort puts first); sort the rest only when its lane is blocked.
	let bi = 0; for (let i = 1; i < cand.length; i++) if (cand[i][0] < cand[bi][0]) bi = i;
	if (aimClear(w, u, cand[bi][1])) return cand[bi][1];
	cand.sort((a, b) => a[0] - b[0]);
	for (const [, h] of cand) if (aimClear(w, u, h)) return h;
	return cand[0][1];
}
// Artillery target: without pack settings the nearest enemy outside the minimum range; with them (f) the
// enemy whose splash catches the most, weighted by f.artilleryDoctrine (pinned / counter / soft / cluster).
function artilleryTarget(w, u, es, f) {
	if (!f) return nearest(u, es, (e) => dist(e, u) >= minR(u)) || nearest(u, es);
	let best = null, bestScore = 0;
	const sp2 = blastR(u) * blastR(u), ad = f.artilleryDoctrine;
	for (const h of es) {
		const d = dist(h, u);
		if (d > u.range || d < minR(u)) continue;
		// Counted from current positions (units move during the tick), with squared distances.
		let n = 0; for (const o of es) { const dx = o.x - h.x, dy = o.y - h.y; if (dx * dx + dy * dy < sp2) n++; }
		const score = n * (ad === 'pinned' && pinned(h) ? f.engagedWeight : 1) *
			(ad === 'counter' && h.role === 'artillery' ? 6 : 1) * (ad === 'soft' && !MELEE[h.role] ? 3 : 1) *
			(u.w && sk(u.w, u.team, 'killSpeed') ? h.dmg / Math.max(0.3, h.cdMax) / Math.max(1, h.hp) * 100 : 1);
		if (score > bestScore) { bestScore = score; best = h; }
	}
	return best;
}

// ---------------------------------------------------------------- abilities
const KEY = { charge: 'rCharge', shield: 'rShield', aimed: 'rAimed', disengage: 'rDiseng', barrage: 'rBarrage', slow: 'rSlow' };
function ready(w, u, name) {
	if (u.abManual && !w._byHand) return false;   // a unit set to manual (hand.html): only its commander's trigger uses its abilities
	const off = w.o.abilOff && w.o.abilOff[u.team];
	if (off && off.includes(name)) return false;
	return (ROLE_ABIL[u.role] || []).includes(name) && (u[KEY[name]] ?? 0) <= w.t && (u.abLock ?? 0) <= w.t;
}
function abStat(w, team, name, field, v) {
	const a = (w.stats.abil = w.stats.abil || [{}, {}]);
	const r = (a[team][name] = a[team][name] || { uses: 0, dmg: 0, blocked: 0 });
	r[field] += v;
}
function spend(w, u, name) {
	abStat(w, u.team, name, 'uses', 1);
	u[KEY[name]] = w.t + ABIL[name].cd;
	u.abLock = w.t + ABIL.lock;
	u.abUsed = name; u.abUsedT = w.t;
}
const busy = (w, u) => u.chargeEnd > w.t || u.aimUntil > w.t || u.disEnd > w.t;
function useCharge(w, u, t) {
	if (!t || !ready(w, u, 'charge')) return false;
	const g = gap(u, t);
	if (g < ABIL.charge.min || g > ABIL.charge.max) return false;
	// (The sandbox rules' abilities, off under game rules, name their own target: the one exception to decide() writing it.)
	spend(w, u, 'charge'); u.chargeT = t; u.chargeEnd = w.t + ABIL.charge.time; u.target = t;
	return true;
}
function useShield(w, u) {
	if (!ready(w, u, 'shield')) return false;
	spend(w, u, 'shield'); u.shieldUntil = w.t + ABIL.shield.dur;
	return true;
}
function useAimed(w, u, t) {
	if (!t || !ready(w, u, 'aimed') || gap(u, t) > u.range) return false;
	spend(w, u, 'aimed'); u.aimT = t; u.aimUntil = w.t + ABIL.aimed.aim;
	return true;
}
function useDisengage(w, u, fromX, fromY) {
	if (!ready(w, u, 'disengage')) return false;
	const d = len(u.x - fromX, u.y - fromY) || 1;
	spend(w, u, 'disengage'); u.prep = 0;   // a dodge ability breaks a wind-up
	u.disX = clamp(u.x + (u.x - fromX) / d * ABIL.disengage.dist, u.r, w.o.width - u.r);
	u.disY = clamp(u.y + (u.y - fromY) / d * ABIL.disengage.dist, u.r, w.o.height - u.r);
	u.disEnd = w.t + ABIL.disengage.dist / ABIL.disengage.speed + 0.05;
	return true;
}
function useBarrage(w, u, h) {
	if (!h || !ready(w, u, 'barrage')) return false;
	const d = dist(u, h);
	if (d > u.range || d < ROLE.artillery.minRange) return false;
	spend(w, u, 'barrage'); u.cd = u.cdMax;
	const lead = ROLE.artillery.flight, [vx, vy] = vel(w, h, u.team), cx = h.x + vx * lead, cy = h.y + vy * lead;
	const px = -(h.y - u.y) / d, py = (h.x - u.x) / d, a = ABIL.barrage;
	for (let i = 0; i < a.shells; i++) {
		const off = (i - (a.shells - 1) / 2) * a.spread;
		w.shells.push({ x: cx + px * off, y: cy + py * off, t: w.t + lead + i * a.gap, src: u, dmg: u.dmg * (a.dmgMul ?? 1), splash: ROLE.artillery.splash, barrage: true });
	}
	return true;
}
function useSlow(w, u, x, y) {
	if (!ready(w, u, 'slow')) return false;
	const d = len(x - u.x, y - u.y);
	if (d > u.range || d < ROLE.artillery.minRange) return false;
	spend(w, u, 'slow');
	w.shells.push({ x, y, t: w.t + ROLE.artillery.flight, src: u, dmg: 0, splash: 0, slow: true });
	return true;
}

// An action in progress (charge, aim, disengage) owns the unit this tick.
function busyAct(w, u, dt) {
	if (u.chargeEnd > w.t) {
		const t = u.chargeT;
		if (!t || !t.alive || gap(u, t) <= u.range * 0.8) { u.chargeEnd = 0; u.chargeBonus = !!(t && t.alive); return false; }
		const dx = t.x - u.x, dy = t.y - u.y, d = len(dx, dy), step = Math.min(ABIL.charge.speed * dt, d - u.r - t.r);
		u.x += dx / d * step; u.y += dy / d * step; u.state = 'charge'; MOVES.n++; lgMoved(u);
		return true;
	}
	if (u.aimUntil > w.t) {
		// A pack that dodges breaks off the aim when a shell is about to land on the shooter.
		const p = w.packs[u.team];
		if (p && shellDodge(w, p) && dodgeVector(w, u)) { u.aimUntil = 0; u.aimT = null; return false; }
		u.state = 'aim'; return true;
	}
	if (u.aimT && u.aimUntil <= w.t) {
		// Release: the aimed target if still alive with a clear line, otherwise the healthiest enemy in
		// range with a clear line, so the burst is not wasted on a dead or blocked target.
		let t = u.aimT;
		u.aimT = null;
		if (!(t.alive && gap(u, t) <= u.range + 20 && laneClear(w, u, t))) {
			t = null;
			for (const e of team(w, 1 - u.team)) if (gap(u, e) <= u.range && laneClear(w, u, e) && (!t || e.hp > t.hp)) t = e;
		}
		if (t) { fireShot(w, u, t, u.dmg * ABIL.aimed.mult); released(w, u); }
		u.state = 'aim'; return true;
	}
	if (u.disEnd > w.t) {
		const dx = u.disX - u.x, dy = u.disY - u.y, d = len(dx, dy);
		if (d < 1) { u.disEnd = 0; return false; }
		const step = Math.min(ABIL.disengage.speed * dt, d);
		u.x += dx / d * step; u.y += dy / d * step; u.state = 'disengage'; MOVES.n++; lgMoved(u);
		return true;
	}
	return false;
}

// A commander's trigger (hand.html): the same use*() the AI's rules call, so cooldowns and the lock are shared.
// name: charge (target: an enemy, default the nearest), shield, aimed (target), disengage (away from the nearest enemy),
// barrage (target), slow (a = { x, y }). Returns whether it fired.
function triggerAbility(w, u, name, a) {
	w._byHand = true;
	try { return triggerAbilityNow(w, u, name, a); } finally { w._byHand = false; }
}
const abilityReady = (w, u, name) => { w._byHand = true; try { return ready(w, u, name); } finally { w._byHand = false; } };
function triggerAbilityNow(w, u, name, a) {
	if (!w.o.abilities || !u.alive || busy(w, u)) return false;
	const es = team(w, 1 - u.team), t = (a && a.target) || nearest(u, es);
	if (name === 'charge') return useCharge(w, u, t);
	if (name === 'shield') return useShield(w, u);
	if (name === 'aimed') return useAimed(w, u, t);
	if (name === 'disengage') return !!t && useDisengage(w, u, t.x, t.y);
	if (name === 'barrage') return useBarrage(w, u, t);
	if (name === 'slow') return useSlow(w, u, a.x, a.y);
	return false;
}
// Default (individual) use: any unit whose pack does not coordinate its abilities.
function defaultAbilities(w, u) {
	const es = team(w, 1 - u.team);
	if (!es.length) return false;
	// Each trigger is worked out only when its ability is ready: ready() has no side effects and every use*()
	// checks it first, so this skips work without changing a result.
	if (u.role === 'melee' || u.role === 'hunter') {
		if (ready(w, u, 'charge') && !es.some((e) => gap(u, e) <= u.range)) {
			const t = (u.target && u.target.alive) ? u.target : nearest(u, es);
			if (useCharge(w, u, t)) return true;
		}
		if (ready(w, u, 'shield') && w.t - (u.lastShotHitT ?? -9) < 1 && !teamMelee(w, 1 - u.team).some((e) => gap(u, e) < 40)) useShield(w, u);
		return false;
	}
	if (u.role === 'ranged' || u.role === 'archer') {
		if (!ready(w, u, 'disengage') && !ready(w, u, 'aimed')) return false;
		const m = nearest(u, teamMelee(w, 1 - u.team));
		if (m && dist(m, u) < 60 && useDisengage(w, u, m.x, m.y)) return true;
		const t = u.target && u.target.alive ? u.target : null;
		if (t && !(m && dist(m, u) < 100) && useAimed(w, u, t)) return true;
		return false;
	}
	if (u.role === 'artillery') {
		if (!ready(w, u, 'barrage') && !ready(w, u, 'slow')) return false;
		let best = null, bn = 0;
		for (const h of es) {
			const d = dist(u, h);
			if (d > u.range || d < ROLE.artillery.minRange) continue;
			let n = 0; for (const o of es) if (dist(o, h) < ROLE.artillery.splash) n++;
			if (n > bn) { bn = n; best = h; }
		}
		if (best && bn >= 3 && useBarrage(w, u, best)) return true;
		if (best && bn >= 2 && useSlow(w, u, best.x, best.y)) return true;
	}
	return false;
}

// Thresholds of our coordinated ability rules (defaults reproduce the hand-written rules; option `ab`).
const AB_DEFAULT = { chargeSync: 3, shieldAimedAt: 2, shieldShellWindow: 0.6, aimedSafe: 120, aimedWorth: 1.5,
	disengageNear: 35, barrageMin: 3, barrageHeld: 2, slowMin: 3, slowMoving: 30 };

// Thresholds tuned by es_tune.js for the RULES commander (no look-ahead): +1.06 survivors per fight on
// held-out battles (sprt.js, 64 pairs). They do not transfer to the look-ahead commander (-0.50).
const AB_TUNED_RULES = { chargeSync: 4, shieldAimedAt: 3, shieldShellWindow: 0.31, aimedSafe: 64.5, aimedWorth: 0,
	disengageNear: 23.7, barrageMin: 4, barrageHeld: 1, slowMin: 4, slowMoving: 32.8 };

// Coordinated use (our pack): plain rules, run once per tick after the formation plan.
// Side-wide ability rules run for a side whose skill says 'coordinated'; a commander's side starts at its first plan.
const coordOn = (w, p) => !!w.o.abilities && sk(w, p.team, 'abilities') === 'coordinated' && (p.brain !== 'reactive' || !!p.f.coordAbilities);
function coordAbilities(w, pack) {
	const P = w.ai[pack.team].ab;
	const ms = team(w, pack.team), es = team(w, 1 - pack.team);
	if (!es.length) return;
	const melee = ms.filter((m) => m.role === 'melee'), ranged = ms.filter((m) => m.role === 'ranged');
	const art = ms.filter((m) => m.role === 'artillery');
	// React to the aim tell (option reactAim): a targeted melee shields, a targeted shooter jumps back.
	if (sk(w, pack.team, 'reactAim')) for (const e of es) {
		if (!(e.aimUntil > w.t) || !e.aimT || e.aimT.team !== pack.team || busy(w, e.aimT)) continue;
		const v = e.aimT;
		if (v.role === 'melee') useShield(w, v); else if (v.role === 'ranged') useDisengage(w, v, e.x, e.y);
	}
	// Melee: strikers charge together; a charge to save the back line (peel, guard, answer) goes at once.
	const inBand = melee.filter((m) => !busy(w, m) && m.target && m.target.alive && !es.some((e) => gap(m, e) <= m.range) &&
		ready(w, m, 'charge') && gap(m, m.target) >= ABIL.charge.min && gap(m, m.target) <= ABIL.charge.max);
	const urgent = inBand.filter((m) => m.state === 'peel' || m.state === 'answer' || pack.threatens(m.target));
	const together = inBand.length >= Math.min(P.chargeSync, melee.length) ? inBand : urgent;
	// Intercept: an enemy charging one of our soft units is met by our nearest ready melee.
	for (const e of es) if (e.chargeEnd > w.t && e.chargeT && !MELEE[e.chargeT.role]) {
		const m = melee.filter((x) => !busy(w, x) && ready(w, x, 'charge') && gap(x, e) >= ABIL.charge.min && gap(x, e) <= ABIL.charge.max)
			.sort((p, q) => dist(p, e) - dist(q, e))[0];
		if (m) { m.target = e; useCharge(w, m, e); }
	}
	for (const m of together) useCharge(w, m, m.target);
	// Melee shield: not fighting, and either two shooters are on it or a shell is about to land on it.
	for (const m of melee) {
		if (busy(w, m) || m.shieldUntil > w.t || !ready(w, m, 'shield') || teamMelee(w, 1 - pack.team).some((e) => gap(m, e) < 50)) continue;
		const aimedAt = es.filter((e) => !MELEE[e.role] && e.target === m && dist(e, m) <= e.range).length;
		const shell = w.shells.some((sh) => sh.src.team !== pack.team && !sh.slow && sh.t - w.t < P.shieldShellWindow && len(m.x - sh.x, m.y - sh.y) < sh.splash + m.r);
		if (aimedAt >= P.shieldAimedAt || shell) useShield(w, m);
	}
	// Shooters: jump away from melee or a charge aimed at them; aimed shot only when safe and worth it.
	for (const r of ranged) {
		if (busy(w, r) || (!ready(w, r, 'disengage') && !ready(w, r, 'aimed'))) continue;
		const m = nearest(r, teamMelee(w, 1 - pack.team));
		const charger = es.find((e) => e.chargeEnd > w.t && e.chargeT === r);
		// Jump only from a charge aimed at us, or from melee on top of us that none of our melee can reach.
		const alone = m && dist(m, r) < P.disengageNear && !melee.some((x) => dist(x, m) < 60);
		if (charger || alone) { const from = charger || m; if (useDisengage(w, r, from.x, from.y)) continue; }
		const t = r.target;
		if (t && t.alive && !(m && dist(m, r) < P.aimedSafe) && t.hp - (pack.pending.get(t) || 0) > r.dmg * P.aimedWorth && laneClear(w, r, t)) useAimed(w, r, t);
	}
	// Artillery: barrage into our own slow field once it holds enemies; otherwise slow a moving cluster.
	const fields = (w.fields || []).filter((f) => f.team === pack.team && f.from <= w.t && f.until > w.t + 0.8);
	const slowPending = w.shells.some((sh) => sh.slow && sh.src.team === pack.team);
	for (const a of art) {
		if (busy(w, a)) continue;
		const rb = ready(w, a, 'barrage');
		if (!rb && !ready(w, a, 'slow')) continue;
		let done = false;
		if (rb) for (const f of fields) {
			const inside = es.filter((e) => len(e.x - f.x, e.y - f.y) <= f.r);
			if (inside.length >= 2) { const h = inside[0]; if (useBarrage(w, a, h)) { done = true; break; } }
		}
		if (done) continue;
		if (slowPending || fields.length) continue;
		// Barrage a dense cluster, or one our melee are holding in place, when no trap is being set.
		if (rb) {
			let bt = null, bv = 0;
			for (const h of es) {
				const d = dist(a, h);
				if (d > a.range || d < ROLE.artillery.minRange) continue;
				let n = 0, held = 0; for (const o of es) if (dist(o, h) < ROLE.artillery.splash) { n++; if (pinned(o)) held++; }
				const v = n + held;
				if ((n >= P.barrageMin || held >= P.barrageHeld) && v > bv) { bv = v; bt = h; }
			}
			if (bt && useBarrage(w, a, bt)) continue;
		}
		if (!ready(w, a, 'slow')) continue;
		let best = null, bn = 0;
		for (const h of es) {
			const d = dist(a, h);
			if (d > a.range || d < ROLE.artillery.minRange || len(h.vx, h.vy) < P.slowMoving) continue;
			let n = 0; for (const o of es) if (dist(o, h) < ABIL.slow.radius) n++;
			if (n > bn) { bn = n; best = h; }
		}
		if (best && bn >= P.slowMin && useSlow(w, a, best.x + vel(w, best, a.team)[0] * ROLE.artillery.flight, best.y + vel(w, best, a.team)[1] * ROLE.artillery.flight)) break;
	}
}

// ---------------------------------------------------------------- world step
// Overlapping bodies push apart. Neighbours come from a grid (cell >= the largest pair of radii), and every
// push is computed from the same positions and applied at once, so unit order favours neither side.
const SEP_CELL = 24;
function separate(w) {
	const us = w.units.filter((u) => u.alive), n = us.length, g = new Map(), px = new Float64Array(n), py = new Float64Array(n);
	for (let i = 0; i < n; i++) {
		const u = us[i], k = Math.floor(u.x / SEP_CELL) * 4096 + Math.floor(u.y / SEP_CELL);
		u._si = i; let c = g.get(k); if (!c) { c = []; g.set(k, c); } c.push(u);
	}
	for (let i = 0; i < n; i++) {
		const a = us[i], cx = Math.floor(a.x / SEP_CELL), cy = Math.floor(a.y / SEP_CELL);
		for (let ox = -1; ox <= 1; ox++) for (let oy = -1; oy <= 1; oy++) {
			const c = g.get((cx + ox) * 4096 + cy + oy); if (!c) continue;
			for (const b of c) {
				if (b._si <= i) continue;
				const dx = b.x - a.x, dy = b.y - a.y, d = len(dx, dy), m = a.r + b.r;
				if (d >= m || d === 0) continue;
				const push = (m - d) / 2, nx = dx / d * push, ny = dy / d * push;
				px[i] -= nx; py[i] -= ny; px[b._si] += nx; py[b._si] += ny;
			}
		}
	}
	for (let i = 0; i < n; i++) { const u = us[i]; u.x = clamp(u.x + px[i], u.r, w.o.width - u.r); u.y = clamp(u.y + py[i], u.r, w.o.height - u.r); lgMoved(u); }
	MOVES.n++;
}

function step(w) {
	const dt = w.o.dt;
	w.t += dt;
	for (const u of w.units) {
		if (isGame(w)) { const ldt = dt * (u.tr || 1); if (u.cd > 0) u.cd -= ldt; }
		else if (u.cd > 0) u.cd -= dt;
		else if (w.o.windUp && WINDUP[u.role]) u.prep = (u.prep || 0) + dt;
		if (u.epRegen) u.ep = Math.min(u.epMax, u.ep + u.epRegen * dt * (u.tr || 1));
		u.px0 = u.x; u.py0 = u.y; u.stepT = w.t;
	}
	if (w.o.abilities) {
		w.fields = (w.fields || []).filter((f) => f.until > w.t);
		for (const u of w.units) {
			if (!u.alive) continue;
			let mul = u.shieldUntil > w.t ? ABIL.shield.speedMul : 1;
			for (const f of w.fields) if (f.from <= w.t && f.team !== u.team && len(u.x - f.x, u.y - f.y) <= f.r) { mul *= ABIL.slow.mul; break; }
			u.speed = (isGame(w) ? u.baseSpeed * (u.tr || 1) : ROLE[u.role].speed) * mul;
		}
	}
	// A tick, in order: the packs plan and propose (a fresh random order each tick: the pack deciding second sees what
	// the first just did); reflexes; every unit decides (target, goal, state: the only writer); fire control; the rules
	// start the casts; the artillery planner releases prepared guns; every unit acts; hits land.
	const pr = rng(((w.o.seed * 2654435761) ^ (Math.round(w.t / dt) * 40503)) >>> 0 || 1);
	pr(); pr();
	const packOrder = pr() < 0.5 ? [0, 1] : [1, 0];
	for (const k of packOrder) {
		const p = w.packs[k];
		if (!p) continue;
		lookahead(w, p); directorStep(w, p); commander(w, p); formationPlan(w, p);
		if (coordOn(w, p)) coordAbilities(w, p);
	}
	w.meleeHits = [];
	const order = w.units.slice();
	const tr = rng(((w.o.seed * 73856093) ^ (Math.round(w.t / dt) * 19349663)) >>> 0 || 1);
	tr(); tr();
	for (let i = order.length - 1; i > 0; i--) { const j = Math.floor(tr() * (i + 1)); [order[i], order[j]] = [order[j], order[i]]; }
	for (const u of order) {
		if (u.dodgeProf && w.shots.length) gameDash(w, u);
		if (u.block && w.shots.length) gameBlock(w, u);
	}
	for (const u of order) decide(w, u);
	if (isGame(w)) {
		for (const u of order) u.castOk = castPermit(w, u);
		for (const u of w.units) gamePrep(w, u, dt * (u.tr || 1));
	}
	for (const k of packOrder) if (w.packs[k]) artilleryVolley(w, w.packs[k]);
	for (const u of order) {
		if (!u.alive) continue;
		if (w.o.abilities) {
			if (busyAct(w, u, dt)) continue;
			const p = w.packs[u.team];
			if (!(p && coordOn(w, p)) && sk(w, u.team, 'abilities') !== 'off' && defaultAbilities(w, u) && busy(w, u)) continue;
		}
		act(w, u, dt);
	}
	for (const [src, dst, mult] of w.meleeHits) damage(w, src, dst, src.dmg * (mult || 1));
	const grid = w.shots.length ? buildGrid(w) : null;
	for (const s of w.shots) {
		if (s.aimed) {
			const stepLen = Math.min(s.speed * dt, s.left), ex = s.x + s.dx * stepLen, ey = s.y + s.dy * stepLen;
			const settle = (hitTarget) => {
				s.done = true; if (s.target) addPending(w, s.src, s.target, -s.pend);
				const pk = w.packs[s.src.team];
				if (pk && s.dodgeable) pk.hitRate = (pk.hitRate ?? 0.3) * 0.97 + (hitTarget ? 0.03 : 0);
			};
			// The first body this step's segment crosses.
			let hitU = null, ht = Infinity;
			const x0 = Math.floor((Math.min(s.x, ex) - 12) / GRID), x1 = Math.floor((Math.max(s.x, ex) + 12) / GRID);
			const y0 = Math.floor((Math.min(s.y, ey) - 12) / GRID), y1 = Math.floor((Math.max(s.y, ey) + 12) / GRID);
			for (let cx = x0; cx <= x1; cx++) for (let cy = y0; cy <= y1; cy++) {
				const c = grid.get(cx * 4096 + cy); if (!c) continue;
				for (const u of c) {
					if (u === s.src || !u.alive || (s.hitSet && s.hitSet.has(u))) continue;
					const px = u.x - s.x, py = u.y - s.y, a = Math.max(0, Math.min(stepLen, px * s.dx + py * s.dy));
					if (len(px - s.dx * a, py - s.dy * a) <= u.r && (a < ht || (a === ht && u._i < hitU._i))) { ht = a; hitU = u; }
				}
			}
			// Where shot damage goes, per side: intended target, other enemy, overkill, a friend, a miss.
			const so = ((w.stats.shotOut = w.stats.shotOut || [{}, {}])[s.src.team]), put = (k, v) => { k += s.dodgeable === false ? '/sure' : ''; so[k] = (so[k] || 0) + v; };
			if (hitU && s.pierce > 0 && hitU.team !== s.src.team) {
				// A piercing shot damages the body and flies on (fire_lance pierce 2).
				(s.hitSet = s.hitSet || new Set()).add(hitU); s.pierce--;
				const hp = hitU.hp; damage(w, s.src, hitU, s.dmg); put(hitU === s.target ? 'target' : 'other', Math.min(s.dmg, hp));
				s.x = ex; s.y = ey; s.left -= stepLen; if (s.left <= 0) settle(false);
				continue;
			}
			if (hitU) {
				if (hitU.team !== s.src.team) {
					const hp = hitU.hp; damage(w, s.src, hitU, s.dmg);
					put(hitU === s.target ? 'target' : 'other', Math.min(s.dmg, hp)); put('overkill', Math.max(0, s.dmg - hp));
				} else { if (s.src.team === 0) w.stats.wasted += s.dmg; put('friend', s.dmg); if (isGame(w)) damage(w, s.src, hitU, s.dmg); }
				settle(hitU === s.target); continue;
			}
			s.x = ex; s.y = ey; s.left -= stepLen;
			if (s.left <= 0) { if (s.src.team === 0) w.stats.wasted += s.dmg; put(s.target && !s.target.alive ? 'missDead' : 'miss', s.dmg); settle(false); }
			continue;
		}
		const t = s.target, dx = t.x - s.x, dy = t.y - s.y, d = len(dx, dy), stepLen = s.speed * dt;
		const settle = () => { s.done = true; addPending(w, s.src, t, -s.dmg); };
		const blocker = lineBlockerGrid(w, grid, s.x, s.y, t, s.src);
		if (blocker && dist(blocker, s) <= stepLen + blocker.r) {
			if (blocker.team !== s.src.team) damage(w, s.src, blocker, s.dmg); else if (s.src.team === 0) w.stats.wasted += s.dmg;
			settle(); continue;
		}
		if (d <= stepLen + t.r) {
			if (t.alive) damage(w, s.src, t, s.dmg); else if (s.src.team === 0) w.stats.wasted += s.dmg;
			settle(); continue;
		}
		s.x += dx / d * stepLen; s.y += dy / d * stepLen;
	}
	w.shots = w.shots.filter((s) => !s.done);
	for (const s of w.shells) {
		if (w.t < s.t) continue;
		if (s.slow) {
			w.fields = w.fields || [];
			w.fields.push({ x: s.x, y: s.y, r: ABIL.slow.radius, from: w.t, until: w.t + ABIL.slow.dur, team: s.src.team });
			s.done = true; continue;
		}
		let hit = false;
		w._barrage = !!s.barrage; w._atk = s.atk; w._shellAge = s.t - (s.born ?? s.t);
		const so = ((w.stats.shellOut = w.stats.shellOut || [{}, {}])[s.src.team]);
		if (s.pred !== undefined) { so.planShells = (so.planShells || 0) + 1; so.planPred = (so.planPred || 0) + s.pred; }
		const st = s.atk && ((w.stats.atk = w.stats.atk || [{}, {}])[s.src.team][s.atk] = w.stats.atk[s.src.team][s.atk] || { used: 0, shells: 0, dmg: 0, kills: 0 });
		if (st) st.shells++;
		for (const h of (s.lob ? w.units.filter((x) => x.alive && x !== s.src) : team(w, 1 - s.src.team))) if (len(h.x - s.x, h.y - s.y) <= s.splash + h.r) {
			if (st) { if (h.team !== s.src.team) { st.dmg += Math.min(s.dmg, h.hp); if (s.dmg >= h.hp) st.kills++; } else st.own = (st.own || 0) + Math.min(s.dmg, h.hp); }
			if (!s.barrage) { so.hits = (so.hits || 0) + 1; so.dmg = (so.dmg || 0) + Math.min(s.dmg, h.hp); if (s.pred !== undefined) so.planDmg = (so.planDmg || 0) + Math.min(s.dmg, h.hp); }
			damage(w, s.src, h, s.dmg); hit = true;
		}
		w._barrage = false; w._atk = null;
		if (!hit && s.src.team === 0) w.stats.wasted += s.dmg;
		s.done = true;
	}
	w.shells = w.shells.filter((s) => !s.done);
	w.hitLog = w.hitLog.filter((h) => w.t - h.t < 3);
	separate(w);
	const smooth = Math.min(1, dt / 0.3);
	for (const u of w.units) if (u.stepT === w.t) {
		u.vx = (u.x - u.px0) / dt; u.vy = (u.y - u.py0) / dt; u.svx += (u.vx - u.svx) * smooth; u.svy += (u.vy - u.svy) * smooth;
		// Over about a second: the average velocity and the average speed (steady movement keeps them equal).
		const k1 = Math.min(1, dt / 1.0); u.lvx = (u.lvx || 0) + (u.vx - (u.lvx || 0)) * k1; u.lvy = (u.lvy || 0) + (u.vy - (u.lvy || 0)) * k1;
		u.lsp = (u.lsp || 0) + (len(u.vx, u.vy) - (u.lsp || 0)) * k1;
	}
	w.units = w.units.filter((u) => u.alive);
	for (const k of [0, 1]) { const p = w.packs[k]; if (p) for (const [x] of p.pending) if (!x.alive) p.pending.delete(x); }
	w.stats.aliveSeconds += monsters(w).length * dt;
	for (const q of w.spawnQueue) if (!q.done && w.t >= q.at) { spawnHunter(w, q.role); q.done = true; }
	if (w.skirmish) while (w.skirmish.left > 0 && team(w, 0).length < w.skirmish.maxAlive) skirmishSpawn(w);
	// Burn ticks: raw (already mitigated at application), whole health points as they accumulate.
	if (w.dots && w.dots.length) {
		w._burnTick = true;
		for (const d of w.dots) if (d.target.alive && d.until > w.t) {
			d.acc += d.dps * dt;
			if (d.acc >= 1) { const a = Math.floor(d.acc); d.acc -= a; const p = d.target.prot; d.target.prot = 0; damage(w, d.src, d.target, a); d.target.prot = p; }
		}
		w._burnTick = false;
		w.dots = w.dots.filter((d) => d.target.alive && d.until > w.t);
	}
	w.spawnQueue = w.spawnQueue.filter((q) => !q.done);
}

// Fork: an independent copy of the world, for look-ahead and the artillery outcome check. Everything a step changes
// in place is copied and every reference to a unit is remapped to its copy, so playing a copy never touches the real
// battle. Shared on purpose, because nothing changes them in place: w.o's settings, w.ai (the profiles), the
// pack's base settings and shape cache, a unit's dodge / block profile.
function fork(w, extraOpts) {
	const map = new Map();
	const o = Object.assign({}, w.o, extraOpts || {});
	const c = { mode: w.mode, o, rand: cloneRng(w.rand), t: w.t, units: [], shots: [], shells: [], nextId: w.nextId,
		spawnQueue: w.spawnQueue.map((q) => Object.assign({}, q)), events: [], meleeHits: [], stats: { melee: 0, ranged: 0, artillery: 0, wasted: 0, monsterDeaths: 0, hunterKills: 0, aliveSeconds: 0, enemyDamage: 0, abil: [{}, {}] },   // telemetry only: no decision reads it
		packs: {}, ai: w.ai, hitLog: w.hitLog.map((h) => Object.assign({}, h)), lastHitT: w.lastHitT, unitVer: 0, _tv: -1,
		kinds: w.kinds, timeRef: w.timeRef, skirmish: w.skirmish && Object.assign({}, w.skirmish, { spawnRand: cloneRng(w.skirmish.spawnRand) }) };
	for (const u of w.units) { const v = Object.assign({}, u); v.w = c; map.set(u, v); c.units.push(v); }
	const R = (u) => (u && map.get(u)) || null;
	for (const v of c.units) {
		v.target = R(v.target); v.meleeAttacker = R(v.meleeAttacker); v.chargeT = R(v.chargeT); v.aimT = R(v.aimT); v.fireOrder = R(v.fireOrder);
		if (v.assigned) v.assigned = R(v.assigned);
		// State a copy changes in place gets its own copy (the player's limbs and manual cast, the shots a unit has
		// rolled a dash against, the decision), so a copy never changes the real battle.
		if (v.limbs) v.limbs = v.limbs.map((l) => Object.assign({}, l, { target: R(l.target) }));
		if (v.manual) v.manual = Object.assign({}, v.manual, { target: R(v.manual.target) });
		if (v.flankGoal) v.flankGoal = Object.assign({}, v.flankGoal);
		if (v.dec) v.dec = Object.assign({}, v.dec, { move: v.dec.move && Object.assign({}, v.dec.move) });
		if (v.order) v.order = Object.assign({}, v.order);
	}
	c.fields = (w.fields || []).map((f) => Object.assign({}, f));
	const smap = new Map();
	for (const s of w.shots) if ((s.aimed || map.has(s.target)) && map.has(s.src)) {
		const t = Object.assign({}, s, { target: R(s.target), src: R(s.src) });
		if (s.hitSet) t.hitSet = new Set([...s.hitSet].map(R).filter(Boolean));
		c.shots.push(t); smap.set(s, t);
	}
	for (const v of c.units) if (v._rolled) v._rolled = new Set([...v._rolled].map((s) => smap.get(s)).filter(Boolean));
	for (const s of w.shells) if (map.has(s.src)) c.shells.push(Object.assign({}, s, { src: R(s.src) }));
	if (w.dots) c.dots = w.dots.filter((d) => map.has(d.target) && map.has(d.src)).map((d) => Object.assign({}, d, { target: R(d.target), src: R(d.src) }));
	for (const k of [0, 1]) {
		const p = w.packs[k];
		if (!p) continue;
		const q = Object.assign({}, p, { anchor: Object.assign({}, p.anchor), f: Object.assign({}, p.f), base: p.base,
			pending: new Map([...p.pending].filter(([u]) => map.has(u)).map(([u, d]) => [R(u), d])),
			flank: Object.assign({}, p.flank, { wings: new Map([...p.flank.wings].filter(([u]) => map.has(u)).map(([u, sd]) => [R(u), sd])) }),
			packFocus: R(p.packFocus), squadFocus: new Map(), surroundTarget: R(p.surroundTarget),
			dir: p.dir && Object.assign({}, p.dir, { goals: Object.assign({}, p.dir.goals), cool: Object.assign({}, p.dir.cool), stats: Object.assign({}, p.dir.stats), log: p.dir.log.slice(),
				active: p.dir.active && Object.assign({}, p.dir.active, { roles: new Map([...p.dir.active.roles].filter(([u]) => map.has(u)).map(([u, r]) => [R(u), r])) }) }),
			// Rebuilt by the pack's next formationPlan before any use; until then they must not point into the real world.
			inZone: () => false, threatens: () => false,
			artyQueue: (p.artyQueue || []).filter((q) => map.has(q.u)).map((q) => Object.assign({}, q, { u: R(q.u) })),
			cutOff: p.cutOff ? { set: new Set([...p.cutOff.set].filter((h) => map.has(h)).map(R)), until: p.cutOff.until } : null,
			cmd: p.cmd ? Object.fromEntries(Object.entries(p.cmd).map(([k, v]) => [k, v && Object.assign({}, v)])) : p.cmd });
		c.packs[k] = q;
	}
	c.anchor = c.packs[0] ? c.packs[0].anchor : null;
	return c;
}

// Situation features for the plan-imitation network (our pack's view, roughly 0..1 each).
function bcFeatures(w, pack, plans) {
	const ours = team(w, pack.team), es = foes(w, pack.team), A = pack.anchor;
	const roles = ['melee', 'ranged', 'artillery'], f = [];
	const cnt = (l, r) => l.filter((u) => u.role === r || (r === 'melee' && u.role === 'hunter') || (r === 'ranged' && u.role === 'archer'));
	for (const l of [ours, es]) for (const r of roles) {
		const g = cnt(l, r);
		f.push(g.length / 30, g.length ? g.reduce((a, u) => a + u.hp / u.maxhp, 0) / g.length : 0);
	}
	const c = (l) => { let x = 0, y = 0; for (const u of l) { x += u.x; y += u.y; } return l.length ? { x: x / l.length, y: y / l.length } : A; };
	const oc = c(ours), ec = c(es);
	const spread = (l, cc) => l.length ? l.reduce((a, u) => a + dist(u, cc), 0) / l.length : 0;
	let near = Infinity; for (const m of ours) for (const e of es) near = Math.min(near, dist(m, e));
	let vx = 0, vy = 0; for (const e of es) { vx += e.vx; vy += e.vy; } vx /= Math.max(1, es.length); vy /= Math.max(1, es.length);
	const dd = dist(oc, ec) || 1, approach = (vx * (oc.x - ec.x) + vy * (oc.y - ec.y)) / dd;
	f.push(Math.min(near, 1000) / 1000, Math.min(dd, 1400) / 1400, spread(es, ec) / 300, spread(ours, oc) / 300, approach / 80);
	const ourInRange = ours.filter((m) => m.role !== 'melee' && es.some((e) => dist(e, m) <= m.range)).length;
	const theirInRange = es.filter((e) => !MELEE[e.role] && ours.some((m) => dist(e, m) <= e.range)).length;
	f.push(ourInRange / 30, theirInRange / 30);
	const rd = (l, k) => l.length ? l.filter((u) => (u[k] ?? 0) <= w.t).length / l.length : 0;
	const em = es.filter((u) => MELEE[u.role]), om = ours.filter((u) => u.role === 'melee');
	const ea = es.filter((u) => u.role === 'artillery'), oa = ours.filter((u) => u.role === 'artillery');
	f.push(rd(em, 'rCharge'), rd(om, 'rCharge'), rd(ea, 'rBarrage'), rd(oa, 'rBarrage'), rd(ea, 'rSlow'), rd(oa, 'rSlow'));
	const r = pack.read || {};
	f.push((r.meleeCharging || 0) / 10, (r.raiders || 0) / 10, (r.fastShooters || 0) / 30, r.exposed ? 1 : 0, r.formedEnemy ? 1 : 0,
		Math.min(r.quiet || 0, 10) / 10, Math.min(w.t, 150) / 150, Math.max(0, Math.min(r.room || 0, 1200)) / 1200);
	// The current plan; for a mixed combination its position tactic, which carries most of a plan's identity.
	const look = pack.lookPlan ? comboOf(pack.lookPlan).position : null;
	for (const p of plans) f.push(look === p ? 1 : 0);
	return f;
}
// Tiny MLP forward pass: the k plan indices with the highest scores (best first).
function bcTop(net, x, k) {
	const h = net.W1.map((row, j) => Math.max(0, row.reduce((a, wv, i) => a + wv * x[i], net.b1[j])));
	const sc = net.W2.map((row, q) => row.reduce((a, wv, j) => a + wv * h[j], net.b2[q]));
	return sc.map((v, i) => [v, i]).sort((a, b) => b[0] - a[0]).slice(0, k).map(([, i]) => i);
}
// Tiny MLP forward pass (weights from bc_train.js): returns the index of the highest score.
function bcPredict(net, x) {
	const h = net.W1.map((row, j) => Math.max(0, row.reduce((a, wv, i) => a + wv * x[i], net.b1[j])));
	let best = 0, bv = -Infinity;
	net.W2.forEach((row, k) => { const v = row.reduce((a, wv, j) => a + wv * h[j], net.b2[k]); if (v > bv) { bv = v; best = k; } });
	return best;
}

// Look-ahead commander (test): every `every` s, fork the fight once per candidate plan, play it
// `horizon` s with that plan forced, and keep the plan with the best damage trade.
const FINISH_PLANS = ['advance', 'hunt', 'push', 'surround', 'engage', 'rush', 'flank'];
function lookahead(w, pack) {
	let la = w.ai[pack.team].lookahead;
	const me = pack.team, them = 1 - me;
	if (!la || (w.forked && !(w.thinkTeams && w.thinkTeams.includes(pack.team)))) return;   // thinkTeams: sides that keep thinking in a copy (aar.js)
	// Replan every la.every s; after a decision that kept the same plan, wait la.everyStable s (if set) instead.
	if (w.t - (pack.lastLook ?? -99) < (pack.lookStable && la.everyStable ? la.everyStable : la.every)) return;
	pack.lastLook = w.t;
	const lookName = pack.lookPlan ? comboName(comboOf(pack.lookPlan)) : null;
	let candidates = la.plans;
	// Finishing: a 2 s horizon never sees the kill that closing in buys, so only closing plans compete.
	if (finishing(w, me)) candidates = FINISH_PLANS.filter((p) => PLANS[p]);
	else if (la.net && la.netPrune) {
		candidates = bcTop(la.net, bcFeatures(w, pack, la.plans), la.netPrune).map((i) => la.plans[i]);
		if (la.extra) candidates = [...new Set([...candidates, ...la.extra])];   // plans the network does not know, always tried
		if (pack.lookPlan && !la.mind && !candidates.includes(pack.lookPlan)) candidates.push(pack.lookPlan);
	}
	// Before contact there is nothing to choose between: the rules commander handles the approach.
	if (la.contact) {
		const ours = team(w, me), es = team(w, them);
		let near = Infinity;
		for (const m of ours) for (const e of es) { const d = dist(m, e); if (d < near) near = d; }
		if (near > la.contact) { pack.lookPlan = null; return; }
	}
	const hp = (list) => list.reduce((a, u) => a + Math.max(0, u.hp), 0);
	// Play one combination la.horizon s ahead against one enemy model: 'oracle' keeps their real brain (upper
	// bound only); 'continue' freezes whatever they are doing now; 'rush' releases every enemy unit at full speed;
	// 'rules' lets their commander re-plan by its rules (a smart reply; their look-ahead does not run in copies).
	const playout = (plan, model) => {
		const c = fork(w, { forcePlan: plan, forceTeam: me, duration: w.t + la.horizon, dt: la.dt || w.o.dt });
		c.forked = true;
		const p0 = c.packs[me];
		p0.plan = null; p0.planSince = -99; p0.lastThink = -1;
		const e = c.packs[them];
		if (e && model === 'rules') { e.lookPlan = null; e.lastThink = -1; }   // their own commander re-plans by its rules
		else if (e && model !== 'oracle') {
			e.brain = 'formation';                       // no commander in the copy: no knowledge of their rules
			if (model === 'rush') e.f = Object.assign({}, e.f, { release: ['melee', 'ranged', 'artillery'], raidTarget: 'soft' });
		}
		const our0 = hp(team(c, me)), their0 = hp(team(c, them)), ourN = team(c, me).length, theirN = team(c, them).length;
		while (!done(c)) step(c);
		const r = { dOur: our0 - hp(team(c, me)), dTheir: their0 - hp(team(c, them)), kOur: ourN - team(c, me).length, kTheir: theirN - team(c, them).length };
		// Shells still in the air count at their expected damage (the planner's prediction, or the average hit).
		r.flyOur = 0; r.flyTheir = 0;
		for (const s of c.shells) if (!s.slow) { const x = s.pred ?? s.dmg * 0.76; if (s.src.team === me) r.flyTheir += x; else r.flyOur += x; }
		// Position at the end (la.terminal s): the damage per second each side can deal from where it stands
		// (a unit with an enemy in its reach — artillery outside its minimum range), counted for la.terminal more
		// seconds. Rewards ending where we can hit and they cannot, which a short horizon never sees.
		if (la.terminal) { r.posOur = la.terminal * reachRate(c, me); r.posTheir = la.terminal * reachRate(c, them); }
		return r;
	};
	const models = la.models || ['oracle'];
	// The mind's value of one playout. objective 'deaths' (gauntlet with healing): a death costs 100 health
	// points' worth and lost health only 0.3 of its worth, since the wounded are healed before the next fight.
	const value = (r) => {
		const hw = la.objective === 'deaths' ? 0.3 : 1, dw = la.objective === 'deaths' ? 100 : 0;
		return r.dTheir + r.flyTheir + dw * r.kTheir - la.k * (hw * (r.dOur + r.flyOur) + dw * r.kOur);
	};
	// Urgency (la.urgency { from, kMin }): a fight not won by the time limit counts as lost, so after `from` of the
	// time limit has passed our losses weigh less and less, down to kMin x la.k at the limit — trades that close
	// the fight become worth it.
	const frac = w.t / w.o.duration, U = la.urgency;
	const k = U && frac > U.from ? la.k * Math.max(U.kMin, 1 - (1 - U.kMin) * (frac - U.from) / (1 - U.from)) : la.k;
	if (U) la = Object.assign({}, la, { k });
	// Stall breaker (la.stall s): when the enemy has lost no health for that long, our losses weigh a third and
	// what we deal counts double, so plans that close the fight win the comparison.
	if (la.stall) {
		const last = w.hitLog.reduce((t, h) => (h.from === me && h.amt > 0 ? Math.max(t, h.t) : t), pack.lastProgress ?? 0);
		pack.lastProgress = last;
		if (w.t - last > la.stall) la = Object.assign({}, la, { k: la.k / 3, stalled: true });
	}
	const pos = (r) => (la.terminal ? r.posOur - la.k * r.posTheir : 0);
	let best = null, bestScore = -Infinity;
	if (!la.mind) {
		// Plans only, each scored by its worst case over the enemy models.
		for (const plan of candidates) {
			let score = Infinity;
			for (const model of models) { const r = playout(plan, model); score = Math.min(score, la.objective ? value(r) : (la.stalled ? 2 : 1) * r.dTheir - la.k * r.dOur) + pos(r); }
			const sticky = plan === pack.lookPlan ? la.inertia : 0;
			if (score + sticky > bestScore) { bestScore = score + sticky; best = plan; }
		}
	} else {
		// The mind. Screen against the first enemy model: the current combination and the shortlisted plans, then
		// one role at a time every distinct tactic of that role with the others held, keeping what is better
		// (la.budget combinations; the role order rotates every decision and the best carries over, so the search
		// keeps improving across decisions). Then the la.robustTop best are also played against the other enemy
		// models and ranked by la.blend x the worst + the rest x the mean.
		const T = tacticsOf(BRAINS[pack.brain] && BRAINS[pack.brain].plans || PLANS), screen = new Map(), combos = new Map();
		let budget = la.budget || 8;
		const sticky = (key) => (key === lookName ? la.inertia : 0);
		const screenScore = (combo) => {
			const key = comboName(combo);
			if (!screen.has(key)) {
				if (budget-- <= 0) return -Infinity;
				const r = playout(combo, models[0]); screen.set(key, value(r) + pos(r)); combos.set(key, combo);
			}
			return screen.get(key) + sticky(key);
		};
		const seeds = [...(pack.lookPlan ? [comboOf(pack.lookPlan)] : pack.combo ? [pack.combo] : []), ...candidates.map(comboOf)];
		for (const c of seeds) { const v = screenScore(c); if (v > bestScore) { bestScore = v; best = c; } }
		const roles = ['artillery', 'ranged', 'melee', 'position'], turn = (pack.mindTurn = ((pack.mindTurn || 0) + 1) % 4);
		for (let i = 0; i < 4; i++) {
			const role = roles[(turn + i) % 4];
			for (const t of distinctTactics(T, role)) {
				if (!best || t === best[role] || budget <= 0) continue;
				// A role tweak must beat the best so far by la.tweakMargin: mixes that only look better over the
				// short horizon against a frozen enemy are what a smart enemy punishes.
				const c = Object.assign({}, best, { [role]: t }), v = screenScore(c);
				if (v > bestScore + (la.tweakMargin || 0)) { bestScore = v; best = c; }
			}
		}
		if (models.length > 1) {
			const top = [...screen.keys()].sort((a, b) => screen.get(b) + sticky(b) - screen.get(a) - sticky(a)).slice(0, la.robustTop || 2);
			bestScore = -Infinity;
			for (const key of top) {
				const vs = [screen.get(key), ...models.slice(1).map((m) => { const r = playout(combos.get(key), m); return value(r) + pos(r); })];
				const v = (la.blend ?? 1) * Math.min(...vs) + (1 - (la.blend ?? 1)) * vs.reduce((a, b) => a + b, 0) / vs.length + sticky(key);
				if (v > bestScore) { bestScore = v; best = combos.get(key); }
			}
		}
		if (best) best = comboName(best) === lookName ? comboOf(pack.lookPlan) : best;
	}
	if (w.o.bcRecord && !la.mind) (w.bcData = w.bcData || []).push([bcFeatures(w, pack, la.plans), la.plans.indexOf(best)]);
	const bestName = best ? comboName(comboOf(best)) : null;
	if (bestName !== lookName) note(w, `look-ahead picks ${bestName}`, me);
	pack.lookStable = bestName === lookName;
	pack.lookPlan = best;
}
// Damage per second side t can deal right now: every unit with an enemy in its reach (artillery: outside its
// minimum range), its damage over its cooldown.
function reachRate(w, t) {
	const es = team(w, 1 - t);
	let r = 0;
	for (const u of team(w, t)) {
		const lo = u.role === 'artillery' ? minR(u) : 0;
		for (const e of es) { const d = u.role === 'artillery' ? dist(u, e) : gap(u, e); if (d <= u.range && d >= lo) { r += u.dmg / u.cdMax; break; } }
	}
	return r;
}
// One representative name per distinct tactic of a role (plans often share a role's settings).
const distinctCache = new Map();
function distinctTactics(T, role) {
	const key = T[role];
	if (distinctCache.has(key)) return distinctCache.get(key);
	const seen = new Map();
	for (const [name, t] of Object.entries(T[role])) { const k = JSON.stringify(t); if (!seen.has(k)) seen.set(k, name); }
	const out = [...seen.values()];
	distinctCache.set(key, out);
	return out;
}

function done(w) {
	if (w.skirmish) return w.t >= w.o.duration || !hunters(w).length || (!monsters(w).length && w.skirmish.left <= 0);
	return w.t >= w.o.duration || !monsters(w).length || (w.o.scenario === 'mirror' && !hunters(w).length);
}

function summary(w) {
	const s = w.stats;
	return { mode: w.mode, melee: s.melee, ranged: s.ranged, artillery: s.artillery, total: s.melee + s.ranged + s.artillery,
		wasted: s.wasted, monsterDeaths: s.monsterDeaths, hunterKills: s.hunterKills, aliveSeconds: s.aliveSeconds,
		enemyDamage: s.enemyDamage, survivors: monsters(w).length, enemySurvivors: hunters(w).length, t: w.t };
}

function run(mode, options) {
	const w = create(mode, options);
	while (!done(w)) step(w);
	return summary(w);
}

// ---------------------------------------------------------------- combos
// Lure -> cross the T -> envelop (PLAN_TACTICAL_COMBOS.md, chain 2 -> 1 -> 3). Against a column that chases: give
// ground so its melee string out ahead of its shooters, stop with the shooters across its head, then release the side
// shooters onto its flanks. Roles come from position and kind, not names: the wings are the shooters furthest off
// the column's line. NOT ADOPTED (README, "Chain 2 -> 1 -> 3"): off by default, kept as the engine's worked example.
{
	const headDist = (c) => { let d = Infinity; for (const e of c.units.theirs) if (MELEE[e.role]) d = Math.min(d, dist(e, c.pack.anchor)); return d; };
	const lateral = (c, u) => Math.abs((u.x - c.obs.ec.x) * -c.obs.column.axis.y + (u.y - c.obs.ec.y) * c.obs.column.axis.x);
	COMBOS.tchain = { name: 'tchain', priority: 1, cooldown: 8,
		enter(c) {
			const o = c.obs, W = c.w.o.width, H = c.w.o.height;
			if (o.finishing || o.theirsByRole[0] < 6 || o.oursByRole[1] < 10 || o.column.ratio < 2.2 || o.approach < 15 || o.chaseShare < 0.5 || o.gapNear < 250 || o.gapNear > 700) return null;
			const ax = o.oc.x - o.ec.x, ay = o.oc.y - o.ec.y, l = len(ax, ay) || 1, away = { x: ax / l, y: ay / l };
			// Room behind us along the lure, to give ground 300 px without the wall.
			const tx = o.oc.x + away.x * 300, ty = o.oc.y + away.y * 300;
			if (tx < 100 || tx > W - 100 || ty < 100 || ty > H - 100) return null;
			return { away, ratio0: o.column.ratio, startMelee: o.theirsByRole[0] };
		},
		roles(c) {
			const sh = c.units.ours.filter((u) => u.role === 'ranged').sort((a, b) => lateral(c, b) - lateral(c, a));
			return { wing: sh.slice(0, Math.floor(sh.length / 2)), core: sh.slice(Math.floor(sh.length / 2)), screen: c.units.ours.filter((u) => u.role === 'melee') };
		},
		phases: [
			{ name: 'lure', min: 1.5, max: 8,
				goals(c) { const A = c.pack.anchor, a = c.choices.away; return { place: { x: clamp(A.x + a.x * 200, 100, c.w.o.width - 100), y: clamp(A.y + a.y * 200, 100, c.w.o.height - 100), face: [c.obs.ec.x, c.obs.ec.y] } }; },
				abort: (c) => c.obs.wallDist < 110 || c.obs.theirs < 3,
				done: (c) => headDist(c) < 300 || c.obs.column.ratio > 1.25 * c.choices.ratio0 },
			{ name: 'cross', min: 1, max: 6,
				goals(c) { const A = c.pack.anchor; return { place: { x: A.x, y: A.y, face: [c.obs.ec.x, c.obs.ec.y] }, plan: 'widehold' }; },
				done: (c) => headDist(c) < 130 || c.w.t - c.tp > 4 },
			{ name: 'envelop', min: 2, max: 8,
				goals(c) {
					const wings = [...c.roles].filter(([, r]) => r === 'wing').map(([u]) => u);
					const melee = c.units.theirs.filter((e) => MELEE[e.role]).sort((a, b) => dist(a, c.pack.anchor) - dist(b, c.pack.anchor)).slice(0, 8);
					return { release: c.ids(wings), engage: c.ids(melee) };
				},
				done: (c) => c.units.theirs.filter((e) => MELEE[e.role]).length === 0 || c.w.t - c.tp > 6 }],
		success: (c) => c.units.theirs.filter((e) => MELEE[e.role]).length <= 0.5 * c.choices.startMelee,
	};
}

// Fix, then lob the clump (PLAN_TACTICAL_COMBOS.md, combo 4): our melee hold theirs in contact and the anchor gives a
// little ground so they compress; the guns then have a dense spot at least a blast away from our own units.
// Needs artillery. Entry: their melee in contact with ours, a clump of 4+ of theirs inside one blast, none of ours near it.
{
	const clump = (c) => {
		const guns = c.units.ours.filter((u) => u.role === 'artillery');
		if (guns.length < 3) return null;
		const sp = blastR(guns[0]), E = c.units.theirs, mine = c.units.ours;
		let best = null;
		for (const e of E) {
			let n = 0; for (const o of E) if (dist(o, e) < sp) n++;
			if (n >= 4 && (!best || n > best.n) && !mine.some((m) => dist(m, e) < sp + 50) && guns.some((g) => dist(g, e) <= g.range && dist(g, e) >= minR(g))) best = { n, x: e.x, y: e.y };
		}
		return best;
	};
	COMBOS.fixlob = { name: 'fixlob', priority: 1, cooldown: 6,
		enter(c) {
			const o = c.obs, mine = c.units.ours.filter((u) => u.role === 'melee'), em = c.units.theirs.filter((e) => MELEE[e.role]);
			if (o.finishing || mine.length < 6 || em.length < 6) return null;
			const contact = em.filter((e) => mine.some((m) => gap(m, e) < 30)).length;
			if (contact < 5) return null;
			const k = clump(c);
			return k ? { startTheirs: o.theirs, clump: k.n } : null;
		},
		roles: (c) => ({ guns: c.units.ours.filter((u) => u.role === 'artillery'), fixers: c.units.ours.filter((u) => u.role === 'melee') }),
		phases: [{ name: 'fix', min: 1, max: 5,
				goals(c) { const A = c.pack.anchor, a = c.obs.oc, e = c.obs.ec, l = len(a.x - e.x, a.y - e.y) || 1; return { place: { x: clamp(A.x + (a.x - e.x) / l * 50, 100, c.w.o.width - 100), y: clamp(A.y + (a.y - e.y) / l * 50, 100, c.w.o.height - 100), face: [e.x, e.y] } }; },
				done: (c) => !!clump(c) },
			{ name: 'lob', min: 2, max: 5, goals(c) { const A = c.pack.anchor; return { place: { x: A.x, y: A.y, face: [c.obs.ec.x, c.obs.ec.y] } }; }, done: (c) => c.w.t - c.tp > 3 }],
		success: (c) => c.obs.theirs <= c.choices.startTheirs - 3,
	};
}

const api = { triggerAbility, ready: abilityReady, COMBOS, observe, GAME, SKILLS, LEVELS, setNet, buildProfile, AB_DEFAULT, AB_TUNED_RULES, ABIL, ROLE_ABIL, DEFAULTS, DEFAULT_F, LOOKAHEAD, PRESETS, POOL, enemyOf, drawOpponents, PLANS, RULES, BRAINS, SHAPES, ROLE, create, step, run, summary, monsters, hunters, done, fork, bcFeatures, bcPredict };
if (typeof module !== 'undefined' && module.exports) module.exports = api;
else root.FormationSim = api;
})(typeof globalThis !== 'undefined' ? globalThis : this);
