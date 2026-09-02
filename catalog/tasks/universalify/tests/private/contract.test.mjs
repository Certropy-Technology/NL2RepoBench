import assert from 'node:assert/strict';
import {test} from 'node:test';
import {callCandidate} from './test_client.mjs';

function value(scenario) {
  const response = callCandidate(scenario);
  assert.equal(response.ok, true, `${scenario}: ${response.error ?? response.message}`);
  return response.value;
}

test('CommonJS root exports exactly the two wrapper factories', () => {
  assert.deepEqual(value('shape'), {
    keys: ['fromCallback', 'fromPromise'],
    types: {fromCallback: 'function', fromPromise: 'function'},
  });
});

test('fromCallback preserves the wrapped function name', () => {
  assert.equal(value('callback-name'), 'callbackSource');
});

test('fromPromise preserves the wrapped function name', () => {
  assert.equal(value('promise-name'), 'promiseSource');
});

test('fromCallback callback mode preserves receiver and arguments', () => {
  assert.deepEqual(value('callback-callback-success'), {
    returned: {type: 'undefined'},
    calls: [[null, {receiver: {label: 'receiver'}, args: [1, 2]}]],
  });
});

test('fromCallback promise mode preserves receiver and arguments', () => {
  assert.deepEqual(value('callback-promise-success'), {
    receiver: {label: 'receiver'}, args: [3, 4],
  });
});

test('fromCallback promise mode does not mutate the caller argument array', () => {
  assert.deepEqual(value('callback-apply-array'), {args: [5, 6], result: [5, 6]});
});

test('fromCallback callback mode forwards Error objects', () => {
  assert.deepEqual(value('callback-callback-error'), [[
    {type: 'error', name: 'TypeError', message: 'callback-failure'},
  ]]);
});

test('fromCallback promise mode rejects with the original error', () => {
  assert.deepEqual(value('callback-promise-error'), {
    settled: 'rejected',
    error: {type: 'error', name: 'RangeError', message: 'promise-failure'},
  });
});

test('fromCallback treats zero as an error rather than success', () => {
  assert.deepEqual(value('callback-falsey-error'), {settled: 'rejected', error: 0});
});

test('fromCallback treats null error as success', () => {
  assert.equal(value('callback-null-success'), 'null-ok');
});

test('fromCallback treats undefined error as success', () => {
  assert.equal(value('callback-undefined-success'), 'undefined-ok');
});

test('fromCallback promise mode resolves only the first result value', () => {
  assert.equal(value('callback-first-result'), 'first');
});

test('fromCallback only detects a callback in the final argument position', () => {
  assert.deepEqual(value('callback-nonfinal-function'), {sameFunction: true, value: 9});
});

test('fromCallback supports synchronous source callback settlement', () => {
  assert.deepEqual(value('callback-sync-settlement'), {isPromise: true, value: 'sync'});
});

test('fromCallback callback mode propagates a user callback throw', () => {
  assert.deepEqual(value('callback-user-throw'), {
    threw: true,
    error: {type: 'error', name: 'Error', message: 'user-callback-threw'},
  });
});

test('fromPromise callback mode preserves receiver and arguments', () => {
  assert.deepEqual(value('promise-callback-success'), {
    returned: {type: 'undefined'},
    calls: [[null, {receiver: {label: 'receiver'}, args: [1, 2]}]],
  });
});

test('fromPromise promise mode returns the source promise unchanged', () => {
  assert.deepEqual(value('promise-passthrough'), {same: true, value: 'same'});
});

test('fromPromise promise mode preserves receiver and arguments', () => {
  assert.deepEqual(value('promise-promise-this'), {
    receiver: {label: 'promise-receiver'}, args: [7, 8],
  });
});

test('fromPromise removes an optional final callback before source invocation', () => {
  assert.deepEqual(value('promise-optional-callback'), [[
    null, {receiver: {label: 'callback-receiver'}, args: [7]},
  ]]);
});

test('fromPromise callback mode forwards rejection errors', () => {
  assert.deepEqual(value('promise-callback-error'), [[
    {type: 'error', name: 'SyntaxError', message: 'rejected'},
  ]]);
});

test('fromPromise promise mode preserves source rejection', () => {
  assert.deepEqual(value('promise-promise-error'), {
    settled: 'rejected',
    error: {type: 'error', name: 'URIError', message: 'promise-rejected'},
  });
});

test('fromPromise callback mode preserves a falsey rejection reason', () => {
  assert.deepEqual(value('promise-falsey-error'), [[0]]);
});

test('fromPromise reports a user callback throw as an unhandled rejection once', () => {
  assert.deepEqual(value('promise-user-throw'), {
    callbackCalls: 1,
    error: {type: 'error', name: 'Error', message: 'callback-throw-rejection'},
  });
});

test('fromPromise callback mode supports a valid thenable', () => {
  assert.deepEqual(value('promise-thenable'), {
    returned: {type: 'undefined'},
    calls: [[null, 'thenable-ok']],
  });
});
