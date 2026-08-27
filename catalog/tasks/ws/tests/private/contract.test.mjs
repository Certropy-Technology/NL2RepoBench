import assert from 'node:assert/strict';
import test from 'node:test';

import { callCandidate, callCandidateError } from './test_client.mjs';

const cache = new Map();
const scenario = (name, payload = {}) => {
  const key = `${name}:${JSON.stringify(payload)}`;
  if (!cache.has(key)) cache.set(key, callCandidate(name, payload));
  return cache.get(key);
};

test('package metadata identifies ws 8.21.3', () => {
  const value = scenario('inventory').package;
  assert.equal(value.name, 'ws');
  assert.equal(value.version, '8.21.3');
  assert.equal(value.main, 'index.js');
  assert.equal(value.browser, 'browser.js');
  assert.equal(value.importEntry, './wrapper.mjs');
});

test('ESM exports the default and named WebSocket classes', () => {
  const value = scenario('inventory').exports;
  assert.equal(value.default, 'function');
  assert.equal(value.WebSocket, 'function');
  assert.equal(value.WebSocketServer, 'function');
});

test('ESM exports stream and framing helpers', () => {
  const value = scenario('inventory').exports;
  assert.equal(value.createWebSocketStream, 'function');
  assert.equal(value.Receiver, 'function');
  assert.equal(value.Sender, 'function');
  assert.equal(value.PerMessageDeflate, 'function');
  assert.equal(value.extension, 'object');
  assert.equal(value.subprotocol, 'object');
});

test('CommonJS and ESM aliases are compatible', () => {
  assert.deepEqual(scenario('inventory').aliases, {
    cjsDefaultWebSocket: true,
    server: true,
    esmDefaultWebSocket: true,
  });
});

test('ready-state constants use RFC-compatible values', () => {
  assert.deepEqual(scenario('inventory').constants, {
    CONNECTING: 0,
    OPEN: 1,
    CLOSING: 2,
    CLOSED: 3,
  });
});

test('WebSocket exposes the documented operational methods', () => {
  assert.deepEqual(scenario('inventory').methods.websocket, [
    'addEventListener',
    'removeEventListener',
    'close',
    'pause',
    'ping',
    'pong',
    'resume',
    'send',
    'terminate',
  ]);
});

test('WebSocketServer exposes lifecycle and upgrade methods', () => {
  assert.deepEqual(scenario('inventory').methods.server, [
    'address',
    'close',
    'handleUpgrade',
    'shouldHandle',
  ]);
});

test('extension.parse normalizes extension parameters', () => {
  assert.deepEqual(
    scenario('extension', {
      action: 'parse',
      value: 'permessage-deflate; client_max_window_bits; server_max_window_bits=10',
    }),
    {
      'permessage-deflate': [{
        client_max_window_bits: [true],
        server_max_window_bits: ['10'],
      }],
    },
  );
});

test('extension.parse preserves repeated offers', () => {
  assert.deepEqual(
    scenario('extension', {
      action: 'parse',
      value: 'x-test; first=one, x-test; second=two',
    }),
    {
      'x-test': [{ first: ['one'] }, { second: ['two'] }],
    },
  );
});

test('extension.format produces a canonical header value', () => {
  assert.equal(
    scenario('extension', {
      action: 'format',
      value: {
        'permessage-deflate': {
          client_max_window_bits: [true],
          server_max_window_bits: ['10'],
        },
      },
    }),
    'permessage-deflate; client_max_window_bits; server_max_window_bits=10',
  );
});

test('extension.parse rejects malformed quoted values', () => {
  const error = callCandidateError('extension', {
    action: 'parse',
    value: 'permessage-deflate; key="unterminated',
  });
  assert.equal(error.exceptionType, 'SyntaxError');
  assert.match(error.message, /Unexpected end of input/);
});

test('subprotocol.parse returns an insertion-ordered set', () => {
  assert.deepEqual(
    scenario('subprotocol', { value: 'chat, superchat, binary-v1' }),
    ['chat', 'superchat', 'binary-v1'],
  );
});

test('subprotocol.parse rejects duplicate protocols', () => {
  const error = callCandidateError('subprotocol', { value: 'chat, chat' });
  assert.equal(error.exceptionType, 'SyntaxError');
  assert.match(error.message, /duplicated/);
});

test('server construction requires exactly one mode', () => {
  const value = scenario('serverShape');
  assert.equal(value.missing.name, 'TypeError');
  assert.match(value.missing.message, /One and only one/);
  assert.equal(value.conflicting.name, 'TypeError');
  assert.match(value.conflicting.message, /One and only one/);
});

test('duplicate client subprotocols are rejected synchronously', () => {
  const value = scenario('serverShape').duplicateProtocol;
  assert.equal(value.name, 'SyntaxError');
  assert.match(value.message, /duplicated/);
});

test('server.address reports a loopback TCP endpoint', () => {
  assert.deepEqual(scenario('serverShape').address, {
    address: '127.0.0.1',
    family: 'IPv4',
    portType: 'number',
  });
});

test('server.shouldHandle compares path while ignoring query text', () => {
  assert.deepEqual(scenario('serverShape').path, {
    exact: true,
    query: true,
    wrong: false,
  });
});

test('text data round-trips over a local client and server', () => {
  const value = scenario('echo', { text: 'hello websocket' });
  assert.deepEqual(value.message, {
    serverBinary: false,
    clientBinary: false,
    text: 'hello websocket',
    base64: null,
    valueType: 'Buffer',
  });
});

test('an open connection reports OPEN on both peers', () => {
  const value = scenario('echo', { text: 'state' }).beforeClose;
  assert.equal(value.clientReadyState, 1);
  assert.equal(value.serverReadyState, 1);
  assert.equal(value.clients, 1);
});

test('custom client headers reach the server request', () => {
  assert.equal(scenario('echo', { text: 'headers' }).beforeClose.requestHeader, 'ws-task');
});

test('the client exposes its normalized URL', () => {
  assert.match(scenario('echo', { text: 'url' }).beforeClose.url, /^ws:\/\/127\.0\.0\.1:\d+\/$/);
});

test('a server close frame preserves code and reason', () => {
  assert.deepEqual(scenario('echo', { text: 'close' }).close, {
    code: 1000,
    reason: 'complete',
    readyState: 3,
  });
});

test('binary data round-trips as an ArrayBuffer when requested', () => {
  const value = scenario('echo', {
    binaryBase64: 'AAECA/7/',
    binaryType: 'arraybuffer',
  }).message;
  assert.equal(value.serverBinary, true);
  assert.equal(value.clientBinary, true);
  assert.equal(value.base64, 'AAECA/7/');
  assert.equal(value.valueType, 'ArrayBuffer');
});

test('subprotocol negotiation can choose the final offered protocol', () => {
  const value = scenario('echo', {
    text: 'protocol',
    protocols: ['chat', 'superchat'],
    selectLastProtocol: true,
  }).beforeClose;
  assert.equal(value.protocol, 'superchat');
  assert.equal(value.serverProtocol, 'superchat');
});

test('permessage-deflate negotiation is visible to both peers', () => {
  const value = scenario('echo', {
    text: 'compressible '.repeat(200),
    perMessageDeflate: true,
  }).beforeClose;
  assert.equal(value.extensions, 'permessage-deflate');
});

test('a ping is exposed to the client', () => {
  assert.equal(scenario('pingPong').ping, 'probe');
});

test('the client automatically replies to ping with pong', () => {
  assert.equal(scenario('pingPong').pong, 'probe');
});

test('terminate closes the peer without a closing handshake', () => {
  assert.equal(scenario('pingPong').serverState, 3);
});

test('client tracking contains both connected peers', () => {
  assert.equal(scenario('broadcast').tracked, 2);
});

test('server iteration can broadcast to all tracked clients', () => {
  assert.deepEqual(scenario('broadcast').messages, ['broadcast', 'broadcast']);
});

test('createWebSocketStream returns a duplex stream', () => {
  assert.equal(scenario('streamRoundTrip').duplex, true);
});

test('createWebSocketStream carries data in both directions', () => {
  assert.deepEqual(scenario('streamRoundTrip'), {
    received: 'stream-data',
    reply: 'reply:stream-data',
    duplex: true,
  });
});

test('noServer handleUpgrade establishes a connection', () => {
  const value = scenario('manualUpgrade');
  assert.equal(value.message, 'upgraded');
  assert.equal(value.path, '/manual');
});

test('address throws in noServer mode', () => {
  const error = scenario('manualUpgrade').noServerAddressError;
  assert.equal(error.name, 'Error');
  assert.match(error.message, /noServer/);
});

test('EventTarget-style open listeners are de-duplicated', () => {
  assert.equal(scenario('eventTarget').filter((entry) => entry === 'open').length, 1);
});

test('onmessage and addEventListener both receive MessageEvent data', () => {
  const events = scenario('eventTarget');
  assert.ok(events.includes('onmessage:event-data'));
  assert.ok(events.includes('message:event-data'));
});

test('removeEventListener suppresses the removed close listener', () => {
  assert.equal(scenario('eventTarget').includes('removed'), false);
});

test('maxPayload reports the RFC message-too-big error', () => {
  assert.equal(scenario('maxPayload').errorCode, 'WS_ERR_UNSUPPORTED_MESSAGE_LENGTH');
});

test('maxPayload closes the remote peer with code 1009', () => {
  assert.equal(scenario('maxPayload').closeCode, 1009);
});

test('readyState moves from CONNECTING to OPEN to CLOSED', () => {
  const value = scenario('stateTransitions');
  assert.equal(value.connecting, 0);
  assert.equal(value.open, 1);
  assert.equal(value.closed, 3);
});

test('send rejects while the client is still CONNECTING', () => {
  const error = scenario('stateTransitions').earlySend;
  assert.equal(error.name, 'Error');
  assert.match(error.message, /readyState 0 \(CONNECTING\)/);
});

test('pause and resume update isPaused', () => {
  const value = scenario('stateTransitions');
  assert.equal(value.initiallyPaused, false);
  assert.equal(value.paused, true);
  assert.equal(value.resumed, false);
});

test('close rejects an invalid status code', () => {
  const error = scenario('stateTransitions').invalidCode;
  assert.equal(error.name, 'TypeError');
  assert.match(error.message, /valid error code|code must be 1000 or between 3000 and 4999/);
});

test('close rejects an overlong UTF-8 reason', () => {
  const error = scenario('stateTransitions').longReason;
  assert.equal(error.name, 'RangeError');
  assert.match(error.message, /must not be greater than 123 bytes/);
});
