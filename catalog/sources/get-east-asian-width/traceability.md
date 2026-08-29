# Specification Traceability

| Public contract | Private behavior group | Coverage |
| --- | --- | --- |
| Package identity and ESM entry | package-shape | name/version/type/exports and lockfile |
| East Asian Width categories | category-classification | narrow, neutral, ambiguous, halfwidth, fullwidth, wide, supplementary code point |
| Numeric display width | numeric-width | default behavior, ambiguous option, category parity |
| Input validation | validation | strings, fractional numbers, safe-integer boundary |
| Stable JSON boundary | determinism | repeat calls and JSON-compatible return values |

Reverse review found no scored assertion requiring a callback, filesystem
fixture, native module, external service, or candidate-controlled source path.
The private adapter calls only the two documented public functions.
