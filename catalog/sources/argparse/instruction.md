# Project Description

Create a complete installable npm package named `argparse`, version `3.0.1`,
from an empty workspace. The package is a CommonJS port of Python's
`argparse` API. The implementation must expose the documented parser classes,
actions, formatters, namespace type, and parsing constants from the package
root.

# Natural Language Instruction

Create the `argparse` project from an empty `workspace/`. Build an installable implementation, not a loose demonstration script. The public API guide below is the complete source of the task contract; preserve its import paths, signatures, return shapes, ordering, state changes, and exceptions.

Required capabilities:
- CommonJS parser construction: implement the documented public behavior and preserve its input/output and error contract.
- typed positional and optional arguments: implement the documented public behavior and preserve its input/output and error contract.
- actions, groups, and subparsers: implement the documented public behavior and preserve its input/output and error contract.
- help, namespace, and parser-error behavior: implement the documented public behavior and preserve its input/output and error contract.

Do not copy an upstream checkout or tests. Keep behavior deterministic and local, and make the package usable from the installation layout described below. The principal public entry points include: `add_argument(name, ...namesAndOptions)`, `parse_args(args?, namespace?)`, `add_argument_group(options?)`, `add_mutually_exclusive_group(options?)`.

# Supports

- Node `24.19.0`, npm `11.17.0`, `linux/amd64`, and glibc.
- `package.json` must identify the package as `argparse` version `3.0.1`, use
  `main: "lib/argparse.js"`, and declare the PSF-2.0 license.
- A committed npm v3 lockfile must allow `npm ci --offline --ignore-scripts
  --no-audit --no-fund` and `npm pack --ignore-scripts` in a clean offline
  environment without lifecycle scripts.

- The package must be self-contained. Do not use runtime dependencies,
  workspaces, native addons, custom loaders, network access, runtime
  downloads, or lifecycle hooks.
- The packed package must contain the runtime JavaScript and its TypeScript
  declaration file under `lib/`; source tests and development-only files need
  not be packaged.


## NoNetwork boundary

Agent, candidate, verifier, Oracle, controls, and normal runtime execution are network-isolated. Do not access GitHub, package registries, Go proxies, DNS, or external services during execution; use only the frozen local build inputs.

# Project Directory Structure

```text
workspace/
├── package.json
├── package-lock.json
└── lib/
    ├── argparse.js
    ├── argparse.d.ts
    ├── action/
    ├── argument_parser.js
    ├── namespace.js
    └── help/
```

# API Usage Guide

Import the CommonJS package with:

```js
const argparse = require('argparse');
const {ArgumentParser} = argparse;
```

The package root returns a plain object with these named exports:
`ArgumentParser`, `ArgumentError`, `ArgumentTypeError`, `BooleanOptionalAction`,
`FileType`, `HelpFormatter`, `ArgumentDefaultsHelpFormatter`,
`RawDescriptionHelpFormatter`, `RawTextHelpFormatter`,
`MetavarTypeHelpFormatter`, `Namespace`, `Action`, and the constants
`ONE_OR_MORE`, `OPTIONAL`, `PARSER`, `REMAINDER`, `SUPPRESS`, and
`ZERO_OR_MORE`.

## ArgumentParser

`new ArgumentParser(options?)` constructs a parser. The options object accepts
the documented parser settings including `prog`, `description`, `epilog`,
`usage`, `add_help`, `exit_on_error`, `formatter_class`, `argument_default`,
`allow_abbrev`, `prefix_chars`, and `fromfile_prefix_chars`. The default parser
uses `process.argv.slice(2)` when no argument array is supplied.

`add_argument(name, ...namesAndOptions)` declares one positional or one or
more option strings and returns an `Action` object. Its final object can use
`dest`, `type`, `action`, `nargs`, `const`, `default`, `required`, `help`,
`metavar`, and `choices`. Supported
standard actions include `store`, `store_const`, `store_true`, `store_false`,
`append`, `append_const`, `count`, `help`, and `version`. The `type` value may
be a callable or the built-in names `int`, `float`, `str`, and `FileType` where
the corresponding public behavior is documented by the declaration file.

`parse_args(args?, namespace?)` returns a `Namespace`-compatible object whose
own enumerable fields contain parsed values. `parse_known_args` returns a
two-element array `[namespace, unknownArguments]`. The `parse_intermixed_args`
and `parse_known_intermixed_args` variants preserve positional/optional
intermixing where supported. Positional values retain order; `nargs` values
use arrays, and repeated `append`/`count` actions accumulate deterministically.

`add_argument_group(options?)` and `add_mutually_exclusive_group(options?)`
return containers with the same `add_argument` method. A mutually exclusive
group rejects more than one selected member. `set_defaults(options)` adds
parser defaults and `get_default(dest)` reads one effective default.

`add_subparsers(options?)` returns a subparser action. Its `add_parser(name,
options?)` method creates a child parser. A selected child parser handles its
own options and can store the selected name in the configured `dest`.

`format_usage()` and `format_help()` return deterministic strings. `print_usage`
and `print_help` write the same strings to a supplied object with `write()`.
`error(message)` and `exit(status?, message?)` use the parser's configured
error behavior. With `exit_on_error: false`, malformed input raises an
ordinary `ArgumentError` or related `Error` instead of terminating the process.

## Public helper types

`new Namespace(options?)` creates a namespace populated from an object.
`new FileType(options?)` or `new FileType(flags, encoding?, mode?)` creates a
callable file-opening converter. `Action` and the formatter classes are
constructible public classes used by advanced callers. The exported parsing
constants are the exact strings shown in the declaration file.

# Implementation Notes

Keep the package deterministic under `TERM=dumb`, `CI=true`, `FORCE_COLOR=0`,
and the English locale. Preserve Unicode strings, option order, positional
order, default values, and informative parser errors. Candidate dependencies
must remain empty and the package must install from the supplied offline npm
v3 closure.

The verifier exercises a fixed JSON-compatible subset through a separate
bounded child process. It covers package identity and exports, scalar and
typed parsing, aliases and defaults, `nargs`, append/count/boolean actions,
choices and required arguments, groups and subparsers, help formatting,
unknown arguments, namespace input, parser constants, and deterministic
repeated calls. Callbacks, file descriptors, process termination, arbitrary
filesystem paths, custom prototypes, external argument files, and locale or
TTY behavior are outside the fixed scored subset.

# Examples

## Ordinary parsing

```javascript
const {ArgumentParser} = require('argparse')
const parser = new ArgumentParser({prog: 'tool'})
parser.add_argument('--count', {type: 'int', default: 1})
const args = parser.parse_args(['--count', '3'])
```

## Ordinary subparser

```javascript
const commands = parser.add_subparsers({dest: 'command'})
commands.add_parser('run').add_argument('file')
```

## Boundary: required option

```javascript
const strict = new ArgumentParser({exit_on_error: false})
strict.add_argument('--name', {required: true})
strict.parse_args([]) // throws an argument error
```

## Boundary: invalid choice

```javascript
parser.add_argument('--mode', {choices: ['fast', 'full']})
parser.parse_args(['--mode', 'other']) // rejected
```

# Error Handling and Boundary Conditions

Reject invalid inputs using the documented exception or error result. Preserve empty-input behavior, ordering, Unicode/encoding behavior, cancellation or timeout semantics, and local filesystem boundaries where the API specifies them. Never turn a failed local operation into a network request, subprocess, or silent success.
