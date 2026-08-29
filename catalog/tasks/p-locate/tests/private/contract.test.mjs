import assert from 'node:assert/strict';
import {test} from 'node:test';
import {request} from './test_client.mjs';

function value(scenario) {
  const response = request(scenario);
  assert.equal(response.ok, true, response.message);
  return response.value;
}

function error(scenario) {
  const response = request(scenario);
  assert.equal(response.ok, false);
  return response;
}

test('package root exposes the frozen ESM package contract', () => {
  assert.deepEqual(value('inventory'), {
    packageName: 'p-locate',
    packageVersion: '7.0.0',
    moduleType: 'module',
    runtimeEntry: './index.js',
    runtimeEntryPresent: true,
    declarationEntry: './index.d.ts',
    declarationEntryPresent: true,
    exportNames: ['default'],
    pLimitDependency: '7.3.1',
    scriptNames: [],
    devDependencyNames: [],
  });
});

test('finds the first matching ordinary value', () => {
  assert.deepEqual(value('basic'), {kind: 'value', value: 2});
});

test('awaits promise values before invoking the tester', () => {
  assert.deepEqual(value('promised-input'), {kind: 'value', value: {id: 2}});
});

test('returns undefined when no value matches', () => {
  assert.deepEqual(value('no-match'), {kind: 'undefined'});
});

test('returns undefined for an empty iterable', () => {
  assert.deepEqual(value('empty'), {kind: 'undefined'});
});

test('accepts Set inputs', () => {
  assert.deepEqual(value('set-input'), {kind: 'value', value: 'b'});
});

test('accepts generator inputs', () => {
  assert.deepEqual(value('generator-input'), {kind: 'value', value: 3});
});

test('accepts a synchronous tester', () => {
  assert.deepEqual(value('sync-tester'), {kind: 'value', value: 1});
});

test('awaits an asynchronous tester', () => {
  assert.deepEqual(value('async-tester'), {kind: 'value', value: 3});
});

test('adopts a PromiseLike tester result', () => {
  assert.deepEqual(value('thenable-tester'), {kind: 'value', value: 2});
});

test('matches only the boolean true', () => {
  assert.deepEqual(value('strict-true'), {kind: 'undefined'});
});

test('tester receives one resolved argument', () => {
  assert.deepEqual(value('tester-arguments'), {
    result: {id: 7},
    argumentCount: 1,
    received: {id: 7},
  });
});

test('returns the matching object value', () => {
  assert.deepEqual(value('object-result'), {
    kind: 'value',
    value: {id: 2, nested: ['x', true]},
  });
});

test('preserves input order by default', () => {
  assert.deepEqual(value('preserve-order'), {id: 'first'});
});

test('preserveOrder false selects the first completed match', () => {
  assert.deepEqual(value('completion-order'), {id: 'second'});
});

test('concurrency one serializes tester calls', () => {
  assert.deepEqual(value('concurrency-one'), {
    result: {kind: 'undefined'},
    maxActive: 1,
    started: [1, 2, 3, 4, 5, 6],
  });
});

test('finite concurrency bounds active tester calls', () => {
  assert.deepEqual(value('concurrency-two'), {
    result: {kind: 'undefined'},
    maxActive: 2,
    started: [1, 2, 3, 4, 5, 6],
  });
});

test('default concurrency allows every bounded tester to start', () => {
  assert.deepEqual(value('concurrency-default'), {
    result: {kind: 'undefined'},
    maxActive: 6,
    started: [1, 2, 3, 4, 5, 6],
  });
});

test('positive infinity is an accepted explicit concurrency', () => {
  assert.deepEqual(value('concurrency-infinity'), {
    result: {kind: 'undefined'},
    maxActive: 4,
    started: [1, 2, 3, 4],
  });
});

test('zero concurrency rejects', () => {
  assert.equal(error('invalid-zero').error_type, 'TypeError');
});

test('fractional concurrency rejects', () => {
  assert.equal(error('invalid-fraction').error_type, 'TypeError');
});

test('a synchronous tester exception rejects unchanged', () => {
  const response = error('tester-throw');
  assert.equal(response.error_type, 'SyntaxError');
  assert.equal(response.message, 'tester threw');
});

test('an asynchronous tester rejection rejects unchanged', () => {
  const response = error('tester-reject');
  assert.equal(response.error_type, 'URIError');
  assert.equal(response.message, 'tester rejected');
});

test('a rejected input promise rejects unchanged', () => {
  const response = error('input-reject');
  assert.equal(response.error_type, 'EvalError');
  assert.equal(response.message, 'input rejected');
});

test('a synchronous iterator exception rejects unchanged', () => {
  const response = error('iterator-throw');
  assert.equal(response.error_type, 'ReferenceError');
  assert.equal(response.message, 'iterator failed');
});

test('completion-order mode can return before a later failure', () => {
  assert.deepEqual(value('race-match-first'), {kind: 'value', value: {kind: 'match', delay: 1}});
});

test('completion-order mode propagates the first failure', () => {
  const response = error('race-error-first');
  assert.equal(response.error_type, 'RangeError');
  assert.equal(response.message, 'race failure');
});

test('async iterable returns its first match', () => {
  assert.deepEqual(value('async-basic'), {kind: 'value', value: 2});
});

test('async iterable awaits yielded promises', () => {
  assert.deepEqual(value('async-promised-input'), {kind: 'value', value: 2});
});

test('async iterable returns undefined when nothing matches', () => {
  assert.deepEqual(value('async-no-match'), {kind: 'undefined'});
});

test('empty async iterable returns undefined', () => {
  assert.deepEqual(value('async-empty'), {kind: 'undefined'});
});

test('async iterable awaits an asynchronous tester', () => {
  assert.deepEqual(value('async-tester'), {kind: 'value', value: 3});
});

test('async iterable also requires strict true', () => {
  assert.deepEqual(value('async-strict-true'), {kind: 'undefined'});
});

test('async iterable stops requesting values after a match', () => {
  assert.deepEqual(value('async-stops'), {result: 2, advances: 1});
});

test('async iterable propagates tester rejection', () => {
  const response = error('async-tester-reject');
  assert.equal(response.error_type, 'AggregateError');
  assert.equal(response.message, 'async tester failed');
});

test('async iterable propagates iterator rejection', () => {
  const response = error('async-iterator-reject');
  assert.equal(response.error_type, 'Error');
  assert.equal(response.message, 'async iterator failed');
});

test('async iterable is serial and ignores sync-only options', () => {
  assert.deepEqual(value('async-serial-options-ignored'), {
    result: {kind: 'undefined'},
    maxActive: 1,
    started: [1, 2, 3, 4, 5],
  });
});

test('async iterator takes precedence when both protocols exist', () => {
  assert.deepEqual(value('dual-iterable'), {kind: 'value', value: 'async-2'});
});
