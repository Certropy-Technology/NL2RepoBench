# Build an Axios-compatible Node package

## Project Description

Create a clean, installable npm package named `axios` at version `1.20.0`, implementing the
documented public Axios API for deterministic configuration, request preparation, headers, form
serialization, cancellation, errors, and status-code helpers. The evaluation slice exercises the
public ESM entry point and uses an injected adapter for request tests; it does not contact a remote
HTTP service.

## Supports

- Runtime: Node.js 24.x on Linux amd64 with npm 11.x.
- Package format: ESM (`"type": "module"`) with `index.js` as the runtime entry point.
- The package root must expose `axios` as the default export and the named exports listed below.
- Include `index.js`, the TypeScript declaration files, and the runtime implementation under `lib/`.
- Provide a lockfile with `lockfileVersion: 3` and exact registry-resolved integrity entries for
  the four runtime dependencies: `follow-redirects`, `form-data`, `https-proxy-agent`, and
  `proxy-from-env`. Development tools and lifecycle scripts are not needed.
- The package and its install must work with `npm ci --offline --ignore-scripts`; do not fetch
  source code or dependencies at runtime and do not add native addons or install hooks.

## API Usage Guide

The root module must expose exactly these named exports in addition to the default `axios` export:
`Axios`, `AxiosError`, `AxiosHeaders`, `Cancel`, `CancelToken`, `CanceledError`, `HttpStatusCode`,
`VERSION`, `all`, `create`, `formToJSON`, `getAdapter`, `isAxiosError`, `isCancel`, `mergeConfig`,
`spread`, and `toFormData`. `VERSION` must be `"1.20.0"`.

### Request preparation

- `axios.request(config)` and the convenience methods (`get`, `delete`, `head`, `options`,
  `post`, `put`, `patch`, and `query`) accept a URL/config plus optional data and config. Merge
  `baseURL`, URL, method, headers, params, timeout, and other request options without mutating the
  caller's objects.
- Methods are normalized to lower case. Object request bodies are JSON encoded by the default
  transform and receive an `application/json` content type when no incompatible content type was
  supplied.
- `axios.create(defaults)` returns an independent client whose defaults are merged into each
  request. A supplied adapter receives the resolved config and may return a response object with
  `data`, `status`, `statusText`, `headers`, `config`, and `request`.
- `axios.getUri(config)` combines `baseURL` and `url`, then serializes params deterministically;
  array brackets and reserved characters must be percent encoded as produced by Axios.

### Headers

- `new AxiosHeaders(input)` accepts a plain object or iterable key/value source. Header names are
  case-insensitive, values are stringified, and CR/LF control characters are removed from values.
- Implement `set(name, value, rewrite?)`, `get(name)`, `has(name)`, `delete(name)`,
  `normalize(format?)`, `toJSON(asStrings?)`, `toString()`, and iteration. `rewrite: false` must
  preserve an existing value; `toJSON()` must return a JSON-safe object.

### Configuration and form helpers

- `mergeConfig(left, right)` deeply merges nested `headers` and `params` objects while allowing
  right-hand scalar values and explicit `null` to override left-hand values.
- `toFormData(input, formData?, options?)` traverses JSON-compatible objects and arrays. Support
  bracket and dot notation, `indexes`, `dots`, and `{}` meta-token serialization, and call the
  destination's `append(key, value)` method in deterministic traversal order.
- `formToJSON(form)` converts compatible form data into a JSON object.

### Errors, cancellation, and helpers

- `new AxiosError(message, code?, config?, request?, response?)` creates an error with the Axios
  error identity. `isAxiosError(value)` recognizes it, and its public diagnostic fields include
  `message`, `name`, `code`, `status`, and `config`.
- `new CanceledError(message?)` has code `ERR_CANCELED`; `isCancel(value)` recognizes it and it is
  also an Axios error.
- `HttpStatusCode` maps standard numeric HTTP status codes to PascalCase names and maps those names
  back to numbers.
- `all(iterable)` resolves all promises in input order. `spread(callback)(array)` invokes the
  callback with the array elements as positional arguments.

## Implementation Notes

Keep the implementation deterministic and JSON-safe at the public boundary. The test adapter may
inject a non-network adapter, so request behavior must be observable through the resolved config
and returned response without opening sockets. Do not hard-code the private test operation names,
test cases, or expected scores. Preserve the public export shape, input immutability, prototype
pollution defenses, and error identities while avoiding any browser-only or native-only dependency.
