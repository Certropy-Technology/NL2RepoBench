import assert from 'node:assert/strict';
import { test } from 'node:test';
import { equal } from './test_client.mjs';

const json = (value) => JSON.parse(value);

test('null values are equal', () => {
  assert.equal(equal(null, null), true);
});

test('boolean values use strict equality', () => {
  assert.equal(equal(true, true), true);
  assert.equal(equal(true, false), false);
});

test('Unicode strings are compared by value', () => {
  assert.equal(equal('cafe \u00e9 \ud83d\ude00', 'cafe \u00e9 \ud83d\ude00'), true);
  assert.equal(equal('cafe \u00e9', 'cafe'), false);
});

test('finite JSON numbers are compared by value', () => {
  assert.equal(equal(-12.5, -12.5), true);
  assert.equal(equal(12.5, -12.5), false);
});

test('different JSON primitive kinds are not equal', () => {
  assert.equal(equal(1, '1'), false);
  assert.equal(equal(null, false), false);
});

test('empty arrays and objects are equal to their own kind', () => {
  assert.equal(equal([], []), true);
  assert.equal(equal({}, {}), true);
});

test('arrays compare elements in order', () => {
  assert.equal(equal([1, 'two', null], [1, 'two', null]), true);
});

test('arrays with different element order are not equal', () => {
  assert.equal(equal([1, 2, 3], [3, 2, 1]), false);
});

test('arrays with different lengths are not equal', () => {
  assert.equal(equal([1, 2], [1, 2, 3]), false);
});

test('nested arrays and objects compare recursively', () => {
  const left = { rows: [{ id: 1, tags: ['a', 'b'] }, { id: 2, tags: [] }] };
  const right = { rows: [{ id: 1, tags: ['a', 'b'] }, { id: 2, tags: [] }] };
  assert.equal(equal(left, right), true);
});

test('object key insertion order does not affect equality', () => {
  assert.equal(equal({ alpha: 1, beta: 2 }, { beta: 2, alpha: 1 }), true);
});

test('objects with different key sets are not equal', () => {
  assert.equal(equal({ alpha: 1 }, { alpha: 1, beta: 2 }), false);
});

test('objects with different nested values are not equal', () => {
  assert.equal(equal({ config: { retry: 2 } }, { config: { retry: 3 } }), false);
});

test('arrays and objects are distinct JSON kinds', () => {
  assert.equal(equal([], {}), false);
});

test('an own __proto__ JSON key is compared recursively', () => {
  const left = json('{"__proto__":{"items":[1,2]}}');
  const right = json('{"__proto__":{"items":[1,2]}}');
  assert.equal(equal(left, right), true);
});

test('matching scalar constructor keys compare equal', () => {
  const left = json('{"constructor":"entry","value":1}');
  const right = json('{"value":1,"constructor":"entry"}');
  assert.equal(equal(left, right), true);
});

test('different scalar constructor keys are not equal', () => {
  const left = json('{"constructor":1}');
  const right = json('{"constructor":2}');
  assert.equal(equal(left, right), false);
});

test('matching structured constructor object keys compare false', () => {
  const left = json('{"constructor":{"nested":true}}');
  const right = json('{"constructor":{"nested":true}}');
  assert.equal(equal(left, right), false);
});

test('matching structured constructor array keys compare false', () => {
  const left = json('{"constructor":[1,2]}');
  const right = json('{"constructor":[1,2]}');
  assert.equal(equal(left, right), false);
});

test('matching null constructor keys compare equal', () => {
  const left = json('{"constructor":null}');
  const right = json('{"constructor":null}');
  assert.equal(equal(left, right), true);
});
