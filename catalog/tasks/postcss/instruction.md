# Build `postcss`

## Project Description

Create an installable npm package named `postcss`, version `8.5.26`. PostCSS
parses CSS into a mutable syntax tree, stringifies that tree while preserving
author formatting where possible, and runs synchronous or asynchronous
JavaScript plugins over the tree. This is a repository-generation task: write
your own package files rather than copying the pinned upstream source or its
tests.

## Supports

- Node.js `24.19.0`, npm `11.17.0`, linux/amd64, CommonJS `require('postcss')`
  and ESM default/named imports from the package root.
- `package.json` must name version `8.5.26`, expose a CommonJS root entry and
  include TypeScript declarations. Include a lockfile with
  `lockfileVersion: 3` that agrees with the manifest.
- The verifier runs `npm ci --offline --ignore-scripts --no-audit --no-fund`.
  The available runtime dependencies are exact `nanoid@3.3.18`,
  `picocolors@1.1.1`, and `source-map-js@1.2.1`; no other runtime dependency
  is available.
- Do not use native addons, workspaces, custom Node loaders, registry settings,
  lifecycle scripts, subprocesses, filesystem-dependent transforms, network
  access, clock, or randomness on the scored paths.

## API Usage Guide

### Root factory and exports

```js
const postcss = require('postcss')
const processor = postcss([plugin])
```

The root export is callable. Calling it with an array (or variadic plugins)
returns a `Processor`; its `version` is `8.5.26`. The root exposes callable
helpers `parse`, `stringify`, `fromJSON`, `root`, `rule`, `decl`, `atRule`,
`comment`, and `document`, as well as constructible exports `Root`, `Rule`,
`Declaration`, `AtRule`, `Comment`, `Container`, `Node`, `Processor`,
`Result`, `Input`, `Warning`, and `CssSyntaxError`.

### Parsing and stringifying

```js
const root = postcss.parse('a { color: red; }')
root.type // 'root'
root.first.type // 'rule'
root.first.selector // 'a'
root.first.first.prop // 'color'
root.first.first.value // 'red'
root.toString() // 'a { color: red; }'
```

`parse(css, options?)` accepts CSS text and returns a `Root` with ordered
`nodes`. Nodes have `type`, mutable data fields, `raws`, and parent relations.
The scored node kinds are `root`, `rule`, `decl`, `atrule`, and `comment`.
Rules contain a `selector`; declarations contain `prop`, `value`, and optional
`important`; at-rules contain `name`, `params`, and optional child nodes;
comments contain `text`.

`root.toString()` and `postcss.stringify(root, builder)` serialize in node
order. Parsing and serializing must preserve comments, at-rules, declaration
importance, nested rules, escaped/quoted text, and ordinary whitespace for the
bounded CSS inputs in this task. Invalid CSS must throw a `CssSyntaxError`
with `name === 'CssSyntaxError'`; the error message must contain the supplied
`from` filename when `from` is provided.

### Tree construction and mutation

Create nodes with `postcss.root`, `postcss.rule`, `postcss.decl`,
`postcss.atRule`, and `postcss.comment`. A declaration construction value is
coerced to a string. `append`, `prepend`, `insertBefore`, `insertAfter`,
`remove`, `removeAll`, `replaceWith`, `clone`, `cloneBefore`, and `cloneAfter`
return the affected node/container and update the tree order. `rule.selectors`
splits comma-separated selectors and its setter joins replacements.

`walk`, `walkRules`, `walkDecls`, `walkAtRules`, and `walkComments` visit the
tree in source order. Within the JSON-safe mutation operations described
below, changing a declaration value or appending/removing a node must mark the
tree dirty so subsequent stringification reflects it.

`root.toJSON()` returns a cycle-free representation that omits parent links.
`postcss.fromJSON(value)` rebuilds such a tree; stringifying a rebuilt tree
has the same CSS result as the original JSON tree.

### Processing plugins

```js
const result = postcss([
  { postcssPlugin: 'rename-color', Declaration(decl) { if (decl.value === 'red') decl.value = 'blue' } }
]).process('a { color: red }', { from: 'input.css' })
```

`processor.process(css, options?)` returns a result-like object with a `css`
string and a `root`. It supports plugins with `postcssPlugin` and visitors
named `Once`, `Rule`, `Declaration`, `AtRule`, or `Comment`. Visitors run in
tree order and may mutate the node. The scored adapter supplies only the
following JSON plugin descriptors: replace declaration values, append a
declaration to every rule, prefix selectors, remove matching declarations, and
append a comment once. Plugin descriptors and requests are verifier protocol,
not part of the public package API.

Both synchronous `result.sync()` and `await result` must produce the final CSS
for synchronous visitors. An `async` visitor in a synchronous `sync()` call
must throw; awaiting the result must run it successfully. Warnings emitted by
`result.warn(text, options?)` are returned by `result.warnings()` in order.

## Implementation Notes

The private verifier calls candidate code only through a bounded JSON
subprocess adapter as an unprivileged user. It never imports candidate code in
the trusted test process. Support only the documented JSON-safe operation
surface and preserve deterministic source order; callbacks, custom parsers,
source-map generation, arbitrary plugin code, filesystem I/O, and external
syntaxes are outside this task.
