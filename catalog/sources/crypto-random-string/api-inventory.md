# `crypto-random-string` API Inventory

## Frozen public surface

- Root import: `import cryptoRandomString from 'crypto-random-string'`
- Package identity: `crypto-random-string@6.0.0`
- Module format: ESM (`type: module`)
- Root export: default function only, from `index.js`; declaration from
  `index.d.ts`
- Options declaration: `Options` with required numeric `length` and mutually
  exclusive `type` or `characters`

## Behavior families

| Family | Contract |
| --- | --- |
| Length | non-negative safe integer; rejects missing, negative, fractional, string, and non-safe values |
| Default/hex | default type is lowercase hexadecimal; exact requested length |
| Encoded bytes | standard base64 without `=` padding; exact requested length |
| Predefined sets | url-safe, numeric, distinguishable, ascii-printable, alphanumeric |
| Custom set | Unicode code-point iteration, repeated-symbol weighting, single-symbol behavior |
| Distribution | 16-bit rejection sampling avoids modulo bias for non-power-of-two sets |
| Limits | 65,536 Unicode symbols; entropy calls split at 65,536 bytes |
| Errors | `TypeError` for invalid options with option-specific upstream-style messages |

## Explicitly out of scope

The upstream development scripts, AVA test runner, `xo`, `tsd`, registry
configuration, and dependency implementations are not part of the scored
surface. The package is intentionally delivered as runnable JavaScript and
declarations, so evaluation does not need TypeScript or a build tool.
