import assert from 'node:assert/strict';
import {test} from 'node:test';
import {call, packageInventory} from './test_client.mjs';

test('package metadata and export map are complete', () => {
  assert.deepEqual(packageInventory(), {
    name: 'string-width',
    version: '8.2.2',
    type: 'module',
    exports: {types: './index.d.ts', default: './index.js'},
    dependencies: {
      'get-east-asian-width': '1.5.0',
      'strip-ansi': '7.1.2',
    },
    files: [true, true],
  });
});

test('default export is a synchronous numeric function', () => {
  assert.equal(typeof call('abc'), 'number');
  assert.equal(call('abc'), 3);
});

test('package accepts the documented dependency closure', () => {
  const site = process.env.NODE_CANDIDATE_SITE;
  assert.ok(site);
  assert.equal(typeof call('你好'), 'number');
});

const cases = [
  ['empty string', '', 0],
  ['printable ASCII', 'Hello, world!', 13],
  ['long ASCII fast path', 'a'.repeat(1000), 1000],
  ['full-width CJK', '你好世界', 8],
  ['mixed Latin and CJK', 'hello世界', 9],
  ['number input', 123, 0],
  ['null input', null, 0],
  ['object input', {value: 'x'}, 0],
  ['ambiguous default narrow', '±×÷', 3],
  ['ambiguous wide option', '±×÷', 6, {ambiguousIsNarrow: false}],

  ['tab is ignored', '\t\t', 0],
  ['tabs between text', 'a\t\tb', 2],
  ['control in text', 'a\u0001b', 2],
  ['newline is ignored', '\n', 0],
  ['CSI is stripped', '\u001B[31mred\u001B[0m', 3],
  ['CSI can be counted', '\u001B[31m', 4, {countAnsiEscapeCodes: true}],
  ['OSC is stripped', '\u001B]8;;https://example.com\u0007link\u001B]8;;\u0007', 4],

  ['combining accent attaches', 'e\u0301', 1],
  ['combining-only cluster is zero', '\u0301\u0302', 0],
  ['spacing mark has width', '\u093E', 1],
  ['precomposed Hangul', '한국어', 6],
  ['Hangul leading plus vowel', '가', 2],
  ['Hangul leading vowel trailing', '각', 2],
  ['repeated leading jamo stays additive', 'ᄀ가', 4],
  ['malformed surrogate is zero', '\uD800', 0],

  ['emoji grapheme', '😀', 2],
  ['emoji with skin tone', '👋🏽', 2],
  ['family ZWJ sequence', '👨‍👩‍👧‍👦', 2],
  ['qualified keycap', '1️⃣', 2],
  ['unqualified keycap', '#\u20E3', 2],
  ['regional indicator pair', '🇺🇸', 2],
  ['single regional indicator', '🇦', 1],
  ['three regional indicators', '🇺🇸🇦', 3],
  ['emoji variation selector', '⚡\uFE0F', 2],
  ['text variation selector', '↔\uFE0E', 1],
  ['emoji combining mark', '😀\u0301', 2],
  ['plain telephone remains narrow', '☎', 1],

  ['zero-width space', 'a\u200Bb', 2],
  ['zero-width non-joiner', 'a\u200Cb', 2],
  ['prepend before CJK', '\u0600你', 2],
  ['soft hyphen is zero', 'a\u00ADb', 2],
  ['DEL control is zero', '\u007F', 0],
  ['unit separator is zero', '\u001F', 0],
  ['halfwidth voiced kana', 'ﾊﾞ', 2],
  ['halfwidth prolonged kana', 'ｶﾞｰ', 3],
  ['long full-width input', '你'.repeat(500), 1000],
  ['mixed long input', 'a你'.repeat(500), 1500],
  ['only tag characters', '\u{E0020}\u{E007F}', 0],
  ['undefined sentinel input', {type: 'undefined'}, 0],
];

for (const [name, input, expected, options] of cases) {
  test(name, () => assert.equal(call(input, options), expected));
}

test('repeated calls are deterministic', () => {
  const input = '\u001B[32mHello 👋 世界\u001B[0m';
  const values = Array.from({length: 5}, () => call(input));
  assert.deepEqual(values, [13, 13, 13, 13, 13]);
});

assert.equal(cases.length + 4, 53);
