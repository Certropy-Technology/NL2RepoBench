# Build `ansi-styles`

## Project Description

Create an installable npm package named `ansi-styles`, version `7.0.0`, from an
empty workspace. The package exposes deterministic ANSI escape-code style
descriptors and color-space conversion helpers for terminal formatting.

This is a repository-generation task. Reproduce the documented public behavior
with your own package files; do not copy the pinned upstream source or tests.

## Supports

- Node.js `24.19.0` and npm `11.17.0` on `linux/amd64`.
- ESM semantics: `package.json` must contain `"type": "module"`.
- The package root must be importable as `ansi-styles` and must expose a
  default style object plus the named arrays `modifierNames`,
  `foregroundColorNames`, `backgroundColorNames`, and `colorNames`.
- The package must contain `index.js` and `index.d.ts`, and its package export
  must make both the runtime and declaration files available to consumers.
- Include a v3 `package-lock.json` that agrees with `package.json`. There are
  no runtime dependencies, and installation must work offline with:

  ```bash
  npm ci --offline --ignore-scripts --no-audit --no-fund
  ```

  Development-only tools such as linters, test runners, type checkers, and
  screenshot utilities must not be declared as package dependencies in the
  generated runtime package.

- Runtime behavior must not need a network service, native addon, custom
  loader, registry configuration, or lifecycle script.

## API Usage Guide

### Default style object

The default export is an object. Each named modifier, foreground color, and
background color is a property with an `{open, close}` pair of strings. The
strings are complete ANSI CSI sequences, such as `\u001b[31m` and
`\u001b[39m`.

The modifier names, in order, are `reset`, `bold`, `dim`, `italic`,
`underline`, `underlineDouble`, `underlineCurly`, `underlineDotted`,
`underlineDashed`, `overline`, `inverse`, `hidden`, and `strikethrough`.

The foreground names, in order, are `black`, `red`, `green`, `yellow`, `blue`,
`magenta`, `cyan`, `white`, `blackBright`, `gray`, `grey`, `redBright`,
`greenBright`, `yellowBright`, `blueBright`, `magentaBright`, `cyanBright`,
and `whiteBright`.

The background names use the same order and the `bg` prefix, for example
`bgBlack`, `bgRed`, `bgBlackBright`, `bgGray`, `bgGrey`, and `bgWhiteBright`.
The underline-color names are `underlineBlack`, `underlineRed`,
`underlineGreen`, `underlineYellow`, `underlineBlue`, `underlineMagenta`,
`underlineCyan`, `underlineWhite`, `underlineBlackBright`, `underlineGray`,
`underlineGrey`, `underlineRedBright`, `underlineGreenBright`,
`underlineYellowBright`, `underlineBlueBright`, `underlineMagentaBright`,
`underlineCyanBright`, and `underlineWhiteBright`. `colorNames` is the
foreground list followed by the background list and does not include underline
colors. The
exported arrays are stable and must not be replaced by newly allocated arrays
when read through the documented aliases.

The default object also exposes non-enumerable groups named `modifier`,
`color`, `bgColor`, and `underlineColor`; each group contains the corresponding
style pairs. The underline group closes with `\u001b[59m`.
`codes` is a non-enumerable `Map` from each opening numeric ANSI code to its
closing numeric code. Group-specific `close` strings are `\u001b[39m` for
foreground and `\u001b[49m` for background.

### Color conversion helpers

The default object exposes these helpers:

- `rgbToAnsi256(red, green, blue)` returns the nearest ANSI 256-color code.
  Equal RGB channels use the grayscale ramp, with values below 8 mapping to
  16 and values above 248 mapping to 231.
- `hexToRgb(hex)` accepts a numeric RGB value or a string containing a
  three-digit or six-digit hexadecimal sequence and returns `[red, green,
  blue]`. Invalid input returns `[0, 0, 0]`.
- `hexToAnsi256(hex)` is equivalent to `rgbToAnsi256(...hexToRgb(hex))`.
- `ansi256ToAnsi(code)` maps an ANSI 256-color code to the closest ANSI 16
  foreground code.
- `rgbToAnsi(red, green, blue)` is equivalent to
  `ansi256ToAnsi(rgbToAnsi256(red, green, blue))`.
- `hexToAnsi(hex)` is equivalent to `ansi256ToAnsi(hexToAnsi256(hex))`.

The color groups expose builder functions `ansi(code)`, `ansi256(code)`, and
`ansi16m(red, green, blue)`. Foreground builders use `38` and background
builders use `48`; each returns the complete opening ANSI sequence. The
underline-color group uses `58` for 256-color and truecolor builders. Its
`ansi(code)` builder maps ANSI 16-color codes to the corresponding palette index
because SGR 58 has no basic 16-color form. The helpers under `color`,
`bgColor`, and `underlineColor` use the same numeric conversion rules.

## Implementation Notes

Keep the package ESM-compatible and deterministic. Preserve the documented
array order, object property behavior, aliases (`gray`/`grey` and
`bgGray`/`bgGrey`), ANSI close codes, and non-enumerable helper properties.
Do not include private verifier files, reference source, provider settings,
or network access in the candidate repository.
