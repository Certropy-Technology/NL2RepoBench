# `is-fullwidth-code-point` traceability

Frozen source revision: `2696d873463fde9f6b09b49c98380bd49c67b00a` (`5.1.0`).

| Leaf range | Public contract | Source/test basis |
| --- | --- | --- |
| 1 | package name/version, ESM root export, declaration, default callable | package metadata and declaration |
| 2-5 | ASCII, Latin punctuation, control, and empty-range values are false | upstream main assertions and width lookup |
| 6-9 | Japanese, Chinese, Hangul, and ideographic space are true | upstream main assertions and Unicode categories |
| 10-12 | supplementary-plane emoji and wide characters are true | upstream supplementary code-point assertions |
| 13-15 | fullwidth forms are true while halfwidth forms and ambiguous punctuation are false | East Asian Width boundary categories |
| 16-20 | non-integer, non-number, negative, out-of-range, and unassigned values return false | upstream integer guard and documented input contract |
| 21-23 | multiple representative calls preserve boolean results across adjacent requests | deterministic stateless API behavior |
| 24 | repeated calls return identical values without leaked state | default function purity and lookup behavior |

The verifier tests only the documented default export and JSON-compatible
inputs. It does not test an unadvertised CLI, private dependency exports,
callbacks, custom prototypes, symbols, BigInt, ambient locale, or network.
