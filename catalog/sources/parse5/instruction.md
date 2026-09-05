# parse5

## Project Description

Build an installable `parse5` project from an empty `workspace/`. The project must reproduce the public, local behavior documented in this instruction, including its package entry points, return shapes, ordering, state changes, and documented exceptions. This is a repository-generation task: the agent creates the build metadata and source modules rather than editing an existing implementation.

Distribution/package identity: `parse5`; root module entry is the package entry documented below.
The scope is the deterministic local API described below. Network services, undeclared external state, and behavior not represented by the public contract are outside the task.

## Natural Language Instruction

Create the complete project in an empty workspace and make it installable with the command in the environment section. Implement these task-specific capability families from the local API contract:

1. `Default tree representation`: expose the documented public entry points, signatures, inputs, outputs, and error behavior.
2. `parse(html, options?)`: preserve the documented object or module behavior, including state and side effects.
3. `parseFragment(...)`: preserve ordering, determinism, serialization, and boundary semantics where specified.
4. `serialize(node, options?)`: make the public package usable through the documented import path or command-line entry.

Do not add speculative APIs or substitute a different package. Keep the implementation self-contained, ensure imports work after installation, and use the exact public names and signatures in the API Usage Guide. A small implementation is acceptable only when it still satisfies every documented contract.

## Supports or Environment Configuration

- Node.js 24.19.0 with npm 11.17.0.
- Distribution/package identity: `parse5`; root module entry is the package entry documented below.
- Install from the workspace with `npm install --offline` using the declared lockfile.
- Declared build/runtime packages are supplied by the frozen evaluation image: `entities@8.0.0`
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

## Default tree representation

The default adapter returns plain JavaScript objects with parent links:

- A document has `nodeName: "#document"`, a `mode` (`"no-quirks"`,
  `"quirks"`, or `"limited-quirks"`), and `childNodes`.
- A document fragment has `nodeName: "#document-fragment"` and `childNodes`.
- An element has equal `nodeName` and `tagName` strings, an `attrs` array in
  source order, a namespace URI, `childNodes`, and `parentNode`. Each attribute
  is `{ name, value, namespace, prefix }`; absent namespace/prefix values are
  `null` or omitted consistently.
- Text nodes are `{ nodeName: "#text", value, parentNode }`; comments are
  `{ nodeName: "#comment", data, parentNode }`; document types expose
  `name`, `publicId`, and `systemId`.
- HTML `template` elements store parsed template children in a separate
  `content` document fragment rather than in the element's `childNodes`.

The namespace constants used by the default tree are:

```text
HTML   http://www.w3.org/1999/xhtml
SVG    http://www.w3.org/2000/svg
MATHML http://www.w3.org/1998/Math/MathML
XLINK  http://www.w3.org/1999/xlink
XML    http://www.w3.org/XML/1998/namespace
XMLNS  http://www.w3.org/2000/xmlns/
```

When source locations are enabled, explicit nodes include zero-based UTF-16
offsets and one-based lines/columns. Element locations also include `startTag`
and, when present, `endTag`; attribute locations are keyed by source attribute
name. Implicitly inserted `html`, `head`, `body`, and `tbody` elements have no
source location.

## `parse(html, options?)`

```ts
function parse(html: string, options?: ParserOptions): Document;
```

Parse a complete HTML document. `html` must be a string. The default options
are `scriptingEnabled: true`, `sourceCodeLocationInfo: false`, the default tree
adapter, and no parse-error callback.

The result follows HTML document parsing rules, including these observable
contracts:

- Missing `html`, `head`, and `body` elements are inserted. A standards
  `<!DOCTYPE html>` produces `mode: "no-quirks"`.
- Tag and HTML attribute names are ASCII-lowercased; duplicate attributes keep
  the first value. Character references are decoded in text and attributes.
- Optional end tags and malformed nesting are repaired. Paragraph starts close
  an open paragraph; table rows gain an implicit `tbody`; text that is invalid
  directly inside a table is foster-parented before the table; misnested
  formatting elements are reconstructed according to HTML parsing behavior.
- `script` and `style` content is raw text. `textarea`/`title` content is RCDATA:
  character references are decoded but nested markup remains text, and an
  initial newline in `textarea` is ignored.
- With `scriptingEnabled: true`, `noscript` content in `head` is treated as raw
  text. With it disabled, that content is parsed as normal markup.
- SVG and MathML elements use their foreign namespaces. Known SVG tag/attribute
  case is adjusted (`lineargradient` becomes `linearGradient`, for example),
  and `xlink:*`, `xml:*`, and `xmlns:*` attributes carry their namespace and
  prefix.
- U+0000 in ordinary parsed text produces an `unexpected-null-character`
  parse error and is omitted from the resulting text. Other Unicode text,
  including astral characters and emoji, is preserved.

`options.onParseError`, when provided, is called in tokenizer/parser processing
order with objects
containing a stable kebab-case `code` plus `startLine`, `startCol`,
`startOffset`, `endLine`, `endCol`, and `endOffset`. Supplying this callback
also enables location tracking. Error recovery still returns a document.

Example:

```js
import {parse} from 'parse5';

const document = parse('<!doctype html><title>A &amp; B</title><p>hello');
// document.mode === 'no-quirks'
// the title text is 'A & B'; html/head/body and the unclosed p are repaired
```

## `parseFragment(...)`

```ts
function parseFragment(html: string, options?: ParserOptions): DocumentFragment;
function parseFragment(
  context: Element | null,
  html: string,
  options?: ParserOptions,
): DocumentFragment;
```

Parse an HTML fragment. The one-string overload uses a forgiving template-like
HTML context. A supplied context controls tokenizer and insertion modes without
becoming part of the returned fragment. In particular, `table` context accepts
rows and creates `tbody`, `select` context discards elements invalid in a
select, and `textarea`/`script` contexts treat markup as text according to
RCDATA/raw-text rules. A foreign SVG context preserves SVG namespace parsing.
The parsing options and source-location behavior match `parse`.

## `serialize(node, options?)`

```ts
function serialize(node: ParentNode, options?: SerializerOptions): string;
```

Serialize the children of a document, fragment, or element. For an element,
the element's own start/end tags are not included. Text and attribute values
are escaped as required (`&` and non-breaking space in text; `&`, U+00A0, and
`"` in attributes). Text in HTML `script`, `style`, `xmp`, `iframe`, `noembed`,
`noframes`, and (when scripting is enabled) `noscript` is not escaped. HTML void
elements never receive closing tags. Templates serialize their `content`
children. Document types serialize as `<!DOCTYPE name>` and comments as
`<!--data-->`. `SerializerOptions.scriptingEnabled` defaults to `true`.

Canonical examples include:

```js
serialize(parse('<!doctype html><title>x</title><p>y'));
// '<!DOCTYPE html><html><head><title>x</title></head><body><p>y</p></body></html>'

serialize(parseFragment('<p>&amp;&nbsp;&lt;</p>'));
// '<p>&amp;&nbsp;&lt;</p>'

serialize(parseFragment('<br><img src=x><input disabled>'));
// '<br><img src="x"><input disabled="">'
```

## `serializeOuter(node, options?)`

```ts
function serializeOuter(node: Node, options?: SerializerOptions): string;
```

Serialize one node including its outer representation. Elements include their
own start/end tags (except HTML void elements), text is escaped in its parent
context, comments and doctypes use their HTML syntax, and attribute order is
preserved.

For example, serializing the outer form of the `div` parsed from
`<div class=x>Hello <b>world</b></div>` returns exactly
`<div class="x">Hello <b>world</b></div>`.

## Root compatibility exports

The ESM root must expose these runtime names with the indicated kinds:

- Functions: `parse`, `parseFragment`, `serialize`, `serializeOuter`.
- Classes/functions: `Parser`, `Tokenizer`.
- Objects: `defaultTreeAdapter`, `ErrorCodes`, `Token`, `TokenizerMode`,
  `foreignContent`, and `html`.

`defaultTreeAdapter` implements the documented default node construction,
mutation, traversal, type-guard, namespace, attribute, document-mode,
template-content, and source-location behavior used by the root APIs. For
package compatibility, it must expose function-valued properties named
`appendChild`, `createDocument`, `createDocumentFragment`, `createElement`,
`detachNode`, `getAttrList`, `getChildNodes`, `getDocumentMode`,
`getFirstChild`, `getNamespaceURI`, `getNodeSourceCodeLocation`,
`getParentNode`, `getTagName`, `insertBefore`, `isElementNode`,
`setDocumentMode`, `setNodeSourceCodeLocation`, `setTemplateContent`, and
`updateNodeSourceCodeLocation`. Direct calls to these adapter methods are not
part of the behavioral surface.

`html.NS` exposes the namespace constants above. At minimum, `ErrorCodes`
contains these exact entries:

```js
{
  missingDoctype: 'missing-doctype',
  duplicateAttribute: 'duplicate-attribute',
  unexpectedNullCharacter: 'unexpected-null-character',
}
```

`Parser` exposes static function-valued properties `parse` and
`getFragmentParser`. The low-level `Parser`, `Tokenizer`, `Token`,
`TokenizerMode`, `foreignContent`, and non-namespace `html` members are
compatibility exports; direct low-level construction or invocation is outside
this task's supported behavior.


- Input strings are interpreted as JavaScript UTF-16 strings. Offsets therefore
  count UTF-16 code units, while lines and columns are one-based.
- Serialization is canonical rather than source preserving: keyword casing,
  optional tags, inserted nodes, quoting, and malformed input may differ from
  the original source while representing the corrected tree.
- A custom tree adapter may be declared in TypeScript, but only the default tree
  adapter is exercised by this task.
- Preserve deterministic child and attribute ordering. Do not expose internal
  caches or mutable process-global parsing state.

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
npm ci --offline --ignore-scripts --no-audit --no-fund
```

### Example 2: ordinary usage
```text
HTML   http://www.w3.org/1999/xhtml
SVG    http://www.w3.org/2000/svg
MATHML http://www.w3.org/1998/Math/MathML
XLINK  http://www.w3.org/1999/xlink
XML    http://www.w3.org/XML/1998/namespace
XMLNS  http://www.w3.org/2000/xmlns/
```

### Example 3: boundary or error behavior
```text
function parse(html: string, options?: ParserOptions): Document;
```

### Example 4: boundary or error behavior
```text
import {parse} from 'parse5';

const document = parse('<!doctype html><title>A &amp; B</title><p>hello');
// document.mode === 'no-quirks'
// the title text is 'A & B'; html/head/body and the unclosed p are repaired
```


## Error Handling and Boundary Conditions

- Empty inputs, invalid types, malformed text or paths, unavailable resources, duplicate calls, and cancellation/timeout cases must follow the exception and return-value contracts documented for the relevant API.
- Do not silently coerce values, reorder results, swallow exceptions, or use a fallback dependency unless the API section explicitly requires that behavior.
- File and environment operations must use caller-provided paths and documented defaults only; never read undeclared host files or network resources.
- The implementation must remain usable in the stated NoNetwork environment. A missing optional integration should expose the documented availability or error behavior rather than attempting an online install.
- Security-sensitive inputs must be treated as data. Do not execute strings, load untrusted code, or interpolate shell commands unless that behavior is explicitly part of the documented public API.
