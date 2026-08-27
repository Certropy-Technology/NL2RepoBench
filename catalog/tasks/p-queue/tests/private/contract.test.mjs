import assert from 'node:assert/strict';
import {test} from 'node:test';
import {call} from './test_client.mjs';

const schedule = payload => call('schedule', payload);
const validation = (target, value, field) => call('validation', {target, value, field});

test('package root is scripts-free ESM with exact runtime dependencies', () => {
	assert.deepEqual(call('inventory'), {
		name: 'p-queue',
		version: '9.3.3',
		type: 'module',
		dependencies: {eventemitter3: '5.0.4', 'p-timeout': '7.0.1'},
		scriptNames: [],
		runtimeFile: true,
		declarationFile: true,
		defaultClass: true,
		priorityQueueClass: true,
		timeoutErrorClass: true,
	});
});

test('default queue starts empty and active', () => {
	assert.deepEqual(call('construct'), {
		concurrency: null,
		timeout: null,
		size: 0,
		pending: 0,
		isPaused: false,
		isRateLimited: false,
		isSaturated: false,
		runningTasks: [],
	});
});

test('constructor exposes finite concurrency, timeout, and paused state', () => {
	const value = call('construct', {options: {concurrency: 3, timeout: 250, autoStart: false}});
	assert.equal(value.concurrency, 3);
	assert.equal(value.timeout, 250);
	assert.equal(value.isPaused, true);
});

test('add resolves synchronous and asynchronous task values', () => {
	const value = schedule({
		tasks: [
			{id: 'sync', sync: true, value: {kind: 'sync'}},
			{id: 'async', delayMs: 5, value: ['async', 2]},
		],
	});
	assert.deepEqual(value.settled, [
		{status: 'fulfilled', value: {kind: 'sync'}},
		{status: 'fulfilled', value: ['async', 2]},
	]);
	assert.deepEqual(value.final, {
		size: 0, pending: 0, isPaused: false, isSaturated: false,
		isRateLimited: false, concurrency: null,
	});
});

test('concurrency one serializes task starts and completions', () => {
	const value = schedule({
		options: {concurrency: 1},
		tasks: [
			{id: 'a', delayMs: 20},
			{id: 'b', delayMs: 5},
			{id: 'c', delayMs: 0},
		],
	});
	assert.equal(value.maxActive, 1);
	assert.deepEqual(value.started, ['a', 'b', 'c']);
	assert.deepEqual(value.completed, ['a', 'b', 'c']);
});

test('finite concurrency runs no more than the configured number', () => {
	const value = schedule({
		options: {concurrency: 2},
		tasks: [
			{id: 'a', delayMs: 30},
			{id: 'b', delayMs: 20},
			{id: 'c', delayMs: 5},
			{id: 'd', delayMs: 0},
		],
	});
	assert.equal(value.maxActive, 2);
	assert.deepEqual(value.started, ['a', 'b', 'c', 'd']);
	assert.deepEqual(value.completed, ['b', 'c', 'd', 'a']);
});

test('paused queues report queued size and start on demand', () => {
	const value = schedule({
		options: {concurrency: 1, autoStart: false},
		tasks: [{id: 'a'}, {id: 'b'}],
		start: true,
	});
	assert.deepEqual(value.afterAdd, {
		size: 2,
		pending: 0,
		isPaused: true,
		isSaturated: false,
		runningTasks: [],
		sizeByPriority: null,
	});
	assert.deepEqual(value.started, ['a', 'b']);
	assert.equal(value.final.isPaused, false);
});

test('higher priority tasks run first in a paused queue', () => {
	const value = schedule({
		options: {concurrency: 1, autoStart: false},
		tasks: [
			{id: 'low', priority: -1},
			{id: 'high-a', priority: 5},
			{id: 'normal', priority: 0},
			{id: 'high-b', priority: 5},
		],
		start: true,
	});
	assert.deepEqual(value.started, ['high-a', 'high-b', 'normal', 'low']);
});

test('setPriority changes a queued task position', () => {
	const value = schedule({
		options: {concurrency: 1, autoStart: false},
		tasks: [{id: 'a'}, {id: 'b'}, {id: 'c'}],
		priorityUpdates: [{id: 'c', priority: 10}],
		start: true,
	});
	assert.deepEqual(value.started, ['c', 'a', 'b']);
});

test('runtime concurrency changes are applied before start', () => {
	const value = schedule({
		options: {concurrency: 1, autoStart: false},
		tasks: [
			{id: 'a', delayMs: 20},
			{id: 'b', delayMs: 20},
			{id: 'c', delayMs: 0},
		],
		concurrency: 2,
		start: true,
	});
	assert.equal(value.maxActive, 2);
	assert.equal(value.final.concurrency, 2);
});

test('sizeBy counts queued tasks at one priority', () => {
	const value = schedule({
		options: {autoStart: false},
		tasks: [
			{id: 'a', priority: 2},
			{id: 'b', priority: 1},
			{id: 'c', priority: 2},
		],
		sizeByPriority: 2,
		start: true,
	});
	assert.equal(value.afterAdd.sizeByPriority, 2);
});

test('runningTasks exposes active task identifiers and priority', () => {
	const value = schedule({
		options: {concurrency: 1},
		tasks: [{id: 'running', priority: 4, delayMs: 20}, {id: 'queued'}],
	});
	assert.equal(value.afterAdd.runningTasks.length, 1);
	assert.equal(value.afterAdd.runningTasks[0].id, 'running');
	assert.equal(value.afterAdd.runningTasks[0].priority, 4);
	assert.equal(typeof value.afterAdd.runningTasks[0].startTime, 'number');
});

test('isSaturated is true when all slots are occupied with backlog', () => {
	const value = schedule({
		options: {concurrency: 1},
		tasks: [{id: 'running', delayMs: 20}, {id: 'queued'}],
	});
	assert.equal(value.afterAdd.pending, 1);
	assert.equal(value.afterAdd.size, 1);
	assert.equal(value.afterAdd.isSaturated, true);
});

test('task rejection rejects add and emits error', () => {
	const value = schedule({tasks: [{id: 'bad', sync: true, reject: true}]});
	assert.deepEqual(value.settled, [{
		status: 'rejected', exceptionType: 'Error', message: 'rejected:bad',
	}]);
	assert.ok(value.events.includes('error'));
});

test('completed tasks emit completed and queue lifecycle events', () => {
	const value = schedule({tasks: [{id: 'a'}, {id: 'b'}]});
	assert.equal(value.events.filter(name => name === 'add').length, 2);
	assert.equal(value.events.filter(name => name === 'active').length, 2);
	assert.equal(value.events.filter(name => name === 'completed').length, 2);
	assert.ok(value.events.includes('empty'));
	assert.ok(value.events.includes('idle'));
	assert.ok(value.events.includes('pendingZero'));
});

test('addAll preserves input result order', () => {
	assert.deepEqual(call('add-all', {
		options: {concurrency: 2},
		tasks: [
			{id: 'a', value: 3},
			{id: 'b', value: 1},
			{id: 'c', value: 2},
		],
	}), {started: ['a', 'b', 'c'], values: [3, 1, 2], size: 0, pending: 0});
});

test('default timeout rejects a slow task with TimeoutError', () => {
	const value = schedule({
		options: {timeout: 20},
		tasks: [{id: 'slow', delayMs: 80}],
	});
	assert.equal(value.settled[0].status, 'rejected');
	assert.equal(value.settled[0].exceptionType, 'TimeoutError');
	assert.match(value.settled[0].message, /timed out after 20ms/);
});

test('per-task timeout overrides the queue default', () => {
	const value = schedule({
		options: {timeout: 200},
		tasks: [{id: 'slow', delayMs: 80, timeout: 20}],
	});
	assert.equal(value.settled[0].exceptionType, 'TimeoutError');
});

test('named TimeoutError matches timeout failures', () => {
	const value = call('timeout-error');
	assert.equal(value.threw, true);
	assert.equal(value.isTimeoutError, true);
	assert.equal(value.exceptionType, 'TimeoutError');
	assert.match(value.message, /queue has 1 running, 0 waiting/);
});

test('onEmpty, onIdle, onPendingZero, and onSizeLessThan resolve', () => {
	const value = call('waiters', {limit: 2});
	assert.deepEqual(value.values, ['first', 'second']);
	assert.deepEqual(new Set(value.resolutions), new Set(['empty', 'idle', 'pendingZero', 'sizeLessThan']));
	assert.equal(value.resolutions.at(-1), 'idle');
});

test('waiters react after a paused queue starts', () => {
	const value = call('waiters', {paused: true, limit: 1});
	assert.deepEqual(value.before, {size: 2, pending: 0, isPaused: true});
	assert.deepEqual(new Set(value.resolutions), new Set(['empty', 'idle', 'pendingZero', 'sizeLessThan']));
	assert.deepEqual(value.final, {size: 0, pending: 0});
});

test('clear removes every paused task without starting it', () => {
	const value = call('clear-paused');
	assert.deepEqual(value.before, {size: 3, pending: 0, isPaused: true});
	assert.deepEqual(value.after, {size: 0, pending: 0, isPaused: true});
	assert.deepEqual(value.ran, []);
	assert.ok(value.events.includes('empty'));
});

test('clear preserves a running task and discards backlog', () => {
	const value = call('clear-running');
	assert.deepEqual(value.before, {size: 1, pending: 1});
	assert.deepEqual(value.afterClear, {size: 0, pending: 1});
	assert.deepEqual(value.ran, ['running']);
	assert.equal(value.value, 'done');
	assert.deepEqual(value.final, {size: 0, pending: 0});
});

test('aborting a queued task removes it and preserves running work', () => {
	const value = call('abort-queued');
	assert.equal(value.secondResult.status, 'rejected');
	assert.equal(value.secondResult.message, 'queued-abort');
	assert.deepEqual(value.afterAbort, {size: 0, pending: 1});
	assert.equal(value.firstValue, 'first');
	assert.deepEqual(value.final, {size: 0, pending: 0});
});

test('running tasks receive the supplied AbortSignal', () => {
	const value = call('abort-running');
	assert.equal(value.receivedSignal, true);
	assert.equal(value.result.status, 'rejected');
	assert.equal(value.result.message, 'running-abort');
	assert.deepEqual(value.final, {size: 0, pending: 0});
});

test('fixed-window intervalCap releases work in batches', () => {
	const value = call('rate-limit', {interval: 100, intervalCap: 2, count: 4});
	assert.deepEqual(value.values, [0, 1, 2, 3]);
	assert.equal(value.offsets.length, 4);
	assert.ok(value.offsets[1] < 70, JSON.stringify(value.offsets));
	assert.ok(value.offsets[2] >= 70, JSON.stringify(value.offsets));
	assert.ok(value.events.includes('rateLimit'));
	assert.ok(value.events.includes('rateLimitCleared'));
});

test('intervalCap one spaces task starts', () => {
	const value = call('rate-limit', {interval: 80, intervalCap: 1, count: 3});
	assert.ok(value.offsets[1] - value.offsets[0] >= 55, JSON.stringify(value.offsets));
	assert.ok(value.offsets[2] - value.offsets[1] >= 55, JSON.stringify(value.offsets));
});

test('strict mode applies a sliding-window start limit', () => {
	const value = call('rate-limit', {interval: 90, intervalCap: 2, count: 4, strict: true});
	assert.ok(value.offsets[2] - value.offsets[0] >= 60, JSON.stringify(value.offsets));
	assert.deepEqual(value.values, [0, 1, 2, 3]);
});

test('rate limit state clears when the queue becomes idle', () => {
	const value = call('rate-limit', {interval: 60, intervalCap: 1, count: 2});
	assert.equal(value.isRateLimited, false);
	assert.equal(value.events.filter(name => name === 'rateLimit').length >= 1, true);
});

test('PriorityQueue dequeues high priority before low priority', () => {
	const value = call('priority-queue', {actions: [
		{op: 'enqueue', label: 'low', priority: -1},
		{op: 'enqueue', label: 'high', priority: 2},
		{op: 'enqueue', label: 'normal', priority: 0},
		{op: 'dequeue'}, {op: 'dequeue'}, {op: 'dequeue'},
	]});
	assert.deepEqual(value.output.filter(item => item.op === 'dequeue').map(item => item.value), ['high', 'normal', 'low']);
});

test('PriorityQueue preserves insertion order for equal priorities', () => {
	const value = call('priority-queue', {actions: [
		{op: 'enqueue', label: 'a', priority: 1},
		{op: 'enqueue', label: 'b', priority: 1},
		{op: 'enqueue', label: 'c', priority: 1},
		{op: 'dequeue'}, {op: 'dequeue'}, {op: 'dequeue'},
	]});
	assert.deepEqual(value.output.slice(-3).map(item => item.value), ['a', 'b', 'c']);
});

test('PriorityQueue setPriority reorders one live item', () => {
	const value = call('priority-queue', {actions: [
		{op: 'enqueue', label: 'a', priority: 0, id: 'a'},
		{op: 'enqueue', label: 'b', priority: 0, id: 'b'},
		{op: 'setPriority', id: 'b', priority: 3},
		{op: 'dequeue'}, {op: 'dequeue'},
	]});
	assert.deepEqual(value.output.slice(-2).map(item => item.value), ['b', 'a']);
});

test('PriorityQueue filter returns live functions at one priority', () => {
	const value = call('priority-queue', {actions: [
		{op: 'enqueue', label: 'a', priority: 2},
		{op: 'enqueue', label: 'b', priority: 1},
		{op: 'enqueue', label: 'c', priority: 2},
		{op: 'filter', priority: 2},
	]});
	assert.deepEqual(value.output.at(-1), {op: 'filter', values: ['a', 'c']});
});

test('PriorityQueue remove by id drops the matching item', () => {
	const value = call('priority-queue', {actions: [
		{op: 'enqueue', label: 'a', priority: 1, id: 'a'},
		{op: 'enqueue', label: 'b', priority: 1, id: 'b'},
		{op: 'remove', value: 'a'},
		{op: 'dequeue'},
	]});
	assert.equal(value.output.at(-1).value, 'b');
});

test('PriorityQueue remove by function drops the matching item', () => {
	const value = call('priority-queue', {actions: [
		{op: 'enqueue', label: 'a', priority: 1},
		{op: 'enqueue', label: 'b', priority: 1},
		{op: 'remove', value: 'b', byRun: true},
		{op: 'dequeue'},
	]});
	assert.equal(value.output.at(-1).value, 'a');
});

test('PriorityQueue returns undefined as null when empty', () => {
	const value = call('priority-queue', {actions: [{op: 'dequeue'}]});
	assert.deepEqual(value.output, [{op: 'dequeue', value: null, size: 0}]);
});

test('constructor rejects zero concurrency', () => {
	const value = validation('constructor', 0, 'concurrency');
	assert.equal(value.exceptionType, 'TypeError');
	assert.match(value.message, /concurrency.*number from 1 and up/);
});

test('concurrency setter rejects non-positive values', () => {
	for (const invalid of [0, -1, '$NaN']) {
		const value = validation('concurrency-setter', invalid);
		assert.equal(value.exceptionType, 'TypeError');
	}
});

test('constructor rejects invalid intervalCap', () => {
	for (const invalid of [0, -1]) {
		const value = validation('constructor', invalid, 'intervalCap');
		assert.equal(value.exceptionType, 'TypeError');
		assert.match(value.message, /intervalCap/);
	}
});

test('constructor rejects non-finite or negative interval', () => {
	for (const invalid of [-1, '$Infinity', '$NaN']) {
		const value = validation('constructor', invalid, 'interval');
		assert.equal(value.exceptionType, 'TypeError');
		assert.match(value.message, /interval/);
	}
});

test('strict mode requires a non-zero interval', () => {
	const value = validation('strict-zero');
	assert.equal(value.exceptionType, 'TypeError');
	assert.match(value.message, /requires a non-zero `interval`/);
});

test('strict mode requires a finite intervalCap', () => {
	const value = validation('strict-infinite-cap');
	assert.equal(value.exceptionType, 'TypeError');
	assert.match(value.message, /requires a finite `intervalCap`/);
});

test('constructor rejects invalid default timeout', () => {
	for (const invalid of [0, -1, '$Infinity']) {
		const value = validation('constructor', invalid, 'timeout');
		assert.equal(value.exceptionType, 'TypeError');
		assert.match(value.message, /timeout.*positive finite number/);
	}
});

test('add rejects invalid per-task timeout', () => {
	for (const invalid of [0, -1, '$NaN']) {
		const value = validation('add-timeout', invalid);
		assert.equal(value.exceptionType, 'TypeError');
		assert.match(value.message, /timeout.*positive finite number/);
	}
});

test('setPriority rejects non-finite priority', () => {
	for (const invalid of ['$Infinity', '$NaN']) {
		const value = validation('set-priority', invalid);
		assert.equal(value.exceptionType, 'TypeError');
		assert.match(value.message, /priority.*finite number/);
	}
});

test('setPriority rejects an unknown task id', () => {
	const value = validation('missing-priority-id');
	assert.equal(value.exceptionType, 'ReferenceError');
	assert.match(value.message, /No promise function with the id "missing"/);
});
