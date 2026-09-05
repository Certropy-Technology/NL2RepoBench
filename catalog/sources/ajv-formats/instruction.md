# Project Description

## Project Description

Create an installable npm package named `ajv-formats`, version `3.0.1`, from an empty workspace. It is an Ajv plugin that registers JSON Schema format validators and optional format comparison keywords. Implement the documented contract below as a deterministic CommonJS package with compiled files under `dist/`.

The scored surface is a JSON-safe adapter around the public plugin. The adapter creates an Ajv instance in a child process, calls your plugin, compiles JSON schemas, and returns JSON. You do not need to provide this adapter or a CLI.

# Natural Language Instruction

Create the `ajv-formats` project from an empty `workspace/`. Build an installable implementation, not a loose demonstration script. The public API guide below is the complete source of the task contract; preserve its import paths, signatures, return shapes, ordering, state changes, and exceptions.

Required capabilities:
- CommonJS Ajv plugin registration: implement the documented public behavior and preserve its input/output and error contract.
- full and fast named formats: implement the documented public behavior and preserve its input/output and error contract.
- selective format registration: implement the documented public behavior and preserve its input/output and error contract.
- format comparison keywords: implement the documented public behavior and preserve its input/output and error contract.

Do not copy an upstream checkout or tests. Keep behavior deterministic and local, and make the package usable from the installation layout described below. The principal public entry points include: `require("ajv-formats")`, `addFormats(ajv, options)`, `an`, `this`.

# Supports

- Run on Node `24.19.0` with npm `11.17.0` on `linux/amd64`.
- `package.json` must identify `ajv-formats@3.0.1`, expose `dist/index.js` as its main entry, and expose TypeScript declarations for the public plugin types.
- Declare the runtime dependency `ajv` with a compatible semver range. The verifier supplies Ajv from an offline npm v3 closure.
- `npm ci --offline --ignore-scripts --no-audit --no-fund` must succeed, followed by `npm pack --ignore-scripts`.
- Build TypeScript sources into `dist/` with `npm run build` or an equivalent deterministic command. The package must not require a network, browser globals, current time, random state, native addons, or lifecycle hooks at runtime.
- The package root must work with `require("ajv-formats")`. The exported value is the plugin function and it also exposes `.get`.


## NoNetwork boundary

Agent, candidate, verifier, Oracle, controls, and normal runtime execution are network-isolated. Do not access GitHub, package registries, Go proxies, DNS, or external services during execution; use only the frozen local build inputs.

# Project Directory Structure

```text
workspace/
├── package.json
├── package-lock.json
├── src/
│   ├── index.ts
│   ├── formats.ts
│   └── limit.ts
└── dist/
    ├── index.js
    ├── index.d.ts
    ├── formats.js
    └── limit.js
```

# API Usage Guide

### Default plugin

The default export has the shape:

```js
const addFormats = require("ajv-formats")
const ajv = new Ajv({strictTypes: false})
addFormats(ajv)
```

`addFormats(ajv, options)` mutates the supplied Ajv instance by registering formats and returns that same instance. `options` is either a list of format names or an object `{mode?: "fast"|"full", formats?: FormatName[], keywords?: boolean}`. The default object behavior is full mode, all format names, and format comparison keywords enabled. A list selects those names in full mode. An object with `keywords: false` does not register comparison keywords.

Unknown format names must cause Ajv's normal format-registration/compilation error. The plugin must not silently turn a requested format into an unrelated format.

### `get`

`addFormats.get(name, mode = "full")` returns the format definition for one known `FormatName`. `mode` is `"full"` or `"fast"`. Definitions may be regular expressions or validator objects and may include a `compare` function. Unknown names throw an error.

### Registered format names

Register these names: `date`, `time`, `date-time`, `iso-time`, `iso-date-time`, `duration`, `uri`, `uri-reference`, `uri-template`, `url`, `email`, `hostname`, `ipv4`, `ipv6`, `regex`, `uuid`, `json-pointer`, `json-pointer-uri-fragment`, `relative-json-pointer`, `byte`, `int32`, `int64`, `float`, `double`, `password`, and `binary`.

The validators accept strings unless a format is explicitly numeric. `password` and `binary` are permissive string formats. `float` and `double` accept finite JSON numbers. `int32` accepts integers in `[-2147483648, 2147483647]`; `int64` accepts JSON-safe integers. Other formats follow their named RFC/OpenAPI purpose: calendar dates, RFC3339 times/date-times, ISO variants, durations, URI forms, email and hostname syntax, IPv4/IPv6, JavaScript regular expressions, UUIDs, JSON pointers, relative JSON pointers, and base64 bytes.

Full mode performs range-aware date/time validation. It accepts leap day only in leap years, requires a timezone for `time` and `date-time`, and validates timezone offsets and leap seconds. `iso-time` and `iso-date-time` allow an absent timezone. Fast mode keeps the same string shapes but intentionally performs simplified range checks, so structurally shaped values such as `2020-09-35` may be accepted.

### Format comparison keywords

When keywords are enabled, register `formatMaximum`, `formatMinimum`, `formatExclusiveMaximum`, and `formatExclusiveMinimum`. They apply only to string data and compare values using the selected format's `compare` function. Inclusive maximum/minimum allow equality; exclusive variants reject equality. For example, with `format: "date"`, a date at `formatMaximum` is valid while a later date is invalid. If the schema uses a comparison keyword without a `format`, or gives a non-boolean exclusive option where Ajv rejects it, compilation must fail through Ajv's normal error behavior. Non-string data passes these keywords.

# Implementation Notes

- Keep the public root export and the `dist/formats` and `dist/limit` runtime modules internally consistent. The generated code used by Ajv must be able to resolve the full/fast format tables without reaching outside the installed package.
- Preserve deterministic format registration order and comparison behavior. Do not rely on host timezone, locale, filesystem state, or network.
- The verifier adapter accepts only JSON values and does not test callbacks, custom format definitions, `$data` references, TypeScript inference, or direct access to Ajv internals. It does test nested schema compilation, errors, and the public behavior listed above.
- Do not copy the reference implementation or its tests. Design your own implementation from this contract.

# Examples

## Ordinary plugin registration

```javascript
const Ajv = require("ajv")
const addFormats = require("ajv-formats")
const ajv = addFormats(new Ajv({strictTypes: false}))
const validate = ajv.compile({type: "string", format: "date"})
```

## Ordinary selective mode

```javascript
addFormats(ajv, {mode: "fast", formats: ["date", "email"], keywords: false})
const dateDefinition = addFormats.get("date", "fast")
```

## Boundary: unknown format

```javascript
addFormats.get("not-a-format") // throws
```

## Boundary: range-aware full mode

```javascript
validate("2020-02-29") // true
validate("2019-02-29") // false
```

# Error Handling and Boundary Conditions

Reject invalid inputs using the documented exception or error result. Preserve empty-input behavior, ordering, Unicode/encoding behavior, cancellation or timeout semantics, and local filesystem boundaries where the API specifies them. Never turn a failed local operation into a network request, subprocess, or silent success.
