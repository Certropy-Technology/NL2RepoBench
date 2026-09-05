# Build `mdast-util-phrasing`

## Project Description

Create the `mdast-util-phrasing` project from an empty workspace. This is a repository-generation task for the frozen `node` package contract, task specification version `4.1.0`, at source revision `67d563d643f75cf4fd26bc3121ddebb89e3a0a9c`. Implement the public behavior described by the local inventories and the task-specific detail below; do not copy upstream source or tests. The supported scope is node, npm, esm, mdast, markdown, type-guard, predicate, repository-generation.

## Natural Language Instruction

Starting with an empty `workspace/`, create an installable `mdast-util-phrasing` project. Implement every public/core API named in the API Usage Guide, its package exports, and its documented integration points. Preserve observable input types, return shapes, ordering, determinism, state changes, and documented exception behavior. The project must be usable through its declared `mdast_util_phrasing` import path (or the package root for this Node task), and all required modules must be present in the directory structure below.

The task-specific specification retained below supplies the detailed behavior for each API family. Treat it as the contract: do not add unrelated APIs, replace deterministic behavior with randomized or time-dependent behavior, or weaken error handling.

## Supports

- Language/runtime: `node` on `24.19.0`; target environment metadata declares `debian-bookworm`.
- Distribution/package: `mdast-util-phrasing`; import/root name: `mdast_util_phrasing`. Package manager: `npm`.
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

The public/core API families recorded in the local inventory are: `phrasing(value)`.

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
import_or_require = "mdast_util_phrasing"
```

The retained task-specific examples below provide ordinary API calls and combinations grounded in the frozen inventory. Keep their result shapes and ordering exact.

## Error Handling and Boundary Conditions

- Empty inputs, malformed values, missing resources, duplicate values, and unsupported options must follow the task-specific error contracts below; do not silently coerce or discard information unless explicitly specified.
- Repeated calls must remain deterministic. Filesystem, process, clock, random, native, callback, and serialization boundaries are supported only where the local specification documents them.
- Network attempts are prohibited and must not be used as a fallback. Installation failures, missing offline dependencies, or unsupported external capabilities are environment/source concerns, not reasons to invent behavior.


## Source-derived task detail

# Build `mdast-util-phrasing`

## Project Description

Create a complete installable npm package named `mdast-util-phrasing`, version
`4.1.0`, from an empty workspace. The package is an ESM utility that determines
whether an mdast node is phrasing content. It has one public function,
`phrasing`, and no default export.

This is a repository-generation task. Implement the behavior with your own
source files; do not copy a reference implementation or upstream tests into the
repository.

## Supports

- Run on Node `24.19.0` with npm `11.17.0` on `linux/amd64` with glibc.
- Use ESM with `"type": "module"`. The package root must provide the named
  export `phrasing` through a safe in-package `exports` entry.
- Include a committed npm v3 `package-lock.json` consistent with
  `package.json`. The package must install from a clean checkout with:

  ```bash
  npm ci --offline --ignore-scripts --no-audit --no-fund
  ```

- The verifier provides an offline npm cache containing the frozen runtime
  dependency closure for `@types/mdast@4.0.4`, `@types/unist@3.0.3`, and
  `unist-util-is@6.0.1`. You may use that closure or implement the behavior
  without runtime dependencies.
- Do not use lifecycle hooks, native addons, custom loaders, workspaces,
  registry configuration, network access, filesystem state, current time, or
  randomness.

## API Usage Guide

### `phrasing(value)`

Import path and signature:

```js
import {phrasing} from 'mdast-util-phrasing'

phrasing(value?: unknown): boolean
```

Return `true` when `value` is a node object whose `type` is one of these exact,
case-sensitive strings:

```text
break
delete
emphasis
footnote
footnoteReference
image
imageReference
inlineCode
inlineMath
link
linkReference
mdxJsxTextElement
mdxTextExpression
strong
text
textDirective
```

Return `false` for omitted input, `null`, primitives, arrays, objects without a
valid string `type`, unknown node types, and block node types such as
`paragraph`, `heading`, `list`, and `html`. `html` is deliberately excluded
because mdast permits it in both phrasing and flow contexts.

Only the node's `type` determines the result. Other fields, including
`children`, `value`, `url`, position data, and extension-specific properties,
must not change classification. The function is synchronous, deterministic,
does not coerce types, does not mutate its argument, and does not throw for any
JavaScript value.

Examples:

```js
phrasing({type: 'paragraph', children: [{type: 'text', value: 'Alpha'}]})
// => false

phrasing({type: 'strong', children: [{type: 'text', value: 'Delta'}]})
// => true

phrasing({type: 'html', value: '<b>Echo</b>'})
// => false

phrasing({type: 'textDirective', name: 'mark'})
// => true
```

## Implementation Notes

Keep the root package importable without a build step. TypeScript declarations
may express `phrasing` as a type predicate, but runtime behavior is the contract
above. The evaluator packs and installs the submitted repository, then invokes
the package only in an unprivileged child process over a bounded JSON protocol;
runtime evaluator code never imports candidate files and candidate code cannot
write verifier-owned grading or reward reports.
