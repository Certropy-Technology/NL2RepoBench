import assert from 'node:assert/strict';
import test from 'node:test';
import {coercible, evaluate, evaluateDefault, styled} from './test_client.mjs';

test('active styles use JavaScript string coercion', () => {
	assert.equal(evaluate(styled('red', 123)), '\u001B[31m123\u001B[39m');
	assert.equal(evaluate(styled('bold', coercible('x'))), '\u001B[1mx\u001B[22m');
});

test('active styles wrap an empty string', () => {
	assert.equal(evaluate(styled('red', '')), '\u001B[31m\u001B[39m');
});

test('the default namespace is behaviorally equivalent', () => {
	assert.equal(evaluateDefault(styled('red', 'Error')), '\u001B[31mError\u001B[39m');
});

test('FORCE_COLOR zero makes formatters no-ops', () => {
	assert.equal(evaluate(styled('red', 'foo'), {forceColor: '0'}), 'foo');
});
