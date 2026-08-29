# Build `crypto-random-string`

## Project Description

Create an installable npm package named `crypto-random-string`, version
`6.0.0`, from an empty workspace. It generates cryptographically strong random
strings using Node's platform crypto source. The scored contract is the
deterministic, bounded public API described below; it is a self-contained
adaptation of the pinned upstream package and does not require runtime or
development dependencies.

Do not copy the upstream source or tests. The workspace must contain runnable
JavaScript and declaration files before evaluation; the verifier has no
TypeScript compiler and has no registry access.

## Supports

- Run on Node `24.19.0` with npm `11.17.0` on `linux/amd64` and glibc.
- `package.json` must name `crypto-random-string` version `6.0.0`, use
  `"type": "module"`, and expose the root entry with import/default
  `"./index.js"` and types `"./index.d.ts"`. Export `./package.json` as a
  metadata subpath.
- Include a valid npm lockfile version 3. There must be no runtime or
  development dependencies, scripts, lifecycle hooks, workspaces, native
  addons, custom loaders, registry configuration, or network requirements.
- A clean verifier must be able to run:

  ```bash
  npm ci --offline --ignore-scripts --no-audit --no-fund
  ```

- Randomness must come from the platform cryptographic source. Do not replace
  it with a fixed sequence, `Math.random`, current time, or a stale entropy
  pool. Large requests must be split into bounded platform calls.

## API Usage Guide

### `cryptoRandomString(options)`

Import the default export from `crypto-random-string`. `options` is an object
with required non-negative safe-integer `length`, and at most one of `type` and
`characters`.

```js
import cryptoRandomString from 'crypto-random-string';

cryptoRandomString({length: 10});
cryptoRandomString({length: 10, type: 'base64'});
cryptoRandomString({length: 10, type: 'url-safe'});
cryptoRandomString({length: 10, characters: '0123456789'});
```

Return a string whose length is the requested number of Unicode characters
selected from the requested set. The default type is `hex` and its characters
are lowercase `0-9a-f`. Supported types and exact sets are:

- `hex`: `0123456789abcdef`
- `base64`: standard base64 characters (`A-Z`, `a-z`, `0-9`, `+`, `/`), with
  padding removed and the result sliced to the requested length
- `url-safe`: `abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-._~`
- `numeric`: `0123456789`
- `distinguishable`: `CDEHKMPRTUWXY012458`
- `ascii-printable`: printable ASCII except the space
- `alphanumeric`: `ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789`

`characters` is a non-empty string interpreted as Unicode code points. Repeated
characters remain repeated entries and therefore retain their weighting. A
single-character set always returns that character repeated. Character sets
may contain at most `65536` Unicode characters. Selection for custom and
predefined sets must use rejection sampling over 16-bit selectors so ordinary
non-power-of-two sets do not receive a modulo-bias shortcut.

Throw a `TypeError` for a missing, negative, fractional, unsafe, or non-numeric
length; for both `type` and `characters`; for a non-string, empty, or oversized
`characters`; and for an unknown `type`. Error messages should identify the
invalid option and match the ordinary upstream wording where applicable.

For a custom set, `length` counts Unicode code points, so an emoji set returns
the requested number of emoji even though JavaScript UTF-16 `.length` is larger.
For `hex` and `base64`, the implementation may encode random bytes and slice
the encoded output, but it must still return exactly the requested string
length and must never expose base64 `=` padding.

### Type declarations

Provide an `Options` type with a required `length`, mutually exclusive `type`
and `characters`, and the default function signature returning `string`.
The declarations must be valid TypeScript syntax and describe the supported
literal type names.

## Implementation Notes

Keep the package side-effect free except for consuming cryptographic entropy.
Use an independent entropy allocation for each operation. A request larger
than the platform's 65,536-byte `getRandomValues` limit must be filled in
chunks. The verifier constructs all inputs in an unprivileged child and sends
only bounded JSON-compatible requests; it does not inspect implementation
source or rely on probabilistic exact-output assertions.
