import assert from 'node:assert/strict';
import test from 'node:test';
import {call, inventory} from './test_client.mjs';

const value = (response, expected) => {
  assert.equal(response.ok, true, JSON.stringify(response));
  assert.equal(response.value, expected);
};
const error = (response, type, message) => {
  assert.equal(response.ok, false, JSON.stringify(response));
  assert.equal(response.error_type, type);
  assert.equal(response.message, message);
};

test('package metadata and default export', () => {
  const response = inventory();
  assert.deepEqual(response.value, {
    name: 'normalize-url', version: '9.0.1', type: 'module',
    exports: {types: './index.d.ts', default: './index.js'},
    runtime_exports: ['default'], default_type: 'function',
  });
});
test('basic hostname receives http', () => value(call('sindresorhus.com'), 'http://sindresorhus.com'));
test('trim case and trailing host dot', () => value(call('  HTTP://WWW.SINDRESORHUS.COM.  '), 'http://sindresorhus.com'));
test('protocol relative uses default protocol', () => value(call('//www.sindresorhus.com:80/../baz?b=bar&a=foo'), 'http://sindresorhus.com/baz?a=foo&b=bar'));
test('protocol relative can remain protocol relative', () => value(call('//sindresorhus.com/', {normalizeProtocol: false}), '//sindresorhus.com'));
test('https default protocol', () => value(call('sindresorhus.com', {defaultProtocol: 'https'}), 'https://sindresorhus.com'));
test('default protocol accepts colon', () => value(call('sindresorhus.com', {defaultProtocol: 'https:'}), 'https://sindresorhus.com'));
test('force http', () => value(call('https://www.example.com/path', {forceHttp: true}), 'http://example.com/path'));
test('force https', () => value(call('http://www.example.com/path', {forceHttps: true}), 'https://example.com/path'));
test('protocol can be stripped', () => value(call('https://www.example.com/path', {stripProtocol: true}), 'example.com/path'));
test('force protocols cannot be combined', () => error(call('https://example.com', {forceHttp: true, forceHttps: true}), 'Error', 'The `forceHttp` and `forceHttps` options cannot be used together'));
test('authentication is stripped by default', () => value(call('https://user:password@www.example.com/path'), 'https://example.com/path'));
test('authentication can be retained', () => value(call('https://user:password@www.example.com/path', {stripAuthentication: false}), 'https://user:password@example.com/path'));
test('www is stripped by default', () => value(call('https://www.example.com'), 'https://example.com'));
test('www can be retained', () => value(call('https://www.example.com', {stripWWW: false}), 'https://www.example.com'));
test('unicode hostname uses IDNA', () => value(call('êxample.com'), 'http://xn--xample-hva.com'));
test('default ports are removed', () => value(call('http://example.com:80/'), 'http://example.com'));
test('nondefault port is retained', () => value(call('http://example.com:8080/'), 'http://example.com:8080'));
test('explicit port option removes nondefault port', () => value(call('http://example.com:8080/path', {removeExplicitPort: true}), 'http://example.com/path'));
test('dot segments are resolved', () => value(call('http://example.com/a/b/../c/./'), 'http://example.com/a/c'));
test('duplicate path slashes are collapsed', () => value(call('https://example.com/a//b///c'), 'https://example.com/a/b/c'));
test('safe path octets are decoded', () => value(call('http://example.com/%7Efoo/'), 'http://example.com/~foo'));
test('encoded backslash remains encoded', () => value(call('https://example.com/%5Cbar'), 'https://example.com/%5Cbar'));
test('trailing path slash is removed', () => value(call('https://example.com/path/'), 'https://example.com/path'));
test('trailing path slash can be preserved', () => value(call('https://example.com/path/', {removeTrailingSlash: false}), 'https://example.com/path/'));
test('root slash can be preserved', () => value(call('https://example.com/', {removeSingleSlash: false}), 'https://example.com/'));
test('query parameters sort', () => value(call('https://example.com?b=two&a=one'), 'https://example.com/?a=one&b=two'));
test('query order can be preserved', () => value(call('https://example.com?b=two&a=one', {sortQueryParameters: false}), 'https://example.com/?b=two&a=one'));
test('utm query parameters are removed', () => value(call('https://example.com?utm_source=x&keep=yes'), 'https://example.com/?keep=yes'));
test('named query parameters are removed', () => value(call('https://example.com?ref=x&keep=yes', {removeQueryParameters: ['ref']}), 'https://example.com/?keep=yes'));
test('all query parameters can be removed', () => value(call('https://example.com?a=1&b=2', {removeQueryParameters: true}), 'https://example.com'));
test('query parameters can be kept', () => value(call('https://example.com?foo=1&bar=2', {keepQueryParameters: ['foo']}), 'https://example.com/?foo=1'));
test('empty query values preserve source spelling', () => value(call('https://example.com?a&b='), 'https://example.com/?a&b='));
test('empty query values always use equals', () => value(call('https://example.com?a&b=', {emptyQueryValue: 'always'}), 'https://example.com/?a=&b='));
test('empty query values can omit equals', () => value(call('https://example.com?a&b=', {emptyQueryValue: 'never'}), 'https://example.com/?a&b'));
test('hash is retained by default', () => value(call('https://example.com/path#section'), 'https://example.com/path#section'));
test('hash can be removed', () => value(call('https://example.com/path#section', {stripHash: true}), 'https://example.com/path'));
test('text fragment is removed by default', () => value(call('https://example.com/path#section:~:text=hello'), 'https://example.com/path#section'));
test('data URL is normalized locally', () => value(call('data:TEXT/PLAIN;charset=US-ASCII,hello#frag'), 'data:,hello#frag'));
test('unknown custom protocol passes through', () => value(call('sindre://www.example.com/path/'), 'sindre://www.example.com/path/'));
test('listed custom protocol is normalized', () => value(call('sindre://www.example.com/path/', {customProtocols: ['sindre']}), 'sindre://example.com/path'));
test('removePath keeps query', () => value(call('https://example.com/a/b?x=1', {removePath: true}), 'https://example.com/?x=1'));
test('directory index can be removed', () => value(call('https://example.com/docs/index.html', {removeDirectoryIndex: ['index.html']}), 'https://example.com/docs'));
test('malformed host text may throw URL error', () => { const response = call('http://'); assert.equal(response.ok, false); assert.equal(response.error_type, 'TypeError'); });
test('repeated calls remain deterministic', () => { const input = 'https://www.example.com/a//b?z=2&a=1'; assert.equal(call(input).value, call(input).value); });
