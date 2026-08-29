# Build `micromark-util-character`

## Project Description

Create an installable npm package named `micromark-util-character`, version
`2.1.1`, from an empty workspace. The package provides pure predicates for
classifying character codes used by micromark. Implement the observable public
API described here with your own package files.

The task is repository generation. Do not fetch or copy a reference checkout,
tests, verifier code, or generated answers.

## Supports

- Run on Node `24.19.0` with npm `11.17.0` on `linux/amd64`.
- Use JavaScript ESM. `package.json` must contain:

  ```json
  {
    "name": "micromark-util-character",
    "version": "2.1.1",
    "type": "module",
    "sideEffects": false,
    "types": "./index.d.ts",
    "exports": {
      "development": "./dev/index.js",
      "default": "./index.js"
    }
  }
  ```

- Both root conditions must expose exactly these 12 named functions, with no
  default export:

  ```text
  asciiAlpha
  asciiAlphanumeric
  asciiAtext
  asciiControl
  asciiDigit
  asciiHexDigit
  asciiPunctuation
  markdownLineEnding
  markdownLineEndingOrSpace
  markdownSpace
  unicodePunctuation
  unicodeWhitespace
  ```

- Provide `index.js`, `dev/index.js`, and `index.d.ts`. The package must be
  usable immediately after installation; no build step may be required.
- Define and export declarations for every function with this shared shape:

  ```ts
  type Code = number | null
  function predicate(code: Code): boolean
  ```

- Include a v3 `package-lock.json` that agrees with `package.json`. Pin these
  npm dependencies exactly:

  ```json
  {
    "micromark-util-symbol": "2.0.1",
    "micromark-util-types": "2.0.2"
  }
  ```

  A clean verifier must be able to run:

  ```bash
  npm ci --offline --ignore-scripts --no-audit --no-fund
  ```

- Do not add `preinstall`, `install`, `postinstall`, `prepare`, `prepublish`,
  `prepublishOnly`, `publish`, or `postpublish` scripts. Do not use native
  addons, workspaces, a CLI, custom loaders, registry configuration, or network
  access.
- Do not add hidden tests, grader or reward files, Oracle material, npm cache
  bytes, credentials, or verifier code to the candidate repository.

The scored `Code` domain is `null`, the micromark virtual integer codes `-5`
through `-1`, and finite UTF-16 code-unit integers `0` through `65535`. Every
function is synchronous, deterministic, stateless, and returns a boolean. No
function mutates input or process state, reads files, or performs network I/O.

## API Usage Guide

All functions are named imports from the package root:

```js
import {
  asciiAlpha,
  markdownSpace,
  unicodePunctuation
} from 'micromark-util-character'

asciiAlpha(65) // true: `A`
markdownSpace(-1) // true: micromark virtual space
unicodePunctuation(0x2014) // true: em dash
```

### `asciiAlpha(code: Code): boolean`

Return `true` only for ASCII uppercase letters U+0041 through U+005A and
lowercase letters U+0061 through U+007A. Return `false` for virtual codes and
`null`.

### `asciiAlphanumeric(code: Code): boolean`

Return `true` for the `asciiAlpha` ranges or ASCII digits U+0030 through
U+0039. Return `false` otherwise.

### `asciiAtext(code: Code): boolean`

Classify RFC 5322 `atext`. Return `true` for ASCII alphanumerics and these
additional characters:

```text
# $ % & ' * + - / = ? ^ _ ` { | } ~
```

Equivalently, the additional inclusive ranges are U+0023 through U+0027,
U+002A through U+002B, U+002D, U+002F, U+003D, U+003F, U+005E through U+0060,
and U+007B through U+007E. Characters such as `!`, `"`, `(`, `)`, `,`, `.`,
`:`, `;`, `<`, `>`, `@`, `[`, `\`, and `]` are not `atext`.

### `asciiControl(code: Code): boolean`

Return `true` for C0 controls U+0000 through U+001F, DEL U+007F, and all five
micromark virtual codes `-5` through `-1`. Return `false` for `null`, U+0020
through U+007E, and code units above DEL.

### `asciiDigit(code: Code): boolean`

Return `true` only for U+0030 (`0`) through U+0039 (`9`).

### `asciiHexDigit(code: Code): boolean`

Return `true` for ASCII digits, U+0041 (`A`) through U+0046 (`F`), and U+0061
(`a`) through U+0066 (`f`).

### `asciiPunctuation(code: Code): boolean`

Return `true` for the inclusive ASCII ranges U+0021 through U+002F, U+003A
through U+0040, U+005B through U+0060, and U+007B through U+007E. Letters,
digits, space, controls, DEL, virtual codes, and `null` return `false`.

### `markdownLineEnding(code: Code): boolean`

Micromark preprocesses concrete line endings into virtual codes. Return `true`
for `-5` (carriage return), `-4` (line feed), and `-3` (CRLF). Return `false`
for all other scored values, including concrete U+000A and U+000D.

### `markdownLineEndingOrSpace(code: Code): boolean`

Return `true` for every micromark virtual code `-5` through `-1` and concrete
U+0020 SPACE. Return `false` otherwise.

### `markdownSpace(code: Code): boolean`

Return `true` only for `-2` (virtual horizontal tab), `-1` (virtual space), and
U+0020 SPACE. Concrete U+0009 TAB is not a markdown space after preprocessing.

### `unicodePunctuation(code: Code): boolean`

For nonnegative code units, return `true` when the single UTF-16 character is
in any Unicode `P` punctuation category or any Unicode `S` symbol category.
This includes ASCII punctuation, connector punctuation such as `_`, dashes and
quotes, and symbols such as U+20AC EURO SIGN and U+2605 BLACK STAR. Letters,
numbers, separators, controls, virtual codes, and `null` return `false`.

### `unicodeWhitespace(code: Code): boolean`

For nonnegative code units, follow ECMAScript whitespace and line-terminator
classification. This includes U+0009 through U+000D, U+0020, Unicode space
separators such as U+00A0 and U+1680, U+2028/U+2029, and U+FEFF. Letters,
symbols, virtual codes, and `null` return `false`.

## Implementation Notes

- Character inputs are numeric code units, not one-character strings.
- The virtual codes have stable meanings: `-5` carriage return, `-4` line
  feed, `-3` CRLF, `-2` horizontal tab, and `-1` virtual space.
- Unicode predicates operate on one UTF-16 code unit. Supplementary-plane code
  points represented by surrogate pairs are outside the scored domain.
- Values outside the documented domain do not need a special error contract.
- The verifier-owned adapter sends one bounded JSON request to a fresh child
  process and receives only boolean or package-inventory JSON. This adapter is
  not a candidate CLI requirement.
