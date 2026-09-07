# Project Description

## Project Description

Create a complete installable npm package named `ansi-regex`, version `6.3.0`,
from an empty workspace. The package provides a regular expression factory for
matching ANSI and VT terminal escape sequences.

This is a repository-generation task. Implement the described behavior with
your own files; do not fetch or copy a reference repository or its tests.

# Natural Language Instruction

Create the `ansi-regex` project from an empty `workspace/`. Build an installable implementation, not a loose demonstration script. The public API guide below is the complete source of the task contract; preserve its import paths, signatures, return shapes, ordering, state changes, and exceptions.

Required capabilities:
- ANSI/VT regular-expression construction: implement the documented public behavior and preserve its input/output and error contract.
- CSI sequence matching: implement the documented public behavior and preserve its input/output and error contract.
- OSC control-string matching: implement the documented public behavior and preserve its input/output and error contract.
- first-only and repeatable matching modes: implement the documented public behavior and preserve its input/output and error contract.

Do not copy an upstream checkout or tests. Keep behavior deterministic and local, and make the package usable from the installation layout described below. The principal public entry points include: `ansiRegex(options?)`, `an`.

# Supports

- Node.js `24.19.0`, npm `11.17.0`, Linux amd64, and ESM package semantics.
- The package root must be importable with `import ansiRegex from 'ansi-regex'`.
- `package.json` must identify `ansi-regex` version `6.3.0`, use `"type":
  "module"`, export `./index.js`, and expose the declaration `./index.d.ts`.
- Commit an npm lockfile with `lockfileVersion: 3`. A clean offline installation runs
  `npm ci --offline --ignore-scripts --no-audit --no-fund`.

- The runtime package has no dependencies. Do not use native addons, npm
  workspaces, custom loaders, lifecycle hooks, generated downloads, or network
  access.
- Runtime behavior is deterministic and local. Do not inspect the filesystem,
  environment, clock, randomness, subprocesses, or network.


## NoNetwork boundary

Agent, candidate, verifier, Oracle, controls, and normal runtime execution are network-isolated. Do not access GitHub, package registries, Go proxies, DNS, or external services during execution; use only the frozen local build inputs.

# Project Directory Structure

```text
workspace/
├── package.json
├── package-lock.json
├── index.js
└── index.d.ts
```

# API Usage Guide

### Default export `ansiRegex(options?)`

**Import path:** the package root.

**Signature:**

```ts
export default function ansiRegex(options?: Options): RegExp;
```

The optional `options` object supports one property, `onlyFirst`, a boolean
that defaults to `false`. With the default it returns a global regular
expression; with `onlyFirst: true` it returns a non-global regular expression
that matches only the first occurrence when used with `String.prototype.match`.

The returned expression must match these sequence families:

- CSI sequences introduced by `ESC [` (`\u001B[`) or the 8-bit CSI byte
  (`\u009B`). It must cover SGR styling, semicolon- and colon-separated
  parameters, cursor/erase commands, and private-mode commands.
- OSC control strings introduced by `ESC ]` (`\u001B]`) and terminated by BEL
  (`\u0007`), the two-character string terminator `ESC \\`, or the 8-bit ST
  byte (`\u009C`). The entire OSC control string is one match.

The expression must preserve ordinary text around matches. It must be safe to
reuse across calls: constructing a new expression must not share mutable
`lastIndex` state with another call. Calls with omitted options and with
`{onlyFirst: false}` are equivalent.

Examples:

```js
import ansiRegex from 'ansi-regex';

'\u001B[4mcake\u001B[0m'.match(ansiRegex());
// ['\u001B[4m', '\u001B[0m']

'\u001B[4mcake\u001B[0m'.match(ansiRegex({onlyFirst: true}));
// ['\u001B[4m']

'\u001B]8;;https://example.com\u0007Click\u001B]8;;\u0007'.match(ansiRegex());
// ['\u001B]8;;https://example.com\u0007', '\u001B]8;;\u0007']
```

# Implementation Notes

Keep the public surface to one default ESM function and its TypeScript
declaration. The expression should use bounded ANSI/VT sequence alternatives,
must not match ordinary text, and must not rely on a stateful module-global
regular expression. Preserve text exactly outside matched controls.

# Examples

## Ordinary global matching

```javascript
import ansiRegex from 'ansi-regex'

'[4mcake[0m'.match(ansiRegex())
```

## Ordinary first-only matching

```javascript
'[4mcake[0m'.match(ansiRegex({onlyFirst: true}))
```

## Boundary: plain Unicode text

```javascript
'plain 文本'.match(ansiRegex()) // null
```

## Boundary: independent state

```javascript
const first = ansiRegex()
const second = ansiRegex()
first.test('[31m')
second.test('[31m') // starts from its own lastIndex
```

# Error Handling and Boundary Conditions

Reject invalid inputs using the documented exception or error result. Preserve empty-input behavior, ordering, Unicode/encoding behavior, cancellation or timeout semantics, and local filesystem boundaries where the API specifies them. Never turn a failed local operation into a network request, subprocess, or silent success.
