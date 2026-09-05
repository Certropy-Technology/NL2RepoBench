# Build `mimic-fn`

## Project Description

Create the `mimic-function` project from an empty workspace. This is a repository-generation task for the frozen `node` package contract, task specification version `1.0.0`, at source revision `3ee1e62d926ac0a5cf631815734d8e06a9381d72`. Implement the public behavior described by the local inventories and the task-specific detail below; do not copy upstream source or tests. The supported scope is node, npm, esm, functions, descriptors, prototype.

## Natural Language Instruction

Starting with an empty `workspace/`, create an installable `mimic-function` project. Implement every public/core API named in the API Usage Guide, its package exports, and its documented integration points. Preserve observable input types, return shapes, ordering, determinism, state changes, and documented exception behavior. The project must be usable through its declared `mimic_function` import path (or the package root for this Node task), and all required modules must be present in the directory structure below.

The task-specific specification retained below supplies the detailed behavior for each API family. Treat it as the contract: do not add unrelated APIs, replace deterministic behavior with randomized or time-dependent behavior, or weaken error handling.

## Supports

- Language/runtime: `node` on `24.19.0`; target environment metadata declares `debian-bookworm`.
- Distribution/package: `mimic-function`; import/root name: `mimic_function`. Package manager: `npm`.
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

The public/core API families recorded in the local inventory are: `mimicFunction(to, from, options?)`, `options.ignoreNonConfigurable`, Wrapped `toString()`.

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
import_or_require = "mimic_function"
```

The retained task-specific examples below provide ordinary API calls and combinations grounded in the frozen inventory. Keep their result shapes and ordering exact.

## Error Handling and Boundary Conditions

- Empty inputs, malformed values, missing resources, duplicate values, and unsupported options must follow the task-specific error contracts below; do not silently coerce or discard information unless explicitly specified.
- Repeated calls must remain deterministic. Filesystem, process, clock, random, native, callback, and serialization boundaries are supported only where the local specification documents them.
- Network attempts are prohibited and must not be used as a fallback. Installation failures, missing offline dependencies, or unsupported external capabilities are environment/source concerns, not reasons to invent behavior.


## Source-derived task detail

# Build `mimic-function`

## Project Description

Create an installable npm package named `mimic-function`, version `5.0.1`, from
an empty workspace. The package is an ESM utility that makes one function mimic
another function while keeping the destination function body and prototype
object.

## Supports

- Run on Node `24.19.0` with npm `11.17.0` on `linux/amd64` with glibc.
- `package.json` must set `name` to `mimic-function`, `version` to `5.0.1`,
  declare `type: "module"`, and expose the root with `types: "./index.d.ts"`
  and `default: "./index.js"`.
- Include `index.js`, `index.d.ts`, and a v3 `package-lock.json` consistent
  with the manifest. There are no runtime dependencies, native addons,
  workspaces, lifecycle scripts, or development dependencies required in the
  published package.
- A clean verifier must be able to run
  `npm ci --offline --ignore-scripts --no-audit --no-fund` followed by
  `npm pack --ignore-scripts`.
- Do not use network services, wall-clock timing, random state, or browser
  globals to determine behavior.

## Supports

### `mimicFunction(to, from, options?)`

Import the default export from `mimic-function`:

```js
import mimicFunction from 'mimic-function';

function source(value) {
  return value;
}

function wrapper(value) {
  return source(value);
}

mimicFunction(wrapper, source);
```

The function accepts two callable values. It mutates and returns `to`; it does
not replace the destination function body. For every own key of `from`, copy
the property descriptor to `to` except `length`, `prototype`, `arguments`, and
`caller`. The destination's pre-existing configurable properties remain in
place. Symbol keys must be handled in the same way as string keys.

The `name` and custom properties of `from` therefore become visible on `to`.
Inherited behavior is copied by setting the destination's prototype to the
source function's prototype when they differ. The function prototype object
itself is not copied.

The return type is the same callable type as `from` in the declaration file.
The operation is synchronous and returns the exact `to` object.

### `options.ignoreNonConfigurable`

`options` is optional. Its `ignoreNonConfigurable` boolean defaults to `false`.
When false, a conflicting non-configurable destination property raises the
ordinary `Object.defineProperty` error. When true, that property is left
unchanged and the remaining properties continue to be processed.

### Wrapped `toString()`

After a successful call, `to.toString()` and `String(to)` return the source's
captured `toString()` text prefixed with `/* Wrapped with <destination-name>() */`.
The patched method remains non-enumerable and its own `name` is `toString`.
Calling `Function.prototype.toString.call(to)` still exposes the original
destination function source. Repeated wrapping preserves the earlier wrapper
text in the captured source string.

## API Usage Guide

The package has one default export, `mimicFunction`, from `index.js`; its type
is declared in `index.d.ts`. The inputs are functions or classes, and the
result is the mutated destination callable. Property values may include
symbols and descriptors, but the function never performs I/O or network work.

## Implementation Notes

Keep the package self-contained and deterministic. Do not copy the upstream
implementation or tests. Preserve property enumerability, writability,
configurability, symbols, source prototype identity rules, and the distinction
between the destination function body and its displayed `toString()` value.
The verifier constructs functions and descriptors inside a candidate child
process; no callback or executable source crosses the trusted boundary.
