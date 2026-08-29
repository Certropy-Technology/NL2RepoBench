# Project Description

Build an installable ESM npm package named `hast-util-to-jsx-runtime` from an
empty workspace. The package transforms a HAST or MDX-HAST tree into values
created by an automatic JSX runtime. Reproduce the documented public behavior
with an independent implementation; do not copy the pinned upstream source or
tests.

# Supports

- Node.js `24.19.0` and npm `11.17.0` on Linux amd64 with glibc.
- ESM package semantics with `"type": "module"`, a root `exports` entry, and
  `index.js` plus `index.d.ts`.
- A committed npm lockfile with `lockfileVersion: 3`. Runtime dependencies
  must be installed by `npm ci --offline --ignore-scripts --no-audit --no-fund`.
- The JSON-compatible tree subset described below. The evaluator invokes the
  package through a verifier-owned child process; no CLI is required.
- No lifecycle scripts, workspaces, native addons, custom loaders, or runtime
  network access.

# API Usage Guide

Export a named function from the package root:

```js
import {toJsxRuntime} from 'hast-util-to-jsx-runtime'
```

Its signature is `toJsxRuntime(tree, options)`. `tree` is a JSON-compatible
`Nodes` value. `options` is required and must contain `Fragment`. In production
mode it must also contain callable `jsx` and `jsxs`; in development mode set
`development: true` and provide callable `jsxDEV`. The function returns the
value produced by the selected runtime callback.

The runtime callbacks receive `(type, props)` or `(type, props, key)` in
production. `jsxs` is selected when `props.children` is an array of two or more
children; `jsx` is used otherwise. A root text node or an empty result is
wrapped with `Fragment`. Each named direct child element receives a key such as
`tagName-0`, with the counter increasing independently per name, when
`passKeys` is enabled (the default).

The JSON tree forms used by this task are:

- `{type: "root", children: Nodes[]}`
- `{type: "element", tagName: string, properties: object, children: Nodes[]}`
- `{type: "text", value: string}`
- `{type: "mdxJsxFlowElement" | "mdxJsxTextElement", name: string | null, attributes: Attribute[], children: Nodes[]}`
- `{type: "mdxFlowExpression" | "mdxTextExpression" | "mdxjsEsm", data: {estree: Program}}`

HTML properties are converted using `property-information`: space-separated
arrays become strings, comma-separated properties use commas, nullish values
and numeric `NaN` are ignored, and `className`, `htmlFor`, boolean properties,
`style`, and `data-*`/`aria-*` values follow the documented React property
names. With `space: "svg"`, SVG property information is used. `style` strings
become objects; `stylePropertyNameCase: "css"` returns CSS keys such as
`text-align`, while the default `"dom"` returns `textAlign`.

The options are:

- `components`: a mapping from literal element names to replacement component
  values.
- `passNode`: when true and a replacement component is used, add the original
  node as `props.node`.
- `passKeys`: default true; set false to omit generated child keys.
- `space`: `"html"` (default) or `"svg"`; selects the initial property schema.
- `elementAttributeNameCase`: `"react"` (default) or `"html"`.
- `stylePropertyNameCase`: `"dom"` (default) or `"css"`.
- `tableCellAlignToStyle`: default true; move `align` on `td`/`th` into the
  style object. Set false to retain the `align` property.
- `ignoreInvalidStyle`: default false; invalid CSS raises a `VFileMessage`,
  while true converts it to an empty style object.
- `filePath`: optional source filename used by development runtime metadata.
- `createEvaluater`: optional factory returning `evaluateExpression(expression)`
  and `evaluateProgram(program)`. It is required for MDX estrees and dynamic
  uppercase/member component names.

In development mode `jsxDEV` receives `(type, props, key, isStaticChildren,
source, self)`. `source.fileName`, `source.lineNumber`, and
`source.columnNumber` are derived from the node position; `isStaticChildren`
is true exactly when the children value is an array.

# Implementation Notes

Keep tree traversal deterministic and do not mutate the input tree or its
properties. Preserve text exactly, including whitespace and line endings.
Nested HTML-to-SVG traversal switches schema at an `svg` element and restores
the parent schema afterwards. Table-family elements discard whitespace-only
text children; table-cell alignment conversion applies only to `td` and `th`.

MDX JSX literal attributes use their literal names and values. Expression
attributes and MDX expression/ESM nodes must be delegated to the evaluator;
without one, throw an error explaining that the estree cannot be handled.
Errors for missing `Fragment`, `jsx`, `jsxs`, or `jsxDEV` are part of the
contract and must be ordinary typed errors with actionable messages.

The verifier's JSONL adapter supplies only plain JSON values and serializes the
runtime callback results. It is not an additional public API requirement.
