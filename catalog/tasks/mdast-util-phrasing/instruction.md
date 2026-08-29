# Build `mdast-util-phrasing`

## Project Description

Create a complete installable npm package named `mdast-util-phrasing`, version
`4.1.0`, from an empty workspace. The package is an ESM utility that determines
whether an mdast node is phrasing content. It has one public function,
`phrasing`, and no default export.

This is a repository-generation task. Implement the behavior with your own
source files; do not copy a reference implementation or upstream tests into the
repository.

## Supports

- Run on Node `24.19.0` with npm `11.17.0` on `linux/amd64` with glibc.
- Use ESM with `"type": "module"`. The package root must provide the named
  export `phrasing` through a safe in-package `exports` entry.
- Include a committed npm v3 `package-lock.json` consistent with
  `package.json`. The package must install from a clean checkout with:

  ```bash
  npm ci --offline --ignore-scripts --no-audit --no-fund
  ```

- The verifier provides an offline npm cache containing the frozen runtime
  dependency closure for `@types/mdast@4.0.4`, `@types/unist@3.0.3`, and
  `unist-util-is@6.0.1`. You may use that closure or implement the behavior
  without runtime dependencies.
- Do not use lifecycle hooks, native addons, custom loaders, workspaces,
  registry configuration, network access, filesystem state, current time, or
  randomness.

## API Usage Guide

### `phrasing(value)`

Import path and signature:

```js
import {phrasing} from 'mdast-util-phrasing'

phrasing(value?: unknown): boolean
```

Return `true` when `value` is a node object whose `type` is one of these exact,
case-sensitive strings:

```text
break
delete
emphasis
footnote
footnoteReference
image
imageReference
inlineCode
inlineMath
link
linkReference
mdxJsxTextElement
mdxTextExpression
strong
text
textDirective
```

Return `false` for omitted input, `null`, primitives, arrays, objects without a
valid string `type`, unknown node types, and block node types such as
`paragraph`, `heading`, `list`, and `html`. `html` is deliberately excluded
because mdast permits it in both phrasing and flow contexts.

Only the node's `type` determines the result. Other fields, including
`children`, `value`, `url`, position data, and extension-specific properties,
must not change classification. The function is synchronous, deterministic,
does not coerce types, does not mutate its argument, and does not throw for any
JavaScript value.

Examples:

```js
phrasing({type: 'paragraph', children: [{type: 'text', value: 'Alpha'}]})
// => false

phrasing({type: 'strong', children: [{type: 'text', value: 'Delta'}]})
// => true

phrasing({type: 'html', value: '<b>Echo</b>'})
// => false

phrasing({type: 'textDirective', name: 'mark'})
// => true
```

## Implementation Notes

Keep the root package importable without a build step. TypeScript declarations
may express `phrasing` as a type predicate, but runtime behavior is the contract
above. The evaluator packs and installs the submitted repository, then invokes
the package only in an unprivileged child process over a bounded JSON protocol;
trusted verifier code never imports candidate files and candidate code cannot
write verifier-owned grading or reward reports.
