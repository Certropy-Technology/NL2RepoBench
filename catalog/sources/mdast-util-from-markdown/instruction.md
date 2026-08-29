# Build `mdast-util-from-markdown`

## Project Description

Create an installable ESM npm package named `mdast-util-from-markdown`, version
`2.0.3`. Its root entry point must export the named function `fromMarkdown`.
The function parses CommonMark-oriented Markdown into an mdast syntax tree.

The evaluation contract is a deterministic, JSON-safe subset of the package.
It starts a fresh process for each scenario and passes a Markdown string. The
returned tree must be JSON serializable. Do not implement network access,
filesystem discovery, mutable global state, or a CLI.

## Supports

- Node `24.19.0` and npm `11.17.0` on Linux amd64 with glibc.
- ESM packaging with `"type": "module"`, package name and version matching the
  contract, and a root `exports` entry that resolves the named `fromMarkdown`.
- Exact runtime dependencies matching the package contract and a root npm
  lockfile using lockfile version 3. The verifier installs with
  `npm ci --offline --ignore-scripts --no-audit --no-fund`.
- JSON-safe inputs: Markdown strings no larger than 64 KiB. Trees and node
  fields must remain ordinary JSON strings, numbers, booleans, nulls, arrays,
  and objects.

## API Usage Guide

### `fromMarkdown(value, encoding?, options?)`

Import it with:

```js
import {fromMarkdown} from 'mdast-util-from-markdown'
const tree = fromMarkdown('# hello')
```

The required `value` is a string in this task. Return a Root object with
`type: 'root'`, a `children` array, and positional information for parsed
nodes. The parser must preserve source order and use mdast node shapes.

The JSON-safe contract covers empty documents, paragraphs and soft line breaks,
ATX and setext headings, emphasis and strong emphasis, inline code, fenced and
indented code, block quotes, ordered and unordered lists, thematic breaks,
links, images, link definitions and reference links, autolinks, raw HTML nodes,
character escapes and character references, hard breaks, Unicode text, and
deterministic source positions. Inline and block nodes must use the standard
mdast fields such as `url`, `title`, `alt`, `depth`, `lang`, `meta`, `ordered`,
`start`, `spread`, `checked`, `label`, `identifier`, and `referenceType` where
those fields apply.

Malformed extension callbacks, custom micromark extensions, typed-array input,
streaming input, browser globals, and non-JSON values are outside this task's
subprocess contract. Do not add a default export in place of the required named
export.

## Implementation Notes

Use a clean package root that can be packed and installed by npm. Keep all
runtime behavior deterministic and independent of wall clock, locale, random
values, environment-specific paths, and network state. `position` objects use
one-based `line` and `column` values and zero-based `offset` values. Preserve
the distinction between `null` fields defined by mdast and omitted fields.

The hidden verifier invokes only the public package from a separate unprivileged
Node process. It owns test collection, timeouts, reports, and scoring. Do not
write reward, grading, JUnit, or verifier files from the candidate package.
