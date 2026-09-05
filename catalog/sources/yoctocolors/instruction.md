# Project Description

Build an installable ESM npm package named `yoctocolors`, version `2.2.0`,
from an empty workspace. The package provides dependency-free terminal text
formatters. Each formatter either wraps text in a fixed ANSI SGR opening and
closing sequence or acts as a no-op when the current process does not support
colors.

# Natural Language Instruction

Create the `yoctocolors` package from an empty `workspace/`. Implement the
dependency-free ESM formatter surface, exact ANSI opening/closing sequences,
color capability detection, nested-style preservation, package exports, and
TypeScript declarations described below. Preserve all 61 named formatter
functions and the equivalent default namespace object.

Formatting must be synchronous, deterministic after module evaluation, and
free of filesystem, subprocess, clock, randomness, and network behavior. The
runtime must honor forced color modes and preserve input coercion and style
group boundaries.

# Supports

- Node.js `24.19.0`, npm `11.17.0`, Linux amd64, and ESM package semantics.
- `package.json` must use `name: "yoctocolors"`, `version: "2.2.0"`,
  `type: "module"`, `sideEffects: false`, Node engine `>=18`, and this root
  export map:

  ```json
  {"types":"./index.d.ts","default":"./index.js"}
  ```

- Publish exactly `index.js`, `index.d.ts`, `base.js`, and `base.d.ts` through
  the package `files` list. The root has no CLI or public subpath export.
- Commit a `package-lock.json` with `lockfileVersion: 3`. A clean verifier must
  be able to install it without network access using:

  ```bash
  npm ci --offline --ignore-scripts --no-audit --no-fund
  ```

- The package has no runtime dependencies. Do not add workspaces, native
  addons, registry overrides, lifecycle scripts, generated downloads,
  subprocesses, or network access.
- Color support is detected when `base.js` is evaluated using Node's terminal
  color capability. `FORCE_COLOR=1` must enable styles in a non-TTY child;
  `FORCE_COLOR=0` must disable them. When color is disabled, every formatter is
  a no-op and returns its input unchanged.

# Project Directory Structure

```text
workspace/
├── package.json
├── package-lock.json
├── index.js
├── index.d.ts
├── base.js
└── base.d.ts
```

The package root is the only public export path. `index.js` and `index.d.ts`
re-export the matching runtime and declaration surfaces from `base.js` and
`base.d.ts`; there is no CLI or public subpath.

# API Usage Guide

The package root exposes every formatter below as a named export. Its default
export is one namespace object containing the same formatter functions and no
extra public members. The declarations use this shared type:

```ts
export type Format = (string: string) => string;
```

Each named formatter has signature `const name: Format`. With color enabled,
calling a formatter produces:

```text
ESC + "[" + open + "m" + String(input) + ESC + "[" + close + "m"
```

where `ESC` is U+001B and `open`/`close` come from these tables.

## Modifiers

| Export | Open | Close | Meaning |
| --- | ---: | ---: | --- |
| `reset` | `0` | `0` | reset styles |
| `bold` | `1` | `22` | bold/intense |
| `dim` | `2` | `22` | dim/faint |
| `italic` | `3` | `23` | italic |
| `underline` | `4` | `24` | single underline |
| `underlineDouble` | `4:2` | `24` | double underline |
| `underlineCurly` | `4:3` | `24` | curly underline |
| `underlineDotted` | `4:4` | `24` | dotted underline |
| `underlineDashed` | `4:5` | `24` | dashed underline |
| `overline` | `53` | `55` | overline |
| `inverse` | `7` | `27` | inverse foreground/background |
| `hidden` | `8` | `28` | hidden text |
| `strikethrough` | `9` | `29` | strikethrough |

## Foreground and background colors

| Export | Open | Close | Export | Open | Close |
| --- | ---: | ---: | --- | ---: | ---: |
| `black` | `30` | `39` | `bgBlack` | `40` | `49` |
| `red` | `31` | `39` | `bgRed` | `41` | `49` |
| `green` | `32` | `39` | `bgGreen` | `42` | `49` |
| `yellow` | `33` | `39` | `bgYellow` | `43` | `49` |
| `blue` | `34` | `39` | `bgBlue` | `44` | `49` |
| `magenta` | `35` | `39` | `bgMagenta` | `45` | `49` |
| `cyan` | `36` | `39` | `bgCyan` | `46` | `49` |
| `white` | `37` | `39` | `bgWhite` | `47` | `49` |
| `gray` | `90` | `39` | `bgGray` | `100` | `49` |
| `redBright` | `91` | `39` | `bgRedBright` | `101` | `49` |
| `greenBright` | `92` | `39` | `bgGreenBright` | `102` | `49` |
| `yellowBright` | `93` | `39` | `bgYellowBright` | `103` | `49` |
| `blueBright` | `94` | `39` | `bgBlueBright` | `104` | `49` |
| `magentaBright` | `95` | `39` | `bgMagentaBright` | `105` | `49` |
| `cyanBright` | `96` | `39` | `bgCyanBright` | `106` | `49` |
| `whiteBright` | `97` | `39` | `bgWhiteBright` | `107` | `49` |

## Underline colors

Underline colors use SGR palette form `58;5;n` and close independently with
SGR `59`.

| Export | Open | Close | Export | Open | Close |
| --- | ---: | ---: | --- | ---: | ---: |
| `underlineBlack` | `58;5;0` | `59` | `underlineRedBright` | `58;5;9` | `59` |
| `underlineRed` | `58;5;1` | `59` | `underlineGreenBright` | `58;5;10` | `59` |
| `underlineGreen` | `58;5;2` | `59` | `underlineYellowBright` | `58;5;11` | `59` |
| `underlineYellow` | `58;5;3` | `59` | `underlineBlueBright` | `58;5;12` | `59` |
| `underlineBlue` | `58;5;4` | `59` | `underlineMagentaBright` | `58;5;13` | `59` |
| `underlineMagenta` | `58;5;5` | `59` | `underlineCyanBright` | `58;5;14` | `59` |
| `underlineCyan` | `58;5;6` | `59` | `underlineWhiteBright` | `58;5;15` | `59` |
| `underlineWhite` | `58;5;7` | `59` |  |  |  |
| `underlineGray` | `58;5;8` | `59` |  |  |  |

Example:

```js
import colors, {red, underlineCurly, underlineRed} from 'yoctocolors';

red('Error'); // "\u001B[31mError\u001B[39m" when enabled
colors.blue(`Welcome to ${colors.green('yoctocolors')}`);
underlineRed(underlineCurly('typo'));
```

# Implementation Notes

- Formatting is synchronous and deterministic after import. Do not read files,
  use randomness, spawn processes, or retain per-call state.
- Enabled formatters apply JavaScript string coercion before wrapping. An empty
  string is still wrapped in the opening and closing sequences. The TypeScript
  API remains string-to-string even though JavaScript callers can supply other
  coercible values.
- Nested styling must preserve the outer style. If the input already contains
  the current formatter's closing sequence, replace each occurrence with the
  formatter's opening sequence before appending the final close. For `bold`
  and `dim`, SGR `22` resets both styles, so preserve the encountered SGR `22`
  and then reopen the outer formatter.
- Style groups close independently: foreground uses `39`, background uses
  `49`, underline shape uses `24`, and underline color uses `59`.
- `index.js` and `index.d.ts` re-export the named surface from `base.js` and
  `base.d.ts`, respectively, and expose that same surface as the default
  namespace. Keep runtime exports and declarations in exact agreement.
- The evaluator imports the installed package in bounded UID-isolated child
  processes under both forced-color modes. Candidate code is never imported
  into the trusted verifier process.

# Examples

```js
import {bold, green, red} from 'yoctocolors';

const message = bold(green('ready'));
const failure = red('failed');
```

```js
import colors from 'yoctocolors';

console.log(colors.cyan('status'), colors.bgBlack('terminal'));
```

```bash
FORCE_COLOR=1 node -e "import('yoctocolors').then(({yellow}) => console.log(yellow('on')))"
FORCE_COLOR=0 node -e "import('yoctocolors').then(({yellow}) => console.log(yellow('off')))"
```

# Error Handling and Boundary Conditions

- Every formatter accepts a string according to its TypeScript signature and
  applies JavaScript string coercion at runtime. Empty strings are still
  wrapped when color output is enabled.
- When color support is disabled, every formatter returns its input unchanged;
  `FORCE_COLOR=1` and `FORCE_COLOR=0` override the non-TTY default as specified.
- Nested formatters preserve outer styles by reopening after an inner closing
  sequence. Foreground, background, underline shape, and underline color close
  with their independent SGR reset codes.
- The default namespace and named exports must remain in exact agreement. An
  import or formatting failure must not contact a registry or silently spawn a
  helper process.
- Agent, candidate, verifier, Oracle, controls, and runtime execution are
  NoNetwork.
