# parse-json

## Project Description

Build an installable `parse-json` project from an empty `workspace/`. The project must reproduce the public, local behavior documented in this instruction, including its package entry points, return shapes, ordering, state changes, and documented exceptions. This is a repository-generation task: the agent creates the build metadata and source modules rather than editing an existing implementation.

Distribution/package identity: `parse-json`; root module entry is the package entry documented below.
The scope is the deterministic local API described below. Network services, undeclared external state, and behavior not represented by the public contract are outside the task.

## Natural Language Instruction

Create the complete project in an empty workspace and make it installable with the command in the environment section. Implement these task-specific capability families from the local API contract:

1. `parseJson(string, reviver?, fileName?)`: expose the documented public entry points, signatures, inputs, outputs, and error behavior.
2. `JSONError`: preserve the documented object or module behavior, including state and side effects.
3. `parse-json`: preserve ordering, determinism, serialization, and boundary semantics where specified.
4. `root exports`: make the public package usable through the documented import path or command-line entry.

Do not add speculative APIs or substitute a different package. Keep the implementation self-contained, ensure imports work after installation, and use the exact public names and signatures in the API Usage Guide. A small implementation is acceptable only when it still satisfies every documented contract.

## Supports or Environment Configuration

- Node.js 24.19.0 with npm 11.17.0.
- Distribution/package identity: `parse-json`; root module entry is the package entry documented below.
- Install from the workspace with `npm install --offline` using the declared lockfile.
- Declared build/runtime packages are supplied by the frozen evaluation image: `@babel/code-frame`, `@babel/helper-validator-identifier`, `js-tokens`, `picocolors`, `index-to-position`, `type-fest`
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

## `parseJson(string, reviver?, fileName?)`

**Import path:** package root.

**Signature:**

```js
parseJson(string, reviver?, fileName?)
```

`string` is JSON text accepted by `JSON.parse`. `reviver` has the same meaning
as the second argument to `JSON.parse`; when it is a string, it is interpreted
as `fileName` instead. `fileName` is optional metadata appended to a parsing
error message and exposed as `error.fileName`.

On valid JSON, return the parsed JSON-compatible value. Preserve native
`JSON.parse` semantics for objects, arrays, primitives, whitespace, and a
reviver callback. The function is synchronous and does not mutate its input.

On invalid JSON, throw a `JSONError`. The error wraps the native `SyntaxError`
as `cause`, has `name === "JSONError"`, and keeps the original `fileName`.
Its `message` adds a printable Unicode code point for unexpected-token errors,
adds `while parsing empty string` only for empty input, appends ` in <fileName>`
when a file name is set, and includes a source frame when a location can be
derived. Native Node error wording and line/column details are preserved.

## `JSONError`

**Import path:** package root.

`JSONError` is a public class for `instanceof` checks. Its legacy constructor
accepts a string message. The writable `message` property can be replaced;
the file name suffix and lazily computed `codeFrame` remain available.

The read-only `codeFrame` includes terminal highlighting when supported, while
`rawCodeFrame` never includes color escape sequences. Both use one-based line
and column locations and JavaScript UTF-16 offsets. For errors without a
location, the frame properties are `undefined`.


Keep the package deterministic under `TZ=UTC` and offline execution. Do not
write files, spawn processes, read environment state, use the network, or
change global parser state. The evaluator calls the package only through a
bounded JSON child adapter; callbacks used for reviver coverage are created by
the trusted adapter and are not supplied as model input. evaluation tests and the
Oracle implementation are not part of the package to implement.

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
parseJson(string, reviver?, fileName?)
```

### Example 2: ordinary usage
```text
parseJson(string, reviver?, fileName?)
```

### Example 3: boundary or error behavior
```text
parseJson(string, reviver?, fileName?)
```

### Example 4: boundary or error behavior
```text
parseJson(string, reviver?, fileName?)
```


## Error Handling and Boundary Conditions

- Empty inputs, invalid types, malformed text or paths, unavailable resources, duplicate calls, and cancellation/timeout cases must follow the exception and return-value contracts documented for the relevant API.
- Do not silently coerce values, reorder results, swallow exceptions, or use a fallback dependency unless the API section explicitly requires that behavior.
- File and environment operations must use caller-provided paths and documented defaults only; never read undeclared host files or network resources.
- The implementation must remain usable in the stated NoNetwork environment. A missing optional integration should expose the documented availability or error behavior rather than attempting an online install.
- Security-sensitive inputs must be treated as data. Do not execute strings, load untrusted code, or interpolate shell commands unless that behavior is explicitly part of the documented public API.
