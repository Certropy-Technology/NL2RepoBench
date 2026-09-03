import assert from 'node:assert/strict';
import test from 'node:test';
import {callCandidate} from './test_client.mjs';

test('package identity and public exports', () => {
  assert.deepEqual(callCandidate('package'), {
    name: 'p-map',
    version: '7.0.7',
    default: 'function',
    pMapIterable: 'function',
    pMapSkip: 'symbol',
    type: 'module',
    hasTypes: true,
  });
});

test('maps synchronous values', () => assert.deepEqual(callCandidate('basic'), [2, 4, 6]));
test('preserves result order when promises settle out of order', () => assert.deepEqual(callCandidate('order'), ['slow', 'fast', 'middle']));
test('passes the element index to the mapper', () => assert.deepEqual(callCandidate('index'), [{value: 'a', index: 0}, {value: 'b', index: 1}, {value: 'c', index: 2}]));
test('awaits promise-valued input items', () => assert.deepEqual(callCandidate('promise-input'), [10, 20, 30]));
test('accepts asynchronous input iterables', () => assert.deepEqual(callCandidate('async-input'), [3, 6, 9]));
test('does not exceed finite concurrency', () => assert.deepEqual(callCandidate('concurrency'), {maxRunning: 2, values: [0, 1, 2, 3] }));
test('starts mapper calls asynchronously', () => assert.deepEqual(callCandidate('async-start'), {beforeTurn: false, result: [42]}));
test('runs all synchronous inputs for infinite concurrency', () => assert.deepEqual(callCandidate('infinite'), {started: [1, 2, 3], error: 'first'}));
test('rejects invalid input with TypeError', () => assert.deepEqual(callCandidate('invalid-input'), {name: 'TypeError'}));
test('rejects a non-function mapper', () => assert.deepEqual(callCandidate('invalid-mapper'), {name: 'TypeError'}));
test('rejects invalid concurrency', () => assert.deepEqual(callCandidate('invalid-concurrency'), {name: 'TypeError'}));
test('rejects invalid backpressure', () => assert.deepEqual(callCandidate('invalid-backpressure'), {name: 'TypeError'}));
test('propagates mapper errors', () => assert.deepEqual(callCandidate('mapper-error'), {name: 'Error', message: 'mapper failed'}));
test('propagates source iterator errors', () => assert.deepEqual(callCandidate('source-error'), {name: 'Error', message: 'source failed'}));
test('stops on the first mapper error by default', () => assert.deepEqual(callCandidate('stop-on-error'), {name: 'Error', message: 'first'}));
test('aggregates mapper errors when requested', () => assert.deepEqual(callCandidate('aggregate-error'), {name: 'AggregateError', errors: ['one', 'two']}));
test('rejects an already-aborted signal', () => assert.deepEqual(callCandidate('aborted-signal'), {name: 'AbortError'}));
test('rejects when a signal aborts before the mapper settles', () => assert.deepEqual(callCandidate('abort-signal'), {name: 'AbortError'}));
test('omits the pMapSkip sentinel', () => assert.deepEqual(callCandidate('skip'), ['keep', 'also-keep']));
test('omits every skipped value', () => assert.deepEqual(callCandidate('skip-all'), []));
test('streams values from pMapIterable in order', () => assert.deepEqual(callCandidate('iterable-basic'), [1, 2, 3]));
test('pMapIterable preserves input order', () => assert.deepEqual(callCandidate('iterable-order'), ['first', 'second', 'third']));
test('pMapIterable passes zero-based indices', () => assert.deepEqual(callCandidate('iterable-index'), [{value: 'x', index: 0}, {value: 'y', index: 1}]));
test('pMapIterable accepts asynchronous input', () => assert.deepEqual(callCandidate('iterable-async-input'), [4, 5, 6]));
test('pMapIterable omits pMapSkip', () => assert.deepEqual(callCandidate('iterable-skip'), ['a', 'c']));
test('pMapIterable raises mapper errors on collection', () => assert.deepEqual(callCandidate('iterable-mapper-error'), {name: 'Error', message: 'iterable mapper failed'}));
test('pMapIterable raises source errors on collection', () => assert.deepEqual(callCandidate('iterable-source-error'), {name: 'Error', message: 'iterable source failed'}));
test('pMapIterable enforces backpressure without timing assumptions', () => assert.deepEqual(callCandidate('backpressure'), {first: 1, startedAfterFirst: [1, 2]}));
test('pMapIterable rejects backpressure below concurrency', () => assert.deepEqual(callCandidate('bad-iterable-options'), {name: 'TypeError'}));

