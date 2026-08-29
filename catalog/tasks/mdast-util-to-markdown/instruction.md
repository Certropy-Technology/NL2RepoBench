# Project Description

Build a complete installable npm package named `mdast-util-to-markdown`,
version `2.1.2`, from an empty workspace. The package synchronously serializes
mdast syntax trees to deterministic Markdown text and supports configurable
markers, safe escaping, custom node handlers, join callbacks, and unsafe
character rules.

This is a repository-generation task. Implement the public contract below with
your own package files; do not fetch or copy a reference repository.

# Supports

- Node.js `24.19.0`, npm `11.17.0`, `linux/amd64`, and ESM semantics.
- `package.json` must identify `mdast-util-to-markdown@2.1.2`, use
  `"type": "module"`, and export the package root through `./index.js`.
  Provide `index.d.ts` declarations for the documented runtime exports and
  public types.
- Commit an npm v3 lockfile. A clean verifier must be able to run:

  ```bash
  npm ci --offline --ignore-scripts --no-audit --no-fund
  ```

- Declare exactly these direct runtime dependencies and versions:
  `@types/mdast@4.0.4`, `@types/unist@3.0.3`,
  `longest-streak@3.1.0`, `mdast-util-phrasing@4.1.0`,
  `mdast-util-to-string@4.0.0`,
  `micromark-util-classify-character@2.0.1`,
  `micromark-util-decode-string@2.0.1`, `unist-util-visit@5.1.0`, and
  `zwitch@2.0.4`. Do not declare other runtime dependencies.
- Do not expose a CLI or npm workspace and do not use native addons, custom
  loaders, registry configuration, generated downloads, or lifecycle hooks
  named `preinstall`, `install`, `postinstall`, `prepare`, `prepack`, or
  `postpack`.
- Runtime behavior is synchronous, deterministic, and offline. Serialization
  must not mutate the input tree or access files, environment-dependent state,
  the clock, randomness, subprocesses, or the network.

# API Usage Guide

## `toMarkdown(tree, options?)`

**Import path:** package root.

**TypeScript signature:**

```ts
function toMarkdown(tree: Nodes, options?: Options | null): string;
```

`Nodes` is the union of mdast nodes from `@types/mdast`. The function returns
Markdown for the supplied node. It accepts either a full `root` or any single
supported node. A nonempty serialization ends with a line ending; an empty root
returns `""`. Calls preserve child order and input text except where Markdown
syntax requires escaping or character-reference encoding.

The built-in handlers support these core node types and fields:

- `root`, `paragraph`, `blockquote`, `heading`, `list`, and `listItem` use
  ordered `children`; headings use `depth` 1 through 6; lists use `ordered`,
  optional `start`, and optional `spread`; list items may also use `spread`.
- `text`, `html`, `code`, and `inlineCode` use `value`. `code` additionally
  accepts nullable `lang` and `meta`.
- `emphasis` and `strong` use phrasing `children`; `break` represents a hard
  line break; `thematicBreak` represents a rule.
- `link` uses `url`, nullable `title`, and phrasing `children`; `image` uses
  `url`, nullable `title`, and nullable `alt`.
- `definition` uses `identifier`, optional `label`, `url`, and nullable
  `title`. `linkReference` uses `identifier`, optional `label`,
  `referenceType` (`"shortcut"`, `"collapsed"`, or `"full"`), and children.
  `imageReference` uses the same association fields plus nullable `alt`.
- Positional metadata may be present and does not change the Markdown output.

Flow nodes are separated by blank lines unless list looseness or a join rule
changes the separation. Phrasing children are concatenated in source order.
Text is made safe for its surrounding construct: syntax-looking punctuation is
escaped or encoded only where it could alter the parsed Markdown structure.
Fenced code chooses a fence long enough not to collide with its content, inline
code chooses a safe grave-accent run, and links use autolink form only when the
label and destination permit it.

Passing a non-node throws `Error` with a message ending in `expected node`.
Passing an unhandled node type throws `Error` containing
`Cannot handle unknown node \`<type>\``. Invalid marker options throw `Error`
when the corresponding construct is serialized and identify the invalid option
and its allowed domain.

Example:

```js
import {toMarkdown} from 'mdast-util-to-markdown';

const tree = {
  type: 'root',
  children: [
    {type: 'heading', depth: 1, children: [{type: 'text', value: 'Hello'}]},
    {type: 'paragraph', children: [{type: 'text', value: 'World'}]}
  ]
};

toMarkdown(tree);
// '# Hello\n\nWorld\n'
```

## `Options`

All fields are optional and accept `null` or `undefined` as absence where the
declaration permits it.

| Field | Domain and behavior |
| --- | --- |
| `bullet` | `"*"`, `"+"`, or `"-"`; unordered-list marker, default `"*"`. |
| `bulletOther` | `"*"`, `"+"`, or `"-"`; collision fallback and must differ from `bullet`; default `"-"` when `bullet` is `"*"`, otherwise `"*"`. |
| `bulletOrdered` | `"."` or `")"`; ordered-list marker, default `"."`. |
| `closeAtx` | Boolean; repeat opening `#` markers at the end of ATX headings, default `false`. |
| `emphasis` | `"*"` or `"_"`, default `"*"`. |
| `strong` | `"*"` or `"_"`, default `"*"`. |
| `fences` | Boolean; prefer fenced code blocks, default `true`. Code that cannot be represented safely as indented code remains fenced. |
| `fence` | ``"`"`` or `"~"`; fenced-code marker, default ``"`"``. |
| `incrementListMarker` | Boolean; increment ordered markers from `start`, default `true`. |
| `listItemIndent` | `"one"`, `"tab"`, or `"mixed"`; default `"one"`. `mixed` uses compact indentation for tight items and tab-stop indentation for loose items. |
| `quote` | `"\""` or `"'"`; title quote marker, default `"\""`. Matching title characters are escaped. |
| `resourceLink` | Boolean; force resource links instead of eligible autolinks, default `false`. |
| `rule` | `"*"`, `"-"`, or `"_"`; thematic-break marker, default `"*"`. |
| `ruleRepetition` | Integer at least 3; default `3`. |
| `ruleSpaces` | Boolean; place spaces between rule markers, default `false`. |
| `setext` | Boolean; use setext form for nonempty rank-1 and rank-2 headings, default `false`. |
| `tightDefinitions` | Boolean; omit blank lines between adjacent definitions, default `false`. |
| `handlers` | Partial mapping from node type to `Handle`; entries extend or replace built-ins. |
| `join` | Ordered array of `Join` callbacks appended to built-in join rules. |
| `unsafe` | Ordered array of `Unsafe` rules appended to built-in escaping rules. |
| `extensions` | Ordered array of `Options`; subextensions are applied first, then the containing options object. Scalar/handler values applied later win; `join` and `unsafe` arrays append in order. |

## Extension callback types

The package root exports these public TypeScript types:
`ConstructNameMap`, `ConstructName`, `Handle`, `Handlers`, `Info`, `Join`,
`Map`, `Options`, `SafeConfig`, `State`, `Tracker`, and `Unsafe`.

```ts
type Handle = (
  node: any,
  parent: Parents | undefined,
  state: State,
  info: Info
) => string;

type Join = (
  left: FlowChildren,
  right: FlowChildren,
  parent: FlowParents,
  state: State
) => boolean | number | null | undefined | void;
```

A handler returns the Markdown fragment for its node. It may call the supplied
state helpers such as `state.handle`, `state.containerPhrasing`,
`state.containerFlow`, `state.safe`, `state.enter`, and
`state.createTracker`. Handler lookup uses the node's `type`.

Join callbacks are consulted in order for adjacent flow children. Return
`false` to prevent joining, `true` or `1` to request one blank line, `0` to
join with no blank line, another finite number to request that many blank
lines, or `undefined`/`null` to make no decision. Multiple numeric decisions
use the most restrictive effective separation.

An `Unsafe` rule has required `character: string` and may have `before`,
`after`, `atBreak`, `inConstruct`, and `notInConstruct` constraints. Matching
characters are escaped or encoded by `state.safe`; `_compiled` is internal and
must not be supplied.

Example custom handler:

```js
toMarkdown(
  {type: 'mention', value: 'Ada'},
  {handlers: {mention(node) { return '@' + node.value; }}}
);
// '@Ada\n'
```

## `defaultHandlers`

**Import path:** package root.

**TypeScript signature:**

```ts
const defaultHandlers: Handlers;
```

This deterministic object maps the core names `blockquote`, `break`, `code`,
`definition`, `emphasis`, `hardBreak`, `heading`, `html`, `image`,
`imageReference`, `inlineCode`, `link`, `linkReference`, `list`, `listItem`,
`paragraph`, `root`, `strong`, `text`, and `thematicBreak` to `Handle`
functions. It is exposed for extension authors; `toMarkdown` starts each call
with a fresh shallow copy, so per-call handler overrides do not mutate this
export.

# Implementation Notes

Implement context-sensitive escaping rather than globally escaping every
punctuation character. Markdown constructs interact: list markers can become
rules, adjacent lists may need alternate bullets, attention markers depend on
surrounding character classes, and code/link delimiters must grow or switch
form when content collides with them. Keep all per-call state local so repeated
calls are independent.

The verifier invokes the installed package only in bounded candidate
subprocesses and exchanges JSON-compatible trees and results. It also creates
fixed child-side custom handlers and join callbacks to exercise the documented
extension boundary; candidate JavaScript is never imported into the trusted
test process.
