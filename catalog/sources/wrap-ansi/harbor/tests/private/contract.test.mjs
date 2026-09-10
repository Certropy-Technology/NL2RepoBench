import assert from 'node:assert/strict';
import {test} from 'node:test';
import {shape, wrap} from './test_client.mjs';

const red = text => `\u001B[31m${text}\u001B[39m`;
const green = text => `\u001B[32m${text}\u001B[39m`;
const strip = value => value
  .replace(/\u001B\][^\u0007]*(?:\u0007|\u001B\\)/g, '')
  .replace(/\u001B\[[0-?]*[ -/]*[@-~]/g, '')
  .replace(/\u009B[0-?]*[ -/]*[@-~]/g, '');

test('package metadata and ESM entry are complete', () => {
  assert.deepEqual(shape(), {
    name: 'wrap-ansi', version: '10.0.1', type: 'module',
    exports: {types: './index.d.ts', default: './index.js'},
    declaration: true, functionName: 'wrapAnsi', functionLength: 3,
  });
});
test('wraps words at a soft boundary', () => assert.equal(wrap('The quick brown fox jumped over the lazy dog', 20), 'The quick brown fox\njumped over the lazy\ndog'));
test('hard-wraps a long word', () => assert.equal(wrap('abcdefghij', 4, {hard: true}), 'abcd\nefgh\nij'));
test('soft mode keeps a long word intact', () => assert.equal(wrap('abcdefghij', 4), 'abcdefghij'));
test('hard mode does not prepend a row for a split first word', () => assert.equal(wrap('hello-world', 5, {hard: true}), 'hello\n-worl\nd'));
test('wordWrap false fills each row', () => assert.equal(wrap('1234567890 12345', 5, {wordWrap: false}), '12345\n67890\n12345'));
test('wordWrap false with hard mode splits long words', () => assert.equal(wrap('abcdefghij', 4, {wordWrap: false, hard: true}), 'abcd\nefgh\nij'));
test('default trimming removes outer spaces', () => assert.equal(wrap('   foo   bar   ', 3), 'foo\nbar'));
test('trim false preserves outer and wrapped spaces', () => assert.equal(wrap(' foo bar ', 3, {trim: false}), ' \nfoo\n \nbar\n '));
test('whitespace-only input trims to empty', () => assert.equal(wrap('   ', 2), ''));
test('whitespace-only input is preserved without trim', () => assert.equal(wrap('   ', 2, {trim: false}), '  \n '));
test('empty input remains empty', () => assert.equal(wrap('', 10), ''));
test('zero columns still returns deterministic text', () => assert.equal(wrap('abc', 0, {hard: true}), 'a\nb\nc'));
test('normalizes CRLF input', () => assert.equal(wrap('foo\r\nbar', 10), 'foo\nbar'));
test('preserves a trailing newline', () => assert.equal(wrap('foo\n', 10), 'foo\n'));
test('wraps existing lines independently', () => assert.equal(wrap('12345678\n9012345678', 4, {hard: true}), '1234\n5678\n9012\n3456\n78'));
test('counts ANSI SGR as zero width', () => assert.equal(wrap(`${red('hello world')}`, 5), `${red('hello')}\n${red('world')}`));
test('reopens foreground style on every wrapped row', () => assert.equal(wrap(`${red('abcdefgh')}`, 3, {hard: true}), `${red('abc')}\n${red('def')}\n${red('gh')}`));
test('preserves nested foreground and background styles', () => {
  const input = '\u001B[42m\u001B[31mabcdef\u001B[39m\u001B[49m';
  const expected = '\u001B[42m\u001B[31mabc\u001B[39m\u001B[49m\n\u001B[42m\u001B[31mdef\u001B[39m\u001B[49m';
  assert.equal(wrap(input, 3, {hard: true}), expected);
});
test('preserves modifier styles', () => assert.equal(wrap('\u001B[1mabcdef\u001B[22m', 3, {hard: true}), '\u001B[1mabc\u001B[22m\n\u001B[1mdef\u001B[22m'));
test('handles combined SGR parameters', () => assert.equal(wrap('\u001B[1;31mabcdef\u001B[0m', 3, {hard: true}), '\u001B[1;31mabc\u001B[39m\u001B[22m\n\u001B[1m\u001B[31mdef\u001B[0m'));
test('respects a style reset at a new row', () => assert.equal(wrap('\u001B[31mabc\u001B[39mdef', 3, {hard: true}), '\u001B[31mabc\u001B[39m\n\u001B[39mdef'));
test('preserves 256-color SGR', () => assert.equal(wrap('\u001B[38;5;196mabcdef\u001B[39m', 3, {hard: true}), '\u001B[38;5;196mabc\u001B[39m\n\u001B[38;5;196mdef\u001B[39m'));
test('preserves truecolor SGR', () => assert.equal(wrap('\u001B[38;2;255;0;0mabcdef\u001B[39m', 3, {hard: true}), '\u001B[38;2;255;0;0mabc\u001B[39m\n\u001B[38;2;255;0;0mdef\u001B[39m'));
test('preserves colon-delimited SGR', () => assert.equal(wrap('\u001B[38:2::255:0:0mabcdef\u001B[39m', 3, {hard: true}), '\u001B[38:2::255:0:0mabc\u001B[39m\n\u001B[38:2::255:0:0mdef\u001B[39m'));
test('preserves BEL hyperlinks', () => {
  const input = '\u001B]8;;https://example.com\u0007abcdefgh\u001B]8;;\u0007';
  const open = '\u001B]8;;https://example.com\u0007';
  const close = '\u001B]8;;\u0007';
  assert.equal(wrap(input, 4, {hard: true}), `${open}abcd${close}\n${open}efgh${close}`);
});
test('preserves ST hyperlinks', () => {
  const input = '\u001B]8;;https://example.com\u001B\\abcdefgh\u001B]8;;\u001B\\';
  const open = '\u001B]8;;https://example.com\u001B\\';
  assert.equal(wrap(input, 4, {hard: true}), `${open}abcd\u001B]8;;\u0007\n${open.replace(/\u001B\\$/, '\u0007')}efgh\u001B]8;;\u001B\\`);
});
test('keeps adjacent hyperlink URLs separate', () => {
  const a = '\u001B]8;;https://a.com\u0007one\u001B]8;;\u0007';
  const b = '\u001B]8;;https://b.com\u0007twothree\u001B]8;;\u0007';
  const result = wrap(`${a} ${b}`, 4, {hard: true});
  assert.deepEqual(result.split('\n').map(strip), ['one', 'twot', 'hree']);
  assert.equal(result.includes('https://a.com'), true);
  assert.equal(result.includes('https://b.com'), true);
});
test('keeps non-SGR CSI opaque', () => assert.equal(wrap('\u001B[2Jabcdefghij', 5, {hard: true}), '\u001B[2Jabcde\nfghij'));
test('keeps C1 CSI opaque', () => assert.equal(wrap('\u009B2Jabcdefghij', 5, {hard: true}), '\u009B2Jabcde\nfghij'));
test('treats unsupported control strings as text', () => assert.equal(strip(wrap('\u001BPunterminated', 5, {hard: true})), '\u001BPunte\nrmina\nted'));
test('expands tabs at eight-column stops', () => assert.equal(wrap('1234\ttest', 10, {hard: true, trim: false}), '1234    \ntest'));
test('expands consecutive tabs deterministically', () => assert.equal(wrap('\t\t\ttesting', 10, {hard: true, trim: false}), '          \n          \n    \ntesting'));
test('ignores ANSI when computing tab stops', () => assert.equal(strip(wrap(`${red('ab')}\tcd`, 20)), 'ab      cd'));
test('does not split fullwidth characters', () => assert.equal(wrap('안녕하세', 4, {hard: true}), '안녕\n하세'));
test('does not split surrogate-pair emoji', () => assert.equal(wrap('a🈀bc', 2, {hard: true}), 'a\n🈀\nbc'));
test('does not split ZWJ grapheme clusters', () => assert.equal(wrap('a👨‍👩‍👧‍👦b', 2, {hard: true}), 'a\n👨‍👩‍👧‍👦\nb'));
test('does not split flag grapheme clusters', () => assert.equal(wrap('a🇺🇸b', 2, {hard: true}), 'a\n🇺🇸\nb'));
test('keeps combining marks with their base', () => assert.equal(wrap('நிநி', 1, {hard: true}), 'நி\nநி'));
test('preserves ANSI around grapheme clusters', () => assert.equal(strip(wrap(`${red('a👨‍👩‍👧‍👦b')}`, 2, {hard: true})), 'a\n👨‍👩‍👧‍👦\nb'));
test('trims spaces inside a colored block', () => assert.equal(wrap(`${green('   foo   bar   ')}`, 6), `${green('foo')}\n${green('bar')}`));
test('keeps spaces inside a colored block when trim is false', () => assert.equal(wrap(`${green(' foo bar ')}`, 20, {trim: false}), `${green(' foo bar ')}`));
test('does not reopen styles on a trailing empty row', () => assert.equal(wrap('\u001B[31mabc ', 3, {wordWrap: false}), '\u001B[31mabc\u001B[39m\n'));
test('coerces the string argument using JavaScript String semantics', () => assert.equal(wrap(12345, 3, {hard: true}), '123\n45'));
