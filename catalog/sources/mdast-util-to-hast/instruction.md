# Build `mdast-util-to-hast`

## Project Description

Create the `mdast-util-to-hast` project from an empty workspace. This is a repository-generation task for the frozen `node` package contract, task specification version `2.0.0`, at source revision `174795b21f7757fffb54dd8d5fb4012f4751f791`. Implement the public behavior described by the local inventories and the task-specific detail below; do not copy upstream source or tests. The supported scope is node, npm, esm, markdown, mdast, hast, ast, html.

## Natural Language Instruction

Starting with an empty `workspace/`, create an installable `mdast-util-to-hast` project. Implement every public/core API named in the API Usage Guide, its package exports, and its documented integration points. Preserve observable input types, return shapes, ordering, determinism, state changes, and documented exception behavior. The project must be usable through its declared `mdast_util_to_hast` import path (or the package root for this Node task), and all required modules must be present in the directory structure below.

The task-specific specification retained below supplies the detailed behavior for each API family. Treat it as the contract: do not add unrelated APIs, replace deterministic behavior with randomized or time-dependent behavior, or weaken error handling.

## Supports

- Language/runtime: `node` on `24.19.0`; target environment metadata declares `debian-bookworm-amd64`.
- Distribution/package: `mdast-util-to-hast`; import/root name: `mdast_util_to_hast`. Package manager: `npm`.
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

The public/core API families recorded in the local inventory are: `toHast`, Definitions, references, and footnotes, Data and options.

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
import_or_require = "mdast_util_to_hast"
```

The retained task-specific examples below provide ordinary API calls and combinations grounded in the frozen inventory. Keep their result shapes and ordering exact.

## Error Handling and Boundary Conditions

- Empty inputs, malformed values, missing resources, duplicate values, and unsupported options must follow the task-specific error contracts below; do not silently coerce or discard information unless explicitly specified.
- Repeated calls must remain deterministic. Filesystem, process, clock, random, native, callback, and serialization boundaries are supported only where the local specification documents them.
- Network attempts are prohibited and must not be used as a fallback. Installation failures, missing offline dependencies, or unsupported external capabilities are environment/source concerns, not reasons to invent behavior.


## Source-derived task detail

# Project Description

Create a complete, installable npm package named `mdast-util-to-hast`, version
`13.2.1`, from an empty workspace. The package transforms a Markdown abstract
syntax tree (mdast) into an HTML abstract syntax tree (hast). The result is
plain JSON-shaped data suitable for a renderer; this task does not ask for an
HTML string renderer.

The scored behavior is deterministic, synchronous transformation of bounded
plain objects. The package must not read files, use a clock or randomness,
start subprocesses, or access the network.

# Supports

- Node.js `24.19.0`, npm `11.17.0`, `linux/amd64`, and ESM semantics.
- `package.json` must declare the exact name and version, use `"type": "module"`,
  expose the package root as `./index.js`, and include a declaration entry for
  `./index.js`. The root must export `toHast`, `defaultFootnoteBackContent`,
  `defaultFootnoteBackLabel`, and `defaultHandlers` as named exports.
- Commit a v3 `package-lock.json` consistent with the package. A clean verifier
  runs `npm ci --offline --ignore-scripts --no-audit --no-fund` and then packs
  the candidate with `npm pack --ignore-scripts`.
- Runtime JavaScript and declarations must already be present. Do not depend on
  `prepack`, `prepare`, TypeScript, a loader, a registry, or lifecycle downloads.
  Do not use workspaces, native addons, or executable install hooks.
- The package may be self-contained. If dependencies are used, they must be
  declared exactly and be usable from the verifier's prebuilt offline closure;
  Node built-ins are not npm dependencies. A zero-dependency implementation is
  valid.
- The verifier passes only JSON-compatible mdast trees and options: null,
  booleans, finite numbers, strings, arrays, and plain objects. Functions,
  symbols, class instances, cyclic objects, VFile instances, custom handlers,
  custom unknown handlers, and shared object identity are outside the scored
  boundary.

The upstream source at the frozen revision contains a broader TypeScript/JSDoc
development suite. This task uses a private 35-leaf contract derived from its
observable API and behavior. It is not necessary to reproduce the upstream
repository layout, test runner, lint configuration, or source code.

# API Usage Guide

## `toHast`

Import path: named export `toHast` from the package root.

Signature:

```js
toHast(tree, options?) => HastRoot | HastNode | null
```

`tree` is an mdast root or one supported mdast node represented as a plain
object. `options` is omitted, `null`, or a plain object. The function is
synchronous and does not mutate the input tree. A root produces a HAST root;
node inputs produce the corresponding HAST node; ignored root-level nodes result
in an empty HAST root.

The following mappings are required: root, paragraph, text, emphasis, strong,
delete, inlineCode, break, heading, blockquote, thematicBreak, code, link,
image, list/listItem, table/tableRow/tableCell, and raw HTML. Text nodes become
`{type: "text", value}` and may preserve a copied `position` field; elements become
`{type: "element", tagName, properties, children}`. Root children preserve
source order, with the package's deterministic newline handling between block
nodes.

Text and URL values are normalized according to the package contract. Text
content is preserved, while unsafe or control characters in link/image URLs are
percent-encoded or rejected as the ordinary sanitizer behavior requires.
Inline code and fenced code preserve code text, add the expected `className`
language property for `lang`, and preserve `meta` as the `dataMeta` property.
Ordered lists preserve `start` when it is not one; unordered lists use `ul`.
Table alignment is represented by the corresponding `align` property on cells.

## Definitions, references, and footnotes

Root definitions are resolved for `linkReference` and `imageReference` nodes.
Collapsed and shortcut references use their identifier lookup; an unresolved
reference falls back to its visible text/image representation. Definition and
footnote-definition nodes are not emitted as ordinary body children.

Footnote references and definitions produce the deterministic section with
`id="user-content-fn-<identifier>"`, `href="#user-content-fnref-<identifier>"`,
an ordered list, and backlink anchors. Repeated references receive stable
suffixes. The default footnote label and backlink functions are also exported:

```js
defaultFootnoteBackLabel(referenceIndex, rereferenceIndex?) => string
defaultFootnoteBackContent(referenceIndex, rereferenceIndex?) => HAST text[]
```

The default label uses the zero-based reference index plus one, producing
`Back to reference N`; a missing index is treated as the ordinary first
reference by the upstream helper. Back content is a one-element text array
containing the left arrow marker. Numeric arguments are ordinary finite values
within the JSON boundary.

## Data and options

`data.hName` changes the element tag name. `data.hProperties` supplies HAST
properties and `data.hChildren` supplies JSON-compatible children where the
ordinary API permits it. Unknown nodes are rendered as text using their
`value` when available, otherwise as a `div`-like element with transformed
children. `options.allowDangerousHtml` controls whether mdast `html` nodes are
emitted as HAST `raw` nodes or ignored. `options.clobberPrefix` changes the
prefix used for generated footnote ids. `options.footnoteLabel` and
`options.footnoteLabelProperties` customize the generated footnote heading.

`defaultHandlers` is a plain object whose keys include the standard mdast node
types and whose values are functions. Its shape is checked only through a
JSON-safe inventory; callback invocation and custom handler options are outside
the subprocess contract.

# Implementation Notes

- Preserve deterministic ordering and do not sort nodes or properties by an
  unrelated key.
- Keep output JSON-serializable. Do not expose functions, prototypes, source
  locations, private state, or candidate-written reports.
- The verifier owns test collection, scoring, JUnit/JSON reports, and network
  proof in a separate no-network environment. Files named `reward.json`,
  `grading.json`, or test files in the candidate workspace are not trusted.
- File, URL, stream, callback, custom handler, VFile, and non-JSON values are
  deliberately excluded rather than silently approximated.
