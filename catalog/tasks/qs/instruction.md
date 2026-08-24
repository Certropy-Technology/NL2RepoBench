# Build `qs`

## Project Description

Build an installable npm package named `qs`, version `6.15.3`, that parses
URL/query-string text into nested JSON-compatible values and serializes
JSON-compatible values back to query-string text. The package is a CommonJS
library intended for server-side use. The scored contract is a deterministic,
JSON-compatible subset of the pinned upstream API; it deliberately excludes
JavaScript-only callbacks and values that cannot cross a bounded JSON
subprocess boundary.

The implementation must be created from an empty workspace. Do not copy the
upstream source or tests into the generated repository.

## Supports

- Run on Node `24.19.0` with npm `11.17.0` on `linux/amd64`.
- The package root must be loadable with CommonJS:

  ```js
  const qs = require("qs");
  ```

  It must expose callable `qs.parse` and `qs.stringify` functions. The root
  `qs.formats` object must expose the string constants `default` (`"RFC3986"`),
  `RFC1738`, and `RFC3986`; callback-valued formatter internals are outside the
  scored JSON contract.
- Include a v3 `package-lock.json` that agrees with `package.json`. A clean
  verifier environment must support:

  ```bash
  npm ci --offline --ignore-scripts --no-audit --no-fund
  ```

  The lock/cache closure must be content-addressed and reviewed before a
  production task is built. The two upstream runtime dependency roots are
  `es-define-property` and `side-channel`; do not add unreviewed runtime
  packages.
- Do not require a registry, network service, current time, random state,
  browser globals, native addons, workspaces, custom loaders, or lifecycle
  scripts. The verifier will disable lifecycle scripts and will not run the
  upstream `posttest` audit command.
- The browser bundle (`dist/qs.js`), Bower/component metadata, README checker,
  lint command, publish hooks, and CLI-like build/publish workflow are outside
  the scored API. The package's CommonJS library entry must work without
  building the browser bundle.
- All scored requests and responses must be representable as one JSON value.
  Object key order in a request is significant to `stringify` in the same way
  JavaScript own-key enumeration is significant; the contract does not promise
  canonical key sorting.

## API Usage Guide

### `parse`

**Import path:** `qs.parse` from the package root.

**Signature:**

```js
qs.parse(input, options?)
```

**Input:** `input` is a query-string `string`. `null` is accepted as an empty
query and produces an empty object. `undefined`, buffers, regular expressions,
functions, and other non-JSON values are outside the scored contract.
`options`, when present, is a JSON object containing only the JSON-compatible
fields listed below. A decoder callback is not part of this contract.

**Return:** a JSON-compatible object, array, string, or `null` value as
produced by the parser. Numeric-looking property names remain object keys;
query values remain strings by default; text such as `"15"`, `"true"`, and `"null"` is not automatically
converted to a number, boolean, or null. The result must not contain functions,
regular expressions, buffers, symbols, BigInts, dates, or cyclic references.

**Default behavior:**

- Split parameters on `&`, decode percent-encoded text, and translate `+` to a
  space. Malformed percent escapes are retained rather than causing an
  incidental crash.
- Parse bracket notation up to depth `5`. When the depth is exceeded and
  `strictDepth` is false, the remaining bracket text is retained as a literal
  key segment.
- Parse numeric array indexes below `arrayLimit` (`20`) as arrays and compact
  sparse indexes by default. An index at or above the limit is represented as
  an object key rather than allocating a huge sparse array.
- Combine repeated keys into an array. Empty values are strings by default;
  a parameter with no `=` is also an empty string unless
  `strictNullHandling` is enabled.
- Ignore keys that would overwrite the ordinary object prototype unless the
  relevant prototype option is explicitly enabled. The implementation must
  not mutate global prototypes.
- Preserve the order of repeated parameters and array members.

**JSON-compatible options:**

| Option | Type and default | Contract |
| --- | --- | --- |
| `allowDots` | boolean, `false` | Treat dots in keys as nested separators. |
| `allowEmptyArrays` | boolean, `false` | Parse `name[]` without a value as an empty array instead of an array containing an empty string. |
| `allowPrototypes` | boolean, `false` | Permit own keys that match ordinary object prototype names. This must not mutate a global prototype. |
| `allowSparse` | boolean, `false` | `true` is outside the JSON response contract because JSON cannot preserve array holes; keep it omitted or `false`. |
| `arrayLimit` | finite number, `20` | Numeric index/array representation threshold. Values at or above the threshold become object keys unless `throwOnLimitExceeded` is enabled. |
| `charset` | `"utf-8"` or `"iso-8859-1"`, default `"utf-8"` | Select percent-decoding behavior. Returned text is still JSON text. |
| `charsetSentinel` | boolean, `false` | Detect the encoded UTF-8/ISO-8859-1 sentinel and omit it from the result. |
| `comma` | boolean, `false` | Split comma-separated flat values into arrays. |
| `decodeDotInKeys` | boolean, `false` | Decode `%2E` in keys; enabling it also enables dot notation. |
| `delimiter` | string, `"&"` | Use a string delimiter. RegExp delimiters are outside the JSON contract. |
| `depth` | finite number or `false`, `5` | Limit nested bracket parsing. `false` has the upstream depth-zero behavior. |
| `duplicates` | `"combine"`, `"first"`, or `"last"`; default `"combine"` | Select repeated-key behavior. Bracket-array notation still combines. |
| `ignoreQueryPrefix` | boolean, `false` | Ignore one leading `?`. |
| `interpretNumericEntities` | boolean, `false` | Decode numeric HTML entities when the effective charset is ISO-8859-1. |
| `parameterLimit` | finite number, `1000` | Maximum number of delimited parameters examined. |
| `parseArrays` | boolean, `true` | When `false`, bracket-array syntax is represented with numeric object keys. |
| `plainObjects` | boolean, `false` | Use null-prototype result objects. Prototype identity is not observable through the JSON response; key/value behavior remains required. |
| `strictDepth` | boolean, `false` | Throw when the depth limit is exceeded instead of retaining the remainder literally. |
| `strictMerge` | boolean, `true` | When primitive and object forms conflict, combine them in an array when true; use legacy key merging when false. |
| `strictNullHandling` | boolean, `false` | Represent parameters without `=` as `null` instead of `""`. |
| `throwOnLimitExceeded` | boolean, `false` | Throw a `RangeError` instead of truncating parameters or switching array representation when a configured limit is exceeded. |

All numeric limits must be finite JSON numbers. `Infinity` and `NaN` are outside
the JSON contract. A JSON request may carry `-0`, but query-string conversion
uses the upstream JavaScript numeric/string rules (including `"0"` when a
negative zero is stringified); callers must not rely on preserving negative-zero
identity through the result.

**Examples:**

```js
qs.parse("a[b][0]=x&a[b][1]=y");
// { a: { b: ["x", "y"] } }

qs.parse("foo=bar&foo=baz", { duplicates: "last" });
// { foo: "baz" }

qs.parse("a[1]=x", { arrayLimit: 1 });
// { a: { "1": "x" } }

qs.parse("name%252Eobj.first=John", {
  allowDots: true,
  decodeDotInKeys: true
});
// { "name.obj": { first: "John" } }
```

### `stringify`

**Import path:** `qs.stringify` from the package root.

**Signature:**

```js
qs.stringify(value, options?)
```

**Input:** `value` is recursively composed of JSON `null`, booleans, finite
numbers, strings, arrays, and plain objects. Array holes, `undefined`,
non-finite numbers, symbols, BigInts, buffers, dates, regular expressions,
functions, custom prototypes, custom `toJSON` methods, and cycles are outside
the scored contract. `options`, when present, is a JSON object. Encoder,
filter-callback, date-serializer, formatter-callback, and sort-callback
options are outside the contract; an array-valued `filter` is supported.

**Return:** a deterministic query-string `string`. For a top-level primitive or
`null`, the upstream behavior is the empty string. For objects, own keys are
visited in JavaScript `Object.keys` order unless an array-valued `filter`
selects the keys. Array order is preserved. The same JSON value and options
must produce byte-for-byte identical output across calls and processes; no
promise of lexicographic object-key sorting is made.

**Default behavior:**

- Encode keys and values using RFC 3986 percent encoding.
- Use `&` as the delimiter, omit a leading `?`, use bracketed numeric array
  indexes (`arrayFormat: "indices"`), and serialize null as an empty value.
- Preserve empty strings, booleans, and finite numbers using their ordinary
  string forms. Omit `undefined` values (which are outside the input domain).
- Serialize nested objects with bracket notation and permit arbitrary nesting
  unless the JSON option `depth` supplies a finite bound.

**JSON-compatible options:**

| Option | Type and default | Contract |
| --- | --- | --- |
| `addQueryPrefix` | boolean, `false` | Prefix a non-empty result with `?`. |
| `allowDots` | boolean, `false` | Use dot separators for nested object keys. |
| `allowEmptyArrays` | boolean, `false` | Emit an empty array as `key[]` instead of omitting it. |
| `arrayFormat` | `"indices"`, `"brackets"`, `"comma"`, or `"repeat"`; default `"indices"` | Select array notation. |
| `charset` | `"utf-8"` or `"iso-8859-1"`, default `"utf-8"` | Select percent-encoding behavior. |
| `charsetSentinel` | boolean, `false` | Prefix the encoded charset sentinel. |
| `commaRoundTrip` | boolean, `false` | Preserve a one-element array when `arrayFormat` is `"comma"`. |
| `delimiter` | string, `"&"` | Join fields with a string delimiter. |
| `depth` | finite number or omitted (upstream default is unbounded) | Throw a `RangeError` when recursive input exceeds the bound. |
| `encode` | boolean, `true` | Enable or disable built-in percent encoding. |
| `encodeDotInKeys` | boolean, `false` | Percent-encode literal dots in keys; this also implies dot notation when `allowDots` is omitted. |
| `encodeValuesOnly` | boolean, `false` | Leave key syntax unencoded while encoding values. |
| `filter` | array of string keys or omitted | Select an explicit key order/subset. Callback filters are outside the contract. |
| `format` | `"RFC3986"` or `"RFC1738"`, default `"RFC3986"` | Select whether spaces use `%20` or `+` and apply the corresponding formatter. |
| `indices` | boolean, deprecated | `true` selects `"indices"`; `false` selects `"repeat"` when `arrayFormat` is absent. |
| `skipNulls` | boolean, `false` | Omit null-valued fields. |
| `strictNullHandling` | boolean, `false` | Emit a null key without `=` instead of an empty value. |

**Examples:**

```js
qs.stringify({ a: { b: ["x", "y"] } });
// "a%5Bb%5D%5B0%5D=x&a%5Bb%5D%5B1%5D=y"

qs.stringify({ a: ["x", "y"] }, { arrayFormat: "brackets" });
// "a%5B%5D=x&a%5B%5D=y"

qs.stringify({ a: "hello world" }, { format: "RFC1738" });
// "a=hello+world"

qs.stringify({ a: null, b: "x" }, { skipNulls: true });
// "b=x"
```

### Errors and determinism

Invalid JSON-compatible option types must raise a normal `TypeError` (for
example, an invalid charset, format, duplicate mode, or boolean option).
`strictDepth` and `throwOnLimitExceeded` failures must raise a `RangeError`.
The exact wording of an error is not a substitute for the required error class
and behavior; where the upstream contract documents a stable message, preserve
that message as well.

## Implementation Notes

- Reproduce the observable behavior of the pinned `qs` revision, not a generic
  query-string library and not a copied implementation.
- Keep the root CommonJS export and package metadata usable from an empty
  workspace. The scored verifier calls only fixed package/export names through
  a JSON subprocess boundary; it never imports candidate code in the trusted
  test process.
- Do not add callback APIs, regular-expression options, JavaScript-only value
  adapters, browser globals, network calls, lifecycle hooks, registry config,
  or a dependency that is not represented in the reviewed lock/cache closure.
- Do not rely on `npm test`: the upstream `posttest` script runs a
  network-capable `npx npm audit --production` command. The development test
  observation uses the local `tests-only` command only; production verification
  uses a verifier-owned `node:test` report and no network.
- Do not include hidden tests, private cache/tarball bytes, verifier code,
  reward files, Oracle material, credentials, or generated Harbor assets in the
  candidate repository.
