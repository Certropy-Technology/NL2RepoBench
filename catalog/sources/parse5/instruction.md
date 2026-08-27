# Project Description

Build `parse5`, an offline ECMAScript module that parses HTML documents and
fragments into a default tree representation and serializes that representation
back to HTML. The package targets standards-oriented server-side HTML tooling:
it must perform HTML tree correction, preserve HTML/SVG/MathML namespaces, and
offer deterministic source-location and parse-error reporting.

This task covers the package-root document/fragment APIs and the default tree
adapter. The root compatibility exports listed below must exist, but direct use
of the low-level tokenizer/parser constructors and custom tree adapters is not
part of the behavioral surface.

# Supports

- Node.js `24.19.0`, npm `11.17.0`, `linux/amd64`, and ESM package semantics.
- `package.json` must name the package `parse5`, use version `8.0.1`, set
  `"type": "module"`, and export the package root to a JavaScript ESM entry.
  It must also identify a TypeScript declaration entry.
- Commit a lockfile with `lockfileVersion: 3`. A clean verifier runs:

  ```bash
  npm ci --offline --ignore-scripts --no-audit --no-fund
  ```

- You may implement the package without dependencies. If you use the
  reference-compatible escaping/entity helper, the only available runtime
  dependency is exact `entities@8.0.0`; no other runtime package is available.
- Do not use npm workspaces, native addons, custom loaders, registry settings,
  generated downloads, or lifecycle scripts (`preinstall`, `install`,
  `postinstall`, `prepare`, `prepublish`, `prepublishOnly`, `publish`, or
  `postpublish`). The package has no CLI.
- Runtime execution is deterministic and offline. Parsing and serialization
  must not read files or environment-dependent state, use the clock or
  randomness, start subprocesses, or access the network.

# API Usage Guide

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

# Implementation Notes

- Input strings are interpreted as JavaScript UTF-16 strings. Offsets therefore
  count UTF-16 code units, while lines and columns are one-based.
- Serialization is canonical rather than source preserving: keyword casing,
  optional tags, inserted nodes, quoting, and malformed input may differ from
  the original source while representing the corrected tree.
- A custom tree adapter may be declared in TypeScript, but only the default tree
  adapter is exercised by this task.
- Preserve deterministic child and attribute ordering. Do not expose internal
  caches or mutable process-global parsing state.
