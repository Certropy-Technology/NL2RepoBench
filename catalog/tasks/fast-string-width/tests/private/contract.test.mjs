import assert from 'node:assert/strict';
import {test} from 'node:test';
import {call} from './test_client.mjs';

test('basic-1 empty string has zero width', () => assert.equal(call(''), 0));
test('basic-2 ASCII uses regular width', () => assert.equal(call('hello'), 5));
test('basic-3 ANSI CSI escapes are zero width', () => assert.equal(call('\x1b[31mhello'), 5));
test('basic-4 ANSI reset escape is zero width', () => assert.equal(call('\x1b[31mhello\x1b[0m'), 5));
test('basic-5 repeated calls are deterministic', () => assert.equal(call('repeat'), call('repeat')));

test('options-1 tab width is configurable', () => assert.equal(call('\ta', {tabWidth: 4}), 5));
test('options-2 control width is configurable', () => assert.equal(call('\x01', {controlWidth: 1}), 1));
test('options-3 emoji width is configurable', () => assert.equal(call('👶👶🏽', {emojiWidth: 1.5}), 3));
test('options-4 regular width is configurable', () => assert.equal(call('ab', {regularWidth: 2}), 4));
test('options-5 wide width applies to CJK blocks', () => assert.equal(call('漢字', {wideWidth: 1}), 2));
test('options-6 multiple options compose', () => assert.equal(call('a\t👶漢', {tabWidth: 3, emojiWidth: 1, regularWidth: 2, wideWidth: 1}), 7));
test('options-7 truncation-looking fields do not enable truncation', () => assert.equal(call('hello', {limit: 1, ellipsis: '…'}), 5));

test('unicode-1 family emoji is one recognized sequence', () => assert.equal(call('👨‍👩‍👧‍👦'), 2));
test('unicode-2 skin-tone emoji sequence counts once', () => assert.equal(call('👶👶🏽'), 4));
test('unicode-3 regional indicator flag counts as one emoji', () => assert.equal(call('🇺🇸'), 2));
test('unicode-4 keycap counts as one emoji', () => assert.equal(call('1️⃣'), 2));
test('unicode-5 CJK characters are wide', () => assert.equal(call('漢字かなカナ한글'), 16));
test('unicode-6 full-width punctuation is wide', () => assert.equal(call('！'), 2));
test('unicode-7 combining marks add no width', () => assert.equal(call('e\u0301'), 1));
test('unicode-8 OSC hyperlink sequence is zero width', () => assert.equal(call('\x1b]8;;https://example.com\x07link\x1b]8;;\x07'), 4));

test('contract-1 result is a number', () => assert.equal(typeof call('x'), 'number'));
test('contract-2 input value is not mutated', () => {
  const input = 'immutable';
  call(input, {regularWidth: 2});
  assert.equal(input, 'immutable');
});
test('contract-3 nullish option fields use defaults', () => assert.equal(call('a\t', {regularWidth: null, tabWidth: null}), 9));
test('contract-4 mixed ANSI Unicode string preserves ordering', () => assert.equal(call('\x1b[32mA漢👩‍💻\x1b[0m'), 5));
