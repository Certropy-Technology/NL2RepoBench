# Build `mdast-util-from-markdown`

## Project Description

Create the `mdast-util-from-markdown` project from an empty workspace. This is a repository-generation task for the frozen `node` package contract, task specification version `1.0.0`, at source revision `f94143765912425fb94ed6518d3a3d1c54f994d4`. Implement the public behavior described by the local inventories and the task-specific detail below; do not copy upstream source or tests. The supported scope is node, npm, esm, markdown, mdast, parser, ast, json.

## Natural Language Instruction

Starting with an empty `workspace/`, create an installable `mdast-util-from-markdown` project. Implement every public/core API named in the API Usage Guide, its package exports, and its documented integration points. Preserve observable input types, return shapes, ordering, determinism, state changes, and documented exception behavior. The project must be usable through its declared `mdast_util_from_markdown` import path (or the package root for this Node task), and all required modules must be present in the directory structure below.

The task-specific specification retained below supplies the detailed behavior for each API family. Treat it as the contract: do not add unrelated APIs, replace deterministic behavior with randomized or time-dependent behavior, or weaken error handling.

## Supports

- Language/runtime: `node` on `24.19.0`; target environment metadata declares `debian-bookworm`.
- Distribution/package: `mdast-util-from-markdown`; import/root name: `mdast_util_from_markdown`. Package manager: `npm`.
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

The public/core API families recorded in the local inventory are: `fromMarkdown(value, encoding?, options?)`.

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
import_or_require = "mdast_util_from_markdown"
```

The retained task-specific examples below provide ordinary API calls and combinations grounded in the frozen inventory. Keep their result shapes and ordering exact.

## Error Handling and Boundary Conditions

- Empty inputs, malformed values, missing resources, duplicate values, and unsupported options must follow the task-specific error contracts below; do not silently coerce or discard information unless explicitly specified.
- Repeated calls must remain deterministic. Filesystem, process, clock, random, native, callback, and serialization boundaries are supported only where the local specification documents them.
- Network attempts are prohibited and must not be used as a fallback. Installation failures, missing offline dependencies, or unsupported external capabilities are environment/source concerns, not reasons to invent behavior.


## Source-derived task detail

# Build `mdast-util-from-markdown`

## Project Description

Create an installable ESM npm package named `mdast-util-from-markdown`, version
`2.0.3`. Its root entry point must export the named function `fromMarkdown`.
The function parses CommonMark-oriented Markdown into an mdast syntax tree.

The evaluation contract is a deterministic, JSON-safe subset of the package.
It starts a fresh process for each scenario and passes a Markdown string. The
returned tree must be JSON serializable. Do not implement network access,
filesystem discovery, mutable global state, or a CLI.

## Supports

- Node `24.19.0` and npm `11.17.0` on Linux amd64 with glibc.
- ESM packaging with `"type": "module"`, package name and version matching the
  contract, and a root `exports` entry that resolves the named `fromMarkdown`.
- Exact runtime dependencies matching the package contract and a root npm
  lockfile using lockfile version 3. The verifier installs with
  `npm ci --offline --ignore-scripts --no-audit --no-fund`.
- JSON-safe inputs: Markdown strings no larger than 64 KiB. Trees and node
  fields must remain ordinary JSON strings, numbers, booleans, nulls, arrays,
  and objects.

## API Usage Guide

### `fromMarkdown(value, encoding?, options?)`

Import it with:

```js
import {fromMarkdown} from 'mdast-util-from-markdown'
const tree = fromMarkdown('# hello')
```

The required `value` is a string in this task. Return a Root object with
`type: 'root'`, a `children` array, and positional information for parsed
nodes. The parser must preserve source order and use mdast node shapes.

The JSON-safe contract covers empty documents, paragraphs and soft line breaks,
ATX and setext headings, emphasis and strong emphasis, inline code, fenced and
indented code, block quotes, ordered and unordered lists, thematic breaks,
links, images, link definitions and reference links, autolinks, raw HTML nodes,
character escapes and character references, hard breaks, Unicode text, and
deterministic source positions. Inline and block nodes must use the standard
mdast fields such as `url`, `title`, `alt`, `depth`, `lang`, `meta`, `ordered`,
`start`, `spread`, `checked`, `label`, `identifier`, and `referenceType` where
those fields apply.

Malformed extension callbacks, custom micromark extensions, typed-array input,
streaming input, browser globals, and non-JSON values are outside this task's
subprocess contract. Do not add a default export in place of the required named
export.

## Implementation Notes

Use a clean package root that can be packed and installed by npm. Keep all
runtime behavior deterministic and independent of wall clock, locale, random
values, environment-specific paths, and network state. `position` objects use
one-based `line` and `column` values and zero-based `offset` values. Preserve
the distinction between `null` fields defined by mdast and omitted fields.

The hidden verifier invokes only the public package from a separate unprivileged
Node process. It owns test collection, timeouts, reports, and scoring. Do not
write reward, grading, JUnit, or verifier files from the candidate package.
