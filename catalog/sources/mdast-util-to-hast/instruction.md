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
