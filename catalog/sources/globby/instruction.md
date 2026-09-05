# Project Description

Build an installable Node.js package named `globby` from an empty workspace.
It is an ESM filesystem globbing utility: callers provide one or more
forward-slash glob patterns and receive matching paths relative to a search
directory. The package must work without a network service or native addon.

## Natural Language Instruction

Create the installable `globby` package from an empty workspace. Implement the
asynchronous and synchronous glob APIs, normalized task generation, dynamic
pattern detection, literal path escaping, directory expansion, negation, and
ignore-file behavior in the JSON-compatible contract below. Preserve relative
path ordering and parity between async and sync calls. The implementation must
perform only local filesystem reads and return deterministic results for a
fixed directory tree.

# Supports

- Node.js 24.19.0 on Linux and npm 11.17.0.
- An ESM package whose package root is named `globby` and exports the public
  functions described below.
- Offline installation with a v3 `package-lock.json`; lifecycle scripts must
  not be required for installation or use.
- Ordinary files and directories, dotfiles when requested, negated patterns,
  directory expansion, and ignore-file filtering.

## Project Directory Structure

```text
workspace/
├── package.json
├── package-lock.json
├── index.js
└── index.d.ts
```

The package root exports the documented ESM functions from `index.js`; the
declaration file describes Promise and synchronous return types. The package
does not require a CLI, lifecycle hook, native addon, generated cache, or
runtime service. Files matched by a caller's `cwd` are external input and are
never copied into the package.

# API Usage Guide

The scored calls cross a JSON request/response boundary. Therefore `patterns`
and options must be representable as JSON; use string paths for `cwd` rather
than `URL` objects, and do not rely on custom filesystem objects in the scored
surface.

## `globby(patterns, options?)`

Import the default function with `import globby from 'globby'`.

Returns a `Promise<string[]>` of paths relative to `options.cwd` (or the
process working directory). `patterns` is a string or an array of strings and
must reject non-string entries with a `TypeError` whose message explains that
patterns must be strings. Support the usual forward-slash glob syntax,
including `*`, `?`, `**`, brace expressions, and `!` negations. Duplicate
patterns should not create duplicate result paths.

By default, existing directory patterns are expanded to files below the
directory and only files are returned. `expandDirectories: false` disables
that convenience; with `onlyFiles: false`, a matched directory may be
returned. `expandDirectories` may also be an array of file names or an object
with `files` and `extensions` to restrict the expansion.

Support the relevant JSON-compatible filesystem options used by this task:

- `cwd`: an existing directory path; passing a regular file must reject with
  an error identifying that `cwd` must be a directory;
- `dot`: include dotfiles when true;
- `onlyFiles`: include directories when false;
- `ignore`: a string or array of result patterns to exclude;
- `ignoreFiles`: a string or array of ignore-file patterns to read before
  filtering results; ignore-file syntax follows Git-style rules; and
- `expandNegationOnlyPatterns`: when true or omitted, a patterns array made
  only of negations behaves as if it had a leading `**/*`; when false, such an
  input returns an empty array.

Results must reflect the filesystem at call time and must not include paths
excluded by the active patterns or ignore files.

## `globbySync(patterns, options?)`

Import `globbySync` with `import {globbySync} from 'globby'`.

Synchronous counterpart of `globby`. It accepts the same patterns and
JSON-compatible options and returns the same path set and filtering behavior.

## `generateGlobTasks(patterns, options?)`

Returns a `Promise<object[]>` of normalized tasks. Each task has a
`patterns: string[]` array and an `options` object suitable for a compatible
glob engine. Negation handling must be reflected in the task patterns and/or
the task's `options.ignore` list, and directory expansion defaults must be
applied consistently with `globby`.

## `generateGlobTasksSync(patterns, options?)`

Synchronous counterpart of `generateGlobTasks`, returning the same normalized
task structure for the same inputs.

## `isDynamicPattern(patterns, options?)`

Returns a boolean indicating whether any supplied pattern contains glob
metacharacters. Literal paths such as `README.md` are not dynamic; wildcard
patterns such as `src/**/*.js` are dynamic.

## `convertPathToPattern(path)`

Import it with `import {convertPathToPattern} from 'globby'`.

Returns a safe glob pattern for a literal path. Escape glob metacharacters
such as brackets and parentheses so that the returned pattern matches the
literal path rather than interpreting those characters as pattern syntax.

# Implementation Notes

Keep the package ESM-compatible and expose the functions from the package
root. Preserve relative-path behavior, negation ordering, directory
expansion, ignore-file semantics, synchronous/asynchronous parity, and
deterministic error handling. The package should include usable TypeScript
declarations for the public functions, but the scored runtime boundary does
not require TypeScript compilation.

The upstream project also exposes stream-returning and predicate-returning
helpers. Those values cannot be serialized through the fixed JSON candidate
boundary used by this task, so they are not part of the scored denominator;
do not replace the serializable APIs above with a narrower toy implementation.
Do not add a network dependency, native addon, runtime download, arbitrary
shell command, or lifecycle hook.

## Examples

```js
import globby from 'globby';
await globby('src/**/*.js', {cwd: 'workspace'});
// ['src/index.js', 'src/util.js'] in deterministic glob order
```

```js
import {globbySync} from 'globby';
globbySync(['**/*.js', '!**/*.test.js'], {cwd: 'workspace'});
// JavaScript files excluding test files
```

```js
import {generateGlobTasks, convertPathToPattern} from 'globby';
await generateGlobTasks(['lib', '!lib/vendor/**'], {cwd: 'workspace'});
convertPathToPattern('docs/[draft].md');
```

## Error Handling and Boundary Conditions

An empty pattern list returns an empty result. Patterns made only of negations
follow `expandNegationOnlyPatterns` exactly as documented, and duplicate
matches are removed without changing deterministic ordering. Dotfiles are
excluded unless `dot` is true; ignored paths are removed after pattern
matching. `cwd` must identify a directory, and non-string pattern entries
reject with `TypeError`. Async and sync APIs report equivalent errors for the
same invalid local input and never fall back to registry or network access.
