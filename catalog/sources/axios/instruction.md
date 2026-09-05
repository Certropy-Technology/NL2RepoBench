# Project Description

## Project Description

Create a clean, installable npm package named `axios` at version `1.20.0`, implementing the
documented public Axios API for deterministic configuration, request preparation, headers, form
serialization, cancellation, errors, and status-code helpers. The evaluation slice exercises the
public ESM entry point and uses an injected adapter for request tests; it does not contact a remote
HTTP service.

# Natural Language Instruction

Create the `axios` project from an empty `workspace/`. Build an installable implementation, not a loose demonstration script. The public API guide below is the complete source of the task contract; preserve its import paths, signatures, return shapes, ordering, state changes, and exceptions.

Required capabilities:
- request configuration and preparation: implement the documented public behavior and preserve its input/output and error contract.
- case-insensitive headers: implement the documented public behavior and preserve its input/output and error contract.
- form serialization: implement the documented public behavior and preserve its input/output and error contract.
- cancellation, errors, and status helpers: implement the documented public behavior and preserve its input/output and error contract.

Do not copy an upstream checkout or tests. Keep behavior deterministic and local, and make the package usable from the installation layout described below. The principal public entry points include: `set(name, value, rewrite?)`, `get(name)`, `has(name)`, `delete(name)`.

# Supports

- Runtime: Node.js 24.x on Linux amd64 with npm 11.x.
- Package format: ESM (`"type": "module"`) with `index.js` as the runtime entry point.
- The package root must expose `axios` as the default export and the named exports listed below.
- Include `index.js`, the TypeScript declaration files, and the runtime implementation under `lib/`.
- Provide a lockfile with `lockfileVersion: 3` and exact registry-resolved integrity entries for
  the four runtime dependencies: `follow-redirects`, `form-data`, `https-proxy-agent`, and
  `proxy-from-env`. Development tools and lifecycle scripts are not needed.
- The package and its install must work with `npm ci --offline --ignore-scripts`; do not fetch
  source code or dependencies at runtime and do not add native addons or install hooks.


## NoNetwork boundary

Agent, candidate, verifier, Oracle, controls, and normal runtime execution are network-isolated. Do not access GitHub, package registries, Go proxies, DNS, or external services during execution; use only the frozen local build inputs.

# Project Directory Structure

```text
workspace/
├── package.json
├── package-lock.json
├── index.js
├── index.d.ts
└── lib/
    ├── axios.js
    ├── core/
    ├── adapters/
    ├── cancel/
    ├── defaults/
    └── helpers/
```

# API Usage Guide

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

# Implementation Notes

Keep the implementation deterministic and JSON-safe at the public boundary. The test adapter may
inject a non-network adapter, so request behavior must be observable through the resolved config
and returned response without opening sockets. Do not hard-code the private test operation names,
test cases, or expected scores. Preserve the public export shape, input immutability, prototype
pollution defenses, and error identities while avoiding any browser-only or native-only dependency.

# Examples

## Ordinary headers

```javascript
import axios, {AxiosHeaders} from 'axios'

const headers = new AxiosHeaders({'Content-Type': 'application/json'})
headers.set('X-Trace', 'abc')
```

## Ordinary merged configuration

```javascript
import {mergeConfig} from 'axios'
const config = mergeConfig({headers: {Accept: 'text/plain'}}, {timeout: 250})
```

## Boundary: header normalization

```javascript
headers.set('X-Value', 'line1\\r\\nline2')
headers.get('x-value') // control characters are removed
```

## Boundary: cancellation identity

```javascript
import {CanceledError, isCancel, isAxiosError} from 'axios'
const error = new CanceledError('stop')
isCancel(error) && isAxiosError(error) // true
```

# Error Handling and Boundary Conditions

Reject invalid inputs using the documented exception or error result. Preserve empty-input behavior, ordering, Unicode/encoding behavior, cancellation or timeout semantics, and local filesystem boundaries where the API specifies them. Never turn a failed local operation into a network request, subprocess, or silent success.
