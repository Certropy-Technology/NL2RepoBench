import assert from 'node:assert/strict';
import {test} from 'node:test';
import {scenario} from './test_client.mjs';

const gated = values => values.map(value => ({value}));

test('package is scripts-free ESM with the documented exports', () => {
	const value = scenario('inventory');
	assert.deepEqual(value, {
		name: 'p-limit',
		version: '7.3.1',
		type: 'module',
		typesPresent: true,
		defaultCallable: true,
		limitFunctionCallable: true,
		runtimeDependencies: ['yocto-queue'],
		scriptNames: [],
		properties: {
			activeCount: 'number',
			pendingCount: 'number',
			clearQueue: 'function',
			concurrency: 'number',
			map: 'function',
		},
		installedName: 'p-limit',
	});
});

test('numeric concurrency accepts positive integers', () => {
	const value = scenario('batch', {concurrency: 2, tasks: gated(['a', 'b', 'c'])});
	assert.equal(value.maxActive, 2);
	assert.deepEqual(value.results.map(item => item.value), ['a', 'b', 'c']);
});

test('options object accepts concurrency and rejectOnClear', () => {
	const value = scenario('batch', {options: {concurrency: 2, rejectOnClear: true}, tasks: gated([1, 2, 3])});
	assert.equal(value.maxActive, 2);
	assert.deepEqual(value.results.map(item => item.value), [1, 2, 3]);
});

test('invalid concurrency and rejectOnClear values throw TypeError', () => {
	for (const value of [0, -1, 1.5, null, true, {}, {concurrency: 0}, {concurrency: 1, rejectOnClear: 'yes'}]) {
		const result = scenario('error', {value});
		assert.equal(result.threw, true);
		assert.equal(result.type, 'TypeError');
	}
});

test('positive infinity permits every bounded task to start', () => {
	const value = scenario('infinity', {tasks: gated([0, 1, 2, 3, 4, 5])});
	assert.equal(value.initial.activeCount, 6);
	assert.equal(value.initial.pendingCount, 0);
	assert.equal(value.maxActive, 6);
});

test('concurrency one serializes task starts', () => {
	const value = scenario('batch', {concurrency: 1, tasks: gated([0, 1, 2, 3])});
	assert.deepEqual(value.waves, [[0], [1], [2], [3]]);
	assert.equal(value.maxActive, 1);
});

test('concurrency three never exceeds the configured bound', () => {
	const value = scenario('batch', {concurrency: 3, tasks: gated([0, 1, 2, 3, 4, 5, 6])});
	assert.equal(value.maxActive, 3);
	assert.ok(value.waves.every(wave => wave.length <= 3));
});

test('results retain input order when completion order differs', () => {
	const value = scenario('batch', {concurrency: 3, reverse: true, tasks: gated(['first', 'second', 'third', 'fourth'])});
	assert.deepEqual(value.completions.slice(0, 3), [2, 1, 0]);
	assert.deepEqual(value.results.map(item => item.value), ['first', 'second', 'third', 'fourth']);
});

test('additional arguments are forwarded without wrapping', () => {
	const value = scenario('batch', {
		concurrency: 1,
		tasks: [{echoArguments: true, args: ['x', 7, {ok: true}]}],
	});
	assert.deepEqual(value.results[0], {status: 'fulfilled', value: ['x', 7, {ok: true}]});
});

test('non-promise return values resolve normally', () => {
	const value = scenario('batch', {concurrency: 1, tasks: [{kind: 'sync-value', value: null}, {kind: 'sync-value', value: 4}]});
	assert.deepEqual(value.results, [{status: 'fulfilled', value: null}, {status: 'fulfilled', value: 4}]);
});

test('a synchronous throw rejects its promise and the queue continues', () => {
	const value = scenario('batch', {concurrency: 1, tasks: [{kind: 'sync-throw', message: 'sync boom'}, {value: 'after'}]});
	assert.equal(value.results[0].status, 'rejected');
	assert.match(value.results[0].reason.message, /sync boom/);
	assert.deepEqual(value.results[1], {status: 'fulfilled', value: 'after'});
});

test('an asynchronous rejection is preserved and the queue continues', () => {
	const value = scenario('batch', {concurrency: 1, tasks: [{kind: 'reject', message: 'async boom'}, {value: 'after'}]});
	assert.equal(value.results[0].status, 'rejected');
	assert.match(value.results[0].reason.message, /async boom/);
	assert.deepEqual(value.results[1], {status: 'fulfilled', value: 'after'});
});

test('limited functions always begin asynchronously', () => {
	assert.deepEqual(scenario('runs-async'), [1, 2]);
});

test('active and pending counts track queued work and return to zero', () => {
	const value = scenario('batch', {concurrency: 2, tasks: gated([0, 1, 2, 3, 4])});
	assert.deepEqual(value.initial, {activeCount: 2, pendingCount: 3});
	assert.deepEqual(value.final, {activeCount: 0, pendingCount: 0});
});

test('clearQueue discards pending work without cancelling active work', () => {
	const value = scenario('clear', {rejectOnClear: false});
	assert.deepEqual(value.before, {activeCount: 1, pendingCount: 3});
	assert.deepEqual(value.afterClear, {activeCount: 1, pendingCount: 0});
	assert.equal(value.activeFinished, true);
	assert.equal(value.activeValue, 'active');
});

test('rejectOnClear rejects pending work with AbortError', () => {
	const value = scenario('clear', {rejectOnClear: true});
	assert.deepEqual(value.pendingResults.map(item => item.status), ['rejected', 'rejected', 'rejected']);
	assert.deepEqual(value.pendingResults.map(item => item.reason.name), ['AbortError', 'AbortError', 'AbortError']);
});

test('map preserves array order and supplies indexes', () => {
	const value = scenario('map', {concurrency: 3, iterable: 'array', values: [10, 10, 10, 10], formula: 'index-sum'});
	assert.deepEqual(value.result, [10, 11, 12, 13]);
	assert.ok(value.maxActive <= 3);
});

test('map accepts Set iterables', () => {
	const value = scenario('map', {concurrency: 2, iterable: 'set', values: [1, 2, 3, 4], formula: 'double'});
	assert.deepEqual(value.result, [2, 4, 6, 8]);
});

test('map accepts iterator objects', () => {
	const value = scenario('map', {concurrency: 2, iterable: 'iterator', values: [2, 4, 6], formula: 'double'});
	assert.deepEqual(value.result, [4, 8, 12]);
});

test('map remains callable when detached from its limiter', () => {
	const value = scenario('map', {concurrency: 1, iterable: 'array', values: [3, 4], formula: 'double', detached: true});
	assert.deepEqual(value.result, [6, 8]);
	assert.equal(value.maxActive, 1);
});

test('raising concurrency starts additional queued work', () => {
	const value = scenario('set-concurrency', {start: 2, next: 4, tasks: gated([0, 1, 2, 3, 4, 5])});
	assert.deepEqual(value.before, {activeCount: 2, pendingCount: 4});
	assert.deepEqual(value.after, {activeCount: 4, pendingCount: 2});
});

test('lowering concurrency constrains later waves without cancelling active work', () => {
	const value = scenario('set-concurrency', {start: 4, next: 2, tasks: gated([0, 1, 2, 3, 4, 5, 6, 7])});
	assert.deepEqual(value.before, {activeCount: 4, pendingCount: 4});
	assert.deepEqual(value.after, {activeCount: 4, pendingCount: 4});
	assert.ok(value.run.waves.slice(1).every(wave => wave.length <= 2));
});

test('limitFunction forwards arguments and limits calls independently', () => {
	const value = scenario('limit-function', {concurrency: 2, values: ['a', 'b', 'c', 'd']});
	assert.equal(value.maxActive, 2);
	assert.deepEqual(value.results, [['a', 0], ['b', 1], ['c', 2], ['d', 3]]);
});

test('async local context is preserved for every queued task', () => {
	assert.deepEqual(scenario('context'), Array.from({length: 8}, (_, id) => [id, id]));
});
