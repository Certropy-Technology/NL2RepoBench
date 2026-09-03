import assert from 'node:assert/strict';
import {test} from 'node:test';
import {call} from './test_client.mjs';

test('package metadata identifies the frozen CommonJS package', () => {
  assert.deepEqual(call('metadata'), {
    name: 'deepmerge', version: '4.3.1', main: 'index.js', type: null,
    callable: true, allCallable: true,
  });
});
test('root merge adds source keys', () => assert.deepEqual(call('merge', {target: {}, source: {a: 1, b: 2}}), {a: 1, b: 2}));
test('source values replace simple target values', () => assert.deepEqual(call('merge', {target: {a: 1, keep: true}, source: {a: 2}}), {a: 2, keep: true}));
test('nested objects merge recursively', () => assert.deepEqual(call('merge', {target: {a: {x: 1}}, source: {a: {y: 2}}}), {a: {x: 1, y: 2}}));
test('inputs are not mutated', () => assert.deepEqual(call('merge', {target: {a: {x: 1}}, source: {a: {y: 2}}}), {a: {x: 1, y: 2}}));
test('object can replace a primitive', () => assert.deepEqual(call('merge', {target: {a: 1}, source: {a: {x: 2}}}), {a: {x: 2}}));
test('primitive can replace an object', () => assert.deepEqual(call('merge', {target: {a: {x: 1}}, source: {a: 2}}), {a: 2}));
test('arrays are values when object and array types differ', () => assert.deepEqual(call('merge', {target: {a: {}}, source: {a: [1, 2]}}), {a: [1, 2]}));
test('null source values are preserved', () => assert.deepEqual(call('merge', {target: {a: 1}, source: {a: null}}), {a: null}));
test('object key order does not change values', () => assert.deepEqual(call('merge', {target: {b: 2, a: 1}, source: {c: 3}}), {b: 2, a: 1, c: 3}));
test('top-level arrays concatenate', () => assert.deepEqual(call('merge', {target: [1, 2], source: [3, 4]}), [1, 2, 3, 4]));
test('array properties concatenate', () => assert.deepEqual(call('merge', {target: {items: [1]}, source: {items: [2, 3]}}), {items: [1, 2, 3]}));
test('nested array objects are cloned', () => assert.deepEqual(call('merge', {target: [], source: [{a: {b: 1}}]}), [{a: {b: 1}}]));
test('clone false preserves nested target identity', () => assert.equal(call('identity').cloneFalseTarget, true));
test('clone false preserves nested source identity', () => assert.equal(call('identity').cloneFalseSource, true));
test('clone true copies nested target values', () => assert.equal(call('identity').cloneTrueTarget, true));
test('clone true copies nested source values', () => assert.equal(call('identity').cloneTrueSource, true));
test('empty arrays remain empty', () => assert.deepEqual(call('merge', {target: [], source: []}), []));
test('custom array merge can overwrite', () => assert.deepEqual(call('merge', {target: {items: [1, 2]}, source: {items: [3]}, options: {arrayMerge: 'overwrite'}}), {items: [3]}));
test('custom array merge can combine matching indexes', () => assert.deepEqual(call('merge', {target: [{a: 1}], source: [{b: 2}], options: {arrayMerge: 'combine'}}), [{a: 1, b: 2}]));
test('custom array merge can append unmatched values', () => assert.deepEqual(call('merge', {target: [{a: 1}], source: [{b: 2}, 'tail'], options: {arrayMerge: 'combine'}}), [{a: 1, b: 2}, 'tail']));
test('custom property merge receives the property key', () => assert.deepEqual(call('merge', {target: {name: {first: 'Alex'}}, source: {name: {first: 'Tony'}}, options: {customMerge: 'join-name'}}), {name: 'Alex and Tony'}));
test('invalid custom property merge falls back', () => assert.deepEqual(call('merge', {target: {a: {x: 1}}, source: {a: {y: 2}}, options: {customMerge: 'invalid'}}), {a: {x: 1, y: 2}}));
test('merge all combines every object', () => assert.deepEqual(call('all', {values: [{a: 1}, {b: 2}, {c: 3}]}), {a: 1, b: 2, c: 3}));
test('merge all accepts an empty list', () => assert.deepEqual(call('all', {values: []}), {}));
test('merge all uses left-to-right precedence', () => assert.deepEqual(call('all', {values: [{a: 1}, {a: 2}, {a: 3}]}), {a: 3}));
test('merge all applies custom clone option', () => assert.deepEqual(call('all', {values: [{a: {x: 1}}, {b: {y: 2}}], options: {clone: false}}), {a: {x: 1}, b: {y: 2}}));
test('merge all rejects a non-array', () => { const result = call('invalid-all', {value: {a: 1}}); assert.equal(result.threw, true); assert.equal(result.name, 'Error'); });
test('merge all error explains its first argument', () => assert.match(call('invalid-all', {value: {}}).message, /first argument.*array/i));
test('own proto input does not pollute the result', () => assert.deepEqual(call('prototype'), {safe: 1, ownProto: false}));
test('enumerable symbol properties are copied', () => assert.deepEqual(call('symbols'), {copied: true, count: 1}));
test('special objects are treated as atomic by default', () => assert.deepEqual(call('special'), {defaultDateIdentity: true, defaultRegexpIdentity: true, plainDateIdentity: true, plainRegexpIdentity: true}));
