# process-warning

## Project Description

Build an installable `process-warning` project from an empty `workspace/`. The project must reproduce the public, local behavior documented in this instruction, including its package entry points, return shapes, ordering, state changes, and documented exceptions. This is a repository-generation task: the agent creates the build metadata and source modules rather than editing an existing implementation.

Distribution/package identity: `process-warning`; root module entry is the package entry documented below.
The scope is the deterministic local API described below. Network services, undeclared external state, and behavior not represented by the public contract are outside the task.

## Natural Language Instruction

Create the complete project in an empty workspace and make it installable with the command in the environment section. Implement these task-specific capability families from the local API contract:

1. `createWarning(params)`: expose the documented public entry points, signatures, inputs, outputs, and error behavior.
2. `createDeprecation(params)`: preserve the documented object or module behavior, including state and side effects.
3. `spyWarning(warning)`: preserve ordering, determinism, serialization, and boundary semantics where specified.
4. `process-warning`: make the public package usable through the documented import path or command-line entry.

Do not add speculative APIs or substitute a different package. Keep the implementation self-contained, ensure imports work after installation, and use the exact public names and signatures in the API Usage Guide. A small implementation is acceptable only when it still satisfies every documented contract.

## Supports or Environment Configuration

- Node.js 24.19.0 with npm 11.17.0.
- Distribution/package identity: `process-warning`; root module entry is the package entry documented below.
- Install from the workspace with `npm install --offline` using the declared lockfile.
- No third-party runtime package is declared by the local task metadata; standard-library support is sufficient unless the API section says otherwise.
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

### `createWarning(params)`

**Import path:** the package root. **Signature:**
`createWarning(params: WarningOptions): WarningItem`.

`params` is an object with required non-empty string fields `name`, `code`, and `message`, plus
optional boolean `unlimited` (default `false`). An invalid or missing name, code, or message
throws `Error` with the corresponding `Warning ... must not be empty` message. A non-boolean
`unlimited` throws `Error` with `Warning opts.unlimited must be a boolean`. The returned
callable uppercases `code` and exposes `name`, `code`, `message`, `unlimited`, and mutable
boolean `emitted` properties.

Calling the returned `WarningItem(a?, b?, c?)` formats `message` and calls
`process.emitWarning(formatted, name, code)`. It returns `true` when this call emits. A limited
warning returns `false` after its first emission until `emitted` is manually set to `false`;
an unlimited warning returns `true` for every call. Calls and formatting are synchronous from
the caller's perspective, while Node may deliver the process `warning` event asynchronously.

`warning.format(a?, b?, c?): string` returns the formatted message without emitting. It accepts
up to three interpolation values and applies a truthy-prefix rule before calling Node's
`util.format`: all three values are forwarded only when `a`, `b`, and `c` are truthy; the first
two are forwarded only when `a` and `b` are truthy; only `a` is forwarded when `a` alone is
truthy; and no values are forwarded when `a` is falsy. For example, formatting
`"%s|%s|%s"` with `("a", 0, "c")` yields `"a|%s|%s"`, while `(0, "b")` and `(0)` both
leave the template unchanged. `warning.emitted` starts as `false` and becomes `true` after an
emission; changing it is the supported way to reset a limited warning.

### `createDeprecation(params)`

**Import path:** the package root. **Signature:**
`createDeprecation(params: DeprecationOptions): WarningItem`.

It has the same behavior and options as `createWarning`, except the warning name is always
`"DeprecationWarning"` even if a name property is supplied.

### `spyWarning(warning)`

**Import path:** the package root. **Signature:**
`spyWarning(warning: WarningItem): WarningSpyData`.

The first call wraps a warning function and returns a spy object with `calls`, `callCount()`,
`reset()`, and `restore()`. Each call made while spying adds `{arguments, result}` to `calls`,
where `result` is the underlying warning function's boolean return. The active spy wrapper
itself returns `undefined`. Its recorded `arguments` use the same trailing truthiness rule as
formatting: retain three entries when the third is truthy, two when the second is truthy, one
when the first is truthy, and otherwise none. `callCount()` returns the number of recorded calls.
`reset()` clears calls and sets `warning.emitted` to `false`. `restore()` also resets state and
removes the wrapper; subsequent calls again return the normal boolean result and are not
recorded. Calling `spyWarning` again for the same active warning returns the existing spy rather
than stacking wrappers. After `restore()`, a later call creates a fresh active spy.


Preserve CommonJS loading, the default and `processWarning` aliases, uppercase warning codes,
Node `util.format` interpolation, once-only versus unlimited state, and the exact boolean
return contract. Warning emission must use `process.emitWarning` with the formatted message,
name, and code. Keep warning state isolated between separately created warnings. Do not read
files, use the clock or randomness, spawn processes, use a TTY, or access the network in the
package implementation. The verifier invokes the package only through a UID-isolated child
adapter; evaluation tests and the Oracle implementation are not available in the candidate
workspace.

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
npm ci --offline --ignore-scripts --no-audit --no-fund
```

### Example 2: ordinary usage
```text
npm ci --offline --ignore-scripts --no-audit --no-fund
```

### Example 3: boundary or error behavior
```text
npm ci --offline --ignore-scripts --no-audit --no-fund
```

### Example 4: boundary or error behavior
```text
npm ci --offline --ignore-scripts --no-audit --no-fund
```


## Error Handling and Boundary Conditions

- Empty inputs, invalid types, malformed text or paths, unavailable resources, duplicate calls, and cancellation/timeout cases must follow the exception and return-value contracts documented for the relevant API.
- Do not silently coerce values, reorder results, swallow exceptions, or use a fallback dependency unless the API section explicitly requires that behavior.
- File and environment operations must use caller-provided paths and documented defaults only; never read undeclared host files or network resources.
- The implementation must remain usable in the stated NoNetwork environment. A missing optional integration should expose the documented availability or error behavior rather than attempting an online install.
- Security-sensitive inputs must be treated as data. Do not execute strings, load untrusted code, or interpolate shell commands unless that behavior is explicitly part of the documented public API.
