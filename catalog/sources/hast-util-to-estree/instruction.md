# Build `hast-util-to-estree`

## Project Description

Create an installable ESM npm package named `hast-util-to-estree`, version
`3.1.3`, from an empty workspace. The package transforms a HAST tree, including
the JSON-compatible MDX node forms described below, into an ESTree `Program`
whose expressions use the ESTree JSX extension.

The implementation is evaluated through a separate subprocess verifier. It
must not require the upstream repository, development tools, network access,
filesystem fixtures, clocks, randomness, or browser globals at runtime.

## Supports

- Node.js `24.19.0` and npm `11.17.0` on `linux/amd64` with glibc.
- ESM through `"type": "module"`; the package root must resolve to
  `./index.js` and provide declarations from `./index.d.ts`.
- A committed npm v3 lockfile. Installation is performed with
  `npm ci --offline --ignore-scripts --no-audit --no-fund` against a frozen
  dependency cache.
- Named root exports `toEstree` and `defaultHandlers`; there is no default
  export.
- Plain JSON-compatible HAST and MDX nodes. Do not use lifecycle scripts,
  workspaces, native addons, custom loaders, or external services.

Runtime dependencies may include the ordinary pure-JavaScript packages needed
for ESTree comments, HTML/SVG property information, style parsing, MDX node
types, positions, and handler dispatch. Declare all runtime dependencies and
lock their complete transitive closure.

## API Usage Guide

### `toEstree`

```js
// import hastUtilToEstree
import {toEstree} from 'hast-util-to-estree'

toEstree(tree, options?)
```

`tree` is a HAST node. Supported ordinary node forms are:

- `root`: `{type: "root", children?: Node[]}`
- `element`: `{type: "element", tagName: string, properties?: object,
  children?: Node[]}`
- `text`: `{type: "text", value?: string}`
- `comment`: `{type: "comment", value?: string}`
- `doctype`: `{type: "doctype"}`

The scored JSON subset additionally supports `mdxFlowExpression`,
`mdxTextExpression`, `mdxJsxFlowElement`, `mdxJsxTextElement`, and `mdxjsEsm`
nodes when their embedded `data.estree` values are JSON ESTree objects.

The function returns a fresh ESTree `Program`:

```js
{
  type: 'Program',
  body: [],
  sourceType: 'module',
  comments: []
}
```

For a renderable node, the final body item is an `ExpressionStatement`. An
element becomes a `JSXElement`. A root becomes a `JSXFragment`. A single text,
comment, or other non-element result is wrapped in a fragment. A doctype emits
no child. Empty roots still emit an empty fragment. Inputs are not mutated and
repeated calls are deterministic.

Text values become `JSXText` only when they are safe literal JSX text;
otherwise represent them as a `JSXExpressionContainer` containing a string
`Literal`. Preserve their exact value. Comments become empty JSX expressions
with block comments and are also listed in `Program.comments`.

Elements use `JSXOpeningElement` and, when children exist, a matching
`JSXClosingElement`. Empty elements are self-closing. Valid tag names can be
identifiers, member names such as `X.Y`, or namespace names such as `svg:path`.

Element properties map to JSX attributes:

- nullish values, `NaN`, and false values for boolean HTML properties are
  omitted;
- ordinary strings and numbers become literal attribute values;
- boolean true becomes an attribute with a null value;
- space-separated properties such as `className` join arrays with spaces;
- comma-separated properties such as `accept` join arrays with comma-space;
- non-identifier property names that cannot be JSX names are emitted through
  a JSX spread attribute containing an object property;
- style strings or plain style objects become an object expression;
- table-cell `align` is moved into `style.textAlign` by default.

Options are a plain object with these supported fields:

- `elementAttributeNameCase`: `"react"` (default) or `"html"`. For example,
  `className` remains React-cased by default and becomes `class` in HTML mode.
- `stylePropertyNameCase`: `"dom"` (default) or `"css"`. For example,
  `background-color` becomes `backgroundColor` in DOM mode and remains
  `background-color` in CSS mode.
- `space`: `"html"` (default) or `"svg"`, selecting the initial property
  schema. Entering an `svg` element switches nested elements to SVG and then
  restores the parent schema.
- `tableCellAlignToStyle`: true by default; false keeps the `align` attribute.

Invalid values that are not nodes throw an error containing
`Cannot handle value`. Unknown node types throw an error containing
`Cannot handle unknown node`. A malformed style string throws an actionable
error identifying the style and element.

Position information is copied when both offsets are present: `start`, `end`,
zero-based ESTree columns in `loc`, and `[start, end]` in `range`. A source
node's JSON-compatible `data` object is inherited by its corresponding output
node where documented by the transform.

Examples:

```js
toEstree({type: 'element', tagName: 'div', properties: {}, children: []})
// Program containing a self-closing <div /> JSXElement

toEstree({
  type: 'element',
  tagName: 'p',
  properties: {className: ['lead', 'wide']},
  children: [{type: 'text', value: 'Hello'}]
})
// Program containing <p className="lead wide">{"Hello"}</p>
```

### `defaultHandlers`

```js
import {defaultHandlers} from 'hast-util-to-estree'
```

This is the shared plain handler table used by `toEstree`. It exposes callable
handlers for `comment`, `doctype`, `element`, `mdxFlowExpression`,
`mdxJsxFlowElement`, `mdxJsxTextElement`, `mdxTextExpression`, `mdxjsEsm`,
`root`, and `text`. Consumers may inspect or reuse this table. Do not mutate it
during normal transformations.

## Implementation Notes

Keep output ordering deterministic. Whitespace-only line-feed text children
directly inside `table`, `tbody`, `thead`, `tfoot`, and `tr` are omitted;
other text is preserved. MDX expression and ESM nodes reuse their embedded
ESTree statements or expressions, and MDX JSX literal attributes map to JSX
attributes.

The public library also permits custom function-valued handlers. This task's
subprocess verifier cannot safely transport callbacks, prototypes, shared
object identity, or non-JSON values, so custom `options.handlers` callbacks
are outside the scored boundary. Implementations should retain the documented
public extension point when practical, but no hidden assertion requires a
function to cross the verifier protocol.

## Natural Language Instruction

Create this ESM package from an empty workspace. Implement the JSON-compatible
HAST and MDX transformation described above, preserving source values, child
ordering, JSX property semantics, position metadata, and deterministic output.
Do not use a hard-coded response table or copy the upstream implementation.

## Project Directory Structure

```text
workspace/
├── package.json
├── package-lock.json
├── index.js
├── index.d.ts
└── lib/
    ├── index.js
    ├── state.js
    └── handlers/
        ├── comment.js
        ├── doctype.js
        ├── element.js
        ├── expression.js
        ├── mdx.js
        ├── root.js
        └── text.js
```

The root exports `toEstree` and `defaultHandlers`; private fixtures and
verifier files are not agent-owned.

## Examples

```js
import {toEstree} from 'hast-util-to-estree';
const program = toEstree({type: 'element', tagName: 'p', properties: {}, children: []});
program.type; // 'Program'
```

```js
const program = toEstree({type: 'root', children: []});
program.body[0].expression.type; // 'JSXFragment'
```

## Error Handling and Boundary Conditions

- Unknown node types and malformed style values produce the documented errors.
- Preserve empty roots, doctype omission, comments, text, table whitespace,
  SVG context, and position data without mutating input nodes.
- Callback-valued custom handlers and non-JSON prototypes are outside the
  adapter boundary. All runtime phases use `network_mode=no-network`.
