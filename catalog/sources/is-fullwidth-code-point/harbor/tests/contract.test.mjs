import assert from 'node:assert/strict';
import {test as nodeTest} from 'node:test';
import {callCandidate} from './test_client.mjs';

function value(input) {
  const response = callCandidate(input);
  assert.equal(response.ok, true, response.error);
  return response.value;
}

function test(name, callback) {
  nodeTest(name, () => {
    assert.equal(value(0x3000), true, 'wide sentinel must be true');
    assert.equal(value(0x41), false, 'narrow sentinel must be false');
    callback();
  });
}

test('package root exposes the expected default ESM function', () => {
  assert.equal(value(0x41), false);
});

test('ASCII letters are not fullwidth', () => {
  assert.deepEqual([0x41, 0x7A, 0x30].map(value), [false, false, false]);
});

test('Japanese hiragana and katakana are fullwidth', () => {
  assert.deepEqual([0x3042, 0x30AB].map(value), [true, true]);
});

test('Chinese ideographs are fullwidth', () => {
  assert.deepEqual([0x8C22, 0x4E2D].map(value), [true, true]);
});

test('Hangul syllables are fullwidth', () => {
  assert.deepEqual([0xACE0, 0xD55C].map(value), [true, true]);
});

test('ideographic space and fullwidth punctuation are fullwidth', () => {
  assert.deepEqual([0x3000, 0xFF01, 0xFF5E].map(value), [true, true, true]);
});

test('supplementary emoji with wide width are true', () => {
  assert.deepEqual([0x1F251, 0x1F600, 0x1F680].map(value), [true, true, true]);
});

test('supplementary CJK ideographs are true', () => {
  assert.deepEqual([0x20000, 0x2A6D6].map(value), [true, true]);
});

test('halfwidth forms are not fullwidth', () => {
  assert.deepEqual([0xFF61, 0xFF66, 0xFFA1].map(value), [false, false, false]);
});

test('ordinary punctuation and ambiguous characters are false', () => {
  assert.deepEqual([0x201D, 0x00B7, 0x03A9].map(value), [false, false, false]);
});

test('controls and zero are false', () => {
  assert.deepEqual([0, 9, 0x1F].map(value), [false, false, false]);
});

test('positive integers outside Unicode are false', () => {
  assert.deepEqual([0x110000, 0x10FFFF + 1, Number.MAX_SAFE_INTEGER].map(value), [false, false, false]);
});

test('negative integers are false', () => {
  assert.deepEqual([-1, -100, Number.MIN_SAFE_INTEGER].map(value), [false, false, false]);
});

test('fractional numbers return false', () => {
  assert.deepEqual([1.5, 0.1, 65535.25].map(value), [false, false, false]);
});

test('numeric strings are false rather than coerced', () => {
  assert.deepEqual(['0', '0x3000', 'あ'].map(value), [false, false, false]);
});

test('booleans and null are false', () => {
  assert.deepEqual([true, false, null].map(value), [false, false, false]);
});

test('arrays and objects are false', () => {
  assert.deepEqual([[], [0x3000], {}, {codePoint: 0x3000}].map(value), [false, false, false, false]);
});

test('unassigned and surrogate values are false', () => {
  assert.deepEqual([0xD800, 0xDFFF, 0x0378].map(value), [false, false, false]);
});

test('boundary fullwidth block values are classified', () => {
  assert.deepEqual([0xFF00, 0xFF10, 0xFF60].map(value), [false, true, true]);
});

test('wide mathematical and symbol values follow Unicode width data', () => {
  assert.deepEqual([0x1F4A9, 0x1F30D, 0x1F9D1].map(value), [true, true, true]);
});

test('neighboring narrow Latin-1 values remain false', () => {
  assert.deepEqual([0x7F, 0xA0, 0xA1, 0xAE].map(value), [false, false, false, false]);
});

test('calls remain stateless across mixed categories', () => {
  const inputs = [0x3042, 0x41, 0x1F251, 0x201D, 0x8C22];
  assert.deepEqual(inputs.map(value), [true, false, true, false, true]);
});

test('repeated wide calls are deterministic', () => {
  const results = Array.from({length: 8}, () => value(0x1F600));
  assert.deepEqual(results, Array(8).fill(true));
});

test('repeated narrow calls are deterministic', () => {
  const results = Array.from({length: 8}, () => value(0x61));
  assert.deepEqual(results, Array(8).fill(false));
});
