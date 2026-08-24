import { test } from 'node:test';
import assert from 'node:assert/strict';
import { callCandidate } from './test_client.mjs';

const canonicalize = (value) => callCandidate('default', [value]);

test('object keys are lexicographically ordered', () => {
  assert.equal(canonicalize({ b: 1, a: 2 }), '{"a":2,"b":1}');
});
test('nested objects and arrays are canonicalized', () => {
  assert.equal(canonicalize({ z: [3, { y: 2, x: 1 }] }), '{"z":[3,{"x":1,"y":2}]}');
});
test('arrays preserve order', () => {
  assert.equal(canonicalize([3, 1, 2]), '[3,1,2]');
});
test('null is canonical JSON', () => {
  assert.equal(canonicalize(null), 'null');
});
test('booleans are canonical JSON', () => {
  assert.equal(canonicalize(true), 'true');
});
test('numbers use JSON spelling', () => {
  assert.equal(canonicalize(-0), '0');
});
test('strings retain Unicode', () => {
  assert.equal(canonicalize('café 😀'), '"café 😀"');
});
test('empty containers are supported', () => {
  assert.equal(canonicalize({}), '{}');
  assert.equal(canonicalize([]), '[]');
});
test('lone high surrogate is rejected', () => {
  assert.throws(() => canonicalize({ key: '\ud800' }), /Lone surrogate is not allowed/);
});
test('lone low surrogate is rejected', () => {
  assert.throws(() => canonicalize({ key: '\udead' }), /Lone surrogate is not allowed/);
});
