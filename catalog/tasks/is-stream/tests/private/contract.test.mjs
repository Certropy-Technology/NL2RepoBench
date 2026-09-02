import assert from 'node:assert/strict';
import test from 'node:test';
import {run} from './test_client.mjs';

const native = (type, destroyed = false) => ({kind: 'native', type, destroyed});
const primitive = value => ({kind: 'primitive', value});
const shape = (methods = [], fields = {}) => ({kind: 'shape', methods, ...fields});
const check = (predicate, value, checkOpen) => run({
	op: 'check',
	predicate,
	value,
	...(checkOpen === undefined ? {} : {checkOpen}),
});

test('adapter-version', async () => {
	assert.deepEqual(await run({op: 'version'}), {version: '4.0.1'});
});

test('adapter-invalid-operation', async () => {
	await assert.rejects(() => run({op: 'unknown'}), /unsupported|unknown/i);
});

test('stream-base', async () => assert.equal(await check('stream', native('stream')), true));
test('stream-readable', async () => assert.equal(await check('stream', native('readable')), true));
test('stream-writable', async () => assert.equal(await check('stream', native('writable')), true));
test('stream-empty-shape', async () => assert.equal(await check('stream', shape()), false));
test('stream-null', async () => assert.equal(await check('stream', primitive(null)), false));
test('stream-string', async () => assert.equal(await check('stream', primitive('stream')), false));
test('stream-pipe-shape', async () => assert.equal(await check('stream', shape(['pipe'])), true));
test('stream-closed-default', async () => assert.equal(await check('stream', native('readable', true)), false));
test('stream-closed-ignored', async () => assert.equal(await check('stream', native('readable', true), false), true));

test('writable-native', async () => assert.equal(await check('writable', native('writable')), true));
test('writable-duplex', async () => assert.equal(await check('writable', native('duplex')), true));
test('writable-transform', async () => assert.equal(await check('writable', native('transform')), true));
test('writable-readable-false', async () => assert.equal(await check('writable', native('readable')), false));
test('writable-closed-default', async () => assert.equal(await check('writable', native('writable', true)), false));
test('writable-closed-ignored', async () => assert.equal(await check('writable', native('writable', true), false), true));

test('readable-native', async () => assert.equal(await check('readable', native('readable')), true));
test('readable-duplex', async () => assert.equal(await check('readable', native('duplex')), true));
test('readable-pass-through', async () => assert.equal(await check('readable', native('passThrough')), true));
test('readable-writable-false', async () => assert.equal(await check('readable', native('writable')), false));
test('readable-closed-default', async () => assert.equal(await check('readable', native('readable', true)), false));
test('readable-closed-ignored', async () => assert.equal(await check('readable', native('readable', true), false), true));

test('duplex-native', async () => assert.equal(await check('duplex', native('duplex')), true));
test('duplex-transform', async () => assert.equal(await check('duplex', native('transform')), true));
test('duplex-pass-through', async () => assert.equal(await check('duplex', native('passThrough')), true));
test('duplex-readable-false', async () => assert.equal(await check('duplex', native('readable')), false));
test('duplex-writable-false', async () => assert.equal(await check('duplex', native('writable')), false));

test('transform-native', async () => assert.equal(await check('transform', native('transform')), true));
test('transform-pass-through', async () => assert.equal(await check('transform', native('passThrough')), true));
test('transform-duplex-false', async () => assert.equal(await check('transform', native('duplex')), false));
test('transform-structural', async () => {
	const value = shape(
		['pipe', 'read', 'write', 'end', 'destroy', '_transform'],
		{readable: true, writable: true, readableObjectMode: false, writableObjectMode: false, destroyed: false},
	);
	assert.equal(await check('transform', value), true);
});
