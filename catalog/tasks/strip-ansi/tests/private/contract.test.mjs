import {test} from 'node:test';
import assert from 'node:assert/strict';
import {inspect, strip} from './test_client.mjs';

function output(value) {
	const response = strip(value);
	assert.equal(response.ok, true, response.message);
	return response.result;
}

function error(value) {
	const response = strip(value);
	assert.equal(response.ok, false);
	return response;
}

test('package exposes the required ESM default function and declaration', () => {
	const shape = inspect();
	assert.equal(shape.name, 'strip-ansi');
	assert.equal(shape.version, '7.2.0');
	assert.equal(shape.type, 'module');
	assert.equal(shape.defaultCallable, true);
	assert.equal(typeof shape.runtimeEntry, 'string');
	assert.equal(typeof shape.declarationEntry, 'string');
	assert.equal(shape.filesExist, true);
});

test('empty string is returned unchanged', () => {
	assert.equal(output(''), '');
});

test('plain ASCII text is returned unchanged', () => {
	assert.equal(output('plain text 123 !?'), 'plain text 123 !?');
});

test('Unicode and emoji text is preserved', () => {
	assert.equal(output('café Ελληνικά 中文 😀'), 'café Ελληνικά 中文 😀');
});

test('ordinary whitespace and line endings are preserved', () => {
	assert.equal(output('a\tb\nline\r\nend'), 'a\tb\nline\r\nend');
});

test('basic SGR foreground color is removed', () => {
	assert.equal(output('\u001B[31mred\u001B[39m'), 'red');
});

test('nested SGR modifiers are all removed', () => {
	assert.equal(output('\u001B[1m\u001B[4mtext\u001B[24m\u001B[22m'), 'text');
});

test('combined reset foreground background and modifiers are removed', () => {
	assert.equal(output('\u001B[0;33;49;3;9;4mbar\u001B[0m'), 'bar');
});

test('ANSI 256 color parameters are removed', () => {
	assert.equal(output('\u001B[38;5;196mred\u001B[48;5;17mblue\u001B[0m'), 'redblue');
});

test('semicolon truecolor parameters are removed', () => {
	assert.equal(output('\u001B[38;2;255;0;0mred\u001B[0m'), 'red');
});

test('colon truecolor parameters are removed', () => {
	assert.equal(output('\u001B[38:2:255:0:0mred\u001B[0m'), 'red');
});

test('erase and cursor CSI commands are removed', () => {
	assert.equal(output('\u001B[2J\u001B[HABC\u001B[1A'), 'ABC');
});

test('private mode CSI commands are removed', () => {
	assert.equal(output('\u001B[?25lhidden\u001B[?25h'), 'hidden');
});

test('8-bit CSI introducer is supported', () => {
	assert.equal(output('\u009B31mred\u009B39m'), 'red');
});

test('OSC title terminated by BEL is removed', () => {
	assert.equal(output('\u001B]0;terminal title\u0007body'), 'body');
});

test('OSC hyperlink terminated by BEL is removed', () => {
	assert.equal(output('\u001B]8;;https://example.com\u0007click\u001B]8;;\u0007'), 'click');
});

test('OSC hyperlink terminated by ESC backslash is removed', () => {
	assert.equal(output('\u001B]8;;https://example.com\u001B\\click\u001B]8;;\u001B\\'), 'click');
});

test('OSC hyperlink terminated by 8-bit ST is removed', () => {
	assert.equal(output('\u001B]8;;https://example.com\u009Cclick\u001B]8;;\u009C'), 'click');
});

test('mixed CSI and OSC sequences preserve surrounding text', () => {
	assert.equal(output('A\u001B[31mB\u001B[0mC\u001B]0;x\u0007D'), 'ABCD');
});

test('multiple separated sequence groups are removed globally', () => {
	assert.equal(output('\u001B[31ma\u001B[0m-\u001B[32mb\u001B[0m'), 'a-b');
});

test('number input raises the specified TypeError', () => {
	assert.deepEqual(error(42), {
		ok: false,
		exceptionType: 'TypeError',
		message: 'Expected a `string`, got `number`',
	});
});

test('boolean input raises the specified TypeError', () => {
	assert.deepEqual(error(true), {
		ok: false,
		exceptionType: 'TypeError',
		message: 'Expected a `string`, got `boolean`',
	});
});

test('null and object inputs use JavaScript typeof in the error', () => {
	for (const value of [null, [], {value: 'x'}]) {
		assert.deepEqual(error(value), {
			ok: false,
			exceptionType: 'TypeError',
			message: 'Expected a `string`, got `object`',
		});
	}
});

test('repeated calls are deterministic and do not leak regex state', () => {
	const value = '\u001B[35mstable\u001B[39m';
	assert.equal(output(value), 'stable');
	assert.equal(output(value), 'stable');
	assert.equal(output(value), 'stable');
});
