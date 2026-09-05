# Project Description

Build an installable ESM npm package named `is-unicode-supported`, version
`2.1.0`, from an empty workspace. It reports whether the current terminal is
considered Unicode-capable from Node's platform identifier and terminal
environment variables.

## Natural Language Instruction

Create the `is-unicode-supported` package from an empty workspace. Implement
the default ESM function and the package metadata required for an offline npm
installation. The implementation must decide terminal capability from the
current Node platform and the documented environment markers, rather than
from a TTY probe or a host-specific heuristic.

The implementation must preserve all of the following capabilities:

1. Export one synchronous default function with the exact boolean return shape.
2. Apply the non-Windows `TERM=linux` exception and ordinary non-Windows rules.
3. Recognize every supported Windows marker with exact, case-sensitive values.
4. Re-read process state for every call so changes between calls are observable.
5. Keep the package root, declaration file, version, and npm metadata consistent.

Do not add a CLI, additional public helpers, persistent state, or fallback that
consults the filesystem, locale, network, or an external terminal service.

# Supports

- Node.js `24.19.0` and npm `11.17.0` on Linux amd64 with glibc.
- A root ESM default export and a matching `index.d.ts` declaration.
- A committed npm `package-lock.json` using `lockfileVersion: 3`.
- Offline installation with lifecycle scripts disabled:

  ```bash
  npm ci --offline --ignore-scripts --no-audit --no-fund
  ```

- No runtime dependencies, workspaces, native addons, registry overrides,
  lifecycle scripts, filesystem reads, spawned processes, or network access.

## Project Directory Structure

```text
workspace/
├── package.json
├── package-lock.json
├── index.js
└── index.d.ts
```

`package.json` must declare the ESM package name and version, set the package
root export to `index.js`, and describe the declaration file. `index.js` is
the public runtime entry and contains the default `isUnicodeSupported` export.
`index.d.ts` declares the same default function and no extra runtime API.
The lockfile is a v3 lockfile for the zero-dependency package. Do not create a
`src/` directory, a generated build directory, a CLI, or test-only exports.

# API Usage Guide

## Default export `isUnicodeSupported()`

**Import path:** the package root.

**Signature:**

```ts
export default function isUnicodeSupported(): boolean;
```

The function takes no arguments and returns a primitive boolean. It consults
Node's `process.platform` and these terminal-environment markers each time it
is called: `TERM`, `TERM_PROGRAM`, `WT_SESSION`, `TERMINUS_SUBLIME`,
`ConEmuTask`, and `TERMINAL_EMULATOR`.

On every platform other than `win32`, return `false` exactly when `TERM` is
the string `"linux"`; return `true` for an absent `TERM`, an empty `TERM`, or
any other `TERM` value. On `win32`, return `true` when at least one supported
Windows-terminal marker is present:

- `WT_SESSION` or `TERMINUS_SUBLIME` is a non-empty string.
- `ConEmuTask` is exactly `"{cmd::Cmder}"`.
- `TERM_PROGRAM` is exactly `"Terminus-Sublime"` or `"vscode"`.
- `TERM` is exactly `"xterm-256color"`, `"alacritty"`,
  `"rxvt-unicode"`, or `"rxvt-unicode-256color"`.
- `TERMINAL_EMULATOR` is exactly `"JetBrains-JediTerm"`.

When no Windows marker matches, return `false`. Matching is case-sensitive;
near-miss names and empty strings are not supported markers. Calls are
synchronous and stateless except for observing the current process state, so
changing one of the documented environment variables between calls changes
the next result.

# Implementation Notes

Keep the package ESM (`"type": "module"`) and expose `index.js` plus
`index.d.ts` through the root export. The evaluator invokes the default export
through an isolated child-process boundary and supplies platform and terminal
state only through that request. Do not add a CLI or expose internal helpers.
The package must remain deterministic for a supplied state and must not depend
on a real TTY, locale, clock, randomness, or network service.

## Examples

```js
import isUnicodeSupported from 'is-unicode-supported';

const supported = isUnicodeSupported(); // primitive boolean
```

```js
// The function observes process.env on each invocation.
process.env.TERM_PROGRAM = 'vscode';
const supportedInTerminal = isUnicodeSupported();
```

```ts
import isUnicodeSupported from 'is-unicode-supported';

const value: boolean = isUnicodeSupported();
```

## Error Handling and Boundary Conditions

- The function accepts no arguments. Extra arguments must not change the
  result; non-boolean return values are not part of the contract.
- Environment matching is exact and case-sensitive. An empty marker is not a
  supported marker, and a near miss such as `VSCODE` is not equivalent to
  `vscode`.
- On non-Windows platforms, `TERM=linux` is the only unsupported terminal
  case. Missing or empty `TERM` values remain supported on those platforms.
- On Windows, no matching marker returns `false`, while any one matching
  marker returns `true`; unrelated environment variables are ignored.
- Calls must not cache an earlier answer. A caller that changes a documented
  marker and calls again receives the answer for the new process state.
- Installation and runtime are NoNetwork for the agent, candidate, verifier,
  Oracle, and controls. No source or dependency fetch is a runtime fallback.
