import assert from 'node:assert/strict';
import {test} from 'node:test';
import {call, inventory} from './test_client.mjs';

function value(method, text, options) {
  const response = call(method, text, options);
  assert.equal(response.ok, true, response.message);
  return response.value;
}

function error(method, text, options) {
  const response = call(method, text, options);
  assert.equal(response.ok, false);
  return response;
}

test('package metadata and root entry contract', () => {
  const result = inventory();
  assert.equal(result.ok, true, result.message);
  assert.deepEqual(result.value, {
    packageName: 'prettier',
    packageVersion: '3.10.0-dev',
    packageType: 'commonjs',
    runtimeEntry: './index.mjs',
    declarationEntry: './index.d.ts',
    dependencyCount: 0,
    hasLifecycleHooks: false,
    requiredExportTypes: {
      check: 'function',
      format: 'function',
      formatWithCursor: 'function',
      version: 'string',
    },
    runtimeVersion: '3.10.0-dev',
  });
});

test('version export matches the package version', () => {
  const result = inventory();
  assert.equal(result.ok, true, result.message);
  assert.equal(result.value.runtimeVersion, result.value.packageVersion);
});

test('formats a basic Babel object expression', () => {
  assert.equal(value('format', 'const x={a:1,b:[2,3]}', {parser: 'babel'}), 'const x = { a: 1, b: [2, 3] };\n');
});

test('applies semicolon quote and arrow options', () => {
  assert.equal(value('format', 'const greeting="hello";const add=(x)=>x+1;', {parser: 'babel', semi: false, singleQuote: true, arrowParens: 'avoid'}), "const greeting = 'hello'\nconst add = x => x + 1\n");
});

test('wraps a Babel call at printWidth', () => {
  assert.equal(value('format', 'const result = doSomething(alpha, beta, gamma, delta);', {parser: 'babel', printWidth: 32}), 'const result = doSomething(\n  alpha,\n  beta,\n  gamma,\n  delta,\n);\n');
});

test('formats a TypeScript type', () => {
  assert.equal(value('format', 'type User={name:string;age?:number};', {parser: 'typescript'}), 'type User = { name: string; age?: number };\n');
});

test('formats compact JSON', () => {
  assert.equal(value('format', '{"b":2,"a":[1,2]}', {parser: 'json'}), '{ "b": 2, "a": [1, 2] }\n');
});

test('formats multiline JSON with tabs', () => {
  assert.equal(value('format', '{"items":[{"name":"alpha","enabled":true},{"name":"beta","enabled":false}]}', {parser: 'json', printWidth: 30, useTabs: true}), '{\n\t"items": [\n\t\t{\n\t\t\t"name": "alpha",\n\t\t\t"enabled": true\n\t\t},\n\t\t{\n\t\t\t"name": "beta",\n\t\t\t"enabled": false\n\t\t}\n\t]\n}\n');
});

test('formats CSS declarations and media rules', () => {
  assert.equal(value('format', 'a{color:red;margin:0  1px}@media(max-width:600px){a{display:none}}', {parser: 'css'}), 'a {\n  color: red;\n  margin: 0 1px;\n}\n@media (max-width: 600px) {\n  a {\n    display: none;\n  }\n}\n');
});

test('normalizes Markdown spacing and list indentation', () => {
  assert.equal(value('format', '#Title\n\nThis   is a sentence with   spaces.\n\n- one\n-   two', {parser: 'markdown'}), '#Title\n\nThis is a sentence with spaces.\n\n- one\n- two\n');
});

test('wraps Markdown prose at printWidth', () => {
  assert.equal(value('format', 'A short paragraph that should wrap across several lines because the configured width is deliberately small.', {parser: 'markdown', printWidth: 35, proseWrap: 'always'}), 'A short paragraph that should wrap\nacross several lines because the\nconfigured width is deliberately\nsmall.\n');
});

test('formats YAML sequences and flow mappings', () => {
  assert.equal(value('format', 'name: test\nitems:\n - one\n - two\nmeta: {enabled: true,count: 2}', {parser: 'yaml'}), 'name: test\nitems:\n  - one\n  - two\nmeta: { enabled: true, count: 2 }\n');
});

test('preserves compact inline HTML phrasing content', () => {
  assert.equal(value('format', '<div class="box"><span>Hello</span><span>world</span></div>', {parser: 'html'}), '<div class="box"><span>Hello</span><span>world</span></div>\n');
});

test('formats a GraphQL query', () => {
  assert.equal(value('format', 'query User($id:ID!){user(id:$id){id name email}}', {parser: 'graphql'}), 'query User($id: ID!) {\n  user(id: $id) {\n    id\n    name\n    email\n  }\n}\n');
});

test('check returns true for already formatted text', () => {
  assert.equal(value('check', 'const x = 1;\n', {parser: 'babel'}), true);
});

test('check returns false for unformatted text', () => {
  assert.equal(value('check', 'const x=1', {parser: 'babel'}), false);
});

test('formatWithCursor translates the cursor offset', () => {
  assert.deepEqual(value('formatWithCursor', 'const value={alpha:1,beta:2}', {parser: 'babel', cursorOffset: 15}), {
    formatted: 'const value = { alpha: 1, beta: 2 };\n',
    cursorOffset: 18,
    comments: [],
  });
});

test('format is idempotent for formatted JavaScript', () => {
  const text = 'function square(value) {\n  return value * value;\n}\n';
  assert.equal(value('format', text, {parser: 'babel'}), text);
});

test('missing parser reports UndefinedParserError', () => {
  const response = error('format', 'x', {});
  assert.equal(response.error_type, 'UndefinedParserError');
  assert.equal(response.message, "No parser and no file path given, couldn't infer a parser.");
});

test('unknown parser reports ConfigError', () => {
  const response = error('format', 'x', {parser: 'not-a-parser'});
  assert.equal(response.error_type, 'ConfigError');
  assert.equal(response.message, 'Couldn\'t resolve parser "not-a-parser".');
});
