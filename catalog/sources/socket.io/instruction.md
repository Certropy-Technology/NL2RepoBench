# Project Description

Build an installable Node.js package named `socket.io` from an empty workspace.
It is a realtime server framework that attaches to a Node HTTP server, accepts
Engine.IO v4 connections, and multiplexes event-based Socket.IO connections
over namespaces and rooms. The implementation must be usable as a library; it
must not depend on an external service or start a server merely because the
package was imported.

# Supports

- Node.js 24.19.0 on Linux and npm 11.17.0.
- A CommonJS package root with equivalent ESM import support. `require("socket.io")`
  and package-root ESM import must expose the public runtime classes described
  below.
- A v3 `package-lock.json` and deterministic offline installation. Lifecycle
  scripts, runtime downloads, native addons, and shell hooks are not allowed.
- A self-contained implementation is valid. If you use the frozen runtime
  closure, pin these direct dependencies exactly: `accepts@1.3.8`,
  `cors@2.8.5`, `debug@4.4.1`, `engine.io@6.6.9`,
  `socket.io-adapter@2.5.8`, and `socket.io-parser@4.2.7`.
- Standard Engine.IO v4 HTTP long-polling and Socket.IO protocol behavior. A
  WebSocket transport may also be implemented, but the package must not require
  a browser, remote endpoint, or native WebSocket addon.

# API Usage Guide

## Package exports

The package root exports exactly the runtime constructors `Server`,
`Namespace`, and `Socket`. Each is a class/function value. TypeScript
declarations should describe these classes and the event-map generics used by
Socket.IO, but runtime behavior is authoritative.

## `new Server(httpServer?, options?)`

Create a Socket.IO server. The first argument may be an existing Node
`http.Server`/`https.Server`, a numeric port, or be omitted. When a server or
port is supplied, attach the Engine.IO request handlers. Construction without a
server must not listen until `listen(serverOrPort, options?)` or
`attach(serverOrPort, options?)` is called. Both methods return the `Server`.

Support these server options and accessors:

- `path`: HTTP endpoint prefix, defaulting to `/socket.io`; both `/path` and
  `/path/` forms identify the same endpoint;
- `transports`, including the `polling` transport;
- `allowUpgrades`, `pingInterval`, and `pingTimeout`;
- `serveClient`, with `serveClient(value): this` and `serveClient(): boolean`;
- `cors` in the same shape accepted by the `cors` middleware; and
- `path(value): this` and `path(): string`.

Unmatched HTTP paths remain available to the attached HTTP server. The polling
transport follows Engine.IO v4 framing and supports the Socket.IO connection,
event, acknowledgement, error, and disconnect packet types, including more than
one framed packet in a polling payload.

## Connections and namespaces

`io.on("connection", listener)` receives each `Socket` connected to the default
namespace. `io.sockets` is that root `Namespace`.

`io.of(nameOrMatcher, listener?)` returns a `Namespace`. A string creates or
returns a named namespace. A `RegExp` or predicate creates a parent namespace;
matching child names are accepted and non-matching names are rejected with a
connect error. Calling `of()` repeatedly for the same string returns the same
namespace.

Both `Server.use(fn)` and `Namespace.use(fn)` register connection middleware:

```js
fn(socket, next)
```

Calling `next()` accepts the connection. Calling `next(error)` rejects it and
sends a connect-error packet whose data includes the error message. Middleware
runs in registration order. The connection `Socket` exposes a `handshake`
object with `auth`, request headers, query data, address, URL, issued time, and
transport information.

## Events and acknowledgements

`Server`, `Namespace`, and `Socket` use EventEmitter-style `on`, `once`, `off`,
and `emit` behavior. Arbitrary event arguments preserve order. The reserved
connection/disconnection names keep their framework meaning.

A client event may carry an acknowledgement callback as its final argument.
Calling it sends one acknowledgement with the provided arguments. For outgoing
events, `socket.emitWithAck(event, ...args)` returns a promise, and
`socket.timeout(milliseconds).emit(event, ...args, callback)` supplies an
`Error` to the callback if the client does not acknowledge before the deadline.
If the acknowledgement arrives, the callback receives `null`/no error followed
by the client values. `send(...args)` and `write(...args)` are aliases for the
`message` event.

## Rooms and broadcasting

Each connected `Socket` has a unique non-empty string `id`, a namespace `nsp`,
boolean `connected`/`disconnected` state, a `data` object, and a `rooms` set.
Its own ID is a room while connected.

- `socket.join(roomOrRooms): Promise<void> | void` joins one or more string
  rooms idempotently.
- `socket.leave(room): Promise<void> | void` leaves a room.
- `socket.to(room)` / `socket.in(room)` returns a broadcast operator excluding
  the sending socket.
- `io.to(room)` / `io.in(room)` and the corresponding `Namespace` methods target
  sockets in any requested room.
- `except(room)` excludes rooms from a broadcast.
- `emit`, `send`, `write`, `compress(boolean)`, `timeout(milliseconds)`,
  `volatile`, and `local` are chainable on the applicable broadcast operator.

`allSockets()` resolves to a `Set` of matching socket IDs. `fetchSockets()`
resolves to matching socket descriptors with IDs, handshake/data, and `rooms`
sets. `socketsJoin(roomOrRooms)`, `socketsLeave(roomOrRooms)`, and
`disconnectSockets(close?)` apply to all sockets selected by the current
namespace/room/exclusion operator. A server-forced namespace disconnect emits
the server-side reason `"server namespace disconnect"` and removes the socket
from inventories.

## Socket listeners and lifecycle

`Socket` provides `onAny`, `prependAny`, and `offAny` for incoming catch-all
listeners, plus `onAnyOutgoing`, `prependAnyOutgoing`, and `offAnyOutgoing` for
outgoing packets. `socket.use(fn)` runs per-event middleware in order.
`socket.disconnect(close?)` disconnects the namespace and optionally the
underlying transport.

`server.close(callback?)` disconnects clients, closes the Engine.IO server and
its attached HTTP listener, invokes the callback once, and returns a
`Promise<void>`. It is valid to await the promise, use the callback, or both.
After close completes, `fetchSockets()` returns an empty array and the HTTP
server no longer listens.

# Implementation Notes

Keep protocol parsing, namespace matching, room membership, acknowledgement
IDs/timers, and cleanup deterministic. Multiple clients must remain isolated,
and a sender-excluding broadcast must not echo to the sender. Clear pending
polls, timers, room membership, middleware state, and acknowledgement callbacks
when a socket or server closes so that Node exits without background work.

Do not access the public network, execute arbitrary commands, load native
addons, use global loader hooks, modify verifier files, or create forged reward
files. The verifier installs and packs the candidate offline before exercising
it through an isolated subprocess boundary.
