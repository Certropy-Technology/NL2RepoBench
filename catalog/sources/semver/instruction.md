## Project Description

`semver` is a JavaScript library for parsing and comparing versions that follow
the Semantic Versioning 2.0.0 specification. It is intended for package
managers, release tools, build systems, and other Node.js programs that need to
decide whether one release precedes another without treating versions as
ordinary strings. The frozen package is `semver` version 7.8.5 from the
`npm/node-semver` project. It is a CommonJS package with no runtime
dependencies.

The implementation target is the version grammar and precedence behavior
exposed by the package. A version has numeric `major`, `minor`, and `patch`
components, optional dot-separated prerelease identifiers, and optional
dot-separated build identifiers. The normalized public version omits build
metadata, while parsed data still reports build identifiers separately. Strict
and loose parsing must be distinguishable, and invalid input must not be
silently converted into a valid strict version.

### Natural Language Instruction

Create an installable Node.js package named `semver` whose package name and
CommonJS root import are both `semver`. Implement the following capabilities:

1. Parse a version string into a JSON-safe representation containing its
   normalized version and numeric or identifier components, or report that the
   input is invalid.
2. Return the normalized version string for valid input and `null` for invalid
   input, with the same strict-versus-loose distinction as the public API.
3. Compare two valid versions using SemVer precedence and return exactly `-1`,
   `0`, or `1`; invalid comparisons must have a deterministic typed error.
4. Provide the `semver` command-line program for validating, filtering,
   sorting, and incrementing versions with the documented flags.

The root module must expose the documented operations through `index.js` and
the executable must be `bin/semver.js`. Keep the implementation deterministic
and free of network, filesystem, subprocess, or clock dependencies during
normal library calls. Do not add a server, a network protocol, or a separate
JSON service: the harness may call the library from a child process and project
returned objects to JSON itself.

This specification covers the root operations `parse`, `valid`, and `compare`
and the shipped CLI. The `SemVer`, `Range`, and `Comparator` constructors,
regular-expression tables, package metadata, `preload`, `internal/*`, and
unlisted deep imports are not part of this task contract. They must not be
treated as required behavior merely because the CommonJS layout makes some of
them resolvable.

## Supports

### Runtime And Package Contract

- Language: JavaScript using CommonJS modules (`require` and `module.exports`).
- Runtime: Node.js 22.23.1 in the reviewed task probes. The upstream manifest
  declares compatibility with Node.js `>=10`; implementations must not depend
  on APIs newer than the declared target behavior without a concrete reason.
- Package manager: npm 10.9.8, with a lockfile version 3.
- Package metadata: `package.json` must declare `name: "semver"`, expose
  `index.js` as `main`, and map the `semver` executable to
  `bin/semver.js`. The package license is ISC.
- Runtime dependencies: none. All parsing, comparison, range handling needed
  by the CLI, and formatting must be implemented inside the package.
- Installation command used by the harness:
  `npm ci --offline --ignore-scripts --no-audit --no-fund`.
  Provide a consistent `package-lock.json` so this command does not resolve
  packages from a registry. Do not require lifecycle scripts to install or run
  the documented API.
- Run environment: agent, candidate, verifier, Oracle, and controls operate
  with no network. They must not contact GitHub, npm, a package registry, DNS,
  or any external service. The library must not fetch reference source or
  inspect a host installation.
- Input bound: library and adapter callers pass bounded JavaScript strings for
  version operands. The public JSON projection accepts only an optional
  boolean `loose` field. It does not accept objects, arrays, functions,
  symbols, BigInts, dates, regular expressions, cyclic values, or unbounded
  input as version operands.

### Project Directory Structure

```text
workspace/
├── package.json
├── package-lock.json
├── index.js
├── preload.js
├── bin/
│   └── semver.js
├── classes/
│   ├── comparator.js
│   ├── range.js
│   └── semver.js
├── functions/
│   ├── clean.js
│   ├── cmp.js
│   ├── coerce.js
│   ├── compare-build.js
│   ├── compare-loose.js
│   ├── compare.js
│   ├── diff.js
│   ├── eq.js
│   ├── gt.js
│   ├── gte.js
│   ├── inc.js
│   ├── lt.js
│   ├── lte.js
│   ├── major.js
│   ├── minor.js
│   ├── neq.js
│   ├── parse.js
│   ├── patch.js
│   ├── prerelease.js
│   ├── rcompare.js
│   ├── rsort.js
│   ├── satisfies.js
│   ├── sort.js
│   └── valid.js
├── internal/
│   ├── constants.js
│   ├── debug.js
│   ├── identifiers.js
│   ├── lrucache.js
│   ├── parse-options.js
│   └── re.js
└── ranges/
    ├── gtr.js
    ├── intersects.js
    ├── ltr.js
    ├── max-satisfying.js
    ├── min-satisfying.js
    ├── min-version.js
    ├── outside.js
    ├── simplify.js
    ├── subset.js
    ├── to-comparators.js
    └── valid.js
```

The root import must work from a consumer's project as
`const semver = require('semver')`. The three documented functions must be
available as `semver.parse`, `semver.valid`, and `semver.compare`. The command
must be runnable after installation as `npx semver` or as the installed
`semver` executable. A harness may create a temporary `node_modules/semver`
link and invoke the root import from outside the package directory.

## API Usage Guide

All options in the following direct JavaScript signatures are optional. For
the bounded harness boundary, `loose` is represented by a boolean and no other
option is sent. Returned `SemVer` objects from `parse` are projected to plain
JSON before crossing a process boundary; class identity and methods are not
observable contract data.

### 1. `parse` Function

**Import path:** `require('semver').parse`, implemented by the root
`index.js` export.

**Signature:**

```js
parse(version, options = undefined, throwErrors = false)
```

`version` is normally a string in the bounded public contract. `options` may
be omitted or may contain the supported `loose` boolean; callers using the
direct JavaScript API may also supply `includePrerelease` where range-related
code passes options through, but it does not change version parsing. The
third argument is a boolean. The JSON adapter does not expose
`throwErrors`; it always uses the default false behavior.

On valid input, return a SemVer value with these observable fields:

- `version`: normalized string in `MAJOR.MINOR.PATCH` form, followed by
  `-PRERELEASE` when prerelease identifiers exist;
- `major`, `minor`, and `patch`: non-negative safe integers;
- `prerelease`: an array whose numeric identifiers are numbers and whose
  non-numeric identifiers are strings;
- `build`: an array of build identifier strings.

The normalized `version` field does not include `+build` metadata. The `raw`
field and parsing options may exist on the direct object, but they are not
part of the JSON projection. Parsing has no filesystem, environment, network,
or global-state side effect. Repeated calls with the same input and options
produce equivalent component values.

With the default `throwErrors = false`, invalid input returns `null`.
Non-string values are invalid for this contract and must not be coerced by
`parse`. With `throwErrors = true`, invalid input raises the package's
`TypeError` rather than returning `null`; an implementation may preserve the
native message wording only insofar as the error remains a `TypeError`.

Ordinary example:

```js
const semver = require('semver')
const parsed = semver.parse('1.2.3-beta.2+build.7')
// parsed.version === '1.2.3-beta.2'
// parsed.major === 1; parsed.minor === 2; parsed.patch === 3
// parsed.prerelease is ['beta', 2]; parsed.build is ['build', '7']
```

Edge examples:

```js
semver.parse('1.2') === null
semver.parse('4.2.0foo', {loose: true}).version === '4.2.0-foo'
semver.parse('1.2', undefined, true) // throws TypeError
```

### 2. `valid` Function

**Import path:** `require('semver').valid`.

**Signature:**

```js
valid(version, options = undefined)
```

`version` is a string version candidate. `options` may be omitted or may
contain `loose: true` for the loose grammar. The function returns a string or
`null`, never a mutable parser object. The returned string is the same
normalized `version` value that `parse` reports; build metadata is therefore
not included in the returned string. The function does not mutate its input or
perform I/O and is deterministic for a fixed input and options.

Strictly valid input returns its normalized version. Invalid strings and
non-string values return `null`; the function does not throw for ordinary
invalid validation input because it delegates to non-throwing parsing.

Ordinary example:

```js
const semver = require('semver')
semver.valid('v1.2.3') === '1.2.3'
semver.valid('1.2.3-beta.2+build.7') === '1.2.3-beta.2'
```

Edge examples:

```js
semver.valid('1.2') === null
semver.valid('4.2.0foo', true) === '4.2.0-foo'
semver.valid(123) === null
```

### 3. `compare` Function

**Import path:** `require('semver').compare`.

**Signature:**

```js
compare(a, b, loose = false)
```

`a` and `b` are bounded version strings. `loose` is a boolean selecting the
same loose parsing mode used by `parse` and `valid`. Return exactly one of the
integers `-1`, `0`, or `1`: `-1` means `a` has lower SemVer precedence, `0`
means equal precedence, and `1` means `a` has higher precedence. Comparison
must use numeric major/minor/patch ordering, then prerelease ordering. A
release version has higher precedence than its prerelease. Numeric prerelease
identifiers compare numerically, numeric identifiers precede non-numeric
identifiers, and a longer otherwise-equal prerelease has lower precedence than
the shorter one. Build metadata does not affect ordinary comparison.

The operation is pure and deterministic. It must not sort or mutate caller
data, perform I/O, or change parser state. If either operand is invalid, the
direct API throws `TypeError` rather than returning a sentinel. The JSON-safe
adapter should serialize this as a bounded typed error object if it exposes
errors, but it must keep non-string operands outside the scored request shape.

Ordinary example:

```js
const semver = require('semver')
semver.compare('1.2.3', '1.2.4') === -1
semver.compare('1.2.3-beta.2', '1.2.3') === -1
```

Edge examples:

```js
semver.compare('1.2.3+one', '1.2.3+two') === 0
semver.compare('1.2.3', '1.2.3') === 0
semver.compare('1.2', '1.2.3') // throws TypeError
```

### 4. `semver` Command-Line Interface

**Entry point:** `bin/semver.js`, installed under the executable name
`semver`.

**Invocation shape:**

```text
semver [options] <version> [<version> [...]]
```

The CLI reads only command-line arguments, writes results to stdout and
diagnostics to stderr, and does not access the network. It first discards
invalid versions, applies every supplied range filter, sorts remaining
versions in ascending SemVer precedence, and prints one cleaned version per
line. The process exits `0` when at least one valid version remains and exits
`1` when no valid or satisfying version remains. With no arguments or with a
help flag it prints usage text and exits successfully.

Supported flags and exact argument shapes are:

- `-r`, `--range <range>`: retain versions satisfying the range; repeated
  flags apply all supplied ranges.
- `-i`, `--inc`, `--increment [level]`: increment exactly one version, with
  `patch` as the default level. Valid levels are `major`, `minor`, `patch`,
  `premajor`, `preminor`, `prepatch`, `prerelease`, and `release`.
- `--preid <identifier>`: identifier used for prerelease increments.
- `-l`, `--loose`: use loose parsing for versions and ranges.
- `-p`, `--include-prerelease`: include prerelease versions in range matches.
- `-c`, `--coerce`: coerce a string containing a version-looking component
  before validation; this does not imply loose parsing.
- `--rtl` and `--ltr`: choose right-to-left or left-to-right coercion;
  left-to-right is the default.
- `-n <base>`: use prerelease base `0`, `1`, or `false` to omit a base number.
- `-v`, `--version <version>`: add a version operand (the same as supplying a
  positional version).
- `-rv`, `-rev`, `--rev`, `--reverse`: print valid versions in descending
  order.
- `-h`, `--help`, `-?`: print help and stop.

An increment operation cannot be combined with a range and requires exactly
one version. An invalid increment level, missing flag argument, or invalid
combination is an error and must exit nonzero. An ordinary invocation is:

```sh
semver 1.2.4 1.2.3 1.2.3-beta.1
# 1.2.3-beta.1
# 1.2.3
# 1.2.4
```

Boundary invocations are:

```sh
semver --range '^1.2.0' 0.9.0 1.2.1 2.0.0
# 1.2.1
semver --inc minor 1.2.3
# 1.3.0
semver 1.2
# no version output; exit status 1
```

The CLI is a public compatibility surface, but its output is textual and is
separate from the bounded JSON projection used for direct API verification.

## Implementation Notes

1. Keep strict parsing, loose parsing, normalization, and precedence rules
   consistent across `parse`, `valid`, `compare`, and every CLI path. Do not
   implement comparison by lexicographic string order. The same input/options
   pair must have the same result across repeated processes.
2. Preserve the distinction between prerelease and build metadata. Prerelease
   identifiers participate in precedence; build identifiers are retained by
   parsing but do not change `compare` results. Parsed numeric prerelease
   components must remain numbers in the object projection rather than being
   stringified.
3. Keep error behavior observable and bounded. Validation returns `null` for
   invalid input, `parse(..., true)` and `compare` raise `TypeError` for
   invalid versions, and the CLI uses a nonzero exit status when it has no
   usable result. Do not print stack traces or ambient object serialization as
   the library result.
4. The package must work when loaded through a temporary `node_modules/semver`
   link and when invoked from a different current working directory. Root
   resolution must not depend on the repository's absolute path. Normal API
   calls must not write files, read environment variables, spawn processes, or
   make network requests.
5. The narrow JSON-safe child-process boundary, when used by a harness, has
   these request/result shapes. The adapter accepts bounded strings and an
   optional boolean `loose`; `parse` returns `null` or a plain object with
   `version`, integer `major`/`minor`/`patch`, and arrays `prerelease` and
   `build`; `valid` returns a normalized string or `null`; and `compare`
   returns `-1`, `0`, or `1`. A typed failure may be represented as
   `{ "error": { "name": "TypeError", "message": "..." } }`.

Small behavior examples that should remain verifiable without prescribing an
implementation algorithm:

```js
const semver = require('semver')

const parsed = semver.parse('1.2.3-beta.2+build.7')
console.log({
  version: parsed.version,
  major: parsed.major,
  minor: parsed.minor,
  patch: parsed.patch,
  prerelease: parsed.prerelease,
  build: parsed.build,
})
// {version: '1.2.3-beta.2', major: 1, minor: 2, patch: 3,
//  prerelease: ['beta', 2], build: ['build', '7']}
```

```js
const semver = require('semver')
console.log(semver.valid('1.2'))       // null
console.log(semver.valid('v1.2.3'))    // '1.2.3'
console.log(semver.compare('1.2.3+left', '1.2.3+right')) // 0
```

```sh
semver --reverse 1.0.0 2.0.0 1.5.0
# 2.0.0
# 1.5.0
# 1.0.0
```

This document is a single-task implementation specification for `semver`. It
does not assert that the currently blocked source record has passed package
closure, Oracle, controls, scoring, or publication gates.
