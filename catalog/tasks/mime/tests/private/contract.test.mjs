import assert from 'node:assert/strict';
import test from 'node:test';

const client = await import(process.env.NODE_TEST_CLIENT ?? './test_client.mjs');

test('package shape and subpath exports', () => {
  assert.deepEqual(client.inventory(), {
    name: 'mime', version: '4.1.0', type: 'module',
    exports: ['.', './lite', './package.json', './types/other.js', './types/standard.js'],
    named: ['Mime', 'default'], liteNamed: ['Mime', 'default'],
    classCallable: true, cli: true, packageJsonReadable: true,
  });
});
test('built-in default is immutable', () => assert.equal(client.immutable(), true));
test('getType recognizes a bare extension', () => assert.equal(client.callCandidate('getType', 'txt'), 'text/plain'));
test('getType recognizes slash paths', () => assert.equal(client.callCandidate('getType', 'dir/text.txt'), 'text/plain'));
test('getType recognizes backslash paths', () => assert.equal(client.callCandidate('getType', 'dir\\text.txt'), 'text/plain'));
test('getType is case insensitive', () => assert.equal(client.callCandidate('getType', 'TEXT.TXT'), 'text/plain'));
test('getType recognizes dotted filenames', () => assert.equal(client.callCandidate('getType', '.config.json'), 'application/json'));
test('getType returns null for unknown extension', () => assert.equal(client.callCandidate('getType', 'file.bogus'), null));
test('getType returns null for extensionless path', () => assert.equal(client.callCandidate('getType', '/txt'), null));
test('getType returns null for non-string', () => assert.equal(client.callCandidate('getType', 42), null));
test('getExtension returns default extension', () => assert.equal(client.callCandidate('getExtension', 'text/html'), 'html'));
test('getExtension trims and ignores charset', () => assert.equal(client.callCandidate('getExtension', ' text/HTML; charset=UTF-8 '), 'html'));
test('getExtension is case insensitive', () => assert.equal(client.callCandidate('getExtension', 'APPLICATION/JSON'), 'json'));
test('getExtension returns null for unknown type', () => assert.equal(client.callCandidate('getExtension', 'application/x-bogus'), null));
test('getExtension returns null for non-string', () => assert.equal(client.callCandidate('getExtension', null), null));
test('getAllExtensions returns all jpeg extensions', () => assert.deepEqual(client.callCandidate('getAllExtensions', 'image/jpeg'), ['jpe', 'jpeg', 'jpg']));
test('getAllExtensions returns null for unknown type', () => assert.equal(client.callCandidate('getAllExtensions', 'application/x-bogus'), null));
test('built-in database includes wasm', () => assert.equal(client.callCandidate('getType', 'wasm'), 'application/wasm'));
test('built-in database includes json', () => assert.equal(client.callCandidate('getType', 'json'), 'application/json'));
test('custom constructor defines maps in order', () => assert.deepEqual(client.custom(), {typeA: 'text/a', extB: 'b', same: true, typeC: 'text/c'}));
test('custom mappings are case insensitive', () => assert.deepEqual(client.customCase(), ['text/upper', 'up']));
test('define rejects conflicting extension without force', () => assert.equal(client.customConflict().threw, true));
test('define conflict reports useful message', () => assert.match(client.customConflict().message, /force=true/));
test('define force replaces an extension mapping', () => assert.deepEqual(client.customForce(), ['text/c', 'text/c', 'b']));
test('starred extensions remain in the type set', () => assert.deepEqual(client.customStar().all, ['a', 'b']));
test('starred extensions do not claim the extension mapping', () => assert.equal(client.customStar().mapped, 'text/b'));
test('lite includes standard types', () => assert.equal(client.callLite('getType', 'html'), 'text/html'));
test('lite omits vendor-only types', () => assert.equal(client.callLite('getType', '7z'), null));
test('CLI maps extension to type', () => assert.deepEqual(client.cli('mpeg'), {status: 0, stdout: 'video/mpeg\n', stderr: ''}));
test('CLI maps type to extension', () => assert.deepEqual(client.cli('-r', 'video/mpeg'), {status: 0, stdout: 'mpeg\n', stderr: ''}));
test('CLI prints package version', () => assert.deepEqual(client.cli('--version'), {status: 0, stdout: '4.1.0\n', stderr: ''}));
test('CLI help prints usage', () => {
  const result = client.cli('--help');
  assert.equal(result.status, 0);
  assert.match(result.stdout, /Usage:/);
});
