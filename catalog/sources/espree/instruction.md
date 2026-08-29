# Project Description

Create a complete installable npm package named `espree`, version `11.2.0`,
from an empty workspace. It must be an ESM package that exposes the public
Espree parser surface used by ESLint: parsing JavaScript into ESTree-compatible
AST objects and tokenizing source text.

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
