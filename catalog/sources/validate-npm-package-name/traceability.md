# `validate-npm-package-name` traceability

Frozen source revision: `f63469d58278635630681c2506f05176ff18a7cb`
(`8.0.0`). Production denominator: 44 `node:test` leaves.

| Leaf range | Public contract | Source/test basis |
| --- | --- | --- |
| 1 | package name/version and callable CommonJS root export | package metadata and `module.exports` |
| 2-4 | ordinary and scoped URL-friendly names | upstream traditional/scoped assertions |
| 5-11 | empty, null, undefined, and other non-string inputs | upstream type guards plus JSON child adapter sentinels |
| 12-21 | period/hyphen/underscore starts, whitespace, slash, colon, percent, and non-ASCII errors | upstream error assertions and URL-encoding rule |
| 22-24 | case-insensitive reserved names and mixed error/warning result | upstream exclusion list and result construction |
| 25-27 | bare and `node:` builtin module behavior | frozen builtin inventory and pinned Node runtime |
| 28-32 | 214-unit boundary, uppercase, special characters, and warning order | upstream legacy warning branches |
| 33-40 | scoped segment exceptions, malformed scopes, and URL-safe scoped punctuation | upstream scope pattern and segment validation |
| 41-43 | omission of empty `warnings`/`errors` properties | public result-shape contract |
| 44 | repeat calls are deterministic and stateless | synchronous pure validation contract |

Every private assertion maps to an explicit section of `instruction.md`. The
verifier does not exercise a CLI, dependency internals, filesystem behavior,
network behavior, locale, time, randomness, or unadvertised exports.
