import assert from 'node:assert/strict';
import {readFileSync, statSync} from 'node:fs';
import {join} from 'node:path';
import test from 'node:test';

const {callScenario} = await import(
  process.env.NODE_TEST_CLIENT ?? '/tests/private/test_client.mjs'
);

function packageManifest() {
  const root = join(process.env.NODE_CANDIDATE_SITE, 'node_modules', 'p-timeout');
  return {
    root,
    package: JSON.parse(readFileSync(join(root, 'package.json'), 'utf8')),
  };
}

test('package identity and scripts-free zero-dependency contract', () => {
  const {root, package: manifest} = packageManifest();
  assert.equal(manifest.name, 'p-timeout');
  assert.equal(manifest.version, '7.0.1');
  assert.equal(manifest.type, 'module');
  assert.deepEqual(manifest.exports, {types: './index.d.ts', default: './index.js'});
  assert.deepEqual(manifest.files, ['index.js', 'index.d.ts']);
  assert.deepEqual(manifest.dependencies ?? {}, {});
  assert.deepEqual(manifest.devDependencies ?? {}, {});
  assert.deepEqual(manifest.scripts ?? {}, {});
  assert.equal(statSync(join(root, 'index.js')).isFile(), true);
  assert.equal(statSync(join(root, 'index.d.ts')).isFile(), true);
});

test('root exports pTimeout and TimeoutError', () => {
  assert.deepEqual(callScenario('exports'), {
    defaultType: 'function',
    defaultName: 'pTimeout',
    errorType: 'function',
    errorName: 'TimeoutError',
  });
});

test('TimeoutError preserves Error shape, message, and cause', () => {
  assert.deepEqual(callScenario('timeout_error'), {
    isError: true,
    isTimeoutError: true,
    type: 'TimeoutError',
    name: 'TimeoutError',
    message: 'custom-message',
    cause: 'root-cause',
  });
});

for (const kind of ['zero', 'negative', 'nan', 'negative-infinity', 'string', 'null', 'missing']) {
  test(`milliseconds rejects ${kind}`, () => {
    const value = callScenario('validation', {kind});
    assert.equal(value.result.status, 'rejected');
    assert.equal(value.result.error.type, 'TypeError');
    assert.match(value.result.error.message, /positive number/);
  });
}

for (const kind of ['positive', 'fractional', 'infinity']) {
  test(`milliseconds accepts ${kind}`, () => {
    const value = callScenario('validation', {kind});
    assert.deepEqual(value.result, {status: 'fulfilled', value: 'accepted'});
  });
}

test('input resolution preserves JSON value and clearable Promise shape', () => {
  const value = callScenario('input_resolve', {milliseconds: 37, value: {answer: [42]}});
  assert.deepEqual(value.result, {status: 'fulfilled', value: {answer: [42]}});
  assert.equal(value.clearType, 'function');
  assert.equal(value.isPromise, true);
  assert.equal(value.timer.delay, 37);
  assert.equal(value.timer.setReceiverIsUndefined, true);
  assert.deepEqual(value.timer.clearCalls, ['timer']);
});

test('input rejection preserves error type, message, and cause', () => {
  const value = callScenario('input_reject');
  assert.equal(value.result.status, 'rejected');
  assert.deepEqual(value.result.error, {
    type: 'RangeError',
    name: 'RangeError',
    message: 'input-failed',
    cause: 'input-cause',
  });
  assert.deepEqual(value.timer.clearCalls, ['timer']);
});

test('PromiseLike input is adopted', () => {
  const value = callScenario('thenable');
  assert.deepEqual(value.result, {status: 'fulfilled', value: {from: 'thenable'}});
  assert.deepEqual(value.timer.clearCalls, ['timer']);
});

test('default timeout rejects TimeoutError and cancels input', () => {
  const value = callScenario('timeout', {milliseconds: 41});
  assert.equal(value.result.status, 'rejected');
  assert.equal(value.result.error.type, 'TimeoutError');
  assert.equal(value.result.error.name, 'TimeoutError');
  assert.equal(value.result.error.message, 'Promise timed out after 41 milliseconds');
  assert.equal(value.cancelCount, 1);
  assert.deepEqual(value.timer.clearCalls, ['timer']);
});

test('string message changes TimeoutError message', () => {
  const value = callScenario('timeout', {messageKind: 'string', message: 'too slow'});
  assert.equal(value.result.status, 'rejected');
  assert.equal(value.result.error.type, 'TimeoutError');
  assert.equal(value.result.error.message, 'too slow');
});

test('empty string remains an empty TimeoutError message', () => {
  const value = callScenario('timeout', {messageKind: 'empty'});
  assert.equal(value.result.status, 'rejected');
  assert.equal(value.result.error.type, 'TimeoutError');
  assert.equal(value.result.error.message, '');
});

test('message false fulfills with undefined', () => {
  const value = callScenario('timeout', {messageKind: 'false'});
  assert.deepEqual(value.result, {status: 'fulfilled'});
  assert.equal(value.cancelCount, 1);
});

test('custom Error is rejected by identity', () => {
  const value = callScenario('timeout', {messageKind: 'error', message: 'custom'});
  assert.equal(value.result.status, 'rejected');
  assert.equal(value.result.error.type, 'RangeError');
  assert.equal(value.result.error.message, 'custom');
  assert.equal(value.sameCustomError, true);
});

test('fallback can return a synchronous value', () => {
  const value = callScenario('fallback', {kind: 'value'});
  assert.deepEqual(value.result, {status: 'fulfilled', value: {fallback: 'value'}});
  assert.equal(value.calls, 1);
  assert.equal(value.cancelCount, 0);
});

test('fallback adopts a returned Promise', () => {
  const value = callScenario('fallback', {kind: 'promise'});
  assert.deepEqual(value.result, {status: 'fulfilled', value: {fallback: 'promise'}});
  assert.equal(value.calls, 1);
  assert.equal(value.cancelCount, 0);
});

test('fallback synchronous throw is preserved', () => {
  const value = callScenario('fallback', {kind: 'throw'});
  assert.equal(value.result.status, 'rejected');
  assert.equal(value.result.error.type, 'SyntaxError');
  assert.equal(value.result.error.message, 'fallback-threw');
});

test('fallback rejected Promise is preserved', () => {
  const value = callScenario('fallback', {kind: 'reject'});
  assert.equal(value.result.status, 'rejected');
  assert.equal(value.result.error.type, 'EvalError');
  assert.equal(value.result.error.message, 'fallback-rejected');
});

test('cancel is called once only when timeout wins', () => {
  const timedOut = callScenario('cancel_behavior', {kind: 'timeout'});
  const resolved = callScenario('cancel_behavior', {kind: 'resolve'});
  assert.equal(timedOut.cancelCount, 1);
  assert.equal(resolved.cancelCount, 0);
  assert.deepEqual(resolved.result, {status: 'fulfilled', value: 'done'});
});

test('clear is idempotent and leaves the input active', () => {
  const value = callScenario('clear');
  assert.deepEqual(value.result, {status: 'fulfilled', value: 'after-clear'});
  assert.deepEqual(value.timer.clearCalls, ['timer', 'undefined', 'undefined']);
});

test('Infinity schedules no timer and still adopts input', () => {
  const value = callScenario('infinity');
  assert.deepEqual(value.result, {status: 'fulfilled', value: 'infinite-result'});
  assert.equal(value.timer.scheduled, false);
  assert.deepEqual(value.timer.clearCalls, ['undefined']);
});

test('already-aborted signal rejects with AbortError', () => {
  const value = callScenario('abort_already');
  assert.equal(value.result.status, 'rejected');
  assert.equal(value.result.error.type, 'DOMException');
  assert.equal(value.result.error.name, 'AbortError');
  assert.equal(value.timer.scheduled, false);
});

test('already-aborted signal preserves custom reason', () => {
  const value = callScenario('abort_already', {customReason: true});
  assert.equal(value.result.status, 'rejected');
  assert.equal(value.result.error.type, 'RangeError');
  assert.equal(value.result.error.message, 'custom-abort');
  assert.equal(value.sameReason, true);
});

test('already-aborted signal still wins with Infinity', () => {
  const value = callScenario('abort_already', {infinity: true});
  assert.equal(value.result.status, 'rejected');
  assert.equal(value.result.error.name, 'AbortError');
  assert.equal(value.timer.scheduled, false);
});

for (const kind of ['resolve', 'reject', 'timeout', 'abort']) {
  test(`abort listener is once-only and removed after ${kind}`, () => {
    const value = callScenario('abort_later', {kind});
    assert.equal(value.added, 1);
    assert.equal(value.once, true);
    assert.equal(value.removed, 1);
    if (kind === 'abort') assert.equal(value.result.error.name, 'AbortError');
  });
}
