# Build `css-tree`

## Project Description

Create an installable npm package named `css-tree`, version `3.2.1`, from an
empty workspace. It is a JavaScript CSS parser toolkit: it tokenizes CSS,
parses CSS and CSS values into an AST, generates CSS from that AST, walks AST
nodes, validates CSS values with its lexer, and parses CSS definition syntax.

This is a repository-generation task. Implement the package behavior with your
own source files. Do not copy the pinned upstream repository or its tests.

## Supports

- Node `24.19.0`, npm `11.17.0`, Linux amd64 with glibc.
- ESM package semantics: `package.json` must contain `"type": "module"` and
  the package root must be importable with `import * as csstree from 'css-tree'`.
- A committed npm v3 lockfile must support
  `npm ci --offline --ignore-scripts --no-audit --no-fund`.
- Runtime dependencies are exactly the declared `mdn-data` and
  `source-map-js` packages, resolved by the lockfile. Do not use git, file,
  workspace, native-addon, registry-override, or network dependencies.
- Do not add `preinstall`, `install`, `postinstall`, `prepare`, or `postpack`
  lifecycle scripts. The verifier ignores lifecycle scripts and does not run
  a browser bundle or a terminal UI.
- The scored contract is JSON-safe and deterministic. Do not require a TTY,
  filesystem fixture, clock, random state, browser, or network service.

## API Usage Guide

### Package root and AST conversion

The root module must export `parse`, `generate`, `tokenize`, `walk`, `find`,
`findLast`, `findAll`, `toPlainObject`, `clone`, `lexer`, `definitionSyntax`,
`ident`, `string`, `url`, `tokenNames`, and `tokenTypes`. It must also expose
`version`, `List`, `Lexer`, `TokenStream`, `OffsetToLocation`, `createSyntax`,
`createLexer`, `fork`, and the other public names documented by the package.

`toPlainObject(node)` returns a recursively JSON-compatible AST. It converts
`List` children to arrays and preserves ordinary node fields, including
`type`, `loc`, `name`, `value`, `unit`, `property`, `important`, and nested
`children`. `fromPlainObject(object)` may be used where needed to reconstruct
an AST, and `clone(node)` returns an independent copy.

### Parsing and generation

**Import path:** `parse` and `generate` from the package root.

**Signatures:**

```js
parse(source, options?)
generate(ast, options?)
```

`source` is a CSS string. The supported parse contexts are `stylesheet` (the
default), `value`, `selector`, and `declaration`. Parsing returns an AST and
must reject malformed input with an ordinary error. With `positions: true`,
nodes may include source locations; the scored calls use the default
position-free form. `generate()` accepts an AST returned by `parse()` or its
plain-object round trip and returns a CSS string. Generation is deterministic;
it may normalize insignificant whitespace but must preserve CSS meaning,
comments, quoted strings, escapes, and declaration importance.

Examples:

```js
const ast = parse('a{color:red;margin:0 1px}');
generate(ast); // 'a{color:red;margin:0 1px}'
parse('1px solid red', {context: 'value'});
parse('div.foo > a:hover', {context: 'selector'});
```

The JSON verifier only sends strings and plain option objects. Callbacks,
custom node types, source-map handlers, and locations are outside the scored
boundary except where explicitly listed below.

### Tokenizer

**Import path:** `tokenize`, `tokenNames`, and `tokenTypes` from the root.

**Signature:**

```js
tokenize(source, onToken)
```

`onToken(type, start, end)` is called once per CSS token in source order.
`start` is inclusive and `end` is exclusive. `type` is the numeric token type;
`tokenNames[type]` is its stable human-readable name. The callback return value
is ignored. The verifier converts each callback to `{type, name, raw}` before
JSON serialization. Empty input produces no callback.

### AST traversal and search

**Import path:** `walk`, `find`, `findLast`, and `findAll` from the root.

```js
walk(ast, options)
find(ast, predicate)
findLast(ast, predicate)
findAll(ast, predicate)
```

`walk` accepts `{enter, leave, visit, reverse}`. It visits nodes in document
order by default, can restrict traversal with `visit: 'NodeType'`, and supports
`this.skip()` and `this.break()` in ordinary JavaScript callers. The scored
adapter uses an `enter` callback to collect node type/property names. `find`
returns the first matching node, `findLast` the last matching node, and
`findAll` an array of all matching nodes; predicates receive `(node, item,
list)` and are limited by the JSON adapter to node-type predicates.

### Definition syntax

**Import path:** `definitionSyntax` from the root.

```js
definitionSyntax.parse(source)
definitionSyntax.generate(ast)
definitionSyntax.walk(ast, options?)
```

The parser accepts CSS value definition syntax such as
`<length> | auto` and `[ <length> | auto ]#`; generation returns its
deterministic textual form. Invalid syntax raises an ordinary error. The JSON
boundary returns the plain object representation of the parsed syntax tree.

### Lexer property matching

**Import path:** `lexer` from the root.

```js
lexer.matchProperty(property, valueAst)
```

For a parsed value AST, the lexer validates the value against the CSS syntax
for the named property and returns a match object containing `matched`,
`iterations`, and `error`. `matched` is serializable after `toPlainObject()`.
The scored boundary sends known CSS property/value pairs and checks both
successful matches and stable failure reporting; internal lexer graphs are not
part of the required output.

### String, identifier, and URL utilities

The namespaces `string`, `ident`, and `url` each expose `encode()` and
`decode()` for CSS escapes. `ident.encode(value)` produces a valid CSS
identifier, `string.encode(value, apostrophe?)` produces a quoted CSS string,
and `url.encode(value)` escapes a URL-compatible CSS token. Their decode
functions reverse valid escapes deterministically. Inputs are finite strings;
custom encoders and non-string objects are outside the boundary.

## JSON-safe subprocess boundary

The verifier-owned adapter launches a fresh child Node process for each JSONL
request. A request is one object with `id`, `operation`, and `payload`. The
allowlisted operations are `shape`, `parse-generate`, `tokens`, `walk`,
`find`, `definition`, `lexer`, and `utils`. The adapter imports the candidate
only inside that child and returns one bounded JSON response line. Candidate
stdout must contain no diagnostics, timestamps, paths, or object addresses.

The adapter never transports callbacks, `List`, `TokenStream`, lexer instances,
functions, symbols, cyclic values, file descriptors, or source maps. Errors
must become `{ok:false,errorType,message}` with a bounded message; a candidate
must not write verifier reports.

## Production Slice

The upstream Mocha suite is a development baseline only. The frozen production
denominator is 32 independent `node:test` leaves covering package shape,
stylesheet/value/selector parsing and generation, token boundaries, AST
round-tripping and cloning, traversal/search order, definition syntax, lexer
success/failure, and deterministic CSS escape utilities. Every scored leaf is
described in task-local traceability; the contract is intentionally narrower
than the 16,725-case upstream suite while retaining behavior across the core
public modules.

