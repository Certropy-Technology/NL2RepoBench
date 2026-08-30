import assert from 'node:assert/strict';
import {test} from 'node:test';

const client = await import(process.env.NODE_TEST_CLIENT);
const base = {name: 'TestWarning', code: 'test_code', message: '%s|%s|%s'};

test('createWarning exposes normalized metadata and initial state', () => {
  const value = client.warning(base, []).value.initial;
  assert.deepEqual(value, {name: 'TestWarning', code: 'TEST_CODE', message: '%s|%s|%s', unlimited: false, emitted: false});
});

test('format without arguments leaves placeholders unchanged', () => {
  const value = client.warning(base, [{kind: 'format', args: []}]).value.actions[0];
  assert.deepEqual(value, {kind: 'format', result: '%s|%s|%s', emitted: false});
});

test('format forwards one, two, or three truthy positional values', () => {
  const actions = client.warning(base, [
    {kind: 'format', args: ['a']},
    {kind: 'format', args: ['a', 'b']},
    {kind: 'format', args: ['a', 'b', 'c']},
  ]).value.actions;
  assert.deepEqual(actions.map(item => item.result), ['a|%s|%s', 'a|b|%s', 'a|b|c']);
});

test('format requires a fully truthy positional prefix', () => {
  const actions = client.warning(base, [
    {kind: 'format', args: [0]},
    {kind: 'format', args: [0, 'b']},
    {kind: 'format', args: ['a', 0, 'c']},
  ]).value.actions;
  assert.deepEqual(actions.map(item => item.result), ['%s|%s|%s', '%s|%s|%s', 'a|%s|%s']);
});

test('limited warnings emit once and return false thereafter', () => {
  const value = client.warning(base, [{kind: 'call', args: ['a', 'b', 'c']}, {kind: 'call', args: ['x']}]);
  assert.deepEqual(value.value.actions.map(item => item.result), [{type: 'boolean', value: true}, {type: 'boolean', value: false}]);
  assert.equal(value.value.finalEmitted, true);
  assert.equal(value.emitted.length, 1);
});

test('manually clearing emitted enables another limited emission', () => {
  const value = client.warning(base, [{kind: 'call', args: ['a']}, {kind: 'reset'}, {kind: 'call', args: ['b']}]);
  assert.deepEqual(value.value.actions.map(item => item.kind), ['call', 'reset', 'call']);
  assert.deepEqual(value.value.actions.filter(item => item.kind === 'call').map(item => item.result.value), [true, true]);
  assert.equal(value.emitted.length, 2);
});

test('unlimited warnings emit and return true on every call', () => {
  const value = client.warning({...base, unlimited: true}, [{kind: 'call', args: ['a']}, {kind: 'call', args: ['b']}]);
  assert.deepEqual(value.value.actions.map(item => item.result.value), [true, true]);
  assert.equal(value.emitted.length, 2);
});

test('emission forwards formatted message, warning name, and uppercase code', () => {
  const value = client.warning(base, [{kind: 'call', args: ['a', 'b', 'c']}]);
  assert.deepEqual(value.emitted, [['a|b|c', 'TestWarning', 'TEST_CODE']]);
});

test('createDeprecation forces the DeprecationWarning name', () => {
  const value = client.validation({name: 'IgnoredName', code: 'dep', message: 'deprecated'}, 'deprecation');
  assert.deepEqual(value, {threw: false, name: 'DeprecationWarning', code: 'DEP', message: 'deprecated', unlimited: false});
});
