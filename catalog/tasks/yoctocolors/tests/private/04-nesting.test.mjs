import assert from 'node:assert/strict';
import test from 'node:test';
import {concat, evaluate, literal, styled} from './test_client.mjs';

test('different foreground colors restore the outer color', () => {
	const expression = styled('red', concat('Error: ', styled('yellow', 'Warning'), ' continues in red'));
	assert.equal(evaluate(expression), '\u001B[31mError: \u001B[33mWarning\u001B[31m continues in red\u001B[39m');
});

test('dim nested in bold restores bold after SGR 22', () => {
	const expression = concat('Hello ', styled('dim', 'world'), ', ', styled('bold', concat('are ', styled('dim', 'you'), ' ok')), '?');
	assert.equal(evaluate(expression), 'Hello \u001B[2mworld\u001B[22m, \u001B[1mare \u001B[2myou\u001B[22m\u001B[1m ok\u001B[22m?');
});

test('bold nested in dim restores dim after SGR 22', () => {
	const expression = styled('dim', concat('outer ', styled('bold', 'inner'), ' rest'));
	assert.equal(evaluate(expression), '\u001B[2mouter \u001B[1minner\u001B[22m\u001B[2m rest\u001B[22m');
});

test('multiple dim segments inside bold each restore bold', () => {
	const expression = styled('bold', concat('a ', styled('dim', 'b'), ' c ', styled('dim', 'd'), ' e'));
	assert.equal(evaluate(expression), '\u001B[1ma \u001B[2mb\u001B[22m\u001B[1m c \u001B[2md\u001B[22m\u001B[1m e\u001B[22m');
});

test('bold self-nesting preserves the outer style', () => {
	assert.equal(evaluate(styled('bold', styled('bold', 'x'))), '\u001B[1m\u001B[1mx\u001B[22m\u001B[1m\u001B[22m');
});

test('dim self-nesting preserves the outer style', () => {
	assert.equal(evaluate(styled('dim', styled('dim', 'x'))), '\u001B[2m\u001B[2mx\u001B[22m\u001B[2m\u001B[22m');
});

test('same foreground color nesting reopens the outer color', () => {
	assert.equal(evaluate(styled('red', concat('a ', styled('red', 'b'), ' c'))), '\u001B[31ma \u001B[31mb\u001B[31m c\u001B[39m');
});

test('foreground and background colors nest independently', () => {
	assert.equal(evaluate(styled('red', concat('a ', styled('bgBlue', 'b'), ' c'))), '\u001B[31ma \u001B[44mb\u001B[49m c\u001B[39m');
});

test('background and foreground colors nest independently', () => {
	assert.equal(evaluate(styled('bgBlue', concat('a ', styled('red', 'b'), ' c'))), '\u001B[44ma \u001B[31mb\u001B[39m c\u001B[49m');
});

test('underline variants sharing SGR 24 restore the outer style', () => {
	assert.equal(evaluate(styled('underline', concat('a ', styled('underlineCurly', 'b'), ' c'))), '\u001B[4ma \u001B[4:3mb\u001B[4m c\u001B[24m');
});

test('underline color and underline shape close independently', () => {
	assert.equal(evaluate(styled('underlineRed', styled('underlineCurly', 'typo'))), '\u001B[58;5;1m\u001B[4:3mtypo\u001B[24m\u001B[59m');
});

test('literal SGR 22 in input causes bold to reopen', () => {
	assert.equal(evaluate(styled('bold', literal('x\u001B[22my'))), '\u001B[1mx\u001B[22m\u001B[1my\u001B[22m');
});

test('literal SGR 39 in input is replaced by a red reopen', () => {
	assert.equal(evaluate(styled('red', literal('x\u001B[39my'))), '\u001B[31mx\u001B[31my\u001B[39m');
});
