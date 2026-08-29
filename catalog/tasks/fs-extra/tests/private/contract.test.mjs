import assert from 'node:assert/strict';
import test from 'node:test';

import {request} from './test_client.mjs';

function value(operation) {
  const response = request(operation);
  assert.equal(response.ok, true, JSON.stringify(response.error));
  return response.value;
}

const EXTRA_NAMES = [
  'copy', 'copySync', 'emptyDir', 'emptyDirSync', 'emptydir', 'emptydirSync',
  'ensureDir', 'ensureDirSync', 'mkdirs', 'mkdirsSync', 'mkdirp', 'mkdirpSync',
  'ensureFile', 'ensureFileSync', 'createFile', 'createFileSync',
  'ensureLink', 'ensureLinkSync', 'createLink', 'createLinkSync',
  'ensureSymlink', 'ensureSymlinkSync', 'createSymlink', 'createSymlinkSync',
  'move', 'moveSync', 'outputFile', 'outputFileSync', 'pathExists',
  'pathExistsSync', 'readJson', 'readJsonSync', 'readJSON', 'readJSONSync',
  'writeJson', 'writeJsonSync', 'writeJSON', 'writeJSONSync', 'outputJson',
  'outputJsonSync', 'outputJSON', 'outputJSONSync', 'remove', 'removeSync',
];

test('package metadata identifies fs-extra 11.4.0', () => {
  const result = value('metadata');
  assert.equal(result.name, 'fs-extra');
  assert.equal(result.version, '11.4.0');
  assert.equal(result.main, './lib/index.js');
  assert.deepEqual(result.engines, {node: '>=14.14'});
});

test('package exports expose CommonJS root and ESM subpath', () => {
  assert.deepEqual(value('metadata').exports, {'.': './lib/index.js', './esm': './lib/esm.mjs'});
});

test('CommonJS root exposes every documented extra function', () => {
  assert.deepEqual(value('cjs-extra-shape'), Object.fromEntries(EXTRA_NAMES.map(name => [name, 'function'])));
});

test('CommonJS root exposes selected graceful-fs compatibility members', () => {
  const result = value('cjs-fs-shape');
  for (const name of Object.keys(result)) {
    assert.equal(result[name], ['constants', 'promises'].includes(name) ? 'object' : 'function', name);
  }
});

test('CommonJS readFile supports the promise form', () => {
  assert.deepEqual(value('cjs-read-promise'), {then: 'function', value: 'promise-value'});
});

test('ESM subpath has the exact documented named export set', () => {
  const expected = [...EXTRA_NAMES.filter(name => !['createFile', 'createFileSync', 'createLink', 'createLinkSync', 'createSymlink', 'createSymlinkSync'].includes(name)),
    'createFile', 'createFileSync', 'createLink', 'createLinkSync', 'createSymlink', 'createSymlinkSync', 'default'].sort();
  assert.deepEqual(value('esm-shape').keys, expected);
});

test('ESM default export contains only callable extra methods', () => {
  const result = value('esm-shape').defaultTypes;
  assert.equal(Object.keys(result).length, 44);
  assert.ok(Object.values(result).every(kind => kind === 'function'));
});

test('ensureDir creates nested directories and resolves the created path', () => {
  const result = value('ensure-dir-async');
  assert.deepEqual(result.directories, [true, true, true]);
  assert.equal(result.values.length, 3);
  assert.ok(result.values.every(path => typeof path === 'string'));
});

test('mkdirs and mkdirp are asynchronous ensureDir aliases', () => {
  assert.deepEqual(value('ensure-dir-async').directories, [true, true, true]);
});

test('synchronous directory aliases create nested directories', () => {
  const result = value('ensure-dir-sync');
  assert.deepEqual(result.directories, [true, true, true]);
  assert.equal(result.values.length, 3);
  assert.ok(result.values.every(path => typeof path === 'string'));
});

test('ensureFile creates parents without truncating an existing file', () => {
  const result = value('ensure-file-async');
  assert.equal(result.existing, 'keep-me');
  assert.equal(result.created, '');
});

test('createFile is an asynchronous ensureFile alias', () => {
  assert.deepEqual(value('ensure-file-async').values, [null, null]);
});

test('synchronous file aliases create and preserve files', () => {
  const result = value('ensure-file-sync');
  assert.deepEqual(result, {existing: 'keep-me', created: '', values: [null, null]});
});

test('ensureLink creates an idempotent hard link and parent directories', () => {
  assert.deepEqual(value('ensure-link-async'), {content: 'linked', sameInode: true});
});

test('ensureLinkSync creates an idempotent hard link', () => {
  assert.deepEqual(value('ensure-link-sync'), {content: 'linked', sameInode: true});
});

test('ensureSymlink creates an idempotent readable symbolic link', () => {
  const result = value('ensure-symlink-async');
  assert.equal(result.symbolic, true);
  assert.equal(result.content, 'linked');
  assert.ok(result.target.endsWith('source.txt'));
});

test('ensureSymlinkSync creates an idempotent readable symbolic link', () => {
  const result = value('ensure-symlink-sync');
  assert.equal(result.symbolic, true);
  assert.equal(result.content, 'linked');
});

test('outputFile creates parents, overwrites, and resolves undefined', () => {
  assert.deepEqual(value('output-file-async'), {content: 'second', value: null});
});

test('outputFileSync creates parents and overwrites', () => {
  assert.deepEqual(value('output-file-sync'), {content: 'second', value: null});
});

test('pathExists resolves true for present and false for absent paths', () => {
  assert.deepEqual(value('path-exists-async'), {present: true, absent: false});
});

test('pathExistsSync returns true for present and false for absent paths', () => {
  assert.deepEqual(value('path-exists-sync'), {present: true, absent: false});
});

test('emptyDir removes descendants, preserves the directory, and creates a missing directory', () => {
  assert.deepEqual(value('empty-dir-async'), {existing: true, existingEntries: [], missing: true});
});

test('emptyDirSync and emptydirSync share synchronous semantics', () => {
  assert.deepEqual(value('empty-dir-sync'), {existing: true, existingEntries: [], missing: true});
});

test('remove recursively deletes paths and is idempotent', () => {
  assert.deepEqual(value('remove-async'), {exists: false, values: [null, null]});
});

test('removeSync recursively deletes paths and is idempotent', () => {
  assert.deepEqual(value('remove-sync'), {exists: false, values: [null, null]});
});

test('writeJson and readJson round trip data with formatting options', () => {
  const result = value('json-async');
  assert.deepEqual(result.value, {name: 'value', list: [1, 2]});
  assert.ok(result.raw.includes('\r\n  "name"'));
  assert.ok(result.raw.endsWith('\r\n'));
});

test('writeJSON and readJSON are asynchronous aliases', () => {
  assert.deepEqual(value('json-alias-async'), {value: {alias: true}});
});

test('readJson with throws false resolves null for invalid JSON', () => {
  assert.equal(value('json-invalid-async').suppressed, null);
});

test('readJson rejects invalid JSON by default', () => {
  const result = value('json-invalid-async').thrown;
  assert.equal(result.name, 'SyntaxError');
  assert.match(result.message, /JSON|position|property/i);
});

test('outputJson and outputJSON create parents and write JSON', () => {
  assert.deepEqual(value('output-json-async'), {value: {alias: true}, parent: true, values: [null, null]});
});

test('writeJsonSync and readJsonSync round trip data with formatting options', () => {
  const result = value('json-sync');
  assert.deepEqual(result.value, {name: 'value', list: [1, 2]});
  assert.ok(result.raw.includes('\r\n  "name"'));
});

test('writeJSONSync and readJSONSync are synchronous aliases', () => {
  assert.deepEqual(value('json-alias-sync'), {value: {alias: true}});
});

test('readJsonSync with throws false returns null for invalid JSON', () => {
  assert.equal(value('json-invalid-sync').suppressed, null);
});

test('readJsonSync throws for invalid JSON by default', () => {
  assert.equal(value('json-invalid-sync').thrown.name, 'SyntaxError');
});

test('outputJsonSync and outputJSONSync create parents and write JSON', () => {
  assert.deepEqual(value('output-json-sync'), {value: {alias: true}, parent: true, values: [null, null]});
});

test('copy recursively copies a directory and creates destination parents', () => {
  assert.deepEqual(value('copy-async'), {a: 'a', b: 'b', value: null});
});

test('copy accepts a synchronous filter callback', () => {
  assert.deepEqual(value('copy-filter-async'), {entries: ['keep.txt']});
});

test('copy honors overwrite false and errorOnExist true', () => {
  const result = value('copy-conflict-async');
  assert.equal(result.content, 'destination');
  assert.match(result.error.message, /already exists/);
});

test('copy preserves symbolic links when dereference is false', () => {
  assert.deepEqual(value('copy-symlink-async'), {symbolic: true, content: 'target'});
});

test('copySync recursively copies and preserves timestamps', () => {
  const result = value('copy-sync');
  assert.equal(result.content, 'value');
  assert.equal(result.mtime, 946684800000);
  assert.equal(result.value, null);
});

test('copySync honors conflict options', () => {
  const result = value('copy-conflict-sync');
  assert.equal(result.content, 'destination');
  assert.match(result.error.message, /already exists/);
});

test('copy rejects identical source and destination', () => {
  assert.match(value('copy-errors').same.message, /same|identical/i);
});

test('copy rejects copying a directory into itself', () => {
  assert.match(value('copy-errors').child.message, /subdirectory|itself/i);
});

test('move relocates a directory and creates destination parents', () => {
  assert.deepEqual(value('move-async'), {source: false, content: 'value', value: null});
});

test('move overwrite replaces an existing destination', () => {
  assert.deepEqual(value('move-overwrite-async'), {source: false, content: 'source'});
});

test('moveSync relocates a directory and creates destination parents', () => {
  assert.deepEqual(value('move-sync'), {source: false, content: 'value', value: null});
});

test('moveSync rejects an existing destination by default', () => {
  const result = value('move-conflict-sync');
  assert.equal(result.source, true);
  assert.equal(result.content, 'old');
  assert.match(result.error.message, /already exists/);
});

test('move rejects identical source and destination', () => {
  assert.match(value('move-errors').same.message, /same|identical/i);
});

test('move rejects moving a directory into itself', () => {
  assert.match(value('move-errors').child.message, /subdirectory|itself/i);
});

test('asynchronous extras retain optional Node-style callbacks', () => {
  assert.deepEqual(value('callbacks'), {
    outputReturn: null,
    copyReturn: null,
    existsValue: true,
    output: 'callback-value',
    copied: 'copy-value',
  });
});
