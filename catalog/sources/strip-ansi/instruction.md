# Project Description

Build a complete installable npm package named `strip-ansi`, version `7.2.0`,
from an empty workspace. The package removes ANSI/VT terminal escape sequences
from strings while preserving all ordinary text.

This is a repository-generation task. Implement the described public contract
with your own package files; do not fetch or copy a reference repository.

# Supports

- Node.js `24.19.0`, npm `11.17.0`, `linux/amd64`, and ESM package semantics.
- `package.json` must use `"type": "module"`, identify the package as
  `strip-ansi` version `7.2.0`, and export the package root to a JavaScript ESM
  entry point.
- The root entry point must have a TypeScript declaration that describes the
  default function as accepting and returning a string.
- Commit an npm lockfile with `lockfileVersion: 3`. A clean verifier must be
  able to run this command without network access:

  ```bash
  npm ci --offline --ignore-scripts --no-audit --no-fund
  ```

- You may implement the behavior without runtime dependencies. If you use the
  upstream-compatible helper dependency, the only available runtime package is
  exact `ansi-regex@6.3.0`; do not declare any other runtime dependency.
- Do not use native addons, npm workspaces, registry configuration, custom
  loaders, generated downloads, or lifecycle scripts such as `preinstall`,
  `install`, `postinstall`, `prepare`, `prepack`, or `postpack`.
- Runtime execution is deterministic and offline. The package does not expose
  a CLI and must not access files, environment-dependent terminal state, the
  clock, randomness, subprocesses, or the network.

# API Usage Guide

## Default export `stripAnsi(string)`

**Import path:** the package root.

**Signature:**

```ts
export default function stripAnsi(string: string): string;
```

The default export is a synchronous function. It removes every recognized
ANSI/VT control sequence from the supplied string and returns the remaining
text in its original order.

The required sequence families are:

- CSI sequences introduced by either `ESC [` (`\u001B[`) or the 8-bit CSI
  byte (`\u009B`). This includes SGR styling, semicolon- or colon-separated
  color parameters, erase/cursor commands, and private-mode commands.
- OSC control strings introduced by `ESC ]` (`\u001B]`) and terminated by
  BEL (`\u0007`), the two-character string terminator `ESC \\`, or the 8-bit
  ST byte (`\u009C`). The whole OSC control string is removed. This covers
  terminal titles and OSC 8 hyperlinks.

All matching sequences are removed, not only the first one. Ordinary ASCII,
Unicode, emoji, spaces, tabs, LF, CRLF, punctuation, and text between or around
the sequences must remain unchanged. Empty strings and strings without a
recognized control sequence are returned unchanged. Calls are stateless and
must return the same result when repeated.

If the argument is not a string, throw a `TypeError` with this exact message:

```text
Expected a `string`, got `<typeof value>`
```

Here `<typeof value>` uses JavaScript's `typeof` result, so `null`, arrays, and
plain objects report `object`.

Examples:

```js
import stripAnsi from 'strip-ansi';

stripAnsi('\u001B[4mUnicorn\u001B[0m');
// 'Unicorn'

stripAnsi('\u001B]8;;https://example.com\u0007Click\u001B]8;;\u0007');
// 'Click'

stripAnsi('\u009B31mred\u009B39m');
// 'red'
```

# Implementation Notes

Keep the public surface intentionally small: one default ESM function and its
declaration. Escape-sequence parsing must be bounded for ordinary string input
and must not mutate process-global regular-expression state between calls.
Preserve text exactly except for the recognized control sequences described
above.
