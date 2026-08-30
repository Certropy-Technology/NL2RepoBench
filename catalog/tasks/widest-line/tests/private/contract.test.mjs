import assert from 'node:assert/strict';
import test from 'node:test';

const {callCandidate, inspectPackage} = await import(
	process.env.NODE_TEST_CLIENT ?? '/tests/private/test_client.mjs'
);

function value(...args) {
	const result = callCandidate(...args);
	assert.equal(result.ok, true, result.error ?? result.message);
	return result.value;
}

test('package metadata and dependency contract', () => {
	assert.deepEqual(inspectPackage(), {
		name: 'widest-line',
		version: '6.0.0',
		type: 'module',
		defaultExport: './index.js',
		typesExport: './index.d.ts',
		dependencies: {'string-width': '^8.1.0'},
	});
});

test('ordinary ASCII width', () => assert.equal(value('a'), 1));
test('widest line wins', () => assert.equal(value('a\nbe'), 2));
test('empty and newline-only inputs are zero', () => {
	assert.equal(value(''), 0);
	assert.equal(value('\n'), 0);
});
test('trailing and repeated empty lines do not change the maximum', () => {
	assert.equal(value('abc\n'), 3);
	assert.equal(value('\nabc\n\n'), 3);
});
test('ties and repeated calls are deterministic', () => {
	assert.equal(value('ab\ncd'), 2);
	assert.equal(value('ab\ncd'), 2);
});
test('ANSI styling is zero-width', () => {
	assert.equal(value('\u001B[1m@\u001B[22m'), 1);
});
test('ANSI styling preserves wide-character width', () => {
	assert.equal(value('\u001B[31m古\u001B[0m\nabc'), 3);
});
test('CJK characters are double-width', () => assert.equal(value('古池や'), 6));
test('emoji presentation is double-width', () => assert.equal(value('😀'), 2));
test('combining marks do not add width', () => {
	assert.equal(value('e\u0301'), 1);
	assert.equal(value('\u0301'), 0);
});
test('emoji clusters stay double-width', () => {
	assert.equal(value('👩‍💻'), 2);
	assert.equal(value('🇺🇸'), 2);
	assert.equal(value('1️⃣'), 2);
});
test('full-width forms are double-width', () => assert.equal(value('Ａ'), 2));
test('ambiguous-width characters are narrow by default', () => assert.equal(value('·'), 1));
test('controls, tabs, and carriage return are zero-width', () => {
	assert.equal(value('\u0000\u0007'), 0);
	assert.equal(value('a\tb'), 2);
	assert.equal(value('a\rb'), 2);
});
test('OSC hyperlinks do not add width', () => {
	assert.equal(value('\u001B]8;;https://example.com\u0007link\u001B]8;;\u0007'), 4);
});
test('long input returns the longest line width', () => {
	assert.equal(value(`short\n${'x'.repeat(4096)}`), 4096);
});
test('number input raises TypeError', () => {
	const result = callCandidate(42);
	assert.equal(result.ok, false);
	assert.equal(result.exception_type, 'TypeError');
});
test('object and null inputs raise TypeError', () => {
	for (const input of [{}, null]) {
		const result = callCandidate(input);
		assert.equal(result.ok, false);
		assert.equal(result.exception_type, 'TypeError');
	}
});
test('missing input raises TypeError', () => {
	const result = callCandidate();
	assert.equal(result.ok, false);
	assert.equal(result.exception_type, 'TypeError');
});
