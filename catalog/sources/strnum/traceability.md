# `strnum` traceability

Frozen source revision: `117d6a5f59fbb8f29d2f88c0c292d7dc44d67a7f`
(`2.4.2`). Production denominator: 42 `node:test` leaves.

| Leaf range | Public contract | Frozen source/test basis |
| --- | --- | --- |
| 1-4 | package-root default function, non-string pass-through, empty/whitespace preservation | package metadata and upstream base cases |
| 5-7 | malformed text, signs, and ordinary integer syntax | `strnum_test.js` ordinary parsing cases |
| 8-14 | hexadecimal defaults and binary/octal opt-in behavior | radix branches plus upstream radix specs |
| 15-22 | leading-zero, decimal, and negative-zero policy | upstream leading-zero and floating-point specs |
| 23-29 | precision round-trip, long numbers, lowercase/uppercase exponent syntax, malformed exponents | upstream precision and scientific-notation specs |
| 30-34 | `eNotation` and all four overflow modes | `infinity_test.js` and option branches |
| 35-37 | Unicode numeral normalization and overflow ordering | `anynum_test.js` and exact `anynum@1.0.1` closure |
| 38-40 | `skipLike` match/non-match and original-string return | upstream regular-expression option specs |
| 41-42 | surrounding whitespace and repeat-call determinism | trim behavior and stateless per-call option merge |

The child adapter reconstructs only a bounded declarative regular expression
inside the unprivileged candidate process. The trusted verifier does not import
the candidate and does not expose hidden tests to the candidate image. Global
or sticky `RegExp.lastIndex` mutation is documented JavaScript behavior but is
not scored because the one-shot boundary intentionally creates a fresh regular
expression for each request.
