# Project Description

Build an installable Node.js package named `socket.io` from an empty workspace.
It is a realtime server framework that attaches to a Node HTTP server, accepts
Engine.IO v4 connections, and multiplexes event-based Socket.IO connections
over namespaces and rooms. The implementation must be usable as a library; it
must not depend on an external service or start a server merely because the
package was imported.

## Natural Language Instruction

Create `socket.io` from an empty workspace as a complete installable node project. Implement
the public operations, data or state behavior, input validation, deterministic ordering, and
error contracts documented below. Keep package metadata, root exports, module imports, and any
subpath entry points consistent across files. Implement the behavior rather than hard-coding the
examples, and do not retrieve or copy a reference implementation.

The finished repository must install from its root, expose every documented API family, preserve
the specified side effects and resource lifecycle, and remain usable in a fresh process.

## Supports

- Package/distribution name: `socket.io`. Primary import or package entry: `socket.io`.
- Node.js 24.19.0 and npm 11.17.0 on Linux amd64.
- Install from `workspace/` using `npm ci --offline --ignore-scripts --no-audit --no-fund`.
- Declared dependency closure: accepts, cors, debug, engine.io, socket.io-adapter, socket.io-parser. Standard-library modules are not dependencies.
- Build requirements are supplied before execution; do not add undeclared dependencies,
  registry overrides, download hooks, or source-fetch steps.
- Agent, candidate, verifier, Oracle, and controls use `network_mode=no-network`. Runtime access
  to GitHub, PyPI, npm, the Go proxy, DNS, and external services is forbidden.
- The declared test framework is `node:test`. A fixed collection
  contains `12` cases when that value is frozen in metadata;
  test implementation details are not part of the package surface.

## Project Directory Structure

```text
workspace/
├── package.json
├── package-lock.json
├── index.js
├── index.d.ts
└── lib/
    ├── index.js
    ├── server.js
    ├── namespace.js
    ├── socket.js
    └── broadcast-operator.js
```

This is the required public project shape. Additional implementation modules are allowed only
when they support the documented API; evaluation, source-fetch, and private runtime files are
not agent-owned project files.

## API Usage Guide

### Package exports

The package root exports exactly the runtime constructors `Server`,
`Namespace`, and `Socket`. Each is a class/function value. TypeScript
declarations should describe these classes and the event-map generics used by
Socket.IO, but runtime behavior is authoritative.

### `new Server(httpServer?, options?)`

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

### Connections and namespaces

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

### Events and acknowledgements

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

### Rooms and broadcasting

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

### Socket listeners and lifecycle

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

## Implementation Notes

Keep protocol parsing, namespace matching, room membership, acknowledgement
IDs/timers, and cleanup deterministic. Multiple clients must remain isolated,
and a sender-excluding broadcast must not echo to the sender. Clear pending
polls, timers, room membership, middleware state, and acknowledgement callbacks
when a socket or server closes so that Node exits without background work.

Do not access the public network, execute arbitrary commands, load native
addons, use global loader hooks, modify verifier files, or create forged reward
files. The verifier installs and packs the candidate offline before exercising
it through an isolated subprocess boundary.

Use the public language semantics described by each API family. Keep repeated calls deterministic
unless state mutation is explicitly part of the contract. Public re-exports and declarations must
match runtime behavior, and installation must not rely on a repository checkout or network access.

## Examples

The API-specific examples above are normative demonstrations of ordinary behavior. These four
local snippets also provide ordinary and boundary-oriented calls without external services:

```javascript
fn(socket, next)
```

```javascript
const api = require('socket.io');
console.log(typeof api);
```

```javascript
import api from 'socket.io';
console.log(typeof api);
```

```javascript
const api = require('socket.io');
console.log(typeof api);
```

## Error Handling and Boundary Conditions

Empty values, malformed values, unsupported types, exhausted inputs, invalid options, and missing
local resources must follow the API-specific contracts above. Preserve documented exception types
and messages where they are stated. Do not silently coerce an unsupported value merely to produce
a result, and do not mutate caller-owned data unless the relevant API explicitly promises it.

All filesystem, process, terminal, clock, randomness, and service interactions are forbidden unless
the API guide explicitly includes that local behavior. Even for an API that models remote or async
work, evaluation must remain bounded, deterministic, and disconnected from public networks.
