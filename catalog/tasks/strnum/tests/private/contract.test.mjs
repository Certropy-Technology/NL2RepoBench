import assert from 'node:assert/strict';
import {test} from 'node:test';
import {call} from './test_client.mjs';

const input = (value) => ({type: 'value', value});
const undefinedInput = {type: 'undefined'};

function result(value, options = {}) {
  const response = call(input(value), options);
  assert.equal(response.ok, true, response.message ?? response.error);
  return response.result;
}

function undefinedResult(options = {}) {
  const response = call(undefinedInput, options);
  assert.equal(response.ok, true, response.message ?? response.error);
  return response.result;
}

function expectNumber(value, expected, options = {}) {
  const actual = result(value, options);
  assert.equal(actual.type, 'number');
  assert.equal(actual.value, Object.is(expected, -0) ? 0 : expected);
  assert.equal(Boolean(actual.negativeZero), Object.is(expected, -0));
}

function expectString(value, expected = value, options = {}) {
  assert.deepEqual(result(value, options), {type: 'string', value: expected});
}

test('package root exposes a callable default export', () => expectNumber('12', 12));

test('undefined is returned unchanged', () => assert.deepEqual(undefinedResult(), {type: 'undefined'}));

test('null, booleans, and numbers are returned unchanged', () => {
  assert.deepEqual(result(null), {type: 'null'});
  assert.deepEqual(result(false), {type: 'boolean', value: false});
  expectNumber(12, 12);
});

test('empty and whitespace-only strings preserve their original bytes', () => {
  expectString('');
  expectString('   ');
  expectString('\t\n');
});

test('ordinary non-numeric strings are unchanged', () => expectString('string'));

test('malformed separators and multiple decimal points are unchanged', () => {
  for (const value of ['12,12', '12 12', '12-12', '12.12.12']) expectString(value);
});

test('an optional plus sign is accepted only at the start', () => {
  expectNumber('+12', 12);
  expectString('+ 12');
  expectString('12+');
});

test('hexadecimal strings parse by default', () => {
  expectNumber('0x2f', 47);
  expectNumber('-0x2f', -47);
});

test('hex false preserves hexadecimal strings', () => {
  expectString('0x2f', '0x2f', {hex: false});
  expectString('-0x2f', '-0x2f', {hex: false});
});

test('malformed or embedded hexadecimal markers are unchanged', () => {
  for (const value of ['0xzz', '1230x55', 'JVBERi0xLjMNCiXi48']) expectString(value);
});

test('binary strings require the binary option', () => {
  expectString('0b1010');
  expectNumber('0b1010', 10, {binary: true});
});

test('signed binary strings remain unchanged', () => {
  expectString('-0b1010', '-0b1010', {binary: true});
});

test('octal strings require the octal option', () => {
  expectString('0o10');
  expectNumber('0o10', 8, {octal: true});
});

test('signed octal strings remain unchanged', () => {
  expectString('-0o10', '-0o10', {octal: true});
});

test('leading zero integers parse by default', () => {
  expectNumber('00', 0);
  expectNumber('006', 6);
  expectNumber('-06', -6);
});

test('leadingZeros false preserves padded integers', () => {
  expectString('00', '00', {leadingZeros: false});
  expectString('006', '006', {leadingZeros: false});
  expectString('-06', '-06', {leadingZeros: false});
});

test('ordinary decimal fractions parse', () => {
  expectNumber('.006', 0.006);
  expectNumber('6.0', 6);
  expectNumber('0.06', 0.06);
});

test('padded decimal fractions parse by default', () => {
  expectNumber('00.6', 0.6);
  expectNumber('-06.0', -6);
  expectNumber('+06.0', 6);
});

test('leadingZeros false preserves padded decimal fractions', () => {
  expectString('00.6', '00.6', {leadingZeros: false});
  expectString('-06.0', '-06.0', {leadingZeros: false});
});

test('zero decimal forms still parse when leading zeros are disabled', () => {
  expectNumber('0.0', 0, {leadingZeros: false});
  expectNumber('-0.0', -0, {leadingZeros: false});
});

test('negative zero is preserved', () => {
  expectNumber('-0.', -0);
  expectNumber('-00.00', -0);
});

test('unsafe integer text is preserved when round-tripping would change it', () => {
  expectString('20211201030005811824');
  expectString('9007199254740993');
});

test('very long numeric text may parse when its numeric spelling is exponential', () => {
  expectNumber('420926189200190257681175017717', 4.209261892001902e+29);
});

test('eNotation false preserves values that Number renders exponentially', () => {
  expectString('420926189200190257681175017717', undefined, {eNotation: false});
});

test('lowercase scientific notation parses', () => {
  expectNumber('1.0e2', 100);
  expectNumber('-1e-2', -0.01);
  expectNumber('1.e+2', 100);
});

test('uppercase scientific notation parses', () => {
  expectNumber('1.0E2', 100);
  expectNumber('0E2', 0);
  expectNumber('-0E2', -0);
});

test('scientific notation with leading zeros follows leadingZeros', () => {
  expectNumber('01.0e2', 100);
  expectString('01.0e2', '01.0e2', {leadingZeros: false});
});

test('malformed scientific notation is unchanged', () => {
  for (const value of ['E2', 'E-2', '00E2']) expectString(value);
});

test('eNotation false preserves explicit scientific notation', () => {
  expectString('1e2', '1e2', {eNotation: false});
});

test('overflow defaults to the original string', () => {
  expectString('1e1000');
  expectString('-1e1000');
});

test('infinity null maps overflow to null', () => {
  assert.deepEqual(result('1e1000', {infinity: 'null'}), {type: 'null'});
});

test('infinity infinity returns signed numeric infinities', () => {
  assert.deepEqual(result('1e1000', {infinity: 'infinity'}), {type: 'number', value: 'Infinity'});
  assert.deepEqual(result('-1e1000', {infinity: 'infinity'}), {type: 'number', value: '-Infinity'});
});

test('infinity string returns signed string literals', () => {
  expectString('1e1000', 'Infinity', {infinity: 'string'});
  expectString('-1e1000', '-Infinity', {infinity: 'string'});
});

test('fullwidth decimal digits normalize when unicode is true', () => {
  expectNumber('１000', 1000, {unicode: true});
});

test('fullwidth decimal digits remain unchanged when unicode is false', () => {
  expectString('１000');
});

test('unicode normalization occurs before overflow handling', () => {
  expectString('１e１000', '１e１000', {unicode: true, infinity: 'original'});
  assert.deepEqual(result('１e１000', {unicode: true, infinity: 'infinity'}), {type: 'number', value: 'Infinity'});
});

test('skipLike preserves matching numeric strings', () => {
  expectString('+1212121212', '+1212121212', {skipLike: {source: '^\\+[0-9]{10}$', flags: ''}});
});

test('skipLike does not alter non-matching conversion', () => {
  expectNumber('+12', 12, {skipLike: {source: '^\\+[0-9]{10}$', flags: ''}});
});

test('skipLike is tested against trimmed text but returns the original string', () => {
  expectString('  +1212121212  ', '  +1212121212  ', {skipLike: {source: '^\\+[0-9]{10}$', flags: ''}});
});

test('valid numeric strings may have surrounding whitespace', () => {
  expectNumber('   +1212   ', 1212);
});

test('invalid strings with surrounding whitespace preserve the original', () => {
  expectString('    +12 12   ');
});

test('mixed repeated calls are deterministic and stateless', () => {
  const values = ['0x2f', '006', '1e2', '１000', 'not-a-number'];
  const options = [{}, {}, {}, {unicode: true}, {}];
  const first = values.map((value, index) => result(value, options[index]));
  const second = values.map((value, index) => result(value, options[index]));
  assert.deepEqual(second, first);
});
