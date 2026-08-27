import assert from 'node:assert/strict';
import {test} from 'node:test';
import {request} from './test_client.mjs';

function value(operation, payload) {
  const response = request(operation, payload);
  assert.equal(response.ok, true, response.message);
  return response.value;
}

function error(operation, payload) {
  const response = request(operation, payload);
  assert.equal(response.ok, false);
  return response;
}

const option = (key, definition) => ({method: 'option', args: [key, definition]});

test('package root and helper exports have the required shape', () => {
  assert.deepEqual(value('inventory', {}), {
    uid: 10001,
    packageName: 'yargs',
    packageVersion: '18.1.0',
    type: 'module',
    rootExport: './index.mjs',
    helperExport: './helpers/helpers.mjs',
    rootDefaultCallable: true,
    commonJsNamedCallable: true,
    helperNames: ['Parser', 'applyExtends', 'hideBin'],
  });
});

test('parses positional arguments', () => {
  assert.deepEqual(value('parse', {argv: ['alpha', 'beta']}), {_: ['alpha', 'beta']});
});

test('parses long options and equals syntax', () => {
  assert.deepEqual(value('parse', {argv: ['--port=8080', '--name', 'api']}), {_: [], port: 8080, name: 'api'});
});

test('expands short option groups', () => {
  assert.deepEqual(value('parse', {argv: ['-abc']}), {_: [], a: true, b: true, c: true});
});

test('boolean options support no-prefix negation', () => {
  assert.deepEqual(value('parse', {argv: ['--no-cache'], methods: [{method: 'boolean', args: ['cache']}]}), {_: [], cache: false});
});

test('string options preserve numeric spelling', () => {
  assert.deepEqual(value('parse', {argv: ['--zip', '0012'], methods: [{method: 'string', args: ['zip']}]}), {_: [], zip: '0012'});
});

test('number options coerce numeric input', () => {
  assert.deepEqual(value('parse', {argv: ['--port', '42'], methods: [{method: 'number', args: ['port']}]}), {_: [], port: 42});
});

test('array options accumulate repeated values', () => {
  assert.deepEqual(value('parse', {argv: ['--tag', 'a', '--tag', 'b'], methods: [{method: 'array', args: ['tag']}]}), {_: [], tag: ['a', 'b']});
});

test('count options accumulate occurrences', () => {
  assert.deepEqual(value('parse', {argv: ['-vvv'], methods: [{method: 'count', args: ['v']}]}), {_: [], v: 3});
});

test('default values are inserted when absent', () => {
  assert.deepEqual(value('parse', {argv: [], methods: [{method: 'default', args: ['mode', 'safe']}]}), {_: [], mode: 'safe'});
});

test('aliases populate both names', () => {
  assert.deepEqual(value('parse', {argv: ['-n', 'Ada'], methods: [{method: 'alias', args: ['name', 'n']}, {method: 'string', args: ['name']}]}), {_: [], n: 'Ada', name: 'Ada'});
});

test('option definitions combine type alias and default', () => {
  assert.deepEqual(value('parse', {argv: [], methods: [option('port', {alias: 'p', type: 'number', default: 3000})]}), {_: [], port: 3000, p: 3000});
});

test('choices accept an allowlisted value', () => {
  assert.deepEqual(value('parse', {argv: ['--format', 'json'], methods: [{method: 'choices', args: ['format', ['json', 'text']]}]}), {_: [], format: 'json'});
});

test('choices reject an unknown value', () => {
  assert.match(error('parse', {argv: ['--format', 'xml'], methods: [{method: 'choices', args: ['format', ['json', 'text']]}]}).message, /Invalid values|Choices:/);
});

test('demandOption rejects a missing option', () => {
  assert.match(error('parse', {argv: [], methods: [{method: 'demandOption', args: ['token']}]}).message, /Missing required argument: token/);
});

test('requiresArg rejects an option without a value', () => {
  assert.match(error('parse', {argv: ['--name'], methods: [{method: 'requiresArg', args: ['name']}]}).message, /Not enough arguments following: name/);
});

test('nargs enforces the configured value count', () => {
  assert.match(error('parse', {argv: ['--pair', 'left'], methods: [{method: 'nargs', args: ['pair', 2]}]}).message, /Not enough arguments following: pair/);
});

test('implies accepts both options', () => {
  assert.deepEqual(value('parse', {argv: ['--user', 'a', '--token', 'b'], methods: [{method: 'implies', args: ['user', 'token']}]}), {_: [], user: 'a', token: 'b'});
});

test('implies rejects a missing dependent option', () => {
  assert.match(error('parse', {argv: ['--user', 'a'], methods: [{method: 'implies', args: ['user', 'token']}]}).message, /Implications failed|token/);
});

test('strict mode rejects unknown options', () => {
  assert.match(error('parse', {argv: ['--extra'], methods: [{method: 'strict', args: [true]}]}).message, /Unknown argument: extra/);
});

test('strictOptions preserves positional arguments', () => {
  assert.deepEqual(value('parse', {argv: ['input.txt'], methods: [{method: 'strictOptions', args: [true]}]}), {_: ['input.txt']});
});

test('camel-case expansion is enabled by default', () => {
  assert.deepEqual(value('parse', {argv: ['--dry-run']}), {_: [], 'dry-run': true, dryRun: true});
});

test('camel-case expansion can be disabled', () => {
  assert.deepEqual(value('parse', {argv: ['--dry-run'], methods: [{method: 'parserConfiguration', args: [{'camel-case-expansion': false}]}]}), {_: [], 'dry-run': true});
});

test('dot notation creates nested objects', () => {
  assert.deepEqual(value('parse', {argv: ['--db.host', 'localhost']}), {_: [], db: {host: 'localhost'}});
});

test('duplicate arguments become arrays by default', () => {
  assert.deepEqual(value('parse', {argv: ['--color', 'red', '--color', 'blue']}), {_: [], color: ['red', 'blue']});
});

test('double dash values remain positional by default', () => {
  assert.deepEqual(value('parse', {argv: ['--name', 'x', '--', '--literal']}), {_: ['--literal'], name: 'x'});
});

test('populate double dash stores trailing values separately', () => {
  assert.deepEqual(value('parse', {argv: ['a', '--', 'b', '--flag'], methods: [{method: 'parserConfiguration', args: [{'populate--': true}]}]}), {_: ['a'], '--': ['b', '--flag']});
});

test('unicode option values are preserved', () => {
  assert.deepEqual(value('parse', {argv: ['--name', 'Miyazaki Hayao']}), {_: [], name: 'Miyazaki Hayao'});
});

test('coerce can normalize a string', () => {
  assert.deepEqual(value('coerce', {argv: ['--name', 'ada'], key: 'name', mode: 'upper'}), {_: [], name: 'ADA'});
});

test('coerce can transform a number', () => {
  assert.deepEqual(value('coerce', {argv: ['--count', '4'], key: 'count', mode: 'increment'}), {_: [], count: 5});
});

test('coerce can produce an array', () => {
  assert.deepEqual(value('coerce', {argv: ['--items', 'a,b,c'], key: 'items', mode: 'csv'}), {_: [], items: ['a', 'b', 'c']});
});

test('check accepts a positive count', () => {
  assert.deepEqual(value('check', {argv: ['--count', '2'], methods: [{method: 'number', args: ['count']}], mode: 'positive-count'}), {_: [], count: 2});
});

test('check reports a domain validation error', () => {
  assert.match(error('check', {argv: ['--count', '0'], methods: [{method: 'number', args: ['count']}], mode: 'positive-count'}).message, /count must be positive/);
});

test('global middleware can augment parsed argv', () => {
  assert.deepEqual(value('middleware', {argv: ['file.txt'], mode: 'tag'}), {_: ['file.txt'], middlewareTag: 'applied'});
});

test('parseAsync matches synchronous parsing for synchronous configuration', () => {
  assert.deepEqual(value('parseAsync', {argv: ['--port', '9000'], methods: [{method: 'number', args: ['port']}]}), {_: [], port: 9000});
});

test('command handlers receive parsed command arguments', () => {
  assert.deepEqual(value('command', {argv: ['serve', '--port', '8080'], command: 'serve', builder: {port: {type: 'number', demandOption: true}}}), {
    parsed: {_: ['serve'], port: 8080},
    handled: {_: ['serve'], port: 8080},
  });
});

test('command positional values use builder declarations', () => {
  assert.deepEqual(value('command', {argv: ['copy', 'a.txt', 'b.txt'], command: 'copy <source> <dest>', builder: {}}), {
    parsed: {_: ['copy'], source: 'a.txt', dest: 'b.txt'},
    handled: {_: ['copy'], source: 'a.txt', dest: 'b.txt'},
  });
});

test('demandCommand rejects an empty command line', () => {
  assert.match(error('parse', {argv: [], methods: [{method: 'demandCommand', args: [1]}]}).message, /Not enough non-option arguments/);
});

test('help output includes usage and described options', () => {
  const help = value('help', {argv: [], usage: 'tool [options]', methods: [option('port', {type: 'number', describe: 'server port', default: 3000})]});
  assert.match(help, /tool \[options\]/);
  assert.match(help, /--port/);
  assert.match(help, /server port/);
  assert.match(help, /3000/);
});

test('hideBin removes the runtime and script prefix', () => {
  assert.deepEqual(value('helper', {name: 'hideBin', argv: ['/usr/bin/node', '/app/tool.mjs', '--port', '3']}), ['--port', '3']);
});

test('Parser helper parses without constructing a Yargs instance', () => {
  assert.deepEqual(value('helper', {name: 'Parser', argv: ['--name', 'Ada', '-v'], options: {boolean: ['v'], string: ['name']}}), {_: [], name: 'Ada', v: true});
});

test('Parser helper respects configuration options', () => {
  assert.deepEqual(value('helper', {name: 'Parser', argv: ['--dry-run'], options: {configuration: {'camel-case-expansion': false}}}), {_: [], 'dry-run': true});
});
