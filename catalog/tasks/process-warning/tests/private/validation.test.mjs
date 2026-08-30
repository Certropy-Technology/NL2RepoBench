import assert from 'node:assert/strict';
import {test} from 'node:test';

const client = await import(process.env.NODE_TEST_CLIENT);

test('missing name raises the documented error', () => {
  assert.deepEqual(client.validation({code: 'CODE', message: 'message'}), {threw: true, name: 'Error', message: 'Warning name must not be empty'});
});

test('missing code raises the documented error', () => {
  assert.deepEqual(client.validation({name: 'Warning', message: 'message'}), {threw: true, name: 'Error', message: 'Warning code must not be empty'});
});

test('missing message raises the documented error', () => {
  assert.deepEqual(client.validation({name: 'Warning', code: 'CODE'}), {threw: true, name: 'Error', message: 'Warning message must not be empty'});
});

test('non-boolean unlimited raises the documented error', () => {
  assert.deepEqual(client.validation({name: 'Warning', code: 'CODE', message: 'message', unlimited: 1}), {threw: true, name: 'Error', message: 'Warning opts.unlimited must be a boolean'});
});

test('separately created warnings keep independent emitted state', () => {
  const value = client.isolation();
  assert.deepEqual(value.value.first, [true, false]);
  assert.deepEqual(value.value.second, [true, false]);
  assert.deepEqual(value.value.state, {first: true, second: true});
  assert.equal(value.emitted.length, 2);
});
