# Build `meow`

## Project Description

Create the `meow` project from an empty workspace. This is a repository-generation task for the frozen `node` package contract, task specification version `1.0.0`, at source revision `1f3ec6cfd29a2df43ad637023be57001db49c410`. Implement the public behavior described by the local inventories and the task-specific detail below; do not copy upstream source or tests. The supported scope is node, npm, esm, cli, argument-parser, flags, commands, help.

## Natural Language Instruction

Starting with an empty `workspace/`, create an installable `meow` project. Implement every public/core API named in the API Usage Guide, its package exports, and its documented integration points. Preserve observable input types, return shapes, ordering, determinism, state changes, and documented exception behavior. The project must be usable through its declared `meow` import path (or the package root for this Node task), and all required modules must be present in the directory structure below.

The task-specific specification retained below supplies the detailed behavior for each API family. Treat it as the contract: do not add unrelated APIs, replace deterministic behavior with randomized or time-dependent behavior, or weaken error handling.

## Supports

- Language/runtime: `node` on `24.19.0`; target environment metadata declares `debian-bookworm`.
- Distribution/package: `meow`; import/root name: `meow`. Package manager: `npm`.
- Install from the repository root with `npm ci --offline --ignore-scripts --no-audit --no-fund`. Build metadata must be complete and agree with the package entry point.
- Dependency status in the frozen source metadata is `known`. Use only dependencies declared by the task and available in the preinstalled build image; standard-library modules are not third-party runtime dependencies.
- NoNetwork boundary: agent, candidate, verifier, Oracle, and controls run with `network_mode=no-network`. Do not access GitHub, PyPI, npm registries, Go proxy, DNS, or external services at runtime. Do not fetch source or dependencies during implementation or package use.

## Project Directory Structure

```text
workspace/
├── package.json
├── package-lock.json
├── build/index.js
├── index.d.ts
└── README.md
```

The tree is the minimum public project layout. Add a module only when it corresponds to a documented import path or package resource. Do not place publicly unavailable evaluator code, non-public evaluation material, Oracle payloads, dependency caches, or trusted reports in this workspace.

## API Usage Guide

The public/core API families recorded in the local inventory are: Parsing and help examples.

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
import pkg from 'meow';
// Use the documented public exports from pkg.
```

The retained task-specific examples below provide ordinary API calls and combinations grounded in the frozen inventory. Keep their result shapes and ordering exact.

## Error Handling and Boundary Conditions

- Empty inputs, malformed values, missing resources, duplicate values, and unsupported options must follow the task-specific error contracts below; do not silently coerce or discard information unless explicitly specified.
- Repeated calls must remain deterministic. Filesystem, process, clock, random, native, callback, and serialization boundaries are supported only where the local specification documents them.
- Network attempts are prohibited and must not be used as a fallback. Installation failures, missing offline dependencies, or unsupported external capabilities are environment/source concerns, not reasons to invent behavior.


## Source-derived task detail

# Project Description

Implement the `meow` package at the frozen revision as a small ESM command-line application helper. The package must expose the default `meow` function from its package root and be installable with npm in the supplied offline environment.

# Supports

Implement the deterministic JSON-safe portion of the public API:

- `meow(helpText, options)` and `meow(options)` as the default ESM export.
- `options.importMeta` must be accepted as an object containing a valid `url` string.
- Flag declarations with `type` (`string`, `boolean`, or `number`), `default`, `shortFlag`, `aliases`, `isMultiple`, `choices`, and boolean or static `isRequired` values.
- Input declarations using `string`, `number`, `boolean`, `array`, `string-array`, `number-array`, or `boolean-array`, including static `isRequired`.
- Camel-case flag keys matching kebab-case command-line arguments, `inferType`, `booleanDefault`, `allowUnknownFlags`, `description`, `help`, `version`, `autoHelp`, `autoVersion`, `pkg`, `argv`, and `helpIndent`.
- Command lists with a command returned separately from the remaining positional input.
- The returned JSON-observable fields `input`, `command`, `flags`, `unnormalizedFlags`, `pkg`, and `help`.

The result also contains callable `showHelp` and `showVersion` methods. They must exist and use the documented exit behavior, but those process-exit callbacks are outside the JSON subprocess contract and are not scored here.

# API Usage Guide

The package root is ESM and the default export is callable:

```js
import meow from 'meow';

const cli = meow('Usage\n  $ demo <input>', {
  importMeta: import.meta,
  argv: ['hello', '--loud'],
  flags: {loud: {type: 'boolean'}}
});
```

`meow(helpText, options)` uses the first string as help text. `meow(options)` is the options-only form. `argv` defaults to `process.argv.slice(2)` but should be honored when supplied. `flags` is keyed in camelCase, while command-line names are normally kebab-case. The returned `flags` removes aliases and camel-case aliases; `unnormalizedFlags` retains parser spellings.

String flags consume a value, boolean flags support `--no-name`, number flags parse numeric values, and `isMultiple` returns an array. `choices` rejects values outside its declared set. `input` describes positional argument conversion and `commands` stops parsing at the first non-option token and returns it as `command` when it is allowed.

The help result begins with a newline. A description is included unless `description: false`; multi-line help is trimmed and reindented by `helpIndent` (default `2`). The package metadata is used for default `description` and `version` when `pkg` is supplied or discovered.

Invalid option shapes and invalid flag values must raise an error. Unknown flags are accepted by default and are rejected when `allowUnknownFlags: false`. Required flags or input use the documented exit path; the static required cases are represented in the task through their observable validation boundary.

# Implementation Notes

Use Node 24 ESM and npm 11. The package must produce its runtime under `build/` and publish an ESM export map with `types` and `default` entries. Build dependencies are installed only during image construction from the private npm lock/cache artifact. The evaluation Agent and separate verifier have no network access and must not run `npm install`, `npm ci`, `git clone`, `curl`, or `wget`.

Keep the implementation self-contained in the candidate workspace. Do not fetch the frozen reference source or rely on development-only test runners. Preserve deterministic ordering and JSON-safe return values for the supported contract. Cycles, callbacks, arbitrary functions, native addons, browser/Deno shims, and process/TTY-specific behavior are intentionally out of scope.

### Parsing and help examples

```js
const parsed = meow('Usage\n  $ demo [name]', {
  importMeta: import.meta,
  argv: ['Ada', '--count=2'],
  flags: {count: {type: 'number'}}
})

parsed.input       // ['Ada']
parsed.flags.count // 2
```

```js
const parsed = meow({
  importMeta: import.meta,
  argv: ['build', '--no-color'],
  commands: {build: {}},
  flags: {color: {type: 'boolean', default: true}}
})

parsed.command     // 'build'
parsed.flags.color // false
```

An empty `argv` produces empty positional input and applies declared defaults.
A number flag with a nonnumeric value, a value outside `choices`, or a required
flag that is absent follows the documented validation/error path. Help and
version output must be derived from supplied options/package metadata and must
not inspect a remote package registry.
