## Project Description

Create a distributable npm package named `eslint` at version `10.9.0`. The
package implements a deterministic, flat-config JavaScript linting API that is
compatible with the public ESLint surface described below. It must parse modern
JavaScript, return ordered diagnostics with source locations, apply selected
autofixes, expose source-code helpers, and provide the documented config helper
subpath.

The evaluator installs the package with `npm ci --offline --ignore-scripts`,
packs it, and installs that tarball into an isolated consumer before testing.
Do not depend on network access, lifecycle scripts, globally installed modules,
or paths outside the installed package.

## Natural Language Instruction

Create the CommonJS `eslint` package from an empty workspace. Implement the
public `Linter`, `ESLint`, `SourceCode`, config, result, parser, and helper
surfaces below, preserving diagnostics, locations, fixes, and export shape.

## Supports or Environment Configuration

- Use Node.js 24.19.0 and npm 11.17.0 on Linux amd64 with the exact package
  version, exports, and v3 lockfile in `task.toml`.
- Install the frozen dependency closure offline with lifecycle scripts disabled;
  no global modules, reference checkout, or runtime network access.
- Agent, candidate, verifier, Oracle, and controls run with no network access.

## Project Directory Structure

```text
workspace/
├── package.json
├── package-lock.json
├── index.js
└── lib/
    ├── api.js
    ├── linter/linter.js
    └── source-code/source-code.js
```

## API Usage Guide

**Import paths:** load the main CommonJS API with `require("eslint")`, the
flat-config helpers with `require("eslint/config")`, and the risk-scoped map
with `require("eslint/use-at-your-own-risk")`. These are package subpaths,
not filesystem paths, and must work after a clean `npm pack` installation.
For source-level module terminology, `import eslint` refers to the package
name only; the scored loader remains CommonJS `require("eslint")`.

The API Usage Guide below is authoritative for every public class, method,
configuration shape, parser option, result field, and error.

## Implementation Notes

Keep diagnostics deterministic for identical input. Autofix must preserve the
documented output and remaining-message behavior.

## Examples

```js
const {Linter} = require('eslint');
const linter = new Linter();
linter.verify('const x = 1;', {languageOptions: {ecmaVersion: 2022}});
```

```js
linter.verifyAndFix('var x = 1;', config);
```

## Error Handling and Boundary Conditions

```js
linter.verify('', config, {filename: 'input.js'});
```

```js
linter.verify('let =', config); // structured parse diagnostic
```

## Supports

- Node.js 24.19.0 and npm 11.17.0 on Linux amd64 with glibc.
- A regular CommonJS npm package with a v3 `package-lock.json`.
- Loading the main entry with `require("eslint")` and the documented subpaths
  with `require("eslint/config")` and
  `require("eslint/use-at-your-own-risk")`.
- Flat config arrays, ECMAScript 2024 syntax, deterministic diagnostic ordering,
  and JSON-serializable results for the tested calls.
- Offline installation with lifecycle scripts disabled. A frozen npm cache
  contains the exact runtime dependency closure of ESLint 10.9.0; an
  implementation may instead use no external runtime dependencies.

The frozen direct dependency versions available to the verifier are:
`@eslint-community/eslint-utils@4.10.1`,
`@eslint-community/regexpp@4.12.2`, `@eslint/config-array@0.23.5`,
`@eslint/config-helpers@0.7.0`, `@eslint/core@1.2.1`,
`@eslint/plugin-kit@0.7.2`, `@humanfs/node@0.16.8`,
`@humanwhocodes/module-importer@1.0.1`, `@humanwhocodes/retry@0.4.3`,
`@types/estree@1.0.9`, `ajv@6.15.0`, `cross-spawn@7.0.6`,
`debug@4.4.3`, `escape-string-regexp@4.0.0`, `eslint-scope@9.1.2`,
`eslint-visitor-keys@5.0.1`, `espree@11.2.0`, `esquery@1.7.0`,
`esutils@2.0.3`, `fast-deep-equal@3.1.3`, `file-entry-cache@8.0.0`,
`find-up@5.0.0`, `glob-parent@6.0.2`, `ignore@5.3.2`,
`imurmurhash@0.1.4`, `is-glob@4.0.3`,
`json-stable-stringify-without-jsonify@1.0.1`, `minimatch@10.2.6`,
`natural-compare@1.4.0`, and `optionator@0.9.4`.

# API Usage Guide

## Main package exports

`require("eslint")` must return an object with exactly these callable exports:
`ESLint`, `Linter`, `RuleTester`, `SourceCode`, and `loadESLint`.
`ESLint.version` and `Linter.version` are the string `"10.9.0"`.
`loadESLint(): Promise<typeof ESLint>` resolves to the same `ESLint`
constructor exported by the package.

`RuleTester` must be a constructible function. Full test-framework integration
for `RuleTester.run` is outside this task's measured slice.

## `new Linter(options?)`

Support the constructor shape
`new Linter(options?: { cwd?: string, configType?: "flat" })` and the following
methods.

### `linter.verify(code, config, filenameOrOptions?)`

Accept source text, a flat config object or array, and either a filename string
or lint-options object. Return an array of diagnostics in source order. Each
diagnostic includes `ruleId`, numeric `severity` (`1` warning, `2` error),
`message`, one-based `line` and `column`, and, when the rule supplies them,
`endLine`, `endColumn`, and `messageId`.

Support these flat-config fields and built-in rules:

- `languageOptions.ecmaVersion`, including the numeric value `2024`;
- `languageOptions.globals`, where `"readonly"` names are treated as defined;
- `linterOptions.reportUnusedDisableDirectives` with warning or error severity;
- rule severities expressed as `"off"`, `"warn"`, `"error"`, or numbers;
- `eqeqeq`, `no-unused-vars`, `no-undef`, and `no-alert`;
- `quotes` with the `"single"` option and `semi` with the `"always"` option for
  autofixing.

Modern optional chaining and nullish coalescing must parse under ECMAScript
2024. Invalid source returns a single parsing diagnostic with `ruleId: null`.
For example, `const = 1;` reports `Parsing error: Unexpected token =` at line 1,
column 7.

Rule diagnostics must follow ESLint 10.9.0 wording and locations. For example,
`value == 42` under `eqeqeq: "error"` reports
`Expected '===' and instead saw '=='.` with `messageId: "unexpected"` over the
two-character operator. Unused variables use `messageId: "unusedVar"`, and
undefined identifiers use `messageId: "undef"`.

Honor `/* eslint-disable rule-name */` comments. A used directive suppresses the
selected rule. When `reportUnusedDisableDirectives` is enabled, an unused
directive produces a `ruleId: null` diagnostic whose message names the unused
rule.

### `linter.verifyAndFix(code, config, filenameOrOptions?)`

Return `{ fixed, output, messages }`. Apply supported fixes repeatedly until the
text is stable or no further fix is available. A valid fix run returns only
remaining diagnostics. With `quotes: ["error", "single"]` and
`semi: ["error", "always"]`, `const message = "hello"\n` becomes
`const message = 'hello';\n`, has `fixed: true`, and has no remaining messages.

### `linter.getSourceCode()`

After a successful `verify`, return a `SourceCode` instance for the most recent
source. It exposes `text`, `lines`, `ast`, `getText(node?, before?, after?)`,
`getFirstToken(node)`, `getAllComments()`, `getLocFromIndex(index)`, and
`getIndexFromLoc({line, column})`. Lines preserve a trailing empty line.
Locations use one-based lines and zero-based columns, while diagnostic columns
are one-based. Line comments have `{type: "Line", value, loc}`.

## `SourceCode`

Expose a constructible `SourceCode` class. Its static
`SourceCode.splitLines(text): string[]` recognizes CRLF, LF, and CR line
terminators and preserves a trailing empty line. For example,
`"a\r\nb\nc\r"` becomes `["a", "b", "c", ""]`.

## `new ESLint(options?)`

Support the asynchronous method
`lintText(code, {filePath?, warnIgnored?}?): Promise<LintResult[]>`.
The measured options are `overrideConfigFile: true`, `overrideConfig` as a flat
config array, and `fix: true|false`.

Return one result containing `filePath`, `messages`, `errorCount`,
`warningCount`, `fixableErrorCount`, `fixableWarningCount`, and optional
`output`. Counts describe the final messages. With `fix: true`, apply fixes and
return the fixed source in `output`; successfully fixed problems are absent
from `messages` and the final error/warning counts.

## `eslint/config`

This subpath exports callable `defineConfig`, `globalIgnores`, and
`includeIgnoreFile` properties.

- `defineConfig(...configs)` returns a flat array in argument order. For the
  measured object arguments, preserve `files`, `rules`, and their nested values.
- `globalIgnores(patterns, name?)` returns `{ ignores: patterns }` plus `name`
  when supplied, preserving pattern order.

## `eslint/use-at-your-own-risk`

This subpath exports `builtinRules` and `shouldUseFlatConfig`.
`builtinRules` is a `Map` containing the 292 built-in rules frozen in ESLint
10.9.0. Its `eqeqeq` entry has `meta.type === "suggestion"`,
`meta.fixable === "code"`, and these messages:

- `unexpected`: `Expected '{{expectedOperator}}' and instead saw '{{actualOperator}}'.`
- `replaceOperator`: `Use '{{expectedOperator}}' instead of '{{actualOperator}}'.`

# Implementation Notes

- Keep all behavior available from a clean consumer directory after `npm pack`;
  do not resolve files relative to the source workspace.
- Do not add install, postinstall, prepare, or other lifecycle hooks. They are
  disabled by the evaluator and cannot be used to generate the implementation.
- Do not access the network, spawn package managers, or use machine-specific
  absolute paths at runtime.
- Keep diagnostics, fixes, config arrays, rule metadata, comment locations, and
  output deterministic for identical input.
- This task deliberately measures a deterministic public API slice. File-glob
  linting, config-file discovery, formatter loading, `RuleTester.run`, custom
  parser/plugin functions, the CLI binary, cache files, concurrency, and writing
  fixes to disk are outside the measured contract.
