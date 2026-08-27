# Build `node-fetch`

## Project Description

Create an installable ESM npm package named `node-fetch`, version `3.1.1`.
It provides a deterministic, JSON-safe subset of the Fetch API suitable for
constructing headers, requests, and responses in Node.js. The package must
export a default `fetch` function plus named `Headers`, `Request`, `Response`,
and `isRedirect` exports from its root entry point.

This task deliberately excludes live `http:` and `https:` traffic. The default
function is evaluated only with `data:` URLs, so the required behavior is
deterministic and works with no network access. This is a bounded task contract,
not a claim of full upstream compatibility.

## Supports

- Node `24.19.0`, npm `11.17.0`, and `linux/amd64`.
- ESM packaging: `package.json` must set `"type": "module"` and provide a
  safe root ESM entry point.
- Declare exactly these runtime dependencies with the exact versions
  `data-uri-to-buffer@4.0.1`, `fetch-blob@3.2.0`, and
  `formdata-polyfill@4.0.10`. Do not declare npm lifecycle hooks, workspaces,
  native addons, registry configuration, custom loaders, browser globals,
  clock-dependent behavior, or random behavior.
- Include a root-only npm lockfile using lockfile version `3` that agrees with
  `package.json`. A clean verifier runs `npm ci --offline --ignore-scripts
  --no-audit --no-fund` before packaging the candidate.

The verifier calls the package from a separate unprivileged Node process. Its
request and response payloads are JSON objects limited to 64 KiB and 256 KiB.
The scored values are JSON strings, null, booleans, finite numbers, arrays, and
plain objects. Functions, streams, buffers, typed arrays, dates, custom
prototypes, symbols, bigints, cyclic values, and callbacks are out of scope.

## API Usage Guide

### `Headers`

```js
import {Headers} from 'node-fetch';
const headers = new Headers(init);
```

`init` is omitted, a plain object of header values, or an array of two-item
`[name, value]` arrays. Header names are case-insensitive; stored names are
lowercase. Names and values must be valid HTTP header names and values.
Invalid names or values throw `TypeError`.

Implement `append(name, value)`, `set(name, value)`, `delete(name)`,
`get(name)`, `getAll(name)`, `has(name)`, `entries()`, `keys()`, `values()`,
the default iterator, and the node-fetch extension `raw()`.

- `append` retains multiple values for a name.
- `set` replaces all prior values for that name.
- `get` returns `null` for a missing name; otherwise it joins values with
  `, `.
- `getAll` returns an array, including an empty array for a missing name.
- Iteration is sorted lexicographically by normalized name. Entries contain
  one joined value per name.
- `raw()` returns a plain object mapping each normalized name to its individual
  string values.

```js
const headers = new Headers([['B', '2'], ['a', '1'], ['b', '3']]);
Array.from(headers.entries()); // [['a', '1'], ['b', '2, 3']]
headers.raw(); // {a: ['1'], b: ['2', '3']}
```

### `Request`

```js
import {Request} from 'node-fetch';
const request = new Request(input, init);
```

`input` is an absolute URL string and `init` is an optional JSON-safe object.
Expose `url`, `method`, `headers`, `redirect`, `referrer`, and
`referrerPolicy`, as well as `clone()`.

- The default method is `GET`; standard methods `DELETE`, `GET`, `HEAD`,
  `OPTIONS`, `POST`, and `PUT` are normalized to uppercase. Other methods keep
  their supplied spelling.
- The default redirect policy is `follow`.
- A `GET` or `HEAD` request with a non-null body throws `TypeError`.
- URLs with embedded user credentials throw `TypeError`.
- A string body with no supplied content type adds
  `content-type: text/plain;charset=UTF-8`.
- An empty `referrer` is exposed as the empty string. An omitted referrer is
  absent from the JSON-safe request snapshot.

### `Response`

```js
import {Response} from 'node-fetch';
const response = new Response(body, init);
```

For this task, `body` is `null` or a string. `init` may contain JSON-safe
`headers`, `status`, and `statusText` fields. Implement `text()`, `json()`,
`arrayBuffer()`, `clone()`, and the static methods `Response.error()`,
`Response.redirect(url, status)`, and `Response.json(data, init)`.

- The default status is `200`; `ok` is true exactly for statuses 200 through
  299 inclusive.
- `text()` removes a leading UTF-8 BOM. `json()` parses the same decoded text.
  Reading a body marks `bodyUsed` true; a second body read rejects.
- `arrayBuffer()` yields the UTF-8 bytes of the original body, including a BOM.
- `clone()` permits independently reading the original and clone before either
  has been consumed.
- `Response.json` serializes JSON data and adds `content-type:
  application/json` unless a content type is supplied.
- `Response.error()` has type `error`, status `0`, and an empty status text.
- `Response.redirect` accepts only 301, 302, 303, 307, or 308; other statuses
  throw `RangeError`. A valid redirect has a normalized `location` header.

### Default `fetch`

```js
import fetch from 'node-fetch';
const response = await fetch(url, init);
```

The only required URL scheme is `data:`. Decode percent-encoded and base64 data
URLs into a `Response`; preserve the media type as its `content-type` header.
Unsupported schemes, including `http:` and `https:`, reject with `TypeError`.
No request may contact a network host.

### `isRedirect`

```js
import {isRedirect} from 'node-fetch';
```

Return true only for status codes 301, 302, 303, 307, and 308.

## Implementation Notes

The package must be deterministic and normal npm package loading must work
without network access. The frozen verifier contains 23 `node:test` leaves for
the JSON-safe contract above. It does not evaluate live networking, redirects
over sockets, compression, streams, form data, blobs, abort signals, proxy or
agent options, filesystem helpers, custom header iterables, or TypeScript-only
behavior.
