# Project Description

Create a complete installable npm package named `espree`, version `11.2.0`,
from an empty workspace. It must be an ESM package that exposes the public
Espree parser surface used by ESLint: parsing JavaScript into ESTree-compatible
AST objects and tokenizing source text.

# Natural Language Instruction

Create the ESM package `espree`, declarations, and public exports `parse`,
`tokenize`, `version`, `name`, `Syntax`, `VisitorKeys`,
`latestEcmaVersion`, and `supportedEcmaVersions`. Match the parse/token
contracts and all options below.

# Supports or Environment Configuration

- Use Node.js 24.19.0 and npm 11.17.0 on Linux amd64 with ESM semantics and the
  frozen offline dependencies in `task.toml`.
- Provide runnable JavaScript, declarations, package metadata, and the
  `./package.json` export. Do not use lifecycle downloads or native addons.
- Agent, candidate, verifier, Oracle, and controls run with no network access.

# Project Directory Structure

```text
workspace/
├── package.json
├── package-lock.json
├── espree.js
├── espree.d.ts
└── lib/
    ├── espree.js
    ├── options.js
    ├── token-translator.js
    └── types.js
```

# API Usage Guide

The API Usage Guide below is authoritative for parse/tokenize signatures,
AST/token shapes, locations, ranges, supported versions, and syntax errors.

# Implementation Notes

Return JSON-safe ESTree data with stable ordering. Validate options before
parsing and preserve source locations and ranges exactly.

# Examples

```js
import {parse, tokenize} from 'espree';
parse('const answer = 42;', {ecmaVersion: 2022, sourceType: 'script'});
```

```js
tokenize('x + 1', {ecmaVersion: 2022});
```

# Error Handling and Boundary Conditions

```js
parse('const =', {ecmaVersion: 2022});
```

```js
parse('<div/>', {ecmaVersion: 2022, ecmaFeatures: {jsx: true}});
```

# Supports

- Node.js 24.19.0 and npm 11.17.0 on Linux amd64 with glibc.
- A package root with `type: "module"`, an ESM entrypoint, and a package export
  for `./package.json`.
- `npm ci --offline --ignore-scripts` followed by `npm pack --ignore-scripts`.
- Runtime dependencies only from the committed npm v3 lockfile and offline
  cache. Do not use lifecycle scripts, workspaces, native addons, or runtime
  downloads.
- The package may use JavaScript or TypeScript internally, but the packed
  package must contain runnable JavaScript and a declaration file describing
  the public exports.

# API Usage Guide

Import the package with `import * as espree from "espree"`. The root exports
`parse(code, options?)`, `tokenize(code, options?)`, `version`, `name`,
`Syntax`, `VisitorKeys`, `latestEcmaVersion`, and
`supportedEcmaVersions`.

The public module example is `import espree`, referring to the package root
namespace shown by the ESM examples below.

The public module path is the package root and the runtime entry is
`espree.js`:

```js
import {parse, tokenize, latestEcmaVersion} from 'espree'
const tree = parse('let answer = 42;', {ecmaVersion: 2022})
const tokens = tokenize('answer + 1', {ecmaVersion: 2022})
```

The public module path is the package root and the runtime entry is
`espree.js`:

```js
import {parse, tokenize, latestEcmaVersion} from 'espree'
const tree = parse('let answer = 42;', {ecmaVersion: 2022})
const tokens = tokenize('answer + 1', {ecmaVersion: 2022})
```

`parse(code, options?)` accepts source text (coercing non-string values using
the package's documented behavior) and returns a `Program` ESTree node. The
default `sourceType` is `script` and the default ECMAScript version is 5.
Support numeric editions 3, 5 through 17, their 2015–2026 year aliases, and
`"latest"`. Support `sourceType` values `script`, `module`, and `commonjs`.

The boolean options `range`, `loc`, `tokens`, and `comment` add respectively
node ranges, source locations, a top-level token list, and a top-level comment
list. `ecmaFeatures.jsx` enables JSX parsing; `globalReturn` and
`impliedStrict` retain their documented parser meanings. `allowReserved` is
valid for ECMAScript 3 and invalid for later editions.

`tokenize(code, options?)` returns an ordered array of Esprima-compatible token
objects. It always collects tokens, and with `comment: true` the returned array
also has a `comments` property. Tokens and comments preserve `start`, `end`,
`range`, and `loc` when requested; regular expression tokens include their
pattern and flags.

Parsing and tokenization errors must be thrown as `SyntaxError` values with
deterministic `index`, `lineNumber`, and one-based `column` fields and the
Espree-style message. Invalid parser options must throw ordinary errors with
the documented option error messages.

# Implementation Notes

Preserve ESTree shape, deterministic ordering, source offsets, line/column
semantics, comment conversion, template-element ranges, JSX token behavior,
and native Acorn promise-free synchronous behavior. The evaluator installs the
packed package into a clean consumer, so imports must not depend on source
workspace paths or globally installed modules. The scored boundary is JSON
serializable and does not require custom parsers, CLI binaries, or test-only
helpers.
