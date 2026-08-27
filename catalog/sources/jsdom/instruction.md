# Build `jsdom`

## Project Description

Create a complete installable npm package named `jsdom`. It implements a
deterministic in-memory subset of browser standards for Node.js: HTML/XML
parsing, DOM querying and mutation, serialization, URLs and origins, cookies,
web storage, events, forms, templates, DOM parsing, and inline CSS declarations.

Start from an empty workspace and write your own implementation. The evaluated
surface is local and deterministic. It does not fetch remote pages or
subresources, open a browser, use Canvas, access a database, or require an
external service.

## Supports

- Node.js `24.19.0`, npm `11.17.0`, Linux amd64/glibc.
- A CommonJS package importable with `require("jsdom")`. The package root must
  expose `JSDOM`, `VirtualConsole`, `CookieJar`, `requestInterceptor`, and
  `toughCookie` with the export shapes described below.
- A package named `jsdom`, a semantic version, a `package-lock.json` using
  `lockfileVersion: 3`, and all implementation files included by `npm pack`.
- Offline installation with `npm ci --offline --ignore-scripts`, followed by
  `npm pack --ignore-scripts`. Do not use lifecycle scripts, native addons,
  workspaces, git/file dependencies, registry overrides, custom loaders, or
  runtime downloads.
- The declared runtime dependency set may use the standard packages in the
  frozen jsdom runtime closure, including `parse5`, `tough-cookie`,
  `whatwg-url`, `whatwg-mimetype`, `saxes`, `css-tree`, and the related CSS and
  Web IDL helpers. No development-only dependency is required at runtime.

## API Usage Guide

### Root exports

```js
const {
  JSDOM,
  VirtualConsole,
  CookieJar,
  requestInterceptor,
  toughCookie
} = require("jsdom");
```

`JSDOM`, `VirtualConsole`, and `CookieJar` are constructors.
`requestInterceptor` is callable. `toughCookie` is the re-exported cookie
module object. `CookieJar` follows tough-cookie semantics and defaults to loose
cookie parsing suitable for web content.

### `new JSDOM(input = "", options = {})`

Construct a window and document from a string, byte input, or value coercible
to a string. HTML parsing inserts the normal `html`, `head`, and `body`
structure, handles a doctype, decodes entities, applies HTML tree-building
rules such as an implied `tbody`, and reaches `document.readyState ===
"complete"`. XML MIME types use XML parsing and serialization instead.

Supported options and their contracts:

- `url`: parsed and serialized as a WHATWG URL. The default is `about:blank`.
- `referrer`: parsed and normalized as a URL and exposed by
  `document.referrer`.
- `contentType`: accepts HTML or XML MIME types and sets
  `document.contentType`; other MIME types throw.
- `includeNodeLocations`: when true for HTML, `dom.nodeLocation(node)` returns
  parse source offsets and line/column data. Calling `nodeLocation()` without
  this option throws. It is incompatible with XML parsing.
- `runScripts`: omitted scripts are inert; `"dangerously"` executes inline
  scripts; `"outside-only"` installs fresh script-capable globals without
  executing inline script elements. No external script or resource loading is
  required.
- `storageQuota`: limits the combined key/value code-unit storage for
  `localStorage` and `sessionStorage`; exceeding it raises a quota error.
- `pretendToBeVisual`, `virtualConsole`, `cookieJar`, and `beforeParse` retain
  their documented local jsdom meanings. Callbacks are not part of the scored
  serialization boundary.

The instance exposes:

- `window`: the Window global proxy and its `document`, `location`, DOM
  constructors, events, storage, parser, and serializer APIs.
- `virtualConsole` and `cookieJar`: the configured instances.
- `serialize() -> string`: serializes the complete document, including the
  doctype when present, escaping text and attribute values correctly.
- `nodeLocation(node) -> object | null`: source location data when enabled.
- `getInternalVMContext()`: returns the context only for a script-enabled
  instance and otherwise throws.
- `reconfigure({ url?, windowTop? })`: changes the document URL/base URL or
  top reference without navigation. Reconfiguring the URL does not recreate
  the existing Window, so its original `window.origin` is retained.

### `JSDOM.fragment(markup = "")`

Return a `DocumentFragment` parsed in a shared HTML template context. Preserve
child order, decoded text, element markup, and HTML fragment parsing rules.

### Required DOM behavior

The created Window must provide standard, case-sensitive JavaScript DOM APIs:

- `querySelector()` and `querySelectorAll()` support tag, ID, class, attribute,
  descendant, and child-combinator selectors and return document order.
- Element identity and content properties include `tagName`, `id`,
  `className`, `textContent`, `innerHTML`, and `outerHTML`.
- Mutation supports attributes, `textContent`, element creation and append,
  removal, and `classList`; serialization reflects mutations and escapes
  inserted text.
- `CustomEvent` dispatch preserves event type, `detail`, and bubbling.
- HTML forms expose ordered `form.elements`, control names, string values, and
  checked state.
- Template element children live in `template.content`, not as direct template
  children, while `template.innerHTML` serializes the content.
- `DOMParser.parseFromString(source, type)` supports HTML and XML MIME types;
  malformed XML produces a document containing `parsererror`.
- Inline `style` declarations expose normalized property values, camel-cased
  properties such as `backgroundColor`, `cssText`, and `!important` priority.

Cookie handling is URL scoped. Assigning `document.cookie` updates the
instance cookie jar; normal same-origin cookies are visible through both, while
`HttpOnly` cookies are not exposed to script. Storage requires a non-opaque
origin and stores key/value inputs as strings.

## Implementation Notes

- Keep all evaluated work in memory. Fixed example domains are URL parser and
  origin inputs only; do not attempt network access.
- Preserve CommonJS root loading and package the generated/runtime source
  needed by the public entry point. The evaluator installs the packed tarball
  into an isolated prefix before invoking it.
- Candidate code runs in a bounded subprocess. Results and thrown errors must
  be deterministic and JSON-serializable at the evaluated boundary.
- You do not need to implement `JSDOM.fromURL()`, external subresource loading,
  XHR/fetch networking, `JSDOM.fromFile()`, Canvas, image decoding, WebSocket
  transport, full Web Platform Tests, or browser automation for this task.
