# Build `immer`

## Project Description

Create an installable npm package named `immer`, version `10.0.3-beta`, from an
empty workspace. Immer lets callers describe changes by mutating a draft while
leaving the original JSON state untouched. The scored contract is a
deterministic, JSON-compatible subset of the public API. It must work without a
network service, a filesystem checkout, a clock, a loader, or a browser.

This is a repository-generation task. Implement the observable contract with
your own package files; do not copy the pinned upstream source or tests.

## Natural Language Instruction

Create the zero-runtime-dependency ESM `immer` package from an empty workspace.
Implement copy-on-write drafts for JSON objects and arrays, the root exports,
patch generation/application, draft lifecycle inspection, freezing controls,
and the deterministic adapter-facing behavior described below. Preserve base
state immutability, no-op identity, mutation ordering, replacement semantics,
and errors for invalid draft use. Do not add a CLI or external service.

## Supports

- Run on Node `24.19.0` with npm `11.17.0` on `linux/amd64`.
- Use ESM package semantics: `package.json` must contain `"type": "module"`.
- The package root must be importable as `immer` and must expose an `exports["."]`
  map whose runtime default is a JavaScript ESM file and whose `types` entry is
  a declaration file. The runtime entry must expose the named values listed
  below.
- Include a v3 `package-lock.json` agreeing with `package.json`. There are no
  runtime dependencies. A clean verifier runs
  `npm ci --offline --ignore-scripts --no-audit --no-fund`.
- Do not use workspaces, native addons, custom loaders, registry configuration,
  lifecycle scripts, or network access. Do not require a build step after
  installation.
- The verifier disables lifecycle scripts and sends only bounded JSON values to
  the candidate. JavaScript callbacks are represented by a verifier-owned
  declarative action list; your public functions must still have the normal
  Immer callback signatures.

## Project Directory Structure

```text
workspace/
├── package.json
├── package-lock.json
├── index.js
└── index.d.ts
```

`index.js` is the ESM root export and `index.d.ts` describes the public
functions and symbols. The package has no runtime dependency in this task
slice. Keep the package installable directly from the workspace root without a
postinstall build or generated runtime directory.

## API Usage Guide

### Package exports

The root must support:

```js
import immer, {
  Immer, produce, produceWithPatches, applyPatches,
  createDraft, finishDraft, current, original, isDraft, isDraftable,
  freeze, setAutoFreeze, enablePatches, enableMapSet,
  nothing, immerable,
} from "immer";
```

`produce` is the default export and a named export. `Immer` is constructible;
its instances expose the same state APIs without sharing settings with other
instances. `nothing` is the sentinel that makes a recipe produce `undefined`.
`immerable` is a symbol. `enablePatches()` enables patch support globally;
`enableMapSet()` and `enableArrayMethods()` may be present as public no-op or
feature-enabling functions, but the scored JSON surface uses plain objects and
arrays only.

### `produce`

Signature:

```js
produce(base, recipe, patchListener?) => nextState
```

The recipe receives a mutable draft. Mutating the draft must not mutate
`base`. If the recipe makes no change, return the original `base` reference.
The supported JSON state consists of `null`, booleans, finite numbers,
strings, arrays, and plain objects, recursively. Draftable arrays and plain
objects use copy-on-write. A recipe may return a replacement value instead of
mutating the draft, but it must not both mutate and return a replacement.

Supported draft mutations include property assignment, property deletion,
array `push`, `pop`, `shift`, `unshift`, `splice`, and nested mutations. Array
order and object keys must be preserved according to JavaScript semantics.
With automatic freezing enabled (the default), produced draftable objects are
deeply frozen. `setAutoFreeze(false)` disables this behavior for the global
instance.

### Patches

After `enablePatches()`,

```js
produceWithPatches(base, recipe) => [nextState, patches, inversePatches]
applyPatches(base, patches) => nextState
```

Each patch is `{op, path, value?}` where `op` is `add`, `remove`, or `replace`
and `path` is an array of object keys or array indexes. Patches must describe
the observable change in traversal order; inverse patches must restore the
original value. `applyPatches` must not mutate its input and must accept the
patches produced by `produceWithPatches`.

### Draft lifecycle and inspection

`createDraft(base)` returns a draft that can be mutated until
`finishDraft(draft, patchListener?)` is called. `finishDraft` returns the
finalized state and rejects use of the draft afterwards. Inside a recipe or
before finishing, `isDraft(value)` is true for the draft and false for ordinary
JSON values. `original(draft)` returns the corresponding original value;
`current(draft)` returns a snapshot of the draft's current values. Calling
either on a non-draft returns `undefined` or raises the ordinary Immer error.

`isDraftable(value)` is true for arrays, plain objects, and `null`-prototype
objects, and false for primitives and `null`. `freeze(value, deep?)` returns
the same value; it shallow-freezes draftable containers by default and
recursively freezes nested draftable values when `deep` is true.

### Deterministic child boundary

The verifier-owned adapter supports `inventory`, `produce`, `patches`,
`apply-patches`, `draft-lifecycle`, `observe`, and `utilities`. For operations
that mutate state, `actions` is a JSON array of objects with `op` and `path`:

- `set` (`value`), `delete`, `push` (`values`), `unshift` (`values`),
  `pop`, `shift`, `splice` (`start`, `deleteCount`, `items`), and `assign`
  (`value`, a plain object).

The adapter turns these data into real recipe callbacks. It returns JSON-only
values and booleans; identity and freeze behavior are exposed as booleans in
the operation results. Candidate code must not implement a CLI or read the
private tests.

## Terminal and determinism rules

All ordinary calls run in a fresh child with stdout/stderr as pipes and with a
sanitized environment (`TERM=dumb`, `CI=true`, `FORCE_COLOR=0`,
`LC_ALL=C.UTF-8`). Do not depend on ambient process state, environment
variables, current time, random values, or host paths. Preserve JSON number,
string, array, and object values exactly as JavaScript would.

## Production Slice

The upstream Vitest/TypeScript development suite is not installed in the
verifier. The frozen production denominator is a deterministic 28-leaf
`node:test` slice covering package shape, no-op identity, nested copy-on-write
updates, array mutations, replacement and `nothing`, deep freezing, patches and
inverse patches, patch application, draft lifecycle, `current`/`original`,
draftability, and the no-runtime-dependency/offline package contract. Every
scored assertion is derived from this public contract and is recorded in
task-local traceability evidence.

## Implementation Notes

Use copy-on-write proxies or an equivalent observable design, but expose only
the documented public values. Preserve object key and array order, recursively
freeze finalized draftable values when auto-freeze is enabled, and emit patch
paths in deterministic traversal order. Global settings such as auto-freeze
and patch enablement must not corrupt already-created drafts or unrelated
instances. JSON action adaptation is a transport boundary, not an additional
public API.

## Examples

```js
import {produce} from 'immer';
const next = produce({count: 1}, draft => { draft.count += 1; });
```

```js
import {produceWithPatches, enablePatches} from 'immer';
enablePatches();
const [next, patches, inverse] = produceWithPatches({items: []}, draft => {
  draft.items.push('new');
});
```

```js
import {createDraft, finishDraft} from 'immer';
const draft = createDraft({ready: false});
draft.ready = true;
finishDraft(draft);
```

## Error Handling and Boundary Conditions

- A recipe must not both mutate its draft and return a replacement value.
- Finalized drafts cannot be reused; `applyPatches` must clone rather than
  mutate its base input.
- `nothing` produces `undefined`, while ordinary `null` remains `null`.
- The scored state domain is JSON-compatible plain objects and arrays; Map,
  Set, functions, native objects, and callback serialization are outside it.
- No operation may consult the network, current time, ambient environment, or
  filesystem paths.
