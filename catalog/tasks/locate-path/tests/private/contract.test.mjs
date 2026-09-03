import assert from 'node:assert/strict';
import {test} from 'node:test';
import {request} from './test_client.mjs';

function value(scenario) {
  const response = request(scenario);
  assert.equal(response.ok, true, response.message);
  return response.value;
}

function failure(scenario) {
  const response = request(scenario);
  assert.equal(response.ok, false);
  return response;
}

test('package root exposes the frozen ESM contract', () => {
  assert.deepEqual(value('inventory'), {
    packageName: 'locate-path',
    packageVersion: '8.0.0',
    moduleType: 'module',
    runtimeEntry: './index.js',
    declarationEntry: './index.d.ts',
    exportNames: ['locatePath', 'locatePathSync'],
    dependency: '6.0.0',
    scriptNames: [],
    devDependencyNames: [],
    declarations: true,
  });
});

for (const [name, scenario, expected] of [
  ['async finds the first existing file', 'async-file', 'alpha.txt'],
  ['async returns undefined when no path exists', 'async-missing', null],
  ['async returns undefined for an empty iterable', 'async-empty', null],
  ['async accepts a Set iterable', 'async-set', 'beta.txt'],
  ['async accepts a generator iterable', 'async-generator', 'beta.txt'],
  ['async accepts a string cwd', 'async-cwd-string', 'alpha.txt'],
  ['async accepts a file URL cwd', 'async-cwd-url', 'alpha.txt'],
  ['async directory mode selects directories', 'async-directory', 'folder'],
  ['async both mode selects a file', 'async-both-file', 'alpha.txt'],
  ['async both mode selects a directory', 'async-both-directory', 'folder'],
  ['async returns the original relative spelling', 'async-original-path', './alpha.txt'],
  ['async skips entries that cannot be stated', 'async-bad-entry', 'alpha.txt'],
  ['sync finds the first existing file', 'sync-file', 'alpha.txt'],
  ['sync returns undefined when no path exists', 'sync-missing', null],
  ['sync returns undefined for an empty iterable', 'sync-empty', null],
  ['sync accepts a Set iterable', 'sync-set', 'beta.txt'],
  ['sync accepts a generator iterable', 'sync-generator', 'beta.txt'],
  ['sync accepts a string cwd', 'sync-cwd-string', 'alpha.txt'],
  ['sync accepts a file URL cwd', 'sync-cwd-url', 'alpha.txt'],
  ['sync directory mode selects directories', 'sync-directory', 'folder'],
  ['sync both mode selects a file', 'sync-both-file', 'alpha.txt'],
  ['sync both mode selects a directory', 'sync-both-directory', 'folder'],
  ['sync returns the original relative spelling', 'sync-original-path', './alpha.txt'],
  ['sync skips entries that cannot be stated', 'sync-bad-entry', 'alpha.txt'],
]) test(name, () => assert.deepEqual(value(scenario), expected));

for (const [name, scenario] of [
  ['async follows a file symlink by default', 'async-file-link'],
  ['async follows a directory symlink by default', 'async-directory-link'],
  ['sync follows a file symlink by default', 'sync-file-link'],
  ['sync follows a directory symlink by default', 'sync-directory-link'],
]) test(name, () => assert.equal(value(scenario), true));

for (const [name, scenario] of [
  ['async rejects a file symlink when disabled', 'async-file-link-disabled'],
  ['async rejects a directory symlink when disabled', 'async-directory-link-disabled'],
  ['async ignores a broken symlink', 'async-broken-link'],
  ['sync rejects a file symlink when disabled', 'sync-file-link-disabled'],
  ['sync rejects a directory symlink when disabled', 'sync-directory-link-disabled'],
  ['sync ignores a broken symlink', 'sync-broken-link'],
]) test(name, () => assert.equal(value(scenario), false));

for (const mode of ['async', 'sync']) {
  test(`${mode} rejects an unknown type`, () => {
    const response = failure(`${mode}-invalid-type`);
    assert.equal(response.errorType, 'Error');
    assert.equal(response.message, 'Invalid type specified: rainbow');
  });
  test(`${mode} rejects inherited object property names as type`, () => {
    const response = failure(`${mode}-prototype-type`);
    assert.equal(response.errorType, 'Error');
    assert.equal(response.message, 'Invalid type specified: toString');
  });
  test(`${mode} rejects a non-file URL cwd`, () => {
    const response = failure(`${mode}-invalid-url`);
    assert.equal(response.errorType, 'TypeError');
    assert.match(response.message, /file URL|scheme file/i);
  });
  test(`${mode} propagates iterable failures`, () => {
    const response = failure(`${mode}-iterator-error`);
    assert.equal(response.errorType, 'RangeError');
    assert.equal(response.message, 'iterator failed');
  });
}

test('async accepts explicit bounded concurrency and unordered completion', () => {
  assert.equal(value('async-options'), 'beta.txt');
});

test('async rejects zero concurrency', () => {
  assert.equal(failure('async-zero-concurrency').errorType, 'TypeError');
});
