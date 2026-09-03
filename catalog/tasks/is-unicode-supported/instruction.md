# Project Description

Build an installable ESM npm package named `is-unicode-supported`, version
`2.1.0`, from an empty workspace. It reports whether the current terminal is
considered Unicode-capable from Node's platform identifier and terminal
environment variables.

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
