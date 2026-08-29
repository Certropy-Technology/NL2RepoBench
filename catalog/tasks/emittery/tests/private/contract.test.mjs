import assert from 'node:assert/strict';
import test from 'node:test';

const {callCandidate} = await import(process.env.NODE_TEST_CLIENT ?? '/tests/private/test_client.mjs');

test('package metadata and declaration export', () => {
	assert.deepEqual(callCandidate('metadata'), {
		name: 'emittery',
		version: '2.0.0',
		type: 'module',
		defaultExport: './index.js',
		typesExport: './index.d.ts',
		hasTypes: true,
		dependencies: [],
		hasScripts: false,
	});
});

test('class exposes the complete bound method surface', () => {
	const result = callCandidate('method-surface');
	assert.deepEqual(result.methods, [
		'anyEvent', 'bindMethods', 'clearListeners', 'emit', 'emitSerial', 'events', 'init',
		'listenerCount', 'logIfDebugEnabled', 'off', 'offAny', 'on', 'onAny', 'once',
	]);
	assert.equal(result.boundOwnMethods, true);
	assert.deepEqual(result.enumerableMethods, []);
	assert.equal(result.listenerAdded, 'symbol');
	assert.equal(result.listenerRemoved, 'symbol');
	assert.equal(result.debugEnabled, false);
});

test('on emits data and unsubscribe removes the listener', () => {
	assert.deepEqual(callCandidate('on-basic'), {
		seen: [{name: 'alpha', data: {value: 1}}],
		count: 0,
	});
});

test('on accepts multiple event names', () => {
	assert.deepEqual(callCandidate('on-multiple'), [
		{name: 'alpha', data: 1},
		{name: 'beta', data: 2},
	]);
});

test('on deduplicates the same listener', () => {
	assert.deepEqual(callCandidate('on-dedupe'), {calls: 1, count: 0});
});

test('number and symbol event names are supported', () => {
	assert.deepEqual(callCandidate('event-name-types'), [
		{name: 7, data: 'number'},
		{name: 'Symbol(token)', data: 'symbol'},
	]);
});

test('event names and listeners are validated', () => {
	const result = callCandidate('listener-validation');
	assert.equal(result.badName.name, 'TypeError');
	assert.match(result.badName.message, /eventName/);
	assert.equal(result.badListener.name, 'TypeError');
	assert.equal(result.badOffListener.name, 'TypeError');
});

test('dataless and explicit undefined events have distinct shapes', () => {
	const result = callCandidate('data-shape');
	assert.deepEqual(result, [
		{hasData: false, event: {name: 'alpha'}},
		{hasData: true, event: {name: 'alpha'}},
	]);
});

test('listeners receive isolated event objects', () => {
	assert.deepEqual(callCandidate('isolated-events'), ['first', 'isolated']);
});

test('on subscriptions honor AbortSignal', () => {
	assert.deepEqual(callCandidate('on-abort'), {calls: 0, count: 0});
});

test('subscription and init removers implement Disposable', () => {
	assert.deepEqual(callCandidate('disposable'), {calls: 0, same: true, initDisposable: true});
});

test('emit starts listeners concurrently and awaits completion', () => {
	assert.deepEqual(callCandidate('emit-concurrent'), {
		beforeRelease: ['a-start', 'b-start'],
		order: ['a-start', 'b-start', 'a-end', 'b-end'],
	});
});

test('emit runs all listeners and aggregates errors', () => {
	const result = callCandidate('emit-errors');
	assert.deepEqual(result.calls, ['sync', 'async']);
	assert.equal(result.error.name, 'AggregateError');
	assert.deepEqual(result.errors, [
		{name: 'Error', message: 'first'},
		{name: 'TypeError', message: 'second'},
	]);
});

test('emitSerial awaits listeners in registration order', () => {
	assert.deepEqual(callCandidate('serial-order'), ['a-start', 'a-end', 'b']);
});

test('emitSerial stops at the first error', () => {
	const result = callCandidate('serial-error');
	assert.deepEqual(result.callsAfter, ['first']);
	assert.deepEqual(result.error, {name: 'RangeError', message: 'stop'});
});

test('onAny observes every ordinary event and unsubscribes', () => {
	assert.deepEqual(callCandidate('any-listener'), {
		seen: [{name: 'alpha', data: 1}, {name: 2, data: 'two'}],
		count: 0,
	});
});

test('onAny honors AbortSignal', () => {
	assert.deepEqual(callCandidate('any-abort'), {calls: 0, count: 0});
});

test('listenerCount includes direct, any, and iterator listeners', () => {
	assert.deepEqual(callCandidate('listener-count'), {alpha: 3, beta: 2, both: 5, all: 4});
});

test('once resolves one event and removes itself', () => {
	assert.deepEqual(callCandidate('once-basic'), {event: {name: 'alpha', data: {value: 1}}, count: 0});
});

test('once accepts multiple names and removes every subscription', () => {
	assert.deepEqual(callCandidate('once-multiple'), {
		event: {name: 'beta', data: 2},
		alpha: 0,
		beta: 0,
	});
});

test('once predicates keep listening until a match', () => {
	assert.deepEqual(callCandidate('once-predicate'), {
		afterFirst: 1,
		event: {name: 'alpha', data: 3},
		afterMatch: 0,
	});
});

test('once validates direct and option predicates', () => {
	const result = callCandidate('once-validation');
	assert.equal(result.badPredicate.name, 'TypeError');
	assert.equal(result.badOptionPredicate.name, 'TypeError');
});

test('once promises expose idempotent cancellation', () => {
	assert.deepEqual(callCandidate('once-cancel'), {hasOff: true, count: 0});
});

test('once rejects with the abort reason and cleans up', () => {
	assert.deepEqual(callCandidate('once-abort'), {
		error: {name: 'Error', message: 'cancelled'},
		count: 0,
	});
});

test('events buffers event objects in order', () => {
	assert.deepEqual(callCandidate('events-buffer'), {
		first: {done: false, value: {name: 'alpha', data: 1}},
		second: {done: false, value: {name: 'alpha', data: 2}},
		count: 0,
	});
});

test('events accepts multiple event names', () => {
	assert.deepEqual(callCandidate('events-multiple'), {
		done: false,
		value: {name: 'beta', data: 2},
	});
});

test('events return awaits its value and implements AsyncDisposable', () => {
	assert.deepEqual(callCandidate('events-return'), {
		hasDispose: true,
		returned: {done: true, value: 'done'},
		next: {done: true},
		count: 0,
	});
});

test('events honors AbortSignal and finishes', () => {
	assert.deepEqual(callCandidate('events-abort'), {next: {done: true}, count: 0});
});

test('anyEvent buffers named and dataless events', () => {
	assert.deepEqual(callCandidate('any-event'), {
		first: {done: false, value: {name: 'alpha', data: 1}},
		second: {done: false, value: {name: 'beta'}},
		count: 0,
	});
});

test('anyEvent honors AbortSignal and finishes', () => {
	assert.deepEqual(callCandidate('any-event-abort'), {next: {done: true}, count: 0});
});

test('clearListeners can clear selected event names', () => {
	assert.deepEqual(callCandidate('clear-selected'), {calls: ['beta'], alpha: 0, beta: 1});
});

test('clearListeners without names clears listeners and iterators', () => {
	assert.deepEqual(callCandidate('clear-all'), {count: 0, iterator: {done: true}});
});

test('bindMethods binds selected methods as non-enumerable properties', () => {
	assert.deepEqual(callCandidate('bind-methods'), {calls: 1, count: 1, enumerable: []});
});

test('bindMethods validates target, names, and conflicts', () => {
	const result = callCandidate('bind-validation');
	assert.equal(result.badTarget.name, 'TypeError');
	assert.equal(result.badNames.name, 'TypeError');
	assert.equal(result.unknown.name, 'Error');
	assert.equal(result.conflict.name, 'Error');
});

test('mixin lazily installs an emitter and selected methods', () => {
	assert.deepEqual(callCandidate('mixin'), {
		sameClass: true,
		before: false,
		after: true,
		calls: 1,
		count: 1,
		enumerable: [],
	});
});

test('mixin validates targets, method lists, and conflicts', () => {
	const result = callCandidate('mixin-validation');
	assert.equal(result.badTarget.name, 'TypeError');
	assert.equal(result.badNames.name, 'TypeError');
	assert.equal(result.unknown.name, 'Error');
	assert.equal(result.conflict.name, 'Error');
});

test('listenerAdded and listenerRemoved expose listener metadata', () => {
	assert.deepEqual(callCandidate('meta-events'), {
		added: [{eventName: 'alpha', listenerType: 'function'}],
		removed: [{eventName: 'alpha', listenerType: 'function'}],
	});
});

test('reserved meta events cannot be emitted by user code', () => {
	const result = callCandidate('meta-blocked');
	assert.equal(result.emit.name, 'TypeError');
	assert.equal(result.serial.name, 'TypeError');
});

test('init runs on first listener and deinit on last removal', () => {
	assert.deepEqual(callCandidate('init-lifecycle'), {
		beforeLast: ['init'],
		order: ['init', 'deinit'],
	});
});

test('init activates immediately for existing listeners and removal is idempotent', () => {
	assert.deepEqual(callCandidate('init-immediate'), ['init', 'deinit']);
});

test('clearListeners invokes deinit for each active lifecycle', () => {
	assert.deepEqual(callCandidate('init-clear'), {
		order: ['init-alpha', 'init-beta', 'deinit-alpha', 'deinit-beta'],
		count: 0,
	});
});

test('init validates duplicate, callback, and meta-event registrations', () => {
	const result = callCandidate('init-validation');
	assert.equal(result.duplicate.name, 'Error');
	assert.equal(result.badFunction.name, 'TypeError');
	assert.equal(result.meta.name, 'TypeError');
});

test('init failure rolls back the triggering listener', () => {
	assert.deepEqual(callCandidate('init-rollback'), {
		error: {name: 'Error', message: 'init failed'},
		count: 0,
	});
});

test('custom debug logger receives deterministic operation records', () => {
	assert.deepEqual(callCandidate('debug'), [
		{type: 'subscribe', name: 'unit', eventName: 'alpha'},
		{type: 'emit', name: 'unit', eventName: 'alpha', data: 1},
		{type: 'unsubscribe', name: 'unit', eventName: 'alpha'},
		{type: 'clear', name: 'unit', eventName: 'alpha'},
	]);
});
