# Build `cookie`

## Project Description

Create an installable npm package named `cookie`, version `2.0.1`, from an
empty workspace. It parses and serializes HTTP `Cookie` and `Set-Cookie`
header values. The package is ESM and exposes four named functions from its
root entry point.

## Natural Language Instruction

Create the `cookie` ESM package from an empty `workspace/`. Implement the four
named root exports for parsing and serializing HTTP `Cookie` and `Set-Cookie`
headers. Preserve pair splitting, percent-decoding fallback, duplicate-key
handling, attribute order, validation errors, JSON-safe value boundaries, and
deterministic output. The package is synchronous, stateless, and independent of
network, time, browser globals, and filesystem state.

This task scores a deterministic JSON-compatible subset of the pinned public
API. It is a bounded rescope of the upstream project, not a claim of complete
upstream test or behavioral parity. Do not copy upstream source or tests into
the generated repository.

## Supports

- Run on Node `24.19.0` with npm `11.17.0` on `linux/amd64`.
- `package.json` must use `"type": "module"` and expose a safe in-package ESM
  root entry containing named exports `parseCookie`, `parseSetCookie`,
  `stringifyCookie`, and `stringifySetCookie`.
- Declare no runtime dependencies and no npm scripts. Include the runtime
  files selected by the root export and a v3 `package-lock.json` that agrees
  with `package.json`.
- A clean verifier must be able to run:

  ```bash
  npm ci --offline --ignore-scripts --no-audit --no-fund
  ```

- Do not use lifecycle hooks, workspaces, native addons, custom loaders,
  registry configuration, network access, browser globals, current time, or
  random state.

## Project Directory Structure

```text
workspace/
├── package.json
├── package-lock.json
├── index.js
└── index.d.ts
```

`index.js` is the ESM package root and exports `parseCookie`, `parseSetCookie`,
`stringifyCookie`, and `stringifySetCookie`; `index.d.ts` describes the public
signatures. The lockfile must agree with the package metadata and no tests,
verifier files, cache, or generated evaluator assets belong in the workspace.

## JSON Boundary

The verifier invokes candidate code only in a bounded child process. Each
request and response is one JSON object of at most 64 KiB and 256 KiB,
respectively. The fixed adapter accepts only an allowlisted operation name and
JSON data. It never transports or evaluates source text, callbacks, functions,
regular expressions, symbols, BigInts, executable strings, or cyclic objects.
Candidate code is never imported into the trusted test process.

The scored value domain is recursively composed of JSON null, booleans, finite
numbers, strings, arrays, and objects. Cookie maps in this task contain string
values only. `undefined` cookie values, custom `encode`/`decode` callbacks,
buffers, custom prototypes, and accessor properties are outside the scored
contract.

JavaScript `Date` values are also outside the boundary. Consequently:

- `parseSetCookie` requests containing a valid `Expires` attribute are outside
  the scored contract because the public API returns a `Date` for that field;
- `stringifySetCookie` input must omit `expires`; and
- the adapter rejects a `Date` result instead of silently converting it to an
  ISO string.

Missing optional object properties remain absent. Parser result objects are
projected by their own enumerable JSON-safe properties; prototype identity is
not observable through the response.

## API Usage Guide

### `parseCookie`

**Import and signature:**

```js
import {parseCookie} from 'cookie';
parseCookie(header)
```

The public module can also be loaded as `import * as cookie from 'cookie'`;
the four named exports are available on that namespace.
For tools that display import paths in language-neutral form, the root path is
`from cookie import parseCookie`; the executable JavaScript form is the ESM
named import shown above.

`header` is a string. Return an object whose own keys are cookie names and
whose values are strings.

- Split pairs at semicolons and each pair at its first equals sign.
- Trim spaces and horizontal tabs around names and values.
- Ignore fragments without an equals sign.
- Keep the first occurrence of a duplicate name.
- Decode values with `decodeURIComponent`; when decoding fails, preserve the
  original text.
- Accept empty names and values, and preserve keys such as `toString` and
  `valueOf` as ordinary own properties.
- Empty or too-short input returns an empty object.

Examples:

```js
parseCookie('foo=bar; email=%20%22%2C%3B%2F')
// {foo: 'bar', email: ' ",;/'}

parseCookie('foo=first; foo=second')
// {foo: 'first'}
```

### `stringifyCookie`

**Import and signature:**

```js
import {stringifyCookie} from 'cookie';
stringifyCookie(cookieMap)
```

`cookieMap` is an object whose own values are strings. Return a `Cookie` header
string. Visit keys in JavaScript `Object.keys` order and join pairs with
`; `. Empty objects return the empty string and empty values produce `name=`.

Names must contain printable ASCII characters other than `=` and whitespace.
Invalid names throw `TypeError` with a message containing
`cookie name is invalid`. Preserve the roundtrip-safe cookie-octet set and use
`encodeURIComponent` for other value characters, including spaces, percent,
comma, semicolon, backslash, double quote, and Unicode.

```js
stringifyCookie({foo: 'bar baz', empty: ''})
// 'foo=bar%20baz; empty='
```

### `parseSetCookie`

**Import and signature:**

```js
import {parseSetCookie} from 'cookie';
parseSetCookie(header)
```

Return an object with string `name` and `value` fields plus recognized optional
attributes. The JSON-safe scored attributes are:

- `maxAge`: an integer parsed only from complete signed decimal text;
- `domain` and `path`: trimmed strings;
- `httpOnly`, `secure`, and `partitioned`: `true` when the attribute appears,
  regardless of an attached value;
- `priority`: lowercase `low`, `medium`, or `high`; and
- `sameSite`: lowercase `lax`, `strict`, or `none`.

Attribute names are case-insensitive. Ignore unknown attributes, empty
attributes, invalid max-age text, invalid priority/same-site values, and an
invalid `Expires` date. Split the first name/value pair at its first equals
sign; when it has no equals sign, return an empty name and the full text as the
value. Percent-decode the cookie value with the same fallback as `parseCookie`.

```js
parseSetCookie('key=value; Max-Age=3600; HttpOnly; SameSite=Lax')
// {name: 'key', value: 'value', maxAge: 3600, httpOnly: true, sameSite: 'lax'}
```

### `stringifySetCookie`

**Import and signature:**

```js
import {stringifySetCookie} from 'cookie';
stringifySetCookie(cookie)
```

`cookie` is a JSON object with `name`, `value`, and optional JSON-safe
attributes. `name` is a string. `value` is a string or `null`; null produces an
empty value. Supported options are integer `maxAge`, string `domain`, string
`path`, booleans `httpOnly`/`secure`/`partitioned`, `priority`, and `sameSite`.

Output attributes in this order when present:
`Max-Age`, `Domain`, `Path`, `HttpOnly`, `Secure`, `Partitioned`, `Priority`,
`SameSite`. Normalize priority and same-site capitalization as shown below.
A boolean `true` same-site value means `Strict`.

```js
stringifySetCookie({
  name: 'key',
  value: 'value',
  maxAge: 3600,
  httpOnly: true,
  secure: true,
  sameSite: 'lax'
})
// 'key=value; Max-Age=3600; HttpOnly; Secure; SameSite=Lax'
```

Reject invalid names, domains, paths, non-integer max ages, priorities, and
same-site values with `TypeError`. Error messages must identify the invalid
field using the forms `argument name is invalid`, `option domain is invalid`,
`option path is invalid`, `option maxAge is invalid`,
`option priority is invalid`, or `option sameSite is invalid`.

## Implementation Notes

Preserve deterministic byte-for-byte output and ordinary ESM package loading.
The frozen verifier has 32 `node:test` leaves derived from JSON-safe cases in
the pinned Vitest suite. It does not run Vitest, benchmark data, snapshots,
size checks, TypeScript build tooling, callback cases, generated Unicode
exhaustive tables, or valid-Date cases. Those omissions define the public task
boundary and must not be interpreted as upstream parity.
