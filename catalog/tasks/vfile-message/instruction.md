# Build `vfile-message`

## Project Description

Create an installable npm package named `vfile-message`, version `4.0.3`, from
an empty workspace. The package provides the ESM `VFileMessage` class used to
represent diagnostics with a reason, optional source/rule origin, and optional
unist point or position.

## Natural Language Instruction

Build `vfile-message` from an empty workspace. Recreate the public
`VFileMessage` error value and its constructor overloads, preserving Error
inheritance, cause handling, origin parsing, unist positions, ancestor
metadata, and deterministic string formatting. Keep the package synchronous
and JSON-safe at the public boundary. The implementation must expose the
named root export and must not require a live repository, service, clock,
random value, or runtime network access.

## Project Directory Structure

```text
workspace/
├── package.json
├── package-lock.json
├── index.js
├── index.d.ts
└── lib/
    └── vfile-message.js
```

`package.json` is the ESM package metadata and root export map. The root
`index.js` re-exports only `VFileMessage`; `lib/vfile-message.js` may contain
the implementation and `index.d.ts` describes the constructor overloads and
observable fields. The lockfile must include the declared unist position
formatter closure. Do not add CLI files, runtime downloads, evaluator
adapters, or private test material to the generated workspace.

## Supports

- Run on Node `24.19.0` with npm `11.17.0` on `linux/amd64`.
- `package.json` must set `"type": "module"`, expose `"./index.js"`, and
  export exactly the named class `VFileMessage` from the package root. There is
  no default export.
- The package may depend on `unist-util-stringify-position`; install from a
  v3 `package-lock.json` with `npm ci --offline --ignore-scripts --no-audit
  --no-fund`. Do not use lifecycle scripts, native addons, loaders, network
  access, random state, or current time.

## API Usage Guide

The public module identifier is `vfile-message`; a consumer uses the named
root export (`import vfileMessage` denotes that module in the examples below).

### `VFileMessage(causeOrReason, optionsOrParentOrPlace?, origin?)`

Import the named export:

```js
import {VFileMessage} from 'vfile-message'
```

Construct an `Error`-like message. The first argument may be a string reason or
an `Error`; when it is an `Error`, copy its message into `message` and `reason`,
preserve it as `cause`, and preserve its stack. A string reason has an empty
stack. The resulting instance must also be an `Error`.

The second argument may be an options object, a unist point (`line` and
`column`), a position (`start` and `end`), a node-like object (`type`, with an
optional `position`), or a legacy origin string. The third argument is a legacy
origin string. An origin without `:` becomes `ruleId`; `source:rule` is split at
the first colon. Explicit `source` and `ruleId` options take precedence over a
legacy origin.

Options include `ancestors`, `cause`, `place`, `ruleId`, and `source`. A node
argument sets `ancestors` to an array containing that node and uses its
`position`; an ancestors array without a place uses the final ancestor's
position. `place` may be a point or position. The instance exposes `file` as an
empty string, `fatal` as undefined, and the documented fields `actual`,
`expected`, `note`, and `url` as initially undefined. Do not mutate supplied
objects or arrays.

The `line` and `column` fields are taken from the starting point of `place`.
The `name` is the stringified place, or `1:1` when no place exists. The normal
string form is `name: reason`; for an empty reason it is just `name`. Position
strings use `line:column` and `line:column-line:column` forms.

Examples:

```js
const message = new VFileMessage('Unexpected word', {
  place: {start: {line: 2, column: 3}, end: {line: 2, column: 8}},
  source: 'spell',
  ruleId: 'unknown-word'
})
String(message) // '2:3-2:8: Unexpected word'

new VFileMessage('Bad token', 'parser:token')
// source === 'parser', ruleId === 'token'
```

## Implementation Notes

Keep the root export limited to `VFileMessage`, preserve Error inheritance and
the legacy overloads, and use deterministic JSON-compatible behavior. The
verifier calls the class in a UID-separated child process; no callback,
filesystem, TTY, asynchronous, native, or external-service behavior is part
of this task.

## Examples

```js
import {VFileMessage} from 'vfile-message'
const warning = new VFileMessage('Unexpected token', {
  place: {line: 4, column: 2},
  source: 'parser',
  ruleId: 'token'
})
String(warning) // '4:2: Unexpected token'
```

```js
const cause = new Error('disk input is invalid')
const message = new VFileMessage(cause)
message.cause === cause // true
message instanceof Error // true
```

```js
const range = new VFileMessage('', {
  place: {start: {line: 2, column: 1}, end: {line: 2, column: 5}}
})
range.name // '2:1-2:5'
range.toString() // '2:1-2:5'
```

## Error Handling and Boundary Conditions

- A string reason is retained exactly; an `Error` reason supplies `message`,
  `reason`, `cause`, and the original stack without inventing a new cause.
- `source:rule` splits at the first colon. An origin without a colon is a
  rule identifier, while explicit `source` and `ruleId` options take priority.
- Point and position inputs use one-based line and column values. Missing
  location data uses the documented default name and does not mutate the input.
- Node arguments add the node to `ancestors`; an ancestors array is copied so
  later caller mutation cannot change the message. Empty reasons stringify as
  the location name alone.
- Inputs crossing the JSON child boundary are finite strings, plain objects,
  arrays, and error descriptors. Runtime execution must remain offline and
  deterministic.
