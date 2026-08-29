import assert from 'node:assert/strict';
import test from 'node:test';
import {scenario} from './test_client.mjs';

const expectResult = (commands, expected, options) => {
  const actual = scenario(commands, options).result;
  assert.deepStrictEqual(actual, expected);
};

test('package metadata and ESM entry are correct', () => {
  expectResult([{op: 'metadata'}], [{name: 'quick-lru', version: '7.3.0', type: 'module', exports: {types: './index.d.ts', default: './index.js'}}]);
});

test('constructor rejects missing and non-positive maxSize', () => {
  assert.throws(() => scenario([]), /maxSize/);
  for (const value of [0, -1, null]) assert.throws(() => scenario([], {maxSize: value}), /maxSize/);
});

test('constructor rejects numeric zero maxAge', () => {
  assert.throws(() => scenario([], {maxSize: 2, maxAge: 0}), /maxAge/);
});

test('set returns the cache and get/size preserve values', () => {
  expectResult([{op: 'set', key: 'a', value: 1}, {op: 'get', key: 'a'}, {op: 'size'}], [true, 1, 1], {maxSize: 3});
});

test('setting a key updates it without duplicating size', () => {
  expectResult([{op: 'set', key: 'a', value: 1}, {op: 'set', key: 'a', value: 2}, {op: 'size'}, {op: 'get', key: 'a'}], [true, true, 1, 2], {maxSize: 3});
});

test('has distinguishes an undefined value from a missing key', () => {
  expectResult([{op: 'set', key: 'empty', value: null}, {op: 'has', key: 'empty'}, {op: 'get', key: 'empty'}, {op: 'has', key: 'missing'}], [true, true, null, false], {maxSize: 3});
});

test('peek returns values without promoting old entries', () => {
  expectResult([
    {op: 'set', key: 'a', value: 1}, {op: 'set', key: 'b', value: 2}, {op: 'set', key: 'c', value: 3},
    {op: 'peek', key: 'a'}, {op: 'set', key: 'd', value: 4}, {op: 'has', key: 'a'}, {op: 'has', key: 'b'},
  ], [true, true, true, 1, true, false, false], {maxSize: 2});
});

test('delete returns existence and clear removes all entries', () => {
  expectResult([{op: 'set', key: 'a', value: 1}, {op: 'set', key: 'b', value: 2}, {op: 'delete', key: 'a'}, {op: 'delete', key: 'a'}, {op: 'clear'}, {op: 'size'}], [true, true, true, false, true, 0], {maxSize: 3});
});

test('keys and values omit expired entries and follow ascending order', () => {
  expectResult([{op: 'set', key: 'old', value: 1, options: {maxAge: 10}}, {op: 'set', key: 'new', value: 2}, {op: 'advance', value: 11}, {op: 'keys'}, {op: 'values'}], [true, true, 11, ['new'], [2]], {maxSize: 3});
});

test('entriesAscending and entries are oldest first', () => {
  expectResult([{op: 'set', key: 'a', value: 1}, {op: 'set', key: 'b', value: 2}, {op: 'set', key: 'c', value: 3}, {op: 'ascending'}, {op: 'entries'}], [true, true, true, [['a', 1], ['b', 2], ['c', 3]], [['a', 1], ['b', 2], ['c', 3]]], {maxSize: 5});
});

test('entriesDescending and default iterator are newest first and ascending respectively', () => {
  expectResult([{op: 'set', key: 'a', value: 1}, {op: 'set', key: 'b', value: 2}, {op: 'set', key: 'c', value: 3}, {op: 'descending'}, {op: 'iterator'}], [true, true, true, [['c', 3], ['b', 2], ['a', 1]], [['a', 1], ['b', 2], ['c', 3]]], {maxSize: 5});
});

test('updating a recent key keeps its insertion position', () => {
  expectResult([{op: 'set', key: 'a', value: 1}, {op: 'set', key: 'b', value: 2}, {op: 'set', key: 'a', value: 3}, {op: 'ascending'}], [true, true, true, [['a', 3], ['b', 2]]], {maxSize: 3});
});

test('forEach receives value, key, cache, and thisArg in ascending order', () => {
  expectResult([{op: 'set', key: 'a', value: 1}, {op: 'set', key: 'b', value: 2}, {op: 'forEach', thisArg: {name: 'ctx'}}], [true, true, [[1, 'a', true, 'ctx'], [2, 'b', true, 'ctx']]], {maxSize: 3});
});

test('getting an old entry promotes it and preserves LRU pressure behavior', () => {
  expectResult([{op: 'set', key: 'a', value: 1}, {op: 'set', key: 'b', value: 2}, {op: 'set', key: 'c', value: 3}, {op: 'get', key: 'a'}, {op: 'set', key: 'd', value: 4}, {op: 'has', key: 'a'}, {op: 'has', key: 'b'}], [true, true, true, 1, true, true, false], {maxSize: 2});
});

test('size is capped during dual-cache rotation while iteration exposes live entries', () => {
  expectResult([{op: 'set', key: 'a', value: 1}, {op: 'set', key: 'b', value: 2}, {op: 'set', key: 'c', value: 3}, {op: 'size'}, {op: 'ascending'}], [true, true, true, 2, [['a', 1], ['b', 2], ['c', 3]]], {maxSize: 2});
});

test('maxSize and maxAge getters expose constructor options', () => {
  expectResult([{op: 'maxSize'}, {op: 'maxAge'}], [4, 50], {maxSize: 4, maxAge: 50});
});

test('resize shrinks to newest entries and emits discarded entries', () => {
  const result = scenario([{op: 'set', key: 'a', value: 1}, {op: 'set', key: 'b', value: 2}, {op: 'set', key: 'c', value: 3}, {op: 'resize', value: 2}, {op: 'ascending'}], {maxSize: 4, callback: true});
  assert.deepStrictEqual(result.result, [true, true, true, 2, [['b', 2], ['c', 3]]]);
  assert.deepStrictEqual(result.evictions, [['a', 1]]);
});

test('resize can increase capacity while preserving entries', () => {
  expectResult([{op: 'set', key: 'a', value: 1}, {op: 'set', key: 'b', value: 2}, {op: 'resize', value: 4}, {op: 'set', key: 'c', value: 3}, {op: 'ascending'}], [true, true, 4, true, [['a', 1], ['b', 2], ['c', 3]]], {maxSize: 2});
});

test('resize rejects non-positive sizes', () => {
  assert.throws(() => scenario([{op: 'resize', value: 0}], {maxSize: 2}), /maxSize/);
});

test('evict defaults to one oldest entry', () => {
  expectResult([{op: 'set', key: 'a', value: 1}, {op: 'set', key: 'b', value: 2}, {op: 'set', key: 'c', value: 3}, {op: 'evict'}, {op: 'ascending'}], [true, true, true, 2, [['b', 2], ['c', 3]]], {maxSize: 5});
});

test('evict removes the requested oldest entries and calls onEviction', () => {
  const result = scenario([{op: 'set', key: 'a', value: 1}, {op: 'set', key: 'b', value: 2}, {op: 'set', key: 'c', value: 3}, {op: 'evict', value: 2}], {maxSize: 5, callback: true});
  assert.deepStrictEqual(result.result, [true, true, true, 1]);
  assert.deepStrictEqual(result.evictions, [['a', 1], ['b', 2]]);
});

test('evict always keeps at least one live entry', () => {
  expectResult([{op: 'set', key: 'a', value: 1}, {op: 'set', key: 'b', value: 2}, {op: 'evict', value: 99}, {op: 'ascending'}], [true, true, 1, [['b', 2]]], {maxSize: 5});
});

test('evict coerces fractional and non-positive counts', () => {
  expectResult([{op: 'set', key: 'a', value: 1}, {op: 'set', key: 'b', value: 2}, {op: 'set', key: 'c', value: 3}, {op: 'evict', value: 1.9}, {op: 'evict', value: 0}, {op: 'ascending'}], [true, true, true, 2, 2, [['b', 2], ['c', 3]]], {maxSize: 5});
});

test('object keys use identity rather than JSON shape', () => {
  expectResult([{op: 'bind', name: 'key', value: {id: 1}}, {op: 'set', key: {$ref: 'key'}, value: 'hit'}, {op: 'has', key: {$ref: 'key'}}, {op: 'has', key: {id: 1}}], [true, true, true, false], {maxSize: 3});
});

test('object values are returned by identity within the candidate process', () => {
  expectResult([{op: 'bind', name: 'value', value: {nested: [1, 2]}}, {op: 'set', key: 'object', value: {$ref: 'value'}}, {op: 'get', key: 'object'}], [true, true, {nested: [1, 2]}], {maxSize: 3});
});

test('toString and toStringTag describe the cache', () => {
  expectResult([{op: 'set', key: 'a', value: 1}, {op: 'toString'}, {op: 'tag'}], [true, 'QuickLRU(1/2)', 'QuickLRU'], {maxSize: 2});
});

test('expiresIn reports missing and non-expiring entries', () => {
  expectResult([{op: 'expiresIn', key: 'missing'}, {op: 'set', key: 'a', value: 1}, {op: 'expiresIn', key: 'a'}], [undefined, true, Infinity], {maxSize: 2});
});

test('expiresIn reports exact remaining time without evicting', () => {
  expectResult([{op: 'set', key: 'a', value: 1, options: {maxAge: 100}}, {op: 'advance', value: 40}, {op: 'expiresIn', key: 'a'}, {op: 'advance', value: 70}, {op: 'expiresIn', key: 'a'}, {op: 'has', key: 'a'}], [true, 40, 60, 110, -10, false], {maxSize: 2});
});

test('get and has lazily remove expired entries', () => {
  const result = scenario([{op: 'set', key: 'a', value: 1}, {op: 'advance', value: 11}, {op: 'get', key: 'a'}, {op: 'size'}, {op: 'set', key: 'b', value: 2, options: {maxAge: 5}}, {op: 'advance', value: 6}, {op: 'has', key: 'b'}], {maxSize: 3, maxAge: 10, callback: true});
  assert.deepStrictEqual(result.result, [true, 11, undefined, 0, true, 17, false]);
  assert.deepStrictEqual(result.evictions, [['a', 1], ['b', 2]]);
});

test('per-entry maxAge overrides the global TTL', () => {
  expectResult([{op: 'set', key: 'global', value: 1}, {op: 'set', key: 'local', value: 2, options: {maxAge: 100}}, {op: 'advance', value: 50}, {op: 'has', key: 'global'}, {op: 'has', key: 'local'}, {op: 'advance', value: 51}, {op: 'has', key: 'local'}], [true, true, 50, false, true, 101, false], {maxSize: 3, maxAge: 40});
});

test('expired entries invoke onEviction when peek removes them', () => {
  const result = scenario([{op: 'set', key: 'a', value: 1, options: {maxAge: 5}}, {op: 'advance', value: 6}, {op: 'peek', key: 'a'}], {maxSize: 2, callback: true});
  assert.deepStrictEqual(result.result, [true, 6, undefined]);
  assert.deepStrictEqual(result.evictions, [['a', 1]]);
});

test('iteration omits expired entries in both cache generations', () => {
  expectResult([{op: 'set', key: 'a', value: 1, options: {maxAge: 5}}, {op: 'set', key: 'b', value: 2}, {op: 'set', key: 'c', value: 3}, {op: 'advance', value: 6}, {op: 'ascending'}, {op: 'descending'}], [true, true, true, 6, [['b', 2], ['c', 3]], [['c', 3], ['b', 2]]], {maxSize: 2});
});

test('clear does not call the eviction callback', () => {
  const result = scenario([{op: 'set', key: 'a', value: 1}, {op: 'set', key: 'b', value: 2}, {op: 'clear'}, {op: 'size'}], {maxSize: 2, callback: true});
  assert.deepStrictEqual(result.result, [true, true, true, 0]);
  assert.deepStrictEqual(result.evictions, []);
});

test('delete does not call the eviction callback', () => {
  const result = scenario([{op: 'set', key: 'a', value: 1}, {op: 'delete', key: 'a'}], {maxSize: 2, callback: true});
  assert.deepStrictEqual(result.result, [true, true]);
  assert.deepStrictEqual(result.evictions, []);
});
