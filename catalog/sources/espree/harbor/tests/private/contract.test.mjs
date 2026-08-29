import assert from 'node:assert/strict';
import {test} from 'node:test';
import {call, inventory} from './test_client.mjs';

function value(operation, payload) {
  const response = call(operation, payload);
  assert.equal(response.ok, true, response.message);
  return response.value;
}
function error(operation, payload) {
  const response = call(operation, payload);
  assert.equal(response.ok, false);
  return response;
}

test('exports the documented root surface and version', () => {
  const result = inventory();
  assert.equal(result.value.packageName, 'espree');
  assert.equal(result.value.packageVersion, '11.2.0');
  assert.deepEqual(result.value.exportNames, ['Syntax', 'VisitorKeys', 'latestEcmaVersion', 'name', 'parse', 'supportedEcmaVersions', 'tokenize', 'version']);
});
test('reports current and supported ECMAScript versions', () => {
  const result = inventory().value;
  assert.equal(result.latestEcmaVersion, 17);
  assert.deepEqual(result.supportedEcmaVersions, [3, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17]);
});
test('parses a basic script into an ESTree Program', () => {
  const ast = value('parse', {code: 'let answer = 42;', options: {ecmaVersion: 6}});
  assert.deepEqual({type: ast.type, sourceType: ast.sourceType, bodyType: ast.body[0].type, kind: ast.body[0].kind}, {type: 'Program', sourceType: 'script', bodyType: 'VariableDeclaration', kind: 'let'});
  assert.equal(ast.body[0].declarations[0].id.name, 'answer');
});
test('supports module source type and imports', () => {
  const ast = value('parse', {code: 'import x from "x";', options: {ecmaVersion: 6, sourceType: 'module'}});
  assert.equal(ast.sourceType, 'module');
  assert.equal(ast.body[0].type, 'ImportDeclaration');
});
test('supports commonjs return', () => {
  const ast = value('parse', {code: 'return value;', options: {ecmaVersion: 6, sourceType: 'commonjs'}});
  assert.equal(ast.sourceType, 'commonjs');
  assert.equal(ast.body[0].type, 'ReturnStatement');
});
test('adds ranges and locations when requested', () => {
  const ast = value('parse', {code: 'const x = 1;', options: {ecmaVersion: 6, range: true, loc: true}});
  assert.deepEqual(ast.range, [0, 12]);
  assert.deepEqual(ast.loc.start, {line: 1, column: 0});
  assert.deepEqual(ast.loc.end, {line: 1, column: 12});
  assert.deepEqual(ast.body[0].declarations[0].id.range, [6, 7]);
});
test('collects comments in parse output', () => {
  const ast = value('parse', {code: '// hello\nanswer;', options: {comment: true, range: true, loc: true}});
  assert.equal(ast.comments.length, 1);
  assert.deepEqual(ast.comments[0], {type: 'Line', value: ' hello', start: 0, end: 8, range: [0, 8], loc: {start: {line: 1, column: 0}, end: {line: 1, column: 0 + 8}}});
});
test('collects tokens in parse output', () => {
  const ast = value('parse', {code: 'const x = 1;', options: {ecmaVersion: 6, tokens: true, range: true}});
  assert.equal(ast.tokens.length, 5);
  assert.deepEqual(ast.tokens.map(token => token.type), ['Keyword', 'Identifier', 'Punctuator', 'Numeric', 'Punctuator']);
  assert.deepEqual(ast.tokens[1].range, [6, 7]);
});
test('tokenize always returns tokens', () => {
  const tokens = value('tokenize', {code: 'let foo = "bar";', options: {ecmaVersion: 6}});
  assert.deepEqual(tokens.map(token => [token.type, token.value]), [['Keyword', 'let'], ['Identifier', 'foo'], ['Punctuator', '='], ['String', '"bar"'], ['Punctuator', ';']]);
});
test('tokenizes regular expressions with metadata', () => {
  const tokens = value('tokenize', {code: 'const r = /foo/gu;', options: {ecmaVersion: 2015}});
  const regex = tokens.find(token => token.type === 'RegularExpression');
  assert.deepEqual(regex.regex, {pattern: 'foo', flags: 'gu'});
  assert.equal(regex.value, '/foo/gu');
});
test('supports optional chaining and nullish coalescing', () => {
  const ast = value('parse', {code: 'value?.name ?? "unknown";', options: {ecmaVersion: 2020}});
  assert.equal(ast.body[0].expression.type, 'LogicalExpression');
  assert.equal(ast.body[0].expression.operator, '??');
});
test('supports JSX when enabled', () => {
  const ast = value('parse', {code: 'const view = <main>Hello</main>;', options: {ecmaVersion: 2024, ecmaFeatures: {jsx: true}}});
  assert.equal(ast.body[0].declarations[0].init.type, 'JSXElement');
  assert.equal(ast.body[0].declarations[0].init.openingElement.name.name, 'main');
});
test('tokenizes JSX text as JSXText', () => {
  const tokens = value('tokenize', {code: '<div>hi</div>', options: {ecmaVersion: 2024, ecmaFeatures: {jsx: true}}});
  assert.equal(tokens.some(token => token.type === 'JSXText' && token.value === 'hi'), true);
});
test('supports hashbang comments', () => {
  const ast = value('parse', {code: '#!/usr/bin/env node\n42;', options: {ecmaVersion: 2023, comment: true}});
  assert.equal(ast.comments[0].type, 'Hashbang');
});
test('supports implied strict mode', () => {
  const ast = value('parse', {code: 'function f(){ return 1; }', options: {ecmaVersion: 6, ecmaFeatures: {impliedStrict: true}}});
  assert.equal(ast.body[0].type, 'FunctionDeclaration');
});
test('normalizes year based ECMAScript editions', () => {
  const ast = value('parse', {code: 'let x = 1;', options: {ecmaVersion: 2015}});
  assert.equal(ast.body[0].kind, 'let');
});
test('accepts latest edition', () => {
  const ast = value('parse', {code: 'const x = 1;', options: {ecmaVersion: 'latest'}});
  assert.equal(ast.body[0].type, 'VariableDeclaration');
});
test('reports Espree syntax error position', () => {
  const result = error('parse', {code: 'const = 1;', options: {ecmaVersion: 2024}});
  assert.equal(result.error_type, 'SyntaxError');
  assert.equal(result.message, 'Unexpected token =');
  assert.equal(result.lineNumber, 1);
  assert.equal(result.column, 7);
});
test('rejects invalid ECMAScript version', () => {
  const result = error('parse', {code: 'x;', options: {ecmaVersion: 4}});
  assert.equal(result.message, 'Invalid ecmaVersion.');
});
test('rejects module mode before ES2015', () => {
  const result = error('parse', {code: 'x;', options: {ecmaVersion: 5, sourceType: 'module'}});
  assert.match(result.message, /sourceType 'module' is not supported/);
});
test('rejects allowReserved for modern editions', () => {
  const result = error('parse', {code: 'const x = 1;', options: {ecmaVersion: 2024, allowReserved: true}});
  assert.match(result.message, /allowReserved.*only supported/);
});
test('rejects invalid source type', () => {
  const result = error('parse', {code: 'x;', options: {sourceType: 'invalid'}});
  assert.equal(result.message, 'Invalid sourceType.');
});
test('reports source locations on statements', () => {
  const ast = value('parse', {code: 'x;\n', options: {loc: true}});
  assert.deepEqual(ast.body[0].loc, {start: {line: 1, column: 0}, end: {line: 1, column: 2}});
});
test('tokenize supports ranges and locations', () => {
  const tokens = value('tokenize', {code: 'a + b', options: {range: true, loc: true}});
  assert.deepEqual(tokens[0].range, [0, 1]);
  assert.deepEqual(tokens[2].loc, {start: {line: 1, column: 4}, end: {line: 1, column: 5}});
});
