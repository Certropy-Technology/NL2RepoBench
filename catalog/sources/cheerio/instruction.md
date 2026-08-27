# Build `cheerio`

## Project Description

Create a complete, installable npm package named `cheerio`, version `1.2.0`,
from an empty workspace. It is a server-side HTML and XML parser with a
jQuery-like selector, traversal, attribute, manipulation, and form API.

The scored contract is the deterministic local, JSON-expressible part of the
package. Callers load a markup string, select elements with CSS selectors,
inspect or mutate the in-memory document, and serialize values back to strings
or JSON. The package must not contact a network, inspect unrelated files, or
depend on browser globals.

## Supports

- Run on Node.js `24.19.0` with npm `11.17.0` on `linux/amd64`.
- `package.json` must declare `"name": "cheerio"`, `"version": "1.2.0"`,
  `"type": "module"`, and expose the package root, `cheerio/slim`,
  `cheerio/utils`, and `cheerio/package.json`.
- The root and `cheerio/slim` entry points must expose a callable named export
  `load`. Both ESM import and CommonJS require consumers must resolve the root
  package. `cheerio/utils` must expose `camelCase`, `cssCase`, and `isHtml`.
- Commit a lockfile with `lockfileVersion: 3` matching `package.json`. A clean
  verifier installs and packs the candidate with:

  ```bash
  npm ci --offline --ignore-scripts --no-audit --no-fund
  npm pack --ignore-scripts
  ```

- Runtime JavaScript and declarations must already exist in the package. Do
  not rely on an install, prepare, prepack, publish, or other lifecycle hook to
  compile or download files. Do not declare development dependencies,
  workspaces, loaders, native addons, registry configuration, or executable
  install scripts.
- A self-contained implementation is valid. If dependencies are used, they
  must be a subset of this scripts-free offline allowlist at the exact shown
  versions: `cheerio-select@2.1.0`, `dom-serializer@2.0.0`,
  `domhandler@5.0.3`, `domutils@4.0.2`, `encoding-sniffer@0.2.1`,
  `htmlparser2@10.1.0`, `parse5@7.3.0`,
  `parse5-htmlparser2-tree-adapter@7.1.0`,
  `parse5-parser-stream@7.1.2`, `undici@8.10.0`, and
  `whatwg-mimetype@5.0.0`. Node built-ins are not dependencies.
- Runtime network access is unavailable. `fromURL` is outside this task even
  if the package chooses to expose it. The scored path never opens a socket.
- The JSON subprocess boundary supplies strings, booleans, finite numbers,
  null, arrays, and plain objects. It does not pass JavaScript callbacks,
  functions, symbols, class instances, DOM nodes, cyclic values, executable
  source, or shared object identity.

The following root APIs are outside the scored contract and need not be
implemented: `fromURL`, `loadBuffer`, `stringStream`, `decodeStream`,
`contains`, and `merge`. Buffer decoding, Node streams, live HTTP requests,
custom parser callbacks, plugin extension, browser bundles, source maps, and
the upstream build/lint/test toolchain are also outside the contract.

## API Usage Guide

### `load(content, options?, isDocument?) => CheerioAPI`

Import path: named `load` from `cheerio` or `cheerio/slim`.

`content` is a markup string. `options` is omitted, `null`, or a plain object.
`isDocument` defaults to `true`.

- In HTML document mode, parse with browser-like HTML tree construction. The
  serialized document contains `html`, `head`, and `body` wrappers as needed.
  A title is placed in `head`; ordinary content is placed in `body`; table
  structure is corrected, including insertion of `tbody` around rows.
- With `isDocument === false`, parse a fragment and preserve adjacent
  top-level text, comments, and elements without document wrappers.
- Empty HTML document input serializes as
  `<html><head></head><body></body></html>`.
- Named HTML entities and numeric references are decoded in text and escaped
  again when markup is serialized. Unicode text is preserved.
- HTML tag and attribute names follow HTML casing rules. For example,
  `prop("tagName")` of an `article` element is `"ARTICLE"`.
- With `{ xmlMode: true }`, use XML parsing and serialization: tag and
  attribute case is preserved and empty elements use self-closing syntax.
- A null or undefined `content` is invalid and raises an ordinary `Error`.

The returned `CheerioAPI` is a callable selector bound to the loaded document:

```js
import { load } from "cheerio";

const $ = load('<ul id="items"><li class="first">A</li><li>B</li></ul>');
$("#items > li").length;       // 2
$("li.first").text();          // "A"
$.html();                       // the complete serialized document
```

Calling `$()` with no selector returns an empty selection. A CSS selector
searches the bound document and returns a `Cheerio` selection in document
order. Passing a markup string creates a detached selection. Selector context
arguments may follow the ordinary Cheerio/jQuery calling shape.

### CSS selectors

Selectors support tags, `#id`, `.class`, selector groups, descendant and child
combinators, adjacent/general siblings, attribute existence and value
operators, and standard structural/content pseudos supported by Cheerio's CSS
selector surface. This includes `:first`, `:last`, `:first-child`,
`:last-child`, `:nth-child(...)`, `:not(...)`, `:has(...)`, and
`:contains("text")`.

Results are de-duplicated and returned in document order. Invalid selector
syntax raises an ordinary selector error; it must not silently become an empty
selection.

### Selection shape

A selection is array-like and iterable. It exposes numeric entries and a
`length` property. Unless noted otherwise, mutating and traversal methods
return a selection and are chainable. Getter methods use the first matched
element; an empty selection has length zero, `html()` returns `null`, and
attribute/value getters return `undefined` where the ordinary API does.

The following order methods are required:

```text
first()               first element or an empty selection
last()                last element or an empty selection
eq(index)             one element; negative indexes count from the end
slice(start, end?)     normal array-style slice of the selection
get(index?)            one raw node, or all nodes as an array
toArray()              all raw nodes as a new array
index()                first node's zero-based position among siblings
end()                  the previous selection in a traversal chain
addBack(selector?)     current selection plus the prior selection
clone()                deep copy of the selected nodes
```

An index outside the selection, including an overly negative index, returns an
empty selection.

### Traversal

All optional traversal filters below are CSS selector strings:

```text
find(selector)                  matching descendants
parent(selector?)               each direct non-document parent
parents(selector?)              all ancestors, nearest first
parentsUntil(stop?, filter?)    ancestors before the stop match
closest(selector)               nearest matching element including self
next(selector?)                 next element sibling
nextAll(selector?)              all following element siblings
nextUntil(stop?, filter?)       following siblings before the stop match
prev(selector?)                 previous element sibling
prevAll(selector?)              all preceding element siblings
prevUntil(stop?, filter?)       preceding siblings before the stop match
siblings(selector?)             all other element siblings
children(selector?)             direct element children only
contents()                      all direct children, including text/comments
filter(selector)                keep matches
not(selector)                   remove matches
is(selector)                    whether any selected element matches
has(selector)                   keep elements containing a matching descendant
```

Traversal across multiple starting elements removes duplicate nodes while
preserving the API's deterministic document order. `find()` searches
descendants, not the starting nodes themselves. `children()` excludes text and
comments; `contents()` includes them.

### Text and markup

```js
selection.text()              // concatenated descendant text of all matches
selection.text(value)         // replace contents with one escaped text node
selection.html()              // inner markup of the first match, or null
selection.html(value)         // parse and replace each match's contents
selection.toString()          // serialized outer markup of all matches
selection.prop("outerHTML")  // serialized first element
selection.prop("innerHTML")  // first element's inner markup
selection.prop("textContent")
selection.prop("innerText")
```

Text extraction includes script and style text for `text()`/`textContent`.
Setting text treats `<` and `>` as data and therefore serializes them escaped.

The document helpers are:

```js
$.html()              // complete HTML serialization
$.xml()               // complete XML serialization
$.text()              // complete document text
$.root()              // selection wrapping the document root
```

Document serialization preserves comments and emits an HTML doctype as
`<!DOCTYPE html>`.

### Attributes, properties, classes, CSS, and values

#### Attributes

```js
selection.attr(name)               // string or undefined
selection.attr()                   // copy of first element's attribute map
selection.attr(name, value)        // set on every element
selection.attr({ name: value })    // set multiple values
selection.removeAttr(names)        // remove whitespace-separated names
```

Attribute values are strings. A `null` setter removes that attribute. Callback
setters are outside the scored boundary.

#### Properties

`prop(name)` reads DOM properties or reflected attributes. Required special
properties include `tagName`, `outerHTML`, `innerHTML`, `textContent`,
`innerText`, and boolean properties such as `checked`, `selected`, `disabled`,
and `multiple`. HTML boolean properties are true when the attribute is present
and false when absent.

#### Classes

```text
hasClass(name)               boolean
addClass(names)              add whitespace-separated tokens
removeClass(names?)          remove tokens, or all classes when omitted
toggleClass(names, state?)   toggle tokens or force with a boolean state
```

Duplicate class tokens are not introduced. Empty class values follow normal
Cheerio serialization.

#### CSS

```js
selection.css(name)                // first inline property or undefined
selection.css([name1, name2])      // property map
selection.css(name, value)         // set on all matches
selection.css({ name: value })     // set multiple properties
```

Inline declarations are parsed case-insensitively using CSS property names.
Setting a value updates the property while preserving other declarations.
Callback CSS setters are outside the boundary.

#### Form values

`val()` reads the first selected input/button/option `value`, textarea text, or
the selected option of a select. A multiple select returns selected option
**text** in option order in this contract. `val(string)` sets scalar controls;
`val(string[])` on a multiple select clears previous selections and marks
options whose `value` is in the array.

### DOM manipulation

All markup arguments below are parsed as local HTML strings. For multiple
targets the content is cloned as required so every target receives content.

```text
append(content)       add content at the end of each element
prepend(content)      add content at the beginning
before(content)       insert siblings before each match
after(content)        insert siblings after each match
remove(selector?)     detach matches from their parents
empty()               remove all child nodes
wrap(content)         wrap each match separately
wrapInner(content)    wrap each match's existing contents
unwrap(selector?)     remove each matched parent while retaining its children
```

`html(value)` and `text(value)` are the replacement operations described
above. String callback overloads and arguments containing DOM instances are
outside the scored JSON boundary.

### Forms

`serializeArray()` returns successful form controls in document order as
plain objects `{ name: string, value: string }`. Disabled controls, controls
without a name, submit/button/file/reset controls, and unchecked radio or
checkbox controls are excluded. Newlines follow standard form normalization.

`serialize()` URL-encodes `serializeArray()` as an ampersand-separated query
string. Spaces are encoded as `+`.

### Extraction

`$.extract(map)` and `selection.extract(map)` map selectors to JSON-compatible
values. A string descriptor returns matched text. A descriptor
`{ selector, value }` selects an element and reads either text or a named
property/attribute. A one-element descriptor array returns an array for every
match in document order. Nested plain maps recursively build objects. Function
descriptors are outside the contract.

Example:

```js
const $ = load('<h1>Docs</h1><a href="/a">A</a><a href="/b">B</a>');
$.extract({
  title: "h1",
  links: [{ selector: "a", value: "href" }],
});
// { title: "Docs", links: ["/a", "/b"] }
```

### Utilities

Import from `cheerio/utils`:

```js
camelCase(name)  // CSS kebab-case to JavaScript camelCase
cssCase(name)    // JavaScript camelCase to CSS kebab-case
isHtml(value)    // true when the string has an HTML tag-like shape
```

`camelCase("border-top-left-radius")` is `"borderTopLeftRadius"`.
`cssCase("WebkitLineClamp")` is `"-webkit-line-clamp"`.
`isHtml("<div>x</div>")` is true while `isHtml("div.item")` is false.

## Implementation Notes

- Preserve deterministic document/selection order; do not sort selector or
  traversal results alphabetically.
- Parsing, selection, mutation, serialization, forms, and extraction must be
  local and synchronous after `load` returns.
- Do not expose candidate-written score, report, or test files. The verifier
  owns collection and scoring in a separate no-network environment.
- The task does not require exact internal classes, helper names, source layout,
  parser algorithm, build tooling, source maps, or upstream tests. Observable
  behavior and package import/install shape are the contract.
- File input, URL input, buffers, streams, callbacks, custom pseudo functions,
  custom adapters, and shared DOM identity cannot cross the scorer boundary and
  are deliberately excluded rather than silently approximated.
