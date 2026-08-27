import assert from 'node:assert/strict';
import {test} from 'node:test';
import {call} from './test_client.mjs';

const p = (operation, payload) => {
  const result = call(operation, payload);
  assert.equal(result.ok, true, result.message);
  return result.value;
};

test('api-exports', () => {
  const value = p('inventory', {});
  assert.equal(value.packageName, 'immer');
  assert.equal(value.packageVersion, '10.0.3-beta');
  assert.equal(value.packageShape, true);
  assert.equal(value.runtimeEntry, true);
  assert.equal(value.declarationEntry, true);
  assert.equal(value.defaultIsProduce, true);
  assert.ok(value.exportNames.includes('produce'));
  assert.ok(value.exportNames.includes('produceWithPatches'));
  assert.ok(value.exportNames.includes('Immer'));
});
test('package-contract', () => {
  const value = p('inventory', {});
  assert.deepEqual(value.exportNames.filter(name => name === 'default'), ['default']);
});
test('produce-noop', () => {
  const value = p('produce', {base: {a: 1}, actions: []});
  assert.deepEqual(value.next, {a: 1});
  assert.equal(value.sameBase, true);
});
test('produce-does-not-mutate-base', () => {
  const value = p('produce', {base: {a: 1}, actions: [{op: 'set', path: ['a'], value: 2}]});
  assert.deepEqual(value.next, {a: 2});
});
test('nested-set', () => {
  const value = p('produce', {base: {user: {name: 'A'}}, actions: [{op: 'set', path: ['user', 'name'], value: 'B'}]});
  assert.deepEqual(value.next, {user: {name: 'B'}});
});
test('delete-property', () => {
  const value = p('produce', {base: {a: 1, b: 2}, actions: [{op: 'delete', path: ['a']}]});
  assert.deepEqual(value.next, {b: 2});
});
test('assign-object', () => {
  const value = p('produce', {base: {a: 1}, actions: [{op: 'assign', path: [], value: {b: 2, c: 3}}]});
  assert.deepEqual(value.next, {a: 1, b: 2, c: 3});
});
test('array-push', () => {
  const value = p('produce', {base: {items: [1]}, actions: [{op: 'push', path: ['items'], values: [2, 3]}]});
  assert.deepEqual(value.next, {items: [1, 2, 3]});
});
test('array-splice', () => {
  const value = p('produce', {base: [1, 2, 4], actions: [{op: 'splice', path: [], start: 2, deleteCount: 1, items: [3, 4]}]});
  assert.deepEqual(value.next, [1, 2, 3, 4]);
});
test('array-shift-unshift', () => {
  const value = p('produce', {base: [2, 3], actions: [{op: 'unshift', path: [], values: [1]}, {op: 'shift', path: []}]});
  assert.deepEqual(value.next, [2, 3]);
});
test('replacement', () => {
  const value = p('produce', {base: {a: 1}, actions: [], replacement: {b: 2}});
  assert.deepEqual(value.next, {b: 2});
  assert.equal(value.sameBase, false);
});
test('nothing-sentinel', () => {
  const value = p('produce', {base: {a: 1}, actions: [], returnNothing: true});
  assert.equal(value.isUndefined, true);
});
test('auto-freeze-default', () => {
  const value = p('produce', {base: {nested: {x: 1}}, actions: [{op: 'set', path: ['nested', 'x'], value: 2}]});
  assert.equal(value.frozen, true);
  assert.equal(value.nestedFrozen, true);
});
test('auto-freeze-toggle', () => {
  const value = p('produce', {base: {nested: {x: 1}}, actions: [{op: 'set', path: ['nested', 'x'], value: 2}], autoFreeze: false});
  assert.equal(value.frozen, false);
});
test('freeze-deep', () => {
  const value = p('utilities', {value: {nested: {x: 1}}, deep: true});
  assert.equal(value.draftable, true);
  assert.equal(value.same, true);
  assert.equal(value.frozenAfter, true);
});
test('patches-replace', () => {
  const value = p('patches', {base: {a: 1}, actions: [{op: 'set', path: ['a'], value: 2}]});
  assert.deepEqual(value.patches, [{op: 'replace', path: ['a'], value: 2}]);
  assert.deepEqual(value.inversePatches, [{op: 'replace', path: ['a'], value: 1}]);
});
test('patches-add-remove', () => {
  const value = p('patches', {base: {a: 1, b: 2}, actions: [{op: 'delete', path: ['a']}, {op: 'set', path: ['c'], value: 3}]});
  assert.deepEqual(value.patches, [{op: 'remove', path: ['a']}, {op: 'add', path: ['c'], value: 3}]);
});
test('patches-array', () => {
  const value = p('patches', {base: [1, 2], actions: [{op: 'push', path: [], values: [3]}]});
  assert.deepEqual(value.patches, [{op: 'add', path: [2], value: 3}]);
});
test('apply-patches', () => {
  const value = p('apply-patches', {base: {a: 1}, patches: [{op: 'replace', path: ['a'], value: 2}]});
  assert.deepEqual(value.next, {a: 2});
});
test('inverse-patches', () => {
  const patches = p('patches', {base: {a: 1}, actions: [{op: 'set', path: ['a'], value: 2}]});
  const value = p('apply-patches', {base: patches.next, patches: patches.inversePatches});
  assert.deepEqual(value.next, {a: 1});
});
test('draft-finish', () => {
  const value = p('draft-lifecycle', {base: {a: 1}, actions: [{op: 'set', path: ['a'], value: 2}]});
  assert.deepEqual(value.next, {a: 2});
  assert.equal(value.beforeFinish.isDraft, true);
  assert.equal(value.mutationError, true);
});
test('draft-used-after-finish', () => {
  const value = p('draft-lifecycle', {base: {a: 1}, actions: []});
  assert.equal(value.mutationError, true);
});
test('observe-current-original', () => {
  const value = p('observe', {base: {a: 1}, actions: [{op: 'set', path: ['a'], value: 2}]});
  assert.equal(value.observed.isDraft, true);
  assert.deepEqual(value.observed.original, {a: 1});
  assert.deepEqual(value.observed.currentBefore, {a: 1});
  assert.deepEqual(value.observed.currentAfter, {a: 2});
});
test('observe-is-draft', () => {
  const value = p('observe', {base: {nested: {a: 1}}, actions: []});
  assert.equal(value.observed.isDraft, true);
  assert.deepEqual(value.next, {nested: {a: 1}});
});
test('is-draftable', () => {
  const values = [null, true, 1, 'x', [], {}, [1], {a: 1}];
  const flags = values.map(value => p('utilities', {value}).draftable);
  assert.deepEqual(flags, [false, false, false, false, true, true, true, true]);
});
test('freeze-returns-same', () => {
  const value = p('utilities', {value: {a: 1}, deep: false});
  assert.equal(value.same, true);
  assert.equal(value.frozenAfter, true);
});
test('json-coercion', () => {
  const value = p('produce', {base: {items: [1, 'x', null, true]}, actions: []});
  assert.deepEqual(value.next, {items: [1, 'x', null, true]});
});
test('repeated-result', () => {
  const payload = {base: {a: {b: 1}, xs: [1, 2]}, actions: [{op: 'set', path: ['a', 'b'], value: 3}, {op: 'push', path: ['xs'], values: [4]}]};
  assert.deepEqual(p('produce', payload).next, p('produce', payload).next);
});
