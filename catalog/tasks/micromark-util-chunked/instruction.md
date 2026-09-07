# Build `micromark-util-chunked`

## Project Description

Create the `micromark-util-chunked` project from an empty workspace. This is a repository-generation task for the frozen `node` package contract, task specification version `2.0.0`, at source revision `774a70c6bae6dd94486d3385dbd9a0f14550b709`. Implement the public behavior described by the local inventories and the task-specific detail below; do not copy upstream source or tests. The supported scope is node, npm, esm, micromark, arrays, splice, chunking.

## Natural Language Instruction

Starting with an empty `workspace/`, create an installable `micromark-util-chunked` project. Implement every public/core API named in the API Usage Guide, its package exports, and its documented integration points. Preserve observable input types, return shapes, ordering, determinism, state changes, and documented exception behavior. The project must be usable through its declared `micromark_util_chunked` import path (or the package root for this Node task), and all required modules must be present in the directory structure below.

The task-specific specification retained below supplies the detailed behavior for each API family. Treat it as the contract: do not add unrelated APIs, replace deterministic behavior with randomized or time-dependent behavior, or weaken error handling.

## Supports

- Language/runtime: `node` on `24.19.0`; target environment metadata declares `debian-bookworm`.
- Distribution/package: `micromark-util-chunked`; import/root name: `micromark_util_chunked`. Package manager: `npm`.
- Install from the repository root with `npm ci --offline --ignore-scripts --no-audit --no-fund`. Build metadata must be complete and agree with the package entry point.
- Dependency status in the frozen source metadata is `known`. Use only dependencies declared by the task and available in the preinstalled build image; standard-library modules are not third-party runtime dependencies.
- NoNetwork boundary: agent, candidate, verifier, Oracle, and controls run with `network_mode=no-network`. Do not access GitHub, PyPI, npm registries, Go proxy, DNS, or external services at runtime. Do not fetch source or dependencies during implementation or package use.

## Project Directory Structure

```text
workspace/
├── package.json
├── package-lock.json
├── index.js
└── README.md
```

The tree is the minimum public project layout. Add a module only when it corresponds to a documented import path or package resource. Do not place publicly unavailable evaluator code, non-public evaluation material, Oracle payloads, dependency caches, or trusted reports in this workspace.

## API Usage Guide

The public/core API families recorded in the local inventory are: `splice(list, start, remove, items)`, `push(list, items)`.

For each listed family, the detailed contract below defines the import path or CLI entry, signature, accepted inputs, return type/shape, ordering and determinism, state or I/O side effects, errors, and examples. Implement the complete public surface, including root re-exports and aliases where the specification names them. If an API is stateful, preserve mutation and repeated-call behavior; if it is pure, do not introduce global state.

## Implementation Notes

Keep the implementation self-contained and deterministic under the declared runtime. The candidate repository must install from the workspace root, import through the documented public path, and run without external services. Preserve package metadata, module semantics (ESM/CommonJS or Python import behavior), serialization formats, resource cleanup, and boundary behavior described below. publicly unavailable evaluator adapters and non-public evaluation details are not part of the implementation.

## Examples

Ordinary project examples:

```bash
cd workspace
npm ci --offline --ignore-scripts --no-audit --no-fund
```

```js
# Import the public package and use the task-specific APIs documented below.
import_or_require = "micromark_util_chunked"
```

The retained task-specific examples below provide ordinary API calls and combinations grounded in the frozen inventory. Keep their result shapes and ordering exact.

## Error Handling and Boundary Conditions

- Empty inputs, malformed values, missing resources, duplicate values, and unsupported options must follow the task-specific error contracts below; do not silently coerce or discard information unless explicitly specified.
- Repeated calls must remain deterministic. Filesystem, process, clock, random, native, callback, and serialization boundaries are supported only where the local specification documents them.
- Network attempts are prohibited and must not be used as a fallback. Installation failures, missing offline dependencies, or unsupported external capabilities are environment/source concerns, not reasons to invent behavior.


## Source-derived task detail

# Build `micromark-util-chunked`

## Project Description

Create an installable npm package named `micromark-util-chunked`, version
`2.0.1`, from an empty workspace. The package provides ESM utilities for
mutating arrays safely when insertion lists can be very large.

## Supports

- Node.js `24.19.0`, npm `11.17.0`, Linux amd64, and ESM package semantics.
- The package root must expose the named exports `push` and `splice`.
- A clean verifier runs `npm ci --offline --ignore-scripts --no-audit --no-fund`.
- Runtime behavior is deterministic and local. Do not use filesystem, clock,
  randomness, subprocesses, browser globals, or network access.

## API Usage Guide

### `splice(list, start, remove, items)`

Import the named function from the package root:

```js
import {splice} from 'micromark-util-chunked'
```

Signature:

```ts
export function splice<T>(list: T[], start: number, remove: number, items: T[]): void
```

Mutate `list` like `Array.prototype.splice`: normalize a negative `start` from
the end, clamp a positive start to the list length, remove up to `remove`
items, and insert every item from `items` at that position. Negative remove
counts behave as zero. The function returns `undefined` and does not return
removed items. Large insertion arrays must work without argument-spread stack
overflows.

### `push(list, items)`

Signature:

```ts
export function push<T>(list: T[], items: T[]): T[]
```

Append all `items` to `list`. When `list` is non-empty, mutate and return the
same `list` object. When `list` is empty, return `items` directly without
copying it. The result preserves item order and supports large arrays.

## Implementation Notes

Keep the package ESM-only with package version `2.0.1` and the exact two named
exports. The runtime dependency closure includes the frozen
`micromark-util-symbol` package only for its public chunk-size constant. Do not
expose additional exports, retain mutable module-global state, or fetch source
or dependencies at runtime.
