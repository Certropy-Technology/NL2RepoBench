# Build `mdast-util-mdxjs-esm`

## Project Description

Create the `mdast-util-mdxjs-esm` project from an empty workspace. This is a repository-generation task for the frozen `node` package contract, task specification version `1.0.0`, at source revision `8d05c28d15ec5b690e7fbb08d703b0752d431109`. Implement the public behavior described by the local inventories and the task-specific detail below; do not copy upstream source or tests. The supported scope is node, npm, esm, mdast, mdx, markdown, separate-verifier.

## Natural Language Instruction

Starting with an empty `workspace/`, create an installable `mdast-util-mdxjs-esm` project. Implement every public/core API named in the API Usage Guide, its package exports, and its documented integration points. Preserve observable input types, return shapes, ordering, determinism, state changes, and documented exception behavior. The project must be usable through its declared `mdast_util_mdxjs_esm` import path (or the package root for this Node task), and all required modules must be present in the directory structure below.

The task-specific specification retained below supplies the detailed behavior for each API family. Treat it as the contract: do not add unrelated APIs, replace deterministic behavior with randomized or time-dependent behavior, or weaken error handling.

## Supports

- Language/runtime: `node` on `24.19.0`; target environment metadata declares `debian-bookworm`.
- Distribution/package: `mdast-util-mdxjs-esm`; import/root name: `mdast_util_mdxjs_esm`. Package manager: `npm`.
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

The public/core API families recorded in the local inventory are: `mdxjsEsmFromMarkdown`, `mdxjsEsmToMarkdown`.

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
import_or_require = "mdast_util_mdxjs_esm"
```

The retained task-specific examples below provide ordinary API calls and combinations grounded in the frozen inventory. Keep their result shapes and ordering exact.

## Error Handling and Boundary Conditions

- Empty inputs, malformed values, missing resources, duplicate values, and unsupported options must follow the task-specific error contracts below; do not silently coerce or discard information unless explicitly specified.
- Repeated calls must remain deterministic. Filesystem, process, clock, random, native, callback, and serialization boundaries are supported only where the local specification documents them.
- Network attempts are prohibited and must not be used as a fallback. Installation failures, missing offline dependencies, or unsupported external capabilities are environment/source concerns, not reasons to invent behavior.


## Source-derived task detail

# Build `mdast-util-mdxjs-esm`

## Project Description

Create an installable npm package named `mdast-util-mdxjs-esm`, version `2.0.1`,
from an empty workspace. The package is an ESM-only mdast extension for MDX
JavaScript module declarations: one extension integrates parsing with
`mdast-util-from-markdown`, and one integrates serialization with
`mdast-util-to-markdown`.

This is a repository-generation task. Implement the described behavior with
your own source files. Do not retrieve the reference repository or hidden
tests.

## Supports

- Run on Node `24.19.0` with npm `11.17.0` on Linux x86-64.
- `package.json` must name `mdast-util-mdxjs-esm`, version `2.0.1`, and set
  `"type": "module"`.
- The root package must expose the named ESM exports
  `mdxjsEsmFromMarkdown` and `mdxjsEsmToMarkdown`. It has no default export.
- Include a compatible npm v3 `package-lock.json`. The package may declare the
  six runtime dependency roots listed below, but must not add native addons,
  git/file/workspace dependencies, custom loaders, lifecycle hooks, or network
  requirements.
- A clean verifier installs with:

  ```bash
  npm ci --offline --ignore-scripts --no-audit --no-fund
  ```

## API Usage Guide

### `mdxjsEsmFromMarkdown`

Import from `mdast-util-mdxjs-esm` and call `mdxjsEsmFromMarkdown()` with no
arguments. It returns a `FromMarkdownExtension` object with `enter.mdxjsEsm`
and `exit.mdxjsEsm`/`exit.mdxjsEsmData` handlers.

The `enter.mdxjsEsm` handler receives a token and uses the compile context's
`enter({type: 'mdxjsEsm', value: ''}, token)` and `buffer()` operations. The
`exit.mdxjsEsm` handler resumes the buffered source value, assigns it to the
top `mdxjsEsm` node, exits the token, and copies a truthy `token.estree` value
to `node.data.estree`. It must leave `data` absent when no ESTree result is
provided. The handler asserts that the top stack node has type `mdxjsEsm`.

The `exit.mdxjsEsmData` handler delegates the token to both configured data
handlers, in enter-then-exit order, with the same compile context as `this`.

### `mdxjsEsmToMarkdown`

Import from `mdast-util-mdxjs-esm` and call `mdxjsEsmToMarkdown()` with no
arguments. It returns a `ToMarkdownExtension` object with a
`handlers.mdxjsEsm` function. That handler returns the node's `value` when it
is truthy and returns the empty string when `value` is missing or falsey.

The extension factory calls are side-effect free and return fresh extension
objects. The handlers preserve object identity for nodes and ESTree values;
they do not parse, clone, mutate, stringify, or normalize the supplied values.

## Implementation Notes

The verifier calls a task-specific JSON adapter subpath,
`mdast-util-mdxjs-esm/adapter`, only to exercise the callback/context handlers
through a process-safe contract. The adapter is required in addition to the
two root exports and must expose an async `run(request)` function. It accepts
only the documented operation names and JSON-compatible arguments; reject
malformed requests with an `Error`.

The adapter operations are `api`, `from-enter`, `from-exit`, `from-data`, and
`to-markdown`. They model the compile context and return JSON-safe summaries or
results. They must delegate to the root extension factories rather than
reimplementing their returned handler behavior. Do not rely on verifier files,
global packages, browser APIs, native addons, lifecycle hooks, or network
access.
