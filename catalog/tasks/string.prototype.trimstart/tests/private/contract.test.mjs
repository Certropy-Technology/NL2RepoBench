import {test} from 'node:test';
import assert from 'node:assert/strict';
import {api, shim, trim} from './test_client.mjs';

function valueOf(args) {
  const result = trim(...args);
  assert.equal(result.ok, true, result.message);
  return result.value;
}

function throwsType(args) {
  const result = trim(...args);
  assert.equal(result.ok, false);
  assert.equal(result.exceptionType, 'TypeError');
}

test('root export is a callable trim function with the public helper surface', () => {
  const result = api();
  assert.equal(result.ok, true, result.message);
  assert.deepEqual(result.value, {
    rootType: 'function', rootName: 'trim', rootLength: 1,
    implementationType: 'function', polyfillType: 'function', shimType: 'function',
    implementationEnumerable: false, polyfillEnumerable: false, shimEnumerable: false,
  });
});
test('empty input returns an empty string', () => assert.equal(valueOf(['']), ''));
test('a string without boundary whitespace is unchanged', () => assert.equal(valueOf(['abc']), 'abc'));
test('leading ASCII whitespace is removed', () => assert.equal(valueOf([' \t\nabc']), 'abc'));
test('trailing ASCII whitespace is preserved', () => assert.equal(valueOf(['abc\t\n ']), 'abc\t\n '));
test('only the leading boundary is removed', () => assert.equal(valueOf([' \t\nabc \r\f']), 'abc \r\f'));
test('internal whitespace is preserved', () => assert.equal(valueOf([' a  b \n c ']), 'a  b \n c '));
test('the ES whitespace set is trimmed from the start', () => {
  const whitespace = '\x09\x0A\x0B\x0C\x0D\x20\xA0\u1680\u2000\u2001\u2002\u2003\u2004\u2005\u2006\u2007\u2008\u2009\u200A\u202F\u205F\u3000\u2028\u2029\uFEFF';
  assert.equal(valueOf([whitespace + 'a' + whitespace]), 'a' + whitespace);
});
test('BOM whitespace is removed from the start', () => assert.equal(valueOf(['\uFEFFdata\uFEFF']), 'data\uFEFF'));
test('Mongolian vowel separator is preserved on Node 24', () => assert.equal(valueOf(['\u180Evalue\u180E']), '\u180Evalue\u180E'));
test('zero-width space is not trimmed', () => assert.equal(valueOf(['\u200bvalue\u200b']), '\u200bvalue\u200b'));
test('next-line and non-character values are preserved', () => {
  assert.equal(valueOf(['\u0085']), '\u0085');
  assert.equal(valueOf(['\uFFFE']), '\uFFFE');
});
test('Unicode line separators are trimmed from the start', () => assert.equal(valueOf(['\u2028text\u2029']), 'text\u2029'));
test('numeric values are converted to strings', () => assert.equal(valueOf([123.5]), '123.5'));
test('boolean values are converted to strings', () => assert.equal(valueOf([true]), 'true'));
test('null is rejected by the bound function', () => throwsType([null]));
test('missing input is rejected by the bound function', () => throwsType([]));
test('arrays use their ordinary string conversion', () => assert.equal(valueOf([[' a ', 'b']]), 'a ,b'));
test('plain objects use their ordinary string conversion', () => assert.equal(valueOf([{value: 1}]), '[object Object]'));
test('a string consisting only of whitespace becomes empty', () => assert.equal(valueOf([' \t\n\u00A0']), ''));
test('a one-code-unit input remains stable', () => assert.equal(valueOf(['x']), 'x'));
test('a supplementary character remains intact', () => assert.equal(valueOf([' \u{1F600} ']), '\u{1F600} '));
test('the implementation helper is exposed as a function', () => {
  const result = api();
  assert.equal(result.ok, true, result.message);
  assert.equal(result.value.implementationType, 'function');
});
test('the polyfill and shim helpers are exposed as functions', () => {
  const result = api();
  assert.equal(result.ok, true, result.message);
  assert.equal(result.value.polyfillType, 'function');
  assert.equal(result.value.shimType, 'function');
});
test('shim returns a callable polyfill and installs a callable builtin', () => {
  const result = shim();
  assert.equal(result.ok, true, result.message);
  assert.deepEqual(result.value, {resultType: 'function', installedType: 'function'});
});
test('helper properties are non-enumerable', () => {
  const result = api();
  assert.equal(result.ok, true, result.message);
  assert.equal(result.value.implementationEnumerable, false);
  assert.equal(result.value.polyfillEnumerable, false);
  assert.equal(result.value.shimEnumerable, false);
});
test('large internal whitespace is preserved without changing content', () => {
  const input = 'A' + ' '.repeat(50_000) + 'B';
  assert.equal(valueOf([input]), input);
});
test('large leading whitespace is removed after internal content', () => {
  const input = ' '.repeat(50_000) + 'A' + ' '.repeat(50_000) + 'B';
  assert.equal(valueOf([input]), 'A' + ' '.repeat(50_000) + 'B');
});
test('punctuation and digits are preserved', () => assert.equal(valueOf([' \t42:_value! ']), '42:_value! '));
test('input strings are not mutated', () => {
  const input = '  immutable  ';
  assert.equal(valueOf([input]), 'immutable  ');
  assert.equal(input, '  immutable  ');
});
test('repeated calls are deterministic', () => {
  const input = '\u2003repeat\uFEFF';
  assert.equal(valueOf([input]), 'repeat\uFEFF');
  assert.equal(valueOf([input]), 'repeat\uFEFF');
});
