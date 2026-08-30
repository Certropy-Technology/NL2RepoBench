# Build `process-warning`

## Project Description

Build an installable CommonJS npm package named `process-warning`, version `5.1.0`, from an
empty workspace. It creates warning functions that format messages and emit a Node.js process
warning once by default, or on every call when configured as unlimited. It also provides a
deprecation-warning helper and a spy facility intended for tests.

## Supports

- Node.js `24.19.0`, npm `11.17.0`, Linux amd64, glibc, and CommonJS package semantics.
- A root `package.json` with `name: "process-warning"`, `version: "5.1.0"`,
  `main: "index.js"`, `type: "commonjs"`, and the TypeScript declaration entry
  `types: "types/index.d.ts"`.
- A committed npm v3 `package-lock.json`. The clean verifier installs with:

  ```bash
  npm ci --offline --ignore-scripts --no-audit --no-fund
  ```

- No runtime dependencies, native addons, workspaces, lifecycle hooks, registry overrides,
  CLI, network access, or globally installed copy of this package.
- The package root is usable with both `require('process-warning')` and a TypeScript
  `export =` declaration. The required object exports are `createWarning`,
  `createDeprecation`, and `spyWarning`; `default` and `processWarning` refer to the same
  exported object.

## API Usage Guide

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

## Implementation Notes

Preserve CommonJS loading, the default and `processWarning` aliases, uppercase warning codes,
Node `util.format` interpolation, once-only versus unlimited state, and the exact boolean
return contract. Warning emission must use `process.emitWarning` with the formatted message,
name, and code. Keep warning state isolated between separately created warnings. Do not read
files, use the clock or randomness, spawn processes, use a TTY, or access the network in the
package implementation. The verifier invokes the package only through a UID-isolated child
adapter; private tests and the Oracle implementation are not available in the candidate
workspace.
