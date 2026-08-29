# Project Description

Build a complete installable npm package named
`fast-string-truncated-width`, version `3.0.3`, from an empty workspace. The
package calculates terminal display width and the UTF-16 slice index at which
an input string must be truncated for a width limit and optional ellipsis.

This is a repository-generation task. Implement the described public contract
with your own package files; do not fetch or copy a reference repository.

# Supports

- Node.js `24.19.0`, npm `11.17.0`, `linux/amd64`, and ESM package semantics.
- `package.json` must use `"type": "module"`, identify the package as
  `fast-string-truncated-width` version `3.0.3`, and export the package root to
  a JavaScript ESM entry point.
- The root entry point must have TypeScript declarations for the default
  function and the three public types described below.
- Commit an npm lockfile with `lockfileVersion: 3`. A clean verifier must be
  able to run this command without network access:

  ```bash
  npm ci --offline --ignore-scripts --no-audit --no-fund
  ```

- The runtime package has no dependencies. Exact `typescript@5.9.3` is
  available offline if you choose to compile TypeScript during development;
  it may be a development dependency but must not be a runtime dependency.
- Do not use native addons, npm workspaces, registry configuration, custom
  loaders, generated downloads, or install/publish lifecycle scripts.
- Runtime behavior is synchronous, deterministic, stateless, and offline. The
  package does not expose a CLI or access files, environment-dependent terminal
  state, the clock, randomness, subprocesses, or the network.

# API Usage Guide

## Default export `fastStringTruncatedWidth(input, truncationOptions?, widthOptions?)`

**Import path:** the package root.

**Signature:**

```ts
type TruncationOptions = {
  limit?: number;
  ellipsis?: string;
  ellipsisWidth?: number;
};

type WidthOptions = {
  controlWidth?: number;
  tabWidth?: number;
  emojiWidth?: number;
  regularWidth?: number;
  wideWidth?: number;
};

type Result = {
  width: number;
  index: number;
  truncated: boolean;
  ellipsed: boolean;
};

export default function fastStringTruncatedWidth(
  input: string,
  truncationOptions?: TruncationOptions,
  widthOptions?: WidthOptions
): Result;

export type {TruncationOptions, WidthOptions, Result};
```

The function scans `input` in source order and returns:

- `width`: the width of the retained input portion, excluding the ellipsis.
  When truncation occurs this equals the non-negative width available before
  the ellipsis; otherwise it is the complete input width.
- `index`: the JavaScript UTF-16 end index for `input.slice(0, index)`. It is
  `input.length` when no truncation is needed and never splits a surrogate pair
  or recognized emoji sequence.
- `truncated`: whether the input exceeds `limit`.
- `ellipsed`: whether truncation occurs and the ellipsis width fits within the
  limit. A false value means the caller must not append the ellipsis.

`limit` defaults to `Infinity`, `ellipsis` defaults to the empty string, and
`ellipsisWidth` defaults to the width obtained by measuring `ellipsis` with the
same `widthOptions`. The available pre-ellipsis width is
`max(0, limit - ellipsisWidth)`. Negative limits therefore retain no input and
cannot fit a positive-width ellipsis.

Default terminal width rules are:

- ANSI CSI sequences and OSC 8 hyperlinks terminated by BEL or `ESC \\` have
  width `0` and remain part of the source index.
- C0/C1 control characters and DEL have width `0`; tabs are handled separately
  and have width `8`.
- Combining marks add width `0` to their base character.
- Recognized emoji presentation, modifier, keycap, regional-flag, subdivision-
  flag, and ZWJ sequences have width `2` as complete clusters.
- Han, Hiragana, Katakana, Hangul, Tangut, common terminal-wide symbols, and
  supplementary CJK ideographs have width `2`. Japanese half-width forms stay
  regular-width.
- Full-width forms, including ideographic space, always have width `2`.
- Other code points, including Unicode ambiguous-width characters, have width
  `1`.

`controlWidth`, `tabWidth`, `emojiWidth`, `regularWidth`, and `wideWidth`
override those corresponding defaults. Full-width forms remain fixed at two
columns. Use finite, non-negative numeric override values.

Examples:

```js
import fastStringTruncatedWidth from 'fast-string-truncated-width';

fastStringTruncatedWidth('\x1b[31mhello');
// {width: 5, index: 10, truncated: false, ellipsed: false}

fastStringTruncatedWidth('\x1b[31mhello', {limit: 3, ellipsis: '…'});
// {width: 2, index: 7, truncated: true, ellipsed: true}

const input = '古池や';
const options = {limit: 5, ellipsis: '…'};
const result = fastStringTruncatedWidth(input, options);
`${input.slice(0, result.index)}${result.ellipsed ? options.ellipsis : ''}`;
// '古池…'
```

# Implementation Notes

Keep the public surface to one default synchronous function and the three type
exports. Process long runs in bounded chunks or an equivalent linear scan;
do not split UTF-16 surrogate pairs or recognized emoji clusters. Sticky or
global regular expressions must not leak mutable state across calls. Preserve
all source bytes in the returned index calculation even when those bytes have
zero terminal width.
