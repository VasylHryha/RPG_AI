// Tests for cache.js (PLAN_CACHE.md section 6, step 3). Run: node --test test_cache.js
'use strict';
const test = require('node:test'), assert = require('node:assert');
const fs = require('fs'), os = require('os'), path = require('path');
const C = require('./cache.js');

const tmp = () => fs.mkdtempSync(path.join(os.tmpdir(), 'cache-test-'));
function fixture() {
	const d = tmp(), sim = path.join(d, 'sim.js'), net = path.join(d, 'net.json');
	fs.writeFileSync(sim, 'function step() { return 1; }\n'); fs.writeFileSync(net, '{"w":[1,2]}');
	return { d, sim, net, root: path.join(d, 'cache') };
}
const fpOf = (f, settings = { duration: 150 }) => C.fingerprint({ files: [f.sim, f.net], settings });

test('the fingerprint is stable, ignores key order, and changes with one byte of a file or a setting', () => {
	const f = fixture(), a = fpOf(f);
	assert.strictEqual(fpOf(f).id, a.id);
	assert.strictEqual(C.fingerprint({ files: [f.sim, f.net], settings: { b: 1, a: 2 } }).id, C.fingerprint({ files: [f.sim, f.net], settings: { a: 2, b: 1 } }).id);
	assert.notStrictEqual(fpOf(f, { duration: 151 }).id, a.id);
	fs.writeFileSync(f.sim, 'function step() { return 2; }\n');
	assert.notStrictEqual(fpOf(f).id, a.id);
	assert.strictEqual(a.parts.node, process.version);
});

test('a changed file gives a new folder; the old folder and its results stay', () => {
	const f = fixture(), s1 = C.open(f.root, fpOf(f));
	s1.put({ p: 'x', seed: 1 }, { m: 3 }); s1.flush();
	fs.writeFileSync(f.sim, 'changed');
	const s2 = C.open(f.root, fpOf(f));
	assert.notStrictEqual(s2.dir, s1.dir);
	assert.strictEqual(s2.get({ p: 'x', seed: 1 }), undefined);
	fs.writeFileSync(f.sim, 'function step() { return 1; }\n');
	assert.deepStrictEqual(C.open(f.root, fpOf(f)).get({ p: 'x', seed: 1 }), { m: 3 });
});

test('put, flush and reopen round trip; keys are order-insensitive objects or strings; a repeated put is a no-op', () => {
	const f = fixture(), fp = fpOf(f), s = C.open(f.root, fp);
	s.put({ seed: 1, p: 'a' }, { m: 1, win: 0 }); s.put('plain', 7); s.put({ p: 'a', seed: 1 }, { m: 99 });
	s.flush();
	const r = C.open(f.root, fp);
	assert.strictEqual(r.loaded, 2);
	assert.deepStrictEqual(r.get({ p: 'a', seed: 1 }), { m: 1, win: 0 });
	assert.strictEqual(r.get('plain'), 7);
	assert.strictEqual(fs.readFileSync(path.join(r.dir, 'fights.jsonl'), 'utf8').trim().split('\n').length, 2);
});

test('a torn last line is ignored; a corrupt line in the middle refuses the cache', () => {
	const f = fixture(), fp = fpOf(f), s = C.open(f.root, fp);
	s.put('a', 1); s.put('b', 2); s.flush();
	const file = path.join(s.dir, 'fights.jsonl');
	fs.appendFileSync(file, '{"k":"tor');
	const t = C.open(f.root, fp);
	assert.strictEqual(t.loaded, 2);
	t.put('c', 3); t.flush();
	assert.strictEqual(C.open(f.root, fp).get('c'), 3);   // the torn tail was cut, so the next append is clean
	const lines = fs.readFileSync(file, 'utf8').split('\n');
	lines.splice(1, 0, 'garbage'); fs.writeFileSync(file, lines.join('\n'));
	assert.throws(() => C.open(f.root, fp), /corrupt/);
});

test('a spot-check mismatch marks the folder BAD and later opens refuse it; a match passes', async () => {
	const f = fixture(), fp = fpOf(f), s = C.open(f.root, fp);
	for (let i = 0; i < 10; i++) s.put({ i }, { m: i });
	s.flush();
	let x = 1; const rand = () => { x = (x * 48271) % 2147483647; return x / 2147483647; };
	const truth = (key) => ({ m: JSON.parse(key).i });
	assert.deepStrictEqual(await C.spotCheck(s, 5, truth, rand), { checked: 5 });
	await assert.rejects(C.spotCheck(s, 10, (key) => ({ m: JSON.parse(key).i === 4 ? -1 : JSON.parse(key).i }), rand), /spot check failed/);
	assert.throws(() => C.open(f.root, fp), /refused/);
});

test('the seed ledger: a selection seed is refused for confirmation and the reverse; nextFree skips used seeds', () => {
	const f = fixture(), s = C.open(f.root, fpOf(f));
	s.ledger.use([101, 102], 'selection', 'run5');
	s.ledger.use([301], 'confirmation', 'run5');
	assert.throws(() => s.ledger.use([102, 303], 'confirmation', 'run6'), /102 were already used for selection/);
	assert.throws(() => s.ledger.use([301], 'selection', 'run6'), /301 were already used for confirmation/);
	s.ledger.use([101], 'selection', 'run6');
	assert.strictEqual(s.ledger.uses(101).length, 2);
	assert.deepStrictEqual(s.ledger.nextFree(3, 100), [100, 103, 104]);
	assert.throws(() => s.ledger.use([1], 'tuning', 'r'), /unknown seed use/);
});

test('the library keeps entries with their evidence and prefers confirmed results for best()', () => {
	const f = fixture(), s = C.open(f.root, fpOf(f));
	assert.throws(() => s.library.add({ kind: 'unit' }), /needs 'key'/);
	s.library.add({ kind: 'unit', key: 'A', pieces: ['dodgeShots=true'], run: 'run4', score_selection: 30 });
	s.library.add({ kind: 'unit', key: 'B', pieces: ['castDodge=true'], run: 'run4', score_selection: 20, confirmation: { margin: 21.3 } });
	s.library.add({ kind: 'pair', key: 'P', pieces: ['a', 'b'], run: 'run4', score_selection: 9 });
	s.library.add({ kind: 'unit', key: 'B', pieces: ['castDodge=true'], run: 'run4', score_selection: 20 });
	assert.strictEqual(s.library.list().length, 3);
	assert.strictEqual(s.library.best('unit').key, 'B');
	assert.strictEqual(s.library.best('pair').key, 'P');
});

test('a line of 4 KB or more is refused (appends must not interleave)', () => {
	const f = fixture(), s = C.open(f.root, fpOf(f));
	assert.throws(() => s.put('big', 'x'.repeat(5000)), /under 4 KB/);
});
