# Project Description

Build an installable npm package named `leven` that measures the Levenshtein edit distance between two strings and finds the closest string in a candidate list. The workspace starts empty. The package must be an ES module and must expose the documented root API.

# Supports

- Use Node.js 24 and npm. The package must install from an empty workspace with `npm pack`, include an npm v3 `package-lock.json`, and must not require runtime dependencies.
- Put the package entry point at the package root and make the package root export the API. Keep the public package small; generated build output is unnecessary.
- The package must work with UTF-16 JavaScript strings, including non-ASCII text and empty strings.
- Do not add network access, native modules, or a CLI. Do not expose test files as part of the package API.

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
