import assert from 'node:assert/strict';
import {spawnSync} from 'node:child_process';
import {resolve} from 'node:path';
import test from 'node:test';

const client = process.env.NODE_TEST_CLIENT;
const candidateSite = resolve(process.env.NODE_CANDIDATE_SITE);

function call(request) {
	const result = spawnSync(process.execPath, ['--no-addons', client], {
		cwd: candidateSite,
		env: {
			PATH: '/usr/local/bin:/usr/bin:/bin',
			HOME: `${candidateSite}/home`,
			TMPDIR: `${candidateSite}/tmp`,
			NODE_CANDIDATE_SITE: candidateSite,
		},
		input: `${JSON.stringify(request)}\n`,
		encoding: 'utf8',
		timeout: 30_000,
		maxBuffer: 256 * 1024,
	});
	assert.equal(result.error, undefined, result.error?.message);
	assert.equal(result.status, 0, result.stderr);
	const response = JSON.parse(result.stdout);
	assert.equal(response.ok, true, response.message ?? response.error);
	return response.value;
}

const stringResult = input => call({operation: 'string', input}).value;
const bytesResult = (bytes, options = {}) => call({operation: 'bytes', bytes, ...options});
const invalidResult = kind => call({operation: 'invalid', kind});

test('package shape exposes the documented ESM function', () => assert.deepEqual(call({operation: 'inspect'}), {
	name: 'strip-final-newline',
	version: '4.0.0',
	type: 'module',
	exports: {types: './index.d.ts', default: './index.js'},
	callable: true,
}));

test('empty string is unchanged', () => assert.equal(stringResult(''), ''));
test('string without LF is unchanged', () => assert.equal(stringResult('plain text  '), 'plain text  '));
test('string ending in LF loses one LF', () => assert.equal(stringResult('foo\n'), 'foo'));
test('string ending in CRLF loses both bytes', () => assert.equal(stringResult('foo\r\n'), 'foo'));
test('lone trailing CR is preserved', () => assert.equal(stringResult('foo\r'), 'foo\r'));
test('only one LF is removed from repeated newlines', () => assert.equal(stringResult('foo\n\n\n'), 'foo\n\n'));
test('mixed LF CRLF ending removes only the final CRLF', () => assert.equal(stringResult('foo\n\r\n'), 'foo\n'));
test('trailing spaces are preserved with a final LF', () => assert.equal(stringResult('foo  \n'), 'foo  '));
test('Unicode content is preserved', () => assert.equal(stringResult('雪😀 cafe\n'), '雪😀 cafe'));

test('empty Uint8Array is unchanged', () => assert.deepEqual(bytesResult([]).bytes, []));
test('Uint8Array ending in LF loses one byte', () => assert.deepEqual(bytesResult([102, 111, 111, 10]).bytes, [102, 111, 111]));
test('Uint8Array ending in CRLF loses both bytes', () => assert.deepEqual(bytesResult([102, 111, 111, 13, 10]).bytes, [102, 111, 111]));
test('Uint8Array lone CR is preserved', () => assert.deepEqual(bytesResult([102, 111, 111, 13]).bytes, [102, 111, 111, 13]));
test('Uint8Array removes one LF from repeated newlines', () => assert.deepEqual(bytesResult([102, 111, 111, 10, 10]).bytes, [102, 111, 111, 10]));
test('Uint8Array mixed LF CRLF removes only final pair', () => assert.deepEqual(bytesResult([102, 111, 111, 10, 13, 10]).bytes, [102, 111, 111, 10]));
test('arbitrary Uint8Array bytes keep their order', () => assert.deepEqual(bytesResult([0, 255, 13, 42]).bytes, [0, 255, 13, 42]));
test('byte result remains a Uint8Array', () => assert.equal(bytesResult([1, 10]).type, 'Uint8Array'));
test('byte input without LF keeps object identity', () => assert.equal(bytesResult([1, 2]).sameObject, true));
test('stripped byte result shares original storage', () => {
	const result = bytesResult([65, 13, 10]);
	assert.equal(result.sameBuffer, true);
	assert.equal(result.byteLength, 1);
});

test('boolean input is rejected', () => assert.deepEqual(invalidResult('boolean'), {threw: true, name: 'Error', message: 'Input must be a string or a Uint8Array'}));
test('null input is rejected', () => assert.equal(invalidResult('null').threw, true));
test('plain object input is rejected', () => assert.equal(invalidResult('object').threw, true));
test('DataView input is rejected', () => assert.equal(invalidResult('dataView').threw, true));
test('multi-byte typed array input is rejected', () => assert.equal(invalidResult('uint16').threw, true));

test('repeated string calls are stable', () => {
	assert.equal(stringResult('a\r\n'), stringResult('a\r\n'));
});
test('repeated byte calls are stable', () => {
	assert.deepEqual(bytesResult([1, 2, 10]).bytes, bytesResult([1, 2, 10]).bytes);
});
test('byte input is not mutated', () => assert.deepEqual(bytesResult([7, 8, 13, 10]).inputBytes, [7, 8, 13, 10]));
test('CRLF in a non-zero-offset view preserves the view offset', () => {
	const result = bytesResult([99, 65, 13, 10], {offset: 1, length: 3});
	assert.deepEqual(result.bytes, [65]);
	assert.equal(result.byteOffset, 1);
	assert.equal(result.sameBuffer, true);
});
