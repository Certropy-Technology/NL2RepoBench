# Build `cross-fetch`

## Project Description

Create a complete installable npm package named `cross-fetch`, version `4.1.0`,
from an empty workspace. It is a CommonJS WHATWG Fetch API ponyfill for Node.
The package root exports a callable `fetch` function and the `Headers`,
`Request`, and `Response` constructors. Implement this behavior with your own
source files; do not retrieve a reference repository or hidden tests.

## Supports

- Node `24.19.0`, npm `11.17.0`, Linux amd64 with glibc, and CommonJS package
  semantics.
- `package.json` must set `name` to `cross-fetch`, `version` to `4.1.0`, and
  `main` to `dist/node-ponyfill.js`.
- The package root must be usable as `const fetch = require('cross-fetch')`.
  Its `fetch` and `default` properties reference that same callable value and
  `fetch.ponyfill` is `true`.
- Commit an npm v3 lockfile. Installation and packing are performed offline
  with lifecycle scripts disabled:

  ```text
  npm ci --offline --ignore-scripts --no-audit --no-fund
  npm pack --ignore-scripts
  ```

- The only available direct runtime dependency is `node-fetch@2.7.0`; its
  exact transitive closure is present in the offline cache. Do not use git,
  file, workspace, native-addon, or network dependencies. Do not add
  `preinstall`, `install`, `postinstall`, `prepare`, or other lifecycle hooks.
- The scored contract is local and deterministic. Calls to a verifier-owned
  loopback HTTP server are covered. Public HTTP, browser globals, React Native,
  service workers, proxy agents, streaming uploads, redirects, and TLS are not
  covered.

## API Usage Guide

### Package exports

```js
const fetch = require('cross-fetch');
const {Headers, Request, Response} = fetch;
```

The root export is a callable fetch implementation. It also exposes
`fetch`, `default`, `Headers`, `Request`, and `Response`. The callable,
`fetch`, and `default` are the identical function value. `Headers`, `Request`,
and `Response` are constructable WHATWG-compatible classes.

### `Headers`

`new Headers(init?)` accepts a plain object, iterable pairs, or another
Headers object. Header names are case-insensitive. `append(name, value)` adds a
value, `set(name, value)` replaces it, `get(name)` returns the combined string
or `null`, `has(name)` reports membership, and `entries()` is iterable. Values
are strings and names in iterated output are normalized to lower case.

### `Request`

`new Request(input, init?)` creates an outbound request. `input` may be an
absolute URL or another Request. The relevant initializer fields are `method`,
`headers`, and `body`. A Request exposes `url`, `method`, and `headers`, and
`clone()` returns an independent body reader. `text()` resolves to the request
body as a string. Methods are normalized to upper case.

### `Response`

`new Response(body?, init?)` creates an inbound response. The initializer
accepts `status`, `statusText`, and `headers`. A Response exposes `status`,
`statusText`, `ok`, `redirected`, `type`, `url`, and `headers`. `text()`
resolves to its string body, and `clone()` permits independent body reads.
`ok` is true for status values from 200 through 299 inclusive.

### `fetch(url, options?)`

`fetch(url, options?)` returns a Promise for a Response. `url` accepts an
absolute URL. `options` supports `method`, `headers`, and `body` as described
for Request. The result preserves status, status text, response headers, and
response body. Invalid URLs reject the Promise with an Error. The task tests a
verifier-local `http://127.0.0.1` server only; do not hard-code that server's
address or response.

## Implementation Notes

- Keep `dist/node-ponyfill.js` as the package entry and retain CommonJS
  `require('cross-fetch')` behavior.
- Preserve constructor and body semantics by using the available dependency or
  a compatible local implementation. Do not substitute Node's process-global
  fetch API when it changes the documented export identity or class behavior.
- Make the package reproducible from a clean checkout under the offline npm
  commands. The verifier runs candidate code in an unprivileged child process
  and does not import it into its trusted process.
