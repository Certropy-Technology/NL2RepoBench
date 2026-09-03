import assert from 'node:assert/strict';
import test from 'node:test';
import {run} from './test_client.mjs';

const signals = (dockerenv, cgroup, mountinfo) => ({dockerenv, cgroup, mountinfo});
const detect = value => run({op: 'detect', signals: value});
const cache = (first, second) => run({op: 'cache', first, second});

test('adapter-version', () => {
	assert.deepEqual(run({op: 'version'}), {version: '4.0.0'});
});

test('adapter-rejects-operation', () => {
	assert.throws(() => run({op: 'unknown'}), /unsupported|unknown/i);
});

test('adapter-rejects-malformed-signals', () => {
	assert.throws(() => detect({dockerenv: true, cgroup: false}), /signal|invalid|unsupported/i);
});

test('detect-dockerenv', () => assert.equal(detect(signals(true, false, false)), true));
test('detect-cgroup', () => assert.equal(detect(signals(false, true, false)), true));
test('detect-mountinfo', () => assert.equal(detect(signals(false, false, true)), true));
test('detect-none', () => assert.equal(detect(signals(false, false, false)), false));
test('detect-all', () => assert.equal(detect(signals(true, true, true)), true));
test('detect-dockerenv-with-negative-rest', () => assert.equal(detect(signals(true, false, false)), true));
test('detect-cgroup-with-negative-rest', () => assert.equal(detect(signals(false, true, false)), true));
test('detect-mountinfo-with-negative-rest', () => assert.equal(detect(signals(false, false, true)), true));

test('cache-true-stays-true', () => {
	assert.deepEqual(cache(signals(true, false, false), signals(false, false, false)), {first: true, second: true});
});

test('cache-false-stays-false', () => {
	assert.deepEqual(cache(signals(false, false, false), signals(true, true, true)), {first: false, second: false});
});

test('cache-first-marker-priority', () => {
	assert.deepEqual(cache(signals(false, true, false), signals(true, false, false)), {first: true, second: true});
});

test('cache-second-markers-ignored', () => {
	assert.deepEqual(cache(signals(false, false, false), signals(false, false, true)), {first: false, second: false});
});
