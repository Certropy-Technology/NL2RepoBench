import assert from 'node:assert/strict';
import {test} from 'node:test';
import {scenario} from './test_client.mjs';

test('package identity, exports, dependency, and scripts match the contract', () => {
	assert.deepEqual(scenario('inventory'), {
		name: 'p-retry',
		version: '8.0.0',
		type: 'module',
		engines: {node: '>=22'},
		sideEffects: false,
		typesPresent: true,
		exports: ['AbortError', 'default', 'makeRetriable'],
		defaultCallable: true,
		abortErrorCallable: true,
		makeRetriableCallable: true,
		abortErrorIsError: true,
		dependencies: {'is-network-error': '1.3.2'},
		scriptNames: [],
	});
});

test('a synchronous value resolves on attempt one', () => {
	const value = scenario('run', {successValue: {ok: true}});
	assert.deepEqual(value.value, {ok: true});
	assert.deepEqual(value.attempts, [1]);
	assert.equal(value.error, undefined);
});

test('an asynchronous value resolves on attempt one', () => {
	const value = scenario('run', {asyncSuccess: true, successValue: 'done'});
	assert.equal(value.value, 'done');
	assert.deepEqual(value.attempts, [1]);
});

test('failed attempts are retried and attempt numbers increase from one', () => {
	const value = scenario('run', {failCount: 2, retries: 2, minTimeout: 0, successValue: 'done'});
	assert.equal(value.value, 'done');
	assert.deepEqual(value.attempts, [1, 2, 3]);
});

test('retry exhaustion preserves the final Error', () => {
	const value = scenario('run', {failCount: 3, retries: 2, minTimeout: 0, message: 'exhausted'});
	assert.deepEqual(value.attempts, [1, 2, 3]);
	assert.deepEqual(value.error, {type: 'Error', name: 'Error', message: 'exhausted'});
});

test('the default retry budget performs ten retries after the first attempt', () => {
	const value = scenario('run', {failCount: 12, captureTimers: true, message: 'default exhausted'});
	assert.equal(value.attempts.length, 11);
	assert.deepEqual(value.attempts, Array.from({length: 11}, (_, index) => index + 1));
});

test('zero retries still performs the first attempt', () => {
	const value = scenario('run', {failCount: 1, retries: 0, minTimeout: 0});
	assert.deepEqual(value.attempts, [1]);
	assert.equal(value.error.message, 'fixture failure');
});

test('Infinity retries can succeed after multiple failures', () => {
	const value = scenario('run', {failCount: 3, retries: 'Infinity', minTimeout: 0, successValue: 7});
	assert.equal(value.value, 7);
	assert.deepEqual(value.attempts, [1, 2, 3, 4]);
});

test('Infinity is reported in retry context without truncation', () => {
	const value = scenario('run', {failCount: 1, retries: 'Infinity', minTimeout: 0, hookPolicy: 'record'});
	assert.equal(value.failedContexts[0].retriesLeft, 'Infinity');
	assert.equal(value.failedContexts[0].retriesConsumed, 0);
});

test('negative, non-number, and NaN retry counts reject with TypeError', () => {
	for (const invalid of [-1, 'three', 'NaN']) {
		const value = scenario('validate', {field: 'retries', value: invalid});
		assert.equal(value.threw, true);
		assert.equal(value.error.name, 'TypeError');
	}
});

test('callback options reject non-functions with TypeError', () => {
	for (const field of ['onFailedAttempt', 'shouldRetry', 'shouldConsumeRetry']) {
		const value = scenario('validate', {field, value: 'not a function'});
		assert.equal(value.threw, true);
		assert.equal(value.error.name, 'TypeError');
	}
});

test('numeric delay and time options reject invalid values', () => {
	for (const [field, value] of [
		['factor', -1],
		['factor', 'Infinity'],
		['minTimeout', -1],
		['minTimeout', 'Infinity'],
		['maxTimeout', -1],
		['maxRetryTime', -1],
	]) {
		const result = scenario('validate', {field, value});
		assert.equal(result.threw, true, `${field}=${value}`);
		assert.equal(result.error.name, 'TypeError');
	}
});

test('the removed forever option rejects with a migration error', () => {
	const value = scenario('validate', {field: 'forever'});
	assert.equal(value.threw, true);
	assert.match(value.error.message, /no longer supported/);
});

test('non-Error throws are normalized to a descriptive TypeError', () => {
	const value = scenario('run', {failCount: 1, retries: 2, minTimeout: 0, failureKind: 'non-error', nonErrorValue: 'bad value'});
	assert.deepEqual(value.attempts, [1]);
	assert.equal(value.error.name, 'TypeError');
	assert.match(value.error.message, /Non-error was thrown/);
});

test('ordinary TypeError stops without retrying', () => {
	const value = scenario('run', {failCount: 2, retries: 2, minTimeout: 0, failureKind: 'type-error', message: 'programming error'});
	assert.deepEqual(value.attempts, [1]);
	assert.equal(value.error.message, 'programming error');
});

test('network TypeError remains retryable', () => {
	const value = scenario('run', {failCount: 2, retries: 2, minTimeout: 0, failureKind: 'type-error', message: 'Failed to fetch', successValue: 'online'});
	assert.deepEqual(value.attempts, [1, 2, 3]);
	assert.equal(value.value, 'online');
});

test('AbortError created from a string exposes an Error original', () => {
	assert.deepEqual(scenario('abort-class', {mode: 'string'}), {
		isError: true,
		name: 'AbortError',
		message: 'abort fixture',
		original: {type: 'Error', name: 'Error', message: 'abort fixture'},
		sameOriginal: false,
	});
});

test('AbortError created from Error preserves the original object', () => {
	const value = scenario('abort-class', {mode: 'error'});
	assert.equal(value.name, 'AbortError');
	assert.equal(value.message, 'abort fixture');
	assert.equal(value.sameOriginal, true);
});

test('AbortError stops retries and bypasses all failure callbacks', () => {
	const value = scenario('run', {
		failCount: 3,
		retries: 5,
		minTimeout: 0,
		failureKind: 'abort-error',
		message: 'stop now',
		consumePolicy: 'async-true',
		hookPolicy: 'record',
		retryPolicy: 'async-true',
	});
	assert.deepEqual(value.attempts, [1]);
	assert.deepEqual(value.events, ['input:1']);
	assert.equal(value.error.message, 'stop now');
});

test('onFailedAttempt receives one-based attempts and consumed retry state', () => {
	const value = scenario('run', {failCount: 2, retries: 2, minTimeout: 0, hookPolicy: 'record', successValue: 'done'});
	assert.deepEqual(value.failedContexts.map(context => ({
		attempt: context.attemptNumber,
		left: context.retriesLeft,
		consumed: context.retriesConsumed,
	})), [
		{attempt: 1, left: 2, consumed: 0},
		{attempt: 2, left: 1, consumed: 1},
	]);
});

test('failure callbacks run consume, failed, then retry', () => {
	const value = scenario('run', {
		failCount: 1,
		retries: 1,
		minTimeout: 0,
		consumePolicy: 'async-true',
		hookPolicy: 'record',
		retryPolicy: 'async-true',
		successValue: 'done',
	});
	assert.deepEqual(value.events, ['input:1', 'consume:1', 'failed:1', 'retry:1', 'input:2']);
});

test('onFailedAttempt still runs before shouldRetry declines', () => {
	const value = scenario('run', {failCount: 3, retries: 3, minTimeout: 0, hookPolicy: 'record', retryPolicy: 'false'});
	assert.deepEqual(value.events, ['input:1', 'failed:1', 'retry:1']);
	assert.deepEqual(value.attempts, [1]);
});

test('an asynchronous shouldRetry callback can permit a retry', () => {
	const value = scenario('run', {failCount: 1, retries: 1, minTimeout: 0, retryPolicy: 'async-true', successValue: 2});
	assert.equal(value.value, 2);
	assert.deepEqual(value.attempts, [1, 2]);
});

test('an error from shouldRetry aborts with that error', () => {
	const value = scenario('run', {failCount: 2, retries: 2, minTimeout: 0, retryPolicy: 'throw'});
	assert.deepEqual(value.attempts, [1]);
	assert.equal(value.error.message, 'retry policy stopped');
});

test('shouldConsumeRetry can skip consumption without skipping the next attempt', () => {
	const value = scenario('run', {failCount: 2, retries: 1, minTimeout: 0, consumePolicy: 'false-first', successValue: 'done'});
	assert.equal(value.value, 'done');
	assert.deepEqual(value.attempts, [1, 2, 3]);
	assert.deepEqual(value.consumeContexts.map(context => context.retriesConsumed), [0, 0]);
});

test('an asynchronous shouldConsumeRetry callback is supported', () => {
	const value = scenario('run', {failCount: 1, retries: 1, minTimeout: 0, consumePolicy: 'async-true', successValue: 'done'});
	assert.equal(value.value, 'done');
	assert.deepEqual(value.attempts, [1, 2]);
});

test('every retry context object is frozen', () => {
	const value = scenario('run', {
		failCount: 1,
		retries: 1,
		minTimeout: 0,
		consumePolicy: 'async-true',
		hookPolicy: 'record',
		retryPolicy: 'async-true',
	});
	assert.equal(value.consumeContexts[0].frozen, true);
	assert.equal(value.failedContexts[0].frozen, true);
	assert.equal(value.retryContexts[0].frozen, true);
});

test('an asynchronous onFailedAttempt callback is awaited', () => {
	const value = scenario('run', {failCount: 1, retries: 1, minTimeout: 0, hookPolicy: 'async-record', successValue: 'done'});
	assert.equal(value.value, 'done');
	assert.deepEqual(value.events, ['input:1', 'failed:1', 'input:2']);
});

test('an error from onFailedAttempt aborts with that error', () => {
	const value = scenario('run', {failCount: 2, retries: 2, minTimeout: 0, hookPolicy: 'throw'});
	assert.deepEqual(value.attempts, [1]);
	assert.equal(value.error.message, 'hook stopped');
});

test('factor produces exponential retry delays', () => {
	const value = scenario('run', {failCount: 3, retries: 3, minTimeout: 100, factor: 2, captureTimers: true, successValue: 'done'});
	assert.deepEqual(value.delays, [100, 200, 400]);
	assert.equal(value.value, 'done');
});

test('maxTimeout caps every computed delay', () => {
	const value = scenario('run', {failCount: 3, retries: 3, minTimeout: 100, factor: 2, maxTimeout: 150, captureTimers: true});
	assert.deepEqual(value.delays, [100, 150, 150]);
});

test('randomize multiplies delays by values between one and two', () => {
	const value = scenario('run', {
		failCount: 3,
		retries: 3,
		minTimeout: 100,
		factor: 1,
		randomize: true,
		captureTimers: true,
		randomSequence: [0, 1, 0.5],
	});
	assert.deepEqual(value.delays, [100, 200, 150]);
});

test('a non-positive factor is normalized to stable delay growth', () => {
	const value = scenario('run', {failCount: 3, retries: 3, minTimeout: 100, factor: 0, captureTimers: true});
	assert.deepEqual(value.delays, [100, 100, 100]);
});

test('retryDelay reports computed delays and zero on the final failure', () => {
	const value = scenario('run', {failCount: 3, retries: 2, minTimeout: 100, factor: 2, captureTimers: true, hookPolicy: 'record'});
	assert.deepEqual(value.failedContexts.map(context => context.retryDelay), [100, 200, 0]);
});

test('skipped consumption reports zero delay and preserves backoff position', () => {
	const value = scenario('run', {
		failCount: 2,
		retries: 1,
		minTimeout: 100,
		factor: 2,
		captureTimers: true,
		consumePolicy: 'false-first',
		hookPolicy: 'record',
		successValue: 'done',
	});
	assert.deepEqual(value.failedContexts.map(context => context.retryDelay), [0, 100]);
	assert.deepEqual(value.delays, [100]);
});

test('zero maxRetryTime calls the failure hook once and performs no retry', () => {
	const value = scenario('run', {failCount: 2, retries: 2, minTimeout: 0, maxRetryTime: 0, hookPolicy: 'record'});
	assert.deepEqual(value.attempts, [1]);
	assert.equal(value.failedContexts.length, 1);
	assert.equal(value.failedContexts[0].retryDelay, 0);
});

test('an already-aborted signal preserves an Error reason and skips input', () => {
	const value = scenario('signal', {mode: 'pre-error'});
	assert.equal(value.threw, true);
	assert.equal(value.attempts, 0);
	assert.equal(value.error.message, 'signal reason');
});

test('an already-aborted signal without a reason throws DOMException AbortError', () => {
	const value = scenario('signal', {mode: 'pre-default'});
	assert.equal(value.threw, true);
	assert.equal(value.attempts, 0);
	assert.equal(value.error.name, 'AbortError');
});

test('aborting during a retry delay rejects promptly without another attempt', () => {
	const value = scenario('signal', {mode: 'during-delay'});
	assert.equal(value.threw, true);
	assert.equal(value.attempts, 1);
	assert.equal(value.error.message, 'signal reason');
});

test('unref invokes the timer token unref method', () => {
	const value = scenario('run', {failCount: 1, retries: 1, minTimeout: 100, captureTimers: true, unref: true, successValue: 'done'});
	assert.equal(value.unrefCalls, 1);
	assert.equal(value.value, 'done');
});

test('makeRetriable forwards every argument and applies retry options', () => {
	const value = scenario('make-retriable', {prefix: 'object', failCount: 2, retries: 2, arguments: ['x', 7, {ok: true}]});
	assert.equal(value.attempts, 3);
	assert.deepEqual(value.value.arguments, ['x', 7, {ok: true}]);
});

test('makeRetriable preserves the dynamic this context', () => {
	const value = scenario('make-retriable', {prefix: 'kept', failCount: 0, retries: 0, arguments: []});
	assert.equal(value.value.prefix, 'kept');
});

test('successful null and false values are preserved', () => {
	assert.equal(scenario('run', {successValue: null}).value, null);
	assert.equal(scenario('run', {successValue: false}).value, false);
});

test('undefined callback options use their documented defaults', () => {
	const value = scenario('run', {failCount: 1, retries: 1, minTimeout: 0, successValue: 'done'});
	assert.equal(value.value, 'done');
	assert.deepEqual(value.events, ['input:1', 'input:2']);
});

test('maxTimeout accepts Infinity', () => {
	const value = scenario('validate', {field: 'maxTimeout', value: 'Infinity'});
	assert.equal(value.threw, false);
});

test('maxRetryTime accepts Infinity', () => {
	const value = scenario('validate', {field: 'maxRetryTime', value: 'Infinity'});
	assert.equal(value.threw, false);
});
