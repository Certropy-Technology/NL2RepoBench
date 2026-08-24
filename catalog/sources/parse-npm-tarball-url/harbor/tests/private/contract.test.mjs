import assert from 'node:assert/strict';
import {test} from 'node:test';
import {call, inventory} from './test_client.mjs';

function value(input) {
  const response = call(input);
  assert.equal(response.ok, true, response.message);
  return response.value;
}

function error(input) {
  const response = call(input);
  assert.equal(response.ok, false);
  return response;
}

test('package root exposes one named ESM runtime export', () => {
  assert.deepEqual(inventory(), {
    packageName: 'parse-npm-tarball-url',
    packageVersion: '5.0.0',
    packageShape: true,
    runtimeEntry: true,
    declarationEntry: true,
    exportNames: ['parseNpmTarballUrl'],
  });
});

test('parses a simple registry tarball URL', () => {
  assert.deepEqual(value('http://registry.yarnpkg.com/foo/-/foo-1.0.0.tgz'), {
    host: 'registry.yarnpkg.com', name: 'foo', version: '1.0.0',
  });
});

test('preserves a prerelease version', () => {
  assert.deepEqual(value('http://registry.yarnpkg.com/foo/-/foo-1.0.0-beta.0.tgz'), {
    host: 'registry.yarnpkg.com', name: 'foo', version: '1.0.0-beta.0',
  });
});

test('decodes a percent-encoded scoped package', () => {
  assert.deepEqual(value('http://registry.npmjs.org/@foo%2fbar/-/bar-1.0.0.tgz'), {
    host: 'registry.npmjs.org', name: '@foo/bar', version: '1.0.0',
  });
});

test('parses an unencoded scoped package', () => {
  assert.deepEqual(value('http://registry.npmjs.org/@foo/bar/-/bar-1.0.0.tgz'), {
    host: 'registry.npmjs.org', name: '@foo/bar', version: '1.0.0',
  });
});

test('preserves a scoped prerelease version', () => {
  assert.deepEqual(value('http://registry.npmjs.org/@foo/bar/-/bar-1.0.0-beta.0.tgz'), {
    host: 'registry.npmjs.org', name: '@foo/bar', version: '1.0.0-beta.0',
  });
});

test('uses WHATWG host semantics and ignores query and fragment', () => {
  assert.deepEqual(value('https://registry.example.test:8443/foo/-/foo-2.0.0.tgz?download=1#file'), {
    host: 'registry.example.test:8443', name: 'foo', version: '2.0.0',
  });
});

test('keeps the original loose SemVer spelling', () => {
  assert.deepEqual(value('https://registry.example.test/foo/-/foo-v1.2.3.tgz'), {
    host: 'registry.example.test', name: 'foo', version: 'v1.2.3',
  });
});

test('returns null for an ordinary non-tarball path', () => {
  assert.equal(value('http://registry.npmjs.org/index.html'), null);
});

test('returns null for an invalid SemVer filename', () => {
  assert.equal(value('http://registry.yarnpkg.com/foo/-/foo-qar.tgz'), null);
});

test('returns null for malformed tarball filenames', () => {
  assert.equal(value('http://registry.yarnpkg.com/foo/-/qar.tgz'), null);
  assert.equal(value('http://registry.yarnpkg.com/foo/-/foo.tgz'), null);
  assert.equal(value('http://registry.yarnpkg.com/foo/-/.tgz'), null);
});

test('returns null when the parsed URL has no host', () => {
  assert.equal(value('file:///foo/-/foo-1.0.0.tgz'), null);
});

test('reports the required-url assertion for an empty value', () => {
  const response = error('');
  assert.equal(response.error_type, 'AssertionError');
  assert.equal(response.message, 'url is required');
});

test('reports the type assertion for a truthy non-string JSON value', () => {
  const response = error(42);
  assert.equal(response.error_type, 'AssertionError');
  assert.equal(response.message, 'url should be a string');
});
