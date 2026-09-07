# Project Description

Build an installable ESM npm package named `is-fullwidth-code-point`, version
`5.1.0`, from an empty workspace. It determines whether a supplied Unicode code
point is rendered as fullwidth or wide in East Asian width classification.

# Natural Language Instruction

Create the `is-fullwidth-code-point` ESM package from an empty `workspace/`.
Implement the default Unicode width predicate, package metadata, and matching
TypeScript declaration. The predicate must classify code points by East Asian
Width category, distinguish fullwidth/wide characters from narrow and ambiguous
characters, and return a stable boolean for every JSON-compatible input.

The implementation is synchronous and stateless. Preserve the package root
default export and do not add a CLI, filesystem access, locale-dependent
behavior, random state, or runtime network lookup.

# Supports

- Node.js `24.19.0`, npm `11.17.0`, Linux amd64, and ESM package semantics.
- The package root must expose the default export and a TypeScript declaration.
- Commit an npm lockfile with `lockfileVersion: 3`. A clean verifier must be
  able to install it without network access using:

  ```bash
  npm ci --offline --ignore-scripts --no-audit --no-fund
  ```

- The only runtime dependency is exact `get-east-asian-width@1.6.0`; it is
  available from the private npm cache prepared for the task. Do not add other
  runtime dependencies, workspaces, native addons, registry overrides, or
  lifecycle scripts.
- Runtime behavior is synchronous, deterministic, stateless, and offline. Do
  not read files, use the clock or randomness, spawn processes, access a TTY,
  or access the network.

# Project Directory Structure

```text
workspace/
├── package.json
├── package-lock.json
├── index.js
└── index.d.ts
```

The package root is the ESM entry point. `index.js` provides the default
`isFullwidthCodePoint` export and `index.d.ts` declares its numeric signature.
The lockfile must agree with package metadata and the declared offline
dependency closure. No tests, verifier files, cache, or generated evaluator
assets are part of the requested workspace.

# API Usage Guide

## Default export `isFullwidthCodePoint(codePoint)`

**Import path:** the package root.

**Signature:**

```ts
export default function isFullwidthCodePoint(codePoint: number): boolean;
```

The function returns `true` when the integer code point has East Asian Width
category Fullwidth or Wide, and `false` for all other integer values. It uses
Unicode scalar/code-point classification rather than JavaScript UTF-16 string
length. Examples:

```js
import isFullwidthCodePoint from 'is-fullwidth-code-point';

isFullwidthCodePoint('谢'.codePointAt(0)); // true
isFullwidthCodePoint('a'.codePointAt(0)); // false
isFullwidthCodePoint(0x1F251); // true
```

Inputs must be JavaScript numbers that are integers. Non-integers and values
whose JavaScript `typeof` is not `number` return `false`; this includes
`NaN`, infinities, strings, booleans, `null`, arrays, and plain objects.
Negative integers, values outside the Unicode range, and unassigned values are
also ordinary `false` results. The function never throws for JSON-compatible
inputs in this contract and does not mutate any input.

The classification includes representative CJK, Hangul, fullwidth-form,
emoji, and supplementary-plane wide characters. It excludes ordinary ASCII,
Latin punctuation with ambiguous/narrow width, control values, halfwidth
forms, and mathematical or quotation characters that are not Fullwidth/Wide.

# Implementation Notes

Use an ESM `package.json` with a safe root export to `index.js` and a matching
`index.d.ts`. Keep the public surface to one default function. Preserve the
boolean return type and avoid exposing dependency internals or an additional
CLI. The evaluator invokes the root export through an isolated JSON child
process; private tests and the Oracle implementation are not part of the
package to implement.

# Examples

```js
import isFullwidthCodePoint from 'is-fullwidth-code-point';

isFullwidthCodePoint('界'.codePointAt(0)); // true
isFullwidthCodePoint('A'.codePointAt(0)); // false
```

```js
isFullwidthCodePoint(0x1F600); // true for a wide emoji code point
isFullwidthCodePoint(0xFF66); // false for a halfwidth form
```

```js
isFullwidthCodePoint(null); // false, outside the numeric domain
isFullwidthCodePoint(65.5); // false, non-integer
```

# Error Handling and Boundary Conditions

The function returns `false`, rather than throwing, for non-number values,
non-integers, negative values, values above `0x10FFFF`, unassigned values, and
values whose East Asian Width is not Fullwidth or Wide. It must also return
`false` for `NaN` and infinities. Ordinary ASCII, ambiguous punctuation, and
halfwidth forms are not wide. Repeated calls with the same integer return the
same primitive boolean and do not mutate input or global state.
