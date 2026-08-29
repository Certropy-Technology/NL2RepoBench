import assert from 'node:assert/strict';
import {spawnSync} from 'node:child_process';
import {resolve} from 'node:path';
import test from 'node:test';

const client = process.env.NODE_TEST_CLIENT;
const candidateSite = process.env.NODE_CANDIDATE_SITE;
const absoluteCandidateSite = resolve(candidateSite);

function call(request) {
	const result = spawnSync(process.execPath, ['--no-addons', client], {
		cwd: absoluteCandidateSite,
		env: {
			PATH: '/usr/local/bin:/usr/bin:/bin',
			HOME: `${absoluteCandidateSite}/home`,
			TMPDIR: `${absoluteCandidateSite}/tmp`,
			NODE_CANDIDATE_SITE: absoluteCandidateSite,
		},
		input: `${JSON.stringify(request)}\n`,
		encoding: 'utf8',
		timeout: 30_000,
		maxBuffer: 256 * 1024,
	});
	assert.equal(result.error, undefined, result.error?.message);
	assert.ok([0, 1].includes(result.status), result.stderr);
	const response = JSON.parse(result.stdout);
	assert.equal(response.ok, true, response.message ?? response.error);
	return response.value;
}

const match = (input, onlyFirst) => call({operation: 'match', input, onlyFirst});
const probe = input => call({operation: 'test', input});

test('package shape exposes the documented ESM factory', () => {
	assert.deepEqual(call({operation: 'inspect'}), {
		name: 'ansi-regex', version: '6.3.0', type: 'module', exports: './index.js', types: './index.d.ts', callable: true,
	});
});

test('empty text has no match', () => assert.deepEqual(match('').matches, []));
test('ordinary ASCII text has no match', () => assert.equal(probe('plain cake').result, false));
test('ordinary Unicode and emoji have no match', () => assert.equal(probe('雪😀café').result, false));
test('ordinary whitespace has no match', () => assert.equal(probe('a\tb\r\nc').result, false));
test('fresh calls do not share lastIndex state', () => {
	assert.equal(probe('\u001B[31mred').result, true);
	assert.equal(probe('\u001B[31mred').result, true);
});

test('matches SGR color sequences globally', () => assert.deepEqual(match('\u001B[31mred\u001B[39m').matches, ['\u001B[31m', '\u001B[39m']));
test('matches 256-color CSI parameters', () => assert.deepEqual(match('\u001B[38;5;200mpink').matches, ['\u001B[38;5;200m']));
test('matches colon-separated truecolor parameters', () => assert.deepEqual(match('\u001B[38:2:255:0:128mcolor').matches, ['\u001B[38:2:255:0:128m']));
test('matches cursor and erase commands', () => assert.deepEqual(match('x\u001B[2J\u001B[3Ay').matches, ['\u001B[2J', '\u001B[3A']));
test('matches private-mode CSI commands', () => assert.deepEqual(match('\u001B[?25lhide\u001B[?25h').matches, ['\u001B[?25l', '\u001B[?25h']));
test('matches the 8-bit CSI introducer', () => assert.deepEqual(match('\u009B31mred\u009B39m').matches, ['\u009B31m', '\u009B39m']));

test('matches BEL-terminated OSC title', () => assert.deepEqual(match('\u001B]0;title\u0007text').matches, ['\u001B]0;title\u0007']));
test('matches ESC-ST-terminated OSC title', () => assert.deepEqual(match('\u001B]0;title\u001B\\text').matches, ['\u001B]0;title\u001B\\']));
test('matches C1-ST-terminated OSC title', () => assert.deepEqual(match('\u001B]0;title\u009Ctext').matches, ['\u001B]0;title\u009C']));
test('matches both OSC hyperlink controls', () => assert.deepEqual(match('\u001B]8;;https://example.com\u0007Click\u001B]8;;\u0007').matches, ['\u001B]8;;https://example.com\u0007', '\u001B]8;;\u0007']));
test('matches OSC payload punctuation as one control', () => assert.deepEqual(match('\u001B]2;a:b;c?d=e\u0007').matches, ['\u001B]2;a:b;c?d=e\u0007']));

test('default expression is global', () => assert.equal(match('\u001B[31ma\u001B[0m').flags.includes('g'), true));
test('onlyFirst expression is not global', () => assert.equal(match('\u001B[31ma\u001B[0m', true).flags.includes('g'), false));
test('onlyFirst returns only the first occurrence', () => assert.deepEqual(match('\u001B[31ma\u001B[0m', true).matches, ['\u001B[31m']));
test('explicit false is equivalent to omitted options', () => {
	const input = '\u001B[1ma\u001B[22m';
	assert.deepEqual(match(input, false), match(input));
});

test('repeated construction has stable source and flags', () => {
	const first = match('\u001B[31m');
	const second = match('\u001B[31m');
	assert.equal(first.source, second.source);
	assert.equal(first.flags, second.flags);
});
test('mixed CSI and OSC sequences preserve match order', () => assert.deepEqual(match('\u001B[1mA\u001B]0;x\u0007B\u001B[0m').matches, ['\u001B[1m', '\u001B]0;x\u0007', '\u001B[0m']));
test('ordinary text around controls is never part of a match', () => assert.deepEqual(match('before\u001B[31mafter').matches, ['\u001B[31m']));
