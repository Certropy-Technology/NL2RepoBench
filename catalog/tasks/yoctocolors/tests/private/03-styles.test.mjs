import assert from 'node:assert/strict';
import test from 'node:test';
import {STYLE_CASES, evaluate, styled} from './test_client.mjs';

for (const [name, open, close] of STYLE_CASES.slice(41)) {
	test(`${name} emits its ANSI open and close sequences`, () => {
		assert.equal(evaluate(styled(name, 'foo')), `\u001B[${open}mfoo\u001B[${close}m`);
	});
}
