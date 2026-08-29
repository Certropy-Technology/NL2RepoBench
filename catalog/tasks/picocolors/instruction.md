# Build `picocolors`

## Project Description

Create a complete installable npm package named `picocolors`, version `1.1.1`,
from an empty workspace. It is a tiny CommonJS terminal formatting library that
returns ANSI-styled strings when color support is enabled and plain strings when
it is disabled.

This is a repository-generation task. Implement the described behavior with
your own package files; do not fetch or copy a reference repository or its tests.

## Supports

- Node.js `24.19.0`, npm `11.17.0`, `linux/amd64`, and CommonJS semantics.
- `require("picocolors")` must load the package root. The package must identify
  itself as `picocolors` version `1.1.1`, use `picocolors.js` as its main entry,
  and include `picocolors.browser.js`, `picocolors.d.ts`, and `types.d.ts` in
  its published files.
- Commit a v3 `package-lock.json`. A clean verifier must support:

  ```bash
  npm ci --offline --ignore-scripts --no-audit --no-fund
  ```

- Do not declare runtime dependencies, workspaces, native addons, custom
  loaders, registry configuration, or lifecycle scripts. Runtime behavior must
  be deterministic and offline.

## API Usage Guide

### Package root

`require("picocolors")` returns an object. It exposes the boolean
`isColorSupported`, the callable `createColors(enabled = isColorSupported)`,
and every formatter listed below. `createColors` returns a fresh object with
the same formatter names and an `isColorSupported` value equal to the supplied
boolean. It must not mutate the default object.

The browser entry is selected by the package `browser` mapping for
`picocolors.js`. It exposes the same formatter names, always reports
`isColorSupported: false`, and each formatter returns its input coerced with
`String(...)` without ANSI escapes.

### Formatter functions

The formatter functions accept any ordinary JavaScript value and return a
string. Missing arguments therefore become `"undefined"`; `null`, booleans,
numbers, arrays, and plain objects use normal JavaScript string coercion.

Required modifiers:

```text
reset bold dim italic underline inverse hidden strikethrough
```

Required foreground colors:

```text
black red green yellow blue magenta cyan white gray
blackBright redBright greenBright yellowBright blueBright
magentaBright cyanBright whiteBright
```

Required background colors:

```text
bgBlack bgRed bgGreen bgYellow bgBlue bgMagenta bgCyan bgWhite
bgBlackBright bgRedBright bgGreenBright bgYellowBright bgBlueBright
bgMagentaBright bgCyanBright bgWhiteBright
```

Enabled formatters wrap the coerced text in these ANSI open/close pairs:

```text
reset 0/0        bold 1/22       dim 2/22       italic 3/23
underline 4/24  inverse 7/27     hidden 8/28    strikethrough 9/29
black 30/39     red 31/39        green 32/39    yellow 33/39
blue 34/39      magenta 35/39    cyan 36/39     white 37/39
gray 90/39
bgBlack 40/49   bgRed 41/49      bgGreen 42/49   bgYellow 43/49
bgBlue 44/49    bgMagenta 45/49  bgCyan 46/49   bgWhite 47/49
bright foreground colors 90..97/39
bright background colors 100..107/49
```

The escape prefix is `\u001b[` and the suffix is `m`. Disabled formatters
return the coerced text with no escapes. Empty text is still wrapped when the
formatter is enabled. Nested ANSI close sequences in the input must be
reopened with the outer formatter's open sequence so an outer style does not
bleed or terminate early. Large already-colored strings must remain bounded.

### Color-support detection

The default `isColorSupported` is computed at module load. A non-empty
`NO_COLOR` or `--no-color` disables color. Otherwise color is supported when
`FORCE_COLOR` is set to a non-empty value, `--color` is in `process.argv`, the
platform is Windows, stdout is a non-dumb TTY, or `CI` is set. `NO_COLOR` and
`--no-color` take precedence over the positive signals. A deterministic
consumer should prefer `createColors(true)` or `createColors(false)`.

## Implementation Notes

Keep the package CommonJS-compatible and make all formatter names enumerable
properties of the returned color object. Preserve JavaScript coercion and text
exactly, including ANSI-looking text and line endings. Do not use network,
filesystem, subprocesses, clock, randomness, or a terminal protocol beyond the
specified environment checks.
