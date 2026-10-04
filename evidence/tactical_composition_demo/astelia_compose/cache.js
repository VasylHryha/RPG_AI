// Fight memory, seed ledger and combination library (PLAN_CACHE.md). Development tooling; generic: any driver (the JS workers today, the C++ host later)
// stores a result under (fingerprint, key) and never replays a fight it already has.
//
//   const C = require('./cache.js');
//   const fp = C.fingerprint({ files: [simPath, netPath], settings: {...} });     // what makes a saved result valid
//   const store = C.open(cacheRoot, fp);                                          // cacheRoot/<fp.id>/
//   store.get(key) / store.put(key, value) / store.flush()                         // fights.jsonl, append-only, one writer per process
//   await C.spotCheck(store, n, replay, rand)                                      // replays n saved results; a mismatch marks the folder BAD
//   store.ledger.use(seeds, 'selection' | 'confirmation', run) / .check(...) / .nextFree(...)
//   store.library.add(entry) / .list() / .best(kind)
//
// Layout of cacheRoot/<id>/: meta.json (what went into the fingerprint), fights.jsonl (not in git: rebuildable), seeds.json and library.json (in git),
// BAD (present = refused, with the reason).
'use strict';
const fs = require('fs'), path = require('path'), crypto = require('crypto');

const FORMAT = 1;
const sha = (s) => crypto.createHash('sha256').update(s).digest('hex');

// Canonical JSON: object keys sorted at every depth, so the fingerprint does not depend on property order.
function canon(x) {
	if (Array.isArray(x)) return '[' + x.map(canon).join(',') + ']';
	if (x && typeof x === 'object') return '{' + Object.keys(x).sort().map((k) => JSON.stringify(k) + ':' + canon(x[k])).join(',') + '}';
	return JSON.stringify(x === undefined ? null : x);
}

// files: paths whose bytes matter; settings: anything else that changes a result (fight options, opponents' skills, host binary hash, ...).
function fingerprint({ files = [], settings = {} }) {
	const parts = { format: FORMAT, node: process.version, files: files.map((f) => ({ name: path.basename(f), sha256: sha(fs.readFileSync(f)) })), settings };
	return { id: sha(canon(parts)).slice(0, 16), parts };
}

const keyHash = (key) => sha(typeof key === 'string' ? key : canon(key)).slice(0, 24);

function readJson(file, dflt) { try { return JSON.parse(fs.readFileSync(file, 'utf8')); } catch (e) { if (e.code === 'ENOENT') return dflt; throw e; } }
function writeJson(file, obj) { const tmp = `${file}.${process.pid}.${Date.now()}.tmp`; fs.writeFileSync(tmp, JSON.stringify(obj, null, 1)); fs.renameSync(tmp, file); }

function loadFights(file) {
	const out = new Map();
	if (!fs.existsSync(file)) return out;
	const lines = fs.readFileSync(file, 'utf8').split('\n');
	for (let i = 0; i < lines.length; i++) {
		if (!lines[i]) continue;
		let r;
		try { r = JSON.parse(lines[i]); } catch (e) {
			const last = lines.slice(i + 1).every((l) => !l);
			if (last) { fs.truncateSync(file, Buffer.byteLength(lines.slice(0, i).join('\n') + (i ? '\n' : ''))); break; }   // a torn last line (a crash mid-append): cut off, so the next append starts clean
			throw new Error(`${file}: line ${i + 1} is corrupt and not the last line; refusing the cache`);
		}
		out.set(r.k, { key: r.key, v: r.v });
	}
	return out;
}

const USES = ['selection', 'confirmation'];

function open(root, fp) {
	const dir = path.join(root, fp.id);
	fs.mkdirSync(dir, { recursive: true });
	const bad = path.join(dir, 'BAD');
	if (fs.existsSync(bad)) throw new Error(`cache ${dir} is refused: ${fs.readFileSync(bad, 'utf8').trim()}`);
	const metaFile = path.join(dir, 'meta.json'), meta = readJson(metaFile, null);
	if (meta && canon(meta.parts) !== canon(fp.parts)) throw new Error(`cache ${dir}: meta.json does not match the fingerprint (hash collision or edited file)`);
	if (!meta) writeJson(metaFile, { id: fp.id, parts: fp.parts, created: new Date().toISOString() });
	const fightsFile = path.join(dir, 'fights.jsonl'), mem = loadFights(fightsFile), loaded = mem.size;
	let pending = [];
	const store = {
		dir, id: fp.id, loaded,
		has: (key) => mem.has(keyHash(key)),
		get: (key) => { const e = mem.get(keyHash(key)); return e === undefined ? undefined : e.v; },
		put(key, value) {
			const k = keyHash(key), ks = typeof key === 'string' ? key : canon(key);
			if (mem.has(k)) return;
			mem.set(k, { key: ks, v: value });
			const line = JSON.stringify({ k, key: ks, v: value });
			if (Buffer.byteLength(line) >= 4000) throw new Error('a cache line must stay under 4 KB so appends from two processes never interleave');
			pending.push(line);
		},
		flush() { if (pending.length) { fs.appendFileSync(fightsFile, pending.join('\n') + '\n'); pending = []; } },
		size: () => mem.size,
		entries: () => [...mem.values()].map((e) => [e.key, e.v]),   // [original key (string), value]
		markBad(reason) { fs.writeFileSync(bad, reason + '\n'); },
	};

	// The seed ledger: which seed was used for what, by which run. A seed used for selection is never fresh for confirmation, and the reverse.
	const seedsFile = path.join(dir, 'seeds.json');
	store.ledger = {
		read: () => readJson(seedsFile, {}),
		uses(seed) { return (this.read()[seed] || []); },
		check(seeds, use) {
			if (!USES.includes(use)) throw new Error(`unknown seed use '${use}'`);
			const other = use === 'selection' ? 'confirmation' : 'selection', bad_ = seeds.filter((s) => this.uses(s).some((u) => u.use === other));
			if (bad_.length) throw new Error(`seeds ${bad_.join(',')} were already used for ${other}; they cannot be used for ${use}`);
		},
		use(seeds, use, run) {
			this.check(seeds, use);
			const led = this.read();
			for (const s of seeds) { led[s] = led[s] || []; if (!led[s].some((u) => u.use === use && u.run === run)) led[s].push({ use, run, at: new Date().toISOString() }); }
			writeJson(seedsFile, led);
		},
		nextFree(count, from) { const led = this.read(), out = []; for (let s = from; out.length < count; s++) if (!led[s]) out.push(s); return out; },
	};

	// The combination library: proven units, pairs and merges with their evidence.
	const libFile = path.join(dir, 'library.json');
	store.library = {
		list: () => readJson(libFile, []),
		add(entry) {
			for (const f of ['kind', 'key', 'pieces', 'run', 'score_selection']) if (entry[f] === undefined) throw new Error(`library entry needs '${f}'`);
			const lib = this.list();
			if (lib.some((e) => e.key === entry.key && e.run === entry.run)) return;
			lib.push(Object.assign({ added: new Date().toISOString() }, entry));
			writeJson(libFile, lib);
		},
		best(kind) {
			const lib = this.list().filter((e) => !kind || e.kind === kind);
			const conf = lib.filter((e) => e.confirmation && typeof e.confirmation.margin === 'number');
			const pool = conf.length ? conf : lib, score = (e) => (e.confirmation && typeof e.confirmation.margin === 'number' ? e.confirmation.margin : e.score_selection);
			return pool.reduce((a, b) => (a === null || score(b) > score(a) ? b : a), null);
		},
	};
	return store;
}

// Replays n saved results chosen with rand() and compares them with what is stored. replay(key) gets the original key (as stored: a string, canonical JSON
// for object keys) and must return the fresh value. Any difference marks the folder BAD and throws.
async function spotCheck(store, n, replay, rand) {
	const all = store.entries();
	if (!all.length) return { checked: 0 };
	const picks = new Set(); while (picks.size < Math.min(n, all.length)) picks.add(Math.floor(rand() * all.length));
	for (const i of picks) {
		const [k, saved] = all[i], fresh = await replay(k);
		if (canon(fresh) !== canon(saved)) {
			const reason = `spot check failed at ${new Date().toISOString()}: key ${k} saved ${canon(saved)} replayed ${canon(fresh)} (the fingerprint missed something that changes results)`;
			store.markBad(reason);
			throw new Error(reason);
		}
	}
	return { checked: picks.size };
}

module.exports = { fingerprint, open, spotCheck, keyHash, canon, FORMAT };
