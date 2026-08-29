# `crypto-random-string` Traceability

| Public contract | Private coverage |
| --- | --- |
| npm name/version, ESM root, default export, no dependencies | metadata leaf and offline candidate install |
| Required non-negative integer length | missing, negative, fractional, and string-length leaves |
| Default lowercase hex output | default output leaves |
| Standard base64, exact length, no padding | base64 alphabet and short-boundary leaves |
| url-safe, numeric, distinguishable, ascii-printable, alphanumeric sets | one leaf per predefined set |
| Custom string alphabet and duplicate weighting | 20,000-character child-side weighting leaf |
| Unicode code-point length, including astral characters | Unicode and single-emoji leaves |
| Empty output does not consume entropy | zero-length leaf across custom and base64 paths |
| 65,536-symbol alphabet does not hang | compact generated maximum-alphabet zero-length leaf |
| More than 65,536 symbols is rejected | generated oversized-alphabet leaf |
| Rejection sampling for non-power-of-two alphabets | compact 40,000-symbol first-half distribution leaf |
| Entropy request limit is handled in chunks | 70,000-character numeric output leaf |
| Independent cryptographic entropy per operation | varied predefined outputs and successive-call leaf |
| `type`/`characters` mutual exclusion and unknown types | argument-error leaves, including `constructor` |

The private adapter only constructs bounded JSON-compatible inputs and returns
observable values or exception name/message. It does not expose callbacks,
source text, random state, filesystem paths, or candidate internals.
