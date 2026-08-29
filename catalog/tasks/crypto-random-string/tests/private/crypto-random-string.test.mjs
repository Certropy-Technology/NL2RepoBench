import assert from 'node:assert/strict';
import {test} from 'node:test';
import {call} from './test_client.mjs';

const run = request => call(request);
const value = request => { const result = run(request); assert.equal(result.ok, true, result.message); return result.value; };
const error = request => { const result = run(request); assert.equal(result.ok, false); return result; };
const defaultCall = args => value({op: 'default', args: [args]});
const contractCall = command => value({op: 'contract', command});
const inSet = (text, set) => [...text].every(character => set.includes(character));
const isVaried = text => new Set([...text]).size > 1;

test('package metadata is exact and dependency free', () => {
  const packageJson = value({op: 'metadata'});
  assert.equal(packageJson.name, 'crypto-random-string');
  assert.equal(packageJson.version, '6.0.0');
  assert.equal(packageJson.type, 'module');
  assert.deepEqual(packageJson.dependencies, undefined);
  assert.deepEqual(packageJson.devDependencies, undefined);
});
test('default export produces varied lowercase hexadecimal', () => { const result = defaultCall({length: 128}); assert.equal(result.length, 128); assert.ok(inSet(result, '0123456789abcdef')); assert.ok(isVaried(result)); });
test('base64 output has the requested length and no padding', () => { const result = defaultCall({length: 257, type: 'base64'}); assert.equal(result.length, 257); assert.ok(inSet(result, 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/')); assert.ok(!result.includes('=')); assert.ok(isVaried(result)); });
test('url-safe output uses the documented set', () => { const result = defaultCall({length: 100, type: 'url-safe'}); assert.equal(result.length, 100); assert.ok(inSet(result, 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-._~')); assert.ok(isVaried(result)); });
test('numeric output uses only digits', () => { const result = defaultCall({length: 100, type: 'numeric'}); assert.equal(result.length, 100); assert.ok(inSet(result, '0123456789')); assert.ok(isVaried(result)); });
test('distinguishable output uses only distinguishable symbols', () => { const result = defaultCall({length: 100, type: 'distinguishable'}); assert.equal(result.length, 100); assert.ok(inSet(result, 'CDEHKMPRTUWXY012458')); assert.ok(isVaried(result)); });
test('ascii-printable output excludes spaces', () => { const result = defaultCall({length: 100, type: 'ascii-printable'}); assert.equal(result.length, 100); assert.ok(inSet(result, '!"#$%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~')); assert.ok(!result.includes(' ')); assert.ok(isVaried(result)); });
test('alphanumeric output uses letters and digits', () => { const result = defaultCall({length: 100, type: 'alphanumeric'}); assert.equal(result.length, 100); assert.ok(inSet(result, 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789')); assert.ok(isVaried(result)); });
test('custom character duplicates retain their weighting', () => {
  const {length, counts} = contractCall('custom-weight');
  assert.equal(length, 20_000);
  assert.ok(Math.abs((counts.a / length) - 0.5) < 0.04);
  assert.ok(Math.abs((counts.b / length) - 0.25) < 0.04);
  assert.ok(Math.abs((counts.c / length) - 0.25) < 0.04);
});
test('single custom character is repeated exactly', () => { assert.equal(defaultCall({length: 64, characters: 'x'}), 'x'.repeat(64)); });
test('custom characters count Unicode code points', () => { const result = defaultCall({length: 100, characters: '😀🎉'}); assert.equal([...result].length, 100); assert.ok(inSet(result, '😀🎉')); });
test('zero length does not require entropy', () => { assert.equal(defaultCall({length: 0, characters: '0123'}), ''); assert.equal(defaultCall({length: 0, type: 'base64'}), ''); });
test('base64 never leaks padding at short lengths', () => { for (const length of [1, 2, 3, 4]) { const result = defaultCall({length, type: 'base64'}); assert.equal(result.length, length); assert.ok(!result.includes('=')); } });
test('default output has the default ten-character example shape', () => { const result = defaultCall({length: 10}); assert.equal(result.length, 10); assert.ok(inSet(result, '0123456789abcdef')); });
test('custom Unicode output is not truncated at a UTF-16 boundary', () => { const result = defaultCall({length: 1, characters: '😀'}); assert.equal(result, '😀'); assert.equal([...result].length, 1); });
test('large custom alphabets remain safe for zero length', () => { assert.equal(defaultCall({length: 0, characters: 'a'.repeat(60_000)}), ''); });
test('unsafe integer lengths are rejected before allocation', () => { assert.match(error({op: 'default', args: [{length: Number.MAX_SAFE_INTEGER + 1}]}).message, /non-negative integer/); });
test('constructor is not an accepted type name', () => { assert.match(error({op: 'default', args: [{length: 1, type: 'constructor'}]}).message, /Unknown type: constructor/); });
test('zero length works for every predefined type', () => { for (const type of ['hex', 'base64', 'url-safe', 'numeric', 'distinguishable', 'ascii-printable', 'alphanumeric']) assert.equal(defaultCall({length: 0, type}), ''); });
test('missing length is rejected', () => { assert.match(error({op: 'default', args: [{}]}).message, /non-negative integer/); });
test('negative length is rejected', () => { assert.match(error({op: 'default', args: [{length: -1}]}).message, /non-negative integer/); });
test('fractional length is rejected', () => { assert.match(error({op: 'default', args: [{length: 1.5}]}).message, /non-negative integer/); });
test('non-numeric length is rejected', () => { assert.match(error({op: 'default', args: [{length: '10'}]}).message, /non-negative integer/); });
test('null length is rejected', () => { assert.match(error({op: 'default', args: [{length: null}]}).message, /non-negative integer/); });
test('type and characters are mutually exclusive', () => { assert.match(error({op: 'default', args: [{length: 1, type: 'hex', characters: 'x'}]}).message, /either/); });
test('non-string characters are rejected', () => { assert.match(error({op: 'default', args: [{length: 1, characters: 42}]}).message, /characters.*string/); });
test('empty characters are rejected', () => { assert.match(error({op: 'default', args: [{length: 1, characters: ''}]}).message, /at least 1 character/); });
test('unknown type is rejected', () => { assert.match(error({op: 'default', args: [{length: 1, type: 'unknown'}]}).message, /Unknown type: unknown/); });
test('oversized random requests do not truncate at the entropy boundary', () => { const result = defaultCall({length: 70_000, type: 'numeric'}); assert.equal(result.length, 70_000); assert.ok(inSet(result, '0123456789')); });
test('successive calls consume independent entropy', () => {
  const result = contractCall('successive');
  assert.equal(result.firstLength, 64);
  assert.equal(result.secondLength, 64);
  assert.equal(result.different, true);
});
test('custom character set limit is exactly 65536 Unicode characters', () => {
  const result = contractCall('character-boundary');
  assert.equal(result.maximum, '');
  assert.equal(result.oversizedError?.name, 'TypeError');
  assert.match(result.oversizedError?.message ?? '', /at most 65536 characters, got 65537/);
});
test('non-power-of-two custom sets have a uniform selector distribution', () => {
  const result = contractCall('rejection-distribution');
  assert.equal(result.length, 40_000);
  assert.equal(result.invalid, 0);
  assert.ok(Math.abs(result.firstHalfRatio - 0.5) < 0.03, `ratio: ${result.firstHalfRatio}`);
});
