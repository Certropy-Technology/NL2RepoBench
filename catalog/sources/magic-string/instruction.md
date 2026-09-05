# Build `magic-string`

## Project Description

Create the `magic-string` project from an empty workspace. This is a repository-generation task for the frozen `node` package contract, task specification version `2.0.0`, at source revision `5473bfb5138e7b7c2fc91d964c0425f57f1470ce`. Implement the public behavior described by the local inventories and the task-specific detail below; do not copy upstream source or tests. The supported scope is node, npm, esm, typescript, string, sourcemap, bundling.

## Natural Language Instruction

Starting with an empty `workspace/`, create an installable `magic-string` project. Implement every public/core API named in the API Usage Guide, its package exports, and its documented integration points. Preserve observable input types, return shapes, ordering, determinism, state changes, and documented exception behavior. The project must be usable through its declared `magic_string` import path (or the package root for this Node task), and all required modules must be present in the directory structure below.

The task-specific specification retained below supplies the detailed behavior for each API family. Treat it as the contract: do not add unrelated APIs, replace deterministic behavior with randomized or time-dependent behavior, or weaken error handling.

## Supports

- Language/runtime: `node` on `24.19.0`; target environment metadata declares `debian-bookworm`.
- Distribution/package: `magic-string`; import/root name: `magic_string`. Package manager: `npm`.
- Install from the repository root with `npm ci --offline --ignore-scripts --no-audit --no-fund`. Build metadata must be complete and agree with the package entry point.
- Dependency status in the frozen source metadata is `known`. Use only dependencies declared by the task and available in the preinstalled build image; standard-library modules are not third-party runtime dependencies.
- NoNetwork boundary: agent, candidate, verifier, Oracle, and controls run with `network_mode=no-network`. Do not access GitHub, PyPI, npm registries, Go proxy, DNS, or external services at runtime. Do not fetch source or dependencies during implementation or package use.

## Project Directory Structure

```text
workspace/
├── package.json
├── package-lock.json
├── index.js
├── index.d.ts
└── README.md
```

The tree is the minimum public project layout. Add a module only when it corresponds to a documented import path or package resource. Do not place publicly unavailable evaluator code, non-public evaluation material, Oracle payloads, dependency caches, or trusted reports in this workspace.

## API Usage Guide

The public/core API families recorded in the local inventory are: `MagicString`, `Bundle`, Errors and determinism.

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
import_or_require = "magic_string"
```

The retained task-specific examples below provide ordinary API calls and combinations grounded in the frozen inventory. Keep their result shapes and ordering exact.

## Error Handling and Boundary Conditions

- Empty inputs, malformed values, missing resources, duplicate values, and unsupported options must follow the task-specific error contracts below; do not silently coerce or discard information unless explicitly specified.
- Repeated calls must remain deterministic. Filesystem, process, clock, random, native, callback, and serialization boundaries are supported only where the local specification documents them.
- Network attempts are prohibited and must not be used as a fallback. Installation failures, missing offline dependencies, or unsupported external capabilities are environment/source concerns, not reasons to invent behavior.


## Source-derived task detail

# Build `magic-string`

## Project Description

Create an installable npm package named `magic-string`, version `1.2.3`, from an empty workspace.
It is an ESM-only utility for editing an original string by character ranges while preserving the
relationship between original and generated content. It also provides `Bundle` for joining several
edited sources and `SourceMap` objects for serialized version-3 source-map metadata.

The evaluation uses a deterministic JSON subprocess adapter. The scored contract is a JSON-safe
slice of the pinned upstream package, with each call constructing fresh instances or applying a
fixed sequence of operations. JavaScript callbacks, regular expressions as direct inputs,
non-JSON values, and browser-only behavior are outside the contract.

## Supports

- Node.js `24.19.0` with npm `11.17.0` on Linux amd64/glibc.
- `package.json` must declare `name: "magic-string"`, `version: "1.2.3"`, and `type: "module"`.
- The package root must export the default `MagicString` class and named exports `MagicString`,
  `MagicStringError`, `Bundle`, and `SourceMap`. The root must be loadable with an ESM import.
- Include an npm `package-lock.json` using lockfile version 3. `npm ci --offline --ignore-scripts
  --no-audit --no-fund` must work with the reviewed cache closure. The only runtime dependency is
  `@jridgewell/sourcemap-codec` at an exact lock entry; development tools are not needed.
- The package must expose a runnable distribution entry without TypeScript, a bundler, a registry,
  lifecycle hook, native addon, browser global, current time, random state, or network service.
- Do not copy upstream source or tests. The verifier calls the public package only through a
  separate child process and JSON values.

## API Usage Guide

### `MagicString`

**Import path:** default export or named `MagicString` from the package root.

**Signature:** `new MagicString(original: string, options?: MagicStringOptions)`

`original` is a string. The JSON-safe options are `filename?: string`, `ignoreList?: boolean`,
`offset?: number`, and `indentExclusionRanges?: [number, number] | [number, number][]`. The
constructor preserves the original text. Methods mutate the instance and return `this` when noted.

- `append(content)` and `prepend(content)` add text outside the original body and return `this`.
- `appendLeft(index, content)` inserts at an original index and follows content ending at that
  index when a range is moved. `prependLeft` has the same placement with newer inserts before older
  inserts. `appendRight` and `prependRight` are the corresponding operations for content starting
  at an index. All four return `this` and require string content.
- `update(start, end, content, options?)` replaces the original half-open range `[start, end)`.
  `options` may contain boolean `storeName` and `overwrite`; `overwrite` controls whether inserts
  inside the range are removed. `overwrite(start, end, content, options?)` is the same operation
  with overwrite enabled by default, and accepts `contentOnly` to retain interior inserts.
- `remove(start, end)` removes a range. `reset(start, end)` restores a range and discards edits in
  it. `slice(start?, end?)` returns generated content corresponding to an original range. Negative
  indexes resolve from the original string where supported. Invalid, reversed, zero-length, or
  overlapping ranges raise `MagicStringError`.
- `move(start, end, index)` relocates an original range and returns `this`; moving into the range
  or across an invalid split raises `MagicStringError`.
- `replace(search, substitution)` replaces the first string match in the original text. String
  substitution is required in this task. `replaceAll(search, substitution)` replaces every string
  match. Matches are against the original text and the methods return `this`.
- `indent(indentString?, options?)` prefixes non-empty lines. If omitted, infer the most common
  indentation or use a tab. `options` may contain `exclude` ranges and `indentStart?: boolean`.
  `getIndentString()` returns the inferred indentation. `trim`, `trimStart`, `trimEnd`, and
  `trimLines` remove whitespace or line-break content and return `this`.
- `toString()` returns the generated string; `length()` counts generated content attached to the
  original body; `lastChar()` returns the final generated character or `""`; `lastLine()` returns
  text after the final newline; `isEmpty()` ignores whitespace; `hasChanged()` reports whether the
  generated result differs from the original.
- `clone()` returns an independent copy. `offset` is a mutable numeric property used by range-based
  methods and must be preserved by cloning.
- `addSourcemapLocation(index)` records an original position for low-resolution maps.
  `generateDecodedMap(options?)` returns a JSON-safe decoded map with `sources`, `names`, and raw
  `mappings`. `generateMap(options?)` returns a `SourceMap` with version `3`, encoded `mappings`,
  and optional `file`, `sourcesContent`, and `x_google_ignoreList`. Options include `file`, `source`,
  `includeContent`, and `hires` (`false`, `true`, or `"boundary"`).

### `Bundle`

**Import path:** named `Bundle` export.

**Signature:** `new Bundle(options?: { intro?: string; separator?: string })`

`addSource(source)` accepts a `MagicString` or `{ content, filename?, ignoreList?, separator? }`.
It returns `this` and keeps source order. `append(text, options?)`, `prepend(text)`, `indent(text?)`,
`trim`, `trimStart`, `trimEnd`, and `trimLines` mutate and return `this`. `toString`, `length`, and
`isEmpty` observe the joined bundle; the default separator between sources is a newline, while
`append` defaults to an empty separator. `clone()` is independent. `generateDecodedMap` and
`generateMap` produce the same JSON-safe map shapes as `MagicString`, deduplicating repeated
filenames and rejecting the same filename with different original content.

### Errors and determinism

Invalid content types, invalid ranges, duplicate filenames with different source content, and
unsupported moves must throw an instance whose `name` is `MagicStringError`. The same input and
operation sequence must produce byte-for-byte identical JSON-safe results across processes. Do not
rely on object identity, callbacks, or non-JSON serialization details.

## Implementation Notes

- Reproduce observable behavior of the pinned upstream revision, not a generic string editor.
- Preserve original indexes when edits, inserts, removals, and moves are combined. Do not mutate
  input strings or caller-owned option arrays.
- Keep the root ESM export shape and package metadata usable from an empty workspace. A build step
  may be used during development, but the generated workspace must already contain its runnable
  distribution and declarations.
- The private tests intentionally cover the public contract through a child-side adapter. They do
  not require the full callback, regex, browser, or complete source-map ecosystem.
