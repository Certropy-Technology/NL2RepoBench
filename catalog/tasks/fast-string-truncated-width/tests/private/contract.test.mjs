import {test} from 'node:test';
import assert from 'node:assert/strict';
import {inspect, measure, repeat} from './test_client.mjs';

function result(input, truncationOptions, widthOptions) {
	return measure(input, truncationOptions, widthOptions);
}

function fitting(width, index) {
	return {width, index, truncated: false, ellipsed: false};
}

function truncated(width, index, ellipsed = true) {
	return {width, index, truncated: true, ellipsed};
}

test('package exposes the ESM default function and complete declarations', () => {
	const shape = inspect();
	assert.equal(shape.name, 'fast-string-truncated-width');
	assert.equal(shape.version, '3.0.3');
	assert.equal(shape.type, 'module');
	assert.equal(shape.defaultCallable, true);
	assert.equal(typeof shape.runtimeEntry, 'string');
	assert.equal(typeof shape.declarationEntry, 'string');
	assert.deepEqual(shape.runtimeDependencies, []);
	assert.match(shape.declaration, /input:\s*string/);
	assert.match(shape.declaration, /TruncationOptions/);
	assert.match(shape.declaration, /WidthOptions/);
	assert.match(shape.declaration, /Result/);
});

test('empty input has zero width and the zero UTF-16 end index', () => {
	assert.deepEqual(result(''), fitting(0, 0));
});

test('plain ASCII uses one column per code unit by default', () => {
	assert.deepEqual(result('hello'), fitting(5, 5));
});

test('an ANSI-prefixed string that fits reports its full input index', () => {
	assert.deepEqual(result('\x1b[31mhello'), fitting(5, 10));
});

test('the documented ANSI example truncates before the ellipsis width', () => {
	assert.deepEqual(result('\x1b[31mhello', {limit: 3, ellipsis: '…'}), truncated(2, 7));
});

test('SGR sequences have zero visual width', () => {
	const input = '\x1b[31m\x1b[1;4mtext\x1b[0m';
	assert.deepEqual(result(input), fitting(4, input.length));
});

test('OSC hyperlinks terminated by BEL or ESC backslash have zero width', () => {
	const bel = '\x1b]8;;https://example.com\x07Click\x1b]8;;\x07';
	const st = '\x1b]8;;https://example.com\x1b\\Click\x1b]8;;\x1b\\';
	assert.deepEqual(result(bel), fitting(5, bel.length));
	assert.deepEqual(result(st), fitting(5, st.length));
});

test('C0 C1 and DEL controls default to zero width', () => {
	const input = '\x00\x1f\x7f\x86\x9f';
	assert.deepEqual(result(input), fitting(0, input.length));
});

test('tabs default to eight columns each', () => {
	assert.deepEqual(result('\t\t\t'), fitting(24, 3));
});

test('combining marks add no width', () => {
	assert.deepEqual(result('x\u0300'), fitting(1, 2));
});

test('Han Hiragana and Katakana code points are wide', () => {
	assert.deepEqual(result('古池や'), fitting(6, 3));
	assert.deepEqual(result('ノード'), fitting(6, 3));
});

test('Hangul code points are wide', () => {
	assert.deepEqual(result('안녕하세요'), fitting(10, 5));
});

test('full-width forms always use two columns', () => {
	assert.deepEqual(result('\u3000Ａ'), fitting(4, 2));
});

test('ambiguous-width symbols remain regular-width', () => {
	assert.deepEqual(result('±★'), fitting(2, 2));
});

test('a basic emoji presentation sequence uses one emoji width', () => {
	assert.deepEqual(result('👶'), fitting(2, 2));
});

test('emoji modifiers and ZWJ families stay single emoji clusters', () => {
	const input = '👶🏽👩‍👩‍👦‍👦';
	assert.deepEqual(result(input), fitting(4, input.length));
});

test('regional flags and subdivision flags stay single emoji clusters', () => {
	const input = '🇸🇪🏴󠁧󠁢󠁷󠁬󠁳󠁿';
	assert.deepEqual(result(input), fitting(4, input.length));
});

test('wide supplementary code points use UTF-16 indices', () => {
	assert.deepEqual(result('a🈀b'), fitting(4, 4));
});

test('Japanese half-width kana remain regular-width code points', () => {
	assert.deepEqual(result('ﾊﾞ'), fitting(2, 2));
});

test('ordinary Unicode and zero-width-space code points use regular width', () => {
	assert.deepEqual(result('↔\u200b…'), fitting(3, 3));
});

test('one-column ellipsis reserves one column for Latin truncation', () => {
	assert.deepEqual(result('hello', {limit: 4, ellipsis: '…'}), truncated(3, 3));
});

test('two-column ellipsis reserves two columns for Latin truncation', () => {
	assert.deepEqual(result('hello', {limit: 4, ellipsis: '..'}), truncated(2, 2));
});

test('zero and negative limits produce an empty non-ellipsed slice', () => {
	assert.deepEqual(result('hello', {limit: 0, ellipsis: '…'}), truncated(0, 0, false));
	assert.deepEqual(result('hello', {limit: -2, ellipsis: '…'}), truncated(0, 0, false));
});

test('an ellipsis wider than the limit is not appended', () => {
	assert.deepEqual(result('hello', {limit: 1, ellipsis: '..'}), truncated(0, 0, false));
});

test('ANSI prefixes remain before the truncation index', () => {
	assert.deepEqual(result('\x1b[31mhello', {limit: 4, ellipsis: '…'}), truncated(3, 8));
});

test('controlWidth changes control accounting and truncation', () => {
	assert.deepEqual(
		result('\x00\x01\x02\x03', {limit: 3, ellipsis: '…'}, {controlWidth: 1}),
		truncated(2, 2),
	);
});

test('tabWidth overrides the default tab width', () => {
	assert.deepEqual(result('\tX', {}, {tabWidth: 3}), fitting(4, 2));
});

test('emojiWidth overrides the default emoji width', () => {
	assert.deepEqual(result('👶x', {}, {emojiWidth: 1}), fitting(2, 3));
});

test('regularWidth overrides regular code-point width', () => {
	assert.deepEqual(result('abc', {}, {regularWidth: 2}), fitting(6, 3));
});

test('wideWidth overrides CJK and other wide code-point width', () => {
	assert.deepEqual(result('古a', {}, {wideWidth: 3}), fitting(4, 2));
});

test('explicit ellipsisWidth overrides measuring the ellipsis string', () => {
	assert.deepEqual(
		result('hello', {limit: 3, ellipsis: 'XX', ellipsisWidth: 1}),
		truncated(2, 2),
	);
});

test('CJK truncation never slices through a UTF-16 code point', () => {
	assert.deepEqual(result('古池や', {limit: 5, ellipsis: '…'}), truncated(4, 2));
});

test('emoji truncation never slices through a grapheme sequence', () => {
	assert.deepEqual(result('👶👶🏽', {limit: 3, ellipsis: '…'}), truncated(2, 2));
});

test('hyperlink truncation keeps the complete OSC prefix before visible text', () => {
	const input = '\x1b]8;;https://github.com\x07Click\x1b]8;;\x07';
	const prefix = '\x1b]8;;https://github.com\x07';
	assert.deepEqual(result(input, {limit: 4, ellipsis: '…'}), truncated(3, prefix.length + 3));
});

test('mixed width overrides are composed in input order', () => {
	const input = '\t古👶a';
	assert.deepEqual(
		result(input, {}, {tabWidth: 2, wideWidth: 3, emojiWidth: 4, regularWidth: 1}),
		fitting(10, input.length),
	);
});

test('an exact CJK limit fits without truncation', () => {
	assert.deepEqual(result('古池や', {limit: 6, ellipsis: '…'}), fitting(6, 3));
});

test('repeat calls in one candidate process are deterministic', () => {
	const expected = truncated(2, 7);
	assert.deepEqual(
		repeat('\x1b[31mhello', 5, {limit: 3, ellipsis: '…'}),
		Array.from({length: 5}, () => expected),
	);
});

test('parser chunk boundaries preserve long ASCII and CJK widths', () => {
	const input = `${'a'.repeat(1001)}${'古'.repeat(1001)}`;
	assert.deepEqual(result(input), fitting(3003, 2002));
});

test('long truncated tails return the first bounded slice index', () => {
	assert.deepEqual(
		result('a'.repeat(5000), {limit: 100, ellipsis: '…'}),
		truncated(99, 99),
	);
});
