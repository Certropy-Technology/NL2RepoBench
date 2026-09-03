import assert from 'node:assert/strict';
import {test} from 'node:test';
import {callCandidate} from './test_client.mjs';

const unix = (TERM) => ({platform: 'linux', env: {TERM}});
const windows = (env = {}) => ({platform: 'win32', env});

test('package metadata and default ESM export are available', () => {
	assert.equal(callCandidate(unix('xterm-256color')), true);
});

test('non-Windows linux console marker is unsupported', () => {
	assert.equal(callCandidate(unix('linux')), false);
});

test('non-Windows ordinary TERM values are supported', () => {
	assert.deepEqual(['xterm', 'xterm-256color', 'screen', 'dumb'].map(TERM => callCandidate(unix(TERM))), [true, true, true, true]);
});

test('non-Windows missing and empty TERM are supported', () => {
	assert.equal(callCandidate({platform: 'darwin', env: {}}), true);
	assert.equal(callCandidate(unix('')), true);
});

test('Windows without a supported marker is unsupported', () => {
	assert.equal(callCandidate(windows()), false);
});

test('Windows Terminal session marker is supported', () => {
	assert.equal(callCandidate(windows({WT_SESSION: 'abc'})), true);
});

test('Terminus Sublime legacy session marker is supported', () => {
	assert.equal(callCandidate(windows({TERMINUS_SUBLIME: '1'})), true);
});

test('Windows terminal program markers are supported', () => {
	assert.equal(callCandidate(windows({TERM_PROGRAM: 'Terminus-Sublime'})), true);
	assert.equal(callCandidate(windows({TERM_PROGRAM: 'vscode'})), true);
});

test('Windows terminal program matching is case sensitive', () => {
	assert.equal(callCandidate(windows({TERM_PROGRAM: 'VSCode'})), false);
	assert.equal(callCandidate(windows({TERM_PROGRAM: 'terminus-sublime'})), false);
});

test('Windows TERM markers are supported', () => {
	for (const TERM of ['xterm-256color', 'alacritty', 'rxvt-unicode', 'rxvt-unicode-256color']) {
		assert.equal(callCandidate(windows({TERM})), true, TERM);
	}
});

test('Windows TERM markers require exact values', () => {
	assert.equal(callCandidate(windows({TERM: 'XTERM-256COLOR'})), false);
	assert.equal(callCandidate(windows({TERM: 'xterm'})), false);
});

test('Windows ConEmu Cmder marker is supported', () => {
	assert.equal(callCandidate(windows({ConEmuTask: '{cmd::Cmder}'})), true);
});

test('Windows JetBrains terminal marker is supported', () => {
	assert.equal(callCandidate(windows({TERMINAL_EMULATOR: 'JetBrains-JediTerm'})), true);
});

test('empty Windows markers are unsupported', () => {
	assert.equal(callCandidate(windows({WT_SESSION: '', TERMINUS_SUBLIME: '', TERM_PROGRAM: '', TERM: '', TERMINAL_EMULATOR: ''})), false);
});

test('unrecognized Windows markers are unsupported', () => {
	assert.equal(callCandidate(windows({WT_SESSION: undefined, TERM: 'screen', TERM_PROGRAM: 'iTerm.app', TERMINAL_EMULATOR: 'other'})), false);
});

test('environment changes are observed on the next call', () => {
	assert.equal(callCandidate(unix('linux')), false);
	assert.equal(callCandidate(unix('xterm-256color')), true);
});

test('platform changes are observed on the next call', () => {
	assert.equal(callCandidate({platform: 'linux', env: {TERM: 'linux'}}), false);
	assert.equal(callCandidate({platform: 'win32', env: {TERM: 'linux'}}), false);
	assert.equal(callCandidate({platform: 'darwin', env: {TERM: 'linux'}}), false);
	assert.equal(callCandidate({platform: 'freebsd', env: {TERM: 'xterm'}}), true);
});

test('each supported marker returns a primitive boolean', () => {
	for (const env of [{WT_SESSION: '1'}, {TERMINUS_SUBLIME: '1'}, {ConEmuTask: '{cmd::Cmder}'}, {TERM_PROGRAM: 'vscode'}, {TERM: 'alacritty'}, {TERMINAL_EMULATOR: 'JetBrains-JediTerm'}]) {
		assert.equal(typeof callCandidate(windows(env)), 'boolean');
	}
});

test('arguments do not change the result', () => {
	assert.equal(callCandidate(unix('linux'), ['ignored']), false);
	assert.equal(callCandidate(windows({TERM: 'alacritty'}), [true, 1]), true);
});

test('Windows marker alternatives remain independent', () => {
	assert.equal(callCandidate(windows({TERM: 'linux', WT_SESSION: '1'})), true);
	assert.equal(callCandidate(windows({TERM: 'linux', ConEmuTask: '{cmd::Cmder}'})), true);
});
