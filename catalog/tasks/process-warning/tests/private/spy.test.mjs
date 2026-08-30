import assert from 'node:assert/strict';
import {test} from 'node:test';

const client = await import(process.env.NODE_TEST_CLIENT);
const options = {name: 'SpyWarning', code: 'spy', message: '%s|%s|%s'};
const run = (overrides = {}) => client.spy(options, [['a'], ['b']], {
  afterResetArgs: ['reset'],
  afterRestoreArgs: ['restored'],
  respiedArgs: ['respied'],
  ...overrides,
});

test('active limited spy returns undefined while recording boolean results', () => {
  const value = run();
  assert.deepEqual(value.value.activeReturns, [{type: 'undefined', value: null}, {type: 'undefined', value: null}]);
  assert.deepEqual(value.value.beforeReset.calls.map(item => item.result), [true, false]);
});

test('active unlimited spy records true for every underlying call', () => {
  const value = client.spy({...options, unlimited: true}, [['a'], ['b']], {afterResetArgs: [], afterRestoreArgs: [], respiedArgs: []});
  assert.deepEqual(value.value.beforeReset.calls.map(item => item.result), [true, true]);
});

test('spy argument records use positional truthiness trimming', () => {
  const value = client.spy(options, [[0], [0, 'b'], ['a', 0, 'c']], {afterResetArgs: [], afterRestoreArgs: [], respiedArgs: []});
  assert.deepEqual(value.value.beforeReset.calls.map(item => item.arguments), [[], [0, 'b'], ['a', 0, 'c']]);
});

test('spyWarning returns the same object for an active spy', () => {
  assert.equal(run().value.duplicateSame, true);
});

test('reset clears calls and emitted state before recording again', () => {
  const value = run().value;
  assert.deepEqual(value.afterReset, {calls: [], callCount: 0, emitted: false});
  assert.equal(value.afterResetReturn.type, 'undefined');
  assert.deepEqual(value.afterResetCall.calls.map(item => item.result), [true]);
});

test('restore clears spy state and restores the warning boolean return', () => {
  const value = run().value;
  assert.deepEqual(value.afterRestoreReturn, {type: 'boolean', value: true});
  assert.deepEqual(value.afterRestore.calls, []);
  assert.equal(value.afterRestore.callCount, 0);
});

test('a restored warning can receive a fresh active spy', () => {
  const value = run().value;
  assert.equal(value.freshSpy, true);
  assert.deepEqual(value.respiedReturn, {type: 'undefined', value: null});
  assert.deepEqual(value.afterRespied.calls.map(item => item.result), [false]);
});
