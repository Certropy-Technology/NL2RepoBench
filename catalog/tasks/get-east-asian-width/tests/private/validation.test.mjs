import test from 'node:test';
import assert from 'node:assert/strict';
import {call} from './test_client.mjs';

function assertTypeError(exportName, args) {
	const result = call(exportName, args);
	assert.equal(result.ok, false);
	assert.equal(result.exception_type, 'TypeError');
}

test('eastAsianWidth rejects a string code point', () => assertTypeError('eastAsianWidth', ['65']));
test('eastAsianWidthType rejects a string code point', () => assertTypeError('eastAsianWidthType', ['65']));
test('eastAsianWidth rejects a fractional code point', () => assertTypeError('eastAsianWidth', [65.5]));
test('eastAsianWidthType rejects a fractional code point', () => assertTypeError('eastAsianWidthType', [65.5]));
