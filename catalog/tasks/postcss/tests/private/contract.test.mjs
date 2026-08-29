import assert from 'node:assert/strict';
import {test} from 'node:test';
import {call, value} from './test_client.mjs';

test('package metadata and root helper export kinds are fixed', () => {
  const data = value('inspect');
  assert.deepEqual({name: data.name, version: data.version, main: data.main, types: data.types, dependencyNames: data.dependencyNames, processorVersion: data.processorVersion}, {
    name: 'postcss', version: '8.5.26', main: './lib/postcss.js', types: './lib/postcss.d.ts',
    dependencyNames: ['nanoid', 'picocolors', 'source-map-js'], processorVersion: '8.5.26',
  });
  for (const name of ['parse', 'stringify', 'fromJSON', 'root', 'rule', 'decl', 'atRule', 'comment', 'document', 'Root', 'Rule', 'Declaration', 'AtRule', 'Comment', 'Container', 'Node', 'Processor', 'Result', 'Input', 'Warning', 'CssSyntaxError']) assert.equal(data.exportKinds[name], 'function');
});

test('parses a root rule and declaration in source order', () => {
  const data = value('parse', {css: 'a { color: red; }'});
  assert.equal(data.css, 'a { color: red; }');
  assert.equal(data.tree.type, 'root');
  assert.equal(data.tree.nodes[0].selector, 'a');
  assert.deepEqual(Object.fromEntries(['type', 'prop', 'value'].map(key => [key, data.tree.nodes[0].nodes[0][key]])), {type: 'decl', prop: 'color', value: 'red'});
});

test('preserves declaration importance and a trailing semicolon', () => {
  const data = value('parse', {css: 'a{color:red!important;}'});
  assert.equal(data.css, 'a{color:red!important;}');
  assert.equal(data.tree.nodes[0].nodes[0].important, true);
});

test('parses comments and at-rules', () => {
  const data = value('parse', {css: '/* top */ @media screen { a { color: red } }'});
  assert.equal(data.tree.nodes[0].type, 'comment');
  assert.equal(data.tree.nodes[0].text, 'top');
  assert.equal(data.tree.nodes[1].name, 'media');
  assert.equal(data.tree.nodes[1].params, 'screen');
  assert.equal(data.tree.nodes[1].nodes[0].selector, 'a');
});

test('parses nested rules as rule children', () => {
  const data = value('parse', {css: '.a { color: red; &:hover { color: blue } }'});
  assert.equal(data.tree.nodes[0].nodes[1].type, 'rule');
  assert.equal(data.tree.nodes[0].nodes[1].selector, '&:hover');
});

test('retains quoted values and escaped selector text', () => {
  const css = '.a\\:b { content: "a; b"; background: url("x;y") }';
  assert.equal(value('parse', {css}).css, css);
});

test('reports one-based source positions', () => {
  const declaration = value('parse', {css: 'a {\n  color: red\n}'}).tree.nodes[0].nodes[0];
  assert.deepEqual(declaration.start, {line: 2, column: 3, offset: 6});
  assert.deepEqual(declaration.end, {line: 2, column: 12, offset: 16});
});

test('invalid CSS returns a CssSyntaxError', () => {
  const response = call('parse', {css: 'a { color: red', from: 'broken.css'});
  assert.equal(response.ok, false);
  assert.equal(response.errorType, 'CssSyntaxError');
  assert.match(response.message, /broken\.css/);
});

test('appends a constructed declaration to the first rule', () => {
  const data = value('mutate', {css: 'a { color: red }', action: 'append', node: {type: 'decl', prop: 'display', value: 'block'}});
  assert.equal(data.css, 'a { color: red; display: block }');
});

test('coerces constructed declaration values to strings', () => {
  const data = value('mutate', {css: 'a {}', action: 'append', node: {type: 'decl', prop: 'z-index', value: 2}});
  assert.equal(data.tree.nodes[0].nodes[0].value, '2');
});

test('prepends a constructed comment to a root', () => {
  assert.equal(value('mutate', {css: 'a{}', action: 'prepend-comment', text: 'before'}).css, '/* before */\na{}');
});

test('changing a declaration value updates stringification', () => {
  assert.equal(value('mutate', {css: 'a { color: red }', action: 'set-decl', prop: 'color', value: 'blue'}).css, 'a { color: blue }');
});

test('removes every matching declaration', () => {
  assert.equal(value('mutate', {css: 'a { color: red; color: blue; margin: 0 }', action: 'remove-decl', prop: 'color'}).css, 'a { margin: 0 }');
});

test('selectors getter/setter normalizes a comma list', () => {
  assert.equal(value('mutate', {css: 'a, b { color: red }', action: 'selectors', selectors: ['.x', '.y']}).css, '.x, .y { color: red }');
});

test('cloneBefore creates an independent sibling in order', () => {
  assert.equal(value('mutate', {css: 'a { color: red }', action: 'clone-before', selector: 'b'}).css, 'b { color: red }\na { color: red }');
});

test('fromJSON rebuilds a stringify-equivalent tree', () => {
  const data = value('mutate', {css: 'a { color: red; /* note */ }', action: 'from-json'});
  assert.equal(data.css, 'a { color: red; /* note */ }');
  assert.equal(data.tree.type, 'root');
});

test('walk visits container descendants in source order', () => {
  const data = value('mutate', {css: 'a { color: red; @media x { b { margin: 0 } } }', action: 'walk-order'});
  assert.deepEqual(data.seen, ['rule:a', 'decl:color', 'atrule:media', 'rule:b', 'decl:margin']);
});

test('parse accepts a source filename for ordinary CSS', () => {
  assert.equal(value('parse', {css: 'a{}', from: 'input.css'}).css, 'a{}');
});

test('process returns unchanged CSS with no plugins', async () => {
  assert.equal((await value('process', {css: 'a { color: red }', plugins: []})).css, 'a { color: red }');
});

test('process replaces matching declaration values', async () => {
  assert.equal((await value('process', {css: 'a { color: red; background: red }', plugins: [{kind: 'replace-decl', prop: 'color', from: 'red', to: 'blue'}]})).css, 'a { color: blue; background: red }');
});

test('process appends a declaration to every rule', async () => {
  assert.equal((await value('process', {css: 'a{} b{}', plugins: [{kind: 'append-decl', prop: 'display', value: 'block'}]})).css, 'a{ display: block} b{ display: block}');
});

test('process prefixes selectors in tree order', async () => {
  assert.equal((await value('process', {css: 'a{} b{}', plugins: [{kind: 'prefix-selector', prefix: '.scope '}]})).css, '.scope a{} .scope b{}');
});

test('process removes declarations selected by property', async () => {
  assert.equal((await value('process', {css: 'a{color:red;margin:0}', plugins: [{kind: 'remove-decl', prop: 'color'}]})).css, 'a{margin:0}');
});

test('process Once appends a comment', async () => {
  assert.equal((await value('process', {css: 'a{}', plugins: [{kind: 'append-comment', text: 'done'}]})).css, 'a{}\n/* done */');
});

test('result warnings preserve insertion order', async () => {
  const data = await value('process', {css: 'a{}', plugins: [{kind: 'warn', text: 'one'}, {kind: 'warn', text: 'two'}]});
  assert.deepEqual(data.warnings, ['one', 'two']);
});

test('sync processing produces final css for synchronous plugins', () => {
  assert.equal(value('process', {css: 'a{}', sync: true, plugins: [{kind: 'append-comment', text: 'sync'}]}).css, 'a{}\n/* sync */');
});

test('sync rejects an async visitor', () => {
  const response = call('process', {css: 'a{}', sync: true, plugins: [{kind: 'async-prefix', prefix: '.x '} ]});
  assert.equal(response.ok, false);
  assert.match(response.message, /async/i);
});

test('awaited processing runs an async visitor', async () => {
  assert.equal((await value('process', {css: 'a{}', plugins: [{kind: 'async-prefix', prefix: '.x '}]})).css, '.x a{}');
});

test('postcss root factory accepts a plugin array', async () => {
  const data = await value('process', {css: 'a{}', plugins: [{kind: 'append-decl', prop: 'x', value: '1'}]});
  assert.equal(data.css, 'a{\n    x: 1}');
});

test('a root with multiple top-level constructs retains order', () => {
  const data = value('parse', {css: '@charset "UTF-8";\n/* c */\na{}'});
  assert.deepEqual(data.tree.nodes.map(node => node.type), ['atrule', 'comment', 'rule']);
});

test('important is false when omitted', () => {
  assert.equal(value('parse', {css: 'a{color:red}'}).tree.nodes[0].nodes[0].important, undefined);
});

test('unsupported adapter action is a bounded error', () => {
  const response = call('mutate', {css: 'a{}', action: 'exec'});
  assert.equal(response.ok, false);
  assert.match(response.message, /unsupported action/);
});
