# Build `mdast-util-mdxjs-esm`

## Project Description

Create an installable npm package named `mdast-util-mdxjs-esm`, version `2.0.1`,
from an empty workspace. The package is an ESM-only mdast extension for MDX
JavaScript module declarations: one extension integrates parsing with
`mdast-util-from-markdown`, and one integrates serialization with
`mdast-util-to-markdown`.

This is a repository-generation task. Implement the described behavior with
your own source files. Do not retrieve the reference repository or hidden
tests.

## Supports

- Run on Node `24.19.0` with npm `11.17.0` on Linux x86-64.
- `package.json` must name `mdast-util-mdxjs-esm`, version `2.0.1`, and set
  `"type": "module"`.
- The root package must expose the named ESM exports
  `mdxjsEsmFromMarkdown` and `mdxjsEsmToMarkdown`. It has no default export.
- Include a compatible npm v3 `package-lock.json`. The package may declare the
  six runtime dependency roots listed below, but must not add native addons,
  git/file/workspace dependencies, custom loaders, lifecycle hooks, or network
  requirements.
- A clean verifier installs with:

  ```bash
  npm ci --offline --ignore-scripts --no-audit --no-fund
  ```

## API Usage Guide

### `mdxjsEsmFromMarkdown`

Import from `mdast-util-mdxjs-esm` and call `mdxjsEsmFromMarkdown()` with no
arguments. It returns a `FromMarkdownExtension` object with `enter.mdxjsEsm`
and `exit.mdxjsEsm`/`exit.mdxjsEsmData` handlers.

The `enter.mdxjsEsm` handler receives a token and uses the compile context's
`enter({type: 'mdxjsEsm', value: ''}, token)` and `buffer()` operations. The
`exit.mdxjsEsm` handler resumes the buffered source value, assigns it to the
top `mdxjsEsm` node, exits the token, and copies a truthy `token.estree` value
to `node.data.estree`. It must leave `data` absent when no ESTree result is
provided. The handler asserts that the top stack node has type `mdxjsEsm`.

The `exit.mdxjsEsmData` handler delegates the token to both configured data
handlers, in enter-then-exit order, with the same compile context as `this`.

### `mdxjsEsmToMarkdown`

Import from `mdast-util-mdxjs-esm` and call `mdxjsEsmToMarkdown()` with no
arguments. It returns a `ToMarkdownExtension` object with a
`handlers.mdxjsEsm` function. That handler returns the node's `value` when it
is truthy and returns the empty string when `value` is missing or falsey.

The extension factory calls are side-effect free and return fresh extension
objects. The handlers preserve object identity for nodes and ESTree values;
they do not parse, clone, mutate, stringify, or normalize the supplied values.

## Implementation Notes

The verifier calls a task-specific JSON adapter subpath,
`mdast-util-mdxjs-esm/adapter`, only to exercise the callback/context handlers
through a process-safe contract. The adapter is required in addition to the
two root exports and must expose an async `run(request)` function. It accepts
only the documented operation names and JSON-compatible arguments; reject
malformed requests with an `Error`.

The adapter operations are `api`, `from-enter`, `from-exit`, `from-data`, and
`to-markdown`. They model the compile context and return JSON-safe summaries or
results. They must delegate to the root extension factories rather than
reimplementing their returned handler behavior. Do not rely on verifier files,
global packages, browser APIs, native addons, lifecycle hooks, or network
access.
