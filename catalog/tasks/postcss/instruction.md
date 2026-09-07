# postcss

## Project Description

Build an installable `postcss` project from an empty `workspace/`. The project must reproduce the public, local behavior documented in this instruction, including its package entry points, return shapes, ordering, state changes, and documented exceptions. This is a repository-generation task: the agent creates the build metadata and source modules rather than editing an existing implementation.

Distribution/package identity: `postcss`; root module entry is the package entry documented below.
The scope is the deterministic local API described below. Network services, undeclared external state, and behavior not represented by the public contract are outside the task.

## Natural Language Instruction

Create the complete project in an empty workspace and make it installable with the command in the environment section. Implement these task-specific capability families from the local API contract:

1. `Root factory and exports`: expose the documented public entry points, signatures, inputs, outputs, and error behavior.
2. `Parsing and stringifying`: preserve the documented object or module behavior, including state and side effects.
3. `Tree construction and mutation`: preserve ordering, determinism, serialization, and boundary semantics where specified.
4. `Processing plugins`: make the public package usable through the documented import path or command-line entry.

Do not add speculative APIs or substitute a different package. Keep the implementation self-contained, ensure imports work after installation, and use the exact public names and signatures in the API Usage Guide. A small implementation is acceptable only when it still satisfies every documented contract.

## Supports or Environment Configuration

- Node.js 24.19.0 with npm 11.17.0.
- Distribution/package identity: `postcss`; root module entry is the package entry documented below.
- Install from the workspace with `npm install --offline` using the declared lockfile.
- Declared build/runtime packages are supplied by the frozen evaluation image: `nanoid@3.3.18`, `picocolors@1.1.1`, `source-map-js@1.2.1`
- Build metadata and package data must be present in the workspace and agree with the public import paths below.
- Agent, candidate, evaluator, Oracle, and control execution are network-isolated. Do not access GitHub, package registries, DNS, databases, or external services at runtime.
- Use deterministic local inputs. Do not rely on the current wall clock, host-specific absolute paths, undeclared environment variables, or an installed copy of the target package.

## Project Directory Structure

```text
workspace/
├── package.json
├── package-lock.json
├── index.js
├── index.d.ts
```

The tree lists agent-owned public project files only. Add additional public modules when required by the API Usage Guide, but keep their import paths consistent with package metadata. Do not create evaluator-only files, hidden fixtures, or private reports in the generated project.

## API Usage Guide

The following is the task-specific public contract recovered from the local instruction and inventory. For every function, class, method, constant, export, and command named below, preserve its complete signature, accepted input domain, return type and shape, ordering, determinism, state/side effects, exceptions, and examples. When the source contract gives an optional argument or a compatibility alias, it is part of the required surface.

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


The private verifier calls candidate code only through a bounded JSON
subprocess adapter as an unprivileged user. It never imports candidate code in
the trusted test process. Support only the documented JSON-safe operation
surface and preserve deterministic source order; callbacks, custom parsers,
source-map generation, arbitrary plugin code, filesystem I/O, and external
syntaxes are outside this task.

## Implementation Notes

- Keep the root exports and module paths stable after installation; do not make behavior depend on the repository's current directory.
- Preserve explicit ordering guarantees. When the contract does not promise an order, do not introduce a new observable order accidentally.
- Propagate documented exceptions and avoid replacing them with generic errors. Validate malformed, empty, boundary, and repeated inputs as described by the API contract.
- Keep filesystem, process, terminal, and resource effects bounded and local. Close files and other resources on both success and failure.
- Do not copy an upstream checkout, implementation source, or evaluation-only material into the generated project. Implement the public behavior from this specification.

## Examples

The examples below are retained from the local task specification. They are starting points for ordinary calls and boundary/error behavior; their exact output and exception semantics remain governed by the API Usage Guide.

### Example 1: ordinary usage
```text
const postcss = require('postcss')
const processor = postcss([plugin])
```

### Example 2: ordinary usage
```text
const root = postcss.parse('a { color: red; }')
root.type // 'root'
root.first.type // 'rule'
root.first.selector // 'a'
root.first.first.prop // 'color'
root.first.first.value // 'red'
root.toString() // 'a { color: red; }'
```

### Example 3: boundary or error behavior
```text
const result = postcss([
  { postcssPlugin: 'rename-color', Declaration(decl) { if (decl.value === 'red') decl.value = 'blue' } }
]).process('a { color: red }', { from: 'input.css' })
```

### Example 4: boundary or error behavior
```text
const postcss = require('postcss')
const processor = postcss([plugin])
```


## Error Handling and Boundary Conditions

- Empty inputs, invalid types, malformed text or paths, unavailable resources, duplicate calls, and cancellation/timeout cases must follow the exception and return-value contracts documented for the relevant API.
- Do not silently coerce values, reorder results, swallow exceptions, or use a fallback dependency unless the API section explicitly requires that behavior.
- File and environment operations must use caller-provided paths and documented defaults only; never read undeclared host files or network resources.
- The implementation must remain usable in the stated NoNetwork environment. A missing optional integration should expose the documented availability or error behavior rather than attempting an online install.
- Security-sensitive inputs must be treated as data. Do not execute strings, load untrusted code, or interpolate shell commands unless that behavior is explicitly part of the documented public API.
