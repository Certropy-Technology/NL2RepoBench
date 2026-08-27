import assert from 'node:assert/strict';
import test from 'node:test';
import { scenario, value } from './test_client.mjs';

const jsonHeaders = { 'content-type': 'application/json' };

test('package root exposes the documented CommonJS surface', () => {
  assert.deepEqual(value('inventory'), {
    packageName: 'nock',
    packageVersion: '0.0.0-development',
    main: './index.js',
    callable: true,
    exports: [
      'activate', 'isActive', 'isDone', 'pendingMocks', 'activeMocks',
      'removeInterceptor', 'disableNetConnect', 'enableNetConnect', 'cleanAll',
      'abortPendingRequests', 'load', 'loadDefs', 'define', 'emitter',
      'recorder', 'restore', 'back',
    ],
  });
});

for (const method of ['GET', 'POST', 'PUT', 'HEAD', 'PATCH', 'DELETE', 'OPTIONS']) {
  test(`${method} shorthand intercepts the matching request`, () => {
    const result = value('shorthandReply', {
      method,
      path: `/method/${method.toLowerCase()}`,
      statusCode: 207,
      replyBody: method === 'HEAD' ? undefined : method,
    });
    assert.equal(result.statusCode, 207);
    if (method !== 'HEAD') assert.equal(result.body, method);
  });
}

test('generic intercept supports MERGE', () => {
  const result = value('staticReply', {
    method: 'MERGE', path: '/merge', statusCode: 200, replyBody: 'merged',
  });
  assert.equal(result.response.body, 'merged');
  assert.equal(result.done, true);
  assert.equal(result.globalDone, true);
});

test('JSON request bodies match structurally', () => {
  const result = value('staticReply', {
    method: 'POST', path: '/items', expectedBody: { nested: { enabled: true }, count: 2 },
    requestHeaders: jsonHeaders, requestBody: JSON.stringify({ count: 2, nested: { enabled: true } }),
    statusCode: 201, replyBody: { accepted: true },
  });
  assert.equal(result.response.statusCode, 201);
  assert.deepEqual(JSON.parse(result.response.body), { accepted: true });
  assert.equal(result.done, true);
});

test('exact query objects match decoded query parameters', () => {
  const result = value('queryMatch', {
    path: '/search', query: { q: 'hello world', page: '2' }, requestPath: '/search?q=hello%20world&page=2',
  });
  assert.equal(result.response.body, 'matched');
  assert.equal(result.done, true);
});

test('query true accepts any query string', () => {
  const result = value('queryMatch', {
    path: '/search', query: true, requestPath: '/search?unicode=%E2%9C%93&empty=',
  });
  assert.equal(result.response.statusCode, 200);
  assert.equal(result.done, true);
});

test('scope-level header matching is case-insensitive', () => {
  const result = value('headerMatch', {
    path: '/header', name: 'X-Token', expected: 'secret', headers: { 'x-token': 'secret' },
  });
  assert.equal(result.response.body, 'matched');
  assert.equal(result.done, true);
});

test('basicAuth matches a Basic Authorization header', () => {
  const result = value('basicAuth', { path: '/auth', user: 'alice', pass: 'p@ss' });
  assert.equal(result.response.statusCode, 200);
  assert.equal(result.done, true);
});

test('regular-expression scopes and paths match', () => {
  const result = value('regexMatch');
  assert.equal(result.response.body, 'regex');
  assert.equal(result.done, true);
});

test('object replies are JSON encoded', () => {
  const result = value('staticReply', {
    method: 'GET', path: '/json', statusCode: 200, replyBody: { ok: true, text: '✓' },
  }).response;
  assert.deepEqual(JSON.parse(result.body), { ok: true, text: '✓' });
  assert.match(result.headers['content-type'], /^application\/json/);
});

test('explicit reply headers are returned', () => {
  const result = value('staticReply', {
    method: 'GET', path: '/reply-headers', statusCode: 204, replyBody: '',
    replyHeaders: { 'x-demo': 'present' },
  }).response;
  assert.equal(result.statusCode, 204);
  assert.equal(result.headers['x-demo'], 'present');
});

test('synchronous reply functions receive the parsed body', () => {
  const result = value('dynamicReply', {
    path: '/dynamic-sync', expectedBody: { id: 7 }, requestBody: { id: 7 }, mode: 'sync',
  });
  assert.deepEqual(JSON.parse(result.body), { echoed: { id: 7 }, async: false });
});

test('async reply functions are awaited', () => {
  const result = value('dynamicReply', {
    path: '/dynamic-async', expectedBody: { id: 8 }, requestBody: { id: 8 }, mode: 'async',
  });
  assert.equal(result.statusCode, 201);
  assert.deepEqual(JSON.parse(result.body), { echoed: { id: 8 }, async: true });
});

test('full reply functions can return status body and headers', () => {
  const result = value('dynamicReply', {
    path: '/dynamic-full', expectedBody: { id: 9 }, requestBody: { id: 9 }, mode: 'full',
  });
  assert.equal(result.statusCode, 202);
  assert.equal(result.headers['x-mode'], 'full');
  assert.deepEqual(JSON.parse(result.body), { echoed: { id: 9 } });
});

test('default reply headers merge with interceptor headers', () => {
  const result = value('defaultHeaders');
  assert.equal(result.response.headers['x-default'], 'yes');
  assert.equal(result.response.headers['x-specific'], 'present');
  assert.equal(result.done, true);
});

test('replyContentLength and replyDate add deterministic metadata', () => {
  const result = value('contentMetadata').response;
  assert.equal(result.headers['content-length'], '5');
  assert.equal(result.headers.date, 'Thu, 02 Jan 2020 03:04:05 GMT');
});

test('times consumes the configured number of requests', () => {
  const result = value('counters', { mode: 'times', count: 3, requests: 3 });
  assert.deepEqual(result.statuses, [200, 200, 200]);
  assert.equal(result.done, true);
  assert.deepEqual(result.pending, []);
});

test('twice consumes exactly two requests', () => {
  const result = value('counters', { mode: 'twice', requests: 2 });
  assert.deepEqual(result.statuses, [200, 200]);
  assert.equal(result.done, true);
});

test('thrice consumes exactly three requests', () => {
  const result = value('counters', { mode: 'thrice', requests: 3 });
  assert.deepEqual(result.statuses, [200, 200, 200]);
  assert.equal(result.done, true);
});

test('persistent interceptors stay active after matching', () => {
  const result = value('counters', { mode: 'persist', requests: 2 });
  assert.deepEqual(result.statuses, [200, 200]);
  assert.equal(result.done, true);
  assert.equal(result.active.length, 1);
});

test('optional interceptors do not remain pending', () => {
  const result = value('optionalWithoutRequest');
  assert.equal(result.done, true);
  assert.deepEqual(result.pending, []);
  assert.equal(result.active.length, 1);
});

test('removeInterceptor removes a specific pending interceptor', () => {
  const result = value('removeInterceptor');
  assert.equal(result.removed, true);
  assert.equal(result.scopeDone, true);
  assert.deepEqual(result.pending, []);
  assert.deepEqual(result.active, []);
});

test('cleanAll removes every active interceptor', () => {
  const result = value('cleanAll');
  assert.equal(result.before.pending.length, 2);
  assert.equal(result.before.active.length, 2);
  assert.deepEqual(result.after, { pending: [], active: [] });
  assert.equal(result.done, true);
});

test('scope.done throws when a required mock is pending', () => {
  const result = value('scopeDoneError');
  assert.equal(result.isDone, false);
  assert.equal(result.pending.length, 1);
  assert.equal(result.error.name, 'AssertionError');
  assert.match(result.error.message, /Mocks not yet satisfied/);
});

test('restore and activate update global activation state', () => {
  assert.deepEqual(value('activationLifecycle'), { initial: true, restored: false, activated: true });
});

test('disableNetConnect rejects an unmatched request before egress', () => {
  const result = value('netConnectBlocked');
  assert.equal(result.threw, true);
  assert.equal(result.code, 'ENETUNREACH');
  assert.match(result.message, /Disallowed net connect/);
});

test('replyWithError surfaces the supplied error code and message', () => {
  const result = value('replyWithError');
  assert.equal(result.threw, true);
  assert.equal(result.code, 'EDEMO');
  assert.equal(result.message, 'socket failed');
});

test('define creates executable scopes from JSON-compatible definitions', () => {
  const result = value('define');
  assert.equal(result.scopeCount, 1);
  assert.equal(result.response.statusCode, 203);
  assert.equal(result.response.headers['x-defined'], 'yes');
  assert.deepEqual(JSON.parse(result.response.body), { source: 'definition' });
  assert.equal(result.done, true);
});

test('filteringPath rewrites request paths before matching', () => {
  const result = value('filteringPath');
  assert.equal(result.response.body, 'filtered');
  assert.equal(result.done, true);
});

test('filteringRequestBody rewrites bodies before matching', () => {
  const result = value('filteringRequestBody');
  assert.equal(result.response.body, 'filtered');
  assert.equal(result.done, true);
});

test('native fetch requests are intercepted without external networking', () => {
  const result = value('fetchReply');
  assert.equal(result.statusCode, 200);
  assert.equal(result.header, 'yes');
  assert.deepEqual(result.body, { transport: 'fetch' });
  assert.equal(result.done, true);
});

