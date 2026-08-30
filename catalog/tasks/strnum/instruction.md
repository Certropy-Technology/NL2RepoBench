# Project Description

Implement the `strnum` package as a small ECMAScript module that converts only
supported numeric strings to JavaScript numbers. It must preserve strings that
are malformed, disabled by options, unsafe to round-trip, or explicitly skipped.
The package has no CLI and performs no filesystem, process, clock, random, or
network work.

# Supports

- Node.js `24.19.0` with npm `11.17.0` on Linux x64.
- Package name `strnum`, version `2.4.2`, with `"type": "module"`.
- The package root provides one default export from `strnum.js`.
- Runtime dependency: exact `anynum@1.0.1`. Do not add other runtime packages.
- Commit a lockfileVersion 3 `package-lock.json`. The evaluation environment is
  offline, so installation must use the preinstalled npm cache and must not
  fetch packages.

# API Usage Guide

## Default export `toNumber(value, options?)`

**Import path:** package root.

**Signature:**

```ts
type InfinityMode = 'original' | 'null' | 'infinity' | 'string';

interface StrnumOptions {
  hex?: boolean;
  binary?: boolean;
  octal?: boolean;
  leadingZeros?: boolean;
  eNotation?: boolean;
  skipLike?: RegExp;
  infinity?: InfinityMode;
  unicode?: boolean;
}

export default function toNumber<T>(
  value: T,
  options?: StrnumOptions,
): number | string | null | T;
```

Defaults are `hex: true`, `binary: false`, `octal: false`,
`leadingZeros: true`, `eNotation: true`, `infinity: 'original'`, and
`unicode: false`.

Non-string values are returned unchanged, including `undefined`, `null`,
numbers, booleans, arrays, and objects. Empty and whitespace-only strings are
also returned byte-for-byte unchanged. For other strings, parsing uses trimmed
text, but every non-conversion result is the original untrimmed string.

Ordinary signed integers and decimals are converted only when the resulting
number faithfully represents the accepted spelling. A leading `+` or `-` is
supported. Decimal forms such as `.006`, `6.0`, `0.06`, and `-0.0` parse;
negative zero must remain distinguishable with `Object.is(result, -0)`.
Malformed separators, embedded signs, multiple decimal points, and precision
losing integer or decimal spellings remain strings.

```js
import toNumber from 'strnum';

toNumber('+12');                         // 12
toNumber('.006');                        // 0.006
toNumber('20211201030005811824');        // unchanged string
toNumber('  not a number  ');            // unchanged, including spaces
Object.is(toNumber('-0.0'), -0);          // true
```

With `leadingZeros: true`, padded numeric forms such as `006`, `00.6`, and
`-06.0` may parse. With `leadingZeros: false`, those padded forms remain
strings, while `0`, `0.0`, `0.06`, `.006`, and `6.0` still parse. Zero-only
spellings with more than one leading zero, such as `00` or `00.00`, remain
strings when this option is false.

Hexadecimal is enabled by default and accepts a leading sign. Binary and octal
are opt-in and accept only unsigned `0b...` and `0o...` forms. Disabled or
malformed radix strings remain unchanged.

```js
toNumber('-0x2f');                        // -47
toNumber('0x2f', {hex: false});           // '0x2f'
toNumber('0b1010', {binary: true});        // 10
toNumber('-0b1010', {binary: true});       // unchanged string
toNumber('0o10', {octal: true});           // 8
```

Scientific notation accepts `e` or `E`, optional exponent signs, and decimal
mantissas. It follows `leadingZeros`; for example `01.0e2` parses by default
but is preserved when leading zeros are disabled. With `eNotation: false`,
explicit scientific notation and ordinary long values that JavaScript would
render in exponent form remain strings.

Finite syntax that overflows to positive or negative infinity is handled by
`infinity`: `original` returns the original string, `null` returns `null`,
`infinity` returns numeric `Infinity` or `-Infinity`, and `string` returns the
corresponding string literal. The option value is case-insensitive. An
`infinity` value without a callable `toLowerCase` throws a `TypeError` only
when overflow handling is reached.

When `unicode: true`, `anynum` normalizes supported non-ASCII decimal numerals
before the same parsing and overflow rules run. With the default `false`, such
text remains unchanged.

`skipLike` is tested against trimmed text before numeric conversion and Unicode
normalization. A match returns the original untrimmed string. The caller-owned
regular expression is used directly, so JavaScript's ordinary `RegExp.test`
state behavior applies to global or sticky expressions. A non-RegExp object
without a callable `test` throws a `TypeError` when this option is reached.

```js
toNumber('１000', {unicode: true});        // 1000
toNumber('１000');                         // unchanged string
toNumber('  +1212121212  ', {
  skipLike: /^\+[0-9]{10}$/,
});                                        // original string with spaces
```

# Implementation Notes

- The default export is synchronous, deterministic, and does not mutate input
  strings or the options object. Only caller-owned regular-expression state can
  change through normal `RegExp.test` semantics.
- Option objects are merged over the defaults for each call; state must not
  leak between calls.
- Preserve the original string whenever conversion is rejected. Do not return
  the trimmed text in those branches.
- Avoid super-linear processing of long decimal strings or long runs of zeroes.
- The verifier invokes candidate code only in bounded, unprivileged child
  processes. `skipLike` expressions cross that boundary as a source-and-flags
  description and are reconstructed in the candidate child.
