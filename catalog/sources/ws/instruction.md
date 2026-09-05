# Project Description

```text
workspace/
├── package.json
├── package-lock.json
└── index.js
```

Build an installable Node.js package named `ws` from an empty workspace. The
package implements RFC 6455 WebSocket clients and servers for Node.js. It must
support CommonJS and ESM consumers, event-driven client/server communication,
local HTTP upgrades, control frames, compression negotiation, and a duplex
stream adapter without depending on a browser, database, native addon, public
network service, or runtime download.

# Natural Language Instruction

Create the package from an empty `workspace/`. Implement the documented
CommonJS/ESM exports, local RFC 6455 client/server behavior, frame handling,
control messages, negotiation, and stream adapter. Keep external services and
runtime downloads out of the package.

# Supports

- Node.js 24.19.0 on Linux x86-64 and npm 11.17.0.
- Package name `ws` and version `8.21.3`.
- CommonJS entry `index.js`, ESM entry `wrapper.mjs`, and browser entry
  `browser.js`. The browser entry must throw an explanatory error because this
  package targets Node.js; browser users must use the platform WebSocket API.
- A committed npm v3 `package-lock.json`. The package must install with
  `npm ci --offline --ignore-scripts`, pack with `npm pack --ignore-scripts`,
  and run without mandatory third-party dependencies.
- No install lifecycle hooks, workspaces, git/file dependencies, native
  addons, `binding.gyp`, or prebuilt binary directories. Optional native
  accelerators are not available and must not be required for correctness.
- Deterministic local-loopback WebSocket behavior. Public Internet access,
  TLS certificate provisioning, HTTP proxies, and remote echo services are
  outside the task.

# API Usage Guide

## Project Directory Structure

```text
workspace/
├── package.json
├── package-lock.json
├── index.js
├── wrapper.mjs
├── browser.js
└── lib/{websocket.js,websocket-server.js,sender.js,receiver.js}
```

The root supports the documented CommonJS and ESM exports.

## Package exports

`require('ws')` returns the `WebSocket` class. It also exposes
`WebSocket`, `WebSocketServer`, the historical `Server` alias,
`createWebSocketStream`, `Receiver`, `Sender`, `PerMessageDeflate`,
`extension`, and `subprotocol` as properties.

The ESM root exports `WebSocket` as both the default and a named export. It
also exports `WebSocketServer`, `createWebSocketStream`, `Receiver`, `Sender`,
`PerMessageDeflate`, `extension`, and `subprotocol` by name. `Receiver`,
`Sender`, and `PerMessageDeflate` are constructable compatibility exports;
ordinary applications should use the high-level client/server API.

## `new WebSocketServer(options[, callback])`

`WebSocketServer` extends `EventEmitter`. Exactly one of these server modes is
required, otherwise construction throws `TypeError`:

- `port`: create and listen on an internal HTTP server; `port: 0` requests an
  ephemeral loopback port;
- `server`: attach to an existing Node `http.Server`; or
- `noServer: true`: do not attach automatically and accept upgrades through
  `handleUpgrade`.

The supported options include `host`, `path`, `clientTracking`,
`handleProtocols`, `maxPayload`, `perMessageDeflate`, `autoPong`,
`allowSynchronousEvents`, `skipUTF8Validation`, `closeTimeout`, and
`verifyClient`. `path` compares only the URL pathname, not its query string.
`handleProtocols(protocols, request)` receives a `Set` in client offer order
and returns the selected protocol or `false`.

The server emits `listening`, `connection`, `headers`, `error`,
`wsClientError`, and `close` as appropriate. A `connection` listener receives
`(websocket, request)`.

- `server.address()` returns the underlying listening address, `null` before
  an attached server is listening, and throws in `noServer` mode.
- `server.clients` is a `Set` of open/tracked clients when tracking is enabled.
- `server.shouldHandle(request)` returns whether a request matches the
  configured path.
- `server.handleUpgrade(request, socket, head, callback)` validates and
  completes an HTTP upgrade in `noServer` or externally managed mode.
- `server.close([callback])` stops accepting connections and completes after
  tracked clients have closed. Re-closing a closed server reports that it is
  not running through the callback.

## `new WebSocket(address[, protocols][, options])`

`WebSocket` extends `EventEmitter`. `address` is a `ws:`/`wss:` URL string or
`URL`; `protocols` is a string or ordered array of unique RFC token strings.
Duplicate or malformed protocols throw `SyntaxError`. The options used by the
task include `headers`, `perMessageDeflate`, `protocolVersion`,
`skipUTF8Validation`, `maxPayload`, and `handshakeTimeout`.

The class and its instances expose these ready-state constants:
`CONNECTING = 0`, `OPEN = 1`, `CLOSING = 2`, and `CLOSED = 3`.

Instances emit `open`, `message`, `ping`, `pong`, `close`, and `error` for the
covered loopback behavior. A `message` listener receives `(data, isBinary)`;
a `close` listener receives `(code, reason)`. The client automatically sends a
pong with the same payload when it receives a ping unless auto-pong behavior
has been explicitly disabled on that peer.

The following properties are supported:

- `binaryType`: `nodebuffer` by default, with `arraybuffer` and `fragments`
  also accepted; it can change while connected;
- `bufferedAmount`: bytes queued for transmission;
- `extensions`: negotiated extension names, such as `permessage-deflate`;
- `isPaused`: whether socket reads are paused;
- `protocol`: negotiated subprotocol or the empty string;
- `readyState`: current state constant;
- `url`: normalized connection URL; and
- `onopen`, `onmessage`, `onerror`, and `onclose`: EventTarget-style event
  handler properties.

### Data and control methods

- `send(data[, options][, callback])` transmits a string, `Buffer`,
  `ArrayBuffer`, typed-array view, or Blob. Sending while `CONNECTING` throws;
  sends after closing fail through the callback or error path.
- `ping([data[, mask]][, callback])` and `pong(...)` send control frames.
  Control payloads must be at most 125 bytes.
- `close([code[, reason]])` performs the closing handshake. A supplied code
  must be `1000` or in `3000..4999`, and the UTF-8 reason must be at most 123
  bytes; invalid values throw `TypeError` or `RangeError`.
- `terminate()` closes the underlying connection immediately.
- `pause()` and `resume()` suspend and resume reads and update `isPaused`.

### EventTarget compatibility

`addEventListener(type, listener[, options])` and
`removeEventListener(type, listener)` coexist with EventEmitter listeners and
the `on*` properties. Adding the same listener for the same event twice does
not duplicate delivery. Message listeners receive an event object whose
`data` property contains the message value.

## `createWebSocketStream(websocket[, options])`

Return a Node `Duplex` stream backed by an existing `WebSocket`. Writes send
WebSocket messages; incoming messages become readable chunks. The stream waits
for a connecting socket to open, propagates errors, respects readable
backpressure by pausing/resuming the WebSocket, closes gracefully on final,
and terminates the WebSocket when the stream is destroyed before a graceful
close.

## Header utilities

### `extension.parse(header) => object`

Parse a `Sec-WebSocket-Extensions` header into an object keyed by extension
name. Each key maps to an array of offered parameter objects; each parameter
maps to an array of values, and a value-less parameter is represented by
`true`. Repeated offers and parameters are preserved in input order. Malformed
tokens, quoting, escaping, separators, or truncated input throw `SyntaxError`.

### `extension.format(extensions) => string`

Format the same extension-offer structure as a header string. Parameters are
separated by `; ` and repeated configurations by `, `.

### `subprotocol.parse(header) => Set<string>`

Parse a `Sec-WebSocket-Protocol` header into an insertion-ordered `Set` of RFC
tokens. Empty entries, invalid characters, malformed separators, and duplicate
protocol names throw `SyntaxError`.

# Examples

```js
const {WebSocketServer, WebSocket} = require('ws');
const server = new WebSocketServer({port: 0});
server.on('connection', socket => socket.on('message', value => socket.send(value)));
```

Use local loopback for client/server tests and `createWebSocketStream` for a
duplex stream interface.

# Error Handling and Boundary Conditions

Reject invalid upgrade headers, unsupported versions, malformed frames,
oversized control payloads, invalid close codes, and messages over
`maxPayload`. Fragmentation, masking, ping/pong, and graceful close retain
their documented state and event behavior.

# Implementation Notes

Use only Node built-ins for the required runtime. A server and client must be
able to connect over `127.0.0.1`, exchange text and binary messages, negotiate
a requested subprotocol and `permessage-deflate`, exchange ping/pong control
frames, enforce `maxPayload` with close code `1009`, close with code/reason,
and clean up all sockets and timers. Compression may use Node's built-in
`zlib`.

HTTP upgrades must validate the RFC handshake (`Upgrade`, `Connection`,
`Sec-WebSocket-Key`, version, extensions, and protocols), apply the WebSocket
GUID accept hash, and transfer the socket to frame parsing without losing the
`head` bytes. Frame parsing must distinguish text/binary/control frames,
mask/unmask client frames, handle fragmentation, validate control-frame size
and close codes, and reject messages above `maxPayload`.

For example, a `WebSocketServer` bound to `127.0.0.1` on port `0`, followed by
a `WebSocket` client using its reported port, must reach `OPEN` on both peers.
If the client sends `"hello"` and the server sends that data back, the client
receives `"hello"` with `isBinary === false`; a server close with code `1000`
and reason `"complete"` reaches the client unchanged and ends in `CLOSED`.
