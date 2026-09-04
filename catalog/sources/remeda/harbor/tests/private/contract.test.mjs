import assert from 'node:assert/strict';
import {test} from 'node:test';
import {call, callLast, inventory} from './test_client.mjs';

const value = (name, ...args) => call(name, args);
test('package shape and selected exports', () => {
  const result = inventory();
  assert.equal(result.name, 'remeda');
  assert.equal(result.version, '2.0.0');
  assert.equal(result.type, 'module');
  assert.equal(result.rootExport.import, './dist/index.js');
  assert.equal(result.rootExport.require, './dist/index.cjs');
  for (const name of ['map','filter','chunk','groupBy','mergeDeep','pipe','range','truncate','unique','zip']) assert.ok(result.exports.includes(name));
});
test('map and filter data-first preserve order and callback indexes', () => {
  assert.deepEqual(value('map', [4, 5, 6], {kind: 'remainder', divisor: 3}), [1, 2, 0]);
  assert.deepEqual(value('filter', [1, 2, 3, 4], {kind: 'even'}), [2, 4]);
});
test('take drop chunk and unique', () => {
  assert.deepEqual(value('take', [1,2,3,4], 2), [1,2]);
  assert.deepEqual(value('drop', [1,2,3,4], 2), [3,4]);
  assert.deepEqual(value('chunk', [1,2,3,4,5], 2), [[1,2],[3,4],[5]]);
  assert.deepEqual(value('unique', [1,2,1,3,2]), [1,2,3]);
});
test('difference partition groupBy and indexBy', () => {
  assert.deepEqual(value('difference', [1,1,2,3], [1,3]), [1,2]);
  assert.deepEqual(value('partition', [1,2,3,4], {kind: 'even'}), [[2,4],[1,3]]);
  assert.deepEqual(value('groupBy', [1,2,3,4], {kind: 'remainder', divisor: 2}), {0:[2,4],1:[1,3]});
  assert.deepEqual(value('indexBy', [{id:'a'},{id:'b'}], {kind:'property', key:'id'}), {a:{id:'a'},b:{id:'b'}});
});
test('zip range reverse and sortBy', () => {
  assert.deepEqual(value('zip', [1,2,3], ['a','b']), [[1,'a'],[2,'b']]);
  assert.deepEqual(value('range', 1, {end:6,step:2}), [1,3,5]);
  assert.deepEqual(value('reverse', [1,2,3]), [3,2,1]);
  assert.deepEqual(value('sortBy', [{x:3},{x:1},{x:2}], [[{kind:'property',key:'x'}, 'asc']]), [{x:1},{x:2},{x:3}]);
});
test('numeric and predicate operations', () => {
  assert.equal(value('add', 4, 5), 9);
  assert.equal(value('multiply', 4, 5), 20);
  assert.equal(value('sum', [1,2,3]), 6);
  assert.equal(value('mean', [1,2,4]), 7/3);
  assert.equal(value('clamp', 10, {min: 0, max: 5}), 5);
  assert.equal(value('isDeepEqual', {a:[1,2]}, {a:[1,2]}), true);
  assert.equal(value('isNullish', null), true);
  assert.equal(value('isString', 'x'), true);
  assert.equal(value('isNumber', 3), true);
});
test('object operations do not mutate input', () => {
  const data = {a:1,b:2,c:3};
  assert.deepEqual(value('pick', data, ['a','c']), {a:1,c:3});
  assert.deepEqual(value('omit', data, ['b']), {a:1,c:3});
  assert.deepEqual(value('merge', {a:1}, {b:2}), {a:1,b:2});
  assert.deepEqual(value('mergeDeep', {a:{x:1},b:1}, {a:{y:2}}), {a:{x:1,y:2},b:1});
});
test('data-last pipeline and strings', () => {
  assert.deepEqual(value('pipe', [1,2,2,3], [{name:'unique'},{name:'take',args:[2]}]), [1,2]);
  assert.equal(value('capitalize', 'hello'), 'Hello');
  assert.equal(value('uncapitalize', 'Hello'), 'hello');
  assert.equal(value('toCamelCase', 'hello-world test'), 'helloWorldTest');
  assert.equal(value('toKebabCase', 'Hello world'), 'hello-world');
  assert.equal(value('toSnakeCase', 'Hello world'), 'hello_world');
  assert.equal(value('truncate', 'hello world', 8), 'hello...');
});
test('data-last forms preserve the same semantics', () => {
  assert.deepEqual(callLast('map', [[1,2,3], {kind:'remainder', divisor:2}]), [1,0,1]);
  assert.deepEqual(callLast('take', [[1,2,3], 2]), [1,2]);
  assert.deepEqual(callLast('difference', [[1,1,2], [1]]), [1,2]);
  assert.equal(callLast('add', [5, 7]), 12);
  assert.deepEqual(callLast('range', [1, 4]), [1,2,3]);
});
test('range and chunk reject invalid sizes', () => {
  assert.throws(() => value('range', 0, {end: 2, step: 0}), /step/);
  assert.throws(() => value('chunk', [1,2], 0), /infinite|positive|zero/i);
});
test('results are fresh and inputs remain unchanged', () => {
  const data = [3,1,2];
  const result = value('reverse', data);
  assert.deepEqual(data, [3,1,2]);
  assert.notEqual(result, data);
  assert.deepEqual(value('sortBy', data, [[{kind:'identity'}, 'asc']]), [1,2,3]);
});
