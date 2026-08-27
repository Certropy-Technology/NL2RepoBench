import assert from 'node:assert/strict';
import {test} from 'node:test';
import {call} from './test_client.mjs';

function value(operation, payload) {
  const response = call(operation, payload);
  assert.equal(response.ok, true, response.message);
  return response.value;
}

test('exports the stable Axios public surface', () => {
  assert.deepEqual(value('inventory', {}), {
    version: '1.20.0',
    exportNames: ['Axios', 'AxiosError', 'AxiosHeaders', 'Cancel', 'CancelToken', 'CanceledError', 'HttpStatusCode', 'VERSION', 'all', 'create', 'default', 'formToJSON', 'getAdapter', 'isAxiosError', 'isCancel', 'mergeConfig', 'spread', 'toFormData'],
  });
});

test('normalizes and reads headers case-insensitively', () => {
  assert.deepEqual(value('headers', {input: {'content-type': 'application/json', 'X-Test': 7}, reads: [{op: 'get', name: 'Content-Type'}, {op: 'get', name: 'x-test'}, {op: 'has', name: 'X-TEST'}]}), {
    reads: {'Content-Type': 'application/json', 'x-test': '7', 'X-TEST': true},
    json: {'content-type': 'application/json', 'X-Test': '7'},
  });
});

test('supports set, overwrite policy, delete, and normalization', () => {
  assert.deepEqual(value('headers', {input: {}, actions: [{op: 'set', name: 'x-name', value: 'first'}, {op: 'set', name: 'X-Name', value: 'blocked', rewrite: false}, {op: 'set', name: 'X-Name', value: 'second'}, {op: 'delete', name: 'missing'}, {op: 'normalize', format: true}], reads: [{op: 'get', name: 'x-name'}]}), {
    reads: {'x-name': 'second'},
    json: {'X-Name': 'second'},
  });
});

test('strips CRLF from header values while preserving Unicode', () => {
  const result = value('headers', {input: {'X-Name': '请求\r\nInjected: true用户'}, reads: [{op: 'get', name: 'x-name'}]});
  assert.equal(result.reads['x-name'], '请求Injected: true用户');
});

test('merges nested request configuration without mutating input', () => {
  assert.deepEqual(value('mergeConfig', {left: {baseURL: 'https://api.test', headers: {common: {A: '1'}}, params: {a: 1}}, right: {url: '/users', headers: {common: {B: '2'}}, params: {b: 2}}}), {
    baseURL: 'https://api.test',
    url: '/users',
    headers: {common: {A: '1', B: '2'}},
    params: {a: 1, b: 2},
  });
});

test('merges request scalar override and preserves explicit null', () => {
  assert.deepEqual(value('mergeConfig', {left: {timeout: 1000, headers: {A: '1'}}, right: {timeout: 0, headers: {A: null}}}), {timeout: 0, headers: {A: null}});
});

test('builds a URI from base URL, path, and serialized params', () => {
  assert.equal(value('getUri', {config: {baseURL: 'https://api.test/v1/', url: '/users', params: {page: 2, tag: ['a', 'b']}}}), 'https://api.test/v1/users?page=2&tag%5B%5D=a&tag%5B%5D=b');
});

test('request pipeline applies method, JSON body, base URL, and headers without network', () => {
  assert.deepEqual(value('request', {config: {method: 'post', baseURL: 'https://api.test', url: '/users', data: {name: 'Ada'}, headers: {'X-Test': 'yes'}}}), {
    status: 207, statusText: 'Multi-Status', reply: 'ok', data: {method: 'post', url: '/users', data: '{"name":"Ada"}', header: 'yes'},
  });
});

test('request pipeline supports the QUERY method and null body', () => {
  assert.deepEqual(value('request', {config: {method: 'query', url: '/search', data: null}}), {
    status: 207, statusText: 'Multi-Status', reply: 'ok', data: {method: 'query', url: '/search', data: null, header: null},
  });
});

test('serializes nested form data using bracket notation', () => {
  assert.deepEqual(value('form', {input: {user: {name: 'Ada'}, tags: ['one', 'two']}}), {calls: [['user[name]', 'Ada'], ['tags[]', 'one'], ['tags[]', 'two']]});
});

test('serializes form data with dot notation and indexed arrays', () => {
  assert.deepEqual(value('form', {input: {user: {name: 'Ada'}, tags: ['one', 'two']}, options: {dots: true, indexes: true}}), {calls: [['user.name', 'Ada'], ['tags.0', 'one'], ['tags.1', 'two']]});
});

test('form meta tokens serialize JSON values', () => {
  assert.deepEqual(value('form', {input: {'profile{}': {name: 'Ada'}}}), {calls: [['profile{}', '{"name":"Ada"}']]});
});

test('identifies Axios errors and keeps diagnostic fields', () => {
  assert.deepEqual(value('error', {message: 'bad request', code: 'ERR_BAD_REQUEST', status: 400, config: {url: '/users'}}), {isAxiosError: true, json: {message: 'bad request', name: 'AxiosError', code: 'ERR_BAD_REQUEST', status: 400, config: {url: '/users'}}});
});

test('identifies cancellation errors separately', () => {
  assert.deepEqual(value('cancel', {message: 'stop'}), {isCancel: true, isAxiosError: true, message: 'stop', code: 'ERR_CANCELED'});
});

test('maps HTTP status names and numbers', () => {
  assert.deepEqual(value('status', {codes: [200, 404, 500], names: ['Ok', 'NotFound', 'InternalServerError']}), {names: ['Ok', 'NotFound', 'InternalServerError'], values: [200, 404, 500]});
});

test('supports promise aggregation helpers', async () => {
  assert.deepEqual(value('all', {values: [1, 'two', null]}), [1, 'two', null]);
  assert.equal(value('spread', {args: [2, 3]}), 5);
});
