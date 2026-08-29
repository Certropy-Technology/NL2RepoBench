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
