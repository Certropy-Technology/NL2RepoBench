# Project Description

Build an installable npm package named `leven` that measures the Levenshtein edit distance between two strings and finds the closest string in a candidate list. The workspace starts empty. The package must be an ES module and must expose the documented root API.

# Natural Language Instruction

Create the `leven` project from an empty `workspace/`. Build the package root
so consumers can import the default `leven` function and the named
`closestMatch` function. Implement UTF-16 code-unit edit distance, optional
distance cutoffs, nearest-candidate selection, stable tie handling, and the
documented empty/non-array boundaries. Keep both functions pure for their
inputs and return JSON-serializable values or the documented `undefined`.

The deliverable is a small ESM package, not a CLI or a copy of upstream source
or tests. Include install metadata and the declaration file required by the
package contract; do not add runtime dependencies or network behavior.

# Supports

- Use Node.js 24 and npm. The package must install from an empty workspace with `npm pack`, include an npm v3 `package-lock.json`, and must not require runtime dependencies.
- Put the package entry point at the package root and make the package root export the API. Keep the public package small; generated build output is unnecessary.
- The package must work with UTF-16 JavaScript strings, including non-ASCII text and empty strings.
- Do not add network access, native modules, or a CLI. Do not expose test files as part of the package API.

# Project Directory Structure

```text
workspace/
├── package.json
├── package-lock.json
├── index.js
└── index.d.ts
```

`package.json` must identify `leven@4.1.0` as an ESM package and map the root
export to `index.js`. `index.js` contains the default `leven` export and named
`closestMatch` export. `index.d.ts` declares both signatures and their return
types. The v3 lockfile must describe the zero-dependency installation and the
package must work from the package root after offline `npm ci`.

# API Usage Guide

## Default export: `leven`

Import path: the package root, for example `import leven from 'leven';`

Signature: `leven(first, second, options?)`

- `first` and `second` are strings. Return a non-negative integer: the minimum number of single-code-unit insertions, deletions, or substitutions needed to change one string into the other.
- The result is symmetric and deterministic. Equal strings always return `0`; an empty string has the distance equal to the other string's JavaScript `.length`.
- `options` is optional. When supplied, `options.maxDistance` is a numeric cutoff. If the true distance is greater than the cutoff, return the cutoff instead of the true distance. If the true distance is at most the cutoff, return the true distance. A cutoff of `0` therefore returns `0` for different strings as well as equal strings.
- A cutoff does not change the exact result when the distance is within the cutoff. The option is allowed to be omitted, `undefined`, or `null`.
- The function must not mutate either input string or the options object.

Example: `leven('kitten', 'sitting')` returns `3`, while `leven('kitten', 'sitting', {maxDistance: 2})` returns `2`.

## Named export: `closestMatch`

Import path: the package root, for example `import {closestMatch} from 'leven';`

Signature: `closestMatch(target, candidates, options?)`

- `target` is a string. `candidates` is an array of strings. Return the candidate with the smallest Levenshtein distance to `target`.
- Preserve input order for equal-distance candidates. An earlier candidate wins. Duplicate values do not change the answer.
- An exact match wins immediately, regardless of other candidates.
- With `options.maxDistance`, return `undefined` when no candidate has distance at most the cutoff. Otherwise return the closest qualifying candidate using the same order rule.
- An empty candidate array returns `undefined`. For compatibility, non-array candidate values also return `undefined` rather than throwing.
- The function is deterministic and must not modify the candidate array or its string values.

Example: `closestMatch('kitten', ['sitting', 'kitchen', 'mittens'])` returns `'kitchen'` because it is one of the closest candidates and appears first among the closest qualifying values.

# Implementation Notes

- Publish valid package metadata with `name: "leven"`, an ESM package configuration, a root export, and a declaration file describing both exports.
- Keep the public default and named exports available from the same root module. Do not require consumers to import an internal path.
- Preserve JavaScript string semantics: indexing and length are based on UTF-16 code units, not Unicode grapheme clusters.
- The implementation may use any correct deterministic algorithm. It should handle repeated calls and long strings without retaining unbounded state from previous calls.
- The evaluator calls the package in isolated child processes and checks only the documented package behavior and installation contract.

The package root is the only runtime import surface. Keep public declarations
and implementation files aligned so that installation from a clean directory
does not rely on the repository checkout.

# Examples

```js
import leven, {closestMatch} from 'leven';

console.log(leven('kitten', 'sitting')); // 3
console.log(closestMatch('cat', ['cut', 'dog'])); // 'cut'
```

```js
const options = {maxDistance: 2};
const distance = leven('kitten', 'sitting', options); // 2
const candidate = closestMatch('kitten', ['sitting', 'kitchen'], options);
```

# Error Handling and Boundary Conditions

- Equal strings return `0`; an empty string compares by JavaScript `.length`,
  including UTF-16 code units for non-BMP characters.
- A cutoff returns the true distance when it is within the cutoff and the
  cutoff itself when the true distance is greater. `0`, omitted, `undefined`,
  and `null` options follow the documented semantics.
- `closestMatch` returns `undefined` for an empty or non-array candidate list,
  and for a non-qualifying cutoff. Ties select the earliest candidate and
  duplicate candidates do not alter that rule.
- Do not mutate strings, the candidate array, or the options object. No file,
  environment, clock, randomness, registry, or network state may affect a
  result.

The package should also remain repeatable across multiple calls in one
process: a previous long-string calculation must not change a later result.
String comparison is case-sensitive and treats combining characters and
surrogate pairs according to JavaScript string indexing, not visual character
count. A candidate that is closer later in the input wins only when it has a
strictly smaller distance; equal distances retain the first candidate.

The public declaration should describe `undefined` for an unqualified
`closestMatch` result and should not invent a promise or callback API. Invalid
inputs outside the documented string/list domain are not a reason to access
the filesystem or network; preserve the package's local deterministic
boundary instead.
