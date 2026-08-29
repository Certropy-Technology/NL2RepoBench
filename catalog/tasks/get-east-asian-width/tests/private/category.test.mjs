import test from 'node:test';
import assert from 'node:assert/strict';
import {call} from './test_client.mjs';

const category = codePoint => call('eastAsianWidthType', [codePoint]).value;
const width = (codePoint, options) => {
	const args = options === undefined ? [codePoint] : [codePoint, options];
	return call('eastAsianWidth', args).value;
};

test('ASCII letter is narrow', () => assert.equal(category(65), 'narrow'));
test('space is narrow', () => assert.equal(category(32), 'narrow'));
test('Hiragana is wide', () => assert.equal(category(0x3042), 'wide'));
test('CJK ideograph is wide', () => assert.equal(category(0x4E00), 'wide'));
test('emoji supplementary code point is wide', () => assert.equal(category(0x1F600), 'wide'));
test('fullwidth exclamation is fullwidth', () => assert.equal(category(0xFF01), 'fullwidth'));
test('halfwidth punctuation is halfwidth', () => assert.equal(category(0xFF61), 'halfwidth'));
test('reference ambiguous character is ambiguous', () => assert.equal(category(0x26E3), 'ambiguous'));
test('wide category has width two', () => assert.equal(width(0x4E00), 2));
test('fullwidth category has width two', () => assert.equal(width(0xFF01), 2));
test('fullwidth Latin letter has width two', () => assert.equal(width(0xFF21), 2));
test('supplementary symbol has width two', () => assert.equal(width(0x1F300), 2));
test('Hangul choseong has width two', () => assert.equal(width(0x1100), 2));
test('ambiguous defaults to width one', () => assert.equal(width(0x26E3), 1));
test('ambiguousAsWide enables width two', () => assert.equal(width(0x26E3, {ambiguousAsWide: true}), 2));
test('ambiguousAsWide false keeps width one', () => assert.equal(width(0x26E3, {ambiguousAsWide: false}), 1));
test('omitted options use the narrow ambiguous default', () => assert.equal(width(0x26E3), 1));
test('negative safe integer is neutral', () => assert.equal(category(-1), 'neutral'));
test('maximum safe integer is neutral', () => assert.equal(category(Number.MAX_SAFE_INTEGER), 'neutral'));
test('width and category agree for supplementary wide data', () => assert.equal(width(0x1F600), 2));
