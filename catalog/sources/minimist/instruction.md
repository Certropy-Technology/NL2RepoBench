# Build `minimist`

## Project Description

Create the `minimist` project from an empty workspace. This is a repository-generation task for the frozen `node` package contract, task specification version `2.0.0`, at source revision `ecfdaea23e7931c0d529c52b743c711c3278a8ce`. Implement the public behavior described by the local inventories and the task-specific detail below; do not copy upstream source or tests. The supported scope is node, npm, commonjs, argv, parser, repository-generation.

## Natural Language Instruction

Starting with an empty `workspace/`, create an installable `minimist` project. Implement every public/core API named in the API Usage Guide, its package exports, and its documented integration points. Preserve observable input types, return shapes, ordering, determinism, state changes, and documented exception behavior. The project must be usable through its declared `minimist` import path (or the package root for this Node task), and all required modules must be present in the directory structure below.

The task-specific specification retained below supplies the detailed behavior for each API family. Treat it as the contract: do not add unrelated APIs, replace deterministic behavior with randomized or time-dependent behavior, or weaken error handling.

## Supports

- Language/runtime: `node` on `24.19.0`; target environment metadata declares `debian-bookworm`.
- Distribution/package: `minimist`; import/root name: `minimist`. Package manager: `npm`.
- Install from the repository root with `npm ci --offline --ignore-scripts --no-audit --no-fund`. Build metadata must be complete and agree with the package entry point.
- Dependency status in the frozen source metadata is `known`. Use only dependencies declared by the task and available in the preinstalled build image; standard-library modules are not third-party runtime dependencies.
- NoNetwork boundary: agent, candidate, verifier, Oracle, and controls run with `network_mode=no-network`. Do not access GitHub, PyPI, npm registries, Go proxy, DNS, or external services at runtime. Do not fetch source or dependencies during implementation or package use.

## Project Directory Structure

```text
workspace/
├── package.json
├── package-lock.json
├── index.js
├── index.d.ts
└── README.md
```

The tree is the minimum public project layout. Add a module only when it corresponds to a documented import path or package resource. Do not place publicly unavailable evaluator code, non-public evaluation material, Oracle payloads, dependency caches, or trusted reports in this workspace.

## API Usage Guide

The public/core API families recorded in the local inventory are: Package root, Long flags and values, Short flags, Option declarations, Dotted names and trailing arguments.

For each listed family, the detailed contract below defines the import path or CLI entry, signature, accepted inputs, return type/shape, ordering and determinism, state or I/O side effects, errors, and examples. Implement the complete public surface, including root re-exports and aliases where the specification names them. If an API is stateful, preserve mutation and repeated-call behavior; if it is pure, do not introduce global state.

## Implementation Notes

Keep the implementation self-contained and deterministic under the declared runtime. The candidate repository must install from the workspace root, import through the documented public path, and run without external services. Preserve package metadata, module semantics (ESM/CommonJS or Python import behavior), serialization formats, resource cleanup, and boundary behavior described below. publicly unavailable evaluator adapters and non-public evaluation details are not part of the implementation.

## Examples

Ordinary project examples:

```bash
cd workspace
npm ci --offline --ignore-scripts --no-audit --no-fund
```

```js
import pkg from 'minimist';
// Use the documented public exports from pkg.
```

The retained task-specific examples below provide ordinary API calls and combinations grounded in the frozen inventory. Keep their result shapes and ordering exact.

## Error Handling and Boundary Conditions

- Empty inputs, malformed values, missing resources, duplicate values, and unsupported options must follow the task-specific error contracts below; do not silently coerce or discard information unless explicitly specified.
- Repeated calls must remain deterministic. Filesystem, process, clock, random, native, callback, and serialization boundaries are supported only where the local specification documents them.
- Network attempts are prohibited and must not be used as a fallback. Installation failures, missing offline dependencies, or unsupported external capabilities are environment/source concerns, not reasons to invent behavior.


## Source-derived task detail

# Build `minimist`

## Project Description

Create a complete installable npm package named `minimist` from an empty
workspace. It is a CommonJS command-line argument parser: the package root
exports one function that accepts an array of argument strings and an optional
options object, then returns a plain JavaScript object describing flags and
positional arguments.

This is a repository-generation task. Implement the documented behavior in
your own package; do not depend on a downloaded copy of the pinned project or
on a command-line parser dependency.

## Supports

- Run on Node `24.19.0` with npm `11.17.0` on `linux/amd64`.
- Use CommonJS package semantics. `require('minimist')` must return the parser
  function, and `package.json` must expose it through its normal package root.
- Include a committed `package-lock.json` using `lockfileVersion: 3`. The
  verifier installs with `npm ci --offline --ignore-scripts --no-audit --no-fund`.
- Do not declare runtime dependencies, native addons, workspaces, custom
  loaders, registry configuration, or lifecycle scripts. The package must not
  require network access during installation or use.
- The function receives only JSON-compatible option objects. Callback-valued
  `unknown` handlers, symbols, custom prototypes, mutation of global
  prototypes, and process argv/environment parsing are outside this task.

## API Usage Guide

### Package root

**Import path:** `require('minimist')`.

**Signature:**

```js
const parse = require('minimist');
const result = parse(args, options?);
```

`args` is an array of strings. `options`, when present, is a plain object that
may contain `boolean`, `string`, `alias`, `default`, `stopEarly`, and `--`.
The return value is a plain object whose `_` property is always an array of
positionals. Property insertion order is not part of the contract.

### Long flags and values

- `--name value` and `--name=value` set `name`. A following non-flag token is
  consumed as the value unless the flag is known boolean.
- `--name` without a value is `true`; `--no-name` is `false`.
- Repeating a non-boolean key preserves values in encounter order: the second
  value changes a scalar into an array, and later values append to that array.
- Numeric-looking values become numbers, including decimal, signed decimal,
  scientific notation, and hexadecimal. Other values remain strings.
- Positional tokens are appended to `_`; numeric-looking positionals use the
  same number conversion unless `_` is listed as a string option.

```js
parse(['--port=8080', '--tag', 'a', '--tag', 'b', 'file'])
// {_: ['file'], port: 8080, tag: ['a', 'b']}
```

### Short flags

- A one-letter flag such as `-v` follows the same capture rules as a long
  flag.
- Combined short letters such as `-abc` set `a` and `b` to `true` and treat
  the final letter as the value-taking flag when a suitable following token
  exists.
- A short option may carry its final value directly: `-n123` means `n: 123`,
  `-s=value` means `s: 'value'`, and `-I/path` means `I: '/path'`.

### Option declarations

`boolean` and `string` may each be a name or an array of names.

- A declared boolean is initialized before parsing: it is its declared default
  when present in `default`, otherwise `false`. It consumes literal following
  `true` or `false` as a Boolean and otherwise leaves a following token in
  `_`.
- `boolean: true` treats all long flags without `=` as booleans.
- A declared string never undergoes numeric conversion. A string flag without
  a value is the empty string.
- `alias` maps a name to one name or an array of equivalent names. Every write
  and default is reflected through every alias. String declarations apply to
  aliases too.
- `default` supplies a value only if the corresponding key was not set while
  parsing. Default and alias names may contain dots.

```js
parse(['-v', '42'], {
  alias: {verbose: 'v'},
  string: 'verbose',
  default: {color: false},
})
// {_: [], v: '42', verbose: '42', color: false}
```

### Dotted names and trailing arguments

Flag names and declared defaults/aliases may use dots to create nested plain
objects. For example, `--db.port 5432` creates `{db: {port: 5432}}`.

`--` terminates flag parsing. With ordinary options, the remaining tokens are
appended to `_` unchanged as strings. With `{ '--': true }`, they are preserved
unchanged in a separate `--` array. With `{stopEarly: true}`, the first
positional and every remaining token are appended to `_` unchanged as strings.

Names containing `__proto__` or a `constructor.prototype` path must not modify
`Object.prototype`, function prototypes, or primitive prototypes. Such writes
are ignored.

## Implementation Notes

- Input ordering is deterministic and repeated values retain encounter order.
- Return only JSON-compatible values for the supported inputs. No terminal,
  browser, filesystem, clock, random source, network, or ambient `process.argv`
  behavior is needed.
- The verifier invokes the package through a child Node process with one
  JSON-compatible request at a time. It does not require you to provide a CLI.
- The scored slice covers package installation, long and short flags, numeric
  coercion, declared string/boolean behavior, aliases/defaults, dotted keys,
  trailing arguments, stop-early parsing, repeated flags, and prototype-pollution
  resistance. Callback-valued `unknown` filtering is intentionally not scored.
