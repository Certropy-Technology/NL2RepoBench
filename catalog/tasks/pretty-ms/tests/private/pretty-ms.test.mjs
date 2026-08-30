import test from 'node:test';
import assert from 'node:assert/strict';
import {invoke, value} from './test_client.mjs';

test('formats a multi-unit duration', () => {
	assert.equal(value(1_337_000_000), '15d 11h 23m 20s');
});

test('formats seconds with the default precision', () => {
	assert.equal(value(1337), '1.3s');
});

test('formats a sub-second value as milliseconds', () => {
	assert.equal(value(133), '133ms');
});

test('formats zero', () => {
	assert.equal(value(0), '0ms');
});

test('preserves a negative sign', () => {
	assert.equal(value(-1337), '-1.3s');
});

test('rejects a string input', () => {
	const response = invoke('1000');
	assert.equal(response.ok, false);
	assert.equal(response.exception_type, 'TypeError');
	assert.equal(response.message, 'Expected a finite number or bigint');
});

test('rejects null input', () => {
	const response = invoke(null);
	assert.equal(response.ok, false);
	assert.equal(response.exception_type, 'TypeError');
});

test('truncates seconds to requested decimal digits', () => {
	assert.equal(value(12_345, {secondsDecimalDigits: 2}), '12.34s');
});

test('can remove seconds decimals', () => {
	assert.equal(value(12_345, {secondsDecimalDigits: 0}), '12s');
});

test('keeps decimals on whole seconds', () => {
	assert.equal(value(13_000, {keepDecimalsOnWholeSeconds: true}), '13.0s');
});

test('removes decimals on whole seconds by default', () => {
	assert.equal(value(13_000), '13s');
});

test('formats compact output using the first unit', () => {
	assert.equal(value(3_661_000, {compact: true}), '1h');
});

test('compact output works for minutes', () => {
	assert.equal(value(61_000, {compact: true}), '1m');
});

test('limits the number of displayed units', () => {
	assert.equal(value(3_661_000, {unitCount: 2}), '1h 1m');
});

test('unitCount retains at least one unit', () => {
	assert.equal(value(3_661_000, {unitCount: 0}), '1h');
});

test('uses singular verbose unit names', () => {
	assert.equal(value(3_661_000, {verbose: true}), '1 hour 1 minute 1 second');
});

test('uses plural verbose unit names', () => {
	assert.equal(value(7_322_000, {verbose: true}), '2 hours 2 minutes 2 seconds');
});

test('shows milliseconds separately', () => {
	assert.equal(value(1234.56, {separateMilliseconds: true}), '1s 235ms');
});

test('shows sub-millisecond units separately', () => {
	assert.equal(value(100.40008, {formatSubMilliseconds: true}), '100ms 400µs 80ns');
});

test('uses decimal milliseconds when requested', () => {
	assert.equal(value(234.56, {millisecondsDecimalDigits: 2}), '234.56ms');
});

test('rounds milliseconds when decimal digits are omitted', () => {
	assert.equal(value(234.56), '235ms');
});

test('formats sub-seconds as decimal seconds', () => {
	assert.equal(value(900, {subSecondsAsDecimals: true}), '0.9s');
});

test('rounds a sub-second value as milliseconds by default', () => {
	assert.equal(value(999.9), '1000ms');
});

test('uses colon notation with padded minutes', () => {
	assert.equal(value(95_500, {colonNotation: true}), '1:35.5');
});

test('colon notation shows minutes for short durations', () => {
	assert.equal(value(1000, {colonNotation: true}), '0:01');
});

test('colon notation overrides compact and verbose options', () => {
	assert.equal(value(3_661_000, {colonNotation: true, compact: true, verbose: true, separateMilliseconds: true, formatSubMilliseconds: true}), '1:01:01');
});

test('hides years by expressing them as days', () => {
	const duration = 31_536_000_000 + 3 * 86_400_000 + 5 * 3_600_000 + 60_000 + 45;
	assert.equal(value(duration, {hideYear: true}), '368d 5h 1m');
});

test('hides years and days by expressing them as hours', () => {
	const duration = 31_536_000_000 + 3 * 86_400_000 + 5 * 3_600_000 + 60_000 + 45;
	assert.equal(value(duration, {hideYearAndDays: true}), '8837h 1m');
});

test('hides seconds and smaller units', () => {
	assert.equal(value(3_661_000, {hideSeconds: true}), '1h 1m');
});

test('returns the zero fallback when seconds are hidden', () => {
	assert.equal(value(0, {hideSeconds: true, verbose: true}), '0 milliseconds');
});
