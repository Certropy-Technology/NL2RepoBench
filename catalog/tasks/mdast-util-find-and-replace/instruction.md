# Build `mdast-util-find-and-replace`

## Project Description

Create an installable npm package named `mdast-util-find-and-replace`, version
`3.0.2`, from an empty workspace. The package mutates an mdast tree by finding
matches inside `text` node values and replacing those matches with strings or
phrasing nodes. It exposes one named function, `findAndReplace`, and has no
default export or command-line interface.

The task covers package-root runtime behavior and TypeScript declarations. It
does not require the upstream formatting, coverage, documentation, or build
toolchain. Do not copy upstream source or tests into the generated repository.

## Supports

- Run on Node `24.19.0` with npm `11.17.0` on `linux/amd64`.
- `package.json` must use `"name": "mdast-util-find-and-replace"`, version
  `3.0.2`, and `"type": "module"`. Its root conditional export must point
  ESM consumers to a JavaScript entry and TypeScript consumers to an existing
  declaration entry.
- Export only the named runtime identifier `findAndReplace` from the package
  root. Do not provide a default export.
- Declare these exact runtime dependencies and no others:

  ```json
  {
    "@types/mdast": "4.0.4",
    "escape-string-regexp": "5.0.0",
    "unist-util-is": "6.0.1",
    "unist-util-visit-parents": "6.0.2"
  }
  ```

- Commit a v3 `package-lock.json`. A clean verifier runs:

  ```bash
  npm ci --offline --ignore-scripts --no-audit --no-fund
  ```

- Declare no npm scripts, development dependencies, workspaces, native addons,
  custom loaders, registry settings, or lifecycle hooks.
- Runtime behavior is synchronous, deterministic, and offline. It must not use
  files, subprocesses, browser globals, the network, randomness, locale, or the
  clock.

## Bounded Evaluation Contract

The verifier never imports candidate JavaScript into its trusted process. A
bounded unprivileged child imports the installed package, constructs RegExp and
callback values from allowlisted declarative scenarios, invokes the package,
and returns a cycle-free JSON projection.

Input trees contain at most 256 nodes, nesting is at most 32 levels, and each
request is at most 64 KiB. Trees, node data, and replacement nodes contain only
plain JSON values. Scored regular expressions are at most 512 characters and
never match the empty string. No source text, arbitrary executable callback,
accessor, custom prototype, symbol, BigInt, cyclic value, or native object
crosses the boundary.

## API Usage Guide

### `findAndReplace`

```ts
import type {Nodes, Parents, PhrasingContent, Text} from 'mdast'
import type {Test} from 'unist-util-is'

type Find = RegExp | string
type RegExpMatchObject = {
  index: number
  input: string
  stack: [...Array<Parents>, Text]
}
type ReplaceFunction = (
  value: string,
  ...capturesAndMatch: [...Array<string | undefined>, RegExpMatchObject]
) => Array<PhrasingContent> | PhrasingContent | string | false | null | undefined
type Replace = ReplaceFunction | string | null | undefined
type FindAndReplaceTuple = [Find, Replace?]
type FindAndReplaceList = Array<FindAndReplaceTuple>
type Options = {ignore?: Test | null}

export function findAndReplace(
  tree: Nodes,
  list: FindAndReplaceList | FindAndReplaceTuple,
  options?: Options | null
): undefined
```

The function mutates `tree` and always returns `undefined`. Invalid values for
`list` throw `TypeError` with a message containing
`Expected find and replace tuple or list of tuples`.

Each tuple is applied completely before the next tuple. For one tuple, visit
eligible `text` nodes in preorder and find matches from left to right inside
each complete text value. Matches do not span two text nodes. A `text` node
without a parent cannot be spliced and is left unchanged.

- A string find value is escaped and treated as a global literal search.
- A RegExp keeps its flags. Reset `lastIndex` before each text node. A global
  RegExp handles every match; a non-global RegExp handles the first match in
  each text node.
- Call a replacement function with the whole match, then every capture group,
  then a match object. `index` is the zero-based UTF-16 offset in that text
  value, `input` is the complete text value, and `stack` contains all ancestors
  followed by the matched text node.
- `null`, `undefined`, and `''` remove a match. A non-empty string becomes a
  new text node. A node or node array is spliced directly into the parent.
- `false` means that occurrence is not a match. For global searches, resume at
  one UTF-16 code unit after that occurrence's start so overlapping later
  matches remain possible.
- Preserve unmatched text before, between, and after matches without creating
  empty text nodes. Replacing a complete text value with nothing removes that
  child.
- Do not revisit nodes inserted by the current tuple. Later tuples do visit
  text contained in nodes inserted by earlier tuples.

`options.ignore` follows the `unist-util-is` `Test` contract: it may be a node
type string, a partial node object, an array of tests, or a predicate receiving
`(node, index, parent)`. Before searching a text node, test every ancestor in
order. If any ancestor matches, leave that text node unchanged.

Example:

```js
import {findAndReplace} from 'mdast-util-find-and-replace'

const tree = {
  type: 'paragraph',
  children: [{type: 'text', value: 'Hello @ada and @lin'}]
}

findAndReplace(tree, [
  [/@([a-z]+)/gi, (whole, name) => ({
    type: 'link',
    url: `/users/${name.toLowerCase()}`,
    children: [{type: 'text', value: whole}]
  })]
])
```

After the call, the original paragraph has text and link children in source
order. The callback-created links are not searched again by that same tuple.

## Implementation Notes

Preserve all fields on unaffected nodes and parents. New text nodes only need
`type: "text"` and their string `value`; source positions from a split input
text node are not copied. Do not attach parent pointers or process-global
state. Pair order, tree preorder, child order, capture order, and replacement
order are observable and must remain deterministic.
