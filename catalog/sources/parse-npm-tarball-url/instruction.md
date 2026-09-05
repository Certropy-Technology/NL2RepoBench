# parse-npm-tarball-url

## Project Description

Build an installable `parse-npm-tarball-url` project from an empty `workspace/`. The project must reproduce the public, local behavior documented in this instruction, including its package entry points, return shapes, ordering, state changes, and documented exceptions. This is a repository-generation task: the agent creates the build metadata and source modules rather than editing an existing implementation.

Distribution/package identity: `parse-npm-tarball-url`; root module entry is the package entry documented below.
The scope is the deterministic local API described below. Network services, undeclared external state, and behavior not represented by the public contract are outside the task.

## Natural Language Instruction

Create the complete project in an empty workspace and make it installable with the command in the environment section. Implement these task-specific capability families from the local API contract:

1. `parseNpmTarballUrl`: expose the documented public entry points, signatures, inputs, outputs, and error behavior.
2. `Errors and JSON boundary`: preserve the documented object or module behavior, including state and side effects.
3. `Production Slice`: preserve ordering, determinism, serialization, and boundary semantics where specified.
4. `parse-npm-tarball-url`: make the public package usable through the documented import path or command-line entry.

Do not add speculative APIs or substitute a different package. Keep the implementation self-contained, ensure imports work after installation, and use the exact public names and signatures in the API Usage Guide. A small implementation is acceptable only when it still satisfies every documented contract.

## Supports or Environment Configuration

- Node.js 24.19.0 with npm 11.17.0.
- Distribution/package identity: `parse-npm-tarball-url`; root module entry is the package entry documented below.
- Install from the workspace with `npm install --offline` using the declared lockfile.
- Declared build/runtime packages are supplied by the frozen evaluation image: `semver`
- Build metadata and package data must be present in the workspace and agree with the public import paths below.
- Agent, candidate, evaluator, Oracle, and control execution are network-isolated. Do not access GitHub, package registries, DNS, databases, or external services at runtime.
- Use deterministic local inputs. Do not rely on the current wall clock, host-specific absolute paths, undeclared environment variables, or an installed copy of the target package.

## Project Directory Structure

```text
workspace/
├── package.json
├── package-lock.json
├── index.js
├── index.d.ts
```

The tree lists agent-owned public project files only. Add additional public modules when required by the API Usage Guide, but keep their import paths consistent with package metadata. Do not create evaluator-only files, hidden fixtures, or private reports in the generated project.

## API Usage Guide

The following is the task-specific public contract recovered from the local instruction and inventory. For every function, class, method, constant, export, and command named below, preserve its complete signature, accepted input domain, return type and shape, ordering, determinism, state/side effects, exceptions, and examples. When the source contract gives an optional argument or a compatibility alias, it is part of the required surface.

### `parseNpmTarballUrl`

**Import path:** the named export from the package root.

**Signature:**

```js
parseNpmTarballUrl(url: string): {
  host: string,
  name: string,
  version: string,
} | null
```

The function is stateless and synchronous. Constructing a WHATWG `URL` parses
the supplied string locally; it does not fetch the URL.

For a URL with a nonempty host and a pathname containing exactly one `/-/`
separator, decode the package portion before the separator with
`decodeURIComponent`. The package portion is the pathname after its leading
slash. Both ordinary names and scoped names are supported. Remove one final
`.tgz` suffix from the filename portion, derive the version after the package
name portion, and accept it when `semver.valid(version, true)` accepts it.
Return the original filename version slice, not a normalized SemVer string:

```js
parseNpmTarballUrl(
  'https://registry.npmjs.org/@scope%2Fpkg/-/pkg-1.2.3-beta.1.tgz'
)
// {host: 'registry.npmjs.org', name: '@scope/pkg', version: '1.2.3-beta.1'}
```

The returned `host` follows WHATWG URL host semantics, including a non-default
explicit port. Query strings and fragments do not change `pathname`. The
protocol is not restricted by this API; a parsed URL with an empty host
returns `null`.

Return `null` when the URL has no host/path, the pathname does not contain
exactly one `/-/` separator, the decoded package name is empty, or the derived
version is not accepted by loose SemVer validation. A malformed percent escape
may throw while decoding instead of returning `null`.

### Errors and JSON boundary

- A falsy input, including `''`, must raise an assertion error with the
  message `url is required`.
- A truthy non-string input must raise an assertion error with the message
  `url should be a string`.
- Malformed or relative URL text may raise the platform `URL` error. The exact
  platform wording is not scored.
- The verifier sends one JSON value as the sole function argument. Values are
  strings, booleans, finite numbers, `null`, arrays, or plain objects only;
  functions, symbols, BigInts, custom prototypes, dates, cycles, and handles
  are outside the boundary. Responses are `null`, the three-string result
  object, or a bounded error record. Do not serialize functions or executable
  strings through this boundary.

The adapter is verifier-owned and is not a candidate CLI requirement. The
candidate function itself must remain directly importable from the package
root.

## Production Slice

The upstream TypeScript development suite is not installed or run. The
frozen denominator is a compact 14-leaf `node:test` slice covering package
shape, simple and prerelease tarballs, scoped and percent-encoded names,
ports/query handling, loose SemVer preservation, malformed and invalid paths,
empty/non-string error behavior, and a null-host URL. Every scored assertion
is derived from the API contract above. The private adapter invokes only the
named export with bounded JSON values and returns JSON values or bounded error
metadata; it never transports source code or JavaScript functions.

## Implementation Notes

- Keep the root exports and module paths stable after installation; do not make behavior depend on the repository's current directory.
- Preserve explicit ordering guarantees. When the contract does not promise an order, do not introduce a new observable order accidentally.
- Propagate documented exceptions and avoid replacing them with generic errors. Validate malformed, empty, boundary, and repeated inputs as described by the API contract.
- Keep filesystem, process, terminal, and resource effects bounded and local. Close files and other resources on both success and failure.
- Do not copy an upstream checkout, implementation source, or evaluation-only material into the generated project. Implement the public behavior from this specification.

## Examples

The examples below are retained from the local task specification. They are starting points for ordinary calls and boundary/error behavior; their exact output and exception semantics remain governed by the API Usage Guide.

### Example 1: ordinary usage
```text
{
    "exports": {
      ".": {
        "types": "./lib/index.d.ts",
        "default": "./lib/index.js"
      }
    }
  }
```

### Example 2: ordinary usage
```text
npm ci --offline --ignore-scripts --no-audit --no-fund
```

### Example 3: boundary or error behavior
```text
parseNpmTarballUrl(url: string): {
  host: string,
  name: string,
  version: string,
} | null
```

### Example 4: boundary or error behavior
```text
parseNpmTarballUrl(
  'https://registry.npmjs.org/@scope%2Fpkg/-/pkg-1.2.3-beta.1.tgz'
)
// {host: 'registry.npmjs.org', name: '@scope/pkg', version: '1.2.3-beta.1'}
```


## Error Handling and Boundary Conditions

- Empty inputs, invalid types, malformed text or paths, unavailable resources, duplicate calls, and cancellation/timeout cases must follow the exception and return-value contracts documented for the relevant API.
- Do not silently coerce values, reorder results, swallow exceptions, or use a fallback dependency unless the API section explicitly requires that behavior.
- File and environment operations must use caller-provided paths and documented defaults only; never read undeclared host files or network resources.
- The implementation must remain usable in the stated NoNetwork environment. A missing optional integration should expose the documented availability or error behavior rather than attempting an online install.
- Security-sensitive inputs must be treated as data. Do not execute strings, load untrusted code, or interpolate shell commands unless that behavior is explicitly part of the documented public API.
