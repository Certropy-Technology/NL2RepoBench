import assert from 'node:assert/strict';
import {test} from 'node:test';
import {call, invoke} from './test_client.mjs';

test('package is a scripts-free ESM implementation of the required exports', () => {
  assert.deepEqual(call({operation: 'inventory'}), {
    name: 'node-fetch', version: '3.1.1', type: 'module', dependencies: {
      'data-uri-to-buffer': '4.0.1', 'fetch-blob': '3.2.0', 'formdata-polyfill': '4.0.10',
    }, scriptNames: [],
    exports: {default: 'function', Headers: 'function', Request: 'function', Response: 'function', isRedirect: 'function'},
  });
});
test('headers normalize names, join values, and sort entries', () => {
  const value = call({operation: 'headers', init: [['B', '2'], ['a', '1'], ['b', '3']], lookups: ['a', 'b', 'missing']});
  assert.deepEqual(value.entries, [['a', '1'], ['b', '2, 3']]);
  assert.deepEqual(value.lookup, [{get: '1', has: true, all: ['1']}, {get: '2, 3', has: true, all: ['2', '3']}, {get: null, has: false, all: []}]);
});
test('headers append set and delete mutate only their normalized name', () => {
  const value = call({operation: 'headers', init: {A: '1', B: '2'}, actions: [{kind: 'append', name: 'a', value: '3'}, {kind: 'set', name: 'B', value: '4'}, {kind: 'delete', name: 'a'}]});
  assert.deepEqual(value.entries, [['b', '4']]);
});
test('headers raw keeps individual values', () => {
  assert.deepEqual(call({operation: 'headers', init: [['Set-Cookie', 'a=1'], ['set-cookie', 'b=2']]}).raw, {'set-cookie': ['a=1', 'b=2']});
});
test('headers reject invalid names and values', () => {
  assert.equal(invoke({operation: 'headers', init: {'bad name': 'x'}}).exceptionType, 'TypeError');
  assert.equal(invoke({operation: 'headers', init: {good: 'bad\nvalue'}}).exceptionType, 'TypeError');
});
test('response defaults and exposes status headers and ok', () => {
  const value = call({operation: 'response', body: null, init: {headers: {X: '1'}}, action: 'snapshot'});
  assert.deepEqual(value, {type: 'default', status: 200, statusText: '', ok: true, bodyUsed: false, entries: [['x', '1']], raw: {x: ['1']}});
});
test('response text removes a BOM and consumes the body', () => {
  assert.deepEqual(call({operation: 'response', body: '\uFEFFhello', action: 'text'}), {value: 'hello', bodyUsed: true});
});
test('response json parses decoded JSON', () => {
  assert.deepEqual(call({operation: 'response', body: '\uFEFF{"a":1}', action: 'json'}), {value: {a: 1}, bodyUsed: true});
});
test('response arrayBuffer keeps original UTF-8 bytes', () => {
  assert.deepEqual(call({operation: 'response', body: '\uFEFFa', action: 'arrayBuffer'}), {value: [239, 187, 191, 97], bodyUsed: true});
});
test('response clone permits independent reads', () => {
  assert.deepEqual(call({operation: 'response', body: 'copy', action: 'clone-text'}), {original: 'copy', clone: 'copy', originalUsed: true, cloneUsed: true});
});
test('response json factory applies a default content type', () => {
  const value = call({operation: 'response-static', kind: 'json', data: {x: 1}});
  assert.equal(value.text, '{"x":1}');
  assert.deepEqual(value.entries, [['content-type', 'application/json']]);
});
test('response error factory has an error status', () => {
  const value = call({operation: 'response-static', kind: 'error'});
  assert.equal(value.type, 'error');
  assert.equal(value.status, 0);
  assert.equal(value.statusText, '');
});
test('response redirect factory normalizes the location', () => {
  const value = call({operation: 'response-static', kind: 'redirect', url: 'https://example.test/a', status: 307});
  assert.deepEqual(value.entries, [['location', 'https://example.test/a']]);
  assert.equal(value.status, 307);
});
test('response redirect rejects non-redirect statuses', () => {
  assert.equal(invoke({operation: 'response-static', kind: 'redirect', url: 'https://example.test/a', status: 304}).exceptionType, 'RangeError');
});
test('request normalizes URL and standard methods', () => {
  assert.deepEqual(call({operation: 'request', input: 'https://example.test/a?b=1', init: {method: 'post'}}).method, 'POST');
});
test('request defaults redirect and preserves a missing referrer', () => {
  const value = call({operation: 'request', input: 'https://example.test/a'});
  assert.equal(value.redirect, 'follow');
  assert.equal(value.referrer, undefined);
});
test('request adds a string body content type', () => {
  assert.deepEqual(call({operation: 'request', input: 'https://example.test/a', init: {method: 'PATCH', body: 'hello'}}).entries, [['content-type', 'text/plain;charset=UTF-8']]);
});
test('request rejects embedded credentials', () => {
  assert.equal(invoke({operation: 'request', input: 'https://user:pass@example.test/a'}).exceptionType, 'TypeError');
});
test('request rejects a GET body', () => {
  assert.equal(invoke({operation: 'request', input: 'https://example.test/a', init: {body: 'no'}}).exceptionType, 'TypeError');
});
test('fetch decodes percent-encoded data URLs offline', () => {
  const value = call({operation: 'fetch-data', url: 'data:text/plain,hello%20world'});
  assert.equal(value.text, 'hello world');
  assert.deepEqual(value.entries, [['content-type', 'text/plain']]);
});
test('fetch decodes base64 data URLs offline', () => {
  assert.equal(call({operation: 'fetch-data', url: 'data:text/plain;base64,aGVsbG8='}).text, 'hello');
});
test('isRedirect accepts the five redirect codes', () => {
  for (const status of [301, 302, 303, 307, 308]) assert.equal(call({operation: 'is-redirect', status}), true);
});
test('isRedirect rejects nearby non-redirect codes', () => {
  for (const status of [300, 304, 305, 306]) assert.equal(call({operation: 'is-redirect', status}), false);
});
