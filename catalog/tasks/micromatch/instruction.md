# Project Description

Create a complete CommonJS npm package named `micromatch` that implements glob matching for strings and path-like strings. The package must be usable through `require('micromatch')`; the required value is a callable function with the method properties documented below. This is a pure library task: it has no CLI, performs no filesystem or network I/O, and must return deterministic results for the same inputs and options.

# Supports

- Target Node.js runtime: Node `24.19.0` on Linux (`linux/amd64`, glibc).
- Package manager contract: npm `11.17.0`, a root `package-lock.json` with `lockfileVersion: 3`, and offline installation with lifecycle scripts disabled.
- Required repository files include `package.json`, `package-lock.json`, and the CommonJS implementation referenced by `package.json.main` (normally `index.js`). `package.json` must use the name `micromatch`, version `4.0.8`, and declare Node `>=8.6` compatibility.
- Do not include `node_modules`, native addons, workspaces, symlinks, shell scripts, or install/prepare/publish lifecycle hooks in the package.
- A dependency-free implementation is valid. If you use the frozen runtime helpers, the available exact versions are `braces@3.0.3` and `picomatch@2.3.1`; their transitive closure is already available to the offline verifier. Do not fetch packages or source code while implementing the task.
- Inputs described as lists are arrays of strings unless the signature explicitly permits one string. Options are ordinary JavaScript objects. Returned collections must be fresh JavaScript arrays or plain objects as described.

# API Usage Guide

## Package export and aliases

```js
const micromatch = require('micromatch');
```

The package export is callable. `micromatch.match` is the same function object as the package export. `micromatch.any` is the same function object as `micromatch.isMatch`. The following method properties are functions: `matcher`, `isMatch`, `any`, `not`, `contains`, `matchKeys`, `some`, `every`, `all`, `capture`, `makeRe`, `scan`, `parse`, `braces`, `braceExpand`, and `hasBraces`.

## `micromatch(list, patterns, options?) -> string[]`

`list` may be one string or an array of strings. `patterns` may be one glob string or an array of glob strings. The function returns the strings selected by the patterns.

- A positive pattern adds matching inputs. Pattern groups are processed from left to right and each group visits inputs in input order, so `micromatch(['a.js', 'a.txt', 'b.md'], ['*.md', '*.js'])` returns `['b.md', 'a.js']`.
- Duplicate inputs and repeated matches appear only once.
- A pattern beginning with `!` is negative unless `nonegate` is true. It removes matching inputs. If every pattern is negative, matching begins with the full input set. A later positive pattern may re-include a previously removed input.
- `*` matches characters inside one path segment, `?` matches one non-separator character, and `**` may span zero or more path segments. Character classes such as `[a-z]` and POSIX classes such as `[[:digit:]]` are supported. Extglobs such as `@(js|md)` and complete brace expressions are supported by default.
- Unless `dot` is true, a wildcard at a segment boundary does not match a leading `.`.

The supported options include:

- `dot: true`: allow wildcard segments to match leading-dot names.
- `nocase: true`: compare without case sensitivity.
- `basename: true` or `matchBase: true`: when a pattern contains no slash, match it against the final path segment.
- `noext: true`: treat extglob operators as ordinary pattern text.
- `nonegate: true`: treat a leading `!` as literal text.
- `noglobstar: true`: treat `**` as ordinary consecutive stars rather than a globstar.
- `nobrace: true`: disable brace processing.
- `ignore`: one pattern or an array of patterns whose matches are removed from otherwise positive results.
- `failglob: true`: if no string remains, throw `Error` with a message beginning `No matches found for`.
- `nonull: true` or `nullglob: true`: if no string remains, return the input patterns instead. If `unescape: true` is also set, remove backslashes from those returned patterns.
- `onResult(state)`, `onMatch(state)`, and `onIgnore(state)`: callbacks forwarded to matching. State includes at least `glob`, `input`, `output`, and `isMatch`. `onResult` runs for every attempted input; `onMatch` runs for accepted matcher results; `onIgnore` runs for results rejected by `ignore`.

Examples:

```js
micromatch(['a.js', 'a.test.js', 'b.js'], ['*.js', '!*.test.js']);
// ['a.js', 'b.js']

micromatch(['a/b.js', 'a/x/b.js'], 'a/**/b.js');
// ['a/b.js', 'a/x/b.js']

micromatch(['.gitignore', 'a.js'], '*', { dot: true });
// ['.gitignore', 'a.js']
```

## `matcher(pattern, options?) -> (input: string) => boolean`

Compile one glob into a reusable predicate. The predicate applies the same matching and option semantics as the main function.

```js
const isJavaScript = micromatch.matcher('*.js');
isJavaScript('a.js');  // true
isJavaScript('a.txt'); // false
```

## `isMatch(input, patterns, options?) -> boolean` and `any`

Return true when `input` matches at least one supplied pattern. `patterns` may be one string or an array. `any` is the identity alias of `isMatch`.

## `not(list, patterns, options?) -> string[]`

Return the unique inputs that are not accepted by any supplied pattern, preserving their deterministic encounter order. It accepts the same pattern syntax and matching options as the main function.

```js
micromatch.not(['a.js', 'a.txt', 'b.js'], ['*.js', 'b.*']);
// ['a.txt']
```

## `contains(input, patterns, options?) -> boolean`

Return true when a literal or glob pattern matches any part of `input`, rather than requiring a whole-string match. `patterns` may be one string or an array. Empty string and `'./'` inputs or patterns do not count as a match. A non-string `input` throws `TypeError` with a message beginning `Expected a string`.

## `matchKeys(object, patterns, options?) -> object`

Filter only the object's own top-level enumerable keys with the normal matching rules and return a new plain object containing matching key/value pairs. Nested keys are not traversed. A non-object first argument (including an array) throws `TypeError` with message `Expected the first argument to be an object`.

## `some(list, patterns, options?) -> boolean`

Return true as soon as at least one item matches at least one pattern. A string is accepted in place of a one-item list.

## `every(list, patterns, options?) -> boolean`

Return true only when every item matches every supplied pattern. Patterns, including negative patterns, are evaluated as predicates. A string is accepted in place of a one-item list.

## `all(input, patterns, options?) -> boolean`

Return true only when one string matches every supplied pattern. A non-string `input` throws `TypeError` with a message beginning `Expected a string`.

## `capture(pattern, input, options?) -> string[] | undefined`

Compile `pattern` in capture mode and return its capture groups when `input` matches. Unmatched optional groups are returned as empty strings. Return `undefined` when the pattern does not match.

```js
micromatch.capture('src/*/(*).js', 'src/lib/file.js');
// ['lib', 'file', 'file']
```

## `makeRe(pattern, options?) -> RegExp`

Compile a glob into a `RegExp`. Calling `.test(input)` on the result must follow the same wildcard, dotfile, case, extglob, globstar, brace, and negation options as other matching methods.

## `scan(pattern, options?) -> object`

Lexically scan one pattern without executing it. Return a state object containing the original `input`, any consumed `prefix`, the non-glob `base`, remaining `glob`, and boolean classification fields including `isGlob`, `isGlobstar`, `isExtglob`, and `negated`.

For example, scanning `!src/**/a*.js` reports `input: '!src/**/a*.js'`, `prefix: '!'`, `base: 'src'`, `glob: '**/a*.js'`, `isGlob: true`, and `negated: true`.

## `parse(patterns, options?) -> object[]`

Parse one pattern or an array of patterns into regex-source states. Always return an array and preserve input pattern order. Brace compilation occurs before parsing. Each state includes at least `input`, `output`, `negated`, and `prefix`.

```js
micromatch.parse('{a,b}/*.js').map(({ input, output, negated, prefix }) => ({
  input, output, negated, prefix
}));
// [{
//   input: '(a|b)/*.js',
//   output: '(a|b)\\/(?!\\.)(?=.)[^/]*?\\.js',
//   negated: false,
//   prefix: ''
// }]
```

## `braces(pattern, options?) -> string[]`

Process one string containing braces. By default, compile alternatives into a compact regex-like form; `{a,b}` becomes `(a|b)`. With `expand: true`, return every expanded string. If `nobrace` is true or no complete brace pair exists, return `[pattern]` unchanged. A non-string pattern throws `TypeError` with message `Expected a string`.

## `braceExpand(pattern, options?) -> string[]`

Equivalent to `braces(pattern, { ...options, expand: true })`. It expands alternatives and ranges, so `braceExpand('file{1..3}.js')` returns `['file1.js', 'file2.js', 'file3.js']`. A non-string pattern throws the same `TypeError` as `braces`.

## `hasBraces(pattern) -> boolean`

Return true only when the string contains an opening `{` followed later by a closing `}`. An incomplete pair returns false.

# Implementation Notes

- Matching uses forward slash as the path-segment separator for the deterministic Linux contract. Preserve input strings in returned arrays; options may normalize only the matcher's comparison/output state where explicitly documented.
- All collection-returning APIs must be deterministic and must not mutate caller-owned arrays or objects.
- Callback order is observable and follows pattern order, then input order within each pattern.
- Keep package initialization free of output and side effects. Do not print diagnostics to stdout, read ambient files, inspect the network, or depend on terminal state.
- The verifier installs and packs the candidate under an unprivileged user, rejects lifecycle/native/workspace features, and invokes each behavior in a bounded child process. Implement the documented package behavior rather than a separate test-only command.
