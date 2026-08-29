import assert from 'node:assert/strict';
import {test} from 'node:test';
import {callCandidate, packageShape} from './test_client.mjs';

function value(...args) {
  const response = callCandidate(...args);
  assert.equal(response.ok, true, response.error);
  if (response.value && Array.isArray(response.value.ranges)) {
    const result = response.value.ranges;
    result.type = response.value.type;
    return result;
  }
  return response.value;
}

function expectRange(size, header, expected, options) {
  const result = value(size, header, ...(options === undefined ? [] : [options]));
  const actual = [...result];
  actual.type = result.type;
  assert.deepEqual(actual, expected);
}

function expectError(size, header, message) {
  const response = callCandidate(size, header);
  assert.equal(response.ok, false);
  assert.match(response.error, message);
}

function range(items, type) {
  items.type = type;
  return items;
}

test('package-shape', () => {
  const response = packageShape();
  assert.equal(response.ok, true, response.error);
  assert.deepEqual(response.value, {
    name: 'range-parser', version: '1.2.1', main: 'index.js', callable: 'function',
  });
});

test('rejects non-string headers', () => expectError(200, {}, /TypeError: argument str must be a string/));
test('returns malformed for an empty header', () => assert.equal(value(200, ''), -2));
test('returns malformed when the equals separator is absent', () => assert.equal(value(200, 'bytes=100200'.replace('=', '')), -2));
test('returns malformed for an invalid start position', () => assert.equal(value(200, 'bytes=x-100'), -2));
test('returns malformed for an invalid end position', () => assert.equal(value(200, 'bytes=100-x'), -2));
test('returns malformed for multiple dashes', () => assert.equal(value(200, 'bytes=100--200'), -2));
test('returns malformed for empty range members', () => assert.equal(value(200, 'bytes= , , '), -2));
test('returns malformed when every member has invalid syntax', () => assert.equal(value(200, 'bytes=y-v,x-'), -2));
test('returns unsatisfiable for a range outside the representation', () => assert.equal(value(200, 'bytes=500-600'), -1));
test('returns unsatisfiable for a mixed invalid and unsatisfiable header', () => assert.equal(value(200, 'bytes=abc-def,500-999'), -1));
test('parses an explicit interval and attaches its unit', () => expectRange(1000, 'bytes=0-499', range([{start: 0, end: 499}], 'bytes')));
test('caps an explicit end at the representation size', () => expectRange(200, 'bytes=0-499', range([{start: 0, end: 199}], 'bytes')));
test('keeps an explicit interval within bounds unchanged', () => expectRange(1000, 'bytes=40-80', range([{start: 40, end: 80}], 'bytes')));
test('parses a suffix interval', () => expectRange(1000, 'bytes=-400', range([{start: 600, end: 999}], 'bytes')));
test('clamps an oversized suffix to the whole representation', () => expectRange(100, 'bytes=-101', range([{start: 0, end: 99}], 'bytes')));
test('marks a zero-length suffix as unsatisfiable', () => assert.equal(value(1000, 'bytes=-0'), -1));
test('parses an open-ended interval', () => expectRange(1000, 'bytes=400-', range([{start: 400, end: 999}], 'bytes')));
test('parses an open-ended interval from zero', () => expectRange(1000, 'bytes=0-', range([{start: 0, end: 999}], 'bytes')));
test('parses the final byte as a suffix', () => expectRange(1000, 'bytes=-1', range([{start: 999, end: 999}], 'bytes')));
test('ignores an invalid member when a valid member remains', () => expectRange(1000, 'bytes=100-200,x-', range([{start: 100, end: 200}], 'bytes')));
test('ignores several invalid members around a valid member', () => expectRange(1000, 'bytes=x-,0-100,y-', range([{start: 0, end: 100}], 'bytes')));
test('preserves multiple valid members in input order', () => expectRange(1000, 'bytes=40-80,81-90,-1', range([{start: 40, end: 80}, {start: 81, end: 90}, {start: 999, end: 999}], 'bytes')));
test('caps and filters multiple members independently', () => expectRange(200, 'bytes=0-499,1000-,500-999', range([{start: 0, end: 199}], 'bytes')));
test('trims whitespace around range positions', () => expectRange(1000, 'bytes=   40-80 , 81-90 , -1 ', range([{start: 40, end: 80}, {start: 81, end: 90}, {start: 999, end: 999}], 'bytes')));
test('supports a non-byte range unit', () => expectRange(1000, 'items=0-5', range([{start: 0, end: 5}], 'items')));
test('ignores a whitespace-only member before a valid member', () => expectRange(1000, 'bytes= , 0-10', range([{start: 0, end: 10}], 'bytes')));
test('combines overlapping intervals', () => expectRange(150, 'bytes=0-4,90-99,5-75,100-199,101-102', range([{start: 0, end: 75}, {start: 90, end: 149}], 'bytes'), {combine: true}));
test('combines adjacent intervals', () => expectRange(100, 'bytes=50-55,0-10,5-10,56-60', range([{start: 50, end: 60}, {start: 0, end: 10}], 'bytes'), {combine: true}));
test('retains the first input order of combined groups', () => expectRange(150, 'bytes=-1,20-100,0-1,101-120', range([{start: 149, end: 149}, {start: 20, end: 120}, {start: 0, end: 1}], 'bytes'), {combine: true}));
test('leaves disjoint combined groups in original order', () => expectRange(1000, 'items=700-710,10-20,400-410', range([{start: 700, end: 710}, {start: 10, end: 20}, {start: 400, end: 410}], 'items'), {combine: true}));
test('combines after capping an oversized end', () => expectRange(100, 'bytes=80-200,0-80', range([{start: 0, end: 99}], 'bytes'), {combine: true}));
test('does not combine unless the option is truthy', () => expectRange(100, 'bytes=0-10,5-15', range([{start: 0, end: 10}, {start: 5, end: 15}], 'bytes'), {combine: false}));
test('accepts a truthy combine option', () => expectRange(100, 'bytes=0-10,5-15', range([{start: 0, end: 15}], 'bytes'), {combine: 1}));
test('returns unsatisfiable for a zero-size representation', () => assert.equal(value(0, 'bytes=0-0'), -1));
test('returns unsatisfiable for a suffix on a zero-size representation', () => assert.equal(value(0, 'bytes=-1'), -1));
test('does not retain state between calls', () => {
  assert.deepEqual(value(100, 'bytes=0-9'), range([{start: 0, end: 9}], 'bytes'));
  assert.deepEqual(value(100, 'items=20-29'), range([{start: 20, end: 29}], 'items'));
});

